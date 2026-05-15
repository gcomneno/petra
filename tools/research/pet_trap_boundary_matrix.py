#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]

PROBE_TOOL = (
    ROOT_DIR
    / "tools"
    / "research"
    / "pet_guarded_redirect_execution_probe.py"
)


DEFAULT_NUMBERS = [
    238238,
    357357,
    374374,
    442442,
    561561,
    935935,
    4526522,
    5527522,
    6789783,
    104110006,
    156165009,
    30030,
    323323,
    646646,
    807807,
]


ACTIVE_SIGNALS = {
    "active-complete",
    "active-prime-leaf",
    "active-partial-expandable",
}

INACTIVE_SIGNALS = {
    "inactive-flat-k-required",
    "inactive-shape-family-required",
}


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def parse_range(raw: str) -> list[int]:
    if ":" not in raw:
        raise argparse.ArgumentTypeError(
            "range must use START:END format"
        )

    start_raw, end_raw = raw.split(":", 1)

    start = positive_int(start_raw)
    end = positive_int(end_raw)

    if end < start:
        raise argparse.ArgumentTypeError(
            "range end must be >= start"
        )

    return list(range(start, end + 1))


def run_probe(numbers: list[int], max_depth: int) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            str(PROBE_TOOL),
            *[str(n) for n in numbers],
            "--max-depth",
            str(max_depth),
            "--json",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"probe failed: {detail}")

    return json.loads(result.stdout)


def classify_activity_transition(
    current_signal: str,
    shadow_signal: str,
) -> str:
    current_active = current_signal in ACTIVE_SIGNALS
    shadow_active = shadow_signal in ACTIVE_SIGNALS

    current_inactive = current_signal in INACTIVE_SIGNALS
    shadow_inactive = shadow_signal in INACTIVE_SIGNALS

    if current_inactive and shadow_active:
        return "inactive-to-active"

    if current_active and shadow_active:
        return "active-stable"

    if current_inactive and shadow_inactive:
        return "inactive-stable"

    if current_signal == "blocked" and shadow_signal == "blocked":
        return "blocked-stable"

    return "mixed"


def classify_row(row: dict[str, Any]) -> str:
    expanded = row["expanded_execution_delta"]

    if expanded == "redirect-completes-with-flat-k":
        return "redirect-recoverable-flat-k"

    if expanded == "redirect-completes-with-shape-family":
        return "redirect-recoverable-shape-family"

    if expanded == "redirect-still-blocked":
        return "redirect-still-blocked"

    if row["current_status"] == "complete":
        return "healthy-active"

    if (
        row["guard_reason"]
        == "shadow-ranking-does-not-change-selection"
    ):
        return "wall-stable-blocked"

    return "inactive-collapse"


def build_rows(
    numbers: list[int],
    max_depth: int,
) -> list[dict[str, Any]]:
    print(
        f"[trap-boundary-matrix] probing "
        f"{len(numbers)} number(s)...",
        file=sys.stderr,
    )

    probe = run_probe(numbers, max_depth)

    rows = []

    for index, row in enumerate(probe["rows"], start=1):
        print(
            f"[trap-boundary-matrix] "
            f"[{index}/{len(probe['rows'])}] "
            f"classifying N={row['n']}",
            file=sys.stderr,
        )
        activity_transition = classify_activity_transition(
            row["current_signal"],
            row["shadow_signal"],
        )

        classification = classify_row(row)

        rows.append(
            {
                "n": row["n"],
                "current_status": row["current_status"],
                "current_anchor": row["current_anchor"],
                "shadow_anchor": row["shadow_anchor"],
                "structural_prefix": row["structural_prefix"],
                "current_signal": row["current_signal"],
                "shadow_signal": row["shadow_signal"],
                "guard_decision": row["guard_decision"],
                "guard_reason": row["guard_reason"],
                "expanded_execution_delta": (
                    row["expanded_execution_delta"]
                ),
                "activity_transition": activity_transition,
                "classification": classification,
            }
        )

    return rows


def print_tsv(rows: list[dict[str, Any]]) -> None:
    headers = [
        "n",
        "current_status",
        "current_anchor",
        "shadow_anchor",
        "structural_prefix",
        "current_signal",
        "shadow_signal",
        "guard_decision",
        "guard_reason",
        "expanded_execution_delta",
        "activity_transition",
        "classification",
    ]

    print("\t".join(headers))

    for row in rows:
        print("\t".join(str(row[key]) for key in headers))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Research-only matrix for structural-prefix trap "
            "activation boundaries."
        ),
    )

    parser.add_argument(
        "n",
        nargs="*",
        type=positive_int,
        default=[],
    )

    parser.add_argument(
        "--range",
        dest="range_values",
        type=parse_range,
        metavar="START:END",
        help="scan inclusive numeric range",
    )
    parser.add_argument("--max-depth", type=int, default=4)

    parser.add_argument(
        "--classification-filter",
        action="append",
        default=[],
        help="restrict output to matching classifications",
    )

    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    numbers = args.n

    if args.range_values is not None:
        numbers.extend(args.range_values)

    if not numbers:
        numbers = DEFAULT_NUMBERS

    rows = build_rows(numbers, args.max_depth)

    if args.classification_filter:
        rows = [
            row
            for row in rows
            if (
                row["classification"]
                in args.classification_filter
            )
        ]

    if args.json:
        print(
            json.dumps(
                {
                    "schema": "pet.trap_boundary_matrix.v0",
                    "profile": {
                        "max_depth": args.max_depth,
                    },
                    "rows": rows,
                    "claim": (
                        "Research-only phenomenological matrix for "
                        "structural-prefix trap activation boundaries."
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_tsv(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
