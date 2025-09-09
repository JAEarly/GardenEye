# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GardenEye is a wildlife camera web viewer with two main components:

- **Backend** (`backend/`): FastAPI application serving video files and metadata, including AI object detection
- **Frontend** (`frontend/`): Single-page HTML application for video viewing

The backend serves videos from the `data/` directory and stores metadata in a SQLite database. The backend includes AI detection scripts that use YOLO-based object detection to identify and annotate wildlife in videos, filtering to only target wildlife and people objects (person, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe). The frontend displays videos with a simple interface for viewing original videos and their AI-detected annotations.

The backend package is named `garden-eye` with source code organized under `src/garden_eye/`.

## Development Commands

### Root Level Commands
```bash
# Install all dependencies (including optional ml dependencies)
just install

# Start development server
just run

# Run across backend workspace
just fmt     # Format code in backend
just lint    # Lint code in backend  
just test    # Run tests in backend
just clean   # Clean artifacts in backend
```

### Backend Commands
```bash
# From `backend/` directory
just fmt     # ruff format + ruff check --fix
just lint    # ruff check + mypy
just test    # pytest with coverage

# Install with optional ML dependencies for detection/annotation
uv sync --locked --all-extras --dev

# Run object detection and annotation (requires ml extras)
uv run python -m garden_eye.scripts.annotate

# Generate thumbnail previews for all videos (requires ml extras)
uv run python -m garden_eye.scripts.thumbnail
```

## Architecture

### Backend Structure (`garden-eye`)
- `backend/src/garden_eye/api/main.py`: FastAPI application with video streaming endpoints
- `backend/src/garden_eye/api/database.py`: Peewee ORM models and file discovery logic
- `backend/src/garden_eye/api/range_stream.py`: HTTP range request handling for efficient video streaming
- `backend/src/garden_eye/api/log.py`: Centralized logging configuration
- `backend/src/garden_eye/scripts/annotate.py`: YOLO-based object detection and annotation storage (filters to target wildlife/people)
- `backend/src/garden_eye/helpers.py`: Helper functions including `COCO_TARGET_LABELS` for annotation filtering
- `backend/src/garden_eye/scripts/thumbnail.py`: FFmpeg-based thumbnail generation for video previews
- `backend/tests/`: Comprehensive test suite with 90%+ coverage
- Uses SQLite database at `data/database.db`
- YOLO model weights stored in `weights/` directory

### Video Processing Pipeline
1. Videos placed in `data/` directory are discovered by `add_files(video_dir)`
2. `VideoFile` model stores path, size, modification time, and annotation status
3. Detection script (`garden_eye.scripts.annotate`) runs YOLO object detection and stores only target wildlife/people annotations in database (filters using `COCO_TARGET_LABELS`)
4. Thumbnail script (`garden_eye.scripts.thumbnail`) generates video preview images using FFmpeg at `data/thumbnails/`
5. `Annotation` model stores detected objects with bounding boxes, confidence scores, and frame positions
6. Frontend displays thumbnail previews and can stream videos via HTTP range requests with AI-detected annotations

### Key API Endpoints
- `/api/videos`: List all video files with metadata including thumbnail URLs (JSON response)
- `/api/annotations/{vid}`: Get AI-detected annotations for a specific video (filtered to target wildlife/people objects)
- `/api/thumbnail/{vid}`: Serve thumbnail image for video with caching headers
- `/stream?vid={id}`: Stream video with HTTP Range support for efficient playback
- `/`: Serves the frontend single-page application

## Dependencies

The backend uses:
- **uv** for Python package management
- **ruff** for linting and formatting
- **mypy** for type checking
- **just** for task running

**Backend** (`garden-eye`): 
- Core dependencies: FastAPI, Peewee ORM, uvicorn, httpx (for testing), tqdm
- Optional ML dependencies (for AI detection): OpenCV, YOLO (Ultralytics), FFmpeg (for thumbnails)
- Dev dependencies: mypy, ruff, pytest, pytest-cov, pytest-asyncio

## Testing & Quality

### Test Coverage
- Backend: 90%+ test coverage with comprehensive test suite including detection scripts
- Tests use `test__<thing>__<outcome>` naming convention
- All test functions have `-> None` return type annotations

### Code Quality
- **ruff**: Comprehensive linting with security rules (bandit)
- **mypy**: Strict type checking with `disallow_untyped_defs`
- **pytest**: Full test automation with coverage reports
- **GitHub Actions**: Automated CI/CD with lint and test jobs
- **Renovate**: Automated dependency updates

### Frontend Structure
- `frontend/static/index.html`: Single-page HTML application 
- `frontend/static/style.css`: Separate CSS stylesheet
- `frontend/static/app.js`: Separate JavaScript application logic
- `frontend/static/images/`: Logo and branding assets
- Dark theme UI with video grid displaying thumbnail previews
- Interactive video selection with expandable player interface
- Displays AI-detected object annotations with confidence scores and bounding boxes
- Uses `/api/videos`, `/api/annotations/{vid}`, `/api/thumbnail/{vid}`, and `/stream` endpoints

## Development Practices

### Testing Convention
- Python tests should be named `test__<thing>__<outcome>`
- All test functions must have `-> None` return type annotation
- Use proper type annotations for fixture parameters (e.g., `SqliteDatabase`, `Path`)
- Tests should achieve high coverage (85%+ threshold)

### Security
- No `shell=True` in subprocess calls - use list format with full executable paths
- Use `shutil.which()` to find system executables like ffmpeg
- Comprehensive security linting with bandit (S-rules in ruff)

### Code Organization
- Source code in `src/` directories within each package
- Comprehensive type annotations required (mypy strict mode)
- 120-character line length limit
- Import sorting and modern Python syntax (pyupgrade)

### Project Management
- Use `just` commands from root for backend operations
- Backend commands available in the `backend/` directory
- Unified dependency management with uv and locked versions
