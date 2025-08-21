import os
import csv
import logging
import uuid
import requests
from tqdm import tqdm
from pathlib import Path
from api import shared_multimodal_db  # Your LanceDB instance

# --- Logging ---
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Config ---
CSV_FILE = "./datasets/open_images_csv/images.csv"
IMAGE_DIR = "./datasets/open_images_sample"
START_index=501
End_index=1500
SAMPLE_SIZE = End_index - START_index + 1  # Total rows to process
HOST_URL= "http://localhost:8008"  # Adjust if needed
os.makedirs(IMAGE_DIR, exist_ok=True)

def main():
    logger.info(f"📥 Reading first {SAMPLE_SIZE} rows from {CSV_FILE}...")
    entries = []
    rows_loaded = 0

    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)  # Use default comma delimiter
            
        for idx, row in enumerate(reader):
            if idx < START_index:
                continue
            if idx > End_index:
                break
            logger.debug(f"Row {idx}: {row}")

            original_url = row.get("OriginalURL")
            image_id = row.get("ImageID")
            author = row.get("Author", "Unknown")
            title = row.get("Title", "")
            flickr_url = row.get("OriginalLandingURL", "")

            if not original_url or not image_id:
                logger.warning(f"Skipping row {idx} due to missing OriginalURL or ImageID.")
                continue

            try:
                description = f"Image by {author}, titled '{title}'. Source: {flickr_url}"

                local_path = Path(IMAGE_DIR) / f"{image_id}.jpg"
                if not local_path.exists():
                    # continue
                    resp = requests.get(original_url, timeout=10)
                    if resp.status_code == 200:
                        with open(local_path, "wb") as f:
                            f.write(resp.content)
                        logger.info(f"Downloaded image {image_id}")
                    else:
                        logger.warning(f"Failed to download {original_url} (status {resp.status_code})")
                        continue

                entries.append({
                    "pk": str(uuid.uuid4().hex),
                    "text": description,
                    "image_path": f"{HOST_URL}/extra_images/{local_path.name}",
                    "file_path": str(local_path)
                })
                rows_loaded += 1
            except Exception as e:
                logger.error(f"Error processing row {idx}: {e}")
                continue

    if not entries:
        logger.error("❌ No valid entries to ingest into LanceDB.")
        return

    logger.info(f"✅ Download complete. Ingesting {rows_loaded} entries into LanceDB...")
    shared_multimodal_db.add_entries(entries)
    logger.info("✔ Done.")

if __name__ == "__main__":
    main()
