import os
from pathlib import Path

import cv2
import torch
from app import DATA_DIR
from app.database import Annotation, VideoFile, add_files, init_database
from peewee import chunked
from tqdm import tqdm
from ultralytics import YOLO

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def run() -> None:
    init_database()
    add_files()
    for vf in tqdm(VideoFile.select().order_by(VideoFile.path), desc="Annotating all files"):
        if not vf.annotated:
            annotate(vf.path)


def annotate(video_path: Path) -> None:
    # Set cache directory for YOLO weights to data directory
    os.environ["YOLO_CONFIG_DIR"] = os.fspath(DATA_DIR)
    model = YOLO("yolo11n.pt")

    # Get the VideoFile from database
    video_file = VideoFile.get(VideoFile.path == video_path)

    # Open input video with cv2 just to grab FPS
    cap = cv2.VideoCapture(os.fspath(video_path))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Process video and collect annotations
    annotations_data = []

    for frame_idx, result in tqdm(
        enumerate(model(video_path, stream=True, verbose=False)),
        desc=f"Annotating {video_path.stem}",
        total=n_frames,
        leave=False,
    ):
        # Process detection results
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                name = model.names[class_id]

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

    # Mark video as annotated (even if no detections were found)
    video_file.annotated = True
    video_file.save()


if __name__ == "__main__":
    run()
