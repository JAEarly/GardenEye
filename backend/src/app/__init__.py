from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
WEIGHTS_DIR = BASE_DIR / "weights"
STATIC_ROOT = BASE_DIR / "frontend" / "static"
DATABASE_PATH = DATA_DIR / "database.db"
