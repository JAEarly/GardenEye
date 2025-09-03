import os
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from app.database import VideoFile, add_files, init_database
from tqdm import tqdm


def run() -> None:
    init_database()
    add_files()
    for vf in tqdm(
        VideoFile.select().order_by(VideoFile.path), desc="Computing movement scores..."
    ):
        if vf.movement == -1:
            vf.movement = compute_movement_score(vf.path)
            vf.save()


def compute_movement_score(path: Path) -> float:
    frame_scores = []

    # Load video and get properties
    cap = cv2.VideoCapture(os.fspath(path))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create video write with browser-compatible codec
    tmp_path = Path(tempfile.mkdtemp()) / (path.stem + "_movement.mp4")
    output_path = path.with_stem(path.stem + "_movement").with_suffix(".mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
    out = cv2.VideoWriter(
        os.fspath(tmp_path),
        fourcc,
        fps,
        (width, height),
        isColor=True,  # Explicitly set color format
    )

    if not out.isOpened():
        raise RuntimeError(f"Could not open video writer for {tmp_path}")

    prev_frame = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Compute movement for this frame and write delta to out stream
        if prev_frame is not None:
            delta = cv2.absdiff(frame, prev_frame)
            score = float(delta.mean() / 255.0)
            frame_scores.append(score)
            out.write(delta)
        else:
            # First frame: write black frame to maintain frame count
            out.write(np.zeros_like(frame))
        prev_frame = frame
    cap.release()
    out.release()

    subprocess.run(
        f"ffmpeg -i {tmp_path} -vcodec libx264 -f mp4 {output_path} -loglevel error",
        shell=True,
    )

    return float(np.mean(frame_scores))


if __name__ == "__main__":
    run()
