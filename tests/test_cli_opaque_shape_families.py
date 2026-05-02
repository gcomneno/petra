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


def test_opaque_shape_families_json_reports_mass_constraints() -> None:
    data = _run_json(
        "opaque-shape-families",
        "10403",
        "--max-generator-count",
        "4",
        "--max-exponent",
        "4",
    )

    assert data["digits"] == 5
    assert data["bit_length"] == 14
    assert data["mass_bits"] == 14

    k2 = next(row for row in data["balanced_families"] if row["k"] == 2)
    assert k2["mass_bits_per_generator"] == 7.0
    assert k2["digits_per_generator"] == 2.5

    exp2 = next(row for row in data["prime_power_families"] if row["exponent"] == 2)
    assert exp2["base_mass_bits"] == 7.0
    assert exp2["base_digits"] == 2.5

    assert "claim" in data
    assert "does not factor N" in data["claim"]


def test_opaque_shape_families_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-shape-families",
        "10403",
        "--max-generator-count",
        "4",
        "--max-exponent",
        "4",
    )

    assert result.returncode == 0, result.stderr
    assert "PET OPAQUE SHAPE FAMILIES" in result.stdout
    assert "Observed projection" in result.stdout
    assert "Balanced generator families" in result.stdout
    assert "Prime-power-like families" in result.stdout
    assert "claim = PET shape-family constraints only; this does not factor N" in result.stdout


def test_opaque_shape_families_rejects_non_positive_integer() -> None:
    result = _run_cli(
        "opaque-shape-families",
        "0",
        "--max-generator-count",
        "4",
        "--max-exponent",
        "4",
    )

    assert result.returncode != 0
    assert "opaque-shape-families expects integers >= 1" in result.stderr
