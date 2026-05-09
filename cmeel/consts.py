"""Cmeel constants."""

import os
import sys

LICENSE_GLOBS = ["LICEN[CS]E*", "COPYING*", "NOTICE*", "AUTHORS*"]
# vvv Warning: keep sync with cmeel_pth.py
CMEEL_PREFIX = "cmeel.prefix"
SITELIB = os.path.join(  # noqa: PTH118
    "lib",
    "python" + ".".join(sys.version.split(".")[:2]),
    "site-packages",
)
# ^^^
