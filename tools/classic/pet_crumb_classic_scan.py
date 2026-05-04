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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
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

    claim = "PET-guided crumb classic scan only; divisors are accepted only when verified"
    payload = {
        "n": args.n,
        "source": "boundary-entry NEW",
        "selected_band": {
            "kind": selected_band.get("kind", "unknown"),
            "move": selected_band.get("move", "unknown"),
            "k_range": selected_band.get("k_range", "unknown"),
        },
        "edge_k": realization.get("edge_k", handoff.get("edge_k", "unknown")),
        "center": realization.get("nearest_integer", handoff.get("center", "unknown")),
        "method": handoff.get("method", "unknown"),
        "recommended": bool(handoff.get("recommended", False)),
        "divisor_found": handoff.get("divisor_found"),
        "cofactor": handoff.get("cofactor"),
        "verified": bool(handoff.get("verified", False)),
        "claim": claim,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("PET CRUMB CLASSIC SCAN")
    print()
    print(f"N = {args.n}")
    print("source = boundary-entry NEW")
    print(f"selected_band = {payload['selected_band']['kind']} {payload['selected_band']['move']} k[{payload['selected_band']['k_range']}]")
    print(f"edge_k = {payload['edge_k']}")
    print(f"center = {payload['center']}")
    print(f"method = {payload['method']}")
    print(f"recommended = {yes_no(payload['recommended'])}")
    print(f"divisor_found = {payload['divisor_found'] or 'none'}")
    print(f"cofactor = {payload['cofactor'] or 'none'}")
    print(f"verified = {yes_no(payload['verified'])}")
    print()
    print(f"claim = {claim}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
