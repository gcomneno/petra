import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_resume_start_and_continue(tmp_path):
    state = tmp_path / "resume-state.json"

    started = _run_json(
        "opaque-resume",
        "start",
        "147184848",
        "--trial-limit",
        "100",
        "--state",
        str(state),
    )

    assert started["checked_until"] == 100
    assert started["known_factorization"] == "2^4 * 3^2"
    assert started["opaque_residual"] == 1022117
    assert started["opaque_residual_status"] == "composite_or_unknown"
    assert started["fully_factored"] is False

    continued = _run_json(
        "opaque-resume",
        "continue",
        "--trial-limit",
        "1010",
        "--state",
        str(state),
    )

    assert continued["checked_until"] == 1010
    assert continued["known_factorization"] == "2^4 * 3^2 * 1009"
    assert continued["opaque_residual"] == 1013
    assert continued["opaque_residual_status"] == "probable_prime"
    assert continued["fully_factored"] is False

    finished = _run_json(
        "opaque-resume",
        "continue",
        "--trial-limit",
        "1013",
        "--state",
        str(state),
    )

    assert finished["checked_until"] == 1013
    assert finished["known_factorization"] == "2^4 * 3^2 * 1009 * 1013"
    assert finished["opaque_residual"] == 1
    assert finished["opaque_residual_status"] == "one"
    assert finished["fully_factored"] is True
    assert "does not solve general factorization" in finished["claim"]
