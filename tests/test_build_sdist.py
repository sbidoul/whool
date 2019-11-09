from pathlib import Path

from wodoo.buildapi import _build_sdist

DATA_PATH = Path(__file__).parent / "data"


def test_build_sdist(tmp_path):
    sdist_name, addon_name = _build_sdist(DATA_PATH / "addon_1", tmp_path)
    assert addon_name == "addon_1"
    assert sdist_name == "odoo12-addon-addon_1-12.0.1.0.0.tar.gz"
    assert (tmp_path / sdist_name).exists()
