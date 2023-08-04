"""Run cmeel as a python module."""

import argparse
import logging
import os
import pathlib
import sys

from . import __version__
from .docker import add_docker_arguments, docker_build
from .env import add_paths_arguments, get_paths
from .release import add_release_arguments, release

LOG = logging.getLogger("cmeel")


def parse_args() -> argparse.Namespace:
    """Check what the user want."""
    # Get current interpreter
    python = pathlib.Path(sys.executable)
    if str(python.parent) in os.environ.get("PATH", "").split(os.pathsep):
        # its path is in PATH: no need for absolute path
        python = pathlib.Path(python.name)

    parser = argparse.ArgumentParser(
        prog=f"{python} -m cmeel",
        description="cmeel helpers",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increment verbosity level",
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid sub-commands",
        help="sub-command help",
    )

    add_paths_arguments(subparsers)
    add_docker_arguments(subparsers)
    add_release_arguments(subparsers)

    ver = subparsers.add_parser("version", help="print current cmeel version.")
    ver.set_defaults(cmd="version")

    args = parser.parse_args()

    if args.verbose == 0:
        level = os.environ.get("CMEEL_LOG_LEVEL", "WARNING")
    else:
        level = 30 - 10 * args.verbose
    logging.basicConfig(level=level)

    LOG.debug("parsed arguments: %s", args)

    if "cmd" in args:
        LOG.debug("running subcommand %s", args.cmd)
        return args

    parser.print_help()
    sys.exit(0)


def main():
    """Run helpers."""
    args = parse_args()
    if args.cmd == "docker":
        docker_build(**vars(args))
    elif args.cmd == "release":
        release(**vars(args))
    elif args.cmd == "version":
        print(f"This is cmeel version {__version__}")
    else:
        print(get_paths(**vars(args)))


if __name__ == "__main__":
    main()
