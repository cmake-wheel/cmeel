"""Utilities."""

import logging
import os
import re
import sys
import warnings
from importlib.util import find_spec
from pathlib import Path
from subprocess import CalledProcessError, check_output, run

try:
    from packaging.tags import sys_tags
except ImportError as e:
    err = "You need the 'build' extra option to use this build module.\n"
    err += "For this you can install the 'cmeel[build]' package."
    raise ImportError(err) from e

LOG = logging.getLogger("cmeel.utils")

PATCH_IGNORE = [
    "hunk ignored",
    "hunks ignored",
    "Skipping patch.",
    "The next patch would delete",
]

EXECUTABLE = """#!python
from cmeel.run import cmeel_run
cmeel_run()
"""


class PatchError(CalledProcessError):
    """Exception raised when patch operation failed."""

    def __str__(self):
        """Render this error as a string."""
        if self.returncode and self.returncode < 0:
            return super().__str__()
        return (
            f"Command '{self.cmd}' exit status {self.returncode}\n"
            f"with output:\n{self.output}\n"
            f"and stderr:\n{self.stderr}\n"
        )


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


def log_pip():
    """Log output of pip freeze."""
    if LOG.getEffectiveLevel() <= logging.DEBUG:
        if find_spec("pip") is not None:
            LOG.debug("pip freeze:")
            deps = check_output([sys.executable, "-m", "pip", "freeze"], text=True)
            for dep in deps.strip().split("\n"):
                LOG.debug("  %s", dep)


def get_tag(pyproject) -> str:
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


def patch():
    """Apply cmeel.patch if it exists and was not already applied."""
    if Path("cmeel.patch").exists():
        LOG.info("patching")
        cmd = ["patch", "-p0", "-s", "-N", "-i", "cmeel.patch"]
        ret = run(cmd, capture_output=True, text=True)
        if ret.returncode != 0:
            # If this patch was already applied, it's okay.
            for line in ret.stdout.split("\n"):
                if not line or any(val in line for val in PATCH_IGNORE):
                    continue
                raise PatchError(
                    returncode=ret.returncode,
                    cmd=cmd,
                    output=ret.stdout,
                    stderr=ret.stderr + f"\nwrong line: {line}\n",
                )
            LOG.info("this patch was already applied")


def expose_bin(install: Path, wheel_dir: Path, distribution: str):
    """Add scripts wrapping calls to CMEEL_PREFIX/bin/ executables."""
    bin_dir = install / "bin"
    if bin_dir.is_dir():
        LOG.info("adding executables")
        scripts = wheel_dir / f"{distribution}.data" / "scripts"
        scripts.mkdir(parents=True)
        for fn in bin_dir.glob("*"):
            executable = scripts / fn.name
            with executable.open("w") as fe:
                fe.write(EXECUTABLE)
            executable.chmod(0o755)
