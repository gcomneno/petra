#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "legacy" / "pet_lens_mass_probe.py"
runpy.run_path(str(TARGET), run_name="__main__")
