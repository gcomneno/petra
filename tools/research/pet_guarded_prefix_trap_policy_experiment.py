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

INACTIVE_SIGNALS = {
    "inactive-flat-k-required",
    "inactive-shape-family-required",
}


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


def is_positive_int_text(raw: str) -> bool:
    return raw.isdigit() and int(raw) > 0


def candidate_by_anchor(
    probe: dict[str, Any],
    anchor: str,
) -> dict[str, Any] | None:
    for row in probe["candidates"]:
        if row["anchor"] == anchor:
            return row

    return None


def evaluate_guard(probe: dict[str, Any]) -> dict[str, str]:
    ranking = probe["ranking_policy_comparison"]

    current_anchor = ranking["current_selected_anchor"]
    shadow_anchor = ranking["suggested_anchor"]

    current_row = candidate_by_anchor(probe, current_anchor)
    shadow_row = candidate_by_anchor(probe, shadow_anchor)

    current_signal = "-"
    shadow_signal = "-"

    if current_row is not None:
        current_signal = current_row.get("active_completion_signal", "-")

    if shadow_row is not None:
        shadow_signal = shadow_row.get("active_completion_signal", "-")

    guard = {
        "structural_prefix": "-",
        "current_signal": current_signal,
        "shadow_signal": shadow_signal,
        "guard_decision": "keep-current",
        "guard_reason": "not-evaluated",
    }

    if probe["status"] != "blocked-no-verified-anchor":
        guard["guard_reason"] = "not-blocked-status"
        return guard

    if not ranking["changed_selection"]:
        guard["guard_reason"] = "shadow-ranking-does-not-change-selection"
        return guard

    if not (
        is_positive_int_text(current_anchor)
        and is_positive_int_text(shadow_anchor)
    ):
        guard["guard_reason"] = "non-positive-integer-anchor"
        return guard

    current_anchor_int = int(current_anchor)
    shadow_anchor_int = int(shadow_anchor)

    if current_anchor_int % shadow_anchor_int != 0:
        guard["guard_reason"] = "current-anchor-not-divisible-by-shadow-anchor"
        return guard

    structural_prefix = current_anchor_int // shadow_anchor_int
    guard["structural_prefix"] = str(structural_prefix)

    if structural_prefix <= 1:
        guard["guard_reason"] = "no-structural-prefix"
        return guard

    if current_row is None or shadow_row is None:
        guard["guard_reason"] = "candidate-details-missing"
        return guard

    if shadow_signal != "active-partial-expandable":
        guard["guard_reason"] = "shadow-not-active-partial-expandable"
        return guard

    if current_signal not in INACTIVE_SIGNALS:
        guard["guard_reason"] = "current-not-inactive"

        return guard

    guard["guard_decision"] = "would-redirect-to-shadow-anchor"
    guard["guard_reason"] = "structural-prefix-trap-active-shadow"

    return guard


def build_row(wall: int, context: int, max_depth: int) -> dict[str, Any]:
    n = wall * context
    probe = run_probe(n, max_depth)
    ranking = probe["ranking_policy_comparison"]
    guard = evaluate_guard(probe)

    return {
        "wall": wall,
        "context": context,
        "n": n,
        "status": probe["status"],
        "current_anchor": ranking["current_selected_anchor"],
        "current_residual": ranking["current_selected_residual"],
        "shadow_anchor": ranking["suggested_anchor"],
        "shadow_residual": ranking["suggested_residual"],
        "structural_prefix": guard["structural_prefix"],
        "current_signal": guard["current_signal"],
        "shadow_signal": guard["shadow_signal"],
        "guard_decision": guard["guard_decision"],
        "guard_reason": guard["guard_reason"],
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


def print_tsv(rows: list[dict[str, Any]], *, redirect_only: bool) -> None:
    headers = [
        "wall",
        "context",
        "n",
        "status",
        "current_anchor",
        "current_residual",
        "shadow_anchor",
        "shadow_residual",
        "structural_prefix",
        "current_signal",
        "shadow_signal",
        "guard_decision",
        "guard_reason",
        "candidate_count",
    ]

    print("\t".join(headers))

    for row in rows:
        if (
            redirect_only
            and row["guard_decision"] != "would-redirect-to-shadow-anchor"
        ):
            continue

        print("\t".join(str(row[key]) for key in headers))


def filtered_rows(
    rows: list[dict[str, Any]],
    *,
    redirect_only: bool,
) -> list[dict[str, Any]]:
    if not redirect_only:
        return rows

    return [
        row
        for row in rows
        if row["guard_decision"] == "would-redirect-to-shadow-anchor"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Research-only guarded policy experiment for structural prefix traps."
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
    parser.add_argument("--include-wall-alone", action="store_true")
    parser.add_argument("--redirect-only", action="store_true")
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
                    "schema": "pet.guarded_prefix_trap_policy_experiment.v0",
                    "profile": {
                        "max_depth": args.max_depth,
                        "include_wall_alone": args.include_wall_alone,
                        "redirect_only": args.redirect_only,
                    },
                    "rows": filtered_rows(
                        rows,
                        redirect_only=args.redirect_only,
                    ),
                    "claim": (
                        "Research-only guarded policy experiment; does not "
                        "change PET routing or real anchor selection."
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_tsv(rows, redirect_only=args.redirect_only)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
