"""Tools to help environment management."""

import argparse
import pathlib
import os
import sys

from .consts import CMEEL_PREFIX

PATHS = {
    "cmake": "CMAKE_PREFIX_PATH",
    "lib": "LD_LIBRARY_PATH",
    "pc": "PKG_CONFIG_PATH",
}


def get_parser() -> argparse.ArgumentParser:
    """Check what the user want."""

    # Get current interpreter
    python = pathlib.Path(sys.executable)
    if str(python.parent) in os.environ.get("PATH", "").split(os.pathsep):
        python = python.name  # its path is in PATH: no need for absolute path

    parser = argparse.ArgumentParser(
        prog=f"{python} -m cmeel", description="cmeel environment helpers"
    )
    subparsers = parser.add_subparsers(
        title="subcommands", description="valid sub-commands", help="sub-command help"
    )

    for cmd, path in PATHS.items():
        sub = subparsers.add_parser(cmd, help=f"show cmeel additions to {path}")
        sub.add_argument("--prepend", action="store_true", help=f"show full {path}")
        sub.set_defaults(cmd=cmd)

    return parser


def get_paths(cmd: str, prepend=False) -> str:
    """Get the paths needed by the user."""
    prefixes = [pathlib.Path(path) / CMEEL_PREFIX for path in sys.path]
    if cmd == "lib":
        prefixes = [p / "lib" for p in prefixes]
    elif cmd == "pc":
        prefixes = [p / sub / "pkgconfig" for p in prefixes for sub in ["lib", "share"]]

    prefixes = [str(p) for p in prefixes if p.exists()]
    if prepend:
        ret = []
        for prefix in prefixes + os.environ.get(PATHS[cmd], "").split(os.pathsep):
            if prefix and prefix not in ret:
                ret.append(prefix)
        return os.pathsep.join(ret)
    else:
        return os.pathsep.join(prefixes)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if "cmd" in args:
        print(get_paths(**vars(args)))
    else:
        parser.print_help()
