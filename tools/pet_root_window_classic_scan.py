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
    end = min(n - 1, center + radius)

    for candidate in range(start, end + 1):
        if n % candidate != 0:
            continue

        cofactor = n // candidate
        if cofactor <= 1 or cofactor >= n:
            continue

        hits.append((candidate, cofactor))

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
    parser.add_argument(
        "--radius-digits",
        type=int,
        default=None,
        help="Set scan radius to 10^D decimal units.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output.",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_root_window_classic_scan expects integers >= 1")
    if args.radius < 0:
        raise SystemExit("--radius expects integers >= 0")
    if args.radius_digits is not None and args.radius_digits < 0:
        raise SystemExit("--radius-digits expects integers >= 0")

    radius = 10 ** args.radius_digits if args.radius_digits is not None else args.radius

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

    claim = "PET-guided root-window classic scan only; divisors are accepted only when verified"
    radius_policy = "decimal-digits" if args.radius_digits is not None else "fixed"
    payload: dict[str, Any] = {
        "n": args.n,
        "source": "PET decoded-center lens",
        "move": args.move,
        "suggested_window": {
            "k_start": k_start,
            "k_end": k_end,
            "k_range": k_range,
        },
        "radius_policy": radius_policy,
        "radius": radius,
        "radius_digits": args.radius_digits,
        "scan_results": [],
        "verified_divisors": [],
        "verified_hit_count": 0,
        "claim": claim,
    }

    if not center_lens.get("center_lens_available"):
        payload["scan_status"] = "unavailable"
        payload["reason"] = center_lens.get("reason", "decoded-center lens is not available")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0

        print("PET ROOT-WINDOW CLASSIC SCAN")
        print()
        print(f"N = {args.n}")
        print("source = PET decoded-center lens")
        print(f"move = {args.move}")
        print(f"suggested_window = k[{k_range}]")
        if args.radius_digits is not None:
            print("radius_policy = decimal-digits")
            print(f"radius_digits = {args.radius_digits}")
        else:
            print("radius_policy = fixed")
        print(f"radius = {radius}")
        print()
        print("scan_status = unavailable")
        print(f"reason = {payload['reason']}")
        print()
        print(f"claim = {claim}")
        return 0

    if k_start < 1 or k_end < k_start:
        payload["scan_status"] = "unavailable"
        payload["reason"] = "decoded-center lens did not provide a valid suggested window"
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0

        print("PET ROOT-WINDOW CLASSIC SCAN")
        print()
        print(f"N = {args.n}")
        print("source = PET decoded-center lens")
        print(f"move = {args.move}")
        print(f"suggested_window = k[{k_range}]")
        if args.radius_digits is not None:
            print("radius_policy = decimal-digits")
            print(f"radius_digits = {args.radius_digits}")
        else:
            print("radius_policy = fixed")
        print(f"radius = {radius}")
        print()
        print("scan_status = unavailable")
        print("reason = decoded-center lens did not provide a valid suggested window")
        print()
        print(f"claim = {claim}")
        return 0

    payload["scan_status"] = "available"
    hits_by_candidate: dict[int, dict[str, object]] = {}

    for k in range(k_start, k_end + 1):
        center = integer_nth_root_nearest(args.n, k)
        hits = scan_window(args.n, center, radius)
        candidate_hits = [
            {"divisor": candidate, "cofactor": cofactor, "verified": True}
            for candidate, cofactor in hits
        ]
        payload["scan_results"].append(
            {
                "k": k,
                "center": center,
                "candidate_hits": candidate_hits,
            }
        )

        for candidate, cofactor in hits:
            record = hits_by_candidate.setdefault(
                candidate,
                {"cofactor": cofactor, "matched_k": []},
            )
            record["matched_k"].append(k)

    verified_divisors = []
    for candidate in sorted(hits_by_candidate):
        record = hits_by_candidate[candidate]
        verified_divisors.append(
            {
                "divisor": candidate,
                "cofactor": record["cofactor"],
                "matched_k": record["matched_k"],
                "verified": True,
            }
        )

    payload["verified_divisors"] = verified_divisors
    payload["verified_hit_count"] = len(verified_divisors)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("PET ROOT-WINDOW CLASSIC SCAN")
    print()
    print(f"N = {args.n}")
    print("source = PET decoded-center lens")
    print(f"move = {args.move}")
    print(f"suggested_window = k[{k_range}]")
    if args.radius_digits is not None:
        print("radius_policy = decimal-digits")
        print(f"radius_digits = {args.radius_digits}")
    else:
        print("radius_policy = fixed")
    print(f"radius = {radius}")
    print()

    for result in payload["scan_results"]:
        print(f"k = {result['k']}")
        print(f"center = {result['center']}")

        candidate_hits = result["candidate_hits"]
        if candidate_hits:
            for hit in candidate_hits:
                print(f"candidate_hit = {hit['divisor']}")
                print("verified = yes")
        else:
            print("candidate_hit = none")
            print("verified = no")

        print()

    print("Verified divisors")
    if verified_divisors:
        for record in verified_divisors:
            matched_k = ",".join(str(k) for k in record["matched_k"])
            print(f"divisor_found = {record['divisor']}")
            print(f"cofactor = {record['cofactor']}")
            print(f"matched_k = {matched_k}")
            print("verified = yes")
    else:
        print("divisor_found = none")

    print()
    print(f"verified_hit_count = {len(verified_divisors)}")
    print()
    print(f"claim = {claim}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
