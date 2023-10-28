from pathlib import Path

import pytest

from whool.cli import main
from whool.init import BUILD_SYSTEM_TOML, init, init_addon_dir

from .utils import dir_changer


def test_init_addon_dir_no_pyproject_toml(addon1: Path) -> None:
    pyproject_toml_path = addon1 / "pyproject.toml"
    assert not pyproject_toml_path.exists()
    assert init_addon_dir(addon1)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML in pyproject_toml_path.read_bytes()


def test_init_addon_dir_pyproject_toml_no_build_system(addon1: Path) -> None:
    pyproject_toml_path = addon1 / "pyproject.toml"
    pyproject_toml_path.write_text("[tool.brol]\n")
    assert init_addon_dir(addon1)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML in pyproject_toml_path.read_bytes()


def test_init_addon_dir_pyproject_toml_other_build_system(addon1: Path) -> None:
    other_build_system_toml = b'[build-system]\nrequires = ["brol"]\n'
    pyproject_toml_path = addon1 / "pyproject.toml"
    pyproject_toml_path.write_bytes(other_build_system_toml)
    assert not init_addon_dir(addon1)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML not in pyproject_toml_path.read_bytes()
    assert other_build_system_toml in pyproject_toml_path.read_bytes()


def test_init_in_addon_dir(addon1: Path) -> None:
    assert init(addon1) == [addon1]


def test_init_in_addon_dir_with_pyproject(addon1_with_pyproject: Path) -> None:
    assert init(addon1_with_pyproject) == []


def test_init_in_non_addon_dir(tmp_path: Path) -> None:
    assert init(tmp_path) == []


def test_init_in_addons_dir(addon1: Path) -> None:
    assert init(addon1.parent) == [addon1]


def test_init_in_addons_dir_mixed(addon1: Path) -> None:
    (addon1.parent / "not_addon2").mkdir()
    (addon1.parent / "brol").touch()
    assert init(addon1.parent) == [addon1]


def test_init_in_addons_dir_with_pyproject(addon1_with_pyproject: Path) -> None:
    assert init(addon1_with_pyproject.parent) == []


def test_init_cli(addon1: Path) -> None:
    pyproject_toml_path = addon1 / "pyproject.toml"
    assert not pyproject_toml_path.exists()
    with dir_changer(addon1):
        assert main(["init"]) == 0
    assert pyproject_toml_path.exists()


def test_init_cli_nonzero_exit(
    addon1: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pyproject_toml_path = addon1 / "pyproject.toml"
    assert not pyproject_toml_path.exists()
    with dir_changer(addon1):
        assert main(["init", "--exit-non-zero-on-changes"]) == 1
    assert pyproject_toml_path.exists()
    captured = capsys.readouterr()
    assert captured.err == "pyproject.toml was generated or modified in .\n"
