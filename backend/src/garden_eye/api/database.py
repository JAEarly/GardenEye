import os
from pathlib import Path

from peewee import BooleanField, CharField, FloatField, ForeignKeyField, IntegerField, Model, SqliteDatabase, fn

from garden_eye import DATA_DIR, DATABASE_PATH, THUMBNAIL_DIR
from garden_eye.api.log import get_logger

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
    annotated = BooleanField(default=False)  # Whether annotations have been processed


class Annotation(Model):
    video_file = ForeignKeyField(VideoFile, backref="annotations")
    frame_idx = IntegerField()
    name = CharField()  # Object class name (e.g., "dog")
    class_id = IntegerField()  # Numeric class ID
    confidence = FloatField()
    x1 = FloatField()  # Bounding box coordinates
    y1 = FloatField()
    x2 = FloatField()
    y2 = FloatField()


def init_database(db_path: Path = DATABASE_PATH) -> SqliteDatabase:
    logger.info(f"Initialising database with {db_path=}")
    db = SqliteDatabase(db_path)
    db.connect()
    # Add tables
    db.bind([VideoFile, Annotation])
    db.create_tables([VideoFile, Annotation])
    # Add indexes for better query performance
    db.execute_sql("CREATE INDEX IF NOT EXISTS idx_annotation_video_frame ON annotation (video_file_id, frame_idx)")
    db.execute_sql("CREATE INDEX IF NOT EXISTS idx_annotation_video_name ON annotation (video_file_id, name)")
    db.execute_sql("CREATE INDEX IF NOT EXISTS idx_annotation_confidence ON annotation (confidence)")
    return db


def add_files(video_dir: Path = DATA_DIR) -> None:
    logger.info("Adding files...")
    data = []
    for path in video_dir.glob("**/*.MP4"):
        st = path.stat()
        data.append({"path": path, "size": st.st_size, "modified": st.st_mtime})
    VideoFile.insert_many(data).on_conflict_ignore().execute()


def get_video_objects(video_file: VideoFile) -> list[str]:
    """Gets the list of unique objects in a particular video, ordered by frequency, e.g. `("dog", "cat", "person")`."""
    # Use SQL aggregation to count annotations by object name and sort by frequency
    objects = (
        Annotation.select(Annotation.name, fn.COUNT().alias("count"))
        .where(Annotation.video_file == video_file)
        .group_by(Annotation.name)
        .order_by(fn.COUNT().desc())
    )

    # Return as ordered set (preserves frequency-based ordering when converted to list)
    return [obj.name for obj in objects]


def get_thumbnail_path(video_path: Path) -> Path:
    return THUMBNAIL_DIR / f"{video_path.stem}.jpg"
