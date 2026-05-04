#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from math import prod

from pet.algebra import distance, structural_distance
from pet.core import encode, shape_signature_dict
from pet_shape_algebra import shape_apply, shape_can_apply, shape_paths


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


def positional_weights_for_digits(digits: list[int], base: int) -> list[int]:
    length = len(digits)
    return [
        digit * (base ** (length - index - 1))
        for index, digit in enumerate(digits)
    ]


def positional_terms_for_digits(digits: list[int], base: int) -> str:
    length = len(digits)
    return " + ".join(
        f"{digit}*{base ** (length - index - 1)}"
        for index, digit in enumerate(digits)
    )


def positional_weight_ratios(weights: list[int]) -> list[float]:
    total = sum(weights)
    if total == 0:
        return [0.0 for _weight in weights]
    return [weight / total for weight in weights]


def digit_delta(digits: list[int]) -> int:
    if len(digits) < 2:
        return 0
    return digits[-1] - digits[0]


def digit_gradient(digits: list[int]) -> str:
    if len(digits) < 2:
        return "single"

    delta = digit_delta(digits)
    if delta > 0:
        return "ascending"
    if delta < 0:
        return "descending"
    return "flat"


def format_float_list(values: list[float], precision: int = 3) -> str:
    return "[" + ", ".join(f"{value:.{precision}f}" for value in values) + "]"


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



def result_fit_against_n(n_signature: list, result_signature: list) -> str:
    if n_signature == result_signature:
        return "result-matches"

    n_mass = structural_mass(n_signature)
    result_mass = structural_mass(result_signature)

    if n_mass < result_mass:
        return "result-overestimates"
    if n_mass > result_mass:
        return "result-underestimates"

    return "result-different-same-mass"


def signature_to_shape(signature: list) -> tuple:
    return tuple(signature_to_shape(child) for child in signature)


def shape_to_signature(shape: tuple) -> list:
    return [shape_to_signature(child) for child in shape]


def operator_priority_for_fit(shape_fit_label: str) -> list[str]:
    if shape_fit_label == "backbone-overestimates":
        return ["DROP", "DEC", "NEW", "INC"]
    if shape_fit_label == "backbone-underestimates":
        return ["INC", "NEW", "DROP", "DEC"]
    if shape_fit_label == "backbone-different-same-mass":
        return ["INC", "DEC", "NEW", "DROP"]
    return []


def format_move(move: tuple[str, tuple]) -> str:
    op, path = move
    return f"{op} {format_probe_path(path)}"


def format_move_sequence(moves: list[tuple[str, tuple]]) -> str:
    if not moves:
        return "none"
    return " -> ".join(format_move(move) for move in moves)


def iterative_operator_probe(
    backbone_signature: list,
    n_signature: list,
    shape_fit_label: str,
    *,
    depth_limit: int = 2,
) -> dict:
    backbone_shape = signature_to_shape(backbone_signature)
    priority = operator_priority_for_fit(shape_fit_label)

    if not priority:
        return {
            "status": "already-matching",
            "depth_limit": depth_limit,
            "priority": ["none"],
            "attempts": [],
            "selected_moves": [],
            "selected_signature": backbone_signature,
            "selected_relation": "same-signature",
            "selected_fit": "result-matches",
        }

    attempts = []
    frontier = [(backbone_shape, [])]
    seen = {backbone_shape}

    while frontier:
        current_shape, current_moves = frontier.pop(0)

        if len(current_moves) >= depth_limit:
            continue

        for op in priority:
            paths = [()] if op in {"NEW", "DROP"} else list(shape_paths(current_shape))
            for path in paths:
                if not shape_can_apply(current_shape, op, path):
                    continue

                result_shape = shape_apply(current_shape, op, path)
                result_signature = shape_to_signature(result_shape)
                result_relation = (
                    "same-signature"
                    if result_signature == n_signature
                    else "different-signature"
                )
                result_fit = result_fit_against_n(n_signature, result_signature)
                result_moves = current_moves + [(op, path)]

                attempt = {
                    "moves": result_moves,
                    "result_shape": result_shape,
                    "result_signature": result_signature,
                    "result_relation": result_relation,
                    "result_fit": result_fit,
                }
                attempts.append(attempt)

                if result_relation == "same-signature":
                    return {
                        "status": "matched",
                        "depth_limit": depth_limit,
                        "priority": priority,
                        "attempts": attempts,
                        "selected_moves": result_moves,
                        "selected_signature": result_signature,
                        "selected_relation": result_relation,
                        "selected_fit": result_fit,
                    }

                if result_shape not in seen:
                    seen.add(result_shape)
                    frontier.append((result_shape, result_moves))

    if attempts:
        fallback = attempts[-1]
        return {
            "status": "exhausted",
            "depth_limit": depth_limit,
            "priority": priority,
            "attempts": attempts,
            "selected_moves": [],
            "selected_signature": fallback["result_signature"],
            "selected_relation": fallback["result_relation"],
            "selected_fit": fallback["result_fit"],
        }

    return {
        "status": "unavailable",
        "depth_limit": depth_limit,
        "priority": priority,
        "attempts": [],
        "selected_moves": [],
        "selected_signature": [],
        "selected_relation": "unavailable",
        "selected_fit": "unavailable",
    }


