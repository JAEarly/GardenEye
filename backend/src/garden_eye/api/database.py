"""Database models and operations for GardenEye."""

import os
from pathlib import Path

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    fn,
)

from garden_eye import DATABASE_PATH, THUMBNAIL_DIR
from garden_eye.helpers import is_target_coco_annotation
from garden_eye.log import get_logger

logger = get_logger(__name__)


class PathField(CharField):
    """Custom Peewee field for storing pathlib.Path objects as strings."""

    def db_value(self, path: Path) -> str:
        """Convert Path to string for database storage."""
        return os.fspath(path)

    def python_value(self, str_path: str) -> Path:
        """Convert database string back to Path object."""
        return Path(str_path)


class VideoFile(Model):
    """Database model for video file metadata."""

    id = AutoField()
    path = PathField(unique=True)  # Path
    size = IntegerField()  # Size in bytes
    modified = FloatField()  # Modification time in seconds
    annotated = BooleanField(default=False)  # Whether annotations have been processed
    is_night = BooleanField(default=False)  # Whether this video is a night-time (black-and-white) recording
    wildlife_prop = FloatField(default=0)  # The proportion of frames that contain a wildlife annotation


class Annotation(Model):
    """Database model for object detection annotations."""

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
    """
    Initialize and configure the SQLite database.

    Args:
        db_path: Path to SQLite database file
    """
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
    logger.info(f"Loaded database with {len(VideoFile)} files")
    return db


def get_video_objects(video_file: VideoFile, filter_person: bool = False) -> list[str]:
    """
    Get unique detected objects in a video, ordered by frequency.

    Args:
        video_file: VideoFile instance to query
        filter_person: Whether to exclude videos containing only "person" annotations
    """
    # Use SQL aggregation to count annotations by object name and sort by frequency
    objs = (
        Annotation.select(Annotation.name, fn.COUNT().alias("count"))
        .where(Annotation.video_file == video_file)
        .group_by(Annotation.name)
        .order_by(fn.COUNT().desc())
    )
    obj_names = [obj.name for obj in objs if is_target_coco_annotation(obj.name)]
    if filter_person and obj_names == ["person"]:
        return []
    return obj_names


def get_thumbnail_path(video_file: VideoFile) -> Path:
    """
    Get the thumbnail file path for a video.

    Args:
        video_file: VideoFile instance
    """
    return THUMBNAIL_DIR / f"{video_file.id}.jpg"
