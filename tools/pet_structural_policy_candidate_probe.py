#!/usr/bin/env python3
from __future__ import annotations

import random
import time
from math import prod
from typing import Any

from pet.builder_from_irsr import (
    _generate_structural_profile_candidates_v1,
    _iroot_floor,
)
from pet.core import is_prime


def _policy_for(
    *,
    max_support_size: int,
    max_total_weight: int,
    deferred_profiles: list[list[int]] | None = None,
) -> dict[str, Any]:
    return {
        "allowed_exponent_profiles": {
            "max_support_size": max_support_size,
            "max_total_weight": max_total_weight,
            "radius_default": 16,
            "deferred_profiles": deferred_profiles or [],
        },
        "squarefree_support_size_range": [3, 5],
        "squarefree_radius_default": 16,
        "squarefree_radius_overrides": {
            5: 64,
        },
    }


def _random_n(rng: random.Random, byte_count: int) -> int:
    raw = bytearray(rng.randbytes(byte_count))
    if raw:
        raw[0] |= 1
        raw[-1] |= 1
    return int.from_bytes(raw, "big")


def _candidate_prime_metrics(n: int, support_size: int, radius: int) -> dict[str, Any]:
    root = _iroot_floor(n, support_size)
    start = max(2, root - radius)
    stop = root + radius

    started = time.perf_counter()
    primes = [p for p in range(start, stop + 1) if is_prime(p)]
    elapsed = time.perf_counter() - started

    return {
        "support_size": support_size,
        "root": root,
        "radius": radius,
        "range_start": start,
        "range_stop": stop,
        "candidate_count": stop - start + 1,
        "prime_count": len(primes),
        "elapsed_seconds": round(elapsed, 6),
        "primes": primes,
    }


def _profile_root_degree(spec: dict[str, Any]) -> int:
    if spec["backend"] == "generic-exponent":
        return sum(int(exp) for exp in spec["exponent_profile"])
    if spec["backend"] == "generic-squarefree":
        return int(spec["support_size"])
    raise ValueError(f"unknown backend: {spec['backend']!r}")


def _profile_label(spec: dict[str, Any]) -> str:
    if spec["backend"] == "generic-exponent":
        return str(spec["exponent_profile"])
    if spec["backend"] == "generic-squarefree":
        return "[1," * 0 + f"squarefree-k{spec['support_size']}"
    raise ValueError(f"unknown backend: {spec['backend']!r}")


def main() -> int:
    rng = random.Random(20260426)
    radius = 64
    policy = _policy_for(
        max_support_size=4,
        max_total_weight=5,
        deferred_profiles=[],
    )

    specs = _generate_structural_profile_candidates_v1(
        policy=policy,
        structural_radius=radius,
    )

    cases = [
        ("random-8b", _random_n(rng, 8)),
        ("random-12b", _random_n(rng, 12)),
    ]

    print("Structural policy candidate probe")
    print(f"radius = {radius}")
    print(f"profile_count = {len(specs)}")

    all_rows = []

    for case_name, n in cases:
        print()
        print("=" * 80)
        print(case_name)
        print(f"n = {n}")
        print(f"digits = {len(str(n))}")
        print(f"bytes = {(n.bit_length() + 7) // 8}")

        for spec in specs:
            root_degree = _profile_root_degree(spec)
            metrics = _candidate_prime_metrics(
                n,
                support_size=root_degree,
                radius=int(spec["radius"]),
            )
            row = {
                "case": case_name,
                "backend": spec["backend"],
                "profile": _profile_label(spec),
                **metrics,
            }
            all_rows.append(row)

            print()
            print(f"{row['backend']} {row['profile']}")
            print(f"  root_degree = {row['support_size']}")
            print(f"  root = {row['root']}")
            print(f"  range = [{row['range_start']}, {row['range_stop']}]")
            print(f"  candidate_count = {row['candidate_count']}")
            print(f"  prime_count = {row['prime_count']}")
            print(f"  elapsed_seconds = {row['elapsed_seconds']}")

    slowest = sorted(
        all_rows,
        key=lambda item: item["elapsed_seconds"],
        reverse=True,
    )[:5]

    total_elapsed = round(sum(row["elapsed_seconds"] for row in all_rows), 6)

    print()
    print("=" * 80)
    print("Summary")
    print(f"rows = {len(all_rows)}")
    print(f"total_candidate_elapsed_seconds = {total_elapsed}")
    print("Slowest candidate searches:")
    for row in slowest:
        print(
            f"- {row['case']} | {row['backend']} {row['profile']} "
            f"| root_degree={row['support_size']} "
            f"| root={row['root']} "
            f"| candidates={row['candidate_count']} "
            f"| primes={row['prime_count']} "
            f"| elapsed={row['elapsed_seconds']}s"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
