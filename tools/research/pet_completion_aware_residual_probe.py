#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
ROUTE_TOOL = ROOT_DIR / "tools" / "core" / "pet_residual_descent_route.py"

KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(.*)$")
CANDIDATE_RE = re.compile(r"^depth_0_anchor_candidate_(\d+)(?:_(.*))?$")


def parse_key_values(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}

    for line in text.splitlines():
        match = KEY_VALUE_RE.match(line.strip())

        if not match:
            continue

        key, value = match.groups()
        values.setdefault(key, []).append(value.strip())

    return values


def latest(values: dict[str, list[str]], key: str, default: str = "-") -> str:
    found = values.get(key)

    if not found:
        return default

    return found[-1]


def run_residual_route(args: argparse.Namespace) -> str:
    command = [
        sys.executable,
        str(ROUTE_TOOL),
        str(args.n),
        "--max-depth",
        str(args.max_depth),
    ]

    if args.auto_flat_k_scan:
        command.append("--auto-flat-k-scan")

    if args.auto_shape_family_scan:
        command.append("--auto-shape-family-scan")

    result = subprocess.run(
        command,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"residual route failed: {detail}")

    return result.stdout


def classify_candidate(row: dict[str, str], selected_anchor: str) -> str:
    final_status = row.get("residual_final_status", "-")
    anchor = row.get("anchor", "-")

    if final_status.startswith("solved-by-"):
        return "completion-friendly"

    if final_status == "stopped-at-atomic-leaf":
        return "prime-leaf-friendly"

    if final_status == "flat-k-scan-required":
        if anchor == selected_anchor:
            return "selected-trap-door-candidate"
        return "trap-door-candidate"

    if final_status == "shape-family-scan-required":
        return "requires-shape-family"

    if final_status.startswith("partial-factorization-by-"):
        return "expandable-with-active-mode"

    if final_status == "handoff-error":
        return "handoff-error"

    return "unclassified"


def parse_depth_zero_candidates(values: dict[str, list[str]]) -> list[dict[str, str]]:
    candidate_indexes: set[int] = set()

    for key in values:
        match = CANDIDATE_RE.match(key)

        if match:
            candidate_indexes.add(int(match.group(1)))

    candidates: list[dict[str, str]] = []

    for index in sorted(candidate_indexes):
        prefix = f"depth_0_anchor_candidate_{index}"
        candidates.append(
            {
                "index": str(index),
                "anchor": latest(values, prefix),
                "residual": latest(values, f"{prefix}_residual"),
                "residual_signature": latest(values, f"{prefix}_residual_signature"),
                "residual_policy": latest(values, f"{prefix}_residual_policy"),
                "residual_execution": latest(values, f"{prefix}_residual_execution"),
                "residual_final_status": latest(
                    values,
                    f"{prefix}_residual_final_status",
                ),
                "selection_score": latest(values, f"{prefix}_selection_score"),
            }
        )

    return candidates


def build_probe(args: argparse.Namespace) -> dict[str, Any]:
    route_output = run_residual_route(args)
    values = parse_key_values(route_output)

    selected_anchor = latest(values, "depth_0_selected_anchor_factor")
    selected_residual = "-"

    candidates = parse_depth_zero_candidates(values)

    for row in candidates:
        row["classification"] = classify_candidate(row, selected_anchor)

        if row["anchor"] == selected_anchor:
            selected_residual = row["residual"]

    return {
        "schema": "pet.completion_aware_residual_probe.v0",
        "n": args.n,
        "profile": {
            "max_depth": args.max_depth,
            "auto_flat_k_scan": args.auto_flat_k_scan,
            "auto_shape_family_scan": args.auto_shape_family_scan,
        },
        "selected_anchor": selected_anchor,
        "selected_residual": selected_residual,
        "status": latest(values, "residual_descent_status"),
        "residual_reduction_chain": latest(values, "residual_reduction_chain"),
        "terminal_residual": latest(values, "terminal_residual"),
        "candidates": candidates,
        "claim": (
            "Research-only probe; observes current residual candidate ranking "
            "without changing PET routing or CLI defaults."
        ),
    }


def print_text(probe: dict[str, Any]) -> None:
    print("PET COMPLETION-AWARE RESIDUAL PROBE")
    print()
    print(f"N = {probe['n']}")
    print(f"status = {probe['status']}")
    print(f"selected_anchor = {probe['selected_anchor']}")
    print(f"selected_residual = {probe['selected_residual']}")
    print(f"residual_reduction_chain = {probe['residual_reduction_chain']}")
    print(f"terminal_residual = {probe['terminal_residual']}")
    print(f"claim = {probe['claim']}")
    print()
    print("candidates:")

    for row in probe["candidates"]:
        print(f"candidate_{row['index']}_anchor = {row['anchor']}")
        print(f"candidate_{row['index']}_residual = {row['residual']}")
        print(
            f"candidate_{row['index']}_residual_signature = "
            f"{row['residual_signature']}"
        )
        print(
            f"candidate_{row['index']}_residual_final_status = "
            f"{row['residual_final_status']}"
        )
        print(f"candidate_{row['index']}_selection_score = {row['selection_score']}")
        print(f"candidate_{row['index']}_classification = {row['classification']}")


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Research-only probe for completion-aware residual descent candidates."
        ),
    )
    parser.add_argument("n", type=positive_int)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--auto-flat-k-scan", action="store_true")
    parser.add_argument("--auto-shape-family-scan", action="store_true")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    probe = build_probe(args)

    if args.json:
        print(json.dumps(probe, indent=2, sort_keys=True))
    else:
        print_text(probe)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
