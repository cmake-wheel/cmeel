"""Generate .tar.gz source distribution."""

import logging
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

from .metadata import Metadata

LOG = logging.getLogger("cmeel.sdist")


def sdist_impl(sdist_directory) -> str:
    """Implement the build_sdist entry point."""
    try:
        import git_archive_all
    except ImportError as e:
        err = "You need the 'build' extra option to use this build module.\n"
        err += "For this you can install the 'cmeel[build]' package."
        raise ImportError(err) from e

    metadata = Metadata()

    # tarfile can't add PKG-INFO to a .tar.gz, so we have to make a tmp one
    with TemporaryDirectory() as tmp:
        tmp_pkg = Path(tmp) / "PKG-INFO"
        tmp_tar = Path(tmp) / f"{metadata.dist}.tar.gz"
        def_tar = Path(sdist_directory) / f"{metadata.dist}.tar.gz"

        LOG.info("archive git repository and its submodules in {tmp}")
        git_archive_all.main(
            ["git_archive_all.py", str(tmp_tar)],
        )

        LOG.info("write PKG-INFO file")
        with tmp_pkg.open("w") as f:
            f.write(metadata.gen())

        LOG.info("create final archive with previous one + PKG-INFO")
        with tarfile.open(tmp_tar, "r") as tr, tarfile.open(def_tar, "w:gz") as tw:
            for member in tr.getmembers():
                fileobj = None
                if member.type not in [tarfile.LNKTYPE, tarfile.SYMTYPE]:
                    fileobj = tr.extractfile(member)
                tw.addfile(member, fileobj)
            tw.add(str(tmp_pkg), f"{metadata.dist}/PKG-INFO")

    return metadata.dist
