from __future__ import annotations

import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_local_probe_proposal.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def assert_common_backbone_selection(output: str, n: int) -> None:
    assert "PET BACKBONE SELECTION PROTOTYPE" in output
    assert f"N = {n}" in output

    assert "Input metrics" in output
    assert "base = 10" in output
    assert "n_digits = 2" in output
    assert "digit_unique_count = 1" in output
    assert "max_digit_frequency = 2" in output
    assert "digit_repetition_ratio = 1.000" in output
    assert "all_digits_same = yes" in output
    assert "palindrome = yes" in output

    assert "Backbone selection" in output
    assert "selection_rule = digit-count primorial backbone" in output
    assert "selected_backbone_order = 2" in output
    assert "selected_backbone_generator = 6" in output
    assert "selected_backbone_factorization = 2 * 3" in output
    assert "backbone_status = selected" in output

    assert "PET shape comparison" in output
    assert "selected_backbone_already_minimal = yes" in output
    assert "selected_backbone_child_generators = [1, 1]" in output
    assert "selected_backbone_signature = [[], []]" in output

    assert "Operator probe" in output
    assert "operator_probe_status = first-iteration" in output
    assert "First operator shape comparison" in output
    assert "claim = PET backbone selection prototype only; this does not factor N" in output


def test_backbone_selection_for_repeated_low_band_two_digit_input() -> None:
    output = run_tool(11)

    assert_common_backbone_selection(output, 11)

    assert "digit_shadow_band = 00..99" in output
    assert "digit_shadow_position = 0.11" in output
    assert "digit_shadow_zone = low" in output

    assert "n_already_minimal = no" in output
    assert "n_child_generators = [1]" in output
    assert "n_signature = [[]]" in output
    assert "shape_relation = different-signature" in output
    assert "shape_fit = backbone-overestimates" in output
    assert "operator_priority = DROP, DEC, NEW, INC" in output
    assert "first_operator = DROP" in output
    assert "first_operator_path = root" in output


def test_backbone_selection_for_repeated_mid_band_two_digit_input() -> None:
    output = run_tool(55)

    assert_common_backbone_selection(output, 55)

    assert "digit_shadow_band = 00..99" in output
    assert "digit_shadow_position = 0.56" in output
    assert "digit_shadow_zone = mid" in output

    assert "n_already_minimal = no" in output
    assert "n_child_generators = [1, 1]" in output
    assert "n_signature = [[], []]" in output
    assert "shape_relation = same-signature" in output
    assert "shape_fit = backbone-matches" in output
    assert "operator_priority = none" in output
    assert "first_operator = none" in output
    assert "first_operator_path = root" in output


def test_backbone_selection_for_repeated_high_band_two_digit_input() -> None:
    output = run_tool(99)

    assert_common_backbone_selection(output, 99)

    assert "digit_shadow_band = 00..99" in output
    assert "digit_shadow_position = 1.00" in output
    assert "digit_shadow_zone = high" in output

    assert "n_already_minimal = no" in output
    assert "n_child_generators = [2, 1]" in output
    assert "n_signature = [[], [[]]]" in output
    assert "shape_relation = different-signature" in output
    assert "shape_fit = backbone-underestimates" in output
    assert "operator_priority = INC, NEW, DROP, DEC" in output
    assert "first_operator = INC" in output
    assert "first_operator_path = (0,)" in output
