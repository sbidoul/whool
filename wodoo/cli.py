import argparse
import logging
import os
import sys
from pathlib import Path

from . import __version__
from .init import init


def main() -> None:
    ap = argparse.ArgumentParser(
        description="The Wodoo CLI is a set of useful commands to work "
        "with pep 517 compliant Odoo addons. It's most useful "
        "use case as of fall 2019 is 'wodoo install --symlink'."
    )
    ap.add_argument("-V", "--version", action="version", version="Wodoo " + __version__)
    ap.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Verbosity level (default: warn, once: info, twice: debug).",
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
    # TODO init --git-commit, --git-add

    args = ap.parse_args(sys.argv[1:])

    if args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level)

    addon_dir = os.path.realpath(args.addon_dir)

    if args.subcmd == "init":
        init(Path(addon_dir))
    else:
        ap.print_help()
        sys.exit(1)
