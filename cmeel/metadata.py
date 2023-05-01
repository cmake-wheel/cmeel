"""Metadata generation from pyproject conf."""

import glob
import pathlib
import warnings

LICENSE_GLOBS = ["LICEN[CS]E*", "COPYING*", "NOTICE*", "AUTHORS*"]


def get_license(conf, dist_info):  # noqa: C901
    """Parse 'license' and 'license-files' keys."""
    metadata = []
    lic_expr, lic_files = "", []
    if "license" in conf:
        if isinstance(conf["license"], str):
            lic_expr = conf["license"]
        elif isinstance(conf["license"], dict):
            lic_expr, lic_files = get_license_dict(conf)
        else:
            e = "'license' accepts either a string or a table."
            raise TypeError(e)
    if "license-files" in conf:
        lic_files = [*lic_files, *get_license_files(conf["license-files"])]
    elif not lic_files:
        for glob_expr in LICENSE_GLOBS:
            for lic_file in glob.glob(glob_expr):
                lic_files.append(lic_file)

    if not lic_expr and not lic_files:
        e = "'license' or 'license-files' is required"
        raise KeyError(e)

    if lic_expr:
        metadata.append(f"License-Expression: {lic_expr}")
    for lic_file in lic_files:
        metadata.append(f"License-File: {lic_file}")
        path_src = pathlib.Path(lic_file)
        path_dst = dist_info / "license" / path_src
        path_dst.parent.mkdir(parents=True, exist_ok=True)
        with path_src.open("r") as f_src, path_dst.open("w") as f_dst:
            f_dst.write(f_src.read())

    return metadata


def get_license_files(license_files):
    """Parse 'license-files' key."""
    lic_files = []
    if isinstance(license_files, str):
        lic_files.append(license_files)
    elif isinstance(license_files, list):
        for lic_file in license_files:
            lic_files.append(lic_file)
    elif isinstance(license_files, dict):
        if "paths" in license_files and "globs" not in license_files:
            for lic_file in license_files["paths"]:
                lic_files.append(lic_file)
        elif "paths" not in license_files and "globs" in license_files:
            for glob_expr in license_files["globs"]:
                for lic_file in glob.glob(glob_expr):
                    lic_files.append(lic_file)
        else:
            e = "'license-files' table must containe either a 'paths' or a 'globs'"
            raise KeyError(e)
    else:
        e = "'license-files' accepts either a string, a list, or a table."
        raise TypeError(e)

    return lic_files


def get_license_dict(conf):
    """Parse 'license' key when it is a table."""
    lic_expr, lic_files = "", []

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

    return lic_expr, lic_files


def get_people(conf, key):
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


def get_urls(conf):
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


def get_deps(conf, build_deps):
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

    return metadata


def get_readme(conf):
    """Parse 'readme' key."""
    metadata = []

    readme_file, readme_content, readme_type = None, None, None
    if "readme" not in conf:
        for ext in [".md", ".rst", ".txt", ""]:
            if pathlib.Path(f"README{ext}").exists():
                conf["readme"] = f"README{ext}"
                break
    if "readme" in conf:
        if isinstance(conf["readme"], str):
            readme_file = conf["readme"]
            if readme_file.lower().endswith(".md"):
                readme_type = "text/markdown"
            elif readme_file.lower().endswith(".rst"):
                readme_type = "text/x-rst"
            else:
                readme_type = "text/plain"
        elif isinstance(conf["readme"], dict):
            metadata += get_readme_dict(conf)
        else:
            e = "'readme' accepts either a string or a table."
            raise TypeError(e)
        metadata.append(f"Description-Content-Type: {readme_type}")

        metadata.append("")

        if readme_content:
            metadata.append(readme_content)
        else:
            with pathlib.Path(readme_file).open() as f:
                metadata.append(f.read())

    return metadata


def get_readme_dict(conf):
    """Parse 'readme' key when it is a table."""
    metadata = []

    if "content-type" in conf["readme"]:
        conf["readme"]["content-type"]
    else:
        e = "if 'readme' is a table, it must contain a 'content-type' key"
        raise KeyError(e)
    if "file" in conf["readme"]:
        conf["readme"]["file"]
    elif "text" in conf["readme"]:
        conf["readme"]["text"]
    else:
        e = "if 'readme' is a table, it must contain a 'file' or a 'text' key"
        raise KeyError(e)

    return metadata
