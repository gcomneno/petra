import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_probe_reports_full_known_factorization():
    data = _run_json("opaque-probe", "37000", "--trial-limit", "50")

    assert data["n"] == 37000
    assert data["digits"] == 5
    assert data["bit_length"] == 16
    assert data["trial_limit"] == 50
    assert data["known_factors"] == [
        {"prime": 2, "exponent": 3},
        {"prime": 5, "exponent": 3},
        {"prime": 37, "exponent": 1},
    ]
    assert data["known_factorization"] == "2^3 * 5^3 * 37"
    assert data["opaque_residual"] == 1
    assert data["fully_factored"] is True


def test_cli_opaque_probe_leaves_unfactored_residual():
    data = _run_json("opaque-probe", "8051", "--trial-limit", "90")

    assert data["known_factors"] == [
        {"prime": 83, "exponent": 1},
    ]
    assert data["known_factorization"] == "83"
    assert data["opaque_residual"] == 97
    assert data["opaque_residual_digits"] == 2
    assert data["opaque_residual_bit_length"] == 7
    assert data["fully_factored"] is False
    assert "does not solve general factorization" in data["claim"]
