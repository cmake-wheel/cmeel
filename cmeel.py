#!/usr/bin/env python
from pathlib import Path
from shutil import rmtree
from subprocess import check_call, check_output
import tomli

__version__ = "0.3.0"

DIR = Path("/tmp/cmeel")
BLD = DIR / "bld"
PFX = DIR / "pfx"
TAG = "from packaging.tags import sys_tags; print(next(sys_tags()))"
PYTHON = "python"

DEPS = []  # TODO


def _txt(txt: str, char: str = "·", width=88):
    print(f" {txt} ".center(width, char))


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _txt("CMake Wheels", "=")
    _txt("load conf")
    with open("pyproject.toml", "rb") as f:
        conf = tomli.load(f)["tool"]["poetry"]
    _txt("clean tmp dir")
    DIR.mkdir(exist_ok=True)
    rmtree(DIR)

    _txt("build wheel")
    # Configure
    distribution = conf["name"].replace("-", "_")
    _txt("configure", "~")
    check_call(
        f"cmake -S . -B {BLD}".split()
        + [
            "-DCMAKE_INSTALL_PREFIX="
            f"{PFX}/{distribution}-{conf['version']}.data/data",
            f"-DPYTHON_EXECUTABLE={PYTHON}",
            "-DCMAKE_CXX_COMPILER_LAUNCHER=sccache",
            "-DCMAKE_INSTALL_LIBDIR=../../cmeel.lib",
            "-DCMAKE_INSTALL_BINDIR=../../cmeel.bin",
            "-DPYTHON_SITELIB=../..",
        ]
    )
    _txt("build", "~")
    check_call(f"cmake --build {BLD}".split())
    _txt("test", "~")
    check_call(f"cmake --build {BLD} -t test".split())
    _txt("install", "~")
    check_call(f"cmake --build {BLD} -t install".split())
    _txt("dist-info")
    dist_info = PFX / f"{distribution}-{conf['version']}.dist-info"
    _txt("METADATA")
    dist_info.mkdir()
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
    _txt("top level")
    with (dist_info / "top_level.txt").open("w") as f:
        f.write("")
    _txt("wheel")
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
    _txt("pack")
    name = check_output(f"wheel pack -d {DIR} {PFX}".split()).decode()
    name = name.split("/")[-1][:-6]
    _txt("done")
    print(name)
    (DIR / name).rename(Path(wheel_directory) / name)
    return name
