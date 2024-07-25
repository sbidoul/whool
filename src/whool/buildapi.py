import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from email.generator import Generator
from email.message import Message
from email.parser import HeaderParser
from pathlib import Path
from typing import Any, Dict, List, Optional

from manifestoo_core.metadata import (
    distribution_name_to_addon_name,
    metadata_from_addon_dir,
)

from .utils import load_pyproject_toml
from .version import version as whool_version

TAG = "py3-none-any"
METADATA_NAME_RE = re.compile(r"^odoo(\d*)-addon-(?P<addon_name>.*)$")


class UnsupportedOperation(NotImplementedError):
    pass


class WhoolException(Exception):
    pass


class NoScmFound(WhoolException):
    pass


def _scm_ls_files(addon_dir: Path) -> List[str]:
    try:
        return (
            subprocess.check_output(
                ["git", "ls-files"], universal_newlines=True, cwd=addon_dir
            )
            .strip()
            .split("\n")
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise NoScmFound() from e


def _copy_to(addon_dir: Path, dst: Path) -> None:
    if _get_pkg_info_metadata(addon_dir):
        # if PKG-INFO is present, assume we are in an sdist, copy everything
        shutil.copytree(addon_dir, dst)
        return
    # copy scm controlled files
    try:
        scm_files = _scm_ls_files(addon_dir)
    except NoScmFound:
        # NOTE This requires pip>=21.3 which builds in-tree. Previous pip versions
        # copied to a temporary directory with a different name than the addon, which
        # caused the resulting distribution name to be wrong.
        shutil.copytree(addon_dir, dst)
    else:
        dst.mkdir()
        for f in scm_files:
            d = Path(f).parent
            dstd = dst / d
            if not dstd.is_dir():
                dstd.mkdir(parents=True)
            shutil.copy(addon_dir / f, dstd)


def _ensure_absent(paths: List[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def _write_metadata(path: Path, msg: Message) -> None:
    with open(path, "w", encoding="utf-8") as f:
        Generator(f, mangle_from_=False, maxheaderlen=0).flatten(msg)


def _prepare_wheel_metadata() -> Message:
    msg = Message()
    msg["Wheel-Version"] = "1.0"  # of the spec
    msg["Generator"] = "Whool " + whool_version
    msg["Root-Is-Purelib"] = "true"
    msg["Tag"] = TAG
    return msg


def _make_dist_info(metadata: Message, dst: Path) -> str:
    dist_info_dirname = "{}-{}.dist-info".format(
        metadata["Name"].replace("-", "_"), metadata["Version"]
    )
    dist_info_path = dst / dist_info_dirname
    dist_info_path.mkdir()
    _write_metadata(dist_info_path / "WHEEL", _prepare_wheel_metadata())
    _write_metadata(dist_info_path / "METADATA", metadata)
    (dist_info_path / "top_level.txt").write_text("odoo")
    return dist_info_dirname


def _make_pkg_info(metadata: Message, dst: Path) -> None:
    _write_metadata(dst / "PKG-INFO", metadata)


def _get_wheel_name(metadata: Message) -> str:
    return "{}-{}-{}.whl".format(
        metadata["Name"].replace("-", "_"), metadata["Version"], TAG
    )


def _get_sdist_base_name(metadata: Message) -> str:
    return "{}-{}".format(metadata["Name"], metadata["Version"])


def _get_pkg_info_metadata(addon_dir: Path) -> Optional[Message]:
    pkg_info_path = Path(addon_dir) / "PKG-INFO"
    if not pkg_info_path.exists():
        return None
    with open(pkg_info_path, encoding="utf-8") as f:
        return HeaderParser().parse(f)


def _get_metadata(addon_dir: Path) -> Message:
    options = load_pyproject_toml(addon_dir).get("tool", {}).get("whool", {})
    whool_post_version_strategy_override = os.getenv(
        "WHOOL_POST_VERSION_STRATEGY_OVERRIDE"
    )
    if whool_post_version_strategy_override:
        options["post_version_strategy_override"] = whool_post_version_strategy_override
    return metadata_from_addon_dir(
        addon_dir,
        options,
        precomputed_metadata_file=addon_dir.joinpath("PKG-INFO"),
    )


def _build_wheel(addon_dir: Path, wheel_directory: Path, editable: bool) -> str:
    metadata = _get_metadata(addon_dir)
    addon_name = distribution_name_to_addon_name(metadata["Name"])
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # always include metadata
        _make_dist_info(metadata, tmppath)
        if editable:
            # Prepare {addon_dir}/build/__editable__/odoo/addon/{addon_name} symlink
            build_dir = addon_dir / "build"
            build_dir.mkdir(parents=True, exist_ok=True)
            build_dir.joinpath(".gitignore").write_text("*")
            editable_dir = build_dir / "__editable__"
            if editable_dir.is_dir():
                shutil.rmtree(editable_dir)
            editable_addons_dir = editable_dir / "odoo" / "addons"
            editable_addons_dir.mkdir(parents=True, exist_ok=True)
            editable_addon_symlink = editable_addons_dir / addon_name
            editable_addon_symlink.symlink_to(addon_dir, target_is_directory=True)
            # Add .pth file pointing to {addon_dir}/build/__editable__ into the wheel
            tmppath.joinpath(metadata["Name"] + ".pth").write_text(
                str(editable_dir.resolve())
            )
        else:
            odoo_addon_path = tmppath / "odoo" / "addons"
            odoo_addon_path.mkdir(parents=True)
            odoo_addon_path = odoo_addon_path / addon_name
            _copy_to(addon_dir, odoo_addon_path)
            # we don't want pyproject.toml nor PKG-INFO in the wheel
            _ensure_absent(
                [odoo_addon_path / "pyproject.toml", odoo_addon_path / "PKG-INFO"]
            )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "wheel",
                "pack",
                "-d",
                os.fspath(wheel_directory),  # conv required on Windows Python 3.7 only
                tmpdir,
            ],
            check=True,
        )
    return _get_wheel_name(metadata)


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Dict[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    return _build_wheel(Path.cwd(), Path(wheel_directory), editable=False)


def build_editable(
    wheel_directory: str,
    config_settings: Optional[Dict[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    return _build_wheel(Path.cwd(), Path(wheel_directory), editable=True)


def _build_sdist(addon_dir: Path, sdist_directory: Path) -> str:
    metadata = _get_metadata(addon_dir)
    sdist_name = _get_sdist_base_name(metadata)
    sdist_tar_name = sdist_name + ".tar.gz"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpppath = Path(tmpdir)
        sdist_tmpdir = tmpppath / sdist_name
        _copy_to(addon_dir, sdist_tmpdir)
        _make_pkg_info(metadata, sdist_tmpdir)
        with tarfile.open(
            str(sdist_directory / sdist_tar_name),
            mode="w|gz",
            format=tarfile.PAX_FORMAT,
        ) as tf:
            tf.add(str(sdist_tmpdir), arcname=sdist_name)
    return sdist_tar_name


def build_sdist(
    sdist_directory: str, config_settings: Optional[Dict[str, Any]] = None
) -> str:
    return _build_sdist(Path.cwd(), Path(sdist_directory))


def prepare_metadata_for_build_wheel(
    metadata_directory: str, config_settings: Optional[Dict[str, Any]] = None
) -> str:
    metadata = _get_metadata(Path.cwd())
    return _make_dist_info(metadata, Path(metadata_directory))


prepare_metadata_for_build_editable = prepare_metadata_for_build_wheel
