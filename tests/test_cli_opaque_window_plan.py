import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_window_plan_reports_balanced_semiprime_window():
    rsa250_digits_only = int("9" * 250)

    data = _run_json(
        "opaque-window-plan",
        str(rsa250_digits_only),
        "--policy",
        "balanced-semiprime",
    )

    assert data["digits"] == 250
    assert data["policy"] == "balanced-semiprime"
    assert data["candidate_factor_digits"] == 125
    assert data["low_digits"] == 125
    assert data["high_digits"] == 126
    assert data["decimal_window_low_power"] == 124
    assert data["decimal_window_high_power"] == 125
    assert data["decimal_window_low"] == "10^124"
    assert data["decimal_window_high"] == "10^125"
    assert data["secondary_decimal_window_low"] == "10^124"
    assert data["secondary_decimal_window_high"] == "10^126"
    assert "does not factor N" in data["claim"]
