"""HTTP range request support for efficient video streaming."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from fastapi import HTTPException, Request
from starlette.responses import Response, StreamingResponse

CHUNK_SIZE = 1024 * 1024  # 1MB


def _parse_range(range_header: str, file_size: int) -> tuple[int, int]:
    """
    Parse a Range header into (start, end) byte positions inclusive.

    Supports formats like 'bytes=START-' or 'bytes=START-END' or 'bytes=-SUFFIX'.

    Args:
        range_header: HTTP Range header value
        file_size: Total file size in bytes
    """
    try:
        units, ranges = range_header.split("=", 1)
    except ValueError as e:
        raise HTTPException(status_code=416, detail="Invalid Range header") from e

    if units.strip() != "bytes":
        raise HTTPException(status_code=416, detail="Only 'bytes' range supported")

    first_range = ranges.split(",")[0].strip()

    if first_range.startswith("-"):
        # Suffix range: last N bytes
        suffix = int(first_range[1:])
        if suffix == 0:
            raise HTTPException(status_code=416, detail="Invalid suffix length")
        start = max(file_size - suffix, 0)
        end = file_size - 1
    else:
        parts = first_range.split("-")
        if len(parts) != 2:
            raise HTTPException(status_code=416, detail="Invalid range format")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if parts[1] else file_size - 1

    if start > end or start < 0:
        raise HTTPException(status_code=416, detail="Invalid range bounds")

    end = min(end, file_size - 1)
    return start, end


def range_file_response(file_path: Path, request: Request) -> Response:
    """
    Create a streaming response supporting HTTP Range requests for video playback.

    Args:
        file_path: Path to video file
        request: FastAPI Request object
    """
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    file_size = os.path.getsize(file_path)
    range_header: str | None = request.headers.get("range") or request.headers.get("Range")

    def file_iterator(start: int, end: int) -> Iterator[bytes]:
        with open(file_path, "rb") as f:
            f.seek(start)
            bytes_left = end - start + 1
            while bytes_left > 0:
                chunk = f.read(min(CHUNK_SIZE, bytes_left))
                if not chunk:
                    break
                bytes_left -= len(chunk)
                yield chunk

    if range_header:
        start, end = _parse_range(range_header, file_size)
        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Cache-Control": "private, max-age=3600",
        }
        return StreamingResponse(
            file_iterator(start, end),
            status_code=206,
            media_type="video/mp4",
            headers=headers,
        )

    # No Range header → send full file
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Cache-Control": "private, max-age=3600",
    }
    return StreamingResponse(
        file_iterator(0, file_size - 1),
        media_type="video/mp4",
        headers=headers,
    )
