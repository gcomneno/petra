#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from math import prod

from pet.algebra import distance, structural_distance
from pet.core import encode, shape_signature_dict


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


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


def digit_count(n: int, base: int) -> int:
    count = 0
    current = n

    while current:
        current //= base
        count += 1

    return max(1, count)


def digits_in_base(n: int, base: int) -> list[int]:
    if n == 0:
        return [0]

    digits: list[int] = []
    current = n

    while current:
        digits.append(current % base)
        current //= base

    return list(reversed(digits))


def digit_shadow_band_bounds(digits: int, base: int) -> tuple[int, int]:
    lower = 0
    upper = (base ** digits) - 1
    return lower, upper


def digit_shadow_position(n: int, lower: int, upper: int) -> float:
    if upper == lower:
        return 0.0
    return (n - lower) / (upper - lower)


def digit_shadow_zone(position: float) -> str:
    if position < 1 / 3:
        return "low"
    if position < 2 / 3:
        return "mid"
    return "high"


def structural_mass(signature: list) -> int:
    return len(signature) + sum(
        structural_mass(child)
        for child in signature
        if isinstance(child, list)
    )


def structural_mass(signature: list) -> int:
    return len(signature) + sum(
        structural_mass(child)
        for child in signature
        if isinstance(child, list)
    )


def shape_fit(n_signature: list, backbone_signature: list) -> str:
    if n_signature == backbone_signature:
        return "backbone-matches"

    n_mass = structural_mass(n_signature)
    backbone_mass = structural_mass(backbone_signature)

    if n_mass < backbone_mass:
        return "backbone-overestimates"
    if n_mass > backbone_mass:
        return "backbone-underestimates"

    return "backbone-different-same-mass"


def format_factorization(values: list[int]) -> str:
    return " * ".join(str(value) for value in values)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prototype PET backbone selection from input mass and digit-shadow metrics."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--base", type=int, default=10)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_local_probe_proposal expects integers >= 1")
    if args.base < 2:
        raise SystemExit("--base expects integers >= 2")

    n_digits = digit_count(args.n, args.base)
    band_min, band_max = digit_shadow_band_bounds(n_digits, args.base)
    n_shadow_position = digit_shadow_position(args.n, band_min, band_max)
    n_digit_shadow_zone = digit_shadow_zone(n_shadow_position)

    digits = digits_in_base(args.n, args.base)
    counts = Counter(digits)
    digit_unique_count = len(counts)
    max_digit_frequency = max(counts.values())
    digit_repetition_ratio = max_digit_frequency / len(digits)
    all_digits_same = digit_unique_count == 1
    palindrome = digits == list(reversed(digits))

    selected_backbone_order = n_digits
    selected_backbone_primes = first_primes(selected_backbone_order)
    selected_backbone_generator = prod(selected_backbone_primes)

    n_signature_data = shape_signature_dict(args.n)
    selected_backbone_signature_data = shape_signature_dict(selected_backbone_generator)
    shape_relation = (
        "same-signature"
        if n_signature_data["signature"] == selected_backbone_signature_data["signature"]
        else "different-signature"
    )
    shape_fit_label = shape_fit(
        n_signature_data["signature"],
        selected_backbone_signature_data["signature"],
    )
    shape_fit_label = shape_fit(
        n_signature_data["signature"],
        selected_backbone_signature_data["signature"],
    )

    n_tree = encode(args.n)
    selected_backbone_tree = encode(selected_backbone_generator)
    backbone_to_n_distance = distance(selected_backbone_tree, n_tree)
    backbone_to_n_structural_distance = structural_distance(selected_backbone_tree, n_tree)
    backbone_to_n_same_shape = backbone_to_n_structural_distance == 0
    relation_status = (
        "structurally-compatible"
        if backbone_to_n_same_shape
        else "structurally-different"
    )

    print("PET BACKBONE SELECTION PROTOTYPE")
    print()
    print(f"N = {args.n}")
    print()
    print("Input metrics")
    print(f"base = {args.base}")
    print(f"n_digits = {n_digits}")
    print(f"digit_shadow_band = {band_min:0{n_digits}d}..{band_max}")
    print(f"digit_shadow_position = {n_shadow_position:.{n_digits}f}")
    print(f"digit_shadow_zone = {n_digit_shadow_zone}")
    print(f"digit_unique_count = {digit_unique_count}")
    print(f"max_digit_frequency = {max_digit_frequency}")
    print(f"digit_repetition_ratio = {digit_repetition_ratio:.3f}")
    print(f"all_digits_same = {yes_no(all_digits_same)}")
    print(f"palindrome = {yes_no(palindrome)}")
    print()
    print("Backbone selection")
    print("selection_rule = digit-count primorial backbone")
    print(f"selected_backbone_order = {selected_backbone_order}")
    print(f"selected_backbone_generator = {selected_backbone_generator}")
    print(f"selected_backbone_factorization = {format_factorization(selected_backbone_primes)}")
    print("backbone_status = selected")
    print()
    print("PET shape comparison")
    print(f"n_already_minimal = {yes_no(n_signature_data['already_minimal'])}")
    print(f"n_child_generators = {n_signature_data['child_generators']}")
    print(f"n_signature = {n_signature_data['signature']}")
    print(f"selected_backbone_already_minimal = {yes_no(selected_backbone_signature_data['already_minimal'])}")
    print(f"selected_backbone_child_generators = {selected_backbone_signature_data['child_generators']}")
    print(f"selected_backbone_signature = {selected_backbone_signature_data['signature']}")
    print(f"shape_relation = {shape_relation}")
    print(f"shape_fit = {shape_fit_label}")
    print()
    print("next_stage = backbone-relative localization")
    print("next_stage_status = pending")
    print("next_stage_note = operator signal search comes after backbone-relative localization")
    print()
    print("claim = PET backbone selection prototype only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
