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
