"""Cmeel constants."""
import os
import sys

CMEEL_PREFIX = "cmeel.prefix"
SITELIB = os.path.join(  # noqa: PTH118
    "lib",
    "python" + ".".join(sys.version.split(".")[:2]),
    "site-packages",
)
