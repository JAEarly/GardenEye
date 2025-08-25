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
    name: str
    path: str
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
                name=vf.path.name,
                path=os.fspath(vf.path),
                size=int(vf.size),
            )
        )
    return items


@app.get("/stream")
async def stream(request: Request, path: str) -> Response:
    """Stream a media file with Range support. The `path` is relative to MEDIA_ROOT."""
    # Security: prevent path traversal
    rel = Path(unquote(path))
    if rel.is_absolute() or ".." in rel.parts:
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path = (DATA_DIR / rel).resolve()
    if not str(full_path).startswith(str(DATA_DIR)):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Always serve as mp4 (browser-friendly). If source isn't mp4, convert offline first.
    return range_file_response(str(full_path), request)
