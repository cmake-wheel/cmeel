import sys
from pathlib import Path

from .consts import CMEEL_PREFIX, SITELIB

sys.path.append(str(Path(__file__).parent.parent / CMEEL_PREFIX / SITELIB))
