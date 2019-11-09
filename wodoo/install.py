import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

from .buildapi import _build_wheel


def _get_purelib_path(python):
    if python == sys.executable:
        return Path(sysconfig.get_paths()["purelib"])
    return Path(
        subprocess.check_output(
            [python, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
            universal_newlines=True,
        ).strip()
    )


def install(addon_dir, python):
    with tempfile.TemporaryDirectory() as tmpdir:
        wheel_name, _, _ = _build_wheel(addon_dir, tmpdir)
        subprocess.check_call([python, "-m", "pip", "install", tmpdir / wheel_name])


def install_symlink(addon_dir, python):
    with tempfile.TemporaryDirectory() as tmpdir:
        wheel_name, dist_info_dirname, addon_name = _build_wheel(
            addon_dir, tmpdir, dist_info_only=True, local_version_identifier="symlink"
        )
        subprocess.check_call([python, "-m", "pip", "install", tmpdir / wheel_name])
        purelib_path = _get_purelib_path(python)
        odoo_addons_path = purelib_path / "odoo" / "addons"
        if not odoo_addons_path.exists():
            odoo_addons_path.mkdir(parents=True)
        addon_path = odoo_addons_path / addon_name
        addon_path.symlink_to(addon_dir)
        record_path = purelib_path / dist_info_dirname / "RECORD"
        with record_path.open("a") as f:
            f.write("odoo/addons/{},,\n".format(addon_name))
        installer_path = purelib_path / dist_info_dirname / "INSTALLER"
        with installer_path.open("w") as f:
            f.write("wodoo")
