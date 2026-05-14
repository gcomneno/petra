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


def run_residual_route_command(
    n: int,
    max_depth: int,
    *,
    auto_flat_k_scan: bool = False,
    auto_shape_family_scan: bool = False,
) -> str:
    command = [
        sys.executable,
        str(ROUTE_TOOL),
        str(n),
        "--max-depth",
        str(max_depth),
    ]

    if auto_flat_k_scan:
        command.append("--auto-flat-k-scan")

    if auto_shape_family_scan:
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


def run_residual_route(args: argparse.Namespace) -> str:
    return run_residual_route_command(
        args.n,
        args.max_depth,
        auto_flat_k_scan=args.auto_flat_k_scan,
        auto_shape_family_scan=args.auto_shape_family_scan,
    )


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


def active_completion_signal(row: dict[str, str]) -> str:
    final_status = row.get("residual_final_status", "-")

    if final_status.startswith("solved-by-"):
        return "active-complete"

    if final_status == "stopped-at-atomic-leaf":
        return "active-prime-leaf"

    if final_status.startswith("partial-factorization-by-"):
        return "active-partial-expandable"

    if final_status == "flat-k-scan-required":
        return "inactive-flat-k-required"

    if final_status == "shape-family-scan-required":
        return "inactive-shape-family-required"

    return "blocked"


def summarize_route(
    n: int,
    max_depth: int,
    *,
    auto_flat_k_scan: bool = False,
    auto_shape_family_scan: bool = False,
) -> dict[str, str]:
    output = run_residual_route_command(
        n,
        max_depth,
        auto_flat_k_scan=auto_flat_k_scan,
        auto_shape_family_scan=auto_shape_family_scan,
    )
    values = parse_key_values(output)

    return {
        "status": latest(values, "residual_descent_status"),
        "terminal_residual": latest(values, "terminal_residual"),
        "residual_reduction_chain": latest(values, "residual_reduction_chain"),
    }


def route_completed(summary: dict[str, str]) -> bool:
    return (
        summary.get("status") == "complete"
        and summary.get("terminal_residual") == "1"
    )


def completion_delta(
    row: dict[str, str],
    comparison: dict[str, dict[str, str] | str],
) -> str:
    final_status = row.get("residual_final_status", "-")

    if (
        final_status.startswith("solved-by-")
        or final_status == "stopped-at-atomic-leaf"
    ):
        return "unchanged-complete"

    flat_k = comparison["flat_k"]
    shape_family = comparison["shape_family"]

    if isinstance(flat_k, dict) and route_completed(flat_k):
        return "opens-with-flat-k"

    if isinstance(shape_family, dict) and route_completed(shape_family):
        return "opens-with-shape-family"

    return "remains-blocked"


def compare_expanded_profile(
    row: dict[str, str],
    args: argparse.Namespace,
) -> dict[str, dict[str, str] | str]:
    residual = row.get("residual", "-")

    if not residual.isdigit():
        return {
            "flat_k": {
                "status": "not-runnable",
                "terminal_residual": "-",
                "residual_reduction_chain": "-",
            },
            "shape_family": {
                "status": "not-runnable",
                "terminal_residual": "-",
                "residual_reduction_chain": "-",
            },
            "completion_delta": "remains-blocked",
        }

    residual_n = int(residual)

    comparison: dict[str, dict[str, str] | str] = {
        "flat_k": summarize_route(
            residual_n,
            args.max_depth,
            auto_flat_k_scan=True,
        ),
        "shape_family": summarize_route(
            residual_n,
            args.max_depth,
            auto_shape_family_scan=True,
        ),
    }
    comparison["completion_delta"] = completion_delta(row, comparison)

    return comparison


ACTIVE_SIGNAL_PRIORITY = {
    "active-complete": 0,
    "active-prime-leaf": 1,
    "active-partial-expandable": 2,
    "inactive-flat-k-required": 3,
    "inactive-shape-family-required": 4,
    "blocked": 9,
}


COMPLETION_DELTA_PRIORITY = {
    "unchanged-complete": 0,
    "opens-with-flat-k": 1,
    "opens-with-shape-family": 2,
    "remains-blocked": 9,
}


CLASSIFICATION_PRIORITY = {
    "completion-friendly": 0,
    "prime-leaf-friendly": 1,
    "expandable-with-active-mode": 2,
    "trap-door-candidate": 4,
    "selected-trap-door-candidate": 4,
    "requires-shape-family": 5,
    "handoff-error": 9,
    "unclassified": 9,
}


def parse_selection_score(raw: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in raw.split(","))
    except ValueError:
        return (999, 999, 999, 999)


