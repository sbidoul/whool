import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .init import init
from .version import version


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-V",
        "--version",
        action="version",
        version="Whool " + version,
    )
    ap.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Verbosity level (default: warn, once: info, twice: debug).",
    )
    subparsers = ap.add_subparsers(title="subcommands", dest="subcmd")

    init_ap = subparsers.add_parser(
        "init",
        help=(
            "Initialize pyproject.toml files with the whool build-system. "
            "This is done in the current directory if it is an addon, "
            "else in immediate subdirectories that are addons."
        ),
    )
    init_ap.add_argument(
        "--exit-non-zero-on-changes",
        action="store_true",
        help="Exit with non-zero status if any changes were made.",
    )

    args = ap.parse_args(argv)
    if args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    logging.basicConfig(level=log_level)

    if args.subcmd == "init":
        modified_files = init(Path.cwd())
        if args.exit_non_zero_on_changes and modified_files:
            return 1
        return 0

    ap.print_help()
    return 1
