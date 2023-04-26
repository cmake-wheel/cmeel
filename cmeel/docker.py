"""Build a project with cmeel in a container."""

from subprocess import check_call


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
    sub.set_defaults(cmd="docker")


def docker_build(image: str, python: str, **kwargs):
    """Build a project with cmeel in a container."""
    pull = ["docker", "pull", image]
    check_call(pull)
    docker = ["docker", "run", "--rm", "-v", ".:/src", "-w", "/src", "-it", image]
    # update = [python, "-m", "pip", "install", "-U", "pip"]
    build = [python, "-m", "pip", "wheel", "-vw", "wh", "."]
    # cmd = [*docker, "bash", "-c", "'", *update, "&&", *build, "'"]
    cmd = [*docker, *build]
    check_call(cmd)
