# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/nim65s/cmeel/compare/v0.4.2...main
[v0.5.1]: https://github.com/nim65s/cmeel/compare/v0.5.0...v0.5.1
[v0.5.0]: https://github.com/nim65s/cmeel/compare/v0.4.3...v0.5.0
[v0.4.2]: https://github.com/nim65s/cmeel/compare/v0.4.1...v0.4.2
[v0.4.1]: https://github.com/nim65s/cmeel/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/nim65s/cmeel/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/nim65s/cmeel/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/nim65s/cmeel/compare/v0.1.0...v0.2.0
[v2.0.0]: https://github.com/nim65s/cmeel/releases/tag/v0.1.0
