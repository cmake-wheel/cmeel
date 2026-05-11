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

LOG = logging.getLogger("cmeel.metadata")
LICENSE_GLOBS = ["LICEN[CS]E*", "COPYING*", "NOTICE*", "AUTHORS*"]


def dotget(data, key, default):
    """Get key in data or default."""
    for part in key.split("."):
        if part in data:
            data = data[part]
        else:
            return default
    return data


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

        self.pyproject = pyproject
        self.conf = conf
        self.dist = f"{conf['name'].replace('-', '_')}-{conf['version']}"
        self.data = []
        self.lic_files = []

    def gen(self) -> str:
        """Generate full file content."""
        self.data = [
            "Metadata-Version: 2.4",  # TODO actually we are 2.5, but PyPI refuse that for now
            f"Name: {self.conf['name']}",
            f"Version: {self.conf['version']}",
            f"Summary: {self.conf['description']}",
            f"Requires-Python: {self.conf.get('requires-python', '>=3.9')}",
        ]

        self.gen_license()
        self.gen_people("author")
        self.gen_people("maintainer")
        self.gen_keywords()
        self.gen_urls()
        self.gen_deps()
        self.gen_classifiers()
        self.gen_import_name()
        self.gen_readme()

        return "\n".join(self.data)

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

    def gen_license(self):
        """Parse 'license' and 'license-files' keys."""
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
            self.data.append(f"License-Expression: {lic_expr}")
        for lic_file in lic_files:
            self.data.append(f"License-File: {lic_file}")

        self.lic_files = lic_files

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

    def gen_people(self, key: str):
        """Parse 'authors' and 'maintainers' keys."""
        names, mails = [], []

        for person in self.conf.get(f"{key}s", []):
            if "name" in person and "email" in person:
                mails.append(f"{person['name']} <{person['email']}>")
            elif "email" in person:
                mails.append(person["email"])
            elif "name" in person:
                names.append(person["name"])

        if names:
            self.data.append(f"{key.title()}: " + ",".join(names))
        if mails:
            self.data.append(f"{key.title()}-Email: " + ",".join(mails))

    def gen_urls(self):
        """Parse 'urls' keys."""
        if "urls" in self.conf:
            for key, url in self.conf["urls"].items():
                if key == "homepage":
                    self.data.append(f"Home-page: {url}")
                else:
                    name = key.replace("-", " ").capitalize()
                    self.data.append(f"Project-URL: {name}, {url}")

    def gen_deps(self):
        """Parse 'dependencies' keys."""
        dependencies = ["cmeel", *self.conf.get("dependencies", [])]
        for dep in dependencies:
            self.data.append(f"Requires-Dist: {dep}")

        build_deps = self.pyproject["build-system"]["requires"]
        build_dependencies = [
            build_dep
            for build_dep in build_deps
            if build_dep != "cmeel[build]" and build_dep not in dependencies
        ]
        if build_dependencies:
            self.data.append("Provides-Extra: build")
            for build_dep in build_dependencies:
                self.data.append(f'Requires-Dist: {build_dep}; extra == "build"')

        for extra, deps in self.conf.get("optional-dependencies", {}).items():
            if extra == "build" and self.conf["name"] != "cmeel":
                e = "the 'build' extra is reserved by cmeel."
                raise ValueError(e)
            self.data.append(f"Provides-Extra: {extra}")
            for dep in deps:
                self.data.append(f'Requires-Dist: {dep}; extra == "{extra}"')

    def gen_readme(self):
        """Parse 'readme' key."""
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
            self.data.append(f"Description-Content-Type: {readme_type}")

            self.data.append("")

            if readme_content:
                self.data.append(readme_content)
            elif readme_file:
                with Path(readme_file).open() as f:
                    self.data.append(f.read())

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

    def gen_keywords(self):
        """Parse 'keyword' key."""
        if "keywords" in self.conf:
            keywords = ",".join(self.conf["keywords"])
            self.data.append(f"Keywords: {keywords}")

    def gen_classifiers(self):
        """Parse 'classifiers' key."""
        if "classifiers" in self.conf:
            self.data += [
                f"Classifier: {classifier}" for classifier in self.conf["classifiers"]
            ]

    def gen_import_name(self):
        """Parse PEP 794 'import-names' and 'import-namespaces' keys."""
        if "import-names" in self.conf:
            self.data += [f"Import-Name: {name}" for name in self.conf["import-names"]]
        if "import-namespaces" in self.conf:
            self.data += [
                f"Import-Namespace: {namespace}"
                for namespace in self.conf["import-namespaces"]
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


def add_metadata_arguments(subparsers):
    """Append metadata command for argparse."""
    sub = subparsers.add_parser(
        "metadata", help="generate metadata from pyproject.toml."
    )
    sub.set_defaults(cmd="metadata")

    sub.add_argument("--dist", action="store_true", help="get distribution name")


def metadata_cmd(dist: bool = False, **kwargs) -> str:
    """Generate metadata from pyproject.toml."""
    metadata = Metadata()
    if dist:
        return metadata.dist
    return metadata.gen()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    metadata_cmd()
