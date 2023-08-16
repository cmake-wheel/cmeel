"""Implementation of the main build function."""

import logging
import os
import re
import sys
from pathlib import Path
from subprocess import check_call, check_output

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from .cmeel import __version__
from .config import cmeel_config
from .consts import CMEEL_PREFIX, SITELIB
from .metadata import metadata
from .utils import (
    deprecate_build_system,
    ensure_relocatable,
    expose_bin,
    get_tag,
    launch_tests,
    log_pip,
    normalize,
    patch,
)

LOG = logging.getLogger("cmeel.impl")


def build_impl(wheel_directory, editable=False) -> str:
    """Run CMake configure / build / test / install steps, and pack the wheel."""
    logging.basicConfig(level=cmeel_config.log_level.upper())
    LOG.info("CMake Wheel in editable mode" if editable else "CMake Wheel")
    LOG.info("cmeel version %s", __version__)
    log_pip()

    prefix = Path() / "build-editable" if editable else cmeel_config.temp_dir
    build = prefix / "bld"
    wheel_dir = prefix / "whl"
    install = (prefix if editable else wheel_dir) / CMEEL_PREFIX

    LOG.info("load conf from pyproject.toml")
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    conf = pyproject["project"]
    conf["name"] = normalize(conf["name"])
    distribution = f"{conf['name'].replace('-', '_')}-{conf['version']}"

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

    check_relocatable = deprecate_build_system(pyproject, "check-relocatable", True)
    fix_pkg_config = deprecate_build_system(pyproject, "fix-pkg-config", True)

    LOG.info("build wheel")

    # Patch

    patch()

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

    launch_tests(True, run_tests and not run_tests_after_install, pyproject, build)

    LOG.info("install")
    install_cmd = ["cmake", "--build", str(build), "-t", "install"]
    LOG.debug("install command: %s", install_cmd)
    check_call(install_cmd)

    launch_tests(False, run_tests and run_tests_after_install, pyproject, build)

    LOG.info("fix relocatablization")
    # Replace absolute install path in generated .cmake files, if any.
    for cmake_file in install.rglob("*.cmake"):
        ff = install / f"{cmake_file.stem}.fix"
        with cmake_file.open("r") as fr, ff.open("w") as fw:
            fw.write(fr.read().replace(str(install), "${PACKAGE_PREFIX_DIR}"))
        cmake_file.unlink()
        ff.rename(cmake_file)

    LOG.info("create dist-info")

    dist_info = wheel_dir / f"{distribution}.dist-info"
    dist_info.mkdir(parents=True)

    LOG.info("create dist-info / METADATA")

    with (dist_info / "METADATA").open("w") as f:
        requires = pyproject["build-system"]["requires"]
        f.write("\n".join(metadata(conf, requires, dist_info)))

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
                    f"Tag: {get_tag(pyproject)}",
                    "",
                ],
            ),
        )

    expose_bin(install, wheel_dir, distribution)

    ensure_relocatable(check_relocatable, install, prefix)

    if editable:
        LOG.info("Add .pth in wheel")
        with (wheel_dir / f"{distribution}.pth").open("w") as f:
            f.write(str((install / SITELIB).absolute()))
    elif fix_pkg_config:
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
    parse_pack = re.search("Repacking wheel as (.*\\.whl)\\.\\.\\.", pack)
    if parse_pack is None:
        err = (
            "'wheel pack' command did not provide the .whl name, "
            "or the parser must be updated. Please report the following output: \n"
        )
        raise FileNotFoundError(err + pack)
    name = Path(parse_pack.group(1)).name
    LOG.debug("returning '%s'", name)

    LOG.info("done")
    return name
