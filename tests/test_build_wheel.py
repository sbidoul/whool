from pathlib import Path
from zipfile import ZipFile

from wodoo.buildapi import _build_wheel


def test_build_wheel(data_path: Path, tmp_path: Path) -> None:
    wheel_name = _build_wheel(data_path / "addon_1", tmp_path, editable=False)
    assert wheel_name == "odoo12_addon_addon_1-12.0.1.0.0-py3-none-any.whl"
    assert (tmp_path / wheel_name).exists()
    with ZipFile(tmp_path / wheel_name) as zf:
        names = zf.namelist()
        assert "odoo/addons/addon_1/__manifest__.py" in names
        assert "odoo/addons/addon_1/pyproject.toml" not in names
