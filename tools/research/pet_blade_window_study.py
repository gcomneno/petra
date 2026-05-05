#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from ast import literal_eval
from collections.abc import Iterable


def digits(n: int) -> list[int]:
    return [int(ch) for ch in str(n)]


def digit_gradient(ds: list[int]) -> str:
    if len(ds) < 2:
        return "flat"
    if all(a == b for a, b in zip(ds, ds[1:])):
        return "flat"
    if ds[-1] > ds[0]:
        return "ascending"
    if ds[-1] < ds[0]:
        return "descending"
    return "mixed"


def digit_shadow_zone(n: int) -> str:
    width = len(str(n))
    lower = 0
    upper = (10 ** width) - 1
    position = (n - lower) / (upper - lower) if upper != lower else 0.0

    if position < 1 / 3:
        return "low"
    if position < 2 / 3:
        return "mid"
    return "high"


def signature_mass(signature) -> int:
    if not isinstance(signature, list):
        return 0
    return sum(1 + signature_mass(child) for child in signature)


def extract(output: str, key: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)} = (.*)$", re.MULTILINE)
    match = pattern.search(output)
    return match.group(1) if match else "unknown"


def run_proposal(n: int, operator_depth: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_local_probe_proposal.py",
            str(n),
            "--operator-depth",
            operator_depth,
            "--backbone-selection",
            "race",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def preset_numbers(name: str) -> list[int]:
    if name == "diagonals":
        return [
            11, 22, 33, 44, 55, 66, 77, 88, 99,
            111, 222, 333, 444, 555, 666, 777, 888, 999,
            9999, 99999, 999999,
        ]

    if name == "known":
        return [
            11, 22, 33, 44, 55, 66, 77, 88, 99,
            1001, 1729, 10007, 65536, 30030, 99999, 9999999999,
        ]

    if name == "palindromes":
        return [
            101, 111, 121, 131, 141, 151, 161, 171, 181, 191,
            1001, 1221, 1331, 1441, 1551, 1661, 1771, 1881, 1991,
            10001, 12321, 15651, 19991, 99999,
            100001, 123321, 456654, 999999,
        ]

    if name == "stress":
        return [
            # tiny / atomic / balanced-flat / near-shape
            11, 22, 33, 44, 55, 66, 77, 88, 99,
            # repeated digits
            111, 222, 333, 444, 555, 666, 777, 888, 999,
            9999, 99999, 999999, 9999999999,
            # palindromes
            101, 121, 131, 141, 1001, 1221, 1331, 1441,
            10001, 12321, 15651, 19991, 100001, 123321, 456654,
            # known PET route examples
            10007, 65536, 30030, 3027009081,
            # balanced-flat semiprime / multiprime style
            143, 221, 323, 437, 667, 899, 1001, 1729,
            # powers and deep shapes
            16, 64, 256, 4096, 65536, 1048576,
            # wide primorial-ish
            2310, 30030, 510510,
        ]

    raise ValueError(f"unknown preset: {name}")


def range_numbers(start: int, stop: int, limit: int | None) -> Iterable[int]:
    count = 0
    for n in range(start, stop + 1):
        yield n
        count += 1
        if limit is not None and count >= limit:
            break


def build_row(n: int, operator_depth: str) -> dict[str, object]:
    output = run_proposal(n, operator_depth)

    ds = digits(n)
    n_digits = len(ds)
    digit_unique_count = len(set(ds))
    max_digit_frequency = max(ds.count(d) for d in set(ds))
    repetition_ratio = max_digit_frequency / n_digits

    selected_order = int(extract(output, "selected_backbone_order"))
    selected_generator = extract(output, "selected_backbone_generator")
    quality = extract(output, "race_selection_quality")
    diagnostic = extract(output, "race_shape_diagnostic")
    shape_relation = extract(output, "shape_relation")
    shape_fit = extract(output, "shape_fit")
    selected_operator_sequence = extract(output, "selected_operator_sequence")
    composite_border_hint = extract(output, "composite_border_hint")

    raw_signature = extract(output, "n_signature")
    signature = literal_eval(raw_signature) if raw_signature != "unknown" else []
    actual_mass = signature_mass(signature)

    max_window_order = n_digits + 2
    mass_deficit = max_window_order - actual_mass
    mass_fill_ratio = actual_mass / max_window_order if max_window_order else 0.0

    start_mass_minus_1 = max(1, actual_mass - 1)
    start_mass_minus_2 = max(1, actual_mass - 2)
    start_mass = max(1, actual_mass)
    start_mass_minus_2_or_deep_guard = (
        1 if diagnostic == "narrow-deep" else start_mass_minus_2
    )

    def window_metrics(start_order: int, end_order: int = max_window_order) -> dict[str, int]:
        selected_inside = start_order <= selected_order <= end_order
        window_size = max(0, end_order - start_order + 1)
        attempts_ltr = selected_order - start_order + 1 if selected_inside else 0
        attempts_rtl = end_order - selected_order + 1 if selected_inside else 0
        saved_left = start_order - 1
        return {
            "window_size": window_size,
            "attempts_ltr": attempts_ltr,
            "attempts_rtl": attempts_rtl,
            "saved_left": saved_left,
        }

    mass_minus_2_metrics = window_metrics(start_mass_minus_2)
    guarded_metrics = window_metrics(start_mass_minus_2_or_deep_guard)
    fill_080_direction = "RTL" if mass_fill_ratio >= 0.80 else "LTR"
    fill_080_attempts = (
        guarded_metrics["attempts_rtl"]
        if fill_080_direction == "RTL"
        else guarded_metrics["attempts_ltr"]
    )
    fill_gt_080_direction = "RTL" if mass_fill_ratio > 0.80 else "LTR"
    fill_gt_080_attempts = (
        guarded_metrics["attempts_rtl"]
        if fill_gt_080_direction == "RTL"
        else guarded_metrics["attempts_ltr"]
    )

    return {
        "N": n,
        "digits": n_digits,
        "all_digits_same": "yes" if digit_unique_count == 1 else "no",
        "digit_unique_count": digit_unique_count,
        "max_digit_frequency": max_digit_frequency,
        "digit_repetition_ratio": f"{repetition_ratio:.3f}",
        "digit_shadow_zone": digit_shadow_zone(n),
        "digit_gradient": digit_gradient(ds),
        "actual_pet_mass": actual_mass,
        "max_window_mass": max_window_order,
        "mass_deficit": mass_deficit,
        "mass_fill_ratio": f"{mass_fill_ratio:.3f}",
        "selected_backbone_order": selected_order,
        "selected_backbone_generator": selected_generator,
        "safe_start_max": selected_order,
        "race_selection_quality": quality,
        "race_shape_diagnostic": diagnostic,
        "shape_relation": shape_relation,
        "shape_fit": shape_fit,
        "selected_operator_sequence": selected_operator_sequence,
        "composite_border_hint": composite_border_hint,
        "keep_from_digits_minus_1": "yes" if max(1, n_digits - 1) <= selected_order else "no",
        "keep_from_digits_minus_2": "yes" if max(1, n_digits - 2) <= selected_order else "no",
        "candidate_start_mass": start_mass,
        "candidate_start_mass_minus_1": start_mass_minus_1,
        "candidate_start_mass_minus_2": start_mass_minus_2,
        "candidate_start_mass_minus_2_or_deep_guard": start_mass_minus_2_or_deep_guard,
        "keep_from_mass": "yes" if start_mass <= selected_order else "no",
        "keep_from_mass_minus_1": "yes" if start_mass_minus_1 <= selected_order else "no",
        "keep_from_mass_minus_2": "yes" if start_mass_minus_2 <= selected_order else "no",
        "keep_from_mass_minus_2_or_deep_guard": "yes"
        if start_mass_minus_2_or_deep_guard <= selected_order
        else "no",
        "mass_minus_2_window_size": mass_minus_2_metrics["window_size"],
        "mass_minus_2_attempts_ltr": mass_minus_2_metrics["attempts_ltr"],
        "mass_minus_2_attempts_rtl": mass_minus_2_metrics["attempts_rtl"],
        "mass_minus_2_saved_left": mass_minus_2_metrics["saved_left"],
        "guarded_window_size": guarded_metrics["window_size"],
        "guarded_attempts_ltr": guarded_metrics["attempts_ltr"],
        "guarded_attempts_rtl": guarded_metrics["attempts_rtl"],
        "guarded_saved_left": guarded_metrics["saved_left"],
        "fill_080_direction": fill_080_direction,
        "fill_080_attempts": fill_080_attempts,
        "fill_gt_080_direction": fill_gt_080_direction,
        "fill_gt_080_attempts": fill_gt_080_attempts,
        "keep_from_mass_fill_half": "yes" if max(1, int(n_digits * 0.5)) <= selected_order else "no",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research study for PET active blade backbone window heuristics."
    )
    parser.add_argument("--preset", choices=["diagonals", "known", "palindromes", "stress"])
    parser.add_argument("--from", dest="from_n", type=int)
    parser.add_argument("--to", dest="to_n", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--operator-depth", default="auto")
    args = parser.parse_args()

    if args.preset:
        numbers = preset_numbers(args.preset)
    else:
        if args.from_n is None or args.to_n is None:
            raise SystemExit("use --preset NAME or --from A --to B")
        numbers = list(range_numbers(args.from_n, args.to_n, args.limit))

    rows = [build_row(n, args.operator_depth) for n in numbers]

    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
