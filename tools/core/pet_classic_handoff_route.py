#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from io import StringIO
from pathlib import Path


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



def monster_route_summary(n: int) -> dict[str, str]:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_shadow_monster_router.py",
            str(n),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip().splitlines()
        return {
            "monster_route_status": "unavailable",
            "monster_route_error": message[0] if message else "unknown router error",
        }

    rows = list(csv.DictReader(StringIO(result.stdout), delimiter="\t"))
    if len(rows) != 1:
        return {
            "monster_route_status": "unavailable",
            "monster_route_error": f"expected 1 router row, got {len(rows)}",
        }

    row = rows[0]
    return {
        "monster_route_status": "available",
        "monster_class": row.get("monster_class", "-"),
        "recommended_strategy": row.get("recommended_strategy", "-"),
        "route_confidence": row.get("route_confidence", "-"),
        "sigma_stability_status": row.get("sigma_stability_status", "-"),
        "sigma_depth_generator": row.get("sigma_depth_generator", "-"),
        "chunk_failure_mode": row.get("chunk_failure_mode", "-"),
        "chunk_best_merge_generator": row.get("chunk_best_merge_generator", "-"),
    }


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
    parser.add_argument("--operator-depth", default="auto")
    parser.add_argument(
        "--blade-window",
        choices=("full", "active"),
        default="full",
        help="Proposal race candidate window policy.",
    )
    parser.add_argument(
        "--proposal-file",
        type=Path,
        help="Reuse a precomputed pet_local_probe_proposal output instead of recomputing it.",
    )
    parser.add_argument(
        "--include-monster-route",
        action="store_true",
        help="Append PET shadow monster router diagnostics to the handoff output.",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_classic_handoff_route expects integers >= 1")

    if args.proposal_file is None:
        proposal = run_command(
            [
                sys.executable,
                "tools/pet_local_probe_proposal.py",
                str(args.n),
                "--operator-depth",
                args.operator_depth,
                "--backbone-selection",
                "race",
                "--blade-window",
                args.blade_window,
            ]
        )
    else:
        proposal = args.proposal_file.read_text(encoding="utf-8")

    transition = extract_value(proposal, "transition")
    transition_side = extract_value(proposal, "transition_side")
    proposal_status = extract_value(proposal, "proposal_status")
    primary_band = extract_value(proposal, "primary_band")
    side_band = extract_value(proposal, "side_band")
    selected_backbone_order = extract_value(proposal, "selected_backbone_order")
    race_shape_diagnostic = extract_value(proposal, "race_shape_diagnostic")
    selected_operator_sequence = extract_value(proposal, "selected_operator_sequence")
    composite_border_hint = extract_value(proposal, "composite_border_hint")
    decimal_rigid_border_score = extract_value(proposal, "decimal_rigid_border_score")
    decimal_rigid_border_hint = extract_value(proposal, "decimal_rigid_border_hint")
    policy = classic_probe_policy(race_shape_diagnostic)
    monster_route = (
        monster_route_summary(args.n)
        if args.include_monster_route
        else {"monster_route_status": "skipped"}
    )

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
    print(f"proposal_composite_border_hint = {composite_border_hint}")
    print(f"proposal_decimal_rigid_border_score = {decimal_rigid_border_score}")
    print(f"proposal_decimal_rigid_border_hint = {decimal_rigid_border_hint}")
    print(f"proposal_operator_depth = {args.operator_depth}")
    print(f"proposal_blade_window = {args.blade_window}")
    print(f"classic_probe_policy = {policy}")
    if decimal_rigid_border_hint == "yes":
        print("route_note = decimal rigid border detected; route-only benchmark may be expensive")
    print()
    if args.include_monster_route:
        print("PET shadow monster route")
        print(f"monster_route_status = {monster_route['monster_route_status']}")
        if monster_route["monster_route_status"] == "available":
            print(f"monster_class = {monster_route['monster_class']}")
            print(f"recommended_strategy = {monster_route['recommended_strategy']}")
            print(f"route_confidence = {monster_route['route_confidence']}")
            print(f"sigma_stability_status = {monster_route['sigma_stability_status']}")
            print(f"sigma_depth_generator = {monster_route['sigma_depth_generator']}")
            print(f"chunk_failure_mode = {monster_route['chunk_failure_mode']}")
            print(f"chunk_best_merge_generator = {monster_route['chunk_best_merge_generator']}")
        else:
            print(f"monster_route_error = {monster_route.get('monster_route_error', '-')}")
        print()
    route_warning = None
    route_note = None
    if monster_route.get("monster_route_status") == "available":
        monster_class = monster_route.get("monster_class", "unknown")
        if monster_class == "deceptive-stable-sigma":
            route_warning = (
                "sigma support appears stable but locally deceptive; avoid trusting sigma generator directly"
            )
        elif monster_class == "local-preserved-shadow-coherent":
            route_note = (
                "local lambda preservation detected; sigma and local chunk diagnostics agree"
            )
        elif monster_class == "local-preserved-sigma-floor-risk":
            route_warning = (
                "local PET generator appears preserved, but sigma support may be collapsed to a low floor"
            )
        elif monster_class == "fragile-shadow-field":
            route_warning = (
                "sigma support is depth-fragile; treat route as conservative only"
            )


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
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "power-like-local-check":
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
        print("route_kind = power-like-local-check")
        print("reason = narrow deep PET shape; run minimal classic check for repeated small factors")
        print(f"suggested_command = {command_text(suggested_parts)}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "backbone-wide-structural-check":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            selected_backbone_order,
        ]
        print("route_status = available")
        print("route_kind = backbone-wide-structural-check")
        print("reason = wide exact PET shape; run classic probe bounded by selected backbone order")
        print(f"suggested_command = {command_text(suggested_parts)}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "operator-neighborhood-check":
        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            selected_backbone_order,
        ]
        print("route_status = available")
        print("route_kind = operator-neighborhood-check")
        print("reason = near PET shape; run classic probe bounded by selected operator neighborhood")
        print(f"suggested_command = {command_text(suggested_parts)}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    if policy == "complex-border-route-needed":
        lens_transition = run_command(
            [
                sys.executable,
                "tools/pet_lens_transition.py",
                str(args.n),
                "--max-leaves",
                str(args.max_leaves),
            ]
        )
        transition_available = extract_value(lens_transition, "transition_available")
        transition = extract_value(lens_transition, "transition")

        suggested_parts = [
            "python",
            "-m",
            "pet.cli",
            "opaque-probe",
            str(args.n),
            "--trial-limit",
            "20",
        ]
        print("route_status = available")
        if (
            composite_border_hint == "balanced-flat-border"
            and transition_available == "yes"
            and transition == "DROP"
        ):
            print("route_kind = balanced-flat-border-lens-drop-classic-probe")
            print("reason = balanced flat PET border has a DROP lens transition; run conservative classic residual probe")
        elif transition_available == "yes" and transition == "DROP":
            print("route_kind = complex-border-lens-drop-classic-probe")
            print("reason = complex border PET shape has a DROP lens transition; run conservative classic residual probe")
        else:
            print("route_kind = complex-border-classic-probe")
            print("reason = complex border PET shape; run conservative classic residual probe")
        print(f"suggested_command = {command_text(suggested_parts)}")
        if route_note is not None:
            print(f"route_note = {route_note}")
        if route_warning is not None:
            print(f"route_warning = {route_warning}")
        print()
        print("claim = PET classic handoff route only; classic verification required")
        return 0

    print("route_status = unavailable")
    print(f"route_kind = {policy}")
    print("reason = classic probe policy route not implemented yet")
    if route_note is not None:
        print(f"route_note = {route_note}")
    if route_warning is not None:
        print(f"route_warning = {route_warning}")
    print()
    print("claim = PET classic handoff route only; classic verification required")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