def completion_aware_rank_key(row: dict[str, str]) -> tuple[Any, ...]:
    comparison = row.get("expanded_profile_comparison", {})
    completion_delta_value = "remains-blocked"

    if isinstance(comparison, dict):
        completion_delta_value = str(
            comparison.get("completion_delta", "remains-blocked")
        )

    return (
        ACTIVE_SIGNAL_PRIORITY.get(row.get("active_completion_signal", "blocked"), 9),
        COMPLETION_DELTA_PRIORITY.get(completion_delta_value, 9),
        CLASSIFICATION_PRIORITY.get(row.get("classification", "unclassified"), 9),
        parse_selection_score(row.get("selection_score", "-")),
    )


def ranking_reason(
    suggested: dict[str, str] | None,
    selected: dict[str, str] | None,
) -> str:
    if suggested is None:
        return "no-depth-0-candidates"

    if selected is None:
        return "no-current-selected-anchor"

    if suggested["anchor"] == selected["anchor"]:
        return "current-selection-matches-completion-aware-shadow-ranking"

    return (
        f"{suggested['active_completion_signal']} beats "
        f"{selected['active_completion_signal']}"
    )


def compare_ranking_policy(
    candidates: list[dict[str, str]],
    selected_anchor: str,
) -> dict[str, Any]:
    ranked = sorted(candidates, key=completion_aware_rank_key)

    for index, row in enumerate(ranked, start=1):
        row["completion_aware_rank"] = str(index)

    suggested = ranked[0] if ranked else None
    selected = next(
        (row for row in candidates if row["anchor"] == selected_anchor),
        None,
    )

    suggested_anchor = suggested["anchor"] if suggested else "-"
    suggested_residual = suggested["residual"] if suggested else "-"
    selected_residual = selected["residual"] if selected else "-"

    return {
        "policy": "research-shadow-active-completion-v0",
        "current_selected_anchor": selected_anchor,
        "current_selected_residual": selected_residual,
        "suggested_anchor": suggested_anchor,
        "suggested_residual": suggested_residual,
        "changed_selection": (
            suggested is not None
            and selected_anchor != "-"
            and suggested_anchor != selected_anchor
        ),
        "reason": ranking_reason(suggested, selected),
    }


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
        row["active_completion_signal"] = active_completion_signal(row)

        if args.compare_expanded_profile or args.compare_ranking_policy:
            row["expanded_profile_comparison"] = compare_expanded_profile(row, args)

        if row["anchor"] == selected_anchor:
            selected_residual = row["residual"]

    result: dict[str, Any] = {
        "schema": "pet.completion_aware_residual_probe.v0",
        "n": args.n,
        "profile": {
            "max_depth": args.max_depth,
            "auto_flat_k_scan": args.auto_flat_k_scan,
            "auto_shape_family_scan": args.auto_shape_family_scan,
            "compare_expanded_profile": args.compare_expanded_profile,
            "compare_ranking_policy": args.compare_ranking_policy,
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

    if args.compare_ranking_policy:
        result["ranking_policy_comparison"] = compare_ranking_policy(
            candidates,
            selected_anchor,
        )

    return result


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

    ranking = probe.get("ranking_policy_comparison")
    if ranking:
        print()
        print("ranking_policy_comparison:")
        print(f"ranking_policy = {ranking['policy']}")
        print(f"current_selected_anchor = {ranking['current_selected_anchor']}")
        print(f"current_selected_residual = {ranking['current_selected_residual']}")
        print(f"completion_aware_suggested_anchor = {ranking['suggested_anchor']}")
        print(f"completion_aware_suggested_residual = {ranking['suggested_residual']}")
        print(f"changed_selection = {ranking['changed_selection']}")
        print(f"ranking_reason = {ranking['reason']}")

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
        print(
            f"candidate_{row['index']}_active_completion_signal = "
            f"{row['active_completion_signal']}"
        )

        completion_aware_rank = row.get("completion_aware_rank")
        if completion_aware_rank:
            print(
                f"candidate_{row['index']}_completion_aware_rank = "
                f"{completion_aware_rank}"
            )

        comparison = row.get("expanded_profile_comparison")
        if comparison:
            flat_k = comparison["flat_k"]
            shape_family = comparison["shape_family"]
            print(
                f"candidate_{row['index']}_expanded_flat_k_status = "
                f"{flat_k['status']}"
            )
            print(
                f"candidate_{row['index']}_expanded_flat_k_terminal_residual = "
                f"{flat_k['terminal_residual']}"
            )
            print(
                f"candidate_{row['index']}_expanded_shape_family_status = "
                f"{shape_family['status']}"
            )
            print(
                f"candidate_{row['index']}_expanded_shape_family_terminal_residual = "
                f"{shape_family['terminal_residual']}"
            )
            print(
                f"candidate_{row['index']}_completion_delta = "
                f"{comparison['completion_delta']}"
            )


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
    parser.add_argument(
        "--compare-expanded-profile",
        action="store_true",
        help=(
            "Compare each depth-0 candidate residual against expanded research "
            "profiles without changing candidate selection."
        ),
    )
    parser.add_argument(
        "--compare-ranking-policy",
        action="store_true",
        help=(
            "Compare current anchor selection with a research-only "
            "completion-aware shadow ranking."
        ),
    )
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
