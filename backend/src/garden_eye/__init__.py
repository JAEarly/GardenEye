"""GardenEye package configuration and path definitions."""

from pathlib import Path

from garden_eye.config import Config
from garden_eye.log import get_logger

logger = get_logger(__file__)

config = Config.load()
print(config)

# Local disk
BASE_DIR = Path(__file__).resolve().parents[3]
WEIGHTS_DIR = BASE_DIR / "weights"
STATIC_ROOT = BASE_DIR / "frontend" / "static"

if not config.data_root.exists():
    logger.warning(f"Data directory not found at {config.data_root}")
RAW_DATA_DIR = config.data_root / "raw"
THUMBNAIL_DIR = config.data_root / "thumbnails"
DATABASE_PATH = config.data_root / "database.db"
