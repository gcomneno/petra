#!/usr/bin/env python3
"""Research-only PET/PEG operator semantics report matrix.

This tool aggregates the single-N operator semantics report across multiple
integers and emits a compact deterministic matrix.

It also derives pattern signatures and groups numbers that share the same
observed operator-semantics pattern.

It is research-only. It does not change stable PET core behavior, CLI behavior,
routing, residual descent, anchor selection, verification, or factorization
behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.pet_operator_semantics_report import (  # noqa: E402
    BOUNDARIES,
    build_payload as build_report_payload,
)


SCHEMA = "pet.operator_semantics_report_matrix.v0"
CLAIM = (
    "research-only PET/PEG 2.0 experimental operator semantics report matrix; "
    "aggregates single-N reports without changing stable behavior"
)


def unique_ordered(values: list[str | None]) -> list[str]:
    seen: list[str] = []

    for value in values:
        if value is None:
            continue
        if value not in seen:
            seen.append(value)

    return seen


def make_signature(values: list[str]) -> str:
    if not values:
        return "none"
    return "|".join(values)


def make_combined_pattern_signature(
    *,
    xy_signature: str,
    address_stability_signature: str,
    axis_invariants_failed: int,
) -> str:
    return (
        f"xy={xy_signature};"
        f"address={address_stability_signature};"
        f"axis_failed={axis_invariants_failed}"
    )


def first_recursive_sample_address(report: dict[str, Any]) -> list[int] | None:
    for row in report["sample_addresses"]:
        address = row["address"]
        if row["valid"] and len(address) > 1:
            return address
    return None


def has_leaf_sample_address(report: dict[str, Any]) -> bool:
    return any(
        row["valid"] and row["selected_exponent_kind"] == "leaf"
        for row in report["sample_addresses"]
    )


def has_recursive_sample_address(report: dict[str, Any]) -> bool:
    return first_recursive_sample_address(report) is not None


def build_row(n: int) -> dict[str, Any]:
    report = build_report_payload(n)
    axis_summary = report["axis_invariants"]["summary"]

    xy_relations = unique_ordered(
        [row.get("relation") for row in report["xy_composition_samples"]]
    )
    address_stability_classes = unique_ordered(
        [row.get("stability") for row in report["address_stability_samples"]]
    )

    xy_signature = make_signature(xy_relations)
    address_stability_signature = make_signature(address_stability_classes)
    combined_pattern_signature = make_combined_pattern_signature(
        xy_signature=xy_signature,
        address_stability_signature=address_stability_signature,
        axis_invariants_failed=axis_summary["failed"],
    )

    first_recursive_address = first_recursive_sample_address(report)

    return {
        "n": n,
        "top_level_baseline": report["top_level_baseline"],
        "top_level_width": len(report["top_level_baseline"]),
        "sample_address_count": len(report["sample_addresses"]),
        "has_leaf_address": has_leaf_sample_address(report),
        "has_recursive_address": first_recursive_address is not None,
        "first_recursive_address": first_recursive_address,
        "leaf_blocked_observed": "leaf-blocked" in address_stability_classes,
        "support_removed_observed": "support-removed-y-target" in xy_relations,
        "axis_invariants_passed": axis_summary["passed"],
        "axis_invariants_failed": axis_summary["failed"],
        "xy_relations": xy_relations,
        "xy_signature": xy_signature,
        "address_stability_classes": address_stability_classes,
        "address_stability_signature": address_stability_signature,
        "combined_pattern_signature": combined_pattern_signature,
        "boundary": "research-only",
    }


def unique_sorted(values: list[int]) -> list[int]:
    return sorted(set(values))


def group_rows_by_pattern(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    by_signature: dict[str, dict[str, Any]] = {}

    for row in rows:
        signature = row["combined_pattern_signature"]

        if signature not in by_signature:
            group = {
                "combined_pattern_signature": signature,
                "xy_signature": row["xy_signature"],
                "address_stability_signature": row["address_stability_signature"],
                "axis_invariants_failed": row["axis_invariants_failed"],
                "numbers": [],
                "count": 0,
                "example_numbers": [],
                "width_values": [],
                "has_leaf_address_count": 0,
                "has_recursive_address_count": 0,
                "leaf_blocked_count": 0,
                "support_removed_count": 0,
            }
            by_signature[signature] = group
            groups.append(group)

        group = by_signature[signature]
        group["numbers"].append(row["n"])
        group["count"] += 1

        if len(group["example_numbers"]) < 5:
            group["example_numbers"].append(row["n"])

        group["width_values"] = unique_sorted(
            [*group["width_values"], row["top_level_width"]]
        )

        if row["has_leaf_address"]:
            group["has_leaf_address_count"] += 1
        if row["has_recursive_address"]:
            group["has_recursive_address_count"] += 1
        if row["leaf_blocked_observed"]:
            group["leaf_blocked_count"] += 1
        if row["support_removed_observed"]:
            group["support_removed_count"] += 1

    return groups


def inclusive_range(start: int, end: int) -> list[int]:
    if start > end:
        raise ValueError("--range START END requires START <= END")
    return list(range(start, end + 1))


def collect_numbers(
    positional_numbers: list[int],
    ranges: list[list[int]] | None,
) -> list[int]:
    collected: list[int] = []

    for n in positional_numbers:
        collected.append(n)

    for start, end in ranges or []:
        collected.extend(inclusive_range(start, end))

    deduped: list[int] = []
    for n in collected:
        if n not in deduped:
            deduped.append(n)

    if not deduped:
        raise ValueError("at least one N or --range START END is required")

    return deduped


def build_payload(numbers: list[int]) -> dict[str, Any]:
    rows = [build_row(n) for n in numbers]
    pattern_groups = group_rows_by_pattern(rows)

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "numbers": numbers,
        "rows": rows,
        "summary": {
            "checked": len(rows),
            "axis_invariant_failures": sum(
                row["axis_invariants_failed"] for row in rows
            ),
            "numbers_with_axis_invariant_failures": [
                row["n"] for row in rows if row["axis_invariants_failed"] > 0
            ],
            "pattern_count": len(pattern_groups),
            "numbers_by_pattern": {
                group["combined_pattern_signature"]: group["numbers"]
                for group in pattern_groups
            },
        },
        "pattern_groups": pattern_groups,
        "boundaries": BOUNDARIES,
    }


def print_text(payload: dict[str, Any]) -> None:
    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"numbers = {payload['numbers']}")
    print(f"summary = {payload['summary']}")
    print()
    print("rows:")

    for row in payload["rows"]:
        print(
            f"- n={row['n']} "
            f"baseline={row['top_level_baseline']} "
            f"width={row['top_level_width']} "
            f"sample_addresses={row['sample_address_count']} "
            f"recursive={row['has_recursive_address']} "
            f"leaf={row['has_leaf_address']} "
            f"leaf_blocked={row['leaf_blocked_observed']} "
            f"support_removed={row['support_removed_observed']} "
            f"axis_failed={row['axis_invariants_failed']} "
            f"xy_signature={row['xy_signature']} "
            f"address_signature={row['address_stability_signature']}"
        )

    print()
    print("pattern_groups:")
    for group in payload["pattern_groups"]:
        print(
            f"- count={group['count']} "
            f"numbers={group['numbers']} "
            f"examples={group['example_numbers']} "
            f"widths={group['width_values']} "
            f"leaf_count={group['has_leaf_address_count']} "
            f"recursive_count={group['has_recursive_address_count']} "
            f"leaf_blocked_count={group['leaf_blocked_count']} "
            f"support_removed_count={group['support_removed_count']} "
            f"signature={group['combined_pattern_signature']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG operator semantics report matrix."
    )
    parser.add_argument("numbers", type=int, nargs="*", metavar="N", help="integer N >= 2")
    parser.add_argument(
        "--range",
        dest="ranges",
        type=int,
        nargs=2,
        action="append",
        metavar=("START", "END"),
        help="inclusive range of N values",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    numbers = collect_numbers(args.numbers, args.ranges)

    for n in numbers:
        if n < 2:
            raise ValueError("all N values must be >= 2")

    payload = build_payload(numbers)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0 if payload["summary"]["axis_invariant_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
