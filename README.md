# CMake Wheel: cmeel

[![PyPI version](https://badge.fury.io/py/cmeel.svg)](https://pypi.org/project/cmeel)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/cmake-wheel/cmeel/main.svg)](https://results.pre-commit.ci/latest/github/cmake-wheel/cmeel/main)
[![Documentation Status](https://readthedocs.org/projects/cmeel/badge/?version=latest)](https://cmeel.readthedocs.io/en/latest/?badge=latest)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

Wheel build backend using CMake, to package anything with pip and distribute on PyPI.

Following those relevant PEPs:
- [PEP 427](https://peps.python.org/pep-0427/), The Wheel Binary Package Format 1.0
- [PEP 517](https://peps.python.org/pep-0517/), A build-system independent format for source trees
- [PEP 518](https://peps.python.org/pep-0518/), Specifying Minimum Build System Requirements for Python Projects
- [PEP 600](https://peps.python.org/pep-0600/), Future ‘manylinux’ Platform Tags for Portable Linux Built Distributions
- [PEP 621](https://peps.python.org/pep-0621/), Storing project metadata in pyproject.toml
- [PEP 639](https://peps.python.org/pep-0639/), Improving License Clarity with Better Package Metadata, **DRAFT**
- [PEP 660](https://peps.python.org/pep-0660/), Editable installs for pyproject.toml based builds (wheel based)

## Chat

https://matrix.to/#/#cmake-wheel:matrix.org

## Basic idea

Glue between PEP 517 & 660 entry points and modern CMake standard project configuration / build / test / install

This Install in `${PYTHON_SITELIB}/cmeel.prefix/`:
- As there is a dot, it is not a valid python module name, so no risk of importing anything there by mistake
- Play well with others, as everything is confined to `${PYTHON_SITELIB}/cmeel.prefix`
- `${PYTHON_SITELIB}/cmeel.pth` automatically load `${PYTHON_SITELIB}/cmeel.prefix/${PYTHON_SITELIB}`, so python
  packages work out of the box
- Existing `${PYTHON_SITELIB}/cmeel.prefix` are automatically added to `$CMAKE_PREFIX_PATH`, so we can build CMake
  packages whose dependencies are provided by other packages installed with cmeel
- Stuff in `${PYTHON_SITELIB}/cmeel.prefix/bin` is exposed via `cmeel.run:cmeel_run`, or copied if start with a shebang

## Basic pyproject.toml example

extract from  https://github.com/cmake-wheel/cmeel-example/blob/main/pyproject.toml:

```toml
[project]
name = "cmeel-example"
version = "0.4.12"
description = "This is an example project, to show how to use cmeel"
requires-python = ">= 3.7"
license = "BSD-2-Clause"
authors = [{name = "Guilhem Saurel", email = "guilhem.saurel@laas.fr"}]

[project.urls]
homepage = "https://github.com/cmake-wheel/cmeel-example"
repository = "https://github.com/cmake-wheel/cmeel-example.git"
changelog = "https://github.com/cmake-wheel/cmeel-example/blob/main/CHANGELOG.md"

[build-system]
requires = ["cmeel[build]"]
build-backend = "cmeel"
```

Complete specification is available at:
https://packaging.python.org/en/latest/specifications/declaring-project-metadata

## Install

If you want to use the helpers provided by cmeel, to *eg*. test building a project in a manylinux container with
`cmeel docker`, the best way to install cmeel is to use pipx: `pipx install cmeel`

Otherwise, if you just want to use the build backend, there is no need to install anything: your frontent (*eg.* `pip`)
should do this for you
