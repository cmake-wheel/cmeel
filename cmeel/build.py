"""Cmeel build."""
import logging
import os
import re
import sys
import warnings
from importlib.util import find_spec
from pathlib import Path
from subprocess import CalledProcessError, check_call, check_output, run

try:
    from packaging.tags import sys_tags
except ImportError as e:
    err = "You need the 'build' extra option to use this build module.\n"
    err += "For this you can install the 'cmeel[build]' package."
    raise ImportError(err) from e
import tomli

from . import __version__
from .config import cmeel_config
from .consts import CMEEL_PREFIX, SITELIB

LOG = logging.getLogger("cmeel")
EXECUTABLE = """#!python
from cmeel.run import cmeel_run
cmeel_run()
"""
PATCH_IGNORE = [
    "hunk ignored",
    "hunks ignored",
    "Skipping patch.",
    "The next patch would delete",
]


class NonRelocatableError(Exception):
    """Exception raised when absolute paths are in the final package."""

    pass


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


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    """Build an editable wheel: main entry point for PEP 660."""
    os.environ["CMAKE_INSTALL_MODE"] = "ABS_SYMLINK"
    return build(wheel_directory, editable=True)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build a binary wheel: main entry point for PEP 517."""
    return build(wheel_directory, editable=False)


def build(wheel_directory, editable=False):  # noqa: C901 TODO
    """Run CMake configure / build / test / install steps, and pack the wheel."""
    logging.basicConfig(level=cmeel_config.log_level.upper())
    LOG.info("CMake Wheel in editable mode" if editable else "CMake Wheel")
    if LOG.getEffectiveLevel() <= logging.DEBUG:
        if find_spec("pip") is not None:
            LOG.debug("pip freeze:")
            deps = check_output([sys.executable, "-m", "pip", "freeze"], text=True)
            for dep in deps.strip().split("\n"):
                LOG.debug("  %s", dep)

    prefix = Path(".") / "build-editable" if editable else cmeel_config.temp_dir
    build = prefix / "bld"
    wheel_dir = prefix / "whl"
    install = (prefix if editable else wheel_dir) / CMEEL_PREFIX
    tag = str(next(sys_tags()))
    # handle cross compilation on macOS with cibuildwheel
    # ref. https://github.com/pypa/cibuildwheel/blob/6549a9/cibuildwheel/macos.py#L221
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        plat = os.environ["_PYTHON_HOST_PLATFORM"].replace("-", "_").replace(".", "_")
        tag = "-".join(tag.split("-")[:-1] + [plat])

    LOG.info("load conf from pyproject.toml")
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomli.load(f)
        conf = pyproject["project"]
        source = deprecate_build_system(pyproject, "source", ".")
        run_tests = (
            os.environ.get("CMEEL_RUN_TESTS", "ON").upper()
            not in ("0", "NO", "OFF", "FALSE")
            if "CMEEL_RUN_TESTS" in os.environ
            else deprecate_build_system(pyproject, "run-tests", True)
        )
        run_tests_after_install = deprecate_build_system(
            pyproject,
            "run-tests-after-install",
            False,
        )
        build_number = deprecate_build_system(pyproject, "build-number", 0)
        configure_args = deprecate_build_system(pyproject, "configure-args", [])
        test_cmd = deprecate_build_system(
            pyproject,
            "test-cmd",
            ["cmake", "--build", "BUILD_DIR", "-t", "test"],
        )
        check_relocatable = deprecate_build_system(pyproject, "check-relocatable", True)
        fix_pkg_config = deprecate_build_system(pyproject, "fix-pkg-config", True)
        if deprecate_build_system(pyproject, "py3-none", False):
            tag = "-".join(["py3", "none", tag.split("-")[-1]])
        elif deprecate_build_system(pyproject, "any", False):
            tag = "py3-none-any"
        elif deprecate_build_system(pyproject, "pyver-any", False):
            tag = f"py3{sys.version_info.minor}-none-any"
    distribution = f"{conf['name'].replace('-', '_')}-{conf['version']}"

    LOG.info("build wheel")

    # Patch

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

    # Set env

    if run_tests_after_install:
        path = f"{install / SITELIB}"
        old = os.environ.get("PYTHONPATH", "")
        if old:
            path += f"{os.pathsep}{old}"
        os.environ.update(PYTHONPATH=path)

    # Configure

    LOG.info("configure")
    configure_env = cmeel_config.get_configure_env()
    configure_args = cmeel_config.get_configure_args(
        conf,
        install,
        configure_args,
        configure_env,
        run_tests,
    )
    configure_cmd = ["cmake", "-S", source, "-B", str(build), *configure_args]
    LOG.debug("configure environment: %s", configure_env)
    LOG.debug("configure command: %s", configure_cmd)
    check_call(configure_cmd, env=configure_env)

    LOG.info("build")
    build_cmd = ["cmake", "--build", str(build), f"-j{cmeel_config.jobs}"]
    LOG.debug("build command: %s", build_cmd)
    check_call(build_cmd)

    def launch_tests():
        LOG.info("test")
        test_env = cmeel_config.get_test_env()
        cmd = [i.replace("BUILD_DIR", str(build)) for i in test_cmd]
        LOG.debug("test environment: %s", test_env)
        LOG.debug("test command: %s", cmd)
        check_call(cmd, env=test_env)

    if run_tests and not run_tests_after_install:
        launch_tests()

    LOG.info("install")
    install_cmd = ["cmake", "--build", str(build), "-t", "install"]
    LOG.debug("install command: %s", install_cmd)
    check_call(install_cmd)

    if run_tests and run_tests_after_install:
        launch_tests()

    LOG.info("fix relocatablization")
    # Replace absolute install path in generated .cmake files, if any.
    for f in install.rglob("*.cmake"):
        ff = install / f"{f.stem}.fix"
        with f.open("r") as fr, ff.open("w") as fw:
            fw.write(fr.read().replace(str(install), "${PACKAGE_PREFIX_DIR}"))
        f.unlink()
        ff.rename(f)

    LOG.info("create dist-info")

    dist_info = wheel_dir / f"{distribution}.dist-info"
    dist_info.mkdir(parents=True)

    LOG.info("create dist-info / METADATA")

    metadata = [
        "Metadata-Version: 2.1",
        f"Name: {conf['name']}",
        f"Version: {conf['version']}",
        f"Summary: {conf['description']}",
        f"License-Expression: {conf['license']}",
        f"Requires-Python: {conf.get('requires-python', '>=3.7')}",
    ]

    authors = []
    maintainers = []
    authors_email = []
    maintainers_email = []

    for author in conf.get("authors", {}):
        if "name" in author and "email" in author:
            authors_email.append(f"{author['name']} <{author['email']}>")
        elif "email" in author:
            authors_email.append(author["email"])
        elif "name" in author:
            authors.append(author["name"])

    for maintainer in conf.get("maintainers", {}):
        if "name" in maintainer and "email" in maintainer:
            maintainers_email.append(f"{maintainer['name']} <{maintainer['email']}>")
        elif "email" in maintainer:
            maintainers_email.append(maintainer["email"])
        elif "name" in maintainer:
            maintainers.append(maintainer["name"])

    if authors:
        metadata.append("Author: " + ",".join(authors))
    if authors_email:
        metadata.append("Author-email: " + ",".join(authors_email))
    if maintainers:
        metadata.append("Maintainer: " + ",".join(maintainers))
    if maintainers_email:
        metadata.append("Maintainer-email: " + ",".join(maintainers_email))

    if "urls" in conf:
        for key, url in conf["urls"].items():
            if key == "homepage":
                metadata.append(f"Home-page: {url}")
            else:
                name = key.replace("-", " ").capitalize()
                metadata.append(f"Project-URL: {name}, {url}")

    dependencies = ["cmeel", *conf.get("dependencies", [])]
    for dep in dependencies:
        metadata.append(f"Requires-Dist: {dep}")

    build_dependencies = [
        build_dep
        for build_dep in pyproject["build-system"]["requires"]
        if build_dep != "cmeel[build]" and build_dep not in dependencies
    ]
    if build_dependencies:
        metadata.append("Provides-Extra: build")
        for build_dep in build_dependencies:
            metadata.append(f'Requires-Dist: {build_dep} ; extra == "build"')

    for classifier in conf.get("classifiers", []):
        metadata.append(f"Classifier: {classifier}")

    if "readme" not in conf:
        for ext in [".md", ".rst", ".txt", ""]:
            readme = f"README{ext}"
            if Path(readme).exists():
                conf["readme"] = readme
                break
    if "readme" in conf:
        if conf["readme"].lower().endswith(".md"):
            content_type = "text/markdown"
        elif conf["readme"].lower().endswith(".rst"):
            content_type = "text/x-rst"
        else:
            content_type = "text/plain"
        metadata.append(f"Description-Content-Type: {content_type}")

        metadata.append("")

        with Path(conf["readme"]).open() as f:
            metadata.append(f.read())

    with (dist_info / "METADATA").open("w") as f:
        f.write("\n".join(metadata))

    LOG.info("create dist-info / top level")
    with (dist_info / "top_level.txt").open("w") as f:
        f.write("")

    LOG.info("create dist-info / WHEEL")
    with (dist_info / "WHEEL").open("w") as f:
        f.write(
            "\n".join(
                [
                    "Wheel-Version: 1.0",
                    f"Generator: cmeel {__version__}",
                    "Root-Is-Purelib: false",
                    f"Tag: {tag}",
                    "",
                ],
            ),
        )

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

    if check_relocatable:
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
                        if any(
                            idx in indexes for idx in (i - 2, i - 1, i, i + 1, i + 2)
                        )
                    ]
                    raise NonRelocatableError(
                        f"{fc} references temporary paths:\n" + "\n".join(display),
                    )
    if fix_pkg_config and not editable:
        LOG.info("fix pkg-config files")
        for fc in install.glob("**/*.pc"):
            with fc.open() as f:
                pc_file = f.read()
            if str(install) in pc_file:
                rel = str(fc.parent.relative_to(install))
                fix = "/".join(["${pcfiledir}"] + [".." for _ in rel.split("/")])
                LOG.warning("fix pkg-config %s: replace %s by %s", fc, install, fix)
                with fc.open("w") as f:
                    f.write(pc_file.replace(str(install), fix))
    if editable:
        LOG.info("Add .pth in wheel")
        with (wheel_dir / f"{distribution}.pth").open("w") as f:
            f.write(str((install / SITELIB).absolute()))

    LOG.info("wheel pack")
    pack = check_output(
        [
            sys.executable,
            "-m",
            "wheel",
            "pack",
            "--build-number",
            str(build_number),
            "-d",
            wheel_directory,
            str(wheel_dir),
        ],
    ).decode()
    LOG.debug("wheel pack output: %s", pack)
    name = Path(re.search("Repacking wheel as (.*\\.whl)\\.\\.\\.", pack).group(1)).name
    LOG.debug("returning '%s'", name)

    LOG.info("done")
    return name
