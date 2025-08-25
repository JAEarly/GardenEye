from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.responses import Response

from app import DATA_DIR, STATIC_ROOT
from app.database import DB, VideoFile, add_files, init_database
from app.log import get_logger
from app.range_stream import range_file_response

# Configure uvicorn loggers
for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    get_logger(name)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, Any]:
    init_database()
    add_files()
    yield
    DB.close()


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
    for vf in VideoFile.select().order_by(VideoFile.path):
        items.append(
            VideoOut(
                vid=vf.id,
                name=vf.path.name,
                size=int(vf.size),
            )
        )
    return items


@app.get("/stream")
async def stream(request: Request, vid: int) -> Response:
    """Stream a media file with Range support."""
    vf = VideoFile.get_by_id(vid)
    return range_file_response(vf.path, request)
