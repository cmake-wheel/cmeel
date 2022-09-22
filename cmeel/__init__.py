"""Cmeel module."""

try:
    from importlib.metadata import metadata
except ImportError:  # Python < 3.8
    from importlib_metadata import metadata

__metadata__ = metadata("cmeel")
__name__ = __metadata__["name"]
__version__ = __metadata__["version"]
__license__ = __metadata__["license"]
__author__ = __metadata__["author"]
