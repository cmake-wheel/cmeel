import os
import sys
from pathlib import Path
from typing import Any, Dict, Union, Optional
import distutils.sysconfig

import tomli

from .consts import CMEEL_PREFIX, SITELIB


class CmeelConfig:
    def __init__(self, default_env: bool = True):
        config_home = os.path.expanduser("~/.config")
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", config_home))
        config_path = config_home / "cmeel"
        config_file = config_path / "cmeel.toml"

        self.conf = {}
        if config_file.exists():
            with config_file.open("rb") as f:
                self.conf = tomli.load(f)
        if self.conf.get("default_env", True):
            self.env = os.environ
        else:
            self.env = {p: os.environ[p] for p in ["PATH", "PYTHONPATH"]}
        self.jobs = int(self.conf.get("jobs", "4"))

    def get_configure_args(
        self, conf: Dict[str, Any], install: Union[Path, str]
    ) -> [str]:
        project = conf["name"]
        ret = (
            [
                "-DBoost_NO_WARN_NEW_VERSIONS=ON",
                "-DCMAKE_BUILD_TYPE=Release",
                f"-DCMAKE_INSTALL_PREFIX={install}",
                f"-DPYTHON_EXECUTABLE={sys.executable}",
                f"-DPython3_INCLUDE_DIR={distutils.sysconfig.get_python_inc()}",
                f"-DPYTHON_INCLUDE_DIRS={distutils.sysconfig.get_python_inc()}",
                f"-DPYTHON_SITELIB={SITELIB}",
            ]
            + conf.get("configure_args", [])
            + self.conf.get("configure_args", [])
        )
        if project in self.conf:
            ret += self.conf[project].get("configure_args", [])
        return ret

    def get_configure_env(self, conf: Dict[str, Any]) -> {str: str}:
        ret = self.env.copy()
        available = self._get_available_prefix()
        if available:
            cpp = ret.get("CMAKE_PREFIX_PATH", "")
            if available not in cpp.split(":"):
                ret["CMAKE_PREFIX_PATH"] = f"{available}:{cpp}"
        return ret

    def get_test_env(self, conf: Dict[str, Any]) -> {str: str}:
        ret = self.env.copy()
        ret.update(CTEST_OUTPUT_ON_FAILURE="1", CTEST_PARALLEL_LEVEL="4")
        return ret

    def _get_available_prefix(self) -> Optional[str]:
        for path in sys.path:
            if CMEEL_PREFIX in path:
                return str(Path(path).parent.parent.parent)


cmeel_config = CmeelConfig()
