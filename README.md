
# GardenEye

## Running

From `backend`:
```bash
uv run python -m uvicorn app.main:app --reload \
  --reload-dir src \
  --reload-dir ../frontend \
  --reload-dir ../data
```
