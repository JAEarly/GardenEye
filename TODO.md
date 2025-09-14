
# TODO List

## Frontend Improvements
- [x] Improve front-end layout and UI/UX
- [ ] Add bounding box support for full screen mode
- [x] Fix FPS synchronization issue (annotations don't line up with video frames)
- [x] Fix annotation positioning issues at video edges - proper aspect ratio handling and letterboxing support
- [x] Allow filtering of annotation types by clicking on label (and filter at top) - implemented as object class dropdown
- [x] Filter checkbox of "empty" clips - implemented as "Hide videos with no detections"
- [x] Add filter for person-only videos - implemented as "Filter out videos containing people" checkbox
- [x] Add video count display in header - shows current filtered video count
- [x] Add day/night filtering - implemented as dropdown filter with "Day + Night", "Day", "Night" options
- [x] Add sorting by wildlife activity and date - implemented with "Oldest", "Latest", "Most Activity", "Least Activity" options
- [x] Display wildlife activity metrics and modification dates on video cards
- [ ] Screenshot in readme

## Data & Analytics
- [ ] Create video summary page showing detected objects per video
- [ ] Show points of annotation below scrubber bar in expanded view mode
- [x] Add annotation filtering to target wildlife/people objects (implemented with WILDLIFE_COCO_LABELS)
- [x] Add search functionality for finding videos with specific objects - implemented as object class filter dropdown
- [x] Add day/night video classification - implemented with `is_night` database field and RGB analysis
- [x] Add color distribution analysis tools - implemented `day_vs_night.py` script with 3D RGB visualization
- [x] Add wildlife activity proportion tracking - implemented `wildlife_prop` field in database and API
- [x] Add wildlife proportion visualization - implemented `annotation_prop.py` script with histogram
- [ ] Animal count? E.g. 0037 has two foxes

## AI/ML Enhancements  
- [x] Remove movement detection functionality
- [ ] Experiment with different YOLO model sizes (nano vs small vs medium)
- [ ] Add support for custom trained models
- [ ] Implement confidence threshold configuration
- [x] Add batch processing improvements for large video sets - implemented with batch=64 and optimized parameters
- [ ] Experiment with depth estimation

## Performance & Optimization
- [x] Simplify dependency structure (merged detection into backend)
- [x] Add video thumbnail generation for faster browsing
- [x] Combine annotation and thumbnail generation into single ingestion pipeline (ingest_data.py)
- [x] Move filtering logic to frontend for better performance - removed server-side filter_person parameter
- [ ] Implement annotation caching/indexing for faster queries
- [ ] Add progress tracking for long-running annotation jobs

## Hosting
- [ ] nginx?
