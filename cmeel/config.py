"""Cmeel configuration.

Parse various configuration files and environment variables.
"""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Union

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from .consts import CMEEL_PREFIX, SITELIB


class CmeelConfig:
    """Cmeel config."""

    def __init__(self) -> None:
        """Get config variables from environment, local, and global config files."""
        config_home = Path("~/.config").expanduser()
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", config_home))
        config_path = config_home / "cmeel"
        config_file = config_path / "cmeel.toml"

        self.conf = {}
        if config_file.exists():
            with config_file.open("rb") as f:
                self.conf = tomllib.load(f)
        if self.conf.get("default-env", True):
            self.env = os.environ.copy()
        else:
            self.env = {p: os.environ[p] for p in ["PATH", "PYTHONPATH"]}
        self.jobs = int(self.conf.get("jobs", self.env.get("CMEEL_JOBS", "4")))
        self.test_jobs = self.conf.get(
            "test-jobs",
            self.env.get("CMEEL_TEST_JOBS", "4"),
        )
        self.temp_dir = Path(
            self.conf.get(
                "temp-dir",
                self.env.get(
                    "CMEEL_TEMP_DIR",
                    TemporaryDirectory(prefix="cmeel-").name,
                ),
            ),
        )
        self.log_level = self.conf.get(
            "log-level",
            self.env.get("CMEEL_LOG_LEVEL", "WARNING"),
        )

    def get_configure_args(
        self,
        conf: Dict[str, Any],
        install: Union[Path, str],
        configure_args: List[str],
        configure_env: Dict[str, str],
        run_tests: bool,
    ) -> List[str]:
        """Get CMake initial arguments."""
        project = conf["name"]
        build_testing: List[str] = [] if run_tests else ["-DBUILD_TESTING=OFF"]
        ret = [
            "-DBoost_NO_WARN_NEW_VERSIONS=ON",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_INSTALL_LIBDIR=lib",
            f"-DCMAKE_INSTALL_PREFIX={install}",
            f"-DPYTHON_SITELIB={SITELIB}",
            f"-DPython3_EXECUTABLE={sys.executable}",
            "-DCMAKE_APPLE_SILICON_PROCESSOR=arm64",
            f"-DCMEEL_JOBS={self.jobs}",
            *build_testing,
            *configure_args,
            *self.conf.get("configure-args", []),
        ]
        if project in self.conf:
            ret += self.conf[project].get("configure-args", [])
        if "CMEEL_CMAKE_ARGS" in configure_env and configure_env["CMEEL_CMAKE_ARGS"]:
            ret += configure_env["CMEEL_CMAKE_ARGS"].split()
        return ret

    def get_configure_env(self) -> Dict[str, str]:
        """Get CMake initial environment."""
        ret = self.env.copy()
        available = self._get_available_prefix()
        if available:
            cpp = ret.get("CMAKE_PREFIX_PATH", "")
            if str(available) not in cpp.split(":"):
                ret["CMAKE_PREFIX_PATH"] = f"{available}:{cpp}".strip(":")
            pcp = ret.get("PKG_CONFIG_PATH", "")
            lpcp = available / "lib" / "pkgconfig"
            if lpcp.is_dir() and str(lpcp) not in pcp.split(":"):
                pcp = f"{lpcp}:{pcp}"
            spcp = available / "share" / "pkgconfig"
            if spcp.is_dir() and str(spcp) not in pcp.split(":"):
                pcp = f"{spcp}:{pcp}"
            ret["PKG_CONFIG_PATH"] = pcp.strip(":")
        return ret

    def get_test_env(self) -> Dict[str, str]:
        """Get test environment."""
        ret = self.env.copy()
        ret.update(CTEST_OUTPUT_ON_FAILURE="1", CTEST_PARALLEL_LEVEL=self.test_jobs)
        return ret

    def _get_available_prefix(self) -> Optional[Path]:
        for path in sys.path:
            if CMEEL_PREFIX in path:
                return Path(path).parent.parent.parent
        return None


cmeel_config = CmeelConfig()
