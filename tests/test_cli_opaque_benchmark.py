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


def test_cli_opaque_benchmark_resume_reports_incremental_runtime(tmp_path):
    state = tmp_path / "resume-state.json"

    _run_json(
        "opaque-resume",
        "start",
        "147184848",
        "--trial-limit",
        "100",
        "--state",
        str(state),
    )

    data = _run_json(
        "opaque-benchmark",
        "resume",
        "--trial-limit",
        "1013",
        "--state",
        str(state),
    )

    assert data["mode"] == "resume"
    assert isinstance(data["elapsed_seconds"], float)
    assert data["elapsed_seconds"] >= 0
    assert data["previous_checked_until"] == 100
    assert data["checked_until"] == 1013
    assert data["known_factorization"] == "2^4 * 3^2 * 1009 * 1013"
    assert data["opaque_residual_status"] == "one"
    assert data["fully_factored"] is True
    assert "does not solve general factorization" in data["claim"]

    state_data = json.loads(state.read_text())
    assert state_data["checked_until"] == 1013
