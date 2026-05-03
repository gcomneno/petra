#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys


def run_tool(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, *args],
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


def find_transition(explain_text: str, target_generator: int) -> dict[str, str]:
    for line in explain_text.splitlines():
        stripped = line.strip()
        if "generator=" not in stripped:
            continue
        match = re.search(
            r"^(?P<move>[A-Z]+): .*-> N'=(?P<n>[0-9]+) generator=(?P<generator>[0-9]+)",
            stripped,
        )
        if not match:
            continue
        if int(match.group("generator")) == target_generator:
            return {
                "available": "yes",
                "move": match.group("move"),
                "representative_target": match.group("n"),
                "target_generator": match.group("generator"),
            }

    return {
        "available": "no",
        "move": "unknown",
        "representative_target": "unknown",
        "target_generator": str(target_generator),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find the PET structural transition from N to its target lens."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-leaves", type=int, default=8)
    parser.add_argument("--flatten", action="store_true")
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_lens_transition expects integers >= 1")

    candidate_args = [
        "tools/pet_lens_candidates.py",
        str(args.n),
        "--max-leaves",
        str(args.max_leaves),
    ]
    if args.flatten:
        candidate_args.append("--flatten")

    candidates = run_tool(*candidate_args)

    source_generator_raw = extract_value(candidates, "source_generator")
    target_generator_raw = extract_value(candidates, "generator")
    target_lens = extract_value(candidates, "target_lens")
    target_leaf_count = extract_value(candidates, "target_leaf_count")
    flatten_first = extract_value(candidates, "flatten_first")

    print("PET LENS TRANSITION")
    print()
    print(f"N = {args.n}")
    print(f"target_lens = {target_lens}")
    print(f"target_leaf_count = {target_leaf_count}")
    print(f"flatten_first = {flatten_first}")

    if source_generator_raw == "unknown" or target_generator_raw == "unknown":
        print("transition_available = no")
        print("reason = lens candidates did not provide source/target generators")
        print()
        print("claim = PET lens transition only; this does not factor N")
        return 0

    source_generator = int(source_generator_raw)
    target_generator = int(target_generator_raw)

    compare = run_tool(
        "-m",
        "pet.cli",
        "compare",
        str(source_generator),
        str(target_generator),
    )
    explain = run_tool(
        "-m",
        "pet.cli",
        "explain",
        str(source_generator),
    )
    transition = find_transition(explain, target_generator)

    print(f"source_generator = {source_generator}")
    print(f"target_generator = {target_generator}")
    print(f"distance = {extract_value(compare, 'distance')}")
    print(f"structural_distance = {extract_value(compare, 'structural_distance')}")
    print(f"transition_available = {transition['available']}")
    print(f"transition = {transition['move']}")
    print(f"representative_target = {transition['representative_target']}")
    print()
    print("claim = PET lens transition only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
