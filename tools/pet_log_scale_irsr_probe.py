#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction
from math import prod
from pathlib import Path
from typing import Any

from pet.builder_from_irsr import _candidate_primes_near_root, _iroot_floor
from pet.builder_from_factorization import build_from_factorization_pipeline
from pet.core import is_prime_fast


def _pow_root_floor(n: int, scale: Fraction) -> int:
    """Return floor(n ** scale) for simple rational scales.

    For scale = a / b, compute floor b-th root of n**a.
    This avoids float precision issues for larger integers.
    """
    if scale <= 0 or scale >= 1:
        raise ValueError("scale must be between 0 and 1")

    numerator = scale.numerator
    denominator = scale.denominator

    return _iroot_floor(n**numerator, denominator)


def _scale_specs(max_denominator: int) -> list[tuple[Fraction, Fraction]]:
    specs: list[tuple[Fraction, Fraction]] = []

    for denominator in range(2, max_denominator + 1):
        low = Fraction(1, denominator)
        high = Fraction(denominator - 1, denominator)
        specs.append((low, high))

    return specs


def _candidate_pair_rows(
    n: int,
    *,
    radius: int,
    max_denominator: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for low_scale, high_scale in _scale_specs(max_denominator):
        low_root = _pow_root_floor(n, low_scale)
        high_root = _pow_root_floor(n, high_scale)

        low_candidates = _candidate_primes_near_root(low_root, radius)
        high_candidates = _candidate_primes_near_root(high_root, radius)

        matches = []
        for p in low_candidates:
            if n % p != 0:
                continue

            q = n // p
            if p * q == n and is_prime_fast(q):
                matches.append((p, q))

        rows.append(
            {
                "low_scale": f"{low_scale.numerator}/{low_scale.denominator}",
                "high_scale": f"{high_scale.numerator}/{high_scale.denominator}",
                "low_root": low_root,
                "high_root": high_root,
                "low_candidate_count": len(low_candidates),
                "high_candidate_count": len(high_candidates),
                "matches": matches,
            }
        )

    return rows


def _build_from_match(
    n: int,
    p: int,
    q: int,
    output_dir: Path,
) -> dict[str, Any]:
    factors = [[min(p, q), 1], [max(p, q), 1]]

    with tempfile.TemporaryDirectory() as td:
        factor_spec_file = Path(td) / "factorization.json"
        factor_spec_file.write_text(
            json.dumps(
                {
                    "schema": "pet-factorization-input-v0",
                    "input_n": n,
                    "factors": factors,
                }
            )
        )

        return build_from_factorization_pipeline(
            factor_spec_file,
            output_dir,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe asymmetric semiprime reconstruction using log-scale IRSR.",
    )
    parser.add_argument("n", type=int)
    parser.add_argument("--radius", type=int, default=16)
    parser.add_argument("--max-denominator", type=int, default=8)
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("artifacts/manual/log-scale-irsr-probe"),
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="materialize PET artifacts if an exact candidate pair is found",
    )

    args = parser.parse_args()

    n = args.n
    print("Log-scale IRSR probe")
    print(f"n = {n}")
    print(f"digits = {len(str(n))}")
    print(f"bytes = {(n.bit_length() + 7) // 8}")
    print(f"radius = {args.radius}")
    print(f"max_denominator = {args.max_denominator}")

    rows = _candidate_pair_rows(
        n,
        radius=args.radius,
        max_denominator=args.max_denominator,
    )

    first_match: tuple[int, int] | None = None

    for row in rows:
        print()
        print(f"scale [{row['low_scale']}, {row['high_scale']}]")
        print(f"  low_root = {row['low_root']}")
        print(f"  high_root = {row['high_root']}")
        print(f"  low_candidate_count = {row['low_candidate_count']}")
        print(f"  high_candidate_count = {row['high_candidate_count']}")
        print(f"  matches = {row['matches']}")

        if row["matches"] and first_match is None:
            first_match = row["matches"][0]

    print()
    print("summary")
    print(f"matched = {first_match is not None}")

    if first_match is None:
        return 1

    p, q = first_match
    print(f"match = ({p}, {q})")
    print(f"product_ok = {p * q == n}")

    if args.build:
        report = _build_from_match(
            n,
            p,
            q,
            args.artifacts_dir,
        )
        print()
        print("build")
        print(f"schema = {report.get('schema')}")
        print(f"input_n = {report.get('input_n')}")
        print(f"exponent_multiset = {report['support_report']['exponent_multiset']}")
        print(f"terminal_build_status = {report['final_build_output']['build_status']}")
        print(f"produced_files = {report['builder_execution']['produced_files']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
