"""Configuration loader for the Accident Blackspot Mapper."""

from pathlib import Path
from typing import Any, Dict
import yaml


def load_config(path: str | Path = "config.yaml") -> Dict[str, Any]:
    """Load configuration YAML file.

    Args:
        path: Path to the config.yaml file.

    Returns:
        Dict containing configuration parameters.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config
