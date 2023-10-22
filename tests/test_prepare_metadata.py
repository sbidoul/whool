import os
import textwrap
from pathlib import Path

from whool.buildapi import (
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

from .utils import dir_changer, env_changer


def test_prepare_metadata_for_build_wheel(addon1: Path, tmp_path: Path) -> None:
    with dir_changer(addon1):
        dist_info_dir = prepare_metadata_for_build_wheel(os.fspath(tmp_path))
        assert dist_info_dir == "odoo_addon_addon1-15.0.1.0.0.1.dist-info"
        dist_info_path = tmp_path / dist_info_dir
        assert dist_info_path.is_dir()
        metadata_path = dist_info_path / "METADATA"
        assert metadata_path.is_file()


def test_prepare_metadata_for_build_editable(addon1: Path, tmp_path: Path) -> None:
    with dir_changer(addon1):
        dist_info_dir = prepare_metadata_for_build_editable(os.fspath(tmp_path))
        assert dist_info_dir == "odoo_addon_addon1-15.0.1.0.0.1.dist-info"
        dist_info_path = tmp_path / dist_info_dir
        assert dist_info_path.is_dir()
        metadata_path = dist_info_path / "METADATA"
        assert metadata_path.is_file()


def test_post_version_strategy_override_in_pyproject(
    addon1_with_pyproject: Path, tmp_path: Path
) -> None:
    # This also tests that options are properly passed to the manifestoo-core
    # metadata_from_addon_dir() function, since the whool tool.whool dict is passed as
    # is.
    with addon1_with_pyproject.joinpath("pyproject.toml").open("a") as f:
        f.write(
            textwrap.dedent(
                """
                [tool.whool]
                post_version_strategy_override = "none"
                """
            )
        )
    with dir_changer(addon1_with_pyproject):
        dist_info_dir = prepare_metadata_for_build_editable(os.fspath(tmp_path))
        assert dist_info_dir == "odoo_addon_addon1-15.0.1.1.0.dist-info"


def test_post_version_strategy_override_in_envvar(
    addon1_with_pyproject: Path, tmp_path: Path
) -> None:
    # Test that the WHOOL_POST_VERSION_STRATEGY_OVERRIDE is properly passed, and has
    # priority over pyproject.toml.
    with addon1_with_pyproject.joinpath("pyproject.toml").open("a") as f:
        f.write(
            textwrap.dedent(
                """
                [tool.whool]
                post_version_strategy_override = "none"
                """
            )
        )
    with dir_changer(addon1_with_pyproject), env_changer(
        {"WHOOL_POST_VERSION_STRATEGY_OVERRIDE": "+1.devN"}
    ):
        dist_info_dir = prepare_metadata_for_build_editable(os.fspath(tmp_path))
        assert dist_info_dir == "odoo_addon_addon1-15.0.1.1.1.dev2.dist-info"
