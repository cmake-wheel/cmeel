"""Metadata generation from pyproject conf.

ref. PEP 621, superseeded by
https://packaging.python.org/en/latest/specifications/declaring-project-metadata/
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

LICENSE_GLOBS = ["LICEN[CS]E*", "COPYING*", "NOTICE*", "AUTHORS*"]


def get_license(conf: Dict[str, Any], dist_info: Optional[Path]) -> List[str]:
    """Parse 'license' and 'license-files' keys."""
    metadata = []

    lic_expr, lic_files = _license(conf)

    if "license-files" in conf:
        lic_files = [*lic_files, *_license_files(conf["license-files"])]
    elif not lic_files:
        for glob_expr in LICENSE_GLOBS:
            for lic_file_s in Path().glob(glob_expr):
                lic_files.append(str(lic_file_s))

    if not lic_expr and not lic_files:
        e = "'license' or 'license-files' is required"
        raise KeyError(e)

    if lic_expr:
        metadata.append(f"License-Expression: {lic_expr}")
    if dist_info:
        for lic_file in lic_files:
            metadata.append(f"License-File: {lic_file}")
            path_src = Path(lic_file)
            path_dst = dist_info / "license" / path_src
            path_dst.parent.mkdir(parents=True, exist_ok=True)
            with path_src.open("r") as f_src, path_dst.open("w") as f_dst:
                f_dst.write(f_src.read())

    return metadata


def _license_files(license_files: Union[str, List[str], Dict[str, str]]) -> List[str]:
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
    else:
        e = "'license-files' accepts either a string, a list, or a table."
        raise TypeError(e)

    return lic_files


def _license(conf) -> Tuple[str, List[str]]:
    """Parse 'license' key."""
    lic_expr, lic_files = "", []
    if "license" in conf:
        if isinstance(conf["license"], str):
            lic_expr = conf["license"]
        elif isinstance(conf["license"], dict):
            warnings.warn(
                "'license' table is deprecated.\n"
                "Please use a 'license' string and/or the 'license-files' key.\n"
                f"The default setting globs {LICENSE_GLOBS}, as per PEP 639",
                DeprecationWarning,
                stacklevel=2,
            )
            if "text" in conf["license"] and "file" not in conf["license"]:
                lic_expr = conf["license"]["text"]
            elif "text" not in conf["license"] and "file" in conf["license"]:
                lic_files.append(conf["license"]["file"])
            else:
                e = "'license' table must containe either a 'file' or a 'text'"
                raise KeyError(e)
        else:
            e = "'license' accepts either a string or a table."
            raise TypeError(e)
    return lic_expr, lic_files


def get_people(conf: Dict[str, Any], key: str) -> List[str]:
    """Parse 'authors' and 'maintainers' keys."""
    metadata = []

    names, mails = [], []

    for person in conf.get(f"{key}s", []):
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


def get_urls(conf: Dict[str, Any]) -> List[str]:
    """Parse 'urls' keys."""
    metadata = []

    if "urls" in conf:
        for key, url in conf["urls"].items():
            if key == "homepage":
                metadata.append(f"Home-page: {url}")
            else:
                name = key.replace("-", " ").capitalize()
                metadata.append(f"Project-URL: {name}, {url}")

    return metadata


def get_deps(conf: Dict[str, Any], build_deps: List[str]) -> List[str]:
    """Parse 'dependencies' keys."""
    metadata = []

    dependencies = ["cmeel", *conf.get("dependencies", [])]
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

    for extra, deps in conf.get("optional-dependencies", []):
        if extra == "build":
            e = "the 'build' extra is reserved by cmeel."
            raise ValueError(e)
        metadata.append(f"Provides-Extra: {extra}")
        for dep in deps:
            metadata.append(f'Requires-Dist: {dep} ; extra == "{extra}"')

    return metadata


def get_readme(conf: Dict[str, Any]) -> List[str]:
    """Parse 'readme' key."""
    metadata = []

    readme_file, readme_content, readme_type = "", "", ""
    if "readme" not in conf:
        for ext in [".md", ".rst", ".txt", ""]:
            if Path(f"README{ext}").exists():
                conf["readme"] = f"README{ext}"
                break
    if "readme" in conf:
        if isinstance(conf["readme"], str):
            readme_file = conf["readme"]
            readme_type = _ext_type(conf["readme"])
        elif isinstance(conf["readme"], dict):
            readme_file, readme_content, readme_type = _readme_dict(conf)
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


def _readme_dict(conf: Dict[str, Any]) -> Tuple[str, str, str]:
    """Parse 'readme' key when it is a table."""
    readme_file, readme_content, readme_type = "", "", ""

    if "content-type" in conf["readme"]:
        readme_type = conf["readme"]["content-type"]
    else:
        e = "if 'readme' is a table, it must contain a 'content-type' key"
        raise KeyError(e)
    if "file" in conf["readme"] and "text" not in conf["readme"]:
        readme_file = conf["readme"]["file"]
    elif "file" not in conf["readme"] and "text" in conf["readme"]:
        readme_content = conf["readme"]["text"]
    else:
        e = "'readme' table accepts either a 'file' or a 'text' key"
        raise KeyError(e)

    return readme_file, readme_content, readme_type


def _ext_type(filename: str) -> str:
    """Guess a content type based on extension."""
    if filename.lower().endswith(".md"):
        return "text/markdown"
    if filename.lower().endswith(".rst"):
        return "text/x-rst"
    return "text/plain"


def get_keywords(conf: Dict[str, Any]) -> List[str]:
    """Parse 'keyword' key."""
    metadata = []
    if "keywords" in conf:
        keywords = ",".join(conf["keywords"])
        metadata.append(f"Keywords: {keywords}")
    return metadata


def metadata(conf, requires: List[str], dist_info: Optional[Path] = None) -> List[str]:
    """Return the lines which should go in the METADATA / PKG-INFO file."""
    return [
        "Metadata-Version: 2.1",
        f"Name: {conf['name']}",
        f"Version: {conf['version']}",
        f"Summary: {conf['description']}",
        f"Requires-Python: {conf.get('requires-python', '>=3.8')}",
        *get_license(conf, dist_info),
        *get_people(conf, "author"),
        *get_people(conf, "maintainer"),
        *get_keywords(conf),
        *get_urls(conf),
        *get_deps(conf, requires),
        *[f"Classifier: {classifier}" for classifier in conf.get("classifiers", [])],
        *get_readme(conf),
    ]
