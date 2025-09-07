from app import WEIGHTS_DIR

from detection.annotate import create_model


def test__create_model__okay() -> None:
    create_model()
    assert (WEIGHTS_DIR / "yolo11n.pt").is_file()
