import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_benchmark_probe_reports_runtime_and_summary():
    data = _run_json(
        "opaque-benchmark",
        "probe",
        "147184848",
        "--trial-limit",
        "1013",
    )

    assert data["mode"] == "probe"
    assert isinstance(data["elapsed_seconds"], float)
    assert data["elapsed_seconds"] >= 0
    assert data["digits"] == 9
    assert data["bit_length"] == 28
    assert data["trial_limit"] == 1013
    assert data["known_factorization"] == "2^4 * 3^2 * 1009 * 1013"
    assert data["opaque_residual_digits"] == 1
    assert data["opaque_residual_status"] == "one"
    assert data["fully_factored"] is True
    assert "does not solve general factorization" in data["claim"]
