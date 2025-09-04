from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import Response

from app import STATIC_ROOT
from app.database import VideoFile, add_files, init_database
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
    for vf in VideoFile.select().order_by(VideoFile.movement.desc()):
        items.append(
            VideoOut(
                vid=vf.id,
                name=vf.path.name,
                size=int(vf.size),
            )
        )
    return items


@app.get("/stream")
async def stream(request: Request, vid: int, mode: Literal["normal", "movement"]) -> Response:
    """Stream a media file with Range support."""
    vf = VideoFile.get_by_id(vid)
    match mode:
        case "normal":
            path = vf.path
        case "movement":
            path = vf.path.with_stem(vf.path.stem + "_movement").with_suffix(".mp4")
        case _:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")
    return range_file_response(path, request)
