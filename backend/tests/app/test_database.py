from pathlib import Path

import pytest
from peewee import IntegrityError, SqliteDatabase

from garden_eye.api.database import Annotation, PathField, VideoFile, get_video_objects, init_database


def test__path_field__converts_between_path_and_string() -> None:
    """Test PathField converts between Path and string."""
    field = PathField()
    test_path = Path("/test/path.mp4")

    # Test db_value conversion
    db_value = field.db_value(test_path)
    assert isinstance(db_value, str)
    assert db_value == "/test/path.mp4"

    # Test python_value conversion
    python_value = field.python_value(db_value)
    assert isinstance(python_value, Path)
    assert python_value == test_path


def test__video_file__creates_record(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test creating VideoFile records."""
    video = VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    assert video.path == sample_video_file
    assert video.size == 1024
    assert video.modified == 1234567890.0


def test__video_file__enforces_unique_path(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test that path field enforces uniqueness."""
    VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    # Should raise IntegrityError on duplicate path
    with pytest.raises(IntegrityError):
        VideoFile.create(path=sample_video_file, size=2048, modified=1234567891.0)


def test__init_database__creates_tables() -> None:
    """Test init_database function creates database and tables."""
    db = init_database(Path(":memory:"))

    # Check that the database is connected
    assert db.is_connection_usable()

    # Check that VideoFile table exists
    assert VideoFile.table_exists()

    db.close()


def test__get_video_objects__returns_unique_object_names(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test get_video_objects returns unique object names for a video."""
    video = VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    # Create annotations with duplicate object names
    Annotation.create(
        video_file=video, frame_idx=0, name="dog", class_id=1, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
    )
    Annotation.create(
        video_file=video, frame_idx=1, name="dog", class_id=1, confidence=0.9, x1=15.0, y1=25.0, x2=55.0, y2=65.0
    )
    Annotation.create(
        video_file=video, frame_idx=2, name="cat", class_id=2, confidence=0.7, x1=30.0, y1=40.0, x2=70.0, y2=80.0
    )

    objects = get_video_objects(video)

    assert len(objects) == 2
    assert "dog" in objects
    assert "cat" in objects


def test__get_video_objects__returns_empty_set_for_video_without_annotations(
    test_db: SqliteDatabase, sample_video_file: Path
) -> None:
    """Test get_video_objects returns empty set for video without annotations."""
    video = VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    objects = get_video_objects(video)

    assert objects == []


def test__get_video_objects__orders_by_annotation_frequency(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test get_video_objects returns objects ordered by annotation frequency."""
    video = VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    # Create annotations with different frequencies: dog=3, cat=1, bird=2
    for i in range(3):
        Annotation.create(
            video_file=video, frame_idx=i, name="dog", class_id=1, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
        )

    Annotation.create(
        video_file=video, frame_idx=3, name="cat", class_id=2, confidence=0.7, x1=30.0, y1=40.0, x2=70.0, y2=80.0
    )

    for i in range(2):
        Annotation.create(
            video_file=video,
            frame_idx=4 + i,
            name="bird",
            class_id=3,
            confidence=0.9,
            x1=20.0,
            y1=30.0,
            x2=60.0,
            y2=70.0,
        )

    objects = get_video_objects(video)

    assert objects == ["dog", "bird", "cat"]
