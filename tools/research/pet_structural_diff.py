#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet.core import prime_factorization, shape_signature_dict


def factor_map(n: int) -> dict[int, int]:
    return {p: e for p, e in prime_factorization(n)}


def exp_signature(exp: int):
    if exp < 1:
        raise ValueError("exp must be >= 1")
    if exp == 1:
        return []
    return shape_signature_dict(exp)["signature"]


def build_multiplicative_diff(before: int, factor: int) -> dict:
    if before < 2:
        raise ValueError("before must be >= 2")
    if factor < 2:
        raise ValueError("factor must be >= 2")

    after = before * factor

    before_map = factor_map(before)
    factor_map_ = factor_map(factor)
    after_map = factor_map(after)

    attached_branches = []
    bumped_branches = []
    unchanged_branches = []

    for prime in sorted(after_map):
        exp_before = before_map.get(prime, 0)
        exp_delta = factor_map_.get(prime, 0)
        exp_after = after_map[prime]

        branch_before = None if exp_before == 0 else exp_signature(exp_before)
        branch_after = exp_signature(exp_after)

        item = {
            "prime": prime,
            "exp_before": exp_before,
            "exp_after": exp_after,
            "delta": exp_delta,
            "branch_before": branch_before,
            "branch_after": branch_after,
        }

        if exp_before == 0:
            attached_branches.append(item)
        elif exp_after > exp_before:
            bumped_branches.append(item)
        else:
            unchanged_branches.append(item)

    return {
        "mode": "mul",
        "before": before,
        "before_signature": shape_signature_dict(before)["signature"],
        "factor": factor,
        "factor_signature": shape_signature_dict(factor)["signature"],
        "after": after,
        "result_signature": shape_signature_dict(after)["signature"],
        "attached_count": len(attached_branches),
        "bumped_count": len(bumped_branches),
        "unchanged_count": len(unchanged_branches),
        "attached_branches": attached_branches,
        "bumped_branches": bumped_branches,
        "unchanged_branches": unchanged_branches,
    }


def build_divisive_diff(before: int, factor: int) -> dict:
    if before < 2:
        raise ValueError("before must be >= 2")
    if factor < 2:
        raise ValueError("factor must be >= 2")
    if before % factor != 0:
        raise ValueError("division mode requires exact divisibility: before % factor == 0")
    after = before // factor
    if after < 2:
        raise ValueError("division mode requires result >= 2")

    before_map = factor_map(before)
    factor_map_ = factor_map(factor)
    after_map = factor_map(after)

    removed_branches = []
    decremented_branches = []
    unchanged_branches = []

    for prime in sorted(before_map):
        exp_before = before_map[prime]
        exp_delta = factor_map_.get(prime, 0)
        exp_after = after_map.get(prime, 0)

        if exp_delta > exp_before:
            raise ValueError(f"factor removes too much exponent on prime {prime}")

        branch_before = exp_signature(exp_before)
        branch_after = None if exp_after == 0 else exp_signature(exp_after)

        item = {
            "prime": prime,
            "exp_before": exp_before,
            "exp_after": exp_after,
            "delta": -exp_delta,
            "branch_before": branch_before,
            "branch_after": branch_after,
        }

        if exp_after == 0:
            removed_branches.append(item)
        elif exp_after < exp_before:
            decremented_branches.append(item)
        else:
            unchanged_branches.append(item)

    return {
        "mode": "div",
        "before": before,
        "before_signature": shape_signature_dict(before)["signature"],
        "factor": factor,
        "factor_signature": shape_signature_dict(factor)["signature"],
        "after": after,
        "result_signature": shape_signature_dict(after)["signature"],
        "removed_count": len(removed_branches),
        "decremented_count": len(decremented_branches),
        "unchanged_count": len(unchanged_branches),
        "removed_branches": removed_branches,
        "decremented_branches": decremented_branches,
        "unchanged_branches": unchanged_branches,
    }


def build_structural_diff(before: int, factor: int, mode: str) -> dict:
    if mode == "mul":
        return build_multiplicative_diff(before, factor)
    if mode == "div":
        return build_divisive_diff(before, factor)
    raise ValueError(f"unsupported mode: {mode}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research-facing PET structural diff for multiplicative and exact divisive updates."
    )
    parser.add_argument("before", type=int, help="Starting integer >= 2")
    parser.add_argument("factor", type=int, help="Factor/divisor >= 2")
    parser.add_argument(
        "--mode",
        choices=["mul", "div"],
        default="mul",
        help="Update mode: multiplication or exact division",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        report = build_structural_diff(args.before, args.factor, args.mode)

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"mode = {report['mode']}")
            print(f"before = {report['before']}")
            print(f"factor = {report['factor']}")
            print(f"after = {report['after']}")
            if report["mode"] == "mul":
                print(f"attached_branches = {report['attached_branches']}")
                print(f"bumped_branches = {report['bumped_branches']}")
                print(f"unchanged_branches = {report['unchanged_branches']}")
            else:
                print(f"removed_branches = {report['removed_branches']}")
                print(f"decremented_branches = {report['decremented_branches']}")
                print(f"unchanged_branches = {report['unchanged_branches']}")
            print(f"result_signature = {report['result_signature']}")

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
