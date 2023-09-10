from pathlib import Path
from typing import Any, Dict

from .compat import tomllib


def load_pyproject_toml(addon_dir: Path) -> Dict[str, Any]:
    pyproject_toml_path = addon_dir / "pyproject.toml"
    if pyproject_toml_path.exists():
        with open(pyproject_toml_path, "rb") as f:
            return tomllib.load(f)
    return {}
