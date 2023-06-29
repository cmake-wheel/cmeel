#!/usr/bin/env python
"""Helper to release a cmeel project."""
from logging import getLogger
from pathlib import Path
from subprocess import check_call

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

LOG = getLogger("cmeel.release")


def add_release_arguments(subparsers):
    """Append release command for argparse."""
    sub = subparsers.add_parser("release", help="release a cmeel project.")
    sub.set_defaults(cmd="release")


def release(**kwargs):
    """Release a cmeel project."""
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    version = pyproject["project"]["version"]
    build = pyproject.get("tool", {}).get("cmeel", {}).get("build-number", 0)
    tag = f"v{version}.c{build}"
    release = f"Cmeel Release {tag}"

    LOG.info("Releasing vesion '%s'", tag)

    commit_cmd = ["git", "commit", "-am", release]
    LOG.debug("commit command: %s", commit_cmd)
    check_call(commit_cmd)

    tag_cmd = ["git", "tag", "-s", tag, "-m", release]
    LOG.debug("tag command: %s", tag_cmd)
    check_call(tag_cmd)

    push_cmd = ["git", "push", "origin", tag]
    LOG.debug("push command: %s", push_cmd)
    check_call(push_cmd)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    release()
