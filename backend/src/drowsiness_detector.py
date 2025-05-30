import cv2
import numpy as np
from scipy.spatial import distance
import time
import logging
from typing import Tuple, Dict, List, Optional
import threading
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DetectionResult:
    is_drowsy: bool
    ear: float
    mar: float
    blink_rate: float
    confidence: float
    face_detected: bool
    timestamp: datetime

class DrowsinessDetector:
    def __init__(self, 
                 ear_threshold: float = 0.20,
                 mar_threshold: float = 0.30,
                 consecutive_frames: int = 3,
                 blink_threshold: float = 0.15,
                 yawn_threshold: float = 0.35):
        # Initialize face and eye cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Detection parameters
        self.EAR_THRESHOLD = ear_threshold
        self.MAR_THRESHOLD = mar_threshold
        self.CONSECUTIVE_FRAMES = consecutive_frames
        self.BLINK_THRESHOLD = blink_threshold
        self.YAWN_THRESHOLD = yawn_threshold
        
        # State variables
        self.consecutive_frames_count = 0
        self.last_blink_time = time.time()
        self.blink_count = 0
        self.session_start_time = time.time()
        self.ear_history: List[float] = []
        self.mar_history: List[float] = []
        self.detection_history: List[DetectionResult] = []
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def calculate_ear(self, eye_points: np.ndarray) -> float:
        """Calculate Eye Aspect Ratio (EAR) from eye landmarks."""
        try:
            # Calculate vertical distances
            v1 = distance.euclidean(eye_points[1], eye_points[5])
            v2 = distance.euclidean(eye_points[2], eye_points[4])
            
            # Calculate horizontal distance
            h = distance.euclidean(eye_points[0], eye_points[3])
            
            # Calculate EAR
            ear = (v1 + v2) / (2.0 * h)
            return ear
        except Exception as e:
            self.logger.error(f"Error calculating EAR: {str(e)}")
            return 0.0

    def calculate_mar(self, mouth_points: np.ndarray) -> float:
        """Calculate Mouth Aspect Ratio (MAR) from mouth landmarks."""
        try:
            # Calculate vertical distances
            v1 = distance.euclidean(mouth_points[1], mouth_points[7])
            v2 = distance.euclidean(mouth_points[2], mouth_points[6])
            v3 = distance.euclidean(mouth_points[3], mouth_points[5])
            
            # Calculate horizontal distance
            h = distance.euclidean(mouth_points[0], mouth_points[4])
            
            # Calculate MAR
            mar = (v1 + v2 + v3) / (2.0 * h)
            return mar
        except Exception as e:
            self.logger.error(f"Error calculating MAR: {str(e)}")
            return 0.0

    def get_eye_landmarks(self, eye_region: np.ndarray) -> Optional[np.ndarray]:
        """Extract eye landmarks using contour detection."""
        try:
            # Convert to grayscale
            gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray_eye, 30, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
                
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get convex hull
            hull = cv2.convexHull(largest_contour)
            
            # Get extreme points
            leftmost = tuple(hull[hull[:, :, 0].argmin()][0])
            rightmost = tuple(hull[hull[:, :, 0].argmax()][0])
            topmost = tuple(hull[hull[:, :, 1].argmin()][0])
            bottommost = tuple(hull[hull[:, :, 1].argmax()][0])
            
            # Return landmarks
            return np.array([leftmost, topmost, rightmost, bottommost])
        except Exception as e:
            self.logger.error(f"Error getting eye landmarks: {str(e)}")
            return None

    def detect_drowsiness(self, frame: np.ndarray) -> DetectionResult:
        """Detect drowsiness in the given frame."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return DetectionResult(
                    is_drowsy=False,
                    ear=0.0,
                    mar=0.0,
                    blink_rate=0.0,
                    confidence=0.0,
                    face_detected=False,
                    timestamp=datetime.now()
                )
            
            # Process the largest face
            face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = face
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(face_roi)
            
            if len(eyes) < 2:
                return DetectionResult(
                    is_drowsy=False,
                    ear=0.0,
                    mar=0.0,
                    blink_rate=0.0,
                    confidence=0.0,
                    face_detected=True,
                    timestamp=datetime.now()
                )
            
            # Process each eye
            ear_values = []
            for (ex, ey, ew, eh) in eyes:
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                landmarks = self.get_eye_landmarks(eye_roi)
                if landmarks is not None:
                    ear = self.calculate_ear(landmarks)
                    ear_values.append(ear)
            
            # Calculate average EAR
            avg_ear = np.mean(ear_values) if ear_values else 0.0
            
            # Update blink detection
            current_time = time.time()
            if avg_ear < self.BLINK_THRESHOLD:
                if current_time - self.last_blink_time > 0.3:  # Minimum time between blinks
                    self.blink_count += 1
                    self.last_blink_time = current_time
            
            # Calculate blink rate (blinks per minute)
            session_duration = (current_time - self.session_start_time) / 60.0
            blink_rate = self.blink_count / session_duration if session_duration > 0 else 0
            
            # Update consecutive frames count
            with self._lock:
                if avg_ear < self.EAR_THRESHOLD:
                    self.consecutive_frames_count += 1
                else:
                    self.consecutive_frames_count = 0
                
                # Update history
                self.ear_history.append(avg_ear)
                if len(self.ear_history) > 30:  # Keep last 30 frames
                    self.ear_history.pop(0)
            
            # Calculate confidence based on history
            confidence = 1.0 - (np.std(self.ear_history) if self.ear_history else 0.0)
            
            # Create detection result
            result = DetectionResult(
                is_drowsy=self.consecutive_frames_count >= self.CONSECUTIVE_FRAMES,
                ear=avg_ear,
                mar=0.0,  # MAR calculation can be added if needed
                blink_rate=blink_rate,
                confidence=confidence,
                face_detected=True,
                timestamp=datetime.now()
            )
            
            # Update detection history
            self.detection_history.append(result)
            if len(self.detection_history) > 100:  # Keep last 100 detections
                self.detection_history.pop(0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in detect_drowsiness: {str(e)}")
            return DetectionResult(
                is_drowsy=False,
                ear=0.0,
                mar=0.0,
                blink_rate=0.0,
                confidence=0.0,
                face_detected=False,
                timestamp=datetime.now()
            )

    def get_session_stats(self) -> Dict:
        """Get current session statistics."""
        with self._lock:
            return {
                'duration': time.time() - self.session_start_time,
                'blink_count': self.blink_count,
                'blink_rate': self.blink_count / ((time.time() - self.session_start_time) / 60.0),
                'drowsy_count': sum(1 for d in self.detection_history if d.is_drowsy),
                'avg_confidence': np.mean([d.confidence for d in self.detection_history]) if self.detection_history else 0.0,
                'avg_ear': np.mean([d.ear for d in self.detection_history]) if self.detection_history else 0.0
            }

    def reset_session(self):
        """Reset session statistics."""
        with self._lock:
            self.session_start_time = time.time()
            self.blink_count = 0
            self.consecutive_frames_count = 0
            self.ear_history.clear()
            self.mar_history.clear()
            self.detection_history.clear() 