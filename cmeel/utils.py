"""Utilities."""

import logging
import os
import re
import sys
import warnings
from importlib.util import find_spec
from subprocess import check_output

try:
    from packaging.tags import sys_tags
except ImportError as e:
    err = "You need the 'build' extra option to use this build module.\n"
    err += "For this you can install the 'cmeel[build]' package."
    raise ImportError(err) from e


def deprecate_build_system(pyproject, key, default):
    """Cmeel up to v0.22 was using the "build-system" section of pyproject.toml.

    This function helps to deprecate that and move to "tool.cmeel".
    """
    if key in pyproject["build-system"]:
        default = pyproject["build-system"][key]
        warnings.warn(
            'Using the "build-system" section of pyproject.toml for cmeel '
            "configuration is deprecated since cmeel v0.23 and will be removed in v1.\n"
            f'Please move your "{key} = {default}" to the "tool.cmeel" section.',
            DeprecationWarning,
            stacklevel=2,
        )
    if "tool" in pyproject and "cmeel" in pyproject["tool"]:
        return pyproject["tool"]["cmeel"].get(key, default)
    return default


def normalize(name: str) -> str:
    """Normalize name.

    ref. https://packaging.python.org/en/latest/specifications/name-normalization
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def log_pip(log):
    """Log output of pip freeze."""
    if log.getEffectiveLevel() <= logging.DEBUG:
        if find_spec("pip") is not None:
            log.debug("pip freeze:")
            deps = check_output([sys.executable, "-m", "pip", "freeze"], text=True)
            for dep in deps.strip().split("\n"):
                log.debug("  %s", dep)


def get_tag(pyproject):
    """Find the correct tag for the wheel."""
    tag = str(next(sys_tags()))
    # handle cross compilation on macOS with cibuildwheel
    # ref. https://github.com/pypa/cibuildwheel/blob/6549a9/cibuildwheel/macos.py#L221
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        plat = os.environ["_PYTHON_HOST_PLATFORM"].replace("-", "_").replace(".", "_")
        tag = "-".join(tag.split("-")[:-1] + [plat])

    if deprecate_build_system(pyproject, "py3-none", False):
        tag = "-".join(["py3", "none", tag.split("-")[-1]])
    elif deprecate_build_system(pyproject, "any", False):
        tag = "py3-none-any"
    elif deprecate_build_system(pyproject, "pyver-any", False):
        tag = f"py3{sys.version_info.minor}-none-any"
    return tag
