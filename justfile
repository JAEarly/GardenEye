# Root justfile for GardenEye project

default: fmt lint test clean

workspaces := "backend detection"

# Run fmt/lint/test across all workspaces
fmt:
    #!/usr/bin/env bash
    for ws in {{workspaces}}; do
        echo "Formatting $ws..."
        cd $ws && just fmt ; cd ../
    done

lint:
    #!/usr/bin/env bash
    for ws in {{workspaces}}; do
        echo "Linting $ws..."
        cd $ws && just lint ; cd ../
    done

test:
    #!/usr/bin/env bash
    for ws in {{workspaces}}; do
        echo "Testing $ws..."
        cd $ws && just test ; cd ../
    done

clean:
    #!/usr/bin/env bash
    for ws in {{workspaces}}; do
        echo "Cleaning $ws..."
        cd $ws && just clean ; cd ../
    done

# Install dependencies for both projects
install:
    @echo "Installing dependencies for backend..."
    cd backend && uv sync --locked --all-extras --dev
    @echo "Installing dependencies for detection..."
    cd detection && uv sync --locked --all-extras --dev

# Run development server
run:
    @echo "Starting development server..."
    cd backend && uv run python -m uvicorn app.main:app --reload \
      --reload-dir src \
      --reload-dir ../frontend \
      --reload-dir ../data

# Show help
help:
    @just --list