import os
from pathlib import Path

import cv2
import torch
from app.database import Annotation, VideoFile, add_files, init_database, get_thumbnail_path
from peewee import chunked
from tqdm import tqdm
from ultralytics import YOLO
import subprocess
import shutil
import logging


logger = logging.getLogger(__name__)


def run() -> None:
    init_database()
    add_files()
    for vf in tqdm(VideoFile.select().order_by(VideoFile.path), desc="Creating thumbnails for all files"):
        create_thumbnail(vf)


def create_thumbnail(video_file: VideoFile, seconds: int = 1) -> None:
    thumbnail_path = get_thumbnail_path(video_file.path)
    # Skip if thumbnail already exists
    if thumbnail_path.exists():
        return

    # Ensure thumbnail directory exists
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

    # Find ffmpeg executable
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        logger.error("ffmpeg not found in PATH")
        return

    command = [
        ffmpeg_path,
        "-ss", str(seconds),  # Seek to timestamp (seconds)
        "-i", os.fspath(video_file.path),
        "-vframes", "1",  # Extract 1 frame
        "-q:v", "2",  # High quality
        "-s", "280x157",  # Resize to card dimensions
        os.fspath(thumbnail_path),
    ]
    subprocess.run(command, capture_output=True, text=True, check=True)


if __name__ == "__main__":
    run()
