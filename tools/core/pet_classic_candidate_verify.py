#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify only the explicitly supplied PET candidate generators against N."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--candidate", action="append", default=[])
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("pet_classic_candidate_verify expects integers >= 2")

    print("PET CLASSIC CANDIDATE VERIFY")
    print()
    print(f"N = {args.n}")
    print(f"candidate_count = {len(args.candidate)}")

    seen: set[int] = set()
    verified = 0
    usable = 0
    best_factor = 1
    best_residual = args.n

    candidate_values: list[int | None] = []
    for raw in args.candidate:
        try:
            candidate_values.append(int(raw))
        except ValueError:
            candidate_values.append(None)

    ordered_pairs = sorted(
        enumerate(candidate_values, start=1),
        key=lambda item: -1 if item[1] is None else -item[1],
    )

    raw_values = args.candidate

    for index, candidate in ordered_pairs:
        raw = raw_values[index - 1]
        if candidate is None:
            print(f"candidate_{index}_raw = {raw}")
            print(f"candidate_{index}_status = invalid")
            continue

        print(f"candidate_{index}_value = {candidate}")

        if candidate < 2:
            print(f"candidate_{index}_status = ignored")
            print(f"candidate_{index}_reason = candidate < 2")
            continue

        if candidate in seen:
            print(f"candidate_{index}_status = duplicate")
            continue
        seen.add(candidate)

        gcd_value = math.gcd(args.n, candidate)
        print(f"candidate_{index}_gcd = {gcd_value}")

        if gcd_value == 1:
            print(f"candidate_{index}_status = no-hit")
            continue

        if gcd_value == args.n:
            print(f"candidate_{index}_status = trivial-hit")
            print(f"candidate_{index}_reason = candidate equals N or is a multiple of N")
            continue

        residual = args.n // gcd_value
        verified += 1
        if gcd_value >= 4:
            usable += 1
            hit_kind = "usable-hit"
        else:
            hit_kind = "weak-hit"

        if gcd_value > best_factor:
            best_factor = gcd_value
            best_residual = residual

        print(f"candidate_{index}_status = verified-factor")
        print(f"candidate_{index}_hit_kind = {hit_kind}")
        print(f"candidate_{index}_factor = {gcd_value}")
        print(f"candidate_{index}_residual = {residual}")

    print()
    print(f"verified_factor_count = {verified}")
    print(f"usable_factor_count = {usable}")
    print(f"best_factor = {best_factor if best_factor > 1 else '-'}")
    print(f"best_residual = {best_residual if best_factor > 1 else '-'}")
    print("claim = verifies only supplied candidates; does not search for new factors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
