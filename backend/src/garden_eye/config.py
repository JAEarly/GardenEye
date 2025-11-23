from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parents[3] / "config.yaml"


@dataclass(frozen=True)
class _Config:
    """One-to-one mapping with config.yaml."""

    data_root: Path

    @staticmethod
    def load() -> _Config:
        """Load the config from disk."""
        with open(CONFIG_PATH) as f:
            raw_config = yaml.safe_load(f)
        return _Config(data_root=Path(raw_config["data_root"]))


config = _Config.load()
