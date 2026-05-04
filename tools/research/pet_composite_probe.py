#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pet.core import prime_factorization, shape_signature_dict


PET_UNIT = 1
PET_UNIT_SIGNATURE: list[Any] = []


def factor_counter(n: int) -> Counter[int]:
    if n == PET_UNIT:
        return Counter()
    if n < PET_UNIT:
        raise ValueError("composite PET operators expect integers >= 1")

    factors: Counter[int] = Counter()
    for prime, exponent in prime_factorization(n):
        factors[int(prime)] += int(exponent)

    return factors


def value_from_factors(factors: Counter[int]) -> int:
    value = PET_UNIT
    for prime, exponent in factors.items():
        value *= prime ** exponent
    return value


def pet_data(n: int) -> dict[str, Any]:
    if n == PET_UNIT:
        return {
            "value": PET_UNIT,
            "generator": PET_UNIT,
            "signature": PET_UNIT_SIGNATURE,
        }

    data = shape_signature_dict(n)
    return {
        "value": n,
        "generator": data["generator"],
        "signature": data["signature"],
    }


def pet_merge(left: int, right: int) -> int:
    return value_from_factors(factor_counter(left) + factor_counter(right))


def pet_unmerge(left: int, right: int) -> int | None:
    result = Counter(factor_counter(left))

    for prime, exponent in factor_counter(right).items():
        if result[prime] < exponent:
            return None

        result[prime] -= exponent
        if result[prime] == 0:
            del result[prime]

    return value_from_factors(result)


def is_flat_signature(signature: list[Any]) -> bool:
    return bool(signature) and all(child == [] for child in signature)


def build_self_probe(n: int) -> dict[str, Any]:
    data = pet_data(n)
    generator = int(data["generator"])
    signature = data["signature"]

    unit_merge_left = pet_merge(PET_UNIT, generator)
    unit_merge_right = pet_merge(generator, PET_UNIT)
    self_unmerge = pet_unmerge(generator, generator)

    return {
        "n": n,
        "n_generator": generator,
        "n_signature": signature,
        "pet_unit": PET_UNIT,
        "pet_unit_signature": PET_UNIT_SIGNATURE,
        "unit_merge_left": unit_merge_left,
        "unit_merge_right": unit_merge_right,
        "self_unmerge_available": self_unmerge is not None,
        "self_unmerge_result": self_unmerge,
        "self_unmerge_signature": pet_data(self_unmerge)["signature"]
        if self_unmerge is not None
        else None,
        "flat_generator": is_flat_signature(signature),
        "flat_leaf_count": len(signature) if is_flat_signature(signature) else None,
    }


def build_comparison(left_n: int, right_n: int) -> dict[str, Any]:
    left_data = pet_data(left_n)
    right_data = pet_data(right_n)

    left_generator = int(left_data["generator"])
    right_generator = int(right_data["generator"])

    merge_result = pet_merge(left_generator, right_generator)
    merge_data = pet_data(merge_result)

    unmerge_result = pet_unmerge(left_generator, right_generator)
    unmerge_data = pet_data(unmerge_result) if unmerge_result is not None else None

    return {
        "left_n": left_n,
        "right_n": right_n,
        "left_generator": left_generator,
        "right_generator": right_generator,
        "left_signature": left_data["signature"],
        "right_signature": right_data["signature"],
        "merge_result": merge_result,
        "merge_result_generator": merge_data["generator"],
        "merge_result_signature": merge_data["signature"],
        "unmerge_available": unmerge_result is not None,
        "unmerge_result": unmerge_result,
        "unmerge_result_generator": unmerge_data["generator"]
        if unmerge_data is not None
        else None,
        "unmerge_result_signature": unmerge_data["signature"]
        if unmerge_data is not None
        else None,
    }


def print_self_probe(report: dict[str, Any]) -> None:
    print("PET COMPOSITE PROBE")
    print()
    print(f"N = {report['n']}")
    print(f"n_generator = {report['n_generator']}")
    print(f"n_signature = {report['n_signature']}")
    print()
    print("PET unit")
    print(f"pet_unit = {report['pet_unit']}")
    print(f"pet_unit_signature = {report['pet_unit_signature']}")
    print()
    print("Unit merge")
    print(f"unit_merge_left = {report['unit_merge_left']}")
    print(f"unit_merge_right = {report['unit_merge_right']}")
    print()
    print("Self unmerge")
    print(f"self_unmerge_available = {'yes' if report['self_unmerge_available'] else 'no'}")
    print(f"self_unmerge_result = {report['self_unmerge_result']}")
    print(f"self_unmerge_signature = {report['self_unmerge_signature']}")
    print()
    print("Flat generator analysis")
    print(f"flat_generator = {'yes' if report['flat_generator'] else 'no'}")
    print(f"flat_leaf_count = {report['flat_leaf_count']}")
    print()
    print("claim = PET composite probe only; this does not factor N")


def print_comparison(report: dict[str, Any]) -> None:
    print()
    print("Composite comparison")
    print(f"left_n = {report['left_n']}")
    print(f"right_n = {report['right_n']}")
    print(f"left_generator = {report['left_generator']}")
    print(f"right_generator = {report['right_generator']}")
    print(f"left_signature = {report['left_signature']}")
    print(f"right_signature = {report['right_signature']}")
    print()
    print("PET-MERGE")
    print(f"merge_result = {report['merge_result']}")
    print(f"merge_result_generator = {report['merge_result_generator']}")
    print(f"merge_result_signature = {report['merge_result_signature']}")
    print()
    print("PET-UNMERGE")
    print(f"unmerge_available = {'yes' if report['unmerge_available'] else 'no'}")
    print(f"unmerge_result = {report['unmerge_result']}")
    print(f"unmerge_result_generator = {report['unmerge_result_generator']}")
    print(f"unmerge_result_signature = {report['unmerge_result_signature']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research-facing PET composite operator probe."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument(
        "--other",
        type=int,
        help="Compare N's canonical generator with another value's canonical generator.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.n < PET_UNIT:
        raise SystemExit("pet_composite_probe expects N >= 1")
    if args.other is not None and args.other < PET_UNIT:
        raise SystemExit("pet_composite_probe expects --other >= 1")

    self_probe = build_self_probe(args.n)
    comparison = (
        build_comparison(args.n, args.other)
        if args.other is not None
        else None
    )

    if args.json:
        print(
            json.dumps(
                {
                    "self_probe": self_probe,
                    "comparison": comparison,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print_self_probe(self_probe)
    if comparison is not None:
        print_comparison(comparison)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
