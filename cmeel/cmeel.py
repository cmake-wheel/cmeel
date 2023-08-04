"""Cmeel metadata."""

from importlib.metadata import metadata

__metadata__ = metadata("cmeel")
__project_name__ = __metadata__["name"]
__version__ = __metadata__["version"]
__license__ = __metadata__["license"]
__author__ = __metadata__["author"]
