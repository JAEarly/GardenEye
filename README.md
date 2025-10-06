
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
- **Smart Filtering**: Date range slider, day/night classification filter, hide empty videos, exclude people filter, sorting by date or wildlife activity, and video count display
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
# Run full data ingestion pipeline: file discovery, AI object detection,
# wildlife proportion calculation, thumbnail generation, and day/night classification
cd backend && uv run python -m garden_eye.scripts.ingest_data
```

## Development

This project uses a single Python package managed by **uv** and coordinated with **just**.

### Running Commands
```bash
# Format, lint, test, and clean (runs across backend workspace)
just fmt lint test clean

# View all available commands
just help
```

### Backend-Specific Commands
```bash
cd backend

# Format code (ruff format + ruff check --fix)
just fmt

# Run linting (ruff check + mypy)
just lint

# Run tests with coverage
just test

# Clean build artifacts
just clean
```

### Technology Stack
- **Backend (garden-eye)**:
  - Core: FastAPI, Peewee ORM, SQLite, uvicorn, httpx, tqdm
  - Dev/ML: OpenCV, YOLO (Ultralytics), matplotlib, Pillow, PyTorch
  - Testing: pytest, pytest-cov, pytest-asyncio
  - Type checking: mypy with strict mode
  - Linting: ruff (with bandit security rules)
- **Build & Automation**: uv (package manager), just (task runner)
- **CI/CD**: GitHub Actions, Renovate
- **Frontend**: Vanilla HTML/CSS/JavaScript with canvas-based annotation overlay

### Project Structure
```
├── backend/               # FastAPI backend (garden-eye package)
│   ├── src/
│   │   ├── garden_eye/   # Core application package
│   │   │   ├── __init__.py   # Path configuration
│   │   │   ├── api/          # FastAPI application
│   │   │   │   ├── main.py       # API endpoints and app setup
│   │   │   │   ├── database.py   # Peewee ORM models (VideoFile, Annotation)
│   │   │   │   └── range_stream.py # HTTP range request handling
│   │   │   ├── log.py        # Logging configuration
│   │   │   └── helpers.py    # Wildlife labels and day/night detection
│   │   └── scripts/      # Analysis and processing scripts
│   │       ├── ingest_data.py # Data ingestion pipeline (detection, thumbnails, classification)
│   │       ├── day_vs_night.py # 3D RGB distribution visualization
│   │       ├── analyse_distribution.py # Animated pie chart for distributions
│   │       └── annotation_prop.py # Wildlife proportion histogram
│   ├── tests/            # Test suite (90%+ coverage)
│   ├── pyproject.toml    # Package config and dependencies
│   └── justfile          # Backend task automation
├── frontend/              # Single-page HTML application
│   └── static/           # Web assets
│       ├── index.html    # Main HTML page
│       ├── style.css     # Stylesheet
│       ├── app.js        # JavaScript application
│       └── images/       # Logo and branding assets
├── data/                  # Video files and SQLite database (gitignored)
│   ├── database.db       # SQLite database
│   ├── thumbnails/       # Generated thumbnail images
│   └── **/*.MP4          # Video files (organized by date/folder structure)
├── weights/               # YOLO model weights (gitignored)
├── .github/
│   ├── workflows/        # CI/CD (lint and test jobs)
│   └── renovate.json     # Dependency automation
├── justfile              # Root task runner (delegates to backend)
├── CLAUDE.md             # AI assistant development guide
└── LICENSE               # Project license
```
