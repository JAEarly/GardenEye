from pathlib import Path

from fastapi.testclient import TestClient
from peewee import SqliteDatabase

from garden_eye.api.database import Annotation, VideoFile
from garden_eye.api.main import app, get_annotations, list_videos


def test__index_endpoint__returns_html_file() -> None:
    client = TestClient(app)
    response = client.get("/")
    # Should attempt to return file, even if mocked
    assert response.status_code in [200]


def test__list_videos__empty_database(test_db: SqliteDatabase) -> None:
    result = list_videos()
    assert result == []


def test__list_videos__returns_sample_data(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    # Insert test video
    VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0)
    result = list_videos()
    assert len(result) == 1
    assert result[0].name == "sample.MP4"
    assert result[0].size == len("fake video content")


def test__list_videos__with_filter_person_false(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    # Insert test video
    video = VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0)
    # Add person annotation only
    Annotation.create(
        video_file=video, frame_idx=0, name="person", class_id=0, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
    )
    result = list_videos(filter_person=False)
    assert len(result) == 1
    assert result[0].objects == ["person"]


def test__list_videos__with_filter_person_true(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    # Insert test video
    video = VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0)
    # Add person annotation only
    Annotation.create(
        video_file=video, frame_idx=0, name="person", class_id=0, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
    )

    result = list_videos(filter_person=True)
    assert len(result) == 1
    assert result[0].objects == []  # Should be empty due to filter_person=True


def test__list_videos__filter_person_with_mixed_objects(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    # Insert test video
    video = VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0)
    # Add person and dog annotations
    Annotation.create(
        video_file=video, frame_idx=0, name="person", class_id=0, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
    )
    Annotation.create(
        video_file=video, frame_idx=1, name="dog", class_id=16, confidence=0.9, x1=15.0, y1=25.0, x2=55.0, y2=65.0
    )
    result = list_videos(filter_person=True)
    assert len(result) == 1
    assert "person" in result[0].objects
    assert "dog" in result[0].objects


def test__api_videos_endpoint__with_filter_person_parameter(test_db: SqliteDatabase) -> None:
    client = TestClient(app)
    # Test without parameter
    response = client.get("/api/videos")
    assert response.status_code == 200
    # Test with filter_person=false
    response = client.get("/api/videos?filter_person=false")
    assert response.status_code == 200
    # Test with filter_person=true
    response = client.get("/api/videos?filter_person=true")
    assert response.status_code == 200


def test__get_annotations__returns_filtered_annotations(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    # Insert test video
    video = VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0)

    # Add target and non-target annotations
    Annotation.create(
        video_file=video, frame_idx=0, name="dog", class_id=16, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
    )
    Annotation.create(
        video_file=video, frame_idx=1, name="chair", class_id=56, confidence=0.7, x1=30.0, y1=40.0, x2=70.0, y2=80.0
    )  # chair is not in COCO_TARGET_LABELS

    result = get_annotations(video.id)

    assert len(result) == 1  # Only the dog annotation should be included
    assert result[0].name == "dog"
    assert result[0].frame_idx == 0
    assert result[0].confidence == 0.8


def test__api_annotations_endpoint(test_db: SqliteDatabase, sample_video_file: Path) -> None:
    client = TestClient(app)

    # Insert test video
    video = VideoFile.create(path=sample_video_file, size=len("fake video content"), modified=1234567890.0)

    # Add annotation
    Annotation.create(
        video_file=video, frame_idx=0, name="dog", class_id=16, confidence=0.8, x1=10.0, y1=20.0, x2=50.0, y2=60.0
    )

    response = client.get(f"/api/annotations/{video.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "dog"
