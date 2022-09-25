from pathlib import Path

from whool.init import BUILD_SYSTEM_TOML, init_addon_dir


def test_init_no_pyproject_toml(addon1: Path) -> None:
    pyproject_toml_path = addon1 / "pyproject.toml"
    assert not pyproject_toml_path.exists()
    assert init_addon_dir(addon1)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML in pyproject_toml_path.read_bytes()


def test_init_pyproject_toml_no_build_system(addon1: Path) -> None:
    pyproject_toml_path = addon1 / "pyproject.toml"
    pyproject_toml_path.write_text("[tool.brol]\n")
    assert init_addon_dir(addon1)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML in pyproject_toml_path.read_bytes()


def test_init_pyproject_toml_other_build_system(addon1: Path) -> None:
    other_build_system_toml = b'[build-system]\nrequires = ["brol"]\n'
    pyproject_toml_path = addon1 / "pyproject.toml"
    pyproject_toml_path.write_bytes(other_build_system_toml)
    assert not init_addon_dir(addon1)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML not in pyproject_toml_path.read_bytes()
    assert other_build_system_toml in pyproject_toml_path.read_bytes()
