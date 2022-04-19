#!/usr/bin/env python
from pathlib import Path
from shutil import rmtree
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory
import logging

import tomli

__version__ = "0.3.0"

DIR = TemporaryDirectory()
BLD = DIR / "bld"
PFX = DIR / "pfx"
TAG = "from packaging.tags import sys_tags; print(next(sys_tags()))"
PYTHON = "python"

DEPS = []  # TODO


def get_requires_for_build_wheel(config_settings=None):
    return ["packaging"]


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    logging.info("CMake Wheel")
    logging.info("load conf from pyproject.toml")
    with open("pyproject.toml", "rb") as f:
        conf = tomli.load(f)["tool"]["poetry"]
    DIR.mkdir()

    logging.info("build wheel")
    # Configure
    distribution = conf["name"].replace("-", "_")
    logging.info("configure")
    check_call(
        f"cmake -S . -B {BLD}".split()
        + [
            "-DCMAKE_INSTALL_PREFIX="
            f"{PFX}/{distribution}-{conf['version']}.data/data",
            f"-DPYTHON_EXECUTABLE={PYTHON}",
            "-DCMAKE_CXX_COMPILER_LAUNCHER=sccache",
        ]
    )
    logging.info("build")
    check_call(f"cmake --build {BLD}".split())
    logging.info("test")
    check_call(f"cmake --build {BLD} -t test".split())
    logging.info("install")
    check_call(f"cmake --install {BLD}".split())

    logging.info("create dist-info")
    dist_info = PFX / f"{distribution}-{conf['version']}.dist-info"
    dist_info.mkdir()
    logging.info("create dist-info / METADATA")
    with open(conf["readme"]) as f:
        readme = f.read()
    requires = "\n".join([f"Requires-Dist: {dep}" for dep in DEPS])
    with (dist_info / "METADATA").open("w") as f:
        f.write(
            "\n".join(
                [
                    "Metadata-Version: 2.1",
                    f"Name: {distribution}",
                    f"Version: {conf['version']}",
                    f"Summary: {conf['description']}",
                    f"Home-page: {conf['homepage']}",
                    "Classifier: Programming Language :: Python :: 2",
                    "Classifier: Programming Language :: Python :: 3",
                    "Classifier: License :: OSI Approved :: BSD License",
                    "Classifier: Operating System :: POSIX :: Linux",
                    "Requires-Python: >= 2.7",
                    "Description-Content-Type: text/markdown",
                    f"{requires}",
                    "",
                    f"{readme}",
                ]
            )
        )
    logging.info("create dist-info / top level")
    with (dist_info / "top_level.txt").open("w") as f:
        f.write("")
    logging.info("create dist-info / WHEEL")
    tag = check_output(["python", "-c", TAG]).decode().strip()
    with (dist_info / "WHEEL").open("w") as f:
        f.write(
            "\n".join(
                [
                    "Wheel-Version: 1.0",
                    f"Generator: cmeel {__version__}",
                    "Root-Is-Purelib: false",
                    f"Tag: {tag}",
                ]
            )
        )

    logging.info("wheel pack")
    name = check_output(f"wheel pack -d {DIR} {PFX}".split()).decode()
    name = name.split("/")[-1][:-6]
    logging.info("move to {wheel_directory}")
    (DIR / name).rename(Path(wheel_directory) / name)
    logging.info("clean")
    rmtree(DIR)
    logging.info("done")
    return name
