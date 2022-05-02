import os
import sys

SITELIB = os.sep.join(
    ["lib", "python" + ".".join(sys.version.split(".")[:2]), "site-packages"]
)
CMEEL_PREFIX = "cmeel.prefix"
CMEEL_PTH = os.sep.join([CMEEL_PREFIX, SITELIB])
