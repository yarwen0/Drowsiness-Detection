import cv2, os, time, uuid, argparse, logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── CONFIG ─────────────────────────────────────────────────────────
# Default paths and settings loaded from .env
DEFAULT_BASE = os.getenv('BASE', 'data/images')
DEFAULT_SPLITS = os.getenv('SPLITS', 'train,val').split(',')
DEFAULT_LABELS = os.getenv('LABELS', 'awake,drowsy').split(',')
DEFAULT_COUNTS = {
    'train': int(os.getenv('COUNTS_TRAIN', 50)),
    'val': int(os.getenv('COUNTS_VAL', 10))
}
DEFAULT_DELAY = int(os.getenv('DELAY', 1))  # seconds between shots
# ──────────────────────────────────────────────────────────────────

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_images(base, splits, labels, counts, delay):
    """
    Capture images from the webcam for each split and label.
    
    Args:
        base (str): Base directory for images.
        splits (list): List of dataset splits (e.g., ['train', 'val']).
        labels (list): List of class labels (e.g., ['awake', 'drowsy']).
        counts (dict): Dictionary mapping splits to the number of images to capture.
        delay (int): Delay in seconds between captures.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Cannot open webcam")
        raise RuntimeError("Cannot open webcam")

    for split in splits:
        for label in labels:
            out_dir = os.path.join(base, split, label)
            os.makedirs(out_dir, exist_ok=True)
            logger.info(f"\nCapturing {counts[split]} images of '{label}' for {split}…")
            time.sleep(2)  # Countdown before capturing starts
            for i in range(counts[split]):
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to grab frame")
                    break
                name = f"{label}_{uuid.uuid4().hex[:8]}.jpg"
                path = os.path.join(out_dir, name)
                cv2.imwrite(path, frame)
                logger.info(f" Saved {path} ({i+1}/{counts[split]})")
                cv2.imshow("Capturing… Press Q to quit", frame)
                if cv2.waitKey(int(delay*1000)) & 0xFF == ord('q'):
                    break
    cap.release()
    cv2.destroyAllWindows()
    logger.info("Done.")

def main():
    parser = argparse.ArgumentParser(description='Capture images for drowsiness detection')
    parser.add_argument('--base', type=str, default=DEFAULT_BASE, help='Base directory for images')
    parser.add_argument('--splits', nargs='+', default=DEFAULT_SPLITS, help='Dataset splits (e.g., train val)')
    parser.add_argument('--labels', nargs='+', default=DEFAULT_LABELS, help='Class labels (e.g., awake drowsy)')
    parser.add_argument('--counts', type=dict, default=DEFAULT_COUNTS, help='Dictionary mapping splits to counts')
    parser.add_argument('--delay', type=int, default=DEFAULT_DELAY, help='Delay in seconds between captures')
    args = parser.parse_args()

    capture_images(args.base, args.splits, args.labels, args.counts, args.delay)

if __name__ == '__main__':
    main()
