#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


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


def band_contains_move(band: dict[str, Any], move: str) -> bool:
    moves = [item.strip() for item in str(band.get("move", "")).split(",")]
    return move in moves


def band_sort_key(band: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(band.get("focus_score", 0)),
        -int(band.get("min_trigger_span", 999999)),
        int(band.get("band_width", 0)),
    )


def band_transition_for(transition: str) -> tuple[str, str]:
    if transition in {"DEC", "DEC_PATH", "DROP_PATH"}:
        return "DROP", f"{transition}-as-DROP"
    if transition in {"INC", "INC_PATH", "NEW_PATH"}:
        return "NEW", f"{transition}-as-NEW"
    return transition, transition


def choose_primary_band(bands: list[dict[str, Any]], transition: str) -> tuple[dict[str, Any] | None, str]:
    band_transition, transition_side = band_transition_for(transition)

    matching = [band for band in bands if band_contains_move(band, band_transition)]
    if matching:
        return max(matching, key=band_sort_key), transition_side

    multi = [band for band in bands if band.get("kind") == "multi-threshold"]
    if multi:
        return max(multi, key=band_sort_key), "embedded"

    if bands:
        return max(bands, key=band_sort_key), "fallback"

    return None, "unknown"


def choose_side_band(
    bands: list[dict[str, Any]],
    transition: str,
    primary_band: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if transition == "unknown":
        return None

    band_transition, _transition_side = band_transition_for(transition)

    matching = [
        band
        for band in bands
        if band is not primary_band and band_contains_move(band, band_transition)
    ]
    if not matching:
        return None

    return max(matching, key=band_sort_key)


def proposal_status(transition: str, transition_side: str) -> str:
    if transition == "unknown":
        return "weak"
    if transition_side in {"fallback", "unknown"}:
        return "weak"
    if transition_side in {
        "DEC-as-DROP",
        "INC-as-NEW",
        "DEC_PATH-as-DROP",
        "INC_PATH-as-NEW",
        "DROP_PATH-as-DROP",
        "NEW_PATH-as-NEW",
    }:
        return "partial"
    return "strong"


def proposal_reason(transition: str, transition_side: str) -> str:
    if transition == "unknown":
        return "no direct PET lens transition available"
    if transition_side in {"fallback", "unknown"}:
        return "no transition-coherent magnetic band available"
    if transition_side == "DEC-as-DROP":
        return "exponent transition mapped to DROP-like release band"
    if transition_side == "INC-as-NEW":
        return "exponent transition mapped to NEW-like pressure band"
    if transition_side == "DEC_PATH-as-DROP":
        return "exponent transition path mapped to DROP-like release band"
    if transition_side == "INC_PATH-as-NEW":
        return "exponent transition path mapped to NEW-like pressure band"
    if transition_side == "DROP_PATH-as-DROP":
        return "DROP transition path mapped to DROP-like release band"
    if transition_side == "NEW_PATH-as-NEW":
        return "NEW transition path mapped to NEW-like pressure band"
    return "transition-coherent magnetic band selected"


def suggested_probe_role(transition: str, transition_side: str) -> str:
    if transition == "DROP":
        if transition_side == "embedded":
            return "inspect embedded DROP side / structural release"
        return "inspect DROP side / lower structural release"

    if transition == "NEW":
        if transition_side == "embedded":
            return "inspect embedded NEW side / structural pressure"
        return "inspect NEW side / upper structural pressure"

    if transition == "DEC":
        return "inspect DEC exponent release through DROP-like band"

    if transition == "INC":
        return "inspect INC exponent pressure through NEW-like band"

    if transition == "DEC_PATH":
        return "inspect DEC exponent path through DROP-like band"

    if transition == "INC_PATH":
        return "inspect INC exponent path through NEW-like band"

    if transition == "DROP_PATH":
        return "inspect DROP transition path through DROP-like band"

    if transition == "NEW_PATH":
        return "inspect NEW transition path through NEW-like band"

    return "inspect unresolved transition neighborhood"


def format_band(band: dict[str, Any] | None) -> str:
    if band is None:
        return "unknown"
    return (
        f"{band.get('kind', 'unknown')} "
        f"{band.get('move', 'unknown')} "
        f"k[{band.get('k_range', 'unknown')}]"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Propose a local PET probe window from lens transition and mass-response bands."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-leaves", type=int, default=8)
    parser.add_argument("--flatten", action="store_true")
    parser.add_argument("--max-generator-count", type=int, default=20)
    parser.add_argument("--excluded-support-limit", type=int, default=16)
    parser.add_argument("--max-move-span", type=int, default=5)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_local_probe_proposal expects integers >= 1")

    transition_args = [
        sys.executable,
        "tools/pet_lens_transition.py",
        str(args.n),
        "--max-leaves",
        str(args.max_leaves),
    ]
    if args.flatten:
        transition_args.append("--flatten")

    transition_text = run_command(transition_args)

    transition = extract_value(transition_text, "transition")
    source_generator = extract_value(transition_text, "source_generator")
    target_generator = extract_value(transition_text, "target_generator")
    representative_target = extract_value(transition_text, "representative_target")

    mass_response_text = run_command(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "opaque-mass-response",
            str(args.n),
            "--max-generator-count",
            str(args.max_generator_count),
            "--excluded-support-limit",
            str(args.excluded_support_limit),
            "--max-move-span",
            str(args.max_move_span),
            "--bands",
            "--json",
        ]
    )
    mass_response = json.loads(mass_response_text)
    bands = mass_response.get("magnetic_bands", [])

    primary_band, transition_side = choose_primary_band(bands, transition)
    side_band = choose_side_band(bands, transition, primary_band)

    print("PET LOCAL PROBE PROPOSAL")
    print()
    print(f"N = {args.n}")
    print(f"transition = {transition}")
    print(f"source_generator = {source_generator}")
    print(f"target_generator = {target_generator}")
    print(f"representative_target = {representative_target}")
    print()
    print(f"primary_band = {format_band(primary_band)}")
    print(f"transition_side = {transition_side}")
    print(f"proposal_status = {proposal_status(transition, transition_side)}")
    print(f"reason = {proposal_reason(transition, transition_side)}")
    print(f"suggested_probe_role = {suggested_probe_role(transition, transition_side)}")
    print(f"candidate_window = k[{primary_band.get('k_range', 'unknown') if primary_band else 'unknown'}]")
    print(f"side_band = {format_band(side_band)}")
    if side_band:
        print(f"side_window = k[{side_band.get('k_range', 'unknown')}]")
    else:
        print("side_window = unknown")
    print()
    print("claim = PET local probe proposal only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
