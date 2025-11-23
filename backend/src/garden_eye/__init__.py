"""GardenEye package configuration and path definitions."""

from pathlib import Path

# Local disk
BASE_DIR = Path(__file__).resolve().parents[3]
WEIGHTS_DIR = BASE_DIR / "weights"
STATIC_ROOT = BASE_DIR / "frontend" / "static"

# External hard drive
EXTERNAL_PATH = Path("/media/jearly/Seagate Expansion Drive")
if not EXTERNAL_PATH.exists():
    raise RuntimeError("External drive not found")
DATA_DIR = EXTERNAL_PATH / "gardeneye"
RAW_DATA_DIR = DATA_DIR / "raw"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
DATABASE_PATH = DATA_DIR / "database.db"

# Output dirs so ensure created
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
