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

    assert "Digit positional profile" in output
    assert "digit_position_terms = " in output
    assert "digit_weight_profile = " in output
    assert "digit_weight_ratios = " in output
    assert "digit_delta = " in output
    assert "digit_gradient = " in output

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
    assert "operator_probe_status = iterative-shape-probe" in output
    assert "operator_probe_depth_limit = 2" in output
    assert "Selected operator shape comparison" in output
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
    assert "selected_operator = DROP" in output
    assert "selected_operator_path = root" in output


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
    assert "selected_operator = none" in output
    assert "selected_operator_path = root" in output


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
    assert "selected_operator = INC" in output
    assert "selected_operator_path = (0,)" in output


def test_iterative_operator_probe_matches_three_digit_same_mass_case_low_mid() -> None:
    output = run_tool(333)

    assert "N = 333" in output
    assert "n_digits = 3" in output
    assert "digit_shadow_band = 000..999" in output
    assert "selected_backbone_order = 3" in output
    assert "selected_backbone_generator = 30" in output
    assert "selected_backbone_factorization = 2 * 3 * 5" in output

    assert "n_signature = [[], [[]]]" in output
    assert "selected_backbone_signature = [[], [], []]" in output
    assert "shape_fit = backbone-different-same-mass" in output

    assert "operator_probe_status = iterative-shape-probe" in output
    assert "operator_probe_depth_limit = 2" in output
    assert "operator_probe_result = matched" in output
    assert "selected_operator_sequence = INC (0,) -> DROP root" in output
    assert "probed_backbone_signature = [[], [[]]]" in output
    assert "probed_backbone_relation_to_n = same-signature" in output
    assert "probed_backbone_fit_against_n = result-matches" in output


def test_iterative_operator_probe_matches_three_digit_same_mass_case_high() -> None:
    output = run_tool(999)

    assert "N = 999" in output
    assert "n_digits = 3" in output
    assert "digit_shadow_band = 000..999" in output
    assert "selected_backbone_order = 3" in output
    assert "selected_backbone_generator = 30" in output
    assert "selected_backbone_factorization = 2 * 3 * 5" in output

    assert "n_signature = [[], [[]]]" in output
    assert "selected_backbone_signature = [[], [], []]" in output
    assert "shape_fit = backbone-different-same-mass" in output

    assert "operator_probe_status = iterative-shape-probe" in output
    assert "operator_probe_depth_limit = 2" in output
    assert "operator_probe_result = matched" in output
    assert "selected_operator_sequence = INC (0,) -> DROP root" in output
    assert "probed_backbone_signature = [[], [[]]]" in output
    assert "probed_backbone_relation_to_n = same-signature" in output
    assert "probed_backbone_fit_against_n = result-matches" in output


def test_operator_depth_can_match_deeper_power_shapes() -> None:
    output = subprocess.run(
        [
            sys.executable,
            "tools/pet_local_probe_proposal.py",
            "16",
            "--operator-depth",
            "3",
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout

    assert "N = 16" in output
    assert "n_signature = [[[[]]]]" in output
    assert "shape_fit = backbone-underestimates" in output
    assert "operator_probe_depth_limit = 3" in output
    assert "operator_probe_result = matched" in output
    assert "selected_operator_sequence = INC (0,) -> INC (1, 0) -> DROP root" in output
    assert "probed_backbone_signature = [[[[]]]]" in output
    assert "probed_backbone_relation_to_n = same-signature" in output
    assert "probed_backbone_fit_against_n = result-matches" in output


def test_operator_depth_auto_uses_input_digit_count_plus_one() -> None:
    output = subprocess.run(
        [
            sys.executable,
            "tools/pet_local_probe_proposal.py",
            "16",
            "--operator-depth",
            "auto",
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout

    assert "N = 16" in output
    assert "n_digits = 2" in output
    assert "operator_probe_depth_limit = 3" in output
    assert "operator_probe_result = matched" in output
    assert "probed_backbone_relation_to_n = same-signature" in output
    assert "probed_backbone_fit_against_n = result-matches" in output
