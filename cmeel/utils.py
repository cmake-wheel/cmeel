"""Utilities."""

import logging
import os
import re
import sys
import warnings
from importlib.util import find_spec
from pathlib import Path
from subprocess import CalledProcessError, check_call, check_output, run

from .config import cmeel_config

LOG = logging.getLogger("cmeel.utils")

PATCH_IGNORE = [
    "hunk ignored",
    "hunks ignored",
    "Skipping patch.",
    "The next patch would delete",
]

EXECUTABLE = ["#!python", "from cmeel.run import cmeel_run", "cmeel_run()"]


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


class NonRelocatableError(Exception):
    """Exception raised when absolute paths are in the final package."""

    pass


def dotget(data, key, default):
    """Get key in data or default."""
    for part in key.split("."):
        if part in data:
            data = data[part]
        else:
            return default
    return data


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
    try:
        from packaging.tags import sys_tags
    except ImportError as e:
        err = "You need the 'build' extra option to use this build module.\n"
        err += "For this you can install the 'cmeel[build]' package."
        raise ImportError(err) from e

    tag = str(next(sys_tags()))
    # handle cross compilation on macOS with cibuildwheel
    # ref. https://github.com/pypa/cibuildwheel/blob/6549a9/cibuildwheel/macos.py#L221
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        plat = os.environ["_PYTHON_HOST_PLATFORM"].replace("-", "_").replace(".", "_")
        tag = "-".join(tag.split("-")[:-1] + [plat])

    if deprecate_build_system(pyproject, "py3-none", False):
        warnings.warn(
            "The 'py3-none = true' key is deprecated. Please use 'has-sitelib = false'",
            DeprecationWarning,
            stacklevel=2,
        )
        tag = "-".join(["py3", "none", tag.split("-")[-1]])
    elif deprecate_build_system(pyproject, "any", False):
        warnings.warn(
            "The 'any = true' key is deprecated. "
            "Please use 'has-sitelib = false' and 'has-binaries = false'",
            DeprecationWarning,
            stacklevel=2,
        )
        tag = "py3-none-any"
    elif deprecate_build_system(pyproject, "pyver-any", False):
        warnings.warn(
            "The 'pyver-any = true' key is deprecated. "
            "Please use 'has-binaries = false'",
            DeprecationWarning,
            stacklevel=2,
        )
        tag = f"py3{sys.version_info.minor}-none-any"
    else:
        binaries = dotget(pyproject, "tool.cmeel.has-binaries", True)
        sitelib = dotget(pyproject, "tool.cmeel.has-sitelib", True)
        if not binaries and not sitelib:
            tag = "py3-none-any"
        elif not binaries:
            tag = f"py3{sys.version_info.minor}-none-any"
        elif not sitelib:
            tag = "-".join(["py3", "none", tag.split("-")[-1]])
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
            with fn.open("rb") as fo:
                is_script = fo.read(2) == b"#!"
            with executable.open("w") as fe:
                content = fn.read_text().split("\n") if is_script else EXECUTABLE
                if "python" in content[0]:
                    content = ["#!python", *content[1:]]
                fe.write("\n".join(content))
            executable.chmod(0o755)


def ensure_relocatable(check_relocatable: bool, install: Path, prefix: Path):
    """Ensure no cmake file contains wrong absolute paths."""
    if not check_relocatable:
        return
    LOG.info("check generated cmake files")
    wrong_dirs = [
        "/tmp/pip-build-env",
        "/tmp/pip-req-build",
        "/opt/_internal",
        str(prefix),
    ]
    for fc in install.glob("**/*.cmake"):
        with fc.open() as f:
            cmake_file = f.read()
            if any(wrong_dir in cmake_file for wrong_dir in wrong_dirs):
                lines = cmake_file.split("\n")
                # Get indexes of of problematic lines
                indexes = [
                    idx
                    for idx, line in enumerate(lines)
                    if any(wrong_dir in line for wrong_dir in wrong_dirs)
                ]
                # Get lines at those indexes and around them to display
                display = [
                    f"{i}: {line}"
                    for i, line in enumerate(lines)
                    if any(idx in indexes for idx in (i - 2, i - 1, i, i + 1, i + 2))
                ]
                raise NonRelocatableError(
                    f"{fc} references temporary paths:\n" + "\n".join(display),
                )


def launch_tests(before: bool, now: bool, pyproject, build: Path):
    """Launch tests, before or after the install."""
    if not now:
        return

    test_cmd = deprecate_build_system(
        pyproject,
        "test-cmd",
        ["cmake", "--build", "BUILD_DIR", "-t", "test"],
    )
    LOG.info("test {} install".format("before") if before else "after")
    test_env = cmeel_config.get_test_env()
    cmd = [i.replace("BUILD_DIR", str(build)) for i in test_cmd]
    LOG.debug("test environment: %s", test_env)
    LOG.debug("test command: %s", cmd)
    check_call(cmd, env=test_env)
