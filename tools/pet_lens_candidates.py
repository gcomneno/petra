#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys

from pet.core import shape_signature_dict


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


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    candidate = 3
    while candidate * candidate <= n:
        if n % candidate == 0:
            return False
        candidate += 2
    return True


def first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1 if candidate == 2 else 2
    return primes


def product(values: list[int]) -> int:
    out = 1
    for value in values:
        out *= value
    return out


def flat_shape_text(leaves: int) -> str:
    return "(" + ", ".join("()" for _ in range(leaves)) + ")"


def flat_shape_signature(leaves: int) -> list[list]:
    return [[] for _ in range(leaves)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate PET structural lens candidates from pet_lens_hint."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--max-leaves", type=int, default=8)
    parser.add_argument("--flatten", action="store_true")
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_lens_candidates expects integers >= 1")

    hint_args = [
        "tools/pet_lens_hint.py",
        str(args.n),
        "--max-leaves",
        str(args.max_leaves),
        "--summary",
    ]
    if args.flatten:
        hint_args.append("--flatten")

    hint = run_tool(*hint_args)

    target_lens = extract_value(hint, "target_lens")
    target_leaf_count_raw = extract_value(hint, "target_leaf_count")
    blade_index = extract_value(hint, "blade_index")
    flatten_first = extract_value(hint, "flatten_first")

    source_signature = shape_signature_dict(args.n)

    print("PET LENS CANDIDATES")
    print()
    print(f"N = {args.n}")
    print(f"source_generator = {source_signature['generator']}")
    print(f"source_signature = {source_signature['signature']}")
    print(f"blade_index = {blade_index}")
    print(f"target_lens = {target_lens}")
    print(f"target_leaf_count = {target_leaf_count_raw}")
    print(f"flatten_first = {flatten_first}")
    print()

    if target_leaf_count_raw == "unknown" or target_lens == "none":
        print("candidate_available = no")
        print("reason = pet_lens_hint did not produce a proper target lens")
        print()
        print("claim = PET lens candidates only; this does not factor N")
        return 0

    target_leaf_count = int(target_leaf_count_raw)
    primes = first_primes(target_leaf_count)
    generator = product(primes)

    print("Target structural lens")
    print(f"  shape = {flat_shape_text(target_leaf_count)}")
    print(f"  signature = {flat_shape_signature(target_leaf_count)}")
    print(f"  generator = {generator}")
    print(f"  generator_factorization = {' * '.join(map(str, primes))}")
    print()
    print("Candidate interpretation")
    print("  The generator is the minimal PET representative of the target lens shape.")
    print("  It is not asserted to be an arithmetic factor of N.")
    print("  It tells the next PET-local probe which structural form to prefer.")
    print()
    print("claim = PET lens candidates only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
