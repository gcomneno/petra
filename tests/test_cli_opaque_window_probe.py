import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_window_probe_finds_factor_inside_window():
    data = _run_json(
        "opaque-window-probe",
        "147184848",
        "--start",
        "1000",
        "--end",
        "1010",
    )

    assert data["n"] == 147184848
    assert data["window_start"] == 1000
    assert data["window_end"] == 1010
    assert data["known_factors"] == [
        {"prime": 1009, "exponent": 1},
    ]
    assert data["known_factorization"] == "1009"
    assert data["opaque_residual"] == 145872
    assert data["opaque_residual_status"] == "composite_or_unknown"
    assert data["fully_factored"] is False
    assert "does not solve general factorization" in data["claim"]


def test_cli_opaque_window_probe_reports_empty_window_hit():
    data = _run_json(
        "opaque-window-probe",
        "147184848",
        "--start",
        "1011",
        "--end",
        "1012",
    )

    assert data["known_factors"] == []
    assert data["known_factorization"] == "1"
    assert data["opaque_residual"] == 147184848
    assert data["opaque_residual_status"] == "composite_or_unknown"
    assert data["fully_factored"] is False


def test_cli_opaque_window_probe_can_probe_around_sqrt():
    data = _run_json(
        "opaque-window-probe",
        "10403",
        "--around-sqrt",
        "--radius",
        "0",
    )

    assert data["window_start"] == 101
    assert data["window_end"] == 101
    assert data["tested_prime_count"] == 1
    assert data["known_factors"] == [
        {"prime": 101, "exponent": 1},
    ]
    assert data["known_factorization"] == "101"
    assert data["opaque_residual"] == 103
    assert data["opaque_residual_status"] == "probable_prime"
    assert data["fully_factored"] is False
