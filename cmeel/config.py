import os
import sys
from pathlib import Path
from typing import Union
import distutils.sysconfig

import tomli

from .consts import SITELIB


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

    def get_configure_args(self, project: str, install: Union[Path, str]) -> [str]:
        ret = [
            f"-DCMAKE_INSTALL_PREFIX={install}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            # f"-DPython_EXECUTABLE={sys.executable}",
            # f"-DPython3_EXECUTABLE={sys.executable}",
            # f"-DPython3_ROOT_DIR={sys.exec_prefix}",
            f"-DPython3_INCLUDE_DIR={distutils.sysconfig.get_python_inc()}",
            # f"-DPython3_LIBRARIES=libpython3.so",
            f"-DPYTHON_SITELIB={SITELIB}",
            # f"-DPYTHON_EXT_SUFFIX={sysconfg.get_config_var('EXT_SUFFIX')}",
            # "-DFINDPYTHON_ALREADY_CALLED=TRUE",
        ] + self.conf.get("configure_args", [])
        if project in self.conf:
            ret += self.conf[project].get("configure_args", [])
        return ret

    def get_configure_env(self, project: str) -> {str: str}:
        return self.env.copy()

    def get_test_env(self, project: str) -> {str: str}:
        ret = self.env.copy()
        ret.update(CTEST_OUTPUT_ON_FAILURE="1", CTEST_PARALLEL_LEVEL="4")
        return ret


cmeel_config = CmeelConfig()
