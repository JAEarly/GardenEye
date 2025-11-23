"""Data ingestion pipeline for video processing and annotation."""

import logging
import os
import shutil
import subprocess

import torch
from peewee import chunked
from tqdm import tqdm
from ultralytics import YOLO

from garden_eye import RAW_DATA_DIR, WEIGHTS_DIR
from garden_eye.api.database import Annotation, VideoFile, get_thumbnail_path, init_database
from garden_eye.helpers import is_night_video, is_target_coco_annotation
from garden_eye.log import get_logger

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "yolo11m.pt"
MODEL = YOLO(WEIGHTS_DIR / MODEL_NAME)


logger = get_logger(__name__)


def run() -> None:
    """Execute the full data ingestion pipeline."""
    # Setup database
    init_database()
    # Load files into database
    add_files()
    # Annotate and create thumbnails for all files
    for vf in tqdm(VideoFile.select().order_by(VideoFile.path), desc="Ingesting files"):
        annotate(vf)
        create_thumbnail(vf)


def add_files() -> None:
    """Discover and add new video files from data directory to database."""
    logger.info("Adding files...")
    data = []
    for path in RAW_DATA_DIR.glob("**/*.MP4"):
        st = path.stat()
        data.append({"path": path, "size": st.st_size, "modified": st.st_mtime})
    result = VideoFile.insert_many(data).on_conflict_ignore().execute()
    logger.info(f"Added {result} new video files to database")


def annotate(video_file: VideoFile) -> None:
    """
    Run YOLO object detection on video and store annotations.

    Args:
        video_file: VideoFile instance to process
    """
    # Skip if already annotated exists
    if video_file.annotated:
        return
    # Process video and collect annotations
    annotations_data = []
    # Use batch processing with optimized parameters for higher GPU utilization rather than `stream=True`
    logging.disable(logging.WARNING)
    results = MODEL(
        str(video_file.path),
        stream=False,
        batch=64,
        verbose=False,
        workers=4,
        device=DEVICE,
    )
    logging.disable(logging.NOTSET)

    wildlife_frames = set()
    for frame_idx, result in enumerate(results):
        # Process detection results
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                class_id = int(box.cls[0].cpu().numpy())
                name = MODEL.names[class_id]
                # Extract bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                # Add frame to set that contains wildlife
                if is_target_coco_annotation(name):
                    wildlife_frames.add(frame_idx)
                # Collect
                annotations_data.append(
                    {
                        "video_file": video_file.id,
                        "frame_idx": frame_idx,
                        "name": name,
                        "class_id": class_id,
                        "confidence": confidence,
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2),
                    }
                )
    # Bulk insert annotations into database
    if annotations_data:
        with Annotation._meta.database.atomic():  # type: ignore[attr-defined]
            for batch in chunked(annotations_data, 50):  # pick size based on column count
                Annotation.insert_many(batch).execute()
    # Add proportion of annotations that are wildlife matches
    video_file.wildlife_prop = len(wildlife_frames) / len(results)  # type: ignore[assignment]
    # Mark video as annotated (even if no detections were found)
    video_file.annotated = True  # type: ignore[assignment]
    video_file.save()


def create_thumbnail(video_file: VideoFile, seconds: int = 1) -> None:
    """
    Generate thumbnail image and classify day/night mode for video.

    Args:
        video_file: VideoFile instance to process
        seconds: Timestamp in seconds to extract thumbnail frame
    """
    thumbnail_path = get_thumbnail_path(video_file)
    # Generate thumbnail if it doesn't already exist
    if not thumbnail_path.exists():
        # Find ffmpeg executable
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            logger.error("ffmpeg not found in PATH")
            return
        # Create thumbnail with ffmpeg
        command = [
            ffmpeg_path,
            "-ss",
            str(seconds),  # Seek to timestamp (seconds)
            "-i",
            str(video_file.path),
            "-vframes",
            "1",  # Extract 1 frame
            "-q:v",
            "2",  # High quality
            "-s",
            "280x157",  # Resize to card dimensions
            os.fspath(thumbnail_path),
        ]
        subprocess.run(command, capture_output=True, text=True, check=True)
    # Update whether this is a night video or not (requires thumbnail)
    video_file.is_night = is_night_video(thumbnail_path)  # type: ignore[assignment]
    video_file.save()


if __name__ == "__main__":
    run()
