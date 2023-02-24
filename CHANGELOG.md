# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- don't require pip on DEBUG mode
- DEBUG: show wheel name

## [v0.31.0] - 2023-02-04

- configure logging through `log-level` / `CMEEL_LOG_LEVEL`
- DEBUG level: show pip freeze, the commands, and their environment

## [v0.30.0] - 2023-01-31

- on Apple Silicon, explicitely build for arm64

## [v0.29.0] - 2023-01-30

- fix architecture for OSX arm64 systems in python 3.8

## [v0.28.0] - 2023-01-24

- fix patch ignore validation

## [v0.27.0] - 2023-01-24

- be more verbose on raising PatchError

## [v0.26.0] - 2023-01-24

- add CHANGELOG url
- patch ignore lines which would delete a non-existent file

## [v0.25.0] - 2023-01-24

- add tests for python 3.11
- improve error message on patch failure

## [v0.24.2] - 2023-01-24

- fix missing file

## [v0.24.1] - 2023-01-24

- load current prefix even if it doesn't exist yet

## [v0.24.0] - 2023-01-23

- load cmeel prefixes in all sys.path

## [v0.23.2] - 2022-12-30

## [v0.23.1] - 2022-12-30

- fix use of tool.cmeel section

## [v0.23.0] - 2022-12-10

- ⚠️ deprecate use of the "build-system" section of pyproject.toml for cmeel configuration
  in favor of the "tool.cmeel" section ⚠️

## [v0.22.0] - 2022-11-18

- detect if `cmeel.patch` was already applied, and don't complain about it
- update README

## [v0.21.0] - 2022-10-21

- consider `CMEEL_RUN_TESTS` environment variable
- add `-DBUILD_TESTING=OFF` when `run-tests` is off

## [v0.20.0] - 2022-10-21

- process `configure_env` before `configure_args`
- consider `CMEEL_CMAKE_ARGS` environment variable
- use emoji in the CHANGELOG

## [v0.19.0] - 2022-10-13

- consider `CMEEL_JOBS`, `CMEEL_TEST_JOBS` environment variables

## [v0.18.0] - 2022-10-04

- Add environment variable manipulation helpers with `python -m cmeel`

## [v0.17.1] - 2022-09-22

- fix classifiers

## [v0.17.0] - 2022-09-22

- set default min python version to 3.7
- add authors/maintainers in matadata
- add classifiers in metadata

## [v0.16.0] - 2022-09-22

- more documentation
- set project urls in metadata
- CI: upload artifacts
- use PEP 639 (draft) for SPDX License expressions
- add `test-jobs` global option
- add `check-relocatable` project option

## [v0.15.0] - 2022-09-21

- documentation
- Decrease min python version to 3.7

## [v0.14.0] - 2022-08-10

- set `CMAKE_INSTALL_LIBDIR` to `lib`

## [v0.13.3] - 2022-08-10

- debug

## [v0.13.2] - 2022-08-10

- fix TAG for macOS

## [v0.13.1] - 2022-08-10

- fix TAG for macOS

## [v0.13.0] - 2022-08-10

- support macOS arm64 crosscompilation for cibuildwheel

## [v0.12.5] - 2022-07-30

- set env before configure

## [v0.12.4] - 2022-07-30

- add INSTALL / SITLIB to PYTHONPATH for tests after install

## [v0.12.3] - 2022-07-30

- implement sed

## [v0.12.2] - 2022-07-30

## [v0.12.1] - 2022-07-30

- `test-cmd`: replace `BUILD_DIR`

## [v0.12.0] - 2022-07-30

- move `test-cmd` parameter to pyproject.toml

## [v0.11.0] - 2022-07-30

- add `test-cmd` parameter

## [v0.10.1] - 2022-07-30

- fix sed -i on OSX

## [v0.10.0] - 2022-07-17

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

## [v0.9.0] - 2022-05-31

- add executables

## [v0.8.0] - 2022-05-28

- apply `cmeel.patch` if exists

## [v0.7.0] - 2022-05-28

- move to `cmake-wheel` org
- misc fixes

## [v0.6.2] - 2022-05-06

## [v0.6.1] - 2022-05-06

- configurable `run_tests`

## [v0.6.0] - 2022-05-06

- parse dependencies
- configurable source dir

## [v0.5.2] - 2022-05-02

- fix pth when the current prefix is not the last

## [v0.5.1] - 2022-05-02

- add metadata
- fix type hint for python < 3.10

## [v0.5.0] - 2022-05-02

- split cmeel.py into cmeel/ package
- add cmeel/pth.py & cmeel.pth
- add config through `${XDG_CONFIG_HOME:-~/.config}/cmeel/cmeel.toml`
- cmake, wheel & packaging are now optionnal, roquired only for the build module

## [v0.4.2] - 2022-04-20

- add README do project metadata

## [v0.4.1] - 2022-04-20

## [v0.4.0] - 2022-04-20

- switch to PEP 621 style

## [v0.3.0] - 2022-04-18

- removed Backend main class.
- renamed cmw -> cmeel

## [v0.2.0] - 2022-04-17

- setup tooling
- add changelog
- setup release process

## [v0.1.0] - 2022-04-16

- Initial minial working example

