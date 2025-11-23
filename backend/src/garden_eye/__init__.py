"""GardenEye package configuration and path definitions."""

from pathlib import Path

from garden_eye.config import Config
from garden_eye.log import get_logger

logger = get_logger(__file__)


from functools import cache


@cache
def config() -> Config:
    return Config.load()


@cache
def raw_dir() -> Path:
    return config().data_root / "raw"


@cache
def weights_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "weights"


@cache
def static_root() -> Path:
    return Path(__file__).resolve().parents[3] / "frontend" / "static"


THUMBNAIL_DIR = config.data_root / "thumbnails"
DATABASE_PATH = config.data_root / "database.db"
