import subprocess
from pathlib import Path

import pytest

from whool.init import init_addon_dir


@pytest.fixture
def addon1(tmp_path: Path) -> Path:
    addon_name = "addon1"
    addon_dir = tmp_path / addon_name
    addon_dir.mkdir()
    subprocess.check_call(["git", "init"], cwd=addon_dir)
    subprocess.check_call(
        ["git", "config", "user.email", "test@example.com"], cwd=addon_dir
    )
    subprocess.check_call(["git", "config", "user.name", "test"], cwd=addon_dir)
    addon_dir.joinpath("__manifest__.py").write_text(
        "{'name': 'addon1', 'version': '15.0.1.0.0'}"
    )
    addon_dir.joinpath("__init__.py").touch()
    subprocess.check_call(["git", "add", "."], cwd=addon_dir)
    subprocess.check_call(["git", "commit", "-am", "initial commit"], cwd=addon_dir)
    return addon_dir


@pytest.fixture
def addon1_with_pyproject(addon1: Path) -> Path:
    init_addon_dir(addon1)
    subprocess.check_call(["git", "add", "pyproject.toml"], cwd=addon1)
    addon1.joinpath("__manifest__.py").write_text(
        "{'name': 'addon1', 'version': '15.0.1.1.0'}"
    )
    subprocess.check_call(["git", "commit", "-am", "add pyproject.toml"], cwd=addon1)
    return addon1
