"""PEP 517 & 660 entry points."""

import logging
import os

from .impl import build_impl
from .sdist import sdist_impl

LOG = logging.getLogger("cmeel")


def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
) -> str:
    """Build an editable wheel: main entry point for PEP 660."""
    LOG.info("cmeel build editable")
    os.environ["CMAKE_INSTALL_MODE"] = "ABS_SYMLINK"
    return build_impl(wheel_directory, editable=True)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None) -> str:
    """Build a binary wheel: main entry point for PEP 517."""
    LOG.info("cmeel build wheel")
    return build_impl(wheel_directory, editable=False)


def build_sdist(sdist_directory, config_settings=None) -> str:
    """Generate a gzipped distribution tarball."""
    return sdist_impl(sdist_directory)
