from pathlib import Path

from fastapi.testclient import TestClient
from peewee import SqliteDatabase

from app.database import VideoFile
from app.main import app


def test__index_endpoint__returns_html_file() -> None:
    """Test the index endpoint returns HTML file."""
    client = TestClient(app)
    response = client.get("/")
    # Should attempt to return file, even if mocked
    assert response.status_code in [200]


def test__list_videos__empty_database(test_db: SqliteDatabase) -> None:
    """Test list videos function with empty database."""
    from app.main import list_videos

    result = list_videos()
    assert result == []


def test__list_videos__returns_sample_data(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    """Test list videos function with sample data."""
    from app.main import list_videos

    # Insert test video
    VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0, movement=0.5)

    result = list_videos()
    assert len(result) == 1
    assert result[0].name == "sample.MP4"
    assert result[0].size == len("fake video content")
