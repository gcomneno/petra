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
    assert k2["drop_zone"] is None
    assert k2["response_moves"] == ["NEW"]
    assert k2["response"] == "NEW"
    assert k2["threshold_crossings"] == [
        "NEW(1):boundary-informative->pressured"
    ]
    assert k2["new_trigger_span"] == 1
    assert k2["minimal_trigger_span"] == 1
    assert k2["hotspot_kind"] == "pressure-entry"
    assert k2["hotspot_kinds"] == ["pressure-entry"]
    assert k2["focus_score"] == 4

    k3 = next(row for row in data["hotspots"] if row["k"] == 3)
    assert k3["zone"] == "pressured"
    assert k3["drop_zone"] == "boundary-informative"
    assert k3["response_moves"] == ["DROP"]
    assert k3["threshold_crossings"] == [
        "DROP(1):pressured->boundary-informative"
    ]
    assert k3["drop_trigger_span"] == 1
    assert k3["minimal_trigger_span"] == 1
    assert k3["hotspot_kind"] == "recovery"
    assert k3["focus_score"] == 3

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
    assert "min_span" in result.stdout
    assert "threshold" in result.stdout
    assert "pressure-entry" in result.stdout
    assert "recovery" in result.stdout
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


def test_opaque_mass_response_uses_larger_trigger_span_when_needed() -> None:
    data = _run_json(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
    )

    k1 = next(row for row in data["hotspots"] if row["k"] == 1)
    assert k1["zone"] == "boundary-informative"
    assert k1["new_k"] == 3
    assert k1["new_zone"] == "pressured"
    assert k1["new_trigger_span"] == 2
    assert k1["minimal_trigger_span"] == 2
    assert k1["threshold_crossings"] == [
        "NEW(2):boundary-informative->pressured"
    ]


def test_opaque_mass_response_rejects_non_positive_move_span() -> None:
    result = _run_cli(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "0",
    )

    assert result.returncode != 0
    assert "--max-move-span expects integers >= 1" in result.stderr


def test_opaque_mass_response_json_reports_magnetic_bands() -> None:
    data = _run_json(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
    )

    assert data["magnetic_band_count"] == len(data["magnetic_bands"])

    pressure = next(
        band
        for band in data["magnetic_bands"]
        if band["kind"] == "pressure-entry"
    )
    assert pressure["move"] == "NEW"
    assert pressure["k_start"] == 1
    assert pressure["k_end"] == 2
    assert pressure["k_range"] == "1..2"
    assert pressure["band_width"] == 2
    assert pressure["min_trigger_span"] == 1
    assert pressure["max_trigger_span"] == 2
    assert pressure["span_range"] == "2..1"
    assert pressure["closest_k"] == 2
    assert pressure["boundary"] == "2/3"
    assert pressure["focus_score"] == 4
    assert pressure["signal"] == "critical"

    recovery = next(
        band
        for band in data["magnetic_bands"]
        if band["kind"] == "recovery"
    )
    assert recovery["move"] == "DROP"
    assert recovery["k_start"] == 3
    assert recovery["k_end"] == 4
    assert recovery["k_range"] == "3..4"
    assert recovery["span_range"] == "1..2"
    assert recovery["boundary"] == "3/2"
    assert recovery["signal"] == "strong"


def test_opaque_mass_response_bands_text_is_optional() -> None:
    without_bands = _run_cli(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
    )
    assert without_bands.returncode == 0, without_bands.stderr
    assert "\nMagnetic bands\n" not in without_bands.stdout

    with_bands = _run_cli(
        "opaque-mass-response",
        "10403",
        "--max-generator-count",
        "4",
        "--excluded-support-limit",
        "16",
        "--max-move-span",
        "2",
        "--bands",
    )
    assert with_bands.returncode == 0, with_bands.stderr
    assert "\nMagnetic bands\n" in with_bands.stdout
    assert "pressure-entry" in with_bands.stdout
    assert "recovery" in with_bands.stdout
