from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import Response

from app import STATIC_ROOT
from app.database import Annotation, VideoFile, add_files, get_video_objects, init_database
from app.log import get_logger
from app.range_stream import range_file_response

# Configure uvicorn loggers
for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    get_logger(name)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    db = init_database()
    add_files()
    yield
    db.close()


class VideoOut(BaseModel):
    vid: int
    name: str
    size: int
    modified: float | None = None
    objects: list[str] = []


class AnnotationOut(BaseModel):
    frame_idx: int
    name: str
    class_id: int
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


# Setup app
app = FastAPI(title="GardenEye", version="0.1.0", lifespan=lifespan)

# CORS for local dev: allow everything on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")


@app.get("/")
def index() -> FileResponse:
    index_path = STATIC_ROOT / "index.html"
    if not index_path.is_file():
        raise HTTPException(500, detail="Missing static/index.html")
    return FileResponse(index_path)


@app.get("/api/videos")
def list_videos() -> list[VideoOut]:
    """Return a flat list of video files from the database."""
    items: list[VideoOut] = []
    # Query the DB and order by path for stable output
    for vf in VideoFile.select().order_by(VideoFile.path.asc()):
        items.append(
            VideoOut(
                vid=vf.id,
                name=vf.path.name,
                size=int(vf.size),
                objects=get_video_objects(vf),
            )
        )
    return items


@app.get("/api/annotations/{vid}")
def get_annotations(vid: int) -> list[AnnotationOut]:
    """Returns annotations for a specific video."""
    video_file = VideoFile.get_by_id(vid)
    annotations = []
    for annotation in Annotation.select().where(Annotation.video_file == video_file):
        annotations.append(
            AnnotationOut(
                frame_idx=annotation.frame_idx,
                name=annotation.name,
                class_id=annotation.class_id,
                confidence=annotation.confidence,
                x1=annotation.x1,
                y1=annotation.y1,
                x2=annotation.x2,
                y2=annotation.y2,
            )
        )
    return annotations


@app.get("/stream")
async def stream(request: Request, vid: int) -> Response:
    """Stream a media file with Range support."""
    vf = VideoFile.get_by_id(vid)
    print(vf)
    return range_file_response(vf.path, request)
