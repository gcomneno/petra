#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import itertools
import math
from collections import Counter


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


def parse_shape(raw: str) -> object:
    try:
        return ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return raw


def flat_shape_width(raw: str) -> int | None:
    shape = parse_shape(raw)

    if not isinstance(shape, list):
        return None

    if not shape:
        return None

    if any(item != [] for item in shape):
        return None

    return len(shape)


def product(values: tuple[int, ...]) -> int:
    result = 1

    for value in values:
        result *= value

    return result


def scan_flat_k_shape(
    n: int,
    *,
    width: int,
    prime_limit: int,
    max_supports: int,
) -> tuple[list[tuple[tuple[int, ...], int]], int, bool]:
    hits: list[tuple[tuple[int, ...], int]] = []
    primes = primes_up_to(prime_limit)
    support_count = 0
    budget_exhausted = False

    for support in itertools.combinations_with_replacement(primes, width):
        if support_count >= max_supports:
            budget_exhausted = True
            break

        support_count += 1
        support_value = product(support)
        gcd_value = math.gcd(n, support_value)

        if 1 < gcd_value < n:
            hits.append((support, gcd_value))

    return hits, support_count, budget_exhausted


def format_support(support: tuple[int, ...]) -> str:
    return "*".join(str(value) for value in support)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classic flat-k support scan for PET flat leaf families."
    )
    parser.add_argument("n", type=int)
    parser.add_argument(
        "--shape",
        required=True,
        help="Flat PET shape, for example '[[], [], []]'.",
    )
    parser.add_argument(
        "--prime-limit",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--max-supports",
        type=int,
        default=5000,
    )
    parser.add_argument(
        "--max-factor-lines",
        type=int,
        default=25,
        help="Maximum number of factor lines to print; 0 prints none.",
    )
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("pet_flat_k_support_scan expects integers >= 2")

    if args.prime_limit < 2:
        raise SystemExit("--prime-limit must be >= 2")

    if args.max_supports < 1:
        raise SystemExit("--max-supports must be >= 1")

    if args.max_factor_lines < 0:
        raise SystemExit("--max-factor-lines must be >= 0")

    print("PET FLAT-K SUPPORT SCAN")
    print()
    print(f"N = {args.n}")
    print(f"target_shape = {args.shape}")
    print(f"prime_limit = {args.prime_limit}")
    print(f"max_supports = {args.max_supports}")
    print(f"max_factor_lines = {args.max_factor_lines}")

    width = flat_shape_width(args.shape)

    if width is None or width < 2:
        print("scan_status = unsupported-shape")
        print("reason = target shape is not a flat PET leaf family with width >= 2")
        print("claim = classic flat-k support scan; PET only selected the shape family")
        return 0

    hits, support_count, budget_exhausted = scan_flat_k_shape(
        args.n,
        width=width,
        prime_limit=args.prime_limit,
        max_supports=args.max_supports,
    )

    hit_frequencies: Counter[int] = Counter()
    unique_hits: dict[int, tuple[int, ...]] = {}

    for support, gcd_value in hits:
        hit_frequencies[gcd_value] += 1
        unique_hits.setdefault(gcd_value, support)

    scan_status = "budget-exhausted" if budget_exhausted else "complete"

    print(f"flat_width = {width}")
    print(f"support_count = {support_count}")
    print(f"scan_status = {scan_status}")
    sorted_unique_hits = sorted(unique_hits.items())
    printable_hits = sorted_unique_hits[: args.max_factor_lines]
    factor_lines_truncated = len(printable_hits) < len(sorted_unique_hits)

    print(f"hit_count = {len(hits)}")
    print(f"unique_factor_hit_count = {len(unique_hits)}")
    print(f"printed_factor_count = {len(printable_hits)}")
    print(
        "factor_lines_truncated = "
        f"{'yes' if factor_lines_truncated else 'no'}"
    )
    print("factor_selection_policy = deferred-to-residual-descent")

    for index, (gcd_value, support) in enumerate(
        printable_hits,
        start=1,
    ):
        support_value = product(support)

        print(f"factor_{index} = {gcd_value}")
        print(f"factor_{index}_hit_frequency = {hit_frequencies[gcd_value]}")
        print(f"factor_{index}_first_support = {format_support(support)}")
        print(f"factor_{index}_first_support_value = {support_value}")

    print("best_factor = deferred")
    print("claim = classic flat-k support scan; PET only selected the shape family")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
