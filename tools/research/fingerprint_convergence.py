#!/usr/bin/env python3
"""Measure the convergence of the cumulative structural fingerprint.

For a base ``k``, the cumulative fingerprint ``F(1, N)`` is the
``(red, exp, stab)`` profile of the shape sequence ``k^n`` over
``n = 1 .. N``. This script prints ``F(1, N)`` at selected checkpoints
and, for each checkpoint after the first, the Euclidean distance from
the previous checkpoint value. It does not decide whether the sequence
converges: it presents the numbers.

Two modes are available:

- ``--checkpoints``: cumulative fingerprint at a list of ``N`` values;
- ``--disjoint``:   fingerprint over consecutive disjoint windows of
                    the given width.

Output is a human-readable table by default; add ``--json`` to emit one
JSON object per line.

The tool is analytical: it does not modify any shape or runtime state.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Sequence

from resolver import fingerprint_cumulative, fingerprint_window


def _euclidean(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _emit_row(
    label: str,
    fp: tuple[float, float, float],
    delta: float | None,
    as_json: bool,
) -> None:
    if as_json:
        row = {
            "label": label,
            "red": fp[0],
            "exp": fp[1],
            "stab": fp[2],
            "delta": None if delta is None else round(delta, 4),
        }
        print(json.dumps(row, separators=(",", ":"), sort_keys=True))
    else:
        delta_str = "  --    " if delta is None else f"{delta:7.4f}"
        print(f"  {label:>10}   red={fp[0]:6.2f}  exp={fp[1]:6.2f}  stab={fp[2]:6.2f}  delta={delta_str}")


def run_checkpoints(
    base: int,
    checkpoints: Sequence[int],
    as_json: bool,
) -> None:
    prev: tuple[float, float, float] | None = None
    if not as_json:
        print(f"== base {base}, cumulative fingerprint at checkpoints ==")
        print(f"  {'N':>10}      red       exp      stab        delta")
    for n in checkpoints:
        fp = fingerprint_cumulative(base, n)
        delta = None if prev is None else _euclidean(fp, prev)
        _emit_row(f"N={n}", fp, delta, as_json)
        prev = fp


def run_disjoint(
    base: int,
    width: int,
    count: int,
    as_json: bool,
) -> None:
    prev: tuple[float, float, float] | None = None
    if not as_json:
        print(f"== base {base}, disjoint windows of width {width}, {count} windows ==")
        print(f"  {'window':>15}   red    exp   stab    delta")
    for i in range(count):
        lo = i * width + 1
        hi = (i + 1) * width + 1
        # transitions covered: n -> n+1 for n in [lo, hi-1]
        fp = fingerprint_window(base, lo, hi - 1)
        delta = None if prev is None else _euclidean(fp, prev)
        _emit_row(f"[{lo:>5},{hi-1:>5}]", fp, delta, as_json)
        prev = fp


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure convergence of the cumulative structural fingerprint."
    )
    parser.add_argument("--base", type=int, required=True, help="base k >= 2")
    parser.add_argument(
        "--checkpoints",
        type=int,
        nargs="+",
        help="list of cumulative N values to sample",
    )
    parser.add_argument(
        "--disjoint",
        type=int,
        metavar="WIDTH",
        help="measure disjoint windows of the given width",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="number of disjoint windows (only with --disjoint); default 10",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit one JSON object per line",
    )
    args = parser.parse_args(argv)

    if args.base < 2:
        parser.error("--base must be >= 2")
    if not args.checkpoints and not args.disjoint:
        parser.error("provide --checkpoints and/or --disjoint")
    if args.checkpoints and args.disjoint:
        parser.error("choose either --checkpoints or --disjoint, not both")

    if args.checkpoints:
        run_checkpoints(args.base, args.checkpoints, args.json)
    else:
        run_disjoint(args.base, args.disjoint, args.count, args.json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
