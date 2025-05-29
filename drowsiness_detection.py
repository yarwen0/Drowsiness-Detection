import os
import cv2
import torch
import numpy as np
import pygame
import requests
import argparse
import logging
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from ultralytics import YOLO
from datetime import datetime
import mediapipe as mp
from scipy.spatial import distance as dist

# Load environment variables from .env file
load_dotenv()

# ─── CONFIG ─────────────────────────────────────────────────────
# Default paths and settings loaded from .env
DEFAULT_WEIGHTS = os.getenv('WEIGHTS', 'yolov5/runs/train/exp/weights/last.pt')
DEFAULT_TEST_IMG_URL = os.getenv('TEST_IMG_URL', 'https://daily.jstor.org/wp-content/uploads/2017/12/traffic_jam_1050x700.jpg')
DEFAULT_ALARM_PATH = os.getenv('ALARM_PATH', 'alarm.mp3')
# ────────────────────────────────────────────────────────────────

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DrowsinessDetector:
    def __init__(self, model_path='yolov5s.pt'):
        logger.info(f"Loading model from {model_path}")
        self.model = YOLO(model_path)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Enhanced thresholds and parameters
        self.ear_threshold = 0.18  # Even more sensitive threshold
        self.mar_threshold = 0.3   # Mouth aspect ratio threshold
        self.eye_ratio_threshold = 0.25
        self.consecutive_frames = 0
        self.required_consecutive_frames = 1
        self.blink_counter = 0
        self.last_blink_time = datetime.now()
        self.blink_rate = 0
        self.session_start_time = datetime.now()
        self.drowsiness_history = []
        
        # Enhanced motivational messages
        self.motivational_messages = [
            "Stay focused! You're doing great! 💪",
            "Keep your eyes on the prize! 🎯",
            "You've got this! Stay alert! ⚡",
            "Time for a quick stretch? 🧘‍♂️",
            "Take a deep breath and stay awake! 🌬️",
            "Your future self thanks you for staying alert! 🌟",
            "Remember why you started! 🚀",
            "Stay sharp, stay successful! 💫",
            "You're stronger than sleep! 💪",
            "Keep pushing forward! 🎯",
            "Take a short walk to refresh! 🚶‍♂️",
            "Hydrate yourself! 💧",
            "Do some quick exercises! 🏃‍♂️",
            "Focus on your goals! 🎯",
            "You're making progress! 🌟"
        ]
        
        # Initialize statistics
        self.stats = {
            'total_drowsiness_events': 0,
            'total_blinks': 0,
            'average_blink_rate': 0,
            'session_duration': 0,
            'drowsiness_percentage': 0
        }
        
        logger.info("Model and face mesh loaded successfully")

    def calculate_ear(self, landmarks):
        try:
            # Calculate the eye aspect ratio (EAR)
            # Vertical eye landmarks
            v1 = np.linalg.norm(landmarks[1] - landmarks[5])
            v2 = np.linalg.norm(landmarks[2] - landmarks[4])
            # Horizontal eye landmarks
            h = np.linalg.norm(landmarks[0] - landmarks[3])
            # Calculate EAR
            ear = (v1 + v2) / (2.0 * h)
            
            # Add additional checks for eye closure
            eye_height = np.mean([v1, v2])
            eye_width = h
            eye_ratio = eye_height / eye_width
            
            # Calculate blink rate
            current_time = datetime.now()
            time_diff = (current_time - self.last_blink_time).total_seconds()
            
            if ear < self.ear_threshold:
                self.blink_counter += 1
                if time_diff >= 1:  # Update blink rate every second
                    self.blink_rate = self.blink_counter / time_diff
                    self.blink_counter = 0
                    self.last_blink_time = current_time
            
            return ear, eye_ratio, self.blink_rate
        except Exception as e:
            logger.error(f"Error calculating EAR: {str(e)}")
            return None, None, 0

    def calculate_mar(self, landmarks):
        try:
            # Calculate mouth aspect ratio
            mouth_width = np.linalg.norm(landmarks[0] - landmarks[6])
            mouth_height = np.linalg.norm(landmarks[2] - landmarks[4])
            mar = mouth_height / mouth_width
            return mar
        except Exception as e:
            logger.error(f"Error calculating MAR: {str(e)}")
            return None

    def update_stats(self, is_drowsy):
        current_time = datetime.now()
        session_duration = (current_time - self.session_start_time).total_seconds()
        
        if is_drowsy:
            self.stats['total_drowsiness_events'] += 1
            self.drowsiness_history.append({
                'timestamp': current_time,
                'duration': 1  # Assuming 1 second per detection
            })
        
        # Calculate drowsiness percentage
        if session_duration > 0:
            drowsiness_time = sum(event['duration'] for event in self.drowsiness_history)
            self.stats['drowsiness_percentage'] = (drowsiness_time / session_duration) * 100
        
        self.stats['session_duration'] = session_duration
        self.stats['average_blink_rate'] = self.blink_rate
        
        return self.stats

    def detect_drowsiness(self, frame):
        try:
            # Convert frame to RGB for face mesh
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run face mesh detection
            face_mesh_results = self.face_mesh.process(frame_rgb)
            
            if face_mesh_results.multi_face_landmarks:
                landmarks = np.array([[lm.x * frame.shape[1], lm.y * frame.shape[0]] 
                                    for lm in face_mesh_results.multi_face_landmarks[0].landmark])
                
                # Calculate metrics
                ear, eye_ratio, blink_rate = self.calculate_ear(landmarks)
                mar = self.calculate_mar(landmarks)
                
                if ear is not None and eye_ratio is not None:
                    # Enhanced drowsiness detection using multiple metrics
                    is_drowsy = (ear < self.ear_threshold or 
                               eye_ratio > self.eye_ratio_threshold or 
                               (mar is not None and mar > self.mar_threshold))
                    
                    if is_drowsy:
                        self.consecutive_frames += 1
                        if self.consecutive_frames >= self.required_consecutive_frames:
                            stats = self.update_stats(True)
                            return True, np.random.choice(self.motivational_messages), stats
                    else:
                        self.consecutive_frames = 0
                        stats = self.update_stats(False)
                        return False, "You're alert and focused! Keep it up! 🌟", stats
            
            return False, "No face detected. Please position yourself in front of the camera.", self.stats
            
        except Exception as e:
            logger.error(f"Error in drowsiness detection: {str(e)}")
            return False, "Error in detection. Please try again.", self.stats

    def get_face_landmarks(self, frame, bbox):
        try:
            x1, y1, x2, y2 = map(int, bbox)
            face_roi = frame[y1:y2, x1:x2]
            
            # Convert to grayscale for better landmark detection
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Use a more sensitive face detector with adjusted parameters
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))
            
            if len(faces) > 0:
                x, y, w, h = faces[0]
                # Extract eye region with more margin
                eye_region = gray[max(0, y-10):min(gray.shape[0], y+h//2+10), max(0, x-10):min(gray.shape[1], x+w+10)]
                
                # Use a more sensitive eye detector with adjusted parameters
                eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
                eyes = eye_cascade.detectMultiScale(eye_region, 1.1, 3, minSize=(20, 20))
                
                if len(eyes) >= 2:
                    # Calculate eye landmarks with more precision
                    landmarks = []
                    for (ex, ey, ew, eh) in eyes[:2]:
                        # Add more landmark points for better accuracy
                        landmarks.append(np.array([ex + x, ey + y]))  # Top-left
                        landmarks.append(np.array([ex + x + ew//3, ey + y]))  # Top-third
                        landmarks.append(np.array([ex + x + 2*ew//3, ey + y]))  # Top-two-thirds
                        landmarks.append(np.array([ex + x + ew, ey + y]))  # Top-right
                        landmarks.append(np.array([ex + x + ew//2, ey + y + eh//2]))  # Center
                        landmarks.append(np.array([ex + x + ew//2, ey + y + eh]))  # Bottom-center
                    return np.array(landmarks)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in face landmark detection: {str(e)}")
            return None

def load_model(weights_path):
    """
    Load the YOLOv5 model from the specified weights path.
    
    Args:
        weights_path (str): Path to the model weights.
    
    Returns:
        model: The loaded YOLOv5 model.
    """
    logger.info(f'Loading model from {weights_path}...')
    try:
        return torch.hub.load('ultralytics/yolov5', 'custom', path=weights_path, force_reload=True)
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

def detect_image(model, url):
    """
    Detect objects in an image from a URL and display the results.
    
    Args:
        model: The YOLOv5 model.
        url (str): URL of the image to test.
    """
    logger.info('Downloading test image…')
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert('RGB')
        results = model(img)                 # inference
        results.print()                     # print results to console
        # display:
        rendered = np.squeeze(results.render())
        cv2.imshow('Test Image Detection', cv2.cvtColor(rendered, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except requests.RequestException as e:
        logger.error(f"Failed to download image: {e}")
    except Exception as e:
        logger.error(f"Error during image detection: {e}")

def real_time_detection(model, alarm_path):
    """
    Perform real-time drowsiness detection using the webcam and play an alarm if drowsiness is detected.
    
    Args:
        model: The YOLOv5 model.
        alarm_path (str): Path to the alarm sound file.
    """
    # init pygame mixer for alarm
    pygame.mixer.init()
    alarm_playing = False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error('Cannot open webcam')
        raise RuntimeError('Cannot open webcam')
    logger.info('Starting webcam stream. Press Q to quit.')

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to grab frame")
                break

            results = model(frame)
            # get list of detected class names
            labels = results.pandas().xyxy[0]['name'].tolist()

            # if drowsy detected → alarm
            if 'drowsy' in labels and not alarm_playing:
                logger.warning('⚠️  Drowsiness detected! Playing alarm.')
                pygame.mixer.music.load(alarm_path)
                pygame.mixer.music.play()
                alarm_playing = True
            elif 'drowsy' not in labels and alarm_playing:
                pygame.mixer.music.stop()
                alarm_playing = False

            # render and show
            rendered = np.squeeze(results.render())
            cv2.imshow('Drowsiness Detection', cv2.cvtColor(rendered, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Drowsiness Detection using YOLOv5')
    parser.add_argument('--weights', type=str, default=DEFAULT_WEIGHTS, help='Path to model weights')
    parser.add_argument('--test-img', type=str, default=DEFAULT_TEST_IMG_URL, help='URL for test image')
    parser.add_argument('--alarm', type=str, default=DEFAULT_ALARM_PATH, help='Path to alarm sound file')
    args = parser.parse_args()

    model = load_model(args.weights)
    # 1) Quick test on a static image:
    detect_image(model, args.test_img)
    # 2) Then real-time webcam with alarm:
    real_time_detection(model, args.alarm)

if __name__ == '__main__':
    main()
