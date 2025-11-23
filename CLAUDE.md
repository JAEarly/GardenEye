# CLAUDE.md

Codebase instructions for Claude Code (claude.ai/code). These instructions override default behavior.

**Note**: Look for TODO(claude) statements indicating tasks for you to address.

## Project Overview

GardenEye: Wildlife camera web viewer with AI object detection.

- **Backend** (`backend/`): FastAPI serving videos/metadata with YOLO-based detection
- **Frontend** (`frontend/`): Single-page HTML app for video viewing with annotation overlay

Backend package: `garden-eye` with source in `src/garden_eye/`

Target wildlife objects: person, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

## Quick Start

```bash
just install    # Install dependencies
just run        # Start dev server (http://localhost:8000)

# Create config.yaml in project root: data_root: /path/to/gardeneye
# Place videos in: {data_root}/raw/
# Process videos (requires dev dependencies)
cd backend && uv run python scripts/ingest_data.py
```

## Development Commands

**Root level:**
```bash
just fmt     # Format backend code
just lint    # Lint backend (ruff + mypy)
just test    # Test backend with coverage
just clean   # Clean artifacts
```

**Backend only:**
```bash
cd backend
just fmt     # ruff format + ruff check --fix
just lint    # ruff check + mypy
just test    # pytest with coverage
```

## Architecture

### Backend (`garden-eye`)
- `src/garden_eye/__init__.py`: Path configuration
- `src/garden_eye/config.py`: YAML config loader (`data_root`)
- `src/garden_eye/api/main.py`: FastAPI endpoints
- `src/garden_eye/api/database.py`: Peewee ORM (`VideoFile`, `Annotation` models)
- `src/garden_eye/api/range_stream.py`: HTTP range requests for video streaming
- `src/garden_eye/helpers.py`: `WILDLIFE_COCO_LABELS`, `is_night_video()`, `is_target_coco_annotation()`
- `src/garden_eye/log.py`: Logging config
- `scripts/ingest_data.py`: YOLO detection + thumbnails + wildlife proportion + day/night classification
- `scripts/day_vs_night.py`: 3D RGB visualization
- `scripts/analyse_distribution.py`: Animated pie charts
- `scripts/annotation_prop.py`: Wildlife proportion histogram
- `tests/`: 90%+ coverage test suite

**Data Storage:** Configured via `config.yaml` (`data_root`)
- Database: `{data_root}/database.db`
- Raw videos: `{data_root}/raw/**/*.MP4`
- Thumbnails: `{data_root}/thumbnails/`

**YOLO weights:** Local `weights/` directory

### Video Processing Pipeline
1. Videos in `{data_root}/raw/` directory discovered by ingestion script
2. `VideoFile` stores path, size, mtime, annotation status, `wildlife_prop`, `is_night`
3. YOLO detection stores target wildlife/people annotations in `Annotation` model
4. FFmpeg generates thumbnails to `{data_root}/thumbnails/` directory
5. Script calculates `wildlife_prop` (frames with wildlife / total frames)
6. RGB analysis classifies day/night videos via `is_night_video()`

### Key API Endpoints
- `/api/videos`: List videos with metadata (JSON)
- `/api/annotations/{vid}`: Get annotations for video
- `/api/thumbnail/{vid}`: Serve thumbnail with caching
- `/stream?vid={id}`: Stream video with Range support
- `/`: Serve frontend

### Frontend
- `frontend/static/index.html`: Single-page app
- `frontend/static/app.js`: Application logic
- `frontend/static/style.css`: Dark theme styles
- Features: grid view, thumbnail previews, expandable player, annotation overlay, date range slider, day/night filter, hide empty filter, exclude people filter, sorting (date/wildlife activity)

## Dependencies

**Package manager:** uv
**Task runner:** just

**Backend core:** FastAPI, Peewee, uvicorn, httpx, tqdm, PyYAML
**Dev/ML:** OpenCV, YOLO (Ultralytics), matplotlib, Pillow, PyTorch
**Testing:** pytest, pytest-cov, pytest-asyncio
**Quality:** mypy (strict), ruff (including bandit security rules), types-pyyaml

## Code Quality

- Test naming: `test__<thing>__<outcome>`
- All test functions: `-> None` return type
- Coverage threshold: 90%+
- Docstrings: Google-style, imperative mood, no default values (module docstrings optional per D100)
- Security: No `shell=True`, use `shutil.which()` for executables
- Type annotations: Required (mypy strict mode)
- Line length: 120 characters

## Sync Task Instructions

When asked to perform sync task:

1. **Analyze project:** List modules, scripts, components, dependencies, features
2. **Update docstrings:** Follow Google-style conventions (imperative mood, no default values, omit None returns)
3. **Update README.md:** Ensure accuracy of purpose, installation, usage, structure
4. **Update CLAUDE.md:** Keep lean, accurate, intentional; trim redundancy
5. **Consistency checks:** Ensure all documentation matches current codebase
6. **Output:** Use project files as source of truth, not old docs
