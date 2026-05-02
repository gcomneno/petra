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


def test_opaque_mass_response_json_reports_hotspots() -> None:
    data = _run_json(
        "opaque-mass-response",
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
    assert data["hotspot_count"] == len(data["hotspots"])

    k2 = next(row for row in data["hotspots"] if row["k"] == 2)
    assert k2["center_bits"] == 7.0
    assert k2["margin_bits"] == 2.0
    assert k2["zone"] == "boundary-informative"
    assert k2["new_zone"] == "pressured"
    assert k2["drop_zone"] == "boundary-informative"
    assert k2["response_moves"] == ["NEW"]
    assert k2["response"] == "NEW"

    k3 = next(row for row in data["hotspots"] if row["k"] == 3)
    assert k3["zone"] == "pressured"
    assert k3["drop_zone"] == "boundary-informative"
    assert k3["response_moves"] == ["DROP"]

    assert "claim" in data
    assert "does not factor N" in data["claim"]


def test_opaque_mass_response_text_is_monkey_friendly() -> None:
    result = _run_cli(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode == 0, result.stderr
    assert "PET OPAQUE MASS RESPONSE" in result.stdout
    assert "Observed projection" in result.stdout
    assert "Response hotspots" in result.stdout
    assert "PET interpretation" in result.stdout
    assert "claim = PET mass-response analysis only; this does not factor N" in result.stdout


def test_opaque_mass_response_rejects_non_positive_integer() -> None:
    result = _run_cli(
        "opaque-mass-response",
        "0",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode != 0
    assert "opaque-mass-response expects integers >= 1" in result.stderr


def test_opaque_mass_response_requires_at_least_two_generators() -> None:
    result = _run_cli(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "1",
        "--excluded-support-limit",
        "16",
    )

    assert result.returncode != 0
    assert "--max-generator-count expects integers >= 2" in result.stderr


def test_opaque_mass_response_requires_positive_excluded_support_limit() -> None:
    result = _run_cli(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "0",
    )

    assert result.returncode != 0
    assert "--excluded-support-limit expects integers >= 1" in result.stderr
