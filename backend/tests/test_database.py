from pathlib import Path

import pytest
from peewee import IntegrityError, SqliteDatabase

from app.database import PathField, VideoFile, init_database


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
    video = VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0, movement=0.75)

    assert video.path == sample_video_file
    assert video.size == 1024
    assert video.modified == 1234567890.0
    assert video.movement == 0.75


def test__video_file__enforces_unique_path(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test that path field enforces uniqueness."""
    VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    # Should raise IntegrityError on duplicate path
    with pytest.raises(IntegrityError):
        VideoFile.create(path=sample_video_file, size=2048, modified=1234567891.0)


def test__video_file__defaults_movement_to_negative_one(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test default movement score is -1."""
    video = VideoFile.create(path=sample_video_file, size=1024, modified=1234567890.0)

    assert video.movement == -1


def test__init_database__creates_tables() -> None:
    """Test init_database function creates database and tables."""
    db = init_database(Path(":memory:"))

    # Check that the database is connected
    assert db.is_connection_usable()

    # Check that VideoFile table exists
    assert VideoFile.table_exists()

    db.close()


def test__add_files__adds_video_files(test_db: SqliteDatabase, tmp_path: Path) -> None:
    """Test add_files function adds video files to database."""
    from app.database import add_files

    # Create mock video files
    video_dir = tmp_path / "videos"
    video_dir.mkdir()

    video1 = video_dir / "video1.MP4"
    video2 = video_dir / "video2.MP4"
    movement_video = video_dir / "video1_movement.MP4"  # Should be ignored

    video1.write_bytes(b"fake video 1 content")
    video2.write_bytes(b"fake video 2 content")
    movement_video.write_bytes(b"movement video content")

    # Call add_files with the video directory
    add_files(video_dir)

    # Check that only non-movement videos were added
    videos = list(VideoFile.select())
    assert len(videos) == 2

    video_names = {v.path.name for v in videos}
    assert "video1.MP4" in video_names
    assert "video2.MP4" in video_names
    assert "video1_movement.MP4" not in video_names


def test__add_files__skips_existing_files(test_db: SqliteDatabase, tmp_path: Path) -> None:
    """Test add_files function skips existing files."""
    from app.database import add_files

    # Create mock video file
    video_dir = tmp_path / "videos"
    video_dir.mkdir()

    video1 = video_dir / "video1.MP4"
    video1.write_bytes(b"fake video content")

    # Add the file first time
    add_files(video_dir)

    assert VideoFile.select().count() == 1

    # Add files again - should not create duplicates due to on_conflict_ignore
    add_files(video_dir)

    assert VideoFile.select().count() == 1  # Still only 1 file
