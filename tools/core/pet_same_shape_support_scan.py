#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math


def primes_up_to(limit: int) -> list[int]:
    if limit < 2:
        return []

    sieve = [True] * (limit + 1)
    sieve[0] = False
    sieve[1] = False

    for value in range(2, int(limit**0.5) + 1):
        if not sieve[value]:
            continue

        step_start = value * value
        sieve[step_start : limit + 1 : value] = [False] * (
            ((limit - step_start) // value) + 1
        )

    return [value for value, is_prime in enumerate(sieve) if is_prime]


def scan_semiprime_shape(
    n: int,
    *,
    prime_limit: int,
) -> list[tuple[int, int, int]]:
    hits: list[tuple[int, int, int]] = []
    primes = primes_up_to(prime_limit)

    for left in primes:
        gcd_value = math.gcd(n, left)

        if 1 < gcd_value < n:
            hits.append((left, left, gcd_value))
            continue

        for right in primes:
            if right < left:
                continue

            support = left * right
            gcd_value = math.gcd(n, support)

            if 1 < gcd_value < n:
                hits.append((left, right, gcd_value))

    return hits


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classic same-shape support scan for PET no-grip cases."
    )
    parser.add_argument("n", type=int)
    parser.add_argument(
        "--shape",
        default="[[], []]",
        help="Currently only supports semiprime-like [[], []].",
    )
    parser.add_argument(
        "--prime-limit",
        type=int,
        default=200,
    )
    args = parser.parse_args()

    print("PET SAME-SHAPE SUPPORT SCAN")
    print()
    print(f"N = {args.n}")
    print(f"target_shape = {args.shape}")
    print(f"prime_limit = {args.prime_limit}")

    if args.shape != "[[], []]":
        print("scan_status = unsupported-shape")
        print("claim = classic fallback scan only; not PET factorization")
        return 0

    hits = scan_semiprime_shape(
        args.n,
        prime_limit=args.prime_limit,
    )

    unique_hits: dict[int, tuple[int, int]] = {}
    hit_frequencies: dict[int, int] = {}

    for left, right, gcd_value in hits:
        unique_hits.setdefault(gcd_value, (left, right))
        hit_frequencies[gcd_value] = hit_frequencies.get(gcd_value, 0) + 1

    print(f"hit_count = {len(hits)}")
    print(f"unique_factor_hit_count = {len(unique_hits)}")

    best_factor = "-"

    for index, (gcd_value, support) in enumerate(
        sorted(unique_hits.items()),
        start=1,
    ):
        left, right = support

        print(f"factor_{index} = {gcd_value}")
        print(f"factor_{index}_hit_frequency = {hit_frequencies[gcd_value]}")
        print(f"factor_{index}_first_support = {left}*{right}")
        print(f"factor_{index}_first_support_value = {left * right}")

        if best_factor == "-":
            best_factor = str(gcd_value)

    print(f"best_factor = {best_factor}")
    print("claim = classic same-shape support scan; PET only selected the shape family")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
