import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_synthetic_profile_generates_bounded_monster_profile():
    data = _run_json(
        "opaque-synthetic-profile",
        "--target-digits",
        "50",
        "--start-prime",
        "1000000",
    )

    assert data["base"] == 72
    assert data["target_digits"] == 50
    assert data["start_prime"] == 1000000
    assert data["prime_count"] == 8
    assert data["first_prime"] == 1000003
    assert data["last_prime"] == 1000121
    assert data["n_digits"] == 50
    assert data["limits"] == [
        100000,
        1000000,
        1000003,
        1000033,
        1000081,
        1000117,
        1000121,
    ]
    assert data["rows"][0]["opaque_residual_status"] == "composite_or_unknown"
    assert data["rows"][-2]["opaque_residual_status"] == "probable_prime"
    assert data["rows"][-2]["fully_factored"] is False
    assert data["rows"][-1]["opaque_residual_status"] == "one"
    assert data["rows"][-1]["fully_factored"] is True
    assert "does not solve general factorization" in data["claim"]
