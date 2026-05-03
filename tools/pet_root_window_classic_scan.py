#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from math import floor
from typing import Any


def run_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr)
    return result.stdout


def integer_nth_root_nearest(n: int, k: int) -> int:
    estimate = int(round(n ** (1 / k)))
    candidates = range(max(1, estimate - 2), estimate + 3)
    return min(candidates, key=lambda candidate: abs(candidate**k - n))


def parse_window(window: dict[str, Any]) -> tuple[int, int, str]:
    k_start = int(window.get("k_start", 0))
    k_end = int(window.get("k_end", 0))
    k_range = str(window.get("k_range", "unknown"))
    return k_start, k_end, k_range


def scan_window(n: int, center: int, radius: int) -> list[tuple[int, int]]:
    hits: list[tuple[int, int]] = []

    start = max(2, center - radius)
    end = center + radius

    for candidate in range(start, end + 1):
        if n % candidate == 0:
            hits.append((candidate, n // candidate))

    return hits


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a PET-guided classic scan around root-window centers."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-generator-count", type=int, default=20)
    parser.add_argument("--excluded-support-limit", type=int, default=16)
    parser.add_argument("--max-move-span", type=int, default=5)
    parser.add_argument("--move", default="DROP")
    parser.add_argument("--radius", type=int, default=500)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_root_window_classic_scan expects integers >= 1")
    if args.radius < 0:
        raise SystemExit("--radius expects integers >= 0")

    focused_text = run_command(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "opaque-focused-peel",
            str(args.n),
            "--max-generator-count",
            str(args.max_generator_count),
            "--excluded-support-limit",
            str(args.excluded_support_limit),
            "--max-move-span",
            str(args.max_move_span),
            "--move",
            args.move,
            "--cut",
            "--peel-step",
            "--slice",
            "--lift",
            "--decode",
            "--center-lens",
            "--realize",
            "--classic-handoff",
            "--json",
        ]
    )
    focused = json.loads(focused_text)

    center_lens = focused.get("decoded_center_lens") or {}
    suggested_window = center_lens.get("suggested_window") or {}
    k_start, k_end, k_range = parse_window(suggested_window)

    print("PET ROOT-WINDOW CLASSIC SCAN")
    print()
    print(f"N = {args.n}")
    print("source = PET decoded-center lens")
    print(f"move = {args.move}")
    print(f"suggested_window = k[{k_range}]")
    print(f"radius = {args.radius}")
    print()

    if not center_lens.get("center_lens_available"):
        print("scan_status = unavailable")
        print(f"reason = {center_lens.get('reason', 'decoded-center lens is not available')}")
        print()
        print("claim = PET-guided root-window classic scan only; divisors are accepted only when verified")
        return 0

    if k_start < 1 or k_end < k_start:
        print("scan_status = unavailable")
        print("reason = decoded-center lens did not provide a valid suggested window")
        print()
        print("claim = PET-guided root-window classic scan only; divisors are accepted only when verified")
        return 0

    total_hits = 0

    for k in range(k_start, k_end + 1):
        center = integer_nth_root_nearest(args.n, k)
        hits = scan_window(args.n, center, args.radius)

        print(f"k = {k}")
        print(f"center = {center}")

        if hits:
            for candidate, cofactor in hits:
                total_hits += 1
                print(f"divisor_found = {candidate}")
                print(f"cofactor = {cofactor}")
                print("verified = yes")
        else:
            print("divisor_found = none")
            print("verified = no")

        print()

    print(f"verified_hit_count = {total_hits}")
    print()
    print("claim = PET-guided root-window classic scan only; divisors are accepted only when verified")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
