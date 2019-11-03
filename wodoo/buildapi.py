import os
import shutil
import subprocess
import tempfile
from email.generator import Generator
from email.message import Message
from pathlib import Path

import toml
from setuptools_odoo import get_addon_metadata
from wheel.wheelfile import WheelFile

from . import __version__

TAG = "py3-none-any"


class UnsupportedOperation(NotImplementedError):
    pass


class NoScmFound(Exception):
    pass


def _load_pyproject_toml(addon_dir):
    pyproject_toml_path = os.path.join(addon_dir, "pyproject.toml")
    if os.path.exists(pyproject_toml_path):
        with open(pyproject_toml_path) as f:
            return toml.load(f)
    return {}


def _scm_ls_files(addon_dir):
    try:
        return (
            subprocess.check_output(
                ["git", "ls-files"], universal_newlines=True, cwd=addon_dir
            )
            .strip()
            .split()
        )
    except subprocess.CalledProcessError:
        raise NoScmFound()


def _copy_to(addon_dir, dst):
    try:
        scm_files = _scm_ls_files(addon_dir)
    except NoScmFound:
        # TODO DO NOT UNCOMMENT, until pip builds in place.
        # TODO In case pip copies, this will crash because of
        # TODO missing .git directory. If it would not crash
        # TODO the addon name would be wrong because cwd is a temp dir.
        # shutil.copytree(addon_dir, dst)
        raise
    else:
        os.mkdir(dst)
        for f in scm_files:
            d = os.path.dirname(f)
            dstd = os.path.join(dst, d)
            if not os.path.isdir(dstd):
                os.makedirs(dstd)
            shutil.copy(os.path.join(addon_dir, f), dstd)


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
    dist_info_dirname = "{}-{}.dist-info".format(
        metadata["Name"].replace("-", "_"), metadata["Version"]
    )
    dist_info_path = Path(dst) / dist_info_dirname
    dist_info_path.mkdir()
    _write_metadata(dist_info_path / "WHEEL", _prepare_wheel_metadata())
    _write_metadata(dist_info_path / "METADATA", metadata)
    (dist_info_path / "top_level.txt").write_text("odoo")
    return dist_info_dirname


def _get_addon_name(addon_dir):
    return Path(addon_dir).resolve().name


def _get_wheel_name(metadata):
    return "{}-{}-{}.whl".format(
        metadata["Name"].replace("-", "_"), metadata["Version"], TAG
    )


def _get_metadata(addon_dir, local_version_identifier=None):
    options = (
        _load_pyproject_toml(addon_dir)
        .get("tool", {})
        .get("wodoo", {})
        .get("options", {})
    )
    metadata = get_addon_metadata(
        addon_dir,
        depends_override=options.get("depends_override", {}),
        external_dependencies_override=options.get(
            "external_dependencies_override", {}
        ),
        odoo_version_override=options.get("odoo_version_override"),
    )
    if local_version_identifier:
        metadata.replace_header(
            "Version", metadata["Version"] + "+" + local_version_identifier
        )
    return metadata


def _build_wheel(
    addon_dir, wheel_directory, dist_info_only=False, local_version_identifier=None
):
    addon_name = _get_addon_name(addon_dir)
    metadata = _get_metadata(
        addon_dir, local_version_identifier=local_version_identifier
    )
    wheel_name = _get_wheel_name(metadata)
    with tempfile.TemporaryDirectory() as tmpdir:
        dist_info_dirname = _make_dist_info(metadata, tmpdir)
        if not dist_info_only:
            odoo_addon_path = Path(tmpdir) / "odoo" / "addons"
            odoo_addon_path.mkdir(parents=True)
            _copy_to(addon_dir, odoo_addon_path / addon_name)
        with WheelFile(os.path.join(wheel_directory, wheel_name), "w") as wf:
            wf.write_files(tmpdir)
    return wheel_name, dist_info_dirname, addon_name


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    wheel_name, _, _ = _build_wheel(Path.cwd(), wheel_directory)
    return wheel_name


def build_sdist(sdist_directory, config_settings=None):
    # TODO put PKG-INFO and pyproject.toml at root
    # TODO with addon code in odoo/addons or at root?
    raise UnsupportedOperation()
