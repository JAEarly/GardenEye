# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GardenEye is a wildlife camera web viewer with three main components:

- **Backend** (`backend/`): FastAPI application serving video files and metadata
- **Frontend** (`frontend/`): Single-page HTML application for video viewing  
- **Detection** (`detection/`): Computer vision module for movement analysis and object detection

The backend serves videos from the `data/` directory, processes them to compute movement scores, and stores metadata in a SQLite database. The detection module includes both frame-difference movement analysis and YOLO-based object detection with annotation storage. The frontend displays videos with a simple interface, streaming both original and movement-processed versions.

The backend package is named `garden-eye` and detection is `garden-eye-detection`, with source code organized under `src/` directories.

## Development Commands

### Root Level (Unified Commands)
```bash
# Install all dependencies
just install

# Start development server
just dev

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

# Run motion detection processing
uv run python -m detection.frame_diff

# Run object detection and annotation
uv run python -m detection.annotate
```

## Architecture

### Backend Structure (`garden-eye`)
- `backend/src/app/main.py`: FastAPI application with video streaming endpoints
- `backend/src/app/database.py`: Peewee ORM models and file discovery logic
- `backend/src/app/range_stream.py`: HTTP range request handling for efficient video streaming
- `backend/src/app/log.py`: Centralized logging configuration
- `backend/tests/`: Comprehensive test suite with 90%+ coverage
- Uses SQLite database at `data/database.db`

### Detection Structure (`garden-eye-detection`)
- `detection/src/detection/frame_diff.py`: OpenCV-based movement detection algorithm
- `detection/src/detection/annotate.py`: YOLO-based object detection and annotation storage
- Depends on backend package via editable install (`uv.sources`)
- Processes videos to generate frame-difference analysis and object detection annotations
- Secure subprocess handling for ffmpeg operations

### Video Processing Pipeline
1. Videos placed in `data/` directory are discovered by `add_files(video_dir)`
2. `VideoFile` model stores path, size, modification time, movement score (-1 = unprocessed), and annotation status
3. Detection module processes videos in two ways:
   - `frame_diff.py`: Computes frame-by-frame movement analysis and creates `*_movement.mp4` files
   - `annotate.py`: Runs YOLO object detection and stores bounding box annotations in database
4. `Annotation` model stores detected objects with bounding boxes, confidence scores, and frame positions
5. Frontend can stream both original and movement-processed videos via HTTP range requests

### Key API Endpoints
- `/api/videos`: List all video files with metadata (JSON response)
- `/stream?vid={id}&mode={normal|movement}`: Stream video with HTTP Range support for efficient playback
- `/`: Serves the frontend single-page application

## Dependencies

Both backend and detection use:
- **uv** for Python package management
- **ruff** for linting and formatting
- **mypy** for type checking
- **just** for task running

**Backend** (`garden-eye`): FastAPI, Peewee ORM, Polars, uvicorn, httpx (for testing)
**Detection** (`garden-eye-detection`): OpenCV, NumPy, matplotlib, tqdm, PyTorch Lightning, PyTorch Wildlife, YOLO (Ultralytics), PyQt6, OmegaConf

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
- Dark theme UI with video selection interface and streaming controls
- Supports both normal and movement-processed video modes
- Uses `/api/videos` endpoint and `/stream` for video delivery

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
