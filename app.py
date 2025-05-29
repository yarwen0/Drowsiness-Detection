from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
from PIL import Image
import io
import random
import logging
from datetime import datetime
from scipy.spatial import distance as dist

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load face and eye cascade classifiers
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Drowsiness detection parameters
EAR_THRESHOLD = 0.20  # Eye Aspect Ratio threshold
MAR_THRESHOLD = 0.3   # Mouth Aspect Ratio threshold
CONSECUTIVE_FRAMES = 3  # Number of consecutive frames for drowsiness detection

# Session statistics
session_start_time = datetime.now()
drowsiness_history = []
blink_counter = 0
last_blink_time = datetime.now()
blink_rate = 0

def calculate_ear(eye_landmarks):
    try:
        # Calculate the eye aspect ratio (EAR)
        # Vertical eye landmarks
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        # Horizontal eye landmarks
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        # Calculate EAR
        ear = (v1 + v2) / (2.0 * h)
        
        # Calculate blink rate
        current_time = datetime.now()
        time_diff = (current_time - last_blink_time).total_seconds()
        
        if ear < EAR_THRESHOLD:
            blink_counter += 1
            if time_diff >= 1:  # Update blink rate every second
                blink_rate = blink_counter / time_diff
                blink_counter = 0
                last_blink_time = current_time
        
        return ear, blink_rate
    except Exception as e:
        logger.error(f"Error calculating EAR: {str(e)}")
        return None, 0

def get_eye_landmarks(eye_region):
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
        
        # Detect eyes
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 3, minSize=(20, 20))
        
        if len(eyes) >= 2:
            # Get the first two eyes detected
            eye1, eye2 = eyes[:2]
            
            # Extract eye regions
            x1, y1, w1, h1 = eye1
            x2, y2, w2, h2 = eye2
            
            # Calculate landmarks for both eyes
            landmarks1 = np.array([
                [x1, y1],  # Top-left
                [x1 + w1//3, y1],  # Top-third
                [x1 + 2*w1//3, y1],  # Top-two-thirds
                [x1 + w1, y1],  # Top-right
                [x1 + w1//2, y1 + h1//2],  # Center
                [x1 + w1//2, y1 + h1]  # Bottom-center
            ])
            
            landmarks2 = np.array([
                [x2, y2],  # Top-left
                [x2 + w2//3, y2],  # Top-third
                [x2 + 2*w2//3, y2],  # Top-two-thirds
                [x2 + w2, y2],  # Top-right
                [x2 + w2//2, y2 + h2//2],  # Center
                [x2 + w2//2, y2 + h2]  # Bottom-center
            ])
            
            return landmarks1, landmarks2
        
        return None, None
    except Exception as e:
        logger.error(f"Error getting eye landmarks: {str(e)}")
        return None, None

def update_stats(is_drowsy):
    current_time = datetime.now()
    session_duration = (current_time - session_start_time).total_seconds()
    
    if is_drowsy:
        drowsiness_history.append({
            'timestamp': current_time,
            'duration': 1  # Assuming 1 second per detection
        })
    
    # Calculate drowsiness percentage
    drowsiness_percentage = 0
    if session_duration > 0:
        drowsiness_time = sum(event['duration'] for event in drowsiness_history)
        drowsiness_percentage = (drowsiness_time / session_duration) * 100
    
    return {
        'total_drowsiness_events': len(drowsiness_history),
        'total_blinks': blink_counter,
        'average_blink_rate': blink_rate,
        'session_duration': session_duration,
        'drowsiness_percentage': drowsiness_percentage
    }

@app.route('/api/detect', methods=['POST'])
def detect_drowsiness():
    try:
        # Get image data from request
        if 'image' not in request.json:
            return jsonify({'error': 'No image data provided'}), 400

        image_data = request.json['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array and BGR for OpenCV
        img_np = np.array(image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        is_drowsy = False
        ear_value = None
        stats = update_stats(False)
        
        if len(faces) > 0:
            # Get the first face detected
            x, y, w, h = faces[0]
            face_roi = img_np[y:y+h, x:x+w]
            
            # Get eye landmarks
            eye1_landmarks, eye2_landmarks = get_eye_landmarks(face_roi)
            
            if eye1_landmarks is not None and eye2_landmarks is not None:
                # Calculate EAR for both eyes
                ear1, _ = calculate_ear(eye1_landmarks)
                ear2, _ = calculate_ear(eye2_landmarks)
                
                if ear1 is not None and ear2 is not None:
                    # Use the average EAR of both eyes
                    ear_value = (ear1 + ear2) / 2
                    
                    # Check for drowsiness
                    is_drowsy = ear_value < EAR_THRESHOLD
                    
                    if is_drowsy:
                        stats = update_stats(True)
        
        # Get random motivational message
        message = random.choice(MOTIVATIONAL_MESSAGES) if is_drowsy else "You're doing great! Stay focused! 💪"
        
        return jsonify({
            'is_drowsy': is_drowsy,
            'message': message,
            'stats': stats,
            'ear_value': ear_value
        })
        
    except Exception as e:
        logger.error(f"Error in detect_drowsiness: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Motivational messages for Gen Z
MOTIVATIONAL_MESSAGES = [
    "No cap, you're doing great! Keep grinding 💪",
    "Sheesh, that focus is immaculate! 🔥",
    "You're built different, keep going! 🚀",
    "That's bussin'! Stay focused! ✨",
    "You're literally slaying rn! Keep it up! 💅",
    "No cap, you're gonna ace this! 🎯",
    "That's straight fire! Keep the momentum! 🔥",
    "You're doing the most (in a good way)! 💯",
]

@app.route('/api/zen-mode', methods=['GET'])
def get_zen_mode():
    # List of peaceful background music URLs (using actual URLs)
    zen_music = [
        "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1bab.mp3",  # Peaceful meditation music
        "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73c3a.mp3",  # Calm nature sounds
        "https://cdn.pixabay.com/download/audio/2022/01/20/audio_0625c1539a.mp3"   # Relaxing piano
    ]
    
    return jsonify({
        'music_urls': zen_music
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': face_cascade is not None,
        'model_path': 'Haar Cascade'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 