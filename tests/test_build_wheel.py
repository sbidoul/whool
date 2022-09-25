from pathlib import Path
from zipfile import ZipFile

from whool.buildapi import _build_wheel


def test_build_wheel(addon1_with_pyproject: Path, tmp_path: Path) -> None:
    wheel_name = _build_wheel(addon1_with_pyproject, tmp_path, editable=False)
    assert wheel_name == "odoo_addon_addon1-15.0.1.1.0-py3-none-any.whl"
    assert (tmp_path / wheel_name).exists()
    with ZipFile(tmp_path / wheel_name) as zf:
        names = zf.namelist()
        assert "odoo/addons/addon1/__manifest__.py" in names
        assert "odoo/addons/addon1/pyproject.toml" not in names
