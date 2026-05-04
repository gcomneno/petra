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


def classic_probe_policy(shape_diagnostic: str) -> str:
    return {
        "atomic-exact": "primality-check-only",
        "narrow-deep": "power-like-local-check",
        "wide-exact": "backbone-wide-structural-check",
        "near-shape": "operator-neighborhood-check",
        "complex-border": "complex-border-route-needed",
    }.get(shape_diagnostic, "route-needed")


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
            "--operator-depth",
            "auto",
            "--backbone-selection",
            "race",
        ]
    )

    transition = extract_value(proposal, "transition")
    transition_side = extract_value(proposal, "transition_side")
    proposal_status = extract_value(proposal, "proposal_status")
    primary_band = extract_value(proposal, "primary_band")
    side_band = extract_value(proposal, "side_band")
    selected_backbone_order = extract_value(proposal, "selected_backbone_order")
    race_shape_diagnostic = extract_value(proposal, "race_shape_diagnostic")
    selected_operator_sequence = extract_value(proposal, "selected_operator_sequence")
    policy = classic_probe_policy(race_shape_diagnostic)

    print("PET CLASSIC HANDOFF ROUTE")
    print()
    print(f"N = {args.n}")
    print(f"proposal_transition = {transition}")
    print(f"proposal_transition_side = {transition_side}")
    print(f"proposal_status = {proposal_status}")
    print(f"proposal_primary_band = {primary_band}")
    print(f"proposal_side_band = {side_band}")
    print(f"proposal_selected_backbone_order = {selected_backbone_order}")
    print(f"proposal_race_shape_diagnostic = {race_shape_diagnostic}")
    print(f"proposal_selected_operator_sequence = {selected_operator_sequence}")
    print(f"classic_probe_policy = {policy}")
    print()

    if policy == "primality-check-only":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            "2",
        ]
        print("route_status = available")
        print("route_kind = primality-check-only")
        print("reason = atomic PET shape; run minimal classic residual/primality probe")
        print(f"suggested_command = {command_text(suggested_parts)}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    print("route_status = unavailable")
    print(f"route_kind = {policy}")
    print("reason = classic probe policy route not implemented yet")
    print()
    print("claim = PET classic handoff route only; classic verification required")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
