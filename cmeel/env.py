"""Tools to help environment management."""

import os
import pathlib
import sys

from .consts import CMEEL_PREFIX

PATHS = {
    "cmake": "CMAKE_PREFIX_PATH",
    "lib": "LD_LIBRARY_PATH",
    "pc": "PKG_CONFIG_PATH",
}


def add_paths_arguments(subparsers):
    """Append paths commands for argparse."""
    for cmd, path in PATHS.items():
        sub = subparsers.add_parser(cmd, help=f"show cmeel additions to {path}")
        sub.add_argument("--prepend", action="store_true", help=f"show full {path}")
        sub.set_defaults(cmd=cmd)


def get_paths(cmd: str, prepend: bool = False, **kwargs) -> str:
    """Get the paths needed by the user."""
    prefixes = [pathlib.Path(path) / CMEEL_PREFIX for path in sys.path]
    if cmd == "lib":
        prefixes = [p / "lib" for p in prefixes]
    elif cmd == "pc":
        prefixes = [p / sub / "pkgconfig" for p in prefixes for sub in ["lib", "share"]]

    available = [str(p) for p in prefixes if p.is_dir()]
    if prepend:
        ret = []
        for prefix in available + os.environ.get(PATHS[cmd], "").split(os.pathsep):
            if prefix and prefix not in ret:
                ret.append(prefix)
        return os.pathsep.join(ret)
    return os.pathsep.join(available)