[Unreleased]: https://github.com/cmake-wheel/cmeel/compare/v0.4.2...main
[v0.31.0]: https://github.com/cmake-wheel/cmeel/compare/v0.30.0...v0.31.0
[v0.30.0]: https://github.com/cmake-wheel/cmeel/compare/v0.29.0...v0.30.0
[v0.29.0]: https://github.com/cmake-wheel/cmeel/compare/v0.28.0...v0.29.0
[v0.28.0]: https://github.com/cmake-wheel/cmeel/compare/v0.27.0...v0.28.0
[v0.27.0]: https://github.com/cmake-wheel/cmeel/compare/v0.26.0...v0.27.0
[v0.26.0]: https://github.com/cmake-wheel/cmeel/compare/v0.25.0...v0.26.0
[v0.25.0]: https://github.com/cmake-wheel/cmeel/compare/v0.24.2...v0.25.0
[v0.24.2]: https://github.com/cmake-wheel/cmeel/compare/v0.24.1...v0.24.2
[v0.24.1]: https://github.com/cmake-wheel/cmeel/compare/v0.24.0...v0.24.1
[v0.24.0]: https://github.com/cmake-wheel/cmeel/compare/v0.23.2...v0.24.0
[v0.23.2]: https://github.com/cmake-wheel/cmeel/compare/v0.23.1...v0.23.2
[v0.23.1]: https://github.com/cmake-wheel/cmeel/compare/v0.23.0...v0.23.1
[v0.23.0]: https://github.com/cmake-wheel/cmeel/compare/v0.22.0...v0.23.0
[v0.22.0]: https://github.com/cmake-wheel/cmeel/compare/v0.21.0...v0.22.0
[v0.21.0]: https://github.com/cmake-wheel/cmeel/compare/v0.20.0...v0.21.0
[v0.20.0]: https://github.com/cmake-wheel/cmeel/compare/v0.19.0...v0.20.0
[v0.19.0]: https://github.com/cmake-wheel/cmeel/compare/v0.18.0...v0.19.0
[v0.18.0]: https://github.com/cmake-wheel/cmeel/compare/v0.17.1...v0.18.0
[v0.17.1]: https://github.com/cmake-wheel/cmeel/compare/v0.17.0...v0.17.1
[v0.17.0]: https://github.com/cmake-wheel/cmeel/compare/v0.16.0...v0.17.0
[v0.16.0]: https://github.com/cmake-wheel/cmeel/compare/v0.15.0...v0.16.0
[v0.15.0]: https://github.com/cmake-wheel/cmeel/compare/v0.14.0...v0.15.0
[v0.14.0]: https://github.com/cmake-wheel/cmeel/compare/v0.13.3...v0.14.0
[v0.13.3]: https://github.com/cmake-wheel/cmeel/compare/v0.13.2...v0.13.3
[v0.13.2]: https://github.com/cmake-wheel/cmeel/compare/v0.13.1...v0.13.2
[v0.13.1]: https://github.com/cmake-wheel/cmeel/compare/v0.13.0...v0.13.1
[v0.13.0]: https://github.com/cmake-wheel/cmeel/compare/v0.12.5...v0.13.0
[v0.12.5]: https://github.com/cmake-wheel/cmeel/compare/v0.12.4...v0.12.5
[v0.12.4]: https://github.com/cmake-wheel/cmeel/compare/v0.12.3...v0.12.4
[v0.12.3]: https://github.com/cmake-wheel/cmeel/compare/v0.12.2...v0.12.3
[v0.12.2]: https://github.com/cmake-wheel/cmeel/compare/v0.12.1...v0.12.2
[v0.12.1]: https://github.com/cmake-wheel/cmeel/compare/v0.12.0...v0.12.1
[v0.12.0]: https://github.com/cmake-wheel/cmeel/compare/v0.11.0...v0.12.0
[v0.11.0]: https://github.com/cmake-wheel/cmeel/compare/v0.10.1...v0.11.0
[v0.10.1]: https://github.com/cmake-wheel/cmeel/compare/v0.10.0...v0.10.1
[v0.10.0]: https://github.com/cmake-wheel/cmeel/compare/v0.9.0...v0.10.0
[v0.9.0]: https://github.com/cmake-wheel/cmeel/compare/v0.8.0...v0.9.0
[v0.8.0]: https://github.com/cmake-wheel/cmeel/compare/v0.7.0...v0.8.0
[v0.7.0]: https://github.com/cmake-wheel/cmeel/compare/v0.6.2...v0.7.0
[v0.6.2]: https://github.com/cmake-wheel/cmeel/compare/v0.6.1...v0.6.2
[v0.6.1]: https://github.com/cmake-wheel/cmeel/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/cmake-wheel/cmeel/compare/v0.5.2...v0.6.0
[v0.5.2]: https://github.com/cmake-wheel/cmeel/compare/v0.5.1...v0.5.2
[v0.5.1]: https://github.com/cmake-wheel/cmeel/compare/v0.5.0...v0.5.1
[v0.5.0]: https://github.com/cmake-wheel/cmeel/compare/v0.4.3...v0.5.0
[v0.4.2]: https://github.com/cmake-wheel/cmeel/compare/v0.4.1...v0.4.2
[v0.4.1]: https://github.com/cmake-wheel/cmeel/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/cmake-wheel/cmeel/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/cmake-wheel/cmeel/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/cmake-wheel/cmeel/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/cmake-wheel/cmeel/releases/tag/v0.1.0
