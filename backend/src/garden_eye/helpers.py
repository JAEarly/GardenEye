import importlib.metadata as metadata
import re
import tomllib
from pathlib import Path

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


def check_optional_dependency_group(group: str) -> None:
    """Checks if all packages from an optional dependency group are installed."""
    logger.info(f"Checking dependencies are installed for optional dependency group: {group}")
    # Find dependencies for this group in the pyproject.toml
    pyproject_path = Path(__file__).parents[2] / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    deps = pyproject["project"].get("optional-dependencies", {}).get(group, [])
    # Strip version from dependencies
    dep_pattern = re.compile(r"^[A-Za-z0-9_.-]+")
    dep_names = []
    for dep in deps:
        match = dep_pattern.match(dep.strip())
        if match is None:
            raise RuntimeError(f"Unable to parse dependency name from {dep}")
        dep_names.append(match.group(0))
    missing_deps = []
    for dep in dep_names:
        try:
            metadata.distribution(dep)
        except metadata.PackageNotFoundError:
            missing_deps.append(dep)
    if len(missing_deps) > 0:
        raise ModuleNotFoundError(
            f"Dependency group `{group}` is not installed!"
            f" Missing dependencies: {', '.join(missing_deps)}."
            f" Install command: `uv sync --extra {group}`."
        )


def is_target_coco_annotation(label: str) -> bool:
    return label in WILDLIFE_COCO_LABELS.values()
