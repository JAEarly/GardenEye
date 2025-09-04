# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GardenEye is a wildlife camera web viewer with three main components:

- **Backend** (`backend/`): FastAPI application serving video files and metadata
- **Frontend** (`frontend/`): Single-page HTML application for video viewing  
- **Detection** (`detection/`): Computer vision module for motion analysis

The backend serves videos from the `data/` directory, processes them to compute movement scores, and stores metadata in a SQLite database. The frontend displays videos with a simple interface, streaming both original and movement-processed versions.

The backend package is named `garden-eye` and detection is `garden-eye-detection`, with source code organized under `src/` directories.

## Development Commands

### Backend (from `backend/` directory)
```bash
# Run development server
uv run python -m uvicorn app.main:app --reload \
  --reload-dir src \
  --reload-dir ../frontend \
  --reload-dir ../data

# Lint and format
just lint    # ruff check + mypy
just fmt     # ruff format + ruff check --fix

# Manual commands
uv run ruff check .
uv run mypy .
uv run ruff format .
```

### Detection (from `detection/` directory)
```bash
# Run motion detection processing
uv run python -m detection.frame_diff

# Lint and format (same as backend)
just lint
just fmt
```

## Architecture

### Backend Structure
- `backend/src/app/main.py`: FastAPI application with video streaming endpoints
- `backend/src/app/database.py`: Peewee ORM models for video metadata  
- `backend/src/app/range_stream.py`: HTTP range request handling for video streaming
- `backend/src/app/log.py`: Logging configuration
- Uses SQLite database at `data/database.db`

### Video Processing Pipeline
1. Videos placed in `data/` directory are automatically discovered
2. `VideoFile` model stores path, size, modification time, and movement score
3. Detection module processes videos to compute frame-by-frame movement
4. Creates `*_movement.mp4` files showing frame differences
5. Frontend can stream both original and movement-processed videos

### Key Endpoints
- `/api/videos`: List all video files with metadata
- `/stream?vid={id}&mode={normal|movement}`: Stream video with Range support
- `/`: Serves the frontend HTML application

## Dependencies

Both backend and detection use:
- **uv** for Python package management
- **ruff** for linting and formatting
- **mypy** for type checking
- **just** for task running

**Backend** (`garden-eye`): FastAPI, Peewee ORM, uvicorn  
**Detection** (`garden-eye-detection`): OpenCV, NumPy, matplotlib, tqdm

The detection package depends on the backend package via local editable install.

### Frontend Structure
- `frontend/static/index.html`: Single-page HTML application with embedded CSS and JavaScript
- Provides video selection interface and streaming controls
- Supports both normal and movement-processed video modes