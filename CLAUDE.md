# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GardenEye is a wildlife camera web viewer with three main components:

- **Backend** (`backend/`): FastAPI application serving video files and metadata
- **Frontend** (`frontend/`): Single-page HTML application for video viewing  
- **Detection** (`detection/`): Computer vision module for AI-powered object detection

The backend serves videos from the `data/` directory and stores metadata in a SQLite database. The detection module uses YOLO-based object detection to identify and annotate wildlife in videos. The frontend displays videos with a simple interface for viewing original videos and their AI-detected annotations.

The backend package is named `garden-eye` and detection is `garden-eye-detection`, with source code organized under `src/` directories.

## Development Commands

### Root Level (Unified Commands)
```bash
# Install all dependencies
just install

# Start development server
just run

# Run across all workspaces
just fmt     # Format code in backend + detection
just lint    # Lint code in backend + detection  
just test    # Run tests in backend + detection
just clean   # Clean artifacts in backend + detection
```

### Individual Workspaces
```bash
# Backend (from `backend/` directory)
just fmt     # ruff format + ruff check --fix
just lint    # ruff check + mypy
just test    # pytest with coverage

# Detection (from `detection/` directory) 
just fmt     # ruff format + ruff check --fix
just lint    # ruff check + mypy
just test    # pytest with coverage

# Run object detection and annotation
uv run python -m detection.annotate

# Generate thumbnail previews for all videos
uv run python -m detection.thumbnail
```

## Architecture

### Backend Structure (`garden-eye`)
- `backend/src/app/main.py`: FastAPI application with video streaming endpoints
- `backend/src/app/database.py`: Peewee ORM models and file discovery logic
- `backend/src/app/range_stream.py`: HTTP range request handling for efficient video streaming
- `backend/src/app/log.py`: Centralized logging configuration
- `backend/tests/`: Comprehensive test suite with 90%+ coverage
- Uses SQLite database at `data/database.db`
- YOLO model weights stored in `weights/` directory

### Detection Structure (`garden-eye-detection`)
- `detection/src/detection/annotate.py`: YOLO-based object detection and annotation storage
- `detection/src/detection/thumbnail.py`: FFmpeg-based thumbnail generation for video previews
- Depends on backend package via editable install (`uv.sources`)
- Processes videos to detect and annotate wildlife objects using AI
- Generates thumbnail previews for improved browsing experience

### Video Processing Pipeline
1. Videos placed in `data/` directory are discovered by `add_files(video_dir)`
2. `VideoFile` model stores path, size, modification time, and annotation status
3. Detection module (`annotate.py`) runs YOLO object detection and stores bounding box annotations in database
4. Thumbnail module (`thumbnail.py`) generates video preview images using FFmpeg at `data/thumbnails/`
5. `Annotation` model stores detected objects with bounding boxes, confidence scores, and frame positions
6. Frontend displays thumbnail previews and can stream videos via HTTP range requests with AI-detected annotations

### Key API Endpoints
- `/api/videos`: List all video files with metadata including thumbnail URLs (JSON response)
- `/api/annotations/{vid}`: Get AI-detected annotations for a specific video
- `/api/thumbnail/{vid}`: Serve thumbnail image for video with caching headers
- `/stream?vid={id}`: Stream video with HTTP Range support for efficient playback
- `/`: Serves the frontend single-page application

## Dependencies

Both backend and detection use:
- **uv** for Python package management
- **ruff** for linting and formatting
- **mypy** for type checking
- **just** for task running

**Backend** (`garden-eye`): FastAPI, Peewee ORM, uvicorn, httpx (for testing)
**Detection** (`garden-eye-detection`): OpenCV, YOLO (Ultralytics), tqdm, FFmpeg (for thumbnails)

The detection package depends on the backend package via local editable install.

## Testing & Quality

### Test Coverage
- Backend: 90%+ test coverage with comprehensive test suite
- Detection: 84% test coverage with mocked OpenCV operations  
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

### Workspace Management
- Use `just` commands from root for cross-workspace operations
- Individual workspace commands available in each package directory
- Unified dependency management with uv and locked versions
