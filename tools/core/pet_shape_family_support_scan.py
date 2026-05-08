#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import math
import sys
from collections import Counter
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.research.pet_operator_bridge_study import shape_signature_dict


SUPPORTED_SHAPE_FAMILIES = {
    "branchy-shape",
    "mixed-depth",
    "one-deep-tail",
}


def parse_shape(raw: str) -> object:
    try:
        return ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return raw


def shape_node_depth(node: object) -> int:
    if not isinstance(node, list) or node == []:
        return 1

    return 1 + max(shape_node_depth(child) for child in node)


def shape_depth_profile(signature: object) -> list[int]:
    if not isinstance(signature, list):
        return []

    return [shape_node_depth(child) for child in signature]


def shape_has_internal_branch(signature: object) -> bool:
    if not isinstance(signature, list):
        return False

    def visit(node: object) -> bool:
        if not isinstance(node, list) or node == []:
            return False

        if len(node) > 1:
            return True

        return any(visit(child) for child in node)

    return any(visit(child) for child in signature)


def shape_family_class_for_signature(target_signature: str) -> str:
    signature = parse_shape(target_signature)

    if not isinstance(signature, list):
        return "unclassified-shape-family"

    width = len(signature)
    depth_profile = shape_depth_profile(signature)
    deep_child_count = sum(1 for depth in depth_profile if depth > 1)
    is_flat = all(child == [] for child in signature)

    if width == 1 and is_flat:
        return "atomic-leaf"

    if width == 2 and is_flat:
        return "semiprime-flat"

    if width >= 3 and is_flat:
        return "flat-k-leaf"

    if width == 1 and deep_child_count == 1:
        return "narrow-deep-chain"

    if deep_child_count == 1 and not shape_has_internal_branch(signature):
        return "one-deep-tail"

    if shape_has_internal_branch(signature):
        return "branchy-shape"

    if deep_child_count > 1:
        return "mixed-depth"

    return "unclassified-shape-family"


def support_shape_matches(
    support_value: int,
    *,
    target_shape: object,
) -> bool:
    try:
        support_shape = shape_signature_dict(support_value)["signature"]
    except Exception:
        return False

    return support_shape == target_shape


def scan_shape_family_supports(
    n: int,
    *,
    target_shape: object,
    support_limit: int,
    max_supports: int,
) -> tuple[list[tuple[int, int]], int, int, bool]:
    hits: list[tuple[int, int]] = []
    tested_value_count = 0
    support_count = 0
    budget_exhausted = False

    for support_value in range(2, support_limit + 1):
        tested_value_count += 1

        if not support_shape_matches(
            support_value,
            target_shape=target_shape,
        ):
            continue

        if support_count >= max_supports:
            budget_exhausted = True
            break

        support_count += 1
        gcd_value = math.gcd(n, support_value)

        if 1 < gcd_value < n:
            hits.append((support_value, gcd_value))

    return hits, tested_value_count, support_count, budget_exhausted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classic support scan for PET branchy and mixed-depth shape families."
    )
    parser.add_argument("n", type=int)
    parser.add_argument(
        "--shape",
        required=True,
        help="PET target shape, for example '[[], [[], []]]'.",
    )
    parser.add_argument(
        "--support-limit",
        type=int,
        default=10000,
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
    )
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("pet_shape_family_support_scan expects integers >= 2")

    if args.support_limit < 2:
        raise SystemExit("--support-limit must be >= 2")

    if args.max_supports < 1:
        raise SystemExit("--max-supports must be >= 1")

    if args.max_factor_lines < 0:
        raise SystemExit("--max-factor-lines must be >= 0")

    target_shape = parse_shape(args.shape)
    shape_family_class = shape_family_class_for_signature(args.shape)

    print("PET SHAPE-FAMILY SUPPORT SCAN")
    print()
    print(f"N = {args.n}")
    print(f"target_shape = {args.shape}")
    print(f"shape_family_class = {shape_family_class}")
    print(f"support_limit = {args.support_limit}")
    print(f"max_supports = {args.max_supports}")
    print(f"max_factor_lines = {args.max_factor_lines}")

    if shape_family_class not in SUPPORTED_SHAPE_FAMILIES:
        print("scan_status = unsupported-shape-family")
        print(
            "reason = shape family is not supported by this structural support scan"
        )
        print(
            "claim = classic shape-family support scan; PET only selected the shape family"
        )
        return 0

    hits, tested_value_count, support_count, budget_exhausted = (
        scan_shape_family_supports(
            args.n,
            target_shape=target_shape,
            support_limit=args.support_limit,
            max_supports=args.max_supports,
        )
    )

    hit_frequencies: Counter[int] = Counter()
    unique_hits: dict[int, int] = {}

    for support_value, gcd_value in hits:
        hit_frequencies[gcd_value] += 1
        unique_hits.setdefault(gcd_value, support_value)

    scan_status = "budget-exhausted" if budget_exhausted else "complete"
    sorted_unique_hits = sorted(unique_hits.items())
    printable_hits = sorted_unique_hits[: args.max_factor_lines]
    factor_lines_truncated = len(printable_hits) < len(sorted_unique_hits)

    print(f"tested_value_count = {tested_value_count}")
    print(f"support_count = {support_count}")
    print(f"scan_status = {scan_status}")
    print(f"hit_count = {len(hits)}")
    print(f"unique_factor_hit_count = {len(unique_hits)}")
    print(f"printed_factor_count = {len(printable_hits)}")
    print(
        "factor_lines_truncated = "
        f"{'yes' if factor_lines_truncated else 'no'}"
    )
    print("factor_selection_policy = deferred-to-residual-descent")

    for index, (gcd_value, support_value) in enumerate(
        printable_hits,
        start=1,
    ):
        print(f"factor_{index} = {gcd_value}")
        print(f"factor_{index}_hit_frequency = {hit_frequencies[gcd_value]}")
        print(f"factor_{index}_first_support = {support_value}")

    print("best_factor = deferred")
    print(
        "claim = classic shape-family support scan; PET only selected the shape family"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
