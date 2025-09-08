
<div align="center">
  <img src="frontend/static/images/logo.png" alt="GardenEye Logo" width="80" />
  <br/>
  <img src="frontend/static/images/wordmark.png" alt="GardenEye" height="40" />
</div>

<br/>

A wildlife camera web viewer that uses AI to identify and annotate objects in wildlife footage, perfect for monitoring garden wildlife.

## Features

- **AI Object Detection**: YOLO-based wildlife detection and annotation with confidence scoring and bounding boxes
- **Thumbnail Previews**: Automatic generation of video thumbnails for improved browsing experience
- **Web Interface**: Simple, clean web interface with video grid and expandable player
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
# Install dependencies
just install

# Start development server
just run
```

Visit http://localhost:8000 to view the application.

### Processing Videos
```bash
# Place your .MP4 files in the data/ directory
# Run AI object detection and annotation
cd detection && uv run python -m detection.annotate

# Generate thumbnail previews (optional - for better browsing)
cd detection && uv run python -m detection.thumbnail
```

## Development

This project uses a monorepo structure with two Python packages managed by **uv** and coordinated with **just**.

### Running Commands
```bash
# Format code across all workspaces (backend + detection)
# Run linting across all workspaces (ruff + mypy)
# Run tests across all workspaces (pytest with coverage)
# Clean build artifacts
just fmt lint test clean

# View all available commands
just help
```

### Individual Workspace Commands
```bash
# Backend only
cd backend && just fmt lint test

# Detection only  
cd detection && just fmt lint test
```

### Technology Stack
- **Backend**: FastAPI, Peewee ORM, SQLite, uvicorn
- **Detection**: OpenCV, YOLO (Ultralytics), FFmpeg, tqdm
- **Development**: uv, just, ruff, mypy, pytest
- **CI/CD**: GitHub Actions, Renovate
- **Frontend**: Vanilla HTML/CSS/JavaScript

### Project Structure
```
├── backend/               # FastAPI application (garden-eye)
│   ├── src/app/          # Application source code
│   │   ├── main.py       # FastAPI app and endpoints
│   │   ├── database.py   # Peewee ORM models
│   │   ├── range_stream.py # HTTP range streaming
│   │   └── log.py        # Logging configuration
│   ├── tests/            # Comprehensive test suite
│   └── pyproject.toml    # Backend dependencies and config
├── detection/             # Computer vision module (garden-eye-detection)
│   ├── src/detection/    # Detection source code
│   │   ├── annotate.py   # YOLO object detection and annotation
│   │   └── thumbnail.py  # FFmpeg-based thumbnail generation
│   ├── tests/            # Detection tests
│   └── pyproject.toml    # Detection dependencies and config
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
├── justfile              # Unified task runner for all workspaces
└── CLAUDE.md             # Development guide for AI assistants
```
