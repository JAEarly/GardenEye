"""Helper functions for wildlife detection and video analysis."""

from pathlib import Path

import numpy as np
from PIL import Image

from garden_eye.log import get_logger

logger = get_logger(__name__)


WILDLIFE_COCO_LABELS = {
    0: "person",
    14: "bird",
    15: "cat",
    16: "dog",
    17: "horse",
    18: "sheep",
    19: "cow",
    20: "elephant",
    21: "bear",
    22: "zebra",
    23: "giraffe",
}


def is_target_coco_annotation(label: str) -> bool:
    """
    Check if a label is in the target wildlife/people categories.

    Args:
        label: COCO annotation label name
    """
    return label in WILDLIFE_COCO_LABELS.values()


def is_night_video(thumbnail_path: Path, tolerance: float = 2.0) -> bool:
    """
    Detect if a video is from night mode (typically grayscale with IR illumination).

    Args:
        thumbnail_path: Path to video thumbnail
        tolerance: Maximum allowed difference between RGB channels to consider grayscale

    Returns:
        True if the video appears to be a night/IR recording
    """
    thumbnail = np.asarray(Image.open(thumbnail_path))
    mean_rgb = thumbnail.mean(axis=(0, 1))

    # Check if RGB channels are nearly equal (grayscale)
    r, g, b = mean_rgb[0], mean_rgb[1], mean_rgb[2]
    max_diff = max(abs(r - g), abs(g - b), abs(r - b))

    return max_diff <= tolerance
