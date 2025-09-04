import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from peewee import SqliteDatabase

from app.database import init_database


@pytest.fixture
def test_db(tmp_path: Path) -> Generator[SqliteDatabase, None, None]:
    """Create an in-memory test database."""
    # Create a temporary database file for testing
    test_db_path = tmp_path / "test.db"
    try:
        test_database = init_database(test_db_path)
        yield test_database
        test_database.close()
    finally:
        # Clean up the temporary database file
        if test_db_path.exists():
            test_db_path.unlink()


@pytest.fixture
def temp_video_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test video files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_video_file(temp_video_dir: Path) -> Path:
    """Create a mock video file for testing."""
    video_path = temp_video_dir / "sample.MP4"
    # Create a minimal fake video file
    video_path.write_bytes(b"fake video content")
    return video_path
