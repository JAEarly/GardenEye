"""GardenEye package configuration and path definitions."""

from pathlib import Path

from garden_eye.config import Config
from garden_eye.log import get_logger

logger = get_logger(__file__)


CONFIG = Config.load()

RAW_DIR = CONFIG.data_root / "raw"
WEIGHTS_DIR = Path(__file__).resolve().parents[3] / "weights"
STATIC_ROOT = Path(__file__).resolve().parents[3] / "frontend" / "static"
THUMBNAIL_DIR = CONFIG.data_root / "thumbnails"
DATABASE_PATH = CONFIG.data_root / "database.db"
