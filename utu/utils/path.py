"""
Path and file utilities.
"""

import json
import os
from pathlib import Path

import yaml

# Define DIR_ROOT as the project root directory
DIR_ROOT = Path(__file__).parent.parent.parent.resolve()

# Define CACHE_DIR as the cache directory
CACHE_DIR = DIR_ROOT / ".cache"

__all__ = ["FileUtils", "DIR_ROOT", "CACHE_DIR"]


class FileUtils:
    """File utilities."""

    @staticmethod
    def load_prompts(fn: str | Path) -> dict:
        """Load prompts from yaml file."""
        if isinstance(fn, str):
            if not fn.endswith(".yaml"):
                fn += ".yaml"
            fn = DIR_ROOT / "utu" / "prompts" / fn
        assert fn.exists(), f"File {fn} does not exist!"
        with fn.open(encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_json(fn: str | Path) -> dict:
        """Load json file."""
        if isinstance(fn, str):
            fn = DIR_ROOT / fn
        assert fn.exists(), f"File {fn} does not exist!"
        with fn.open(encoding='utf-8') as f:
            return json.load(f)