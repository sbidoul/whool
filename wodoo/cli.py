import argparse
import logging
import os
import subprocess
import sys
import sysconfig
import tempfile
import textwrap

from pep517.build import build as pep517_build

from . import __version__
from .buildapi import _make_dist_info, _prepare_package_metadata


def _get_purelib(python):
    if python == sys.executable:
        return sysconfig.get_paths()["purelib"]
    return subprocess.check_output(
        [python, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
        universal_newlines=True,
    ).strip()


def init(source_dir):
    pyproject_path = os.path.join(source_dir, "pyproject.toml")
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


def install(source_dir, python):
    with tempfile.TemporaryDirectory() as tmpdir:
        pep517_build(source_dir, "wheel", tmpdir)
        wheel = None
        # find generated wheel, the only file in tmpdir
        for f in os.listdir(tmpdir):
            assert not wheel
            assert f.endswith(".whl")
            wheel = f
        subprocess.check_call(
            [python, "-m", "pip", "install", os.path.join(tmpdir, wheel)]
        )


def install_symlink(source_dir, python):
    metadata = _prepare_package_metadata(source_dir)
    _make_dist_info(_get_purelib(), metadata)
    # TODO via wheel to prepare RECORD?
    # TODO add symlink in odoo/addons/addon
    # TODO add odoo, addons, addon in RECORD
    # TODO !!! pip uninstall does not remove the symlink (pip bug)
    raise NotImplementedError()


def main():
    ap = argparse.ArgumentParser(
        description="The Wodoo CLI is a thin wrapper around standard python tools "
        "to build and install pep517 compliant packages. It's most useful "
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
        "-s",
        "--source-dir",
        default=".",
        help="The addon directory, where __manifest__.py and pyproject.toml are "
        "(default: current directory).",
    )
    subparsers = ap.add_subparsers(title="subcommands", dest="subcmd")
    subparsers.add_parser(
        "init",
        help="Initialize pyproject.toml in SOURCE_DIR with the wodoo build-system.",
    )
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
        default=sys.executable,
        help="Target Python executable, if different from the one running Wodoo.",
    )
    parser_build = subparsers.add_parser(
        "build",
        help="Build the addon. A trivial a wrapper around 'python -m pep517.build'.",
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
        init(args.source_dir)
    elif args.subcmd == "install":
        if args.symlink:
            install_symlink(args.source_dir, args.python)
        else:
            install(args.source_dir, args.python)
    elif args.subcmd == "build":
        pep517_build(args.source_dir, "wheel", args.out_dir)
    else:
        ap.print_help()
        sys.exit(1)
