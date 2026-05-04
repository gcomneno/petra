#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "classic" / "pet_classic_scan_summary.py"
runpy.run_path(str(TARGET), run_name="__main__")
