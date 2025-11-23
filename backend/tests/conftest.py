import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from peewee import SqliteDatabase

from garden_eye.config import Config


@pytest.fixture(autouse=True)
def test_config(tmp_path: Path) -> None:
    config = Config(data_root=tmp_path)
    patch("garden_eye.config.Config.load", side_effect=config)


@pytest.fixture
def test_db(tmp_path: Path) -> Generator[SqliteDatabase]:
    """Create an in-memory test database."""
    # Lazy import to ensure config is patch first
    from garden_eye.api.database import init_database

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
def temp_video_dir() -> Generator[Path]:
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
