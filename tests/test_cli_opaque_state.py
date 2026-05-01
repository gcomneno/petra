import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_state_summarizes_low_peel_state(tmp_path):
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

    data = _run_json("opaque-state", "summarize", str(state))

    assert data["kind"] == "pet-opaque-resume-state"
    assert data["known_factorization"] == "2^4 * 3^2"
    assert data["opaque_residual_digits"] == 7
    assert data["opaque_residual_status"] == "composite_or_unknown"
    assert data["checked_ranges"] == [
        {"kind": "low-peel", "start": 2, "end": 100},
    ]
    assert data["checked_range_count"] == 1
    assert "does not solve general factorization" in data["claim"]


def test_cli_opaque_state_summarizes_window_resume_state(tmp_path):
    state = tmp_path / "window-resume-state.json"

    _run_json(
        "opaque-window-resume",
        "start",
        "147184848",
        "--start",
        "1000",
        "--end",
        "1010",
        "--state",
        str(state),
    )
    _run_json(
        "opaque-window-resume",
        "continue",
        "--end",
        "1013",
        "--state",
        str(state),
    )

    data = _run_json("opaque-state", "summarize", str(state))

    assert data["kind"] == "pet-opaque-window-resume-state"
    assert data["known_factorization"] == "1009 * 1013"
    assert data["opaque_residual"] == 144
    assert data["checked_ranges"] == [
        {"kind": "window", "start": 1000, "end": 1010},
        {"kind": "window", "start": 1011, "end": 1013},
    ]
    assert data["checked_range_count"] == 2
    assert "does not solve general factorization" in data["claim"]
