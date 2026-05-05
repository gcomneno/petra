#!/usr/bin/env python3
from __future__ import annotations

import argparse
import multiprocessing as mp
import time
from typing import Any

from pet.core import shape_signature_dict
from pet_decimal_boundary_study import decimal_boundary_profile


def compute_signature(n: int) -> dict[str, Any]:
    return shape_signature_dict(n)


def run_with_timeout(n: int, timeout_seconds: float) -> tuple[str, float]:
    start = time.monotonic()

    with mp.Pool(processes=1) as pool:
        result = pool.apply_async(compute_signature, (n,))
        try:
            result.get(timeout=timeout_seconds)
        except mp.TimeoutError:
            pool.terminate()
            pool.join()
            return "timeout", time.monotonic() - start

    return "ok", time.monotonic() - start


def digit_repetition_ratio(n: int) -> float:
    digits = str(n)
    if not digits:
        return 0.0

    counts: dict[str, int] = {}
    for digit in digits:
        counts[digit] = counts.get(digit, 0) + 1

    return max(counts.values()) / len(digits)


def digit_unique_count(n: int) -> int:
    return len(set(str(n)))


def format_float(value: float) -> str:
    return f"{value:.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Study PET shape signature cost against lightweight decimal profiles."
    )
    parser.add_argument("numbers", nargs="+", type=int, metavar="N")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    fields = [
        "N",
        "digits",
        "digit_unique_count",
        "digit_repetition_ratio",
        "decimal_rigid_border_score",
        "decimal_rigid_border_hint",
        "digit_block_count",
        "longest_digit_run",
        "digit_island_count",
        "digit_transition_pressure",
        "signature_status",
        "signature_elapsed_seconds",
    ]

    print(" ".join(fields))

    for n in args.numbers:
        profile = decimal_boundary_profile(n)
        status, elapsed = run_with_timeout(n, args.timeout)

        row = {
            "N": str(n),
            "digits": str(profile["digits"]),
            "digit_unique_count": str(digit_unique_count(n)),
            "digit_repetition_ratio": format_float(digit_repetition_ratio(n)),
            "decimal_rigid_border_score": format_float(
                float(profile["decimal_rigid_border_score"])
            ),
            "decimal_rigid_border_hint": str(profile["decimal_rigid_border_hint"]),
            "digit_block_count": str(profile["digit_block_count"]),
            "longest_digit_run": str(profile["longest_digit_run"]),
            "digit_island_count": str(profile["digit_island_count"]),
            "digit_transition_pressure": format_float(
                float(profile["digit_transition_pressure"])
            ),
            "signature_status": status,
            "signature_elapsed_seconds": f"{elapsed:.2f}",
        }

        print(" ".join(row[field] for field in fields), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
