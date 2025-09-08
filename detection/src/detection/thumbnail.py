import logging
import os
import shutil
import subprocess
from pathlib import Path

from app.database import VideoFile, add_files, get_thumbnail_path, init_database
from tqdm import tqdm

logger = logging.getLogger(__name__)


def run() -> None:
    init_database()
    add_files()
    for vf in tqdm(VideoFile.select().order_by(VideoFile.path), desc="Creating thumbnails for all files"):
        create_thumbnail(vf)


def create_thumbnail(video_file: VideoFile, seconds: int = 1) -> None:
    video_path = Path(str(video_file.path))
    thumbnail_path = get_thumbnail_path(video_path)
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
        "-ss",
        str(seconds),  # Seek to timestamp (seconds)
        "-i",
        os.fspath(video_path),
        "-vframes",
        "1",  # Extract 1 frame
        "-q:v",
        "2",  # High quality
        "-s",
        "280x157",  # Resize to card dimensions
        os.fspath(thumbnail_path),
    ]
    subprocess.run(command, capture_output=True, text=True, check=True)


if __name__ == "__main__":
    run()
