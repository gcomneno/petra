#!/usr/bin/env python3
"""Research-only PET/PEG operator semantics report matrix.

This tool aggregates the single-N operator semantics report across multiple
integers and emits a compact deterministic matrix.

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


def build_row(n: int) -> dict[str, Any]:
    report = build_report_payload(n)
    axis_summary = report["axis_invariants"]["summary"]

    xy_relations = unique_ordered(
        [row.get("relation") for row in report["xy_composition_samples"]]
    )
    address_stability_classes = unique_ordered(
        [row.get("stability") for row in report["address_stability_samples"]]
    )

    return {
        "n": n,
        "top_level_baseline": report["top_level_baseline"],
        "sample_address_count": len(report["sample_addresses"]),
        "axis_invariants_passed": axis_summary["passed"],
        "axis_invariants_failed": axis_summary["failed"],
        "xy_relations": xy_relations,
        "address_stability_classes": address_stability_classes,
        "boundary": "research-only",
    }


def build_payload(numbers: list[int]) -> dict[str, Any]:
    rows = [build_row(n) for n in numbers]

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
        },
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
            f"sample_addresses={row['sample_address_count']} "
            f"axis_failed={row['axis_invariants_failed']} "
            f"xy_relations={row['xy_relations']} "
            f"address_stability={row['address_stability_classes']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG operator semantics report matrix."
    )
    parser.add_argument("numbers", type=int, nargs="+", metavar="N", help="integer N >= 2")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    for n in args.numbers:
        if n < 2:
            raise ValueError("all N values must be >= 2")

    payload = build_payload(args.numbers)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0 if payload["summary"]["axis_invariant_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
