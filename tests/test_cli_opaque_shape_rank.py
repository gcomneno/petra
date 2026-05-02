import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def _run_json(*args: str) -> dict:
    result = _run_cli(*args, "--json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_opaque_shape_rank_json_reports_opacity_margins() -> None:
    data = _run_json(
        "opaque-shape-rank",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert data["digits"] == 5
    assert data["bit_length"] == 14
    assert data["mass_bits"] == 14
    assert data["excluded_support_bits"] == 5

    k2 = next(row for row in data["ranked_families"] if row["k"] == 2)
    assert k2["avg_generator_bits"] == 7.0
    assert k2["margin_bits"] == 2.0
    assert k2["opacity"] == "low"

    assert "claim" in data
    assert "does not factor N" in data["claim"]


def test_opaque_shape_rank_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-shape-rank",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode == 0, result.stderr
    assert "PET OPAQUE SHAPE RANK" in result.stdout
    assert "Observed projection" in result.stdout
    assert "Ranked compatible families" in result.stdout
    assert "PET interpretation" in result.stdout
    assert "claim = PET shape-family ranking only; this does not factor N" in result.stdout


def test_opaque_shape_rank_rejects_non_positive_integer() -> None:
    result = _run_cli(
        "opaque-shape-rank",
        "0",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode != 0
    assert "opaque-shape-rank expects integers >= 1" in result.stderr


def test_opaque_shape_rank_requires_positive_excluded_support_limit() -> None:
    result = _run_cli(
        "opaque-shape-rank",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "0",
    )

    assert result.returncode != 0
    assert "--excluded-support-limit expects integers >= 1" in result.stderr
