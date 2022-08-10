# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- :warning: BREAKING: fix wheel name (it was using distribution, which replace `-` by `_`)
- :warning: BREAKING: rename `run_tests` into `run-tests`
- :warning: BREAKING: rename `default_env` into `default-env`
- :warning: BREAKING: rename `configure_args` into `configure-args`
- :warning: BREAKING: remove `PYTHON_COMPONENTS`

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
[v2.0.0]: https://github.com/cmake-wheel/cmeel/releases/tag/v0.1.0
