import argparse
import logging
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

    if args.subcmd == "init":
        init(Path.cwd())
    else:
        ap.print_help()
        sys.exit(1)
