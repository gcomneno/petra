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


def test_opaque_mass_centers_json_reports_boundary_signals() -> None:
    data = _run_json(
        "opaque-mass-centers",
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

    k2 = next(row for row in data["mass_centers"] if row["k"] == 2)
    assert k2["center_bits"] == 7.0
    assert k2["center_digits"] == 2.5
    assert k2["margin_bits"] == 2.0
    assert k2["zone"] == "boundary-informative"
    assert k2["signal"] == "strong"
    assert k2["information_weight"] == 1.0 / 3.0

    k3 = next(row for row in data["mass_centers"] if row["k"] == 3)
    assert k3["zone"] == "pressured"
    assert k3["signal"] == "critical"

    assert "claim" in data
    assert "does not factor N" in data["claim"]


def test_opaque_mass_centers_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-mass-centers",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode == 0, result.stderr
    assert "PET OPAQUE MASS CENTERS" in result.stdout
    assert "Observed projection" in result.stdout
    assert "Mass centers" in result.stdout
    assert "PET interpretation" in result.stdout
    assert "claim = PET mass-center analysis only; this does not factor N" in result.stdout


def test_opaque_mass_centers_rejects_non_positive_integer() -> None:
    result = _run_cli(
        "opaque-mass-centers",
        "0",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode != 0
    assert "opaque-mass-centers expects integers >= 1" in result.stderr


def test_opaque_mass_centers_requires_positive_excluded_support_limit() -> None:
    result = _run_cli(
        "opaque-mass-centers",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "0",
    )

    assert result.returncode != 0
    assert "--excluded-support-limit expects integers >= 1" in result.stderr
