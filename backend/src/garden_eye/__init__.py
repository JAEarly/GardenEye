"""GardenEye package configuration and path definitions."""

from pathlib import Path

from garden_eye.log import get_logger

logger = get_logger(__file__)

# Local disk
BASE_DIR = Path(__file__).resolve().parents[3]
WEIGHTS_DIR = BASE_DIR / "weights"
STATIC_ROOT = BASE_DIR / "frontend" / "static"

# External hard drive
EXTERNAL_PATH = Path("/media/jearly/Seagate Expansion Drive")
if not EXTERNAL_PATH.exists():
    logger.warning(f"External drive not found at {EXTERNAL_PATH}")
DATA_DIR = EXTERNAL_PATH / "gardeneye"
RAW_DATA_DIR = DATA_DIR / "raw"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
DATABASE_PATH = DATA_DIR / "database.db"
