import os
from pathlib import Path
from zipfile import ZipFile

from whool.buildapi import build_editable

from .utils import dir_changer


def test_build_editable(addon1_with_pyproject: Path, tmp_path: Path) -> None:
    with dir_changer(addon1_with_pyproject):
        wheel_name = build_editable(os.fspath(tmp_path))
        # test build directory content
        build_dir = addon1_with_pyproject / "build"
        assert build_dir.is_dir()
        assert build_dir.joinpath(".gitignore").is_file()
        editable_dir = build_dir / "__editable__"
        editable_manifest_path = (
            editable_dir / "odoo" / "addons" / "addon1" / "__manifest__.py"
        )
        assert editable_manifest_path.is_file()
        # test wheel contenet
        assert (tmp_path / wheel_name).exists()
        with ZipFile(tmp_path / wheel_name) as zf:
            names = zf.namelist()
            assert "odoo/addons/addon1/__manifest__.py" not in names
            assert "odoo-addon-addon1.pth" in names
            assert zf.open("odoo-addon-addon1.pth", "r").read().decode("utf-8") == str(
                editable_dir.resolve()
            )
