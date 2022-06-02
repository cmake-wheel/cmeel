from pathlib import Path
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory
import logging
import sys

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

EXECUTABLE = """#!python
from cmeel.run import cmeel_run
cmeel_run()
"""


class NonRelocatableError(Exception):
    pass


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    logging.info("CMake Wheel")

    TEMP = Path(TemporaryDirectory(prefix="cmeel-").name)
    BUILD = TEMP / "bld"
    PREFIX = TEMP / "pfx"
    INSTALL = PREFIX / CMEEL_PREFIX
    TAG = str(next(sys_tags()))

    logging.info("load conf from pyproject.toml")
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
        CONF = pyproject["project"]
        SOURCE = pyproject["build-system"].get("source", ".")
        RUN_TESTS = pyproject["build-system"].get("run_tests", True)
    DISTRIBUTION = CONF["name"].replace("-", "_")

    logging.info("build wheel")

    # Patch

    if Path("cmeel.patch").exists():
        logging.info("patching")
        check_call(["patch", "-p0", "-i", "cmeel.patch"])

    # Configure

    logging.info("configure")
    configure_args = cmeel_config.get_configure_args(CONF, INSTALL)
    configure_env = cmeel_config.get_configure_env()
    check_call(["cmake", "-S", SOURCE, "-B", BUILD] + configure_args, env=configure_env)

    logging.info("build")
    check_call(["cmake", "--build", BUILD, f"-j{cmeel_config.jobs}"])

    if RUN_TESTS:
        logging.info("test")
        test_env = cmeel_config.get_test_env()
        check_call(["cmake", "--build", BUILD, "-t", "test"], env=test_env)

    logging.info("install")
    check_call(["cmake", "--build", BUILD, "-t", "install"])

    logging.info("fix relocatablization")
    for f in INSTALL.rglob("*.cmake"):
        check_call(["sed", "-i", f"s|{INSTALL}|${{PACKAGE_PREFIX_DIR}}|g", str(f)])

    logging.info("create dist-info")

    dist_info = PREFIX / f"{DISTRIBUTION}-{CONF['version']}.dist-info"
    dist_info.mkdir()

    logging.info("create dist-info / METADATA")
    with open(CONF["readme"]) as f:
        readme = f.read()
    dependencies = ["cmeel"] + CONF.get("dependencies", [])
    requires = "\n".join([f"Requires-Dist: {dep}" for dep in dependencies])
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
                    f"Requires-Python: {CONF.get('requires-python', '>=3.8')}",
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

    logging.info("check generated cmake files")
    for fc in INSTALL.glob("**/*.cmake"):
        with fc.open() as f:
            if "/tmp/pip-build-env" in f.read():
                raise NonRelocatableError(f"{fc} references '/tmp/pip-build-env'")

    logging.info("wheel pack")
    name = check_output(
        [sys.executable, "-m", "wheel", "pack", "-d", wheel_directory, PREFIX]
    ).decode()
    name = name.split("/")[-1][:-6]

    logging.info("done")
    return name
