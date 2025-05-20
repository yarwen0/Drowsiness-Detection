import os
import cv2
import sys
import argparse
import logging
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── CONFIG ─────────────────────────────────────────────────────────
# Default paths and settings loaded from .env
DEFAULT_BASE = os.getenv('BASE', 'data')
DEFAULT_IMG_DIR = os.path.join(DEFAULT_BASE, 'images')
DEFAULT_LBL_DIR = os.path.join(DEFAULT_BASE, 'labels')
DEFAULT_SPLITS = os.getenv('SPLITS', 'train,val').split(',')
DEFAULT_CLASSES = os.getenv('LABELS', 'awake,drowsy').split(',')
DEFAULT_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
# ──────────────────────────────────────────────────────────────────

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_face_cascade(cascade_path):
    """
    Load the face detection cascade classifier.
    
    Args:
        cascade_path (str): Path to the cascade file.
    
    Returns:
        cv2.CascadeClassifier: The loaded cascade classifier.
    """
    if not os.path.isfile(cascade_path):
        logger.error(f"❌ ERROR: Cascade file not found: {cascade_path}")
        sys.exit(1)
    return cv2.CascadeClassifier(cascade_path)

def process_split(split, img_dir, lbl_dir, classes, face_cascade):
    """
    Process a dataset split (train/val) and generate annotations.
    
    Args:
        split (str): Dataset split name (e.g., 'train', 'val').
        img_dir (str): Base directory for images.
        lbl_dir (str): Base directory for labels.
        classes (list): List of class names.
        face_cascade (cv2.CascadeClassifier): Face detection cascade.
    """
    logger.info(f"\n— Processing split: {split} —")
    out_folder = os.path.join(lbl_dir, split)
    os.makedirs(out_folder, exist_ok=True)

    for cls_idx, cls_name in enumerate(classes):
        img_folder = os.path.join(img_dir, split, cls_name)
        logger.info(f"  Class '{cls_name}' (idx={cls_idx}) folder: {img_folder}")

        if not os.path.isdir(img_folder):
            logger.warning(f"   ⚠️  Folder does not exist: {img_folder}")
            continue

        images = [f for f in os.listdir(img_folder)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        logger.info(f"   Found {len(images)} image(s): {images}")

        if not images:
            continue

        for fname in tqdm(images, desc=f"Processing {cls_name} images"):
            img_path = os.path.join(img_folder, fname)
            img = cv2.imread(img_path)
            if img is None:
                logger.error(f"     ❌ Failed to load image: {img_path}")
                continue

            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            logger.info(f"     Detected {len(faces)} face(s) in {fname}")

            label_path = os.path.join(out_folder, fname.rsplit('.',1)[0] + '.txt')
            with open(label_path, 'w') as f:
                for (x, y, fw, fh) in faces:
                    x_c = (x + fw/2) / w
                    y_c = (y + fh/2) / h
                    bw  = fw / w
                    bh  = fh / h
                    f.write(f"{cls_idx} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}\n")
            logger.info(f"      → Wrote labels to {label_path}")

def main():
    parser = argparse.ArgumentParser(description='Auto-annotate images for drowsiness detection')
    parser.add_argument('--base', type=str, default=DEFAULT_BASE, help='Base directory for data')
    parser.add_argument('--img-dir', type=str, default=DEFAULT_IMG_DIR, help='Directory for images')
    parser.add_argument('--lbl-dir', type=str, default=DEFAULT_LBL_DIR, help='Directory for labels')
    parser.add_argument('--splits', nargs='+', default=DEFAULT_SPLITS, help='Dataset splits (e.g., train val)')
    parser.add_argument('--classes', nargs='+', default=DEFAULT_CLASSES, help='Class names (e.g., awake drowsy)')
    parser.add_argument('--cascade', type=str, default=DEFAULT_CASCADE_PATH, help='Path to face cascade file')
    args = parser.parse_args()

    logger.info("🐍 Starting auto_annotate.py")
    logger.info(f" Cascade path: {args.cascade}")

    face_cascade = load_face_cascade(args.cascade)
    for split in args.splits:
        process_split(split, args.img_dir, args.lbl_dir, args.classes, face_cascade)

    logger.info("\n✅ auto_annotate complete!")

if __name__ == '__main__':
    main()
