import os
from pathlib import Path
from tarfile import TarFile

from whool.buildapi import _build_sdist, build_sdist

from .utils import dir_changer


def test_build_sdist(addon1: Path, tmp_path: Path) -> None:
    with dir_changer(addon1):
        sdist_name = build_sdist(os.fspath(tmp_path))
        assert sdist_name == "odoo_addon_addon1-15.0.1.0.0.1.tar.gz"
        assert (tmp_path / sdist_name).exists()


def test_build_sdist_from_sdist(addon1_with_pyproject: Path, tmp_path: Path) -> None:
    sdist_name = _build_sdist(addon1_with_pyproject, tmp_path)
    assert sdist_name == "odoo_addon_addon1-15.0.1.1.0.1.tar.gz"
    # extract sdist and test that the root directory has the correct name
    tmp_path2 = tmp_path / "2"
    tmp_path2.mkdir()
    with TarFile.open(tmp_path / sdist_name, mode="r:gz") as tf1:
        tf1_names = sorted(tf1.getnames())
        tf1.extractall(tmp_path2)
    assert "odoo_addon_addon1-15.0.1.1.0.1/PKG-INFO" in tf1_names
    assert "odoo_addon_addon1-15.0.1.1.0.1/pyproject.toml" in tf1_names
    # build sdist from sdist
    tmp_path3 = tmp_path / "3"
    tmp_path3.mkdir()
    sdist_name = _build_sdist(tmp_path2 / "odoo_addon_addon1-15.0.1.1.0.1", tmp_path3)
    assert sdist_name == "odoo_addon_addon1-15.0.1.1.0.1.tar.gz"
    # extract 2nd sdist and test that the root directory has the correct name
    with TarFile.open(tmp_path3 / sdist_name, mode="r:gz") as tf2:
        tf2_names = sorted(tf2.getnames())
        tf2.extractall(tmp_path3)
    # content of both sdists must be identical
    assert tf1_names == tf2_names
    # PKG-INFO in both sdists must be identical
    assert (tmp_path2 / "odoo_addon_addon1-15.0.1.1.0.1" / "PKG-INFO").read_bytes() == (
        tmp_path3 / "odoo_addon_addon1-15.0.1.1.0.1" / "PKG-INFO"
    ).read_bytes()
