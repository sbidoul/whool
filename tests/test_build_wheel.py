import os
from pathlib import Path
from zipfile import ZipFile

from whool.buildapi import build_wheel

from .utils import dir_changer


def test_build_wheel(addon1_with_pyproject: Path, tmp_path: Path) -> None:
    with dir_changer(addon1_with_pyproject):
        wheel_name = build_wheel(os.fspath(tmp_path))
        assert wheel_name == "odoo_addon_addon1-15.0.1.1.0.1-py3-none-any.whl"
        assert (tmp_path / wheel_name).exists()
        with ZipFile(tmp_path / wheel_name) as zf:
            names = zf.namelist()
            assert "odoo/addons/addon1/__manifest__.py" in names
            assert "odoo/addons/addon1/pyproject.toml" not in names
