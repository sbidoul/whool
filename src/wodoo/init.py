import sys
import textwrap
from pathlib import Path

import tomli
from manifestoo_core.addon import Addon
from manifestoo_core.exceptions import AddonNotFound

BUILD_SYSTEM_TOML = textwrap.dedent(
    """\
        [build-system]
        requires = ["wodoo"]
        build-backend = "wodoo.buildapi"
    """
).encode("ascii")


def init(addon_dir: Path) -> bool:
    try:
        Addon.from_addon_dir(addon_dir)
    except AddonNotFound as e:
        print(
            f"Did not initialize Wodoo build-system in {addon_dir} "
            f"because it does not seem to be an Odoo addon directory: {e}.",
            file=sys.stderr,
        )
        return False
    pyproject_toml_path = addon_dir / "pyproject.toml"
    if not pyproject_toml_path.exists():
        with open(pyproject_toml_path, "wb") as f:
            f.write(BUILD_SYSTEM_TOML)
    else:
        with open(pyproject_toml_path, "rb") as f:
            pyproject_toml = tomli.load(f)
        if "build-system" in pyproject_toml:
            if (
                pyproject_toml.get("build-system", {}).get("build-backend")
                != "wodoo.buildapi"
            ):
                print(
                    f"Did not initialize Wodoo build-system in {pyproject_toml_path} "
                    f"because another one is already defined.",
                    file=sys.stderr,
                )
                return False
        else:
            with open(pyproject_toml_path, "ab") as f:
                f.write(b"\n")
                f.write(BUILD_SYSTEM_TOML)
    return True
