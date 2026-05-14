#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
PROBE_TOOL = ROOT_DIR / "tools" / "research" / "pet_completion_aware_residual_probe.py"


DEFAULT_WALLS = [
    1001,
    17017,
    323323,
    7436429,
]

DEFAULT_CONTEXTS = [
    14,
    21,
    22,
    26,
    30,
    33,
    42,
    55,
    66,
    70,
    78,
]


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def parse_int_list(raw: str) -> list[int]:
    values: list[int] = []

    for part in raw.split(","):
        item = part.strip()

        if not item:
            continue

        values.append(positive_int(item))

    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")

    return values


def run_probe(n: int, max_depth: int) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            str(PROBE_TOOL),
            str(n),
            "--max-depth",
            str(max_depth),
            "--compare-ranking-policy",
            "--json",
        ],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"probe failed for {n}: {detail}")

    return json.loads(result.stdout)


def build_row(wall: int, context: int, max_depth: int) -> dict[str, Any]:
    n = wall * context
    probe = run_probe(n, max_depth)
    ranking = probe["ranking_policy_comparison"]

    return {
        "wall": wall,
        "context": context,
        "n": n,
        "status": probe["status"],
        "current_anchor": ranking["current_selected_anchor"],
        "current_residual": ranking["current_selected_residual"],
        "shadow_anchor": ranking["suggested_anchor"],
        "shadow_residual": ranking["suggested_residual"],
        "changed": ranking["changed_selection"],
        "reason": ranking["reason"],
        "candidate_count": len(probe["candidates"]),
    }


def build_rows(
    walls: list[int],
    contexts: list[int],
    max_depth: int,
    *,
    include_wall_alone: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for wall in walls:
        if include_wall_alone:
            rows.append(build_row(wall, 1, max_depth))

        for context in contexts:
            rows.append(build_row(wall, context, max_depth))

    return rows


def print_tsv(rows: list[dict[str, Any]], *, changed_only: bool) -> None:
    headers = [
        "wall",
        "context",
        "n",
        "status",
        "current_anchor",
        "current_residual",
        "shadow_anchor",
        "shadow_residual",
        "changed",
        "reason",
        "candidate_count",
    ]

    print("\t".join(headers))

    for row in rows:
        if changed_only and not row["changed"]:
            continue

        print("\t".join(str(row[key]) for key in headers))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Research-only matrix report for PET shadow completion-aware ranking."
        ),
    )
    parser.add_argument(
        "--walls",
        type=parse_int_list,
        default=DEFAULT_WALLS,
        help="Comma-separated wall numbers.",
    )
    parser.add_argument(
        "--contexts",
        type=parse_int_list,
        default=DEFAULT_CONTEXTS,
        help="Comma-separated multiplicative contexts.",
    )
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--changed-only", action="store_true")
    parser.add_argument("--include-wall-alone", action="store_true")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    rows = build_rows(
        args.walls,
        args.contexts,
        args.max_depth,
        include_wall_alone=args.include_wall_alone,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "schema": "pet.shadow_ranking_matrix.v0",
                    "profile": {
                        "max_depth": args.max_depth,
                        "changed_only": args.changed_only,
                        "include_wall_alone": args.include_wall_alone,
                    },
                    "rows": [
                        row
                        for row in rows
                        if not args.changed_only or row["changed"]
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_tsv(rows, changed_only=args.changed_only)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
