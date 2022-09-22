"""Cmeel build."""
from pathlib import Path
from subprocess import check_call, check_output
import logging
import os
import sys

try:
    from packaging.tags import sys_tags
except ImportError as e:
    err = "You need the 'build' extra option to use this build module.\n"
    err += "For this you can install the 'cmeel[build]' package."
    raise ImportError(err) from e
import tomli

from .consts import CMEEL_PREFIX, SITELIB
from .config import cmeel_config
from . import __version__

EXECUTABLE = """#!python
from cmeel.run import cmeel_run
cmeel_run()
"""


class NonRelocatableError(Exception):
    """Exception raised when absolute paths are in the final package."""

    pass


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Main entry point for PEP 517."""
    logging.info("CMake Wheel")

    TEMP = cmeel_config.temp_dir
    BUILD = TEMP / "bld"
    PREFIX = TEMP / "pfx"
    INSTALL = PREFIX / CMEEL_PREFIX
    TAG = str(next(sys_tags()))
    # handle cross compilation on macOS with cibuildwheel
    # ref. https://github.com/pypa/cibuildwheel/blob/6549a9/cibuildwheel/macos.py#L221
    if "_PYTHON_HOST_PLATFORM" in os.environ:
        plat = os.environ["_PYTHON_HOST_PLATFORM"].replace("-", "_").replace(".", "_")
        TAG = "-".join(TAG.split("-")[:-1] + [plat])

    logging.info("load conf from pyproject.toml")
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
        CONF = pyproject["project"]
        SOURCE = pyproject["build-system"].get("source", ".")
        RUN_TESTS = pyproject["build-system"].get("run-tests", True)
        RUN_TESTS_AFTER_INSTALL = pyproject["build-system"].get(
            "run-tests-after-install", False
        )
        BUILD_NUMBER = pyproject["build-system"].get("build-number", 0)
        CONFIGURE_ARGS = pyproject["build-system"].get("configure-args", [])
        TEST_CMD = pyproject["build-system"].get(
            "test-cmd", ["cmake", "--build", "BUILD_DIR", "-t", "test"]
        )
        CHECK_RELOCATABLE = pyproject["build-system"].get("check-relocatable", True)
    DISTRIBUTION = CONF["name"].replace("-", "_")

    logging.info("build wheel")

    # Patch

    if Path("cmeel.patch").exists():
        logging.info("patching")
        check_call(["patch", "-p0", "-i", "cmeel.patch"])

    # Set env

    if RUN_TESTS_AFTER_INSTALL:
        path = f"{INSTALL / SITELIB}"
        old = os.environ.get("PYTHONPATH", "")
        if old:
            path += f"{os.pathsep}{old}"
        os.environ.update(PYTHONPATH=path)

    # Configure

    logging.info("configure")
    configure_args = cmeel_config.get_configure_args(CONF, INSTALL, CONFIGURE_ARGS)
    configure_env = cmeel_config.get_configure_env()
    check_call(["cmake", "-S", SOURCE, "-B", BUILD] + configure_args, env=configure_env)

    logging.info("build")
    check_call(["cmake", "--build", BUILD, f"-j{cmeel_config.jobs}"])

    def run_tests():
        logging.info("test")
        test_env = cmeel_config.get_test_env()
        test_cmd = [i.replace("BUILD_DIR", str(BUILD)) for i in TEST_CMD]
        check_call(test_cmd, env=test_env, shell=True)

    if RUN_TESTS and not RUN_TESTS_AFTER_INSTALL:
        run_tests()

    logging.info("install")
    check_call(["cmake", "--build", BUILD, "-t", "install"])

    if RUN_TESTS and RUN_TESTS_AFTER_INSTALL:
        run_tests()

    logging.info("fix relocatablization")
    # Replace absolute install path in generated .cmake files, if any.
    for f in INSTALL.rglob("*.cmake"):
        ff = INSTALL / f"{f.stem}.fix"
        with f.open("r") as fr, ff.open("w") as fw:
            fw.write(fr.read().replace(str(INSTALL), "${PACKAGE_PREFIX_DIR}"))
        f.unlink()
        ff.rename(f)

    logging.info("create dist-info")

    dist_info = PREFIX / f"{DISTRIBUTION}-{CONF['version']}.dist-info"
    dist_info.mkdir()

    logging.info("create dist-info / METADATA")

    metadata = [
        "Metadata-Version: 2.1",
        f"Name: {CONF['name']}",
        f"Version: {CONF['version']}",
        f"Summary: {CONF['description']}",
        f"License-Expression: {CONF['license']}",
        f"Requires-Python: {CONF.get('requires-python', '>=3.7')}",
    ]

    authors = []
    maintainers = []
    authors_email = []
    maintainers_email = []

    for author in CONF.get("authors", {}):
        if "name" in author and "email" in author:
            authors_email.append(f"{author['name']} <{author['email']}>")
        elif "email" in author:
            authors_email.append(author["email"])
        elif "name" in author:
            authors.append(author["name"])

    for maintainer in CONF.get("maintainers", {}):
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

    for key, url in CONF["urls"].items():
        if key == "homepage":
            metadata.append(f"Home-page: {url}")
        else:
            name = key.replace("-", " ").capitalize()
            metadata.append(f"Project-URL: {name}, {url}")

    for dep in ["cmeel"] + CONF.get("dependencies", []):
        metadata.append(f"Requires-Dist: {dep}")

    for classifier in CONF.get("classifiers", []):
        metadata.append(f"Classifier: {classifier}")

    if CONF["readme"].lower().endswith(".md"):
        content_type = "text/markdown"
    elif CONF["readme"].lower().endswith(".rst"):
        content_type = "text/x-rst"
    else:
        content_type = "text/plain"
    metadata.append(f"Description-Content-Type: {content_type}")

    metadata.append("")

    with open(CONF["readme"]) as f:
        metadata.append(f.read())

    with (dist_info / "METADATA").open("w") as f:
        f.write("\n".join(metadata))

    logging.info("create dist-info / top level")
    with (dist_info / "top_level.txt").open("w") as f:
        f.write("")

    logging.info("create dist-info / WHEEL")
    with (dist_info / "WHEEL").open("w") as f:
        f.write(
            "\n".join(
                [
                    "Wheel-Version: 1.0",
                    f"Generator: cmeel {__version__}",
                    "Root-Is-Purelib: false",
                    f"Tag: {TAG}",
                ]
            )
        )

    BIN = INSTALL / "bin"
    if BIN.is_dir():
        logging.info("adding executables")
        scripts = PREFIX / f"{DISTRIBUTION}-{CONF['version']}.data" / "scripts"
        scripts.mkdir(parents=True)
        for fn in BIN.glob("*"):
            executable = scripts / fn.name
            with executable.open("w") as fe:
                fe.write(EXECUTABLE)
            executable.chmod(0o755)

    if CHECK_RELOCATABLE:
        logging.info("check generated cmake files")
        WRONG_DIRS = [
            "/tmp/pip-build-env",
            "/tmp/pip-req-build",
            "/opt/_internal",
            str(TEMP),
        ]
        for fc in INSTALL.glob("**/*.cmake"):
            with fc.open() as f:
                cmake_file = f.read()
                if any(wrong_dir in cmake_file for wrong_dir in WRONG_DIRS):
                    lines = cmake_file.split("\n")
                    # Get indexes of of problematic lines
                    indexes = [
                        idx
                        for idx, line in enumerate(lines)
                        if any(wrong_dir in line for wrong_dir in WRONG_DIRS)
                    ]
                    # Get lines at those indexes and around them to display
                    display = [
                        f"{i}: {l}"
                        for i, l in enumerate(lines)
                        if any(
                            idx in indexes for idx in (i - 2, i - 1, i, i + 1, i + 2)
                        )
                    ]
                    raise NonRelocatableError(
                        f"{fc} references temporary paths:\n" + "\n".join(display)
                    )

    logging.info("wheel pack")
    name = check_output(
        [
            sys.executable,
            "-m",
            "wheel",
            "pack",
            "--build-number",
            str(BUILD_NUMBER),
            "-d",
            wheel_directory,
            PREFIX,
        ]
    ).decode()
    name = name.split("/")[-1][:-6]

    logging.info("done")
    return name
