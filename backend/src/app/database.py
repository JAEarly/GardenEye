import os
from pathlib import Path

from peewee import CharField, FloatField, IntegerField, Model, SqliteDatabase

from app import DATA_DIR, DATABASE_PATH
from app.log import get_logger

logger = get_logger(__name__)


class PathField(CharField):
    def db_value(self, path: Path) -> str:
        return os.fspath(path)

    def python_value(self, str_path: str) -> Path:
        return Path(str_path)


class VideoFile(Model):
    path = PathField(unique=True)  # Path
    size = IntegerField()  # Size in bytes
    modified = FloatField()  # Modification time in seconds
    # Score between 0 (no movement) and 1 (maximum movement). -1 indicates not computed.
    movement = FloatField(default=-1)


def init_database(db_path: Path = DATABASE_PATH) -> SqliteDatabase:
    logger.info(f"Initialising database with {db_path=}")
    db = SqliteDatabase(db_path)
    db.connect()
    db.bind([VideoFile])
    db.create_tables([VideoFile])
    return db


def add_files(video_dir: Path = DATA_DIR) -> None:
    logger.info("Adding files...")
    data = []
    for path in video_dir.glob("**/*.MP4"):
        if "_movement" in path.stem:
            continue
        st = path.stat()
        data.append({"path": path, "size": st.st_size, "modified": st.st_mtime})
    VideoFile.insert_many(data).on_conflict_ignore().execute()
