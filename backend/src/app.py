from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import base64
import logging
from datetime import datetime
import os
from typing import Dict, Any
import json
from drowsiness_detector import DrowsinessDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize drowsiness detector
detector = DrowsinessDetector(
    ear_threshold=0.20,
    mar_threshold=0.30,
    consecutive_frames=3,
    blink_threshold=0.15,
    yawn_threshold=0.35
)

# Store session data
sessions: Dict[str, Dict[str, Any]] = {}

def get_session_id() -> str:
    """Generate a unique session ID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def initialize_session(session_id: str):
    """Initialize a new session."""
    sessions[session_id] = {
        'start_time': datetime.now(),
        'drowsy_count': 0,
        'blink_count': 0,
        'last_alert_time': None,
        'alert_history': [],
        'settings': {
            'ear_threshold': 0.20,
            'mar_threshold': 0.30,
            'consecutive_frames': 3,
            'blink_threshold': 0.15,
            'yawn_threshold': 0.35,
            'show_face_box': True,
            'show_eye_markers': True,
            'auto_zen_mode': False
        }
    }

@app.route('/api/detect', methods=['POST'])
def detect_drowsiness():
    """Endpoint for drowsiness detection."""
    try:
        # Get session ID from request
        session_id = request.headers.get('X-Session-ID')
        if not session_id or session_id not in sessions:
            session_id = get_session_id()
            initialize_session(session_id)
        
        # Get image data
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'].split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Detect drowsiness
        result = detector.detect_drowsiness(frame)
        
        # Update session statistics
        if result.is_drowsy:
            sessions[session_id]['drowsy_count'] += 1
            current_time = datetime.now()
            
            # Add to alert history
            alert = {
                'timestamp': current_time.isoformat(),
                'ear': result.ear,
                'confidence': result.confidence
            }
            sessions[session_id]['alert_history'].append(alert)
            
            # Keep only last 100 alerts
            if len(sessions[session_id]['alert_history']) > 100:
                sessions[session_id]['alert_history'].pop(0)
            
            sessions[session_id]['last_alert_time'] = current_time
        
        # Get session statistics
        stats = detector.get_session_stats()
        
        # Prepare response
        response = {
            'session_id': session_id,
            'is_drowsy': result.is_drowsy,
            'ear': result.ear,
            'mar': result.mar,
            'blink_rate': result.blink_rate,
            'confidence': result.confidence,
            'face_detected': result.face_detected,
            'stats': stats,
            'settings': sessions[session_id]['settings']
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in detect_drowsiness endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Endpoint for managing session settings."""
    try:
        session_id = request.headers.get('X-Session-ID')
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if request.method == 'GET':
            return jsonify(sessions[session_id]['settings'])
        
        # Update settings
        new_settings = request.get_json()
        if not new_settings:
            return jsonify({'error': 'No settings provided'}), 400
        
        # Update only provided settings
        for key, value in new_settings.items():
            if key in sessions[session_id]['settings']:
                sessions[session_id]['settings'][key] = value
        
        # Update detector parameters
        detector.EAR_THRESHOLD = sessions[session_id]['settings']['ear_threshold']
        detector.MAR_THRESHOLD = sessions[session_id]['settings']['mar_threshold']
        detector.CONSECUTIVE_FRAMES = sessions[session_id]['settings']['consecutive_frames']
        detector.BLINK_THRESHOLD = sessions[session_id]['settings']['blink_threshold']
        detector.YAWN_THRESHOLD = sessions[session_id]['settings']['yawn_threshold']
        
        return jsonify(sessions[session_id]['settings'])
        
    except Exception as e:
        logger.error(f"Error in settings endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Endpoint for resetting session statistics."""
    try:
        session_id = request.headers.get('X-Session-ID')
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        # Reset detector
        detector.reset_session()
        
        # Reset session data
        initialize_session(session_id)
        
        return jsonify({'message': 'Session reset successfully'})
        
    except Exception as e:
        logger.error(f"Error in reset endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    
    # Start the server
    app.run(host='0.0.0.0', port=5001, debug=True) 