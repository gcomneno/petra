#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys


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


def yes_no(value: object) -> str:
    return "yes" if bool(value) else "no"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a PET-guided first-step crumb classic scan."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-generator-count", type=int, default=20)
    parser.add_argument("--excluded-support-limit", type=int, default=16)
    parser.add_argument("--max-move-span", type=int, default=5)
    parser.add_argument("--handoff-radius", type=int, default=100)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_crumb_classic_scan expects integers >= 1")

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
            "NEW",
            "--kind",
            "boundary-entry",
            "--cut",
            "--peel-step",
            "--slice",
            "--lift",
            "--decode",
            "--center-lens",
            "--realize",
            "--classic-handoff",
            "--handoff-radius",
            str(args.handoff_radius),
            "--json",
        ]
    )
    focused = json.loads(focused_text)

    selected_band = focused.get("selected_band") or {}
    realization = focused.get("pet_realization") or {}
    handoff = focused.get("pet_classic_handoff") or {}

    print("PET CRUMB CLASSIC SCAN")
    print()
    print(f"N = {args.n}")
    print("source = boundary-entry NEW")
    print(f"selected_band = {selected_band.get('kind', 'unknown')} {selected_band.get('move', 'unknown')} k[{selected_band.get('k_range', 'unknown')}]")
    print(f"edge_k = {realization.get('edge_k', handoff.get('edge_k', 'unknown'))}")
    print(f"center = {realization.get('nearest_integer', handoff.get('center', 'unknown'))}")
    print(f"method = {handoff.get('method', 'unknown')}")
    print(f"recommended = {yes_no(handoff.get('recommended', False))}")
    print(f"divisor_found = {handoff.get('divisor_found') or 'none'}")
    print(f"cofactor = {handoff.get('cofactor') or 'none'}")
    print(f"verified = {yes_no(handoff.get('verified', False))}")
    print()
    print("claim = PET-guided crumb classic scan only; divisors are accepted only when verified")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
