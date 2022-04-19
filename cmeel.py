#!/usr/bin/env python

from pathlib import Path
from shutil import move
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory
import logging
import sys
import os

from packaging.tags import sys_tags
import tomli

__version__ = "0.4.2"

TEMP = Path(TemporaryDirectory(prefix="cmeel-").name)
BUILD = TEMP / "bld"
PREFIX = TEMP / "pfx"

TAG = str(next(sys_tags()))
SITE = os.sep.join(
    ["lib", "python" + ".".join(sys.version.split(".")[:2]), "site-packages"]
)

DEPS = []  # TODO


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    logging.info("CMake Wheel")
    logging.info("load conf from pyproject.toml")
    with open("pyproject.toml", "rb") as f:
        conf = tomli.load(f)["project"]

    logging.info("build wheel")
    # Configure
    distribution = conf["name"].replace("-", "_")
    logging.info("configure")
    install = PREFIX / f"{distribution}-{conf['version']}.data" / "data"
    check_call(["cmake", "-S", ".", "-B", BUILD, f"-DCMAKE_INSTALL_PREFIX={install}"])

    logging.info("build")
    check_call(["cmake", "--build", BUILD])
    logging.info("test")
    check_call(["cmake", "--build", BUILD, "-t", "test"])
    logging.info("install")
    check_call(["cmake", "--build", BUILD, "-t", "install"])

    logging.info("create dist-info")
    dist_info = PREFIX / f"{distribution}-{conf['version']}.dist-info"
    dist_info.mkdir()
    logging.info("create dist-info / METADATA")
    with open(conf["readme"]) as f:
        readme = f.read()
    requires = "\n".join([f"Requires-Dist: {dep}" for dep in DEPS])
    with (dist_info / "METADATA").open("w") as f:
        if conf["readme"].lower().endswith(".md"):
            content_type = "text/markdown"
        elif conf["readme"].lower().endswith(".rst"):
            content_type = "text/x-rst"
        else:
            content_type = "text/plain"
        f.write(
            "\n".join(
                [
                    "Metadata-Version: 2.1",
                    f"Name: {distribution}",
                    f"Version: {conf['version']}",
                    f"Summary: {conf['description']}",
                    f"Home-page: {conf['urls']['homepage']}",
                    "Classifier: Programming Language :: Python :: 3",
                    "Classifier: License :: OSI Approved :: BSD License",
                    "Classifier: Operating System :: POSIX :: Linux",
                    f"Requires-Python: {conf['requires-python']}",
                    f"Description-Content-Type: {content_type}",
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

    logging.info("move module")
    for module in (install / SITE).glob("*"):
        move(module, PREFIX)

    logging.info("wheel pack")
    name = check_output(["wheel", "pack", "-d", wheel_directory, PREFIX]).decode()
    name = name.split("/")[-1][:-6]
    logging.info("done")
    return name
