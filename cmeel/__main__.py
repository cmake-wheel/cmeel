"""Run cmeel as a python module."""

import argparse
import os
import sys
from pathlib import Path

from .docker import add_docker_arguments, docker_build
from .helpers import add_paths_arguments, get_paths


def get_parser() -> argparse.ArgumentParser:
    """Check what the user want."""
    # Get current interpreter
    python = Path(sys.executable)
    if str(python.parent) in os.environ.get("PATH", "").split(os.pathsep):
        python = Path(python.name)  # its path is in PATH: no need for absolute path

    parser = argparse.ArgumentParser(
        prog=f"{python} -m cmeel",
        description="cmeel environment helpers",
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid sub-commands",
        help="sub-command help",
    )

    add_paths_arguments(subparsers)
    add_docker_arguments(subparsers)

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if "cmd" in args:
        if args.cmd == "docker":
            docker_build(**vars(args))
        else:
            print(get_paths(**vars(args)))
    else:
        parser.print_help()
