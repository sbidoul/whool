import sys
import textwrap
from pathlib import Path

import toml

BUILD_SYSTEM_TOML = textwrap.dedent(
    """\
        [build-system]
        requires = ["wodoo"]
        build-backend = "wodoo.buildapi"
    """
)


def init(addon_dir: Path) -> None:
    pyproject_toml_path = addon_dir / "pyproject.toml"
    if not pyproject_toml_path.exists():
        with open(pyproject_toml_path, "w") as f:
            f.write(BUILD_SYSTEM_TOML)
    else:
        with open(pyproject_toml_path, "r") as f:
            pyproject_toml = toml.load(f)
        if "build-system" in pyproject_toml:
            if (
                pyproject_toml.get("build-system", {}).get("build-backend")
                != "wodoo.build-api"
            ):
                print(
                    f"Did not initialize Wodoo build-system in {pyproject_toml_path} "
                    f"because another one is already defined.",
                    file=sys.stderr,
                )
        else:
            with open(pyproject_toml_path, "a") as f:
                f.write("\n")
                f.write(BUILD_SYSTEM_TOML)
