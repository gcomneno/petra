#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy
import sys

TARGET = Path(__file__).resolve().parent / "core" / "pet_flat_k_support_scan.py"
CORE_DIR = TARGET.parent

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
else:
    globals().update(runpy.run_path(str(TARGET), run_name=__name__))
