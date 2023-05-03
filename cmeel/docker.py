"""Build a project with cmeel in a container."""

import logging
import os
import pathlib
from subprocess import check_call
from typing import List, Optional

from .backports import BooleanOptionalAction

LOG = logging.getLogger("cmeel.docker")


def add_docker_arguments(subparsers):
    """Append docker command for argparse."""
    sub = subparsers.add_parser("docker", help="build a project in a container.")
    sub.add_argument(
        "-i",
        "--image",
        default="quay.io/pypa/manylinux_2_28_x86_64",
        help="docker image to use for building the wheel",
    )
    sub.add_argument(
        "-p",
        "--python",
        default="python3.11",
        help="python interpreter inside that image",
    )
    sub.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="update docker image",
    )
    sub.add_argument(
        "-U",
        "--upgrade",
        action="store_true",
        help="upgrade pip",
    )
    sub.add_argument(
        "-c",
        "--cache",
        action="store_true",
        help="binds /root/.cache/pip",
    )
    sub.add_argument(
        "-C",
        "--cwd",
        default=str(pathlib.Path.cwd()),
        help="build the project in this directory",
    )
    sub.add_argument(
        "-e",
        "--env",
        action="append",
        help="pass environment variables to docker run",
    )
    sub.add_argument(
        "--cmeel-env",
        action=BooleanOptionalAction,
        default=True,
        help="forward 'CMEEL_*' environment variables to docker run",
    )
    sub.set_defaults(cmd="docker")


def docker_build(
    image: str,
    python: str,
    update: bool,
    cache: bool,
    upgrade: bool,
    cwd: str,
    env: Optional[List[str]],
    cmeel_env: bool,
    **kwargs,
):
    """Build a project with cmeel in a container."""
    if update:
        pull = ["docker", "pull", image]
        LOG.info("running '%s'", pull)
        check_call(pull)

    volumes = ["-v", f"{cwd}/:/src"]
    envs: List[str] = []
    if env:
        for e in env:
            envs = [*envs, "-e", e]
    if cmeel_env:
        for e in os.environ:
            if e.startswith("CMEEL_"):
                envs = [*envs, "-e", e]
    if cache:
        volumes = [*volumes, "-v", "/root/.cache/pip:/root/.cache/pip"]
    docker = ["docker", "run", "--rm", *envs, *volumes, "-w", "/src", "-t", image]
    build = [python, "-m", "pip", "wheel", "-vw", "wh", "."]
    if upgrade:
        pip = [python, "-m", "pip", "install", "-U", "pip"]
        pip_cmd = " ".join(pip)
        build_cmd = " ".join(build)
        cmd = [*docker, "bash", "-c", f"{pip_cmd} && {build_cmd}"]
    else:
        cmd = [*docker, *build]
    LOG.info("running '%s'", cmd)
    check_call(cmd)
