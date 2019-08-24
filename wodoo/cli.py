import argparse
import logging
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import tempfile
import textwrap

from . import __version__
from .buildapi import _build_wheel


def _get_purelib_path(python):
    if python == sys.executable:
        return Path(sysconfig.get_paths()["purelib"])
    return Path(
        subprocess.check_output(
            [python, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
            universal_newlines=True,
        ).strip()
    )


def init(addon_dir):
    pyproject_path = os.path.join(addon_dir, "pyproject.toml")
    if not os.path.exists(pyproject_path):
        with open(pyproject_path, "w") as f:
            f.write(
                textwrap.dedent(
                    """\
                        [build-system]
                        requires = ["wodoo"]
                        build-backend = "wodoo.buildapi
                    """
                )
            )
    else:
        # TODO inject build-system into pyproject.toml if not yet present
        raise NotImplementedError()


def install(addon_dir, python):
    with tempfile.TemporaryDirectory() as tmpdir:
        wheel_name, _, _ = _build_wheel(addon_dir, tmpdir)
        subprocess.check_call(
            [python, "-m", "pip", "install", os.path.join(tmpdir, wheel_name)]
        )


def install_symlink(addon_dir, python):
    with tempfile.TemporaryDirectory() as tmpdir:
        wheel_name, dist_info_dirname, addon_name = _build_wheel(
            addon_dir, tmpdir, dist_info_only=True, local_version_identifier="symlink"
        )
        subprocess.check_call(
            [python, "-m", "pip", "install", os.path.join(tmpdir, wheel_name)]
        )
        purelib_path = _get_purelib_path(python)
        odoo_addons_path = purelib_path / "odoo" / "addons"
        if not odoo_addons_path.exists():
            odoo_addons_path.mkdir(parents=True)
        addon_path = odoo_addons_path / addon_name
        addon_path.symlink_to(os.path.abspath(addon_dir))
        record_path = purelib_path / dist_info_dirname / "RECORD"
        with record_path.open("a") as f:
            f.write("odoo/addons/{},,\n".format(addon_name))
        installer_path = purelib_path / dist_info_dirname / "INSTALLER"
        with installer_path.open("w") as f:
            f.write("wodoo")


def main():
    ap = argparse.ArgumentParser(
        description="The Wodoo CLI is a set of usefull commands to work "
        "with pep 517 compliant Odoo addons. It's most useful "
        "use case as of fall 2019 is 'wodoo install --symlink'."
    )
    ap.add_argument("-V", "--version", action="version", version="Wodoo " + __version__)
    ap.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Verbosity level (default: warnings, once: info, twice: debug).",
    )
    ap.add_argument(
        "--addon-dir",
        default=".",
        help="The addon directory, where __manifest__.py and pyproject.toml are "
        "(default: current directory).",
    )
    # TODO --addons-dir
    subparsers = ap.add_subparsers(title="subcommands", dest="subcmd")
    subparsers.add_parser(
        "init",
        help="Initialize pyproject.toml in addon_dir with the wodoo build-system.",
    )
    # TODO init --commit
    parser_install = subparsers.add_parser(
        "install",
        help="Install the addon. "
        "--symlink is mostly a workaround for pip install "
        "--editable not being compatible with pep517 yet. When "
        "--symlink is not used, this command builds the wheel "
        "and installs it with pip. For more advanced use cases, "
        "please use pep517.build and pip.",
    )
    parser_install.add_argument(
        "-s",
        "--symlink",
        action="store_true",
        help="Symlink the addon into site packages instead of copying it.",
    )
    parser_install.add_argument(
        "--python",
        help="Target Python executable. If not set, use the python of the "
        "active current virtualenv, or else the python running wodoo.",
    )
    parser_build = subparsers.add_parser(
        "build",
        help="Build the addon. A trivial alternative to 'python -m pep517.build'.",
    )
    parser_build.add_argument(
        "--out-dir", "-o", required=True, help="Destination in which to save the build."
    )

    args = ap.parse_args(sys.argv[1:])

    if args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level)

    if args.subcmd == "init":
        init(args.addon_dir)
    elif args.subcmd == "install":
        python = args.python
        if not python:
            venv = os.environ.get("VIRTUAL_ENV")
            if venv:
                python = os.path.join(venv, "bin", "python")
            else:
                python = sys.executable
        if args.symlink:
            install_symlink(args.addon_dir, python)
        else:
            install(args.addon_dir, python)
    elif args.subcmd == "build":
        _build_wheel(args.addon_dir, args.out_dir)
    else:
        ap.print_help()
        sys.exit(1)
