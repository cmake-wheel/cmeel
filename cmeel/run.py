"""Cmeel run."""
import os
import sys
from pathlib import Path
from subprocess import run

from .consts import CMEEL_PREFIX


def cmeel_run():
    """Wrap an executable inside cmeel prefix."""
    prefix = Path(__file__).parent.parent / CMEEL_PREFIX  # TODO: not uniq

    exe = Path(sys.argv[0]).name
    sys.argv[0] = prefix / "bin" / exe

    # TODO: RPATH would be better
    lib = f"{prefix}/lib"
    if "LD_LIBRARY_PATH" in os.environ:
        if lib not in os.environ["LD_LIBRARY_PATH"]:
            os.environ["LD_LIBRARY_PATH"] = f"{lib}:{os.environ['LD_LIBRARY_PATH']}"
    else:
        os.environ["LD_LIBRARY_PATH"] = lib

    exe = run(sys.argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(exe.returncode)
