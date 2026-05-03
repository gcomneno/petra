#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math


def factor_small(n: int) -> list[int]:
    factors: list[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
        if d == 3:
            pass
    if n > 1:
        factors.append(n)
    return factors


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def first_odd_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 3
    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 2
    return primes


def product(values: list[int]) -> int:
    out = 1
    for value in values:
        out *= value
    return out


def fmt_factorization(factors: list[int]) -> str:
    if not factors:
        return "1"
    return " * ".join(str(factor) for factor in factors)


def blade_for_index(index: int) -> tuple[int, list[int]]:
    odd_primes = first_odd_primes(index)
    factors = [2, *odd_primes]
    return product(factors), factors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print experimental PET surface signature metrics."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument(
        "--schedule-limit",
        type=int,
        default=12,
        help="maximum k denominator for the digit blade schedule",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("surface_signature expects integers >= 1")
    if args.schedule_limit < 1:
        raise SystemExit("--schedule-limit expects integers >= 1")

    n = args.n
    decimal = str(n)
    digits = len(decimal)
    digit_sum = sum(int(ch) for ch in decimal)
    max_digit_sum = digits * 9
    decimal_density = digit_sum / max_digit_sum if max_digit_sum else 0.0

    bit_length = n.bit_length()
    popcount = n.bit_count()
    binary_density = popcount / bit_length if bit_length else 0.0

    full_blade, full_blade_factors = blade_for_index(digits)

    print("PET SURFACE SIGNATURE")
    print()
    print(f"N = {n}")
    print(f"digits = {digits}")
    print(f"bit_length = {bit_length}")
    print()
    print("Base surface")
    print("  base = 10")
    print(f"  base_factorization = {fmt_factorization(factor_small(10))}")
    print("  base_minus_one = 9")
    print(f"  base_minus_one_factorization = {fmt_factorization(factor_small(9))}")
    print()
    print("Decimal surface density")
    print(f"  digit_sum = {digit_sum}")
    print(f"  max_digit_sum = {max_digit_sum}")
    print(f"  decimal_surface_density = {decimal_density:.6f}")
    print()
    print("Binary surface density")
    print(f"  popcount = {popcount}")
    print(f"  binary_surface_density = {binary_density:.6f}")
    print()
    print("Digit blade")
    print(f"  blade_index = {digits}")
    print(f"  blade = {full_blade}")
    print(f"  blade_factorization = {fmt_factorization(full_blade_factors)}")
    print()
    print("Digit blade schedule")
    print("  k | blade_index | blade")
    seen: set[int] = set()
    for k in range(1, args.schedule_limit + 1):
        index = max(1, digits // k)
        if index in seen:
            continue
        seen.add(index)
        blade, _ = blade_for_index(index)
        print(f"  {k:>2} | {index:>11} | {blade}")
    print()
    print("claim = PET surface signature only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
