from pathlib import Path

from wodoo.buildapi import _build_sdist


def test_build_sdist(data_path: Path, tmp_path: Path) -> None:
    sdist_name = _build_sdist(data_path / "addon_1", tmp_path)
    assert sdist_name == "odoo12-addon-addon_1-12.0.1.0.0.tar.gz"
    assert (tmp_path / sdist_name).exists()
