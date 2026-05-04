from __future__ import annotations

import subprocess
import sys


def run_matrix(*samples: str) -> str:
    command = [
        sys.executable,
        "tools/pet_backbone_race_matrix.py",
        "--operator-depth",
        "auto",
    ]
    for sample in samples:
        command.extend(["--sample", sample])

    result = subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_backbone_race_matrix_prints_header_and_prime_shape() -> None:
    output = run_matrix("prime:101")

    assert "N | class | n_digits | selected_backbone_order | selected_result | selected_move_count | selection_quality | selected_sequence" in output
    assert "101 | prime | 3 | 1 | already-matching | 0 | exact-shape | none" in output


def test_backbone_race_matrix_reports_power_as_narrow_deep_shape() -> None:
    output = run_matrix("power:65536")

    assert "65536 | power | 5 | 1 | matched | 3 | multi-move | INC (0,) -> INC (0, 0) -> INC (0, 0, 0)" in output


def test_backbone_race_matrix_reports_mixed_as_wide_exact_shape() -> None:
    output = run_matrix("mixed:30030")

    assert "30030 | mixed | 5 | 6 | already-matching | 0 | exact-shape | none" in output


def test_backbone_race_matrix_reports_large_diagonal_as_one_move_shape() -> None:
    output = run_matrix("diagonal:9999999999")

    assert "9999999999 | diagonal | 10 | 5 | matched | 1 | one-move | INC (0,)" in output


def test_backbone_race_matrix_reports_border_power_like_shape() -> None:
    output = run_matrix("border:10000")

    assert "10000 | border | 5 | 2 | matched | 4 | multi-move | INC (0,) -> INC (0,) -> INC (0, 0) -> INC (0, 0)" in output
