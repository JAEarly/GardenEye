
# TODO List

## Frontend Improvements
- [x] Improve front-end layout and UI/UX
- [ ] Add bounding box support for full screen mode
- [x] Fix FPS synchronization issue (annotations don't line up with video frames)

## Data & Analytics
- [ ] Create video summary page showing detected objects per video
- [ ] Add annotation filtering and aggregation features
- [ ] Add search functionality for finding videos with specific objects
- [ ] Export annotations to standard formats (COCO, YOLO, etc.)

## AI/ML Enhancements  
- [x] Remove movement detection functionality
- [ ] Experiment with different YOLO model sizes (nano vs small vs medium)
- [ ] Add support for custom trained models
- [ ] Implement confidence threshold configuration
- [ ] Add batch processing improvements for large video sets

## Testing & Quality
- [ ] Add comprehensive tests for annotation functionality
- [ ] Add frontend tests for video player and annotation display
- [ ] Improve test coverage for edge cases (corrupted videos, etc.)

## Performance & Optimization
- [x] Simplify dependency structure (merged detection into backend)
- [x] Add video thumbnail generation for faster browsing
- [ ] Implement annotation caching/indexing for faster queries
- [ ] Add progress tracking for long-running annotation jobs
