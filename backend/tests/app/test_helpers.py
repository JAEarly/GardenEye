from garden_eye.helpers import is_target_coco_annotation


def test__is_target_coco_annotation__returns_true_for_target_labels() -> None:
    target_labels = ["person", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"]

    for label in target_labels:
        assert is_target_coco_annotation(label) is True


def test__is_target_coco_annotation__returns_false_for_non_target_labels() -> None:
    non_target_labels = ["bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "chair", "table"]

    for label in non_target_labels:
        assert is_target_coco_annotation(label) is False
