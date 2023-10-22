import os
from pathlib import Path

from whool.buildapi import (
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

from .utils import dir_changer


def test_prepare_metadata_for_build_wheel(addon1: Path, tmp_path: Path) -> None:
    with dir_changer(addon1):
        dist_info_dir = prepare_metadata_for_build_wheel(os.fspath(tmp_path))
        assert dist_info_dir == "odoo_addon_addon1-15.0.1.0.0.dist-info"
        dist_info_path = tmp_path / dist_info_dir
        assert dist_info_path.is_dir()
        metadata_path = dist_info_path / "METADATA"
        assert metadata_path.is_file()


def test_prepare_metadata_for_build_editable(addon1: Path, tmp_path: Path) -> None:
    with dir_changer(addon1):
        dist_info_dir = prepare_metadata_for_build_editable(os.fspath(tmp_path))
        assert dist_info_dir == "odoo_addon_addon1-15.0.1.0.0.dist-info"
        dist_info_path = tmp_path / dist_info_dir
        assert dist_info_path.is_dir()
        metadata_path = dist_info_path / "METADATA"
        assert metadata_path.is_file()
