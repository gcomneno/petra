#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys


def run_command(args: list[str]) -> str:
    result = subprocess.run(
        args,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr)
    return result.stdout


def extract_value(text: str, key: str) -> str:
    prefix = f"{key} = "
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return "unknown"


def branch_for_transition_side(transition_side: str) -> str:
    if "DROP" in transition_side:
        return "DROP"
    if "NEW" in transition_side:
        return "NEW"
    return "unknown"


def command_text(parts: list[str]) -> str:
    return " ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a PET-guided route from local probe proposal to classic handoff."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-leaves", type=int, default=8)
    parser.add_argument("--max-generator-count", type=int, default=20)
    parser.add_argument("--excluded-support-limit", type=int, default=16)
    parser.add_argument("--max-move-span", type=int, default=5)
    parser.add_argument("--handoff-radius", type=int, default=100)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_classic_handoff_route expects integers >= 1")

    proposal = run_command(
        [
            sys.executable,
            "tools/pet_local_probe_proposal.py",
            str(args.n),
            "--max-leaves",
            str(args.max_leaves),
            "--max-generator-count",
            str(args.max_generator_count),
            "--excluded-support-limit",
            str(args.excluded_support_limit),
            "--max-move-span",
            str(args.max_move_span),
        ]
    )

    transition = extract_value(proposal, "transition")
    transition_side = extract_value(proposal, "transition_side")
    proposal_status = extract_value(proposal, "proposal_status")
    primary_band = extract_value(proposal, "primary_band")
    side_band = extract_value(proposal, "side_band")

    branch = branch_for_transition_side(transition_side)

    print("PET CLASSIC HANDOFF ROUTE")
    print()
    print(f"N = {args.n}")
    print(f"proposal_transition = {transition}")
    print(f"proposal_transition_side = {transition_side}")
    print(f"proposal_status = {proposal_status}")
    print(f"proposal_primary_band = {primary_band}")
    print(f"proposal_side_band = {side_band}")

    if branch == "unknown":
        print()
        print("route_status = unavailable")
        print("reason = local probe proposal did not identify a NEW/DROP branch")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    focused = run_command(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "opaque-focused-peel",
            str(args.n),
            "--max-generator-count",
            str(args.max_generator_count),
            "--excluded-support-limit",
            str(args.excluded_support_limit),
            "--max-move-span",
            str(args.max_move_span),
            "--fork-follow",
            branch,
            "--classic-handoff",
            "--handoff-radius",
            str(args.handoff_radius),
            "--json",
        ]
    )
    focused_json = json.loads(focused)
    followup = focused_json.get("peel_fork_followup") or {}

    source_window = followup.get("source_window") or {}
    next_kind = source_window.get("source_kind", "unknown")
    next_move = source_window.get("source_move", "unknown")
    target_edge_hint = followup.get("target_edge_hint", "unknown")
    recommended_next_lens = followup.get("recommended_next_lens", "unknown")

    if not followup.get("available"):
        print()
        print("route_status = unavailable")
        print(f"route_branch = {branch}")
        print(f"reason = {followup.get('reason', 'fork follow-up lens is not available')}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    suggested_parts = [
        "python",
        "-m",
        "pet.cli",
        "opaque-focused-peel",
        str(args.n),
        "--max-generator-count",
        str(args.max_generator_count),
        "--excluded-support-limit",
        str(args.excluded_support_limit),
        "--max-move-span",
        str(args.max_move_span),
        "--move",
        str(next_move),
        "--kind",
        str(next_kind),
        "--cut",
        "--peel-step",
        "--slice",
        "--lift",
        "--decode",
        "--center-lens",
        "--realize",
        "--classic-handoff",
        "--handoff-radius",
        str(args.handoff_radius),
    ]

    print()
    print("route_status = available")
    print("route_kind = fork-follow-rescan")
    print(f"route_branch = {branch}")
    print(f"source_branch = {followup.get('source_branch', 'unknown')}")
    print(f"next_move = {next_move}")
    print(f"next_kind = {next_kind}")
    print(f"source_window = k[{source_window.get('k_range', 'unknown')}]")
    print(f"target_edge_hint = {target_edge_hint}")
    print(f"recommended_next_lens = {recommended_next_lens}")
    print()
    print(f"suggested_command = {command_text(suggested_parts)}")
    print()
    print("claim = PET classic handoff route only; classic verification required")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
