
# TODO List

## Frontend Improvements
- [ ] Improve front-end layout and UI/UX
- [ ] Fix bounding boxes rendering - currently rendered in video instead of overlay
- [ ] Add bounding box support for full screen mode
- [ ] Fix FPS synchronization issue (annotations don't line up with video frames)
- [ ] Add annotation confidence score display in UI
- [ ] Add object class filtering/toggle in frontend

## Data & Analytics
- [ ] Create video summary page showing detected objects per video
- [ ] Add annotation filtering and aggregation features
- [ ] Add search functionality for finding videos with specific objects
- [ ] Export annotations to standard formats (COCO, YOLO, etc.)

## AI/ML Enhancements  
- [ ] Experiment with different YOLO model sizes (nano vs small vs medium)
- [ ] Add support for custom trained models
- [ ] Implement confidence threshold configuration
- [ ] Add batch processing improvements for large video sets

## Testing & Quality
- [ ] Add comprehensive tests for annotation functionality
- [ ] Add frontend tests for video player and annotation display
- [ ] Improve test coverage for edge cases (corrupted videos, etc.)

## Performance & Optimization
- [ ] Add video thumbnail generation for faster browsing
- [ ] Implement annotation caching/indexing for faster queries
- [ ] Add progress tracking for long-running annotation jobs

## Completed
- [x] Remove movement detection functionality 
- [x] Simplify dependency structure
