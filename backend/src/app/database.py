import os
from pathlib import Path
from typing import Final

from peewee import CharField, FloatField, IntegerField, Model, SqliteDatabase

from app import DATA_DIR, DATABASE_PATH
from app.log import get_logger

logger = get_logger(__name__)

DB: Final[SqliteDatabase] = SqliteDatabase(DATABASE_PATH)


class PathField(CharField):
    def db_value(self, path: Path) -> str:
        return os.fspath(path)

    def python_value(self, str_path: str) -> Path:
        return Path(str_path)


class VideoFile(Model):
    path = PathField(unique=True)  # Path
    size = IntegerField()  # Size in bytes
    modified = FloatField()  # Modification time in seconds

    class Meta:
        database = DB


def init_database() -> SqliteDatabase:
    logger.info(f"Initialising database from {DATABASE_PATH}")
    DB.connect()
    DB.create_tables([VideoFile])
    return DB


def add_files() -> None:
    logger.info("Adding files...")
    data = []
    for path in DATA_DIR.glob("**/*.MP4"):
        st = path.stat()
        data.append({"path": path, "size": st.st_size, "modified": st.st_mtime})
    (VideoFile.insert_many(data).on_conflict_ignore().execute())
