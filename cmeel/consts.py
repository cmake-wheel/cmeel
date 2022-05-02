import os
import sys

CMEEL_PREFIX = "cmeel.prefix"
SITELIB = os.sep.join(
    ["lib", "python" + ".".join(sys.version.split(".")[:2]), "site-packages"]
)
