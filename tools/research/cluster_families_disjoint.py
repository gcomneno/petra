"""
Compatibility wrapper for the disjoint family benchmark.

The canonical implementation now lives in src/pet/families.py
and is exposed through:

    pet families benchmark-disjoint
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pet.families import cmd_benchmark_disjoint


def main() -> int:
    return cmd_benchmark_disjoint(argparse.Namespace())


if __name__ == "__main__":
    raise SystemExit(main())
