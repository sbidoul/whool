import logging
from pathlib import Path
from typing import Sequence

import tomli

_logger = logging.getLogger(__name__)

BUILD_SYSTEM_TOML = b"""\
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
"""


def init_addon_dir(addon_dir: Path) -> bool:
    if not addon_dir.joinpath("__manifest__.py").is_file():
        return False
    pyproject_toml_path = addon_dir / "pyproject.toml"
    if not pyproject_toml_path.exists():
        with open(pyproject_toml_path, "wb") as f:
            f.write(BUILD_SYSTEM_TOML)
    else:
        with open(pyproject_toml_path, "rb") as f:
            pyproject_toml = tomli.load(f)
        if "build-system" in pyproject_toml:
            if (
                pyproject_toml.get("build-system", {}).get("build-backend")
                != "whool.buildapi"
            ):
                _logger.debug(
                    f"Did not initialize Whool build-system in {pyproject_toml_path} "
                    f"because another one is already defined.",
                )
                return False
        else:
            with open(pyproject_toml_path, "ab") as f:
                f.write(b"\n")
                f.write(BUILD_SYSTEM_TOML)
    return True


def init(dir: Path) -> Sequence[Path]:
    res = []
    if init_addon_dir(dir):
        res.append(dir)
    else:
        for subdir in dir.iterdir():
            if subdir.is_dir():
                if init_addon_dir(subdir):
                    res.append(subdir)
    return res
