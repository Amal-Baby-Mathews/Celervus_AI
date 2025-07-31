import os
import logging
import requests
from pathlib import Path

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Config ---
CSV_DIR = "./datasets/open_images_csv"
FILES = {
    "images": "https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable.csv",
    "labels": "https://storage.googleapis.com/openimages/2018_04/train/train-annotations-human-imagelabels.csv",
    "class_map": "https://storage.googleapis.com/openimages/2018_04/class-descriptions-boxable.csv"
}

# --- Ensure Directory ---
os.makedirs(CSV_DIR, exist_ok=True)

def download_file(url: str, dest: Path):
    """Download a file from URL to destination path (with streaming)."""
    if dest.exists():
        logger.info(f"✅ {dest.name} already exists. Skipping download.")
        return
    try:
        logger.info(f"📥 Downloading {dest.name} ...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(f"✔ Completed: {dest.name}")
    except Exception as e:
        logger.error(f"❌ Failed to download {url}: {e}")

def main():
    logger.info("📦 Preparing Open Images CSV files...")
    for name, url in FILES.items():
        dest_path = Path(CSV_DIR) / f"{name}.csv"
        download_file(url, dest_path)
    logger.info("✅ All CSV files are ready in ./datasets/open_images_csv")

if __name__ == "__main__":
    main()
