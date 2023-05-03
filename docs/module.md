# The `cmeel` module

## Environment helpers

Cmeel provides a python module to help dealing with `CMAKE_PREFIX_PATH`, `LD_LIBRARY_PATH` and `PKG_CONFIG_PATH`:
```
usage: python -m cmeel [-h] [-v] {cmake,lib,pc} ...

cmeel environment helpers

options:
  -h, --help            show this help message and exit
  -v, --verbose         increment verbosity level

subcommands:
  valid sub-commands

  {cmake,lib,pc}
                        sub-command help
    cmake               show cmeel additions to CMAKE_PREFIX_PATH
    lib                 show cmeel additions to LD_LIBRARY_PATH
    pc                  show cmeel additions to PKG_CONFIG_PATH
```

For those 3 sub-commands, a `--prepend` option as available to obtain directly the full variable.

## Docker builds

Cmeel provides a python module to build a project in a container, eg. [manylinux](https://github.com/pypa/manylinux):
```
usage: python -m cmeel docker [-h] [-i IMAGE] [-p PYTHON] [-u] [-U]
                              [-c] [-C CWD] [-e ENV] [-E]

options:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        docker image to use for building the wheel
  -p PYTHON, --python PYTHON
                        python interpreter inside that image
  -u, --update          update docker image
  -U, --upgrade         upgrade pip
  -c, --cache           binds /root/.cache/pip
  -C CWD, --cwd CWD     build the project in this directory
  -e ENV, --env ENV     pass environment variables to docker run
  -E, --cmeel-env       forward 'CMEEL_*' environment variables to docker run
```

Environment variables can be forwarded or defined, and so multilple times, eg.:

```
export CMEEL_RUN_TESTS=OFF
export CTEST_PARALLEL_LEVEL=8
python -m cmeel -vvv docker -c -e CTEST_PARALLEL_LEVEL -e CTEST_OUTPUT_ON_FAILURE=ON -E
```
