import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_window_resume_start_and_continue(tmp_path):
    state = tmp_path / "window-resume.json"

    started = _run_json(
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

    assert started["window_start"] == 1000
    assert started["window_end"] == 1010
    assert started["checked_ranges"] == [
        {"kind": "window", "start": 1000, "end": 1010},
    ]
    assert started["known_factorization"] == "1009"
    assert started["opaque_residual"] == 145872
    assert started["fully_factored"] is False

    continued = _run_json(
        "opaque-window-resume",
        "continue",
        "--end",
        "1013",
        "--state",
        str(state),
    )

    assert continued["window_start"] == 1011
    assert continued["window_end"] == 1013
    assert continued["checked_ranges"] == [
        {"kind": "window", "start": 1000, "end": 1010},
        {"kind": "window", "start": 1011, "end": 1013},
    ]
    assert continued["known_factorization"] == "1009 * 1013"
    assert continued["opaque_residual"] == 144
    assert continued["opaque_residual_status"] == "composite_or_unknown"
    assert continued["fully_factored"] is False
    assert "does not solve general factorization" in continued["claim"]
