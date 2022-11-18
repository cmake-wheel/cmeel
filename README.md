# CMake Wheel

[![PyPI version](https://badge.fury.io/py/cmeel.svg)](https://pypi.org/project/cmeel)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/cmake-wheel/cmeel/main.svg)](https://results.pre-commit.ci/latest/github/cmake-wheel/cmeel/main)
[![Documentation Status](https://readthedocs.org/projects/cmeel/badge/?version=latest)](https://cmeel.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Wheel build backend using CMake, to package anything with pip and distribute on PyPI.

Following those relevant PEPs:
- [PEP 427](https://peps.python.org/pep-0427/), The Wheel Binary Package Format 1.0
- [PEP 517](https://peps.python.org/pep-0517/), A build-system independent format for source trees
- [PEP 518](https://peps.python.org/pep-0518/), Specifying Minimum Build System Requirements for Python Projects
- [PEP 600](https://peps.python.org/pep-0600/), Future ‘manylinux’ Platform Tags for Portable Linux Built Distributions
- [PEP 621](https://peps.python.org/pep-0621/), Storing project metadata in pyproject.toml
- [PEP 639](https://peps.python.org/pep-0639/), Improving License Clarity with Better Package Metadata, **DRAFT**

## Chat

https://matrix.to/#/#cmake-wheel:matrix.org

## Basic idea

Glue between PEP 517 `build_wheel` function and modern CMake standard project configuration / build / test / install

This Install in `${PYTHON_SITELIB}/cmeel.prefix/`:
- As there is a dot, it is not a valid python module name, so no risk of importing anything there by mistake
- Play well with others, as everything is confined to `${PYTHON_SITELIB}/cmeel.prefix`
- `${PYTHON_SITELIB}/cmeel.pth` automatically load `${PYTHON_SITELIB}/cmeel.prefix/${PYTHON_SITELIB}`, so python
  packages work out of the box
- Existing `${PYTHON_SITELIB}/cmeel.prefix` are automatically added to `$CMAKE_PREFIX_PATH`, so we can build CMake
  packages whose dependencies are provided by other CMake packages installed with cmeel
- Stuff in `${PYTHON_SITELIB}/cmeel.prefix/bin` is exposed via `cmeel.run:cmeel_run`
