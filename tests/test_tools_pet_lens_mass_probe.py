from __future__ import annotations

import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_lens_mass_probe.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_lens_mass_probe_reports_digit_mass_weight_and_shadow_for_55() -> None:
    output = run_tool(55)

    assert "PET LENS MASS PROBE" in output
    assert "N = 55" in output
    assert "base = 10" in output
    assert "n_digits = 2" in output

    assert "source_generator = 6" in output
    assert "source_generator_digits = 1" in output
    assert "source_signature = [[], []]" in output

    assert "target_lens = one-leaf" in output
    assert "target_leaf_count = 1" in output

    assert "primorial_expanded_generator = 30" in output
    assert "primorial_expanded_digits = 2" in output
    assert "expansion_primes = [5]" in output
    assert "digit_aligned = yes" in output

    assert "digit_band_min = 10" in output
    assert "digit_band_max = 99" in output
    assert "n_band_position = 0.506" in output
    assert "expanded_band_position = 0.225" in output
    assert "weight_ratio = 0.545" in output
    assert "weight_gap = 25" in output
    assert "relative_weight_gap = 0.455" in output
    assert "weight_alignment = loose" in output
    assert "weight_direction = lighter" in output

    assert "digit_unique_count = 1" in output
    assert "max_digit_frequency = 2" in output
    assert "digit_repetition_ratio = 1.000" in output
    assert "all_digits_same = yes" in output
    assert "palindrome = yes" in output

    assert "mass_note = expanded generator matches N digit count" in output
    assert "shadow_note = repeated digits detected in base representation" in output
    assert "claim = PET lens mass/shadow probe only; this does not factor N" in output
