from wodoo.init import BUILD_SYSTEM_TOML, init


def test_init_no_pyproject_toml(tmp_path):
    pyproject_toml_path = tmp_path / "pyproject.toml"
    assert not pyproject_toml_path.exists()
    init(tmp_path)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML in pyproject_toml_path.read_text()


def test_init_pyproject_toml_no_build_system(tmp_path):
    pyproject_toml_path = tmp_path / "pyproject.toml"
    pyproject_toml_path.write_text("[tool.brol]\n")
    init(tmp_path)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML in pyproject_toml_path.read_text()


def test_init_pyproject_toml_other_build_system(tmp_path):
    other_build_system_toml = '[build-system]\nrequires = ["brol"]\n'
    pyproject_toml_path = tmp_path / "pyproject.toml"
    pyproject_toml_path.write_text(other_build_system_toml)
    init(tmp_path)
    assert pyproject_toml_path.exists()
    assert BUILD_SYSTEM_TOML not in pyproject_toml_path.read_text()
    assert other_build_system_toml in pyproject_toml_path.read_text()
