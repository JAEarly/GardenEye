from __future__ import annotations
from pathlib import Path
from urllib.parse import unquote
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.range_stream import range_file_response
from starlette.responses import Response

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MEDIA_ROOT = (BASE_DIR / "data" / "25_10_08").resolve()
STATIC_ROOT = (BASE_DIR / "frontend" / "static").resolve()

app = FastAPI(title="GardenEye", version="0.1.0")

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
    print(index_path.absolute())
    if not index_path.is_file():
        raise HTTPException(500, detail="Missing static/index.html")
    return FileResponse(index_path)


@app.get("/api/videos")
def list_videos() -> list[dict]:
    """Return a flat list of video files under MEDIA_ROOT (non-recursive by default)."""
    exts = {".mp4", ".mov", ".m4v", ".webm"}
    items = []
    for p in sorted(MEDIA_ROOT.glob("*")):
        if p.suffix.lower() in exts and p.is_file():
            rel = p.relative_to(MEDIA_ROOT)
            items.append(
                {
                    "name": p.name,
                    "path": str(rel).replace("\\", "/"),
                    "size": p.stat().st_size,
                }
            )
    return items


@app.get("/stream")
async def stream(request: Request, path: str) -> Response:
    """Stream a media file with Range support. The `path` is relative to MEDIA_ROOT."""
    # Security: prevent path traversal
    rel = Path(unquote(path))
    if rel.is_absolute() or ".." in rel.parts:
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path = (MEDIA_ROOT / rel).resolve()
    if not str(full_path).startswith(str(MEDIA_ROOT)):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Always serve as mp4 (browser-friendly). If source isn't mp4, convert offline first.
    return range_file_response(str(full_path), request)
