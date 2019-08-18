import argparse
import os
import subprocess
import sys
import tempfile

from pep517.build import build as pep517_build

from . import __version__
from .buildapi import _make_dist_info, _prepare_package_metadata


def _get_purelib(python):
    if python != sys.executable:
        # TODO (ses how flit _get_dirs does it)
        raise NotImplementedError()
    import sysconfig

    return sysconfig.get_paths()["purelib"]


def install(python):
    with tempfile.TemporaryDirectory() as tmpdir:
        pep517_build(".", "wheel", tmpdir)
        wheel = None
        # find generated wheel, the only file in tmpdir
        for f in os.listdir(tmpdir):
            assert not wheel
            assert f.endswith(".whl")
            wheel = f
        subprocess.check_call(
            [python, "-m", "pip", "install", os.path.join(tmpdir, wheel)]
        )


def install_symlink(python):
    metadata = _prepare_package_metadata(".")
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
    subparsers = ap.add_subparsers(title="subcommands", dest="subcmd")
    parser_install = subparsers.add_parser(
        "install",
        help="Install the addon. "
        "--symlink is mostly a workaround for pip install "
        "--editable not being compatible with pep517 yet; when "
        "--symlink is not used, this command builds the wheel "
        "and installs it with pip; for more advanced use cases, "
        "please use pep517.build and pip",
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
    parser_build.add_argument("--binary", "-b", action="store_true", default=False)
    parser_build.add_argument("--source", "-s", action="store_true", default=False)
    parser_build.add_argument(
        "--out-dir", "-o", help="Destination in which to save the builds"
    )

    args = ap.parse_args(sys.argv[1:])

    if args.subcmd == "install":
        if args.symlink:
            install_symlink(args.python)
        else:
            install(args.python)
    elif args.subcmd == "build":
        # determine which dists to build
        dists = list(
            filter(
                None,
                (
                    "sdist" if args.source or not args.binary else None,
                    "wheel" if args.binary or not args.source else None,
                ),
            )
        )
        for dist in dists:
            pep517_build(".", dist, args.out_dir)
    else:
        ap.print_help()
        sys.exit(1)
