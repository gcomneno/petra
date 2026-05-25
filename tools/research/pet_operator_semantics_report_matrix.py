#!/usr/bin/env python3
"""Experimental PET/PEG operator semantics report matrix.

This tool aggregates the single-N operator semantics report across multiple
integers and emits a compact deterministic matrix.

It also derives pattern signatures and groups numbers that share the same
observed operator-semantics pattern.

It is experimental documented tooling. It does not change stable PET core behavior, CLI behavior,
routing, residual descent, anchor selection, verification, or factorization
behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.pet_operator_semantics_report import (  # noqa: E402
    BOUNDARIES,
    build_payload as build_report_payload,
)


SCHEMA = "pet.operator_semantics_report_matrix.v0"
CLAIM = (
    "experimental PET/PEG 2.0 operator semantics report matrix; "
    "aggregates single-N reports without changing stable behavior"
)
TOOLING_STATUS = "experimental documented tooling"
STABLE_CLI_CONTRACT = False


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
        "boundary": "experimental",
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


def _signature_parts(signature: str) -> set[str]:
    if signature == "none":
        return set()
    return set(signature.split("|"))


def classify_pattern_group(group: dict[str, Any]) -> str:
    """Return a descriptive class for an observed matrix pattern group.

    These labels are experimental vocabulary for matrix readability. They do
    not define stable PET semantics.
    """

    xy_parts = _signature_parts(group["xy_signature"])
    address_parts = _signature_parts(group["address_stability_signature"])
    widths = set(group["width_values"])

    support_removed = "support-removed-y-target" in xy_parts
    stable = "stable" in address_parts
    destroyed = "destroyed" in address_parts
    leaf_blocked = "leaf-blocked" in address_parts
    single_support = widths == {1}

    if single_support and stable and not destroyed and not leaf_blocked:
        return "single-support-root-stable"
    if single_support and not stable and not destroyed and not leaf_blocked:
        return "single-support-leaf"
    if single_support and stable and not destroyed and leaf_blocked:
        return "single-support-leaf-blocked"
    if single_support and stable and destroyed and not leaf_blocked:
        return "single-support-recursive-chain"
    if single_support and not stable and not destroyed and leaf_blocked:
        return "single-support-leaf-blocked-retarget"
    if single_support and not stable and destroyed and not leaf_blocked:
        return "single-support-power-destroyed"

    if support_removed and stable and destroyed and not leaf_blocked:
        return "multi-support-stable-removal"
    if support_removed and not stable and destroyed and not leaf_blocked:
        return "multi-support-removal"
    if support_removed and stable and destroyed and leaf_blocked:
        return "multi-support-recursive-leaf-blocked"
    if support_removed and not stable and destroyed and leaf_blocked:
        return "multi-support-leaf-blocked-removal"

    return "unclassified-operator-pattern"


def annotate_pattern_groups(pattern_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for group in pattern_groups:
        group["pattern_class"] = classify_pattern_group(group)
    return pattern_groups


def count_pattern_classes(pattern_groups: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for group in pattern_groups:
        pattern_class = group["pattern_class"]
        counts[pattern_class] = counts.get(pattern_class, 0) + group["count"]

    return counts


def dominant_pattern_class(pattern_groups: list[dict[str, Any]]) -> str | None:
    if not pattern_groups:
        return None

    counts = count_pattern_classes(pattern_groups)
    return max(counts.items(), key=lambda item: (item[1], item[0]))[0]


def unclassified_pattern_class_count(pattern_groups: list[dict[str, Any]]) -> int:
    return sum(
        group["count"]
        for group in pattern_groups
        if group["pattern_class"] == "unclassified-operator-pattern"
    )


def factor_items(n: int) -> list[tuple[int, int]]:
    items: list[tuple[int, int]] = []
    divisor = 2

    while divisor * divisor <= n:
        if n % divisor == 0:
            exponent = 0
            while n % divisor == 0:
                n //= divisor
                exponent += 1
            items.append((divisor, exponent))

        divisor += 1 if divisor == 2 else 2

    if n > 1:
        items.append((n, 1))

    return items


def first_nonflat_exponent(items: list[tuple[int, int]]) -> int | None:
    for _, exponent in items:
        if exponent > 1:
            return exponent
    return None


def arithmetic_anatomy(numbers: list[int]) -> dict[str, Any]:
    omega: Counter[int] = Counter()
    big_omega: Counter[int] = Counter()
    max_exp: Counter[int] = Counter()
    first_nonflat_exp: Counter[int | str] = Counter()
    squarefree_count = 0
    has_support_2_3_count = 0

    for n in numbers:
        items = factor_items(n)
        exponents = [exponent for _, exponent in items]
        primes = {prime for prime, _ in items}

        omega[len(exponents)] += 1
        big_omega[sum(exponents)] += 1
        max_exp[max(exponents)] += 1

        nonflat = first_nonflat_exponent(items)
        first_nonflat_exp[nonflat if nonflat is not None else "none"] += 1

        if all(exponent == 1 for exponent in exponents):
            squarefree_count += 1

        if 2 in primes and 3 in primes:
            has_support_2_3_count += 1

    return {
        "omega_dist": dict(sorted(omega.items())),
        "big_omega_dist": dict(sorted(big_omega.items())),
        "max_exp_dist": dict(sorted(max_exp.items())),
        "first_nonflat_exp_dist": {
            str(key): value
            for key, value in sorted(
                first_nonflat_exp.items(),
                key=lambda item: str(item[0]),
            )
        },
        "squarefree_count": squarefree_count,
        "squarefree_ratio": squarefree_count / len(numbers) if numbers else 0.0,
        "has_support_2_3_count": has_support_2_3_count,
        "has_support_2_3_ratio": (
            has_support_2_3_count / len(numbers) if numbers else 0.0
        ),
    }


def add_arithmetic_anatomy(pattern_groups: list[dict[str, Any]]) -> None:
    for group in pattern_groups:
        group["arithmetic_anatomy"] = arithmetic_anatomy(group["numbers"])


def has_support_2_3(items: list[tuple[int, int]]) -> bool:
    primes = {prime for prime, _ in items}
    return 2 in primes and 3 in primes


def predicted_multi_support_nonflat_class(n: int) -> str:
    items = factor_items(n)
    first_nonflat = first_nonflat_exponent(items)
    support_2_3 = has_support_2_3(items)

    if first_nonflat == 2:
        if support_2_3:
            return "multi-support-recursive-leaf-blocked"
        return "multi-support-leaf-blocked-removal"

    if support_2_3:
        return "multi-support-stable-removal"
    return "multi-support-removal"


def check_multi_support_nonflat_rule(
    pattern_groups: list[dict[str, Any]],
) -> dict[str, Any]:
    checked = 0
    mismatches: list[dict[str, Any]] = []

    for group in pattern_groups:
        actual_class = group["pattern_class"]
        if not actual_class.startswith("multi-support"):
            continue

        for n in group["numbers"]:
            checked += 1
            predicted_class = predicted_multi_support_nonflat_class(n)

            if predicted_class == actual_class:
                continue

            items = factor_items(n)
            mismatches.append(
                {
                    "n": n,
                    "actual_pattern_class": actual_class,
                    "predicted_pattern_class": predicted_class,
                    "factor_items": items,
                    "first_nonflat_exp": first_nonflat_exponent(items),
                    "has_support_2_3": has_support_2_3(items),
                }
            )

    return {
        "status": "passed" if not mismatches else "failed",
        "checked": checked,
        "mismatch_count": len(mismatches),
        "sample_mismatches": mismatches[:10],
    }


def filter_pattern_groups(
    pattern_groups: list[dict[str, Any]],
    *,
    top_patterns: int | None = None,
    min_count: int | None = None,
    pattern: str | None = None,
) -> list[dict[str, Any]]:
    filtered = pattern_groups

    if min_count is not None:
        filtered = [group for group in filtered if group["count"] >= min_count]

    if pattern is not None:
        filtered = [
            group
            for group in filtered
            if pattern in group["combined_pattern_signature"]
        ]

    if top_patterns is not None:
        indexed_groups = list(enumerate(filtered))
        indexed_groups.sort(key=lambda item: (-item[1]["count"], item[0]))
        filtered = [group for _, group in indexed_groups[:top_patterns]]

    return filtered


def validate_pattern_group_filters(
    *,
    top_patterns: int | None = None,
    min_count: int | None = None,
) -> None:
    if top_patterns is not None and top_patterns < 1:
        raise ValueError("--top-patterns N requires N >= 1")
    if min_count is not None and min_count < 1:
        raise ValueError("--min-count N requires N >= 1")


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


def progress_milestones(total: int) -> dict[int, int]:
    if total <= 0:
        return {}

    return {
        max(1, (total * percent + 99) // 100): percent
        for percent in range(10, 101, 10)
    }


def build_rows(
    numbers: list[int],
    *,
    progress: bool = False,
    progress_stream: TextIO = sys.stderr,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    milestones = progress_milestones(len(numbers)) if progress else {}

    for index, n in enumerate(numbers, start=1):
        rows.append(build_row(n))

        if index in milestones:
            print(
                f"progress: checked {index}/{len(numbers)} ({milestones[index]}%)",
                file=progress_stream,
            )

    return rows


def build_payload(
    numbers: list[int],
    *,
    top_patterns: int | None = None,
    min_count: int | None = None,
    pattern: str | None = None,
    include_rows: bool = True,
    include_anatomy: bool = False,
    check_rules: bool = False,
    progress: bool = False,
    progress_stream: TextIO = sys.stderr,
) -> dict[str, Any]:
    validate_pattern_group_filters(top_patterns=top_patterns, min_count=min_count)

    rows = build_rows(numbers, progress=progress, progress_stream=progress_stream)
    all_pattern_groups = annotate_pattern_groups(group_rows_by_pattern(rows))

    if include_anatomy:
        add_arithmetic_anatomy(all_pattern_groups)

    pattern_groups = filter_pattern_groups(
        all_pattern_groups,
        top_patterns=top_patterns,
        min_count=min_count,
        pattern=pattern,
    )
    filters_active = (
        top_patterns is not None
        or min_count is not None
        or pattern is not None
        or not include_rows
    )

    payload = {
        "schema": SCHEMA,
        "claim": CLAIM,
        "tooling_status": TOOLING_STATUS,
        "stable_cli_contract": STABLE_CLI_CONTRACT,
        "numbers": numbers,
        "summary": {
            "checked": len(rows),
            "axis_invariant_failures": sum(
                row["axis_invariants_failed"] for row in rows
            ),
            "numbers_with_axis_invariant_failures": [
                row["n"] for row in rows if row["axis_invariants_failed"] > 0
            ],
            "pattern_count": len(all_pattern_groups),
            "emitted_pattern_count": len(pattern_groups),
            "pattern_class_count": count_pattern_classes(all_pattern_groups),
            "emitted_pattern_class_count": count_pattern_classes(pattern_groups),
            "dominant_pattern_class": dominant_pattern_class(all_pattern_groups),
            "unclassified_pattern_class_count": unclassified_pattern_class_count(
                all_pattern_groups
            ),
            "anatomy_enabled": include_anatomy,
            "pattern_group_filter_active": filters_active,
            "numbers_by_pattern": {
                group["combined_pattern_signature"]: group["numbers"]
                for group in all_pattern_groups
            },
        },
        "pattern_groups": pattern_groups,
        "pattern_group_filters": {
            "top_patterns": top_patterns,
            "min_count": min_count,
            "pattern": pattern,
            "include_rows": include_rows,
            "active": filters_active,
        },
        "boundaries": BOUNDARIES,
    }

    if check_rules:
        payload["rule_checks"] = {
            "multi_support_nonflat_rule": check_multi_support_nonflat_rule(
                all_pattern_groups
            )
        }

    if include_rows:
        payload["rows"] = rows

    return payload



def print_text(payload: dict[str, Any]) -> None:
    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"tooling_status = {payload['tooling_status']}")
    print(f"stable_cli_contract = {payload['stable_cli_contract']}")
    print(f"numbers = {payload['numbers']}")
    print(f"summary = {payload['summary']}")

    if payload["pattern_group_filters"]["active"]:
        print(f"pattern_group_filters = {payload['pattern_group_filters']}")

    if "rule_checks" in payload:
        print()
        print("rule_checks:")
        for name, check in payload["rule_checks"].items():
            print(
                f"- {name} "
                f"status={check['status']} "
                f"checked={check['checked']} "
                f"mismatches={check['mismatch_count']}"
            )

            if check["sample_mismatches"]:
                print(f"  sample_mismatches={check['sample_mismatches']}")

    if "rows" in payload:
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
        anatomy_suffix = ""
        if "arithmetic_anatomy" in group:
            anatomy_suffix = f" anatomy={group['arithmetic_anatomy']}"

        print(
            f"- class={group['pattern_class']} "
            f"count={group['count']} "
            f"numbers={group['numbers']} "
            f"examples={group['example_numbers']} "
            f"widths={group['width_values']} "
            f"leaf_count={group['has_leaf_address_count']} "
            f"recursive_count={group['has_recursive_address_count']} "
            f"leaf_blocked_count={group['leaf_blocked_count']} "
            f"support_removed_count={group['support_removed_count']} "
            f"signature={group['combined_pattern_signature']}"
            f"{anatomy_suffix}"
        )



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Experimental PET/PEG operator semantics report matrix."
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
    parser.add_argument(
        "--top-patterns",
        type=int,
        metavar="N",
        help="emit only the N most frequent pattern groups",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        metavar="N",
        help="emit only pattern groups with count >= N",
    )
    parser.add_argument(
        "--pattern",
        metavar="TEXT",
        help="emit only pattern groups whose combined signature contains TEXT",
    )
    parser.add_argument(
        "--no-rows",
        action="store_true",
        help="omit per-N rows and emit only summary plus pattern groups",
    )
    parser.add_argument(
        "--anatomy",
        action="store_true",
        help="include arithmetic anatomy summaries for each pattern group",
    )
    parser.add_argument(
        "--check-rules",
        action="store_true",
        help="include experimental rule-check summaries in the payload",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="emit progress checkpoints to stderr every 10%",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    numbers = collect_numbers(args.numbers, args.ranges)

    for n in numbers:
        if n < 2:
            raise ValueError("all N values must be >= 2")

    payload = build_payload(
        numbers,
        top_patterns=args.top_patterns,
        min_count=args.min_count,
        pattern=args.pattern,
        include_rows=not args.no_rows,
        include_anatomy=args.anatomy,
        check_rules=args.check_rules,
        progress=args.progress,
    )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0 if payload["summary"]["axis_invariant_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
