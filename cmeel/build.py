from pathlib import Path
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory
import logging

try:
    from packaging.tags import sys_tags
except ImportError as e:
    err = "You need the 'build' extra option to use this build module.\n"
    err += "For this you can install the 'cmeel[build]' package."
    raise ImportError(err) from e
import tomli

from .consts import CMEEL_PREFIX
from .config import cmeel_config
from . import __version__


def get_deps():
    return ["cmeel"]  # TODO


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    logging.info("CMake Wheel")

    TEMP = Path(TemporaryDirectory(prefix="cmeel-").name)
    BUILD = TEMP / "bld"
    PREFIX = TEMP / "pfx"
    INSTALL = PREFIX / CMEEL_PREFIX
    TAG = str(next(sys_tags()))

    logging.info("load conf from pyproject.toml")
    with open("pyproject.toml", "rb") as f:
        CONF = tomli.load(f)["project"]
    DISTRIBUTION = CONF["name"].replace("-", "_")

    logging.info("build wheel")

    # Configure

    logging.info("configure")
    configure_args = cmeel_config.get_configure_args(CONF["name"], INSTALL)
    configure_env = cmeel_config.get_configure_env(CONF["name"])
    check_call(["cmake", "-S", ".", "-B", BUILD] + configure_args, env=configure_env)

    logging.info("build")
    check_call(["cmake", "--build", BUILD])

    logging.info("test")
    test_env = cmeel_config.get_test_env(CONF["name"])
    check_call(["cmake", "--build", BUILD, "-t", "test"], env=test_env)

    logging.info("install")
    check_call(["cmake", "--build", BUILD, "-t", "install"])

    logging.info("create dist-info")

    dist_info = PREFIX / f"{DISTRIBUTION}-{CONF['version']}.dist-info"
    dist_info.mkdir()

    logging.info("create dist-info / METADATA")
    with open(CONF["readme"]) as f:
        readme = f.read()
    requires = "\n".join([f"Requires-Dist: {dep}" for dep in get_deps()])
    with (dist_info / "METADATA").open("w") as f:
        if CONF["readme"].lower().endswith(".md"):
            content_type = "text/markdown"
        elif CONF["readme"].lower().endswith(".rst"):
            content_type = "text/x-rst"
        else:
            content_type = "text/plain"
        f.write(
            "\n".join(
                [
                    "Metadata-Version: 2.1",
                    f"Name: {DISTRIBUTION}",
                    f"Version: {CONF['version']}",
                    f"Summary: {CONF['description']}",
                    f"Home-page: {CONF['urls']['homepage']}",
                    "Classifier: Programming Language :: Python :: 3",
                    "Classifier: License :: OSI Approved :: BSD License",
                    "Classifier: Operating System :: POSIX :: Linux",
                    f"Requires-Python: {CONF['requires-python']}",
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

    if (INSTALL / "bin").is_dir():
        logging.info("adding entrypoint")
        # TODO

    logging.info("wheel pack")
    name = check_output(["wheel", "pack", "-d", wheel_directory, PREFIX]).decode()
    name = name.split("/")[-1][:-6]

    logging.info("done")
    return name
