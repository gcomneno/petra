#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from collections import Counter


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


def next_prime_after(n: int) -> int:
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


def prime_support(n: int) -> set[int]:
    support: set[int] = set()
    candidate = 2
    current = n

    while candidate * candidate <= current:
        if current % candidate == 0:
            support.add(candidate)
            while current % candidate == 0:
                current //= candidate
        candidate += 1 if candidate == 2 else 2

    if current > 1:
        support.add(current)

    return support


def digit_count(n: int, base: int) -> int:
    if n < 1:
        return 1

    count = 0
    current = n
    while current:
        current //= base
        count += 1

    return count


def digits_in_base(n: int, base: int) -> list[int]:
    if n == 0:
        return [0]

    digits: list[int] = []
    current = n
    while current:
        digits.append(current % base)
        current //= base

    return list(reversed(digits))


def primorial_expand_to_digits(generator: int, target_digits: int, base: int) -> tuple[int, list[int]]:
    expanded = generator
    used_primes: list[int] = []
    support = prime_support(generator)

    prime = 2
    while digit_count(expanded, base) < target_digits:
        if prime not in support:
            expanded *= prime
            used_primes.append(prime)
            support.add(prime)

        prime = next_prime_after(prime)

    return expanded, used_primes


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def digit_band_bounds(digits: int, base: int) -> tuple[int, int]:
    lower = base ** (digits - 1)
    upper = (base ** digits) - 1
    return lower, upper


def band_position(n: int, lower: int, upper: int) -> float:
    if upper == lower:
        return 0.0
    return (n - lower) / (upper - lower)


def weight_alignment(relative_gap: float) -> str:
    if relative_gap <= 0.10:
        return "close"
    if relative_gap <= 0.50:
        return "loose"
    return "far"


def weight_direction(weight_gap: int) -> str:
    if weight_gap > 0:
        return "lighter"
    if weight_gap < 0:
        return "heavier"
    return "exact"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe PET lens mass and digit-shadow metrics without classic verification."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--base", type=int, default=10)
    parser.add_argument("--max-leaves", type=int, default=8)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_lens_mass_probe expects integers >= 1")
    if args.base < 2:
        raise SystemExit("--base expects integers >= 2")

    candidates_text = run_tool(
        "tools/pet_lens_candidates.py",
        str(args.n),
        "--max-leaves",
        str(args.max_leaves),
    )

    source_generator_raw = extract_value(candidates_text, "source_generator")
    source_signature_raw = extract_value(candidates_text, "source_signature")
    target_lens = extract_value(candidates_text, "target_lens")
    target_leaf_count = extract_value(candidates_text, "target_leaf_count")

    source_generator = int(source_generator_raw)
    source_signature = ast.literal_eval(source_signature_raw)

    n_digits = digit_count(args.n, args.base)
    source_generator_digits = digit_count(source_generator, args.base)
    expanded_generator, expansion_primes = primorial_expand_to_digits(
        source_generator,
        n_digits,
        args.base,
    )
    expanded_generator_digits = digit_count(expanded_generator, args.base)

    digits = digits_in_base(args.n, args.base)
    counts = Counter(digits)
    unique_digit_count = len(counts)
    max_digit_frequency = max(counts.values())
    repetition_ratio = max_digit_frequency / len(digits)
    all_digits_same = unique_digit_count == 1
    palindrome = digits == list(reversed(digits))
    digit_aligned = expanded_generator_digits == n_digits
    band_min, band_max = digit_band_bounds(n_digits, args.base)
    n_band_position = band_position(args.n, band_min, band_max)
    expanded_band_position = band_position(expanded_generator, band_min, band_max)
    weight_gap = args.n - expanded_generator
    weight_ratio = expanded_generator / args.n
    relative_weight_gap = abs(weight_gap) / args.n
    weight_alignment_label = weight_alignment(relative_weight_gap)
    weight_direction_label = weight_direction(weight_gap)

    print("PET LENS MASS PROBE")
    print()
    print(f"N = {args.n}")
    print(f"base = {args.base}")
    print(f"n_digits = {n_digits}")
    print()
    print(f"source_generator = {source_generator}")
    print(f"source_generator_digits = {source_generator_digits}")
    print(f"source_signature = {source_signature}")
    print()
    print(f"target_lens = {target_lens}")
    print(f"target_leaf_count = {target_leaf_count}")
    print()
    print(f"primorial_expanded_generator = {expanded_generator}")
    print(f"primorial_expanded_digits = {expanded_generator_digits}")
    print(f"expansion_primes = {expansion_primes if expansion_primes else 'none'}")
    print(f"digit_aligned = {yes_no(digit_aligned)}")
    print()
    print(f"digit_band_min = {band_min}")
    print(f"digit_band_max = {band_max}")
    print(f"n_band_position = {n_band_position:.3f}")
    print(f"expanded_band_position = {expanded_band_position:.3f}")
    print(f"weight_ratio = {weight_ratio:.3f}")
    print(f"weight_gap = {weight_gap}")
    print(f"relative_weight_gap = {relative_weight_gap:.3f}")
    print(f"weight_alignment = {weight_alignment_label}")
    print(f"weight_direction = {weight_direction_label}")
    print()
    print(f"digit_unique_count = {unique_digit_count}")
    print(f"max_digit_frequency = {max_digit_frequency}")
    print(f"digit_repetition_ratio = {repetition_ratio:.3f}")
    print(f"all_digits_same = {yes_no(all_digits_same)}")
    print(f"palindrome = {yes_no(palindrome)}")
    print()
    if digit_aligned:
        print("mass_note = expanded generator matches N digit count")
    else:
        print("mass_note = expanded generator does not match N digit count")
    if all_digits_same:
        print("shadow_note = repeated digits detected in base representation")
    elif palindrome:
        print("shadow_note = palindromic digit shadow detected")
    else:
        print("shadow_note = no strong digit repetition shadow detected")
    print()
    print("claim = PET lens mass/shadow probe only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
