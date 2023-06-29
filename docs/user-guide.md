# Use software packaged with cmeel

## Install cmeel packages

cmeel expose a standard pip interface, so with an up-to-date `pip`, you can follow
<https://pip.pypa.io/en/stable/cli/pip_install/#description>

### Install binary packages from PyPI (or other indexes)

```
python -m pip install cmeel-example
```

### Install source package from a git url

```
python -m pip install git+https://github.com/your-fork/cmeel-example@some-branch
```

### Install source package from a local path

```
python -m pip install ./cmeel-example
```

### Install binary packages from a wheel over HTTP

```
python -m pip install https://hostname.tld/path/package-version-python-abi-platform.whl
```

## Use installed cmeel packages to compile something else

For other CMake packages, you just need to tell CMake where to find cmeel dependencies, eg.:
```
export CMAKE_PREFIX_PATH=$(python -m cmeel cmake)
```

If your packages require pkg-config:
```
export PKG_CONFIG_PATH=$(python -m cmeel pc)
```

And, at runtime, if you libraries have a hard time finding each other:
```
export LD_LIBRARY_PATH=$(python -m cmeel lib)
```
