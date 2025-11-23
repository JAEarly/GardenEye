"""GardenEye package configuration and path definitions."""

from pathlib import Path

from garden_eye.config import config
from garden_eye.log import get_logger

logger = get_logger(__file__)


# Local disk
BASE_DIR = Path(__file__).resolve().parents[3]
WEIGHTS_DIR = BASE_DIR / "weights"
STATIC_ROOT = BASE_DIR / "frontend" / "static"

DATA_DIR = config.data_root
if not DATA_DIR.exists():
    logger.warning(f"Data directory not found at {DATA_DIR}")
RAW_DATA_DIR = DATA_DIR / "raw"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
DATABASE_PATH = DATA_DIR / "database.db"
