from email.generator import Generator
from email.message import Message
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from setuptools_odoo import get_addon_metadata
from wheel.wheelfile import WheelFile

from . import __version__

TAG = "py3-none-any"


class UnsupportedOperation(Exception):
    pass


class NoScmFound(Exception):
    pass


def _scm_ls_files():
    try:
        return (
            subprocess.check_output(["git", "ls-files"], universal_newlines=True)
            .strip()
            .split()
        )
    except subprocess.CalledProcessError:
        raise NoScmFound()


def _copy_to(dst):
    try:
        scm_files = _scm_ls_files()
    except NoScmFound:
        # shutil.copytree(".", dst)
        raise
    else:
        os.mkdir(dst)
        for f in scm_files:
            d = os.path.dirname(f)
            dstd = os.path.join(dst, d)
            if not os.path.isdir(dstd):
                os.makedirs(dstd)
            shutil.copy(f, dstd)


def _write_metadata(path, msg):
    with open(path, "w", encoding="utf-8") as out:
        Generator(out, mangle_from_=False, maxheaderlen=0).flatten(msg)


def _prepare_wheel_metadata():
    msg = Message()
    msg["Wheel-Version"] = "1.0"  # of the spec
    msg["Generator"] = "Wodoo " + __version__
    msg["Root-Is-Purelib"] = "true"
    msg["Tag"] = TAG
    return msg


def _make_dist_info(metadata, dst):
    distinfo_dirname = "{}-{}.dist-info".format(
        metadata["Name"].replace("-", "_"), metadata["Version"]
    )
    distinfo_path = Path(dst) / distinfo_dirname
    distinfo_path.mkdir()
    _write_metadata(distinfo_path / "WHEEL", _prepare_wheel_metadata())
    _write_metadata(distinfo_path / "METADATA", metadata)
    (distinfo_path / "top_level.txt").write_text("odoo")
    return distinfo_dirname


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    addon_dir = Path.cwd()
    # TODO!!! When pip doing pip install/pip wheel from addon dir,
    # TODO!!! pip copies to a temp dir so addon_name may be wrong;
    # TODO!!! moreover pip loses git information.
    # TODO!!! However when doing this from root with &subdirectory, it's ok
    # TODO!!! because pip copies from the root.
    # TODO!!! python -m pep517.build works fine because it builds in place.
    addon_name = Path.cwd().name
    metadata = get_addon_metadata(addon_dir)
    wheel_name = "{}-{}-{}.whl".format(
        metadata["Name"].replace("-", "_"), metadata["Version"], TAG
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        _make_dist_info(metadata, tmppath)
        odoo_addon_path = tmppath / "odoo" / "addons"
        odoo_addon_path.mkdir(parents=True)
        _copy_to(odoo_addon_path / addon_name)
        with WheelFile(os.path.join(wheel_directory, wheel_name), "w") as wf:
            wf.write_files(tmppath)
    return wheel_name


def build_sdist(sdist_directory, config_settings=None):
    # TODO put PKG-INFO at root
    # TODO pyproject.toml too, I suppose
    # TODO with addon code in odoo/addons or at root?
    raise UnsupportedOperation()
