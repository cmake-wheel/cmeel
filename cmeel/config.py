"""Cmeel config."""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Union, Optional

import tomli

from .consts import CMEEL_PREFIX, SITELIB


class CmeelConfig:
    """Cmeel config."""

    def __init__(self):
        """Get config variables from environment, local, and global config files."""
        config_home = os.path.expanduser("~/.config")
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", config_home))
        config_path = config_home / "cmeel"
        config_file = config_path / "cmeel.toml"

        self.conf = {}
        if config_file.exists():
            with config_file.open("rb") as f:
                self.conf = tomli.load(f)
        if self.conf.get("default-env", True):
            self.env = os.environ
        else:
            self.env = {p: os.environ[p] for p in ["PATH", "PYTHONPATH"]}
        self.jobs = int(self.conf.get("jobs", "4"))
        self.test_jobs = self.conf.get("test-jobs", "4")
        self.temp_dir = Path(
            self.env.get(
                "CMEEL_TEMP_DIR",
                self.conf.get("temp-dir", TemporaryDirectory(prefix="cmeel-").name),
            )
        )

    def get_configure_args(
        self,
        conf: Dict[str, Any],
        install: Union[Path, str],
        configure_args: Dict[str, Any],
    ) -> [str]:
        """Get CMake initial arguments."""
        project = conf["name"]
        ret = (
            [
                "-DBoost_NO_WARN_NEW_VERSIONS=ON",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DCMAKE_INSTALL_LIBDIR=lib",
                f"-DCMAKE_INSTALL_PREFIX={install}",
                f"-DPYTHON_SITELIB={SITELIB}",
                f"-DPython3_EXECUTABLE={sys.executable}",
            ]
            + configure_args
            + self.conf.get("configure-args", [])
        )
        if project in self.conf:
            ret += self.conf[project].get("configure-args", [])
        return ret

    def get_configure_env(self) -> {str: str}:
        """Get CMake initial environment."""
        ret = self.env.copy()
        available = self._get_available_prefix()
        if available:
            cpp = ret.get("CMAKE_PREFIX_PATH", "")
            if available not in cpp.split(":"):
                ret["CMAKE_PREFIX_PATH"] = f"{available}:{cpp}".strip(":")
        return ret

    def get_test_env(self) -> {str: str}:
        """Get test environment."""
        ret = self.env.copy()
        ret.update(CTEST_OUTPUT_ON_FAILURE="1", CTEST_PARALLEL_LEVEL=self.test_jobs)
        return ret

    def _get_available_prefix(self) -> Optional[str]:
        for path in sys.path:
            if CMEEL_PREFIX in path:
                return str(Path(path).parent.parent.parent)


cmeel_config = CmeelConfig()
