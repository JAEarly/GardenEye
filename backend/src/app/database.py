import os
from pathlib import Path
from typing import Final

from peewee import CharField, FloatField, IntegerField, Model, SqliteDatabase

from app import DATA_DIR, DATABASE_PATH

# Config
DB: Final[SqliteDatabase] = SqliteDatabase(DATABASE_PATH)
DATA_ROOT: Final[Path] = DATA_DIR


class PathField(CharField):
    def db_value(self, path: Path) -> str:
        rel_path = path.relative_to(DATA_ROOT)
        return os.fspath(rel_path)

    def python_value(self, str_path: str) -> Path:
        return DATA_ROOT / str_path


class VideoFile(Model):
    path = PathField(unique=True)  # Path
    size = IntegerField()  # Size in bytes
    modified = FloatField()  # Modification time in seconds

    class Meta:
        database = DB


def init_database() -> SqliteDatabase:
    DB.connect()
    DB.create_tables([VideoFile])
    return DB


def add_files() -> None:
    data = []
    for path in DATA_ROOT.glob("**/*.MP4"):
        st = path.stat()
        data.append({"path": path, "size": st.st_size, "modified": st.st_mtime})
    (VideoFile.insert_many(data).on_conflict_ignore().execute())


if __name__ == "__main__":
    init_database()
    add_files()