def format_probe_path(path: tuple) -> str:
    return str(path) if path else "root"




def format_factorization(values: list[int]) -> str:
    return " * ".join(str(value) for value in values)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prototype PET backbone selection from input mass and digit-shadow metrics."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--base", type=int, default=10)
    parser.add_argument("--operator-depth", type=int, default=2)
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_local_probe_proposal expects integers >= 1")
    if args.base < 2:
        raise SystemExit("--base expects integers >= 2")
    if args.operator_depth < 0:
        raise SystemExit("--operator-depth expects integers >= 0")

    n_digits = digit_count(args.n, args.base)
    band_min, band_max = digit_shadow_band_bounds(n_digits, args.base)
    n_shadow_position = digit_shadow_position(args.n, band_min, band_max)
    n_digit_shadow_zone = digit_shadow_zone(n_shadow_position)

    digits = digits_in_base(args.n, args.base)
    positional_weights = positional_weights_for_digits(digits, args.base)
    positional_ratios = positional_weight_ratios(positional_weights)
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
    operator_probe = iterative_operator_probe(
        selected_backbone_signature_data["signature"],
        n_signature_data["signature"],
        shape_fit_label,
        depth_limit=args.operator_depth,
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
    print("Digit positional profile")
    print(f"digit_position_terms = {positional_terms_for_digits(digits, args.base)}")
    print(f"digit_weight_profile = {positional_weights}")
    print(f"digit_weight_ratios = {format_float_list(positional_ratios)}")
    print(f"digit_delta = {digit_delta(digits)}")
    print(f"digit_gradient = {digit_gradient(digits)}")
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
    print("Operator probe")
    print("operator_probe_status = iterative-shape-probe")
    print(f"operator_probe_depth_limit = {operator_probe['depth_limit']}")
    print(f"operator_probe_result = {operator_probe['status']}")
    print(f"operator_priority = {', '.join(operator_probe['priority'])}")
    for index, attempt in enumerate(operator_probe["attempts"], start=1):
        print(
            f"operator_probe_{index} = "
            f"{format_move_sequence(attempt['moves'])} -> "
            f"{attempt['result_signature']} / "
            f"{attempt['result_relation']} / "
            f"{attempt['result_fit']}"
        )
    print(f"selected_operator_sequence = {format_move_sequence(operator_probe['selected_moves'])}")
    selected_first_move = operator_probe["selected_moves"][0] if operator_probe["selected_moves"] else ("none", ())
    print(f"selected_operator = {selected_first_move[0]}")
    print(f"selected_operator_path = {format_probe_path(selected_first_move[1])}")
    print()
    print("Selected operator shape comparison")
    print(f"probed_backbone_signature = {operator_probe['selected_signature']}")
    print(f"probed_backbone_relation_to_n = {operator_probe['selected_relation']}")
    print(f"probed_backbone_fit_against_n = {operator_probe['selected_fit']}")
    print()
    print("claim = PET backbone selection prototype only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
