"""Append cmeel prefix sitelib to sys.path."""
import os
import sys
from pathlib import Path

# This is copy-pasted to avoid any non-stdlib import in the .pth file
# vvv uwarning: keep sync with cmeel/consts.py
CMEEL_PREFIX = "cmeel.prefix"
SITELIB = os.sep.join(  # noqa: PTH118
    ["lib", "python" + ".".join(sys.version.split(".")[:2]), "site-packages"],
)
# ^^^

sys.path.append(str(Path(__file__).parent / CMEEL_PREFIX / SITELIB))

for path in sys.path.copy():
    cmeel_sitelib = Path(path) / CMEEL_PREFIX / SITELIB
    if cmeel_sitelib.exists() and str(cmeel_sitelib) not in sys.path:
        sys.path.append(str(cmeel_sitelib))
