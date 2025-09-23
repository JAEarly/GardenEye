
<div align="center">
  <img src="frontend/static/images/logo.png" alt="GardenEye Logo" width="80" />
  <br/>
  <img src="frontend/static/images/wordmark.png" alt="GardenEye" height="40" />
</div>

<br/>

A wildlife camera web viewer that uses AI to identify and annotate wildlife and people in camera footage, focusing on specific target objects like birds, cats, dogs, and other animals.

[Watch the dev logs!](https://youtube.com/playlist?list=PL2SaEVMy91qKqFED7C5Ah0m3iMt1X5nD4&si=FENz3UhlJ0tX4zfB)

## Features

- **AI Object Detection**: YOLO-based wildlife and people detection with filtering to target objects (person, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe) with confidence scoring and bounding boxes
- **Smart Filtering**: Filter videos by detected object types, day/night classification, hide videos with no detections, filter out videos containing people, with sorting by date or wildlife activity and video count display
- **Thumbnail Previews**: Automatic generation of video thumbnails for improved browsing experience
- **Web Interface**: Simple, clean web interface with video grid, expandable player, wildlife activity metrics, and properly aligned annotations that account for video aspect ratios
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
# Run full data ingestion pipeline: file discovery, AI object detection, wildlife proportion calculation, thumbnail generation, and day/night classification (requires dev dependencies)
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
│   │   │   └── range_stream.py # HTTP range streaming
│   │   ├── log.py            # Logging configuration
│   │   ├── helpers.py        # Helper functions, COCO target labels, and day/night detection
│   ├── src/scripts/      # Analysis and utility scripts  
│   │   ├── day_vs_night.py    # RGB color distribution analysis with 3D visualization
│   │   ├── analyse_distribution.py # Animated pie chart visualization for annotation and video distributions
│   │   ├── annotation_prop.py # Wildlife proportion distribution analysis with histogram
│   │   └── ingest_data.py # Combined data ingestion pipeline: file discovery, YOLO object detection, annotation, wildlife proportion calculation, thumbnail generation, and day/night classification
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
