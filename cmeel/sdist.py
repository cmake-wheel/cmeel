"""Generate .tar.gz source distribution."""

import logging
from pathlib import Path

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

try:
    import git_archive_all
except ImportError as e:
    err = "You need the 'build' extra option to use this build module.\n"
    err += "For this you can install the 'cmeel[build]' package."
    raise ImportError(err) from e

from .utils import normalize

LOG = logging.getLogger("cmeel.sdist")


def sdist_impl(sdist_directory) -> str:
    """Implement the build_sdist entry point."""
    LOG.info("load conf from pyproject.toml")
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    conf = pyproject["project"]
    conf["name"] = normalize(conf["name"])
    distribution = f"{conf['name'].replace('-', '_')}-{conf['version']}"

    git_archive_all.main(
        ["git_archive_all.py", str(Path(sdist_directory) / f"{distribution}.tar.gz")],
    )
    return distribution
