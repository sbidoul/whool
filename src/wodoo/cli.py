import argparse
import logging
import os
import sys
from pathlib import Path

from .init import init
from .version import version


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-V",
        "--version",
        action="version",
        version="Wodoo " + version,
    )
    ap.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Verbosity level (default: warn, once: info, twice: debug).",
    )
    subparsers = ap.add_subparsers(title="subcommands", dest="subcmd")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize pyproject.toml in addon_dir with the wodoo build-system.",
    )
    init_parser.add_argument(
        "--addon-dir",
        default=".",
        help="The addon directory, where __manifest__.py and pyproject.toml are "
        "(default: current directory).",
    )
    # TODO --addons-dir
    # TODO init --git-commit, --git-add

    args = ap.parse_args(sys.argv[1:])
    if args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level)

    if args.subcmd == "init":
        addon_dir = os.path.realpath(args.addon_dir)
        init(Path(addon_dir))
    else:
        ap.print_help()
        sys.exit(1)
