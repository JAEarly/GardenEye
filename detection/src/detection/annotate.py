import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import cv2
import polars as pl
import torch
from app.database import VideoFile, add_files, init_database
from tqdm import tqdm
from ultralytics import YOLO

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def run() -> None:
    init_database()
    add_files()
    for vf in tqdm(VideoFile.select().order_by(VideoFile.path), desc="Annotating all files"):
        annotate(vf.path)


def annotate(video_path: Path) -> None:
    # Set cache directory for YOLO weights to /tmp
    os.environ['YOLO_CONFIG_DIR'] = '/tmp'
    model = YOLO("yolo11n.pt")

    # Open input video with cv2 just to grab metadata (fps, size)
    cap = cv2.VideoCapture(os.fspath(video_path))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create video write with browser-compatible codec
    tmp_path = Path(tempfile.mkdtemp()) / (video_path.stem + "_annotated.mp4")
    output_path = video_path.with_stem(video_path.stem + "_annotated").with_suffix(".mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
    out = cv2.VideoWriter(
        os.fspath(tmp_path),
        fourcc,
        fps,
        (w, h),
        isColor=True,  # Explicitly set color format
    )

    if not out.isOpened():
        raise RuntimeError(f"Could not open video writer for {tmp_path}")

    if output_path.is_file() and video_path.with_suffix(".json").is_file():
        return

    # Create empty DataFrame with required columns
    dfs = []

    for frame_idx, result in tqdm(
        enumerate(model(video_path, stream=True, verbose=False)),
        desc=f"Annotating {video_path.stem}",
        total=n_frames,
        leave=False,
    ):
        frame = result.plot()
        frame_df = result.to_df()
        out.write(frame)

        # Add frame_idx column to the frame results and append to main DataFrame
        if len(frame_df) > 0:
            frame_df_with_idx = frame_df.with_columns(pl.lit(frame_idx).alias("frame_idx"))
            dfs.append(frame_df_with_idx)

        frame_idx += 1

        # print(result.save(filename="test.png"))
        # TODO(jearly): Use save crop in future
        # print(result.save_crop(save_dir="./"))
        # TODO(jearly): use save txt or summary for writing into database
        # print(result.summary())
        # print(result.save_txt(txt_file="test.txt"))
        # exit(0)

    # Write detection results to JSON file
    if len(dfs) > 0:
        df = pl.concat(dfs, how="vertical")
        df = df.select(["frame_idx"] + [col for col in df.columns if col != "frame_idx"])
        df.write_json(video_path.with_suffix(".json"))
    else:
        # Write empty DataFrame with correct schema when no detections found
        empty_df = pl.DataFrame({"frame_idx": [], "name": [], "class": [], "confidence": [], "box": []})
        empty_df.write_json(video_path.with_suffix(".json"))

    cap.release()
    out.release()

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg not found in PATH")

    subprocess.run(
        [
            ffmpeg_path,
            "-i",
            str(tmp_path),
            "-vcodec",
            "libx264",
            "-f",
            "mp4",
            str(output_path),
            "-loglevel",
            "error",
            "-y",
        ]
    )


if __name__ == "__main__":
    run()
