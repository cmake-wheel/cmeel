"""Metadata generation from pyproject conf.

ref. PEP 621, superseeded by
https://packaging.python.org/en/latest/specifications/declaring-project-metadata/
"""

import logging
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Union

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from .consts import LICENSE_GLOBS
from .utils import dotget

LOG = logging.getLogger("cmeel.metadata")


class Metadata:
    """Metadata generation from pyproject.toml."""

    def __init__(self):
        """Metadata generation from pyproject.toml."""
        LOG.info("load conf from pyproject.toml")
        with Path("pyproject.toml").open("rb") as f:
            pyproject = tomllib.load(f)

        conf = pyproject["project"]
        # normalize name
        # ref. https://packaging.python.org/en/latest/specifications/name-normalization
        conf["name"] = re.sub(r"[-_.]+", "-", conf["name"]).lower()
        dist = f"{conf['name'].replace('-', '_')}-{conf['version']}"

        self.pyproject = pyproject
        self.conf = conf
        self.dist = dist

    def deprecate_build_system(self, key, default):
        """Cmeel up to v0.22 was using the "build-system" section of pyproject.toml.

        This function helps to deprecate that and move to "tool.cmeel".
        """
        if key in self.pyproject["build-system"]:
            default = self.pyproject["build-system"][key]
            warnings.warn(
                'Using the "build-system" section of pyproject.toml for cmeel '
                "configuration is deprecated since cmeel v0.23 and will be removed in v1.\n"
                f'Please move your "{key} = {default}" to the "tool.cmeel" section.',
                DeprecationWarning,
                stacklevel=2,
            )
        if "tool" in self.pyproject and "cmeel" in self.pyproject["tool"]:
            return self.pyproject["tool"]["cmeel"].get(key, default)
        return default

    def get_license(self) -> list[str]:
        """Parse 'license' and 'license-files' keys."""
        metadata = []

        lic_expr, lic_files = self._license()

        if "license-files" in self.conf:
            lic_files = [*lic_files, *self._license_files(self.conf["license-files"])]
        elif not lic_files:
            for glob_expr in LICENSE_GLOBS:
                for lic_file_s in Path().glob(glob_expr):
                    lic_files.append(str(lic_file_s))

        if not lic_expr and not lic_files:
            e = "'license' or 'license-files' is required"
            raise KeyError(e)

        if lic_expr:
            metadata.append(f"License-Expression: {lic_expr}")
        for lic_file in lic_files:
            metadata.append(f"License-File: {lic_file}")
            # path_src = Path(lic_file)
            # path_dst = dist_info / "licenses" / path_src
            # path_dst.parent.mkdir(parents=True, exist_ok=True)
            # with path_src.open("r") as f_src, path_dst.open("w") as f_dst:
            #     f_dst.write(f_src.read())

        return metadata

    def _license_files(
        self, license_files: Union[str, list[str], dict[str, str]]
    ) -> list[str]:
        """Parse 'license-files' key."""
        lic_files = []
        if isinstance(license_files, str):
            lic_files.append(license_files)
        elif isinstance(license_files, list):
            lic_files += license_files
        elif isinstance(license_files, dict):
            if "paths" in license_files and "globs" not in license_files:
                for lic_file in license_files["paths"]:
                    lic_files.append(lic_file)
            elif "paths" not in license_files and "globs" in license_files:
                for glob_expr in license_files["globs"]:
                    for lic_file_s in Path().glob(glob_expr):
                        lic_files.append(str(lic_file_s))
            else:
                e = "'license-files' table must containe either a 'paths' or a 'globs'"
                raise KeyError(e)

        return lic_files

    def _license(self) -> tuple[str, list[str]]:
        """Parse 'license' key."""
        lic_expr, lic_files = "", []
        if "license" in self.conf:
            if isinstance(self.conf["license"], str):
                lic_expr = self.conf["license"]
            elif isinstance(self.conf["license"], dict):
                warnings.warn(
                    "'license' table is deprecated.\n"
                    "Please use a 'license' string and/or the 'license-files' key.\n"
                    f"The default setting globs {LICENSE_GLOBS}, as per PEP 639",
                    DeprecationWarning,
                    stacklevel=2,
                )
                if (
                    "text" in self.conf["license"]
                    and "file" not in self.conf["license"]
                ):
                    lic_expr = self.conf["license"]["text"]
                elif (
                    "text" not in self.conf["license"]
                    and "file" in self.conf["license"]
                ):
                    lic_files.append(self.conf["license"]["file"])
                else:
                    e = "'license' table must containe either a 'file' or a 'text'"
                    raise KeyError(e)
            else:
                e = "'license' accepts either a string or a table."
                raise TypeError(e)
        return lic_expr, lic_files

    def get_people(self, key: str) -> list[str]:
        """Parse 'authors' and 'maintainers' keys."""
        metadata = []

        names, mails = [], []

        for person in self.conf.get(f"{key}s", []):
            if "name" in person and "email" in person:
                mails.append(f"{person['name']} <{person['email']}>")
            elif "email" in person:
                mails.append(person["email"])
            elif "name" in person:
                names.append(person["name"])

        if names:
            metadata.append(f"{key.title()}: " + ",".join(names))
        if mails:
            metadata.append(f"{key.title()}-email: " + ",".join(mails))

        return metadata

    def get_urls(self) -> list[str]:
        """Parse 'urls' keys."""
        metadata = []

        if "urls" in self.conf:
            for key, url in self.conf["urls"].items():
                if key == "homepage":
                    metadata.append(f"Home-page: {url}")
                else:
                    name = key.replace("-", " ").capitalize()
                    metadata.append(f"Project-URL: {name}, {url}")

        return metadata

    def get_deps(self) -> list[str]:
        """Parse 'dependencies' keys."""
        metadata = []

        build_deps = self.pyproject["build-system"]["requires"]
        dependencies = ["cmeel", *self.conf.get("dependencies", [])]
        for dep in dependencies:
            metadata.append(f"Requires-Dist: {dep}")

        build_dependencies = [
            build_dep
            for build_dep in build_deps
            if build_dep != "cmeel[build]" and build_dep not in dependencies
        ]
        if build_dependencies:
            metadata.append("Provides-Extra: build")
            for build_dep in build_dependencies:
                metadata.append(f'Requires-Dist: {build_dep} ; extra == "build"')

        for extra, deps in self.conf.get("optional-dependencies", []):
            if extra == "build":
                e = "the 'build' extra is reserved by cmeel."
                raise ValueError(e)
            metadata.append(f"Provides-Extra: {extra}")
            for dep in deps:
                metadata.append(f'Requires-Dist: {dep} ; extra == "{extra}"')

        return metadata

    def get_readme(self) -> list[str]:
        """Parse 'readme' key."""
        metadata = []

        readme_file, readme_content, readme_type = "", "", ""
        if "readme" not in self.conf:
            for ext in [".md", ".rst", ".txt", ""]:
                if Path(f"README{ext}").exists():
                    self.conf["readme"] = f"README{ext}"
                    break
        if "readme" in self.conf:
            if isinstance(self.conf["readme"], str):
                readme_file = self.conf["readme"]
                readme_type = self._ext_type(self.conf["readme"])
            elif isinstance(self.conf["readme"], dict):
                readme_file, readme_content, readme_type = self._readme_dict()
            else:
                e = "'readme' accepts either a string or a table."
                raise TypeError(e)
            metadata.append(f"Description-Content-Type: {readme_type}")

            metadata.append("")

            if readme_content:
                metadata.append(readme_content)
            elif readme_file:
                with Path(readme_file).open() as f:
                    metadata.append(f.read())

        return metadata

    def _readme_dict(self) -> tuple[str, str, str]:
        """Parse 'readme' key when it is a table."""
        readme_file, readme_content, readme_type = "", "", ""

        if "content-type" in self.conf["readme"]:
            readme_type = self.conf["readme"]["content-type"]
        else:
            e = "if 'readme' is a table, it must contain a 'content-type' key"
            raise KeyError(e)
        if "file" in self.conf["readme"] and "text" not in self.conf["readme"]:
            readme_file = self.conf["readme"]["file"]
        elif "file" not in self.conf["readme"] and "text" in self.conf["readme"]:
            readme_content = self.conf["readme"]["text"]
        else:
            e = "'readme' table accepts either a 'file' or a 'text' key"
            raise KeyError(e)

        return readme_file, readme_content, readme_type

    def _ext_type(self, filename: str) -> str:
        """Guess a content type based on extension."""
        if filename.lower().endswith(".md"):
            return "text/markdown"
        if filename.lower().endswith(".rst"):
            return "text/x-rst"
        return "text/plain"

    def get_keywords(self) -> list[str]:
        """Parse 'keyword' key."""
        metadata = []
        if "keywords" in self.conf:
            keywords = ",".join(self.conf["keywords"])
            metadata.append(f"Keywords: {keywords}")
        return metadata

    def generate(self) -> list[str]:
        """Return the lines which should go in the METADATA / PKG-INFO file."""
        return [
            "Metadata-Version: 2.4",
            f"Name: {self.conf['name']}",
            f"Version: {self.conf['version']}",
            f"Summary: {self.conf['description']}",
            f"Requires-Python: {self.conf.get('requires-python', '>=3.8')}",
            *self.get_license(),
            *self.get_people("author"),
            *self.get_people("maintainer"),
            *self.get_keywords(),
            *self.get_urls(),
            *self.get_deps(),
            *[
                f"Classifier: {classifier}"
                for classifier in self.conf.get("classifiers", [])
            ],
            *self.get_readme(),
        ]

    def get_tag(self) -> str:
        """Find the correct tag for the wheel."""
        try:
            from packaging.tags import sys_tags
        except ImportError as e:
            err = "You need the 'build' extra option to use this build module.\n"
            err += "For this you can install the 'cmeel[build]' package."
            raise ImportError(err) from e

        tag = str(next(sys_tags()))
        # handle cross compilation on macOS with cibuildwheel
        # ref. https://github.com/pypa/cibuildwheel/blob/6549a9/cibuildwheel/macos.py#L221
        if "_PYTHON_HOST_PLATFORM" in os.environ:
            plat = (
                os.environ["_PYTHON_HOST_PLATFORM"].replace("-", "_").replace(".", "_")
            )
            tag = "-".join([*tag.split("-")[:-1], plat])

        if self.deprecate_build_system("py3-none", False):
            warnings.warn(
                "The 'py3-none = true' key is deprecated. Please use 'has-sitelib = false'",
                DeprecationWarning,
                stacklevel=2,
            )
            tag = "-".join(["py3", "none", tag.split("-")[-1]])
        elif self.deprecate_build_system("any", False):
            warnings.warn(
                "The 'any = true' key is deprecated. "
                "Please use 'has-sitelib = false' and 'has-binaries = false'",
                DeprecationWarning,
                stacklevel=2,
            )
            tag = "py3-none-any"
        elif self.deprecate_build_system("pyver-any", False):
            warnings.warn(
                "The 'pyver-any = true' key is deprecated. "
                "Please use 'has-binaries = false'",
                DeprecationWarning,
                stacklevel=2,
            )
            tag = f"py3{sys.version_info.minor}-none-any"
        else:
            binaries = dotget(self.pyproject, "tool.cmeel.has-binaries", True)
            sitelib = dotget(self.pyproject, "tool.cmeel.has-sitelib", True)
            if not binaries and not sitelib:
                tag = "py3-none-any"
            elif not binaries:
                tag = f"py3{sys.version_info.minor}-none-any"
            elif not sitelib:
                tag = "-".join(["py3", "none", tag.split("-")[-1]])
        return tag
