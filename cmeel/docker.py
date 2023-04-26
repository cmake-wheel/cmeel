"""Build a project with cmeel in a container."""

import logging
from subprocess import check_call

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
        default="python3.10",
        help="python interpreter inside that image",
    )
    sub.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="update docker image",
    )
    sub.add_argument(
        "-c",
        "--cache",
        action="store_true",
        help="binds /root/.cache/pip",
    )
    sub.set_defaults(cmd="docker")


def docker_build(image: str, python: str, update: bool, cache: bool, **kwargs):
    """Build a project with cmeel in a container."""
    if update:
        pull = ["docker", "pull", image]
        LOG.info("running '%s'", pull)
        check_call(pull)

    volumes = ["-v", ".:/src"]
    if cache:
        volumes = [*volumes, "-v", "/root/.cache/pip:/root/.cache/pip"]
    docker = ["docker", "run", "--rm", *volumes, "-w", "/src", "-it", image]
    # upgrade = [python, "-m", "pip", "install", "-U", "pip"]
    build = [python, "-m", "pip", "wheel", "-vw", "wh", "."]
    # cmd = [*docker, "bash", "-c", "'", *upgrade, "&&", *build, "'"]
    cmd = [*docker, *build]
    LOG.info("running '%s'", cmd)
    check_call(cmd)
