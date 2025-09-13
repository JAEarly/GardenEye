
<div align="center">
  <img src="frontend/static/images/logo.png" alt="GardenEye Logo" width="80" />
  <br/>
  <img src="frontend/static/images/wordmark.png" alt="GardenEye" height="40" />
</div>

<br/>

A wildlife camera web viewer that uses AI to identify and annotate wildlife and people in camera footage, focusing on specific target objects like birds, cats, dogs, and other animals.

## Features

- **AI Object Detection**: YOLO-based wildlife and people detection with filtering to target objects (person, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe) with confidence scoring and bounding boxes
- **Object Filtering**: Filter videos by detected object types or hide videos with no detections
- **Thumbnail Previews**: Automatic generation of video thumbnails for improved browsing experience
- **Web Interface**: Simple, clean web interface with video grid and expandable player focused on AI detection results
- **Fast Streaming**: Efficient video streaming with HTTP range support for large files
- **Comprehensive Testing**: Full test coverage with automated CI/CD pipeline
- **Security-First**: Secure subprocess handling and comprehensive linting with ruff and mypy

## Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for package management
- [just](https://github.com/casey/just) for task running
- FFmpeg for video processing

### Setup
```bash
# Install dependencies (includes optional ML dependencies for AI detection)
just install

# Start development server
just run
```

Visit http://localhost:8000 to view the application.

### Processing Videos
```bash
# Place your .MP4 files in the data/ directory
# Run full data ingestion pipeline: file discovery, AI object detection, and thumbnail generation (requires ML dependencies)
cd backend && uv run python -m garden_eye.scripts.ingest_data
```

## Development

This project uses a single Python package managed by **uv** and coordinated with **just**.

### Running Commands
```bash
# Format code in backend
# Run linting in backend (ruff + mypy)
# Run tests in backend (pytest with coverage)
# Clean build artifacts
just fmt lint test clean

# View all available commands
just help
```

### Backend Commands
```bash
# Backend commands
cd backend && just fmt lint test
```

### Technology Stack
- **Backend**: 
  - Core: FastAPI, Peewee ORM, SQLite, uvicorn, tqdm
  - Optional ML: OpenCV, YOLO (Ultralytics), FFmpeg (for AI detection and thumbnails)
- **Development**: uv, just, ruff, mypy, pytest
- **CI/CD**: GitHub Actions, Renovate
- **Frontend**: Vanilla HTML/CSS/JavaScript

### Project Structure
```
├── backend/               # FastAPI application (garden-eye)
│   ├── src/garden_eye/   # Application source code
│   │   ├── api/          # FastAPI application
│   │   │   ├── main.py       # FastAPI app and endpoints
│   │   │   ├── database.py   # Peewee ORM models
│   │   │   ├── range_stream.py # HTTP range streaming
│   │   │   └── log.py        # Logging configuration
│   │   └── scripts/      # Data processing scripts
│   │       └── ingest_data.py # Combined data ingestion pipeline: file discovery, YOLO object detection, annotation, and FFmpeg-based thumbnail generation
│   ├── tests/            # Comprehensive test suite
│   └── pyproject.toml    # Backend dependencies and config
├── frontend/              # Single-page HTML application
│   └── static/           # Web assets
│       ├── index.html    # Main HTML page
│       ├── style.css     # Stylesheet
│       ├── app.js        # JavaScript application
│       └── images/       # Logo and branding assets
├── data/                  # Video files and thumbnails directory (gitignored)
│   ├── thumbnails/       # Generated thumbnail images
│   └── 25_10_08/         # Video files organized by date
├── weights/               # YOLO model weights directory (gitignored)
├── .github/
│   ├── workflows/        # GitHub Actions CI/CD
│   └── renovate.json     # Automated dependency updates
├── justfile              # Unified task runner for backend
└── CLAUDE.md             # Development guide for AI assistants
```
