"""Append cmeel prefix sitelib to sys.path."""
import sys
from pathlib import Path

from .consts import CMEEL_PREFIX, SITELIB

sys.path.append(str(Path(__file__).parent.parent / CMEEL_PREFIX / SITELIB))

for path in sys.path.copy():
    cmeel_sitelib = Path(path) / CMEEL_PREFIX / SITELIB
    if cmeel_sitelib.exists() and str(cmeel_sitelib) not in sys.path:
        sys.path.append(str(cmeel_sitelib))
