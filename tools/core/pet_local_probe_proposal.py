#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import Counter
from math import prod
from pathlib import Path

from pet_backbone_race import shape_diagnostic

from pet.algebra import distance, structural_distance
from pet.core import encode, shape_signature_dict
from pet_shape_algebra import shape_apply, shape_can_apply, shape_paths

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.research.pet_decimal_boundary_study import decimal_boundary_profile


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


def operator_sequence_move_count(sequence: str) -> int:
    if sequence == "none":
        return 0
    return sequence.count(" -> ") + 1


def operator_probe_selection_quality(result: str, move_count: int) -> str:
    if result not in {"already-matching", "matched"}:
        return "unmatched"
    if move_count == 0:
        return "exact-shape"
    if move_count == 1:
        return "one-move"
    return "multi-move"


def operator_probe_result_rank(result: str) -> int:
    return {
        "already-matching": 0,
        "matched": 1,
        "exhausted": 2,
        "unavailable": 3,
    }.get(result, 4)


def shape_diagnostic_summary(diagnostic: str) -> str:
    return {
        "atomic-exact": "selected backbone is atomic and already matches N shape",
        "narrow-deep": "selected backbone is narrow and reaches N through depth-increasing moves",
        "wide-exact": "selected backbone is wider than digit-count and exactly matches N shape",
        "near-shape": "selected backbone is one operator move away from N shape",
        "complex-border": "selected backbone has a non-trivial PET relation to N shape",
    }.get(diagnostic, "selected backbone has an unknown PET diagnostic relation to N shape")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prototype PET backbone selection from input mass and digit-shadow metrics."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument("--base", type=int, default=10)
    parser.add_argument("--operator-depth", default="2")
    parser.add_argument("--backbone-order", type=int)
    parser.add_argument(
        "--backbone-selection",
        choices=("digit-count", "race"),
        default="digit-count",
    )
    parser.add_argument(
        "--blade-window",
        choices=("full", "active"),
        default="full",
        help="Race candidate window policy. Default keeps the historical full window.",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("pet_local_probe_proposal expects integers >= 1")
    if args.base < 2:
        raise SystemExit("--base expects integers >= 2")

    n_digits = digit_count(args.n, args.base)

    if args.backbone_order is not None and args.backbone_order < 1:
        raise SystemExit("--backbone-order expects integers >= 1")

    if args.operator_depth == "auto":
        operator_depth = n_digits + 1
    else:
        try:
            operator_depth = int(args.operator_depth)
        except ValueError as exc:
            raise SystemExit("--operator-depth expects an integer or auto") from exc

        if operator_depth < 0:
            raise SystemExit("--operator-depth expects integers >= 0 or auto")
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
    decimal_boundary = decimal_boundary_profile(args.n)

    n_signature_data = shape_signature_dict(args.n)

    if args.backbone_selection == "race" and args.backbone_order is not None:
        raise SystemExit("--backbone-selection race cannot be combined with --backbone-order")

    race_candidates = []
    race_selected = None

    active_blade_start = 1
    active_blade_end = n_digits + 2
    active_blade_direction = "LTR"
    actual_pet_mass = structural_mass(n_signature_data["signature"])
    max_window_mass = n_digits + 2
    mass_fill_ratio = actual_pet_mass / max_window_mass if max_window_mass else 0.0

    if args.backbone_selection == "race":
        selection_rule = "PET backbone race"
        if args.blade_window == "active":
            active_blade_start = max(1, actual_pet_mass - 2)
            active_blade_direction = "RTL" if mass_fill_ratio > 0.80 else "LTR"

        candidate_orders = list(range(active_blade_start, active_blade_end + 1))
        if active_blade_direction == "RTL":
            candidate_orders = list(reversed(candidate_orders))

        for candidate_order in candidate_orders:
            candidate_primes = first_primes(candidate_order)
            candidate_generator = prod(candidate_primes)
            candidate_signature_data = shape_signature_dict(candidate_generator)
            candidate_shape_fit = shape_fit(
                n_signature_data["signature"],
                candidate_signature_data["signature"],
            )
            candidate_probe = iterative_operator_probe(
                candidate_signature_data["signature"],
                n_signature_data["signature"],
                candidate_shape_fit,
                depth_limit=operator_depth,
            )
            candidate_sequence = format_move_sequence(candidate_probe["selected_moves"])
            candidate_move_count = operator_sequence_move_count(candidate_sequence)
            candidate_result = candidate_probe["status"]

            race_candidates.append(
                {
                    "order": candidate_order,
                    "generator": candidate_generator,
                    "shape_fit": candidate_shape_fit,
                    "result": candidate_result,
                    "sequence": candidate_sequence,
                    "move_count": candidate_move_count,
                    "quality": operator_probe_selection_quality(
                        candidate_result,
                        candidate_move_count,
                    ),
                }
            )

        race_selected = min(
            race_candidates,
            key=lambda candidate: (
                operator_probe_result_rank(candidate["result"]),
                candidate["move_count"],
                abs(candidate["order"] - n_digits),
            ),
        )
        selected_backbone_order = race_selected["order"]
    else:
        selected_backbone_order = args.backbone_order or n_digits
        selection_rule = (
            "manual primorial backbone order override"
            if args.backbone_order is not None
            else "digit-count primorial backbone"
        )

    selected_backbone_primes = first_primes(selected_backbone_order)
    selected_backbone_generator = prod(selected_backbone_primes)

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
        depth_limit=operator_depth,
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
    print("Decimal boundary profile")
    print(f"digit_block_count = {decimal_boundary['digit_block_count']}")
    print(f"longest_digit_run = {decimal_boundary['longest_digit_run']}")
    print(f"longest_zero_run = {decimal_boundary['longest_zero_run']}")
    print(f"longest_nine_run = {decimal_boundary['longest_nine_run']}")
    print(f"zero_run_weighted_pressure = {decimal_boundary['zero_run_weighted_pressure']:.3f}")
    print(f"nine_run_weighted_pressure = {decimal_boundary['nine_run_weighted_pressure']:.3f}")
    print(f"decimal_boundary_pressure = {decimal_boundary['decimal_boundary_pressure']:.3f}")
    print(f"digit_island_count = {decimal_boundary['digit_island_count']}")
    print(f"digit_island_span_ratio = {decimal_boundary['digit_island_span_ratio']:.3f}")
    print(f"digit_transition_pressure = {decimal_boundary['digit_transition_pressure']:.3f}")
    print(f"decimal_rigid_border_score = {decimal_boundary['decimal_rigid_border_score']:.3f}")
    print(f"decimal_rigid_border_hint = {decimal_boundary['decimal_rigid_border_hint']}")
    print()
    print("Backbone selection")
    print(f"selection_rule = {selection_rule}")
    print(f"selected_backbone_order = {selected_backbone_order}")
    print(f"selected_backbone_generator = {selected_backbone_generator}")
    print(f"selected_backbone_factorization = {format_factorization(selected_backbone_primes)}")
    if race_selected is not None:
        print(f"blade_window = {args.blade_window}")
        print(f"active_blade_start = {active_blade_start}")
        print(f"active_blade_end = {active_blade_end}")
        print(f"active_blade_direction = {active_blade_direction}")
        print(f"active_blade_actual_pet_mass = {actual_pet_mass}")
        print(f"active_blade_mass_fill_ratio = {mass_fill_ratio:.3f}")
        print(f"race_candidate_orders = {','.join(str(order) for order in candidate_orders)}")
        print(f"race_selected_move_count = {race_selected['move_count']}")
        print(f"race_selected_sequence = {race_selected['sequence']}")
        race_diagnostic = shape_diagnostic(
            selected_backbone_order,
            n_digits,
            race_selected["quality"],
        )
        print(f"race_selection_quality = {race_selected['quality']}")
        print(f"race_shape_diagnostic = {race_diagnostic}")
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
    print("Composite operator probe")
    print("composite_probe_status = available")
    print("pet_unit = 1")
    print("pet_unit_signature = []")
    print(f"unit_merge_left = {selected_backbone_generator}")
    print(f"unit_merge_right = {selected_backbone_generator}")
    print("self_unmerge_available = yes")
    print("self_unmerge_result = 1")
    print("self_unmerge_signature = []")
    selected_signature = selected_backbone_signature_data["signature"]
    flat_generator = bool(selected_signature) and all(child == [] for child in selected_signature)
    print(f"flat_generator = {yes_no(flat_generator)}")
    print(f"flat_leaf_count = {len(selected_signature) if flat_generator else 'unknown'}")
    print("composite_relation = flat-self-unmerge-to-unit" if flat_generator else "composite_relation = none")
    selected_operator_sequence = format_move_sequence(operator_probe["selected_moves"])
    balanced_flat_border = (
        race_selected is not None
        and race_diagnostic == "complex-border"
        and shape_relation == "same-signature"
        and shape_fit_label == "backbone-matches"
        and selected_operator_sequence == "none"
        and flat_generator
    )
    print(f"composite_border_hint = {'balanced-flat-border' if balanced_flat_border else 'none'}")
    print()
    if race_selected is not None:
        print("PET diagnostic summary")
        print(f"shape_diagnostic = {race_diagnostic}")
        print(f"summary = {shape_diagnostic_summary(race_diagnostic)}")
        print()
    print("claim = PET backbone selection prototype only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
