# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.61.0] - 2026-08-27

- :warning: enforce manylinux/musllinux on linux, following packaging 26.3
- add `-t` / `--test` flag to `cmeel docker`, allowing use of test.pypi.org

## [0.60.1] - 2026-05-11

- back to metadata version 2.4

## [0.60.0] - 2026-05-09

- :warning: Refactored python API. No change to cli or pip APIs.
- added `metadata` cli command
- added [PEP 794](https://peps.python.org/pep-0794/) support for `import-name`
- added argcomplete
- removed backport as we now have python 3.9
- mypy -> ty

## [0.59.0] - 2026-01-19

- expose `CMEEL_AVAILABLE_PREFIX` in configure env

## [0.58.0] - 2026-01-17

- Require python >= 3.9
- Test python 3.14
- update `musllinux_1_1` to `musllinux_1_2`
- main branch is now `cmeel`
- set both `-DPython_EXECUTABLE` and `-DPython3_EXECUTABLE`. Thanks CMake.
- `cmeel release` now accept to tag without creating a new commit first

## [0.57.3] - 2025-03-19

- Handle symlinks and hardlinks in sdist

## [0.57.2] - 2025-03-19

- Fix symlink issue in sdist
- Fix release

## [0.57.1] - 2025-02-05

- Install license file in `*.dist-info/license{ -> s}/`

## [0.57.0] - 2025-02-05

- bump metadata version to 2.4

## [0.56.0] - 2025-01-03

- define CMEEL_BUILD environment variable
- docker: default to python 3.13

## [0.55.0] - 2025-01-03

- set LD_LIBRARY_PATH=$(cmeel lib) for tests

## [0.54.2] - 2024-12-31

- release: fix permissions

## [0.54.1] - 2024-12-31

- release: dist files needs to be built

## [0.54.0] - 2024-12-31

- poetry -> uv + hatch
- drop safety
- isort + black -> ruff
- manylinux2014 -> manylinux_2_28

## [0.53.3] - 2023-12-15

- fix path computation following move of cmeel.pth to cmeel_pth

## [0.53.2] - 2023-12-12

- avoid any non-stdlib import in the .pth file

## [0.53.1] - 2023-12-11

- break import order issue

## [0.53.0] - 2023-11-30

- fix python shebang in scripts

## [0.52.1] - 2023-11-21

## [0.52.0] - 2023-11-21

- document `upstream-version`
- copy scripts with shebang in bin/

## [0.51.1] - 2023-11-07

## [0.51.0] - 2023-11-07

- set `PKG_PREFIX_PATH` on configure

## [0.50.2] - 2023-08-16

- ⚠️ rename `has-binaries` & `has-sitelib`

## [0.50.1] - 2023-08-16

- fix `has_binaries` & `has_sitelib` doc and defaults

## [0.50.0] - 2023-08-16

- update readthedocs config after python version bump
- ⚠️ `py3-none`, `any` and `pyver-any` are deprecated. Please use `has_binaries` and/or `has_sitelib`

## [0.49.0] - 2023-08-08

- Forward `-DCMEEL_JOBS={config.jobs}` to CMake

## [0.48.1] - 2023-08-04

## [0.48.0] - 2023-08-04

- Add sdist CI
- Add PKG-INFO in sdist
- Don't raise import errors until required
- Expose entrypoints in __init__.py

## [0.47.1] - 2023-08-04

## [0.47.0] - 2023-08-04

- Add `build_sdist` to get source distributions with `git-archive-all`
- Split `cmeel.build.build` into multiple utils functions
- Move `cmeel.build.build` to `cmeel.impl.build_impl`
- ⚠️  Update minimal python version to 3.8
- Add `version` subcommand for cmeel

## [0.46.0] - 2023-06-29

- Add undocumented `release` subcommand for cmeel

## [0.45.0] - 2023-05-30

- Add `cmeel` script as shortcut to `python -m cmeel`

## [0.44.1] - 2023-05-20

- revert "prepend cmeel stuff to `LD_LIBRARY_PATH` when running tests"

## [0.44.0] - 2023-05-20

- prepend cmeel stuff to `LD_LIBRARY_PATH` when running tests

## [0.43.1] - 2023-05-03

- `--cmeel-env` is now a default deactivable with `--no-cmeel-env`

## [0.43.0] - 2023-05-03

- add `--cmeel-env` option to `docker` subcommand to forward `CMEEL_*` environment variables
- improve docs

## [0.42.1] - 2023-05-03

- `[project]` section of `pyproject.toml`:
    - normalize `name`
    - accept `keywords` key
    - accept `optional-dependencies` key
    - fix `readme` str key
- switch to tomllib for python >= 3.11
- switch sphinx theme to furo for dark theme
- improve docs
- log current version

## [0.42.0] - 2023-05-01

- `[project]` section of `pyproject.toml`:
    - accept `readme` table with `content-type` and (`file` or `text`)
    - accept `license` table with `file` or `text` (this table is deprecated)
    - accept `license-files` as a string, list of strings, or table with `paths` or `globs`
    - default `license-files` globs to `["LICEN[CS]E*", "COPYING*", "NOTICE*", "AUTHORS*"]`
- rename `cmeel/{helpers -> env}.py`
- add `cmeel/metadata.py` to move pyproject parsing out of the way and help with C901

## [0.41.1] - 2023-04-27

- fix docker environment

## [0.41.0] - 2023-04-27

- docker: add environment

## [0.40.0] - 2023-04-26

- add `docker` subcommand
- add tests running helpers

## [0.39.0] - 2023-04-21

- allow building "py3-none-{platform}" wheels with `py3-none = true` in pyproject.toml

## [0.38.0] - 2023-04-18

- add `fix-pkg-config` option, default to `true`

## [0.37.0] - 2023-04-05

- autodetect `README{.md, .rst, .txt, }`
- `readme` is no longer required

## [0.36.0] - 2023-04-05

- forward build dependencies as "build" extra
- `project.urls` is no longer required
- tools: flake8, pydocstyle, pyupgrade → ruff

## [0.35.0] - 2023-03-07

- add `build_editable` following [PEP 660](https://peps.python.org/pep-0660/)
- update tooling, lints & ci, notably: isort, pydocstyle, mypy & safety

## [0.34.1] - 2023-03-06

- allow building "py3x-none-any" wheels with `pyver-any = true` in pyproject.toml

## [0.33.0] - 2023-03-06

- allow building "py3-none-any" wheels with `any = true` in pyproject.toml

## [0.32.3] - 2023-02-28

- stringfy paths in `check_output`s, to fix build on windows

## [0.32.2] - 2023-02-28

- parse wheel pack output with a regex
- fix some builds on windows
- fix ci on some mac OS

## [0.32.1] - 2023-02-27

- fix path separator on windows

## [0.32.0] - 2023-02-25

- don't require pip on DEBUG mode
- DEBUG: show wheel name

## [0.31.0] - 2023-02-04

- configure logging through `log-level` / `CMEEL_LOG_LEVEL`
- DEBUG level: show pip freeze, the commands, and their environment

## [0.30.0] - 2023-01-31

- on Apple Silicon, explicitely build for arm64

## [0.29.0] - 2023-01-30

- fix architecture for OSX arm64 systems in python 3.8

## [0.28.0] - 2023-01-24

- fix patch ignore validation

## [0.27.0] - 2023-01-24

- be more verbose on raising PatchError

## [0.26.0] - 2023-01-24

- add CHANGELOG url
- patch ignore lines which would delete a non-existent file

## [0.25.0] - 2023-01-24

- add tests for python 3.11
- improve error message on patch failure

## [0.24.2] - 2023-01-24

- fix missing file

## [0.24.1] - 2023-01-24

- load current prefix even if it doesn't exist yet

## [0.24.0] - 2023-01-23

- load cmeel prefixes in all sys.path

## [0.23.2] - 2022-12-30

## [0.23.1] - 2022-12-30

- fix use of tool.cmeel section

## [0.23.0] - 2022-12-10

- ⚠️ deprecate use of the "build-system" section of pyproject.toml for cmeel configuration
  in favor of the "tool.cmeel" section ⚠️

## [0.22.0] - 2022-11-18

- detect if `cmeel.patch` was already applied, and don't complain about it
- update README

## [0.21.0] - 2022-10-21

- consider `CMEEL_RUN_TESTS` environment variable
- add `-DBUILD_TESTING=OFF` when `run-tests` is off

## [0.20.0] - 2022-10-21

- process `configure_env` before `configure_args`
- consider `CMEEL_CMAKE_ARGS` environment variable
- use emoji in the CHANGELOG

## [0.19.0] - 2022-10-13

- consider `CMEEL_JOBS`, `CMEEL_TEST_JOBS` environment variables

## [0.18.0] - 2022-10-04

- Add environment variable manipulation helpers with `python -m cmeel`

## [0.17.1] - 2022-09-22

- fix classifiers

## [0.17.0] - 2022-09-22

- set default min python version to 3.7
- add authors/maintainers in matadata
- add classifiers in metadata

## [0.16.0] - 2022-09-22

- more documentation
- set project urls in metadata
- CI: upload artifacts
- use PEP 639 (draft) for SPDX License expressions
- add `test-jobs` global option
- add `check-relocatable` project option

## [0.15.0] - 2022-09-21

- documentation
- Decrease min python version to 3.7

## [0.14.0] - 2022-08-10

- set `CMAKE_INSTALL_LIBDIR` to `lib`

## [0.13.3] - 2022-08-10

- debug

## [0.13.2] - 2022-08-10

- fix TAG for macOS

## [0.13.1] - 2022-08-10

- fix TAG for macOS

## [0.13.0] - 2022-08-10

- support macOS arm64 crosscompilation for cibuildwheel

## [0.12.5] - 2022-07-30

- set env before configure

## [0.12.4] - 2022-07-30

- add INSTALL / SITLIB to PYTHONPATH for tests after install

## [0.12.3] - 2022-07-30

- implement sed

## [0.12.2] - 2022-07-30

## [0.12.1] - 2022-07-30

- `test-cmd`: replace `BUILD_DIR`

## [0.12.0] - 2022-07-30

- move `test-cmd` parameter to pyproject.toml

## [0.11.0] - 2022-07-30

- add `test-cmd` parameter

## [0.10.1] - 2022-07-30

- fix sed -i on OSX

## [0.10.0] - 2022-07-17

- check generated cmake files to ensure we don't have relocatablization issues
- add `build-number` parameter
- add `run-tests-after-install` parameter
- add `Numpy` to `-DPYTHON_COMPONENTS`
- add `temp-dir` / `CMEEL_TEMP_DIR` configuration (useful for caching builds, as default generate names)
- ⚠️  BREAKING: fix wheel name (it was using distribution, which replace `-` by `_`)
- ⚠️  BREAKING: rename `run_tests` into `run-tests`
- ⚠️  BREAKING: rename `default_env` into `default-env`
- ⚠️  BREAKING: rename `configure_args` into `configure-args`
- ⚠️  BREAKING: remove `PYTHON_COMPONENTS`

## [0.9.0] - 2022-05-31

- add executables

## [0.8.0] - 2022-05-28

- apply `cmeel.patch` if exists

## [0.7.0] - 2022-05-28

- move to `cmake-wheel` org
- misc fixes

## [0.6.2] - 2022-05-06

## [0.6.1] - 2022-05-06

- configurable `run_tests`

## [0.6.0] - 2022-05-06

- parse dependencies
- configurable source dir

## [0.5.2] - 2022-05-02

- fix pth when the current prefix is not the last

## [0.5.1] - 2022-05-02

- add metadata
- fix type hint for python < 3.10

## [0.5.0] - 2022-05-02

- split cmeel.py into cmeel/ package
- add cmeel/pth.py & cmeel.pth
- add config through `${XDG_CONFIG_HOME:-~/.config}/cmeel/cmeel.toml`
- cmake, wheel & packaging are now optionnal, roquired only for the build module

## [0.4.2] - 2022-04-20

- add README do project metadata

## [0.4.1] - 2022-04-20

## [0.4.0] - 2022-04-20

- switch to PEP 621 style

## [0.3.0] - 2022-04-18

- removed Backend main class.
- renamed cmw -> cmeel

## [0.2.0] - 2022-04-17

- setup tooling
- add changelog
- setup release process

## [0.1.0] - 2022-04-16

- Initial minial working example

[Unreleased]: https://github.com/cmake-wheel/cmeel/compare/v0.61.0...HEAD
[0.61.0]: https://github.com/cmake-wheel/cmeel/compare/v0.60.1...v0.61.0
[0.60.1]: https://github.com/cmake-wheel/cmeel/compare/v0.60.0...v0.60.1
[0.60.0]: https://github.com/cmake-wheel/cmeel/compare/v0.59.0...v0.60.0
[0.59.0]: https://github.com/cmake-wheel/cmeel/compare/v0.58.0...v0.59.0
[0.58.0]: https://github.com/cmake-wheel/cmeel/compare/v0.57.3...v0.58.0
[0.57.3]: https://github.com/cmake-wheel/cmeel/compare/v0.57.2...v0.57.3
[0.57.2]: https://github.com/cmake-wheel/cmeel/compare/v0.57.1...v0.57.2
[0.57.1]: https://github.com/cmake-wheel/cmeel/compare/v0.57.0...v0.57.1
[0.57.0]: https://github.com/cmake-wheel/cmeel/compare/v0.56.0...v0.57.0
[0.56.0]: https://github.com/cmake-wheel/cmeel/compare/v0.55.0...v0.56.0
[0.55.0]: https://github.com/cmake-wheel/cmeel/compare/v0.54.2...v0.55.0
[0.54.2]: https://github.com/cmake-wheel/cmeel/compare/v0.54.1...v0.54.2
[0.54.1]: https://github.com/cmake-wheel/cmeel/compare/v0.54.0...v0.54.1
[0.54.0]: https://github.com/cmake-wheel/cmeel/compare/v0.53.3...v0.54.0
[0.53.3]: https://github.com/cmake-wheel/cmeel/compare/v0.53.2...v0.53.3
[0.53.2]: https://github.com/cmake-wheel/cmeel/compare/v0.53.1...v0.53.2
[0.53.1]: https://github.com/cmake-wheel/cmeel/compare/v0.53.0...v0.53.1
[0.53.0]: https://github.com/cmake-wheel/cmeel/compare/v0.52.1...v0.53.0
[0.52.1]: https://github.com/cmake-wheel/cmeel/compare/v0.52.0...v0.52.1
[0.52.0]: https://github.com/cmake-wheel/cmeel/compare/v0.51.1...v0.52.0
[0.51.1]: https://github.com/cmake-wheel/cmeel/compare/v0.51.0...v0.51.1
[0.51.0]: https://github.com/cmake-wheel/cmeel/compare/v0.50.2...v0.51.0
[0.50.2]: https://github.com/cmake-wheel/cmeel/compare/v0.50.1...v0.50.2
[0.50.1]: https://github.com/cmake-wheel/cmeel/compare/v0.50.0...v0.50.1
[0.50.0]: https://github.com/cmake-wheel/cmeel/compare/v0.49.0...v0.50.0
[0.49.0]: https://github.com/cmake-wheel/cmeel/compare/v0.48.1...v0.49.0
[0.48.1]: https://github.com/cmake-wheel/cmeel/compare/v0.48.0...v0.48.1
[0.48.0]: https://github.com/cmake-wheel/cmeel/compare/v0.47.1...v0.48.0
[0.47.1]: https://github.com/cmake-wheel/cmeel/compare/v0.47.0...v0.47.1
[0.47.0]: https://github.com/cmake-wheel/cmeel/compare/v0.46.0...v0.47.0
[0.46.0]: https://github.com/cmake-wheel/cmeel/compare/v0.45.0...v0.46.0
[0.45.0]: https://github.com/cmake-wheel/cmeel/compare/v0.44.1...v0.45.0
[0.44.1]: https://github.com/cmake-wheel/cmeel/compare/v0.44.0...v0.44.1
[0.44.0]: https://github.com/cmake-wheel/cmeel/compare/v0.43.1...v0.44.0
[0.43.1]: https://github.com/cmake-wheel/cmeel/compare/v0.43.0...v0.43.1
[0.43.0]: https://github.com/cmake-wheel/cmeel/compare/v0.42.1...v0.43.0
[0.42.1]: https://github.com/cmake-wheel/cmeel/compare/v0.42.0...v0.42.1
[0.42.0]: https://github.com/cmake-wheel/cmeel/compare/v0.41.1...v0.42.0
[0.41.1]: https://github.com/cmake-wheel/cmeel/compare/v0.41.0...v0.41.1
[0.41.0]: https://github.com/cmake-wheel/cmeel/compare/v0.40.0...v0.41.0
[0.40.0]: https://github.com/cmake-wheel/cmeel/compare/v0.39.0...v0.40.0
[0.39.0]: https://github.com/cmake-wheel/cmeel/compare/v0.38.0...v0.39.0
[0.38.0]: https://github.com/cmake-wheel/cmeel/compare/v0.37.0...v0.38.0
[0.37.0]: https://github.com/cmake-wheel/cmeel/compare/v0.36.0...v0.37.0
[0.36.0]: https://github.com/cmake-wheel/cmeel/compare/v0.35.0...v0.36.0
[0.35.0]: https://github.com/cmake-wheel/cmeel/compare/v0.34.1...v0.35.0
[0.34.1]: https://github.com/cmake-wheel/cmeel/compare/v0.33.0...v0.34.1
[0.33.0]: https://github.com/cmake-wheel/cmeel/compare/v0.32.3...v0.33.0
[0.32.3]: https://github.com/cmake-wheel/cmeel/compare/v0.32.2...v0.32.3
[0.32.2]: https://github.com/cmake-wheel/cmeel/compare/v0.32.1...v0.32.2
[0.32.1]: https://github.com/cmake-wheel/cmeel/compare/v0.32.0...v0.32.1
[0.32.0]: https://github.com/cmake-wheel/cmeel/compare/v0.31.0...v0.32.0
[0.31.0]: https://github.com/cmake-wheel/cmeel/compare/v0.30.0...v0.31.0
[0.30.0]: https://github.com/cmake-wheel/cmeel/compare/v0.29.0...v0.30.0
[0.29.0]: https://github.com/cmake-wheel/cmeel/compare/v0.28.0...v0.29.0
[0.28.0]: https://github.com/cmake-wheel/cmeel/compare/v0.27.0...v0.28.0
[0.27.0]: https://github.com/cmake-wheel/cmeel/compare/v0.26.0...v0.27.0
[0.26.0]: https://github.com/cmake-wheel/cmeel/compare/v0.25.0...v0.26.0
[0.25.0]: https://github.com/cmake-wheel/cmeel/compare/v0.24.2...v0.25.0
[0.24.2]: https://github.com/cmake-wheel/cmeel/compare/v0.24.1...v0.24.2
[0.24.1]: https://github.com/cmake-wheel/cmeel/compare/v0.24.0...v0.24.1
[0.24.0]: https://github.com/cmake-wheel/cmeel/compare/v0.23.2...v0.24.0
[0.23.2]: https://github.com/cmake-wheel/cmeel/compare/v0.23.1...v0.23.2
[0.23.1]: https://github.com/cmake-wheel/cmeel/compare/v0.23.0...v0.23.1
[0.23.0]: https://github.com/cmake-wheel/cmeel/compare/v0.22.0...v0.23.0
[0.22.0]: https://github.com/cmake-wheel/cmeel/compare/v0.21.0...v0.22.0
[0.21.0]: https://github.com/cmake-wheel/cmeel/compare/v0.20.0...v0.21.0
[0.20.0]: https://github.com/cmake-wheel/cmeel/compare/v0.19.0...v0.20.0
[0.19.0]: https://github.com/cmake-wheel/cmeel/compare/v0.18.0...v0.19.0
[0.18.0]: https://github.com/cmake-wheel/cmeel/compare/v0.17.1...v0.18.0
[0.17.1]: https://github.com/cmake-wheel/cmeel/compare/v0.17.0...v0.17.1
[0.17.0]: https://github.com/cmake-wheel/cmeel/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/cmake-wheel/cmeel/compare/v0.15.0...v0.16.0
[0.15.0]: https://github.com/cmake-wheel/cmeel/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/cmake-wheel/cmeel/compare/v0.13.3...v0.14.0
[0.13.3]: https://github.com/cmake-wheel/cmeel/compare/v0.13.2...v0.13.3
[0.13.2]: https://github.com/cmake-wheel/cmeel/compare/v0.13.1...v0.13.2
[0.13.1]: https://github.com/cmake-wheel/cmeel/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/cmake-wheel/cmeel/compare/v0.12.5...v0.13.0
[0.12.5]: https://github.com/cmake-wheel/cmeel/compare/v0.12.4...v0.12.5
[0.12.4]: https://github.com/cmake-wheel/cmeel/compare/v0.12.3...v0.12.4
[0.12.3]: https://github.com/cmake-wheel/cmeel/compare/v0.12.2...v0.12.3
[0.12.2]: https://github.com/cmake-wheel/cmeel/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/cmake-wheel/cmeel/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/cmake-wheel/cmeel/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/cmake-wheel/cmeel/compare/v0.10.1...v0.11.0
[0.10.1]: https://github.com/cmake-wheel/cmeel/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/cmake-wheel/cmeel/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/cmake-wheel/cmeel/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/cmake-wheel/cmeel/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/cmake-wheel/cmeel/compare/v0.6.2...v0.7.0
[0.6.2]: https://github.com/cmake-wheel/cmeel/compare/v0.6.1...v0.6.2
[0.6.1]: https://github.com/cmake-wheel/cmeel/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/cmake-wheel/cmeel/compare/v0.5.2...v0.6.0
[0.5.2]: https://github.com/cmake-wheel/cmeel/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/cmake-wheel/cmeel/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/cmake-wheel/cmeel/compare/v0.4.3...v0.5.0
[0.4.2]: https://github.com/cmake-wheel/cmeel/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/cmake-wheel/cmeel/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/cmake-wheel/cmeel/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/cmake-wheel/cmeel/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/cmake-wheel/cmeel/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cmake-wheel/cmeel/releases/tag/v0.1.0
