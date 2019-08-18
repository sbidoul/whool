from email.generator import Generator
from email.message import Message
from email.parser import Parser
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from setuptools_odoo.core import (
    _prepare_odoo_addon_metadata as _prepare_setuptools_metadata,
)
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


def _write_metadata(src, msg):
    with open(src, "w") as f:
        Generator(f, maxheaderlen=0).flatten(msg)


def _read_metadata(dst):
    with open(dst, "r") as f:
        return Parser.parsestr(f.read())


def _prepare_wheel_metadata():
    msg = Message()
    msg["Wheel-Version"] = "1.0"  # of the spec
    msg["Generator"] = "Wodoo " + __version__
    msg["Root-Is-Purelib"] = "true"
    msg["Tag"] = TAG
    return msg


def _prepare_package_metadata(addon_dir):
    smeta = _prepare_setuptools_metadata(addon_dir)
    msg = Message()
    msg["Metadata-Version"] = "1.0"
    msg["Name"] = smeta.get("name")
    msg["Version"] = smeta.get("version")
    # Summary
    # Description
    # ...
    return msg


def _make_dist_info(metadata, dst):
    distinfo_dirname = "{}-{}.dist-info".format(
        metadata["name"].replace("-", "_"), metadata["version"]
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
    metadata = _prepare_package_metadata(addon_dir)
    wheel_name = "{}-{}-{}.whl".format(
        metadata["name"].replace("-", "_"), metadata["version"], TAG
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
