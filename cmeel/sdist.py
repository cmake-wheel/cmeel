"""Generate .tar.gz source distribution."""

import logging
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from .metadata import metadata
from .utils import normalize

LOG = logging.getLogger("cmeel.sdist")


def sdist_impl(sdist_directory) -> str:
    """Implement the build_sdist entry point."""
    try:
        import git_archive_all
    except ImportError as e:
        err = "You need the 'build' extra option to use this build module.\n"
        err += "For this you can install the 'cmeel[build]' package."
        raise ImportError(err) from e

    LOG.info("load conf from pyproject.toml")
    with Path("pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    conf = pyproject["project"]
    conf["name"] = normalize(conf["name"])
    distribution = f"{conf['name'].replace('-', '_')}-{conf['version']}"

    # tarfile can't add PKG-INFO to a .tar.gz, so we have to make a tmp one
    with TemporaryDirectory() as tmp:
        tmp_pkg = Path(tmp) / "PKG-INFO"
        tmp_tar = Path(tmp) / f"{distribution}.tar.gz"
        def_tar = Path(sdist_directory) / f"{distribution}.tar.gz"

        LOG.info("archive git repository and its submodules in {tmp}")
        git_archive_all.main(
            ["git_archive_all.py", str(tmp_tar)],
        )

        LOG.info("write PKG-INFO file")
        requires = pyproject["build-system"]["requires"]
        with tmp_pkg.open("w") as f:
            f.write("\n".join(metadata(conf, requires)))

        LOG.info("create final archive with previous one + PKG-INFO")
        with tarfile.open(tmp_tar, "r") as tr, tarfile.open(def_tar, "w:gz") as tw:
            for member in tr.getmembers():
                tw.addfile(member, tr.extractfile(member.name))
            tw.add(str(tmp_pkg), f"{distribution}/PKG-INFO")

    return distribution
