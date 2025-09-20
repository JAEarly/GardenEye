
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
    return label in WILDLIFE_COCO_LABELS.values()
