"""GardenEye package configuration and path definitions."""

from functools import cache
from pathlib import Path

from garden_eye.config import Config
from garden_eye.log import get_logger

logger = get_logger(__file__)


@cache
def config() -> Config:
    """Load and cache the GardenEye configuration."""
    return Config.load()


@cache
def raw_dir() -> Path:
    """Get the path to the raw video directory."""
    return config().data_root / "raw"


@cache
def weights_dir() -> Path:
    """Get the path to the YOLO weights directory."""
    return Path(__file__).resolve().parents[3] / "weights"


@cache
def static_root() -> Path:
    """Get the path to the frontend static files directory."""
    return Path(__file__).resolve().parents[3] / "frontend" / "static"


@cache
def thumbnail_dir() -> Path:
    """Get the path to the thumbnails directory."""
    return config().data_root / "thumbnails"


@cache
def database_path() -> Path:
    """Get the path to the database file."""
    return config().data_root / "database.db"
