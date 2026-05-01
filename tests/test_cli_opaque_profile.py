import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def test_cli_opaque_profile_reports_progressive_residual_status():
    data = _run_json(
        "opaque-profile",
        "147184848",
        "--limits",
        "100,1000,1010,1013",
    )

    assert data["n"] == 147184848
    assert data["digits"] == 9
    assert data["limits"] == [100, 1000, 1010, 1013]
    assert data["rows"] == [
        {
            "trial_limit": 100,
            "known_count": 2,
            "opaque_residual_digits": 7,
            "opaque_residual_bit_length": 20,
            "opaque_residual_status": "composite_or_unknown",
            "fully_factored": False,
        },
        {
            "trial_limit": 1000,
            "known_count": 2,
            "opaque_residual_digits": 7,
            "opaque_residual_bit_length": 20,
            "opaque_residual_status": "composite_or_unknown",
            "fully_factored": False,
        },
        {
            "trial_limit": 1010,
            "known_count": 3,
            "opaque_residual_digits": 4,
            "opaque_residual_bit_length": 10,
            "opaque_residual_status": "probable_prime",
            "fully_factored": False,
        },
        {
            "trial_limit": 1013,
            "known_count": 4,
            "opaque_residual_digits": 1,
            "opaque_residual_bit_length": 1,
            "opaque_residual_status": "one",
            "fully_factored": True,
        },
    ]
    assert "does not solve general factorization" in data["claim"]


def test_cli_opaque_profile_preserves_requested_limit_order_and_duplicates():
    data = _run_json(
        "opaque-profile",
        "147184848",
        "--limits",
        "1013,100,1010,100,1013",
    )

    assert data["limits"] == [1013, 100, 1010, 100, 1013]
    assert [row["trial_limit"] for row in data["rows"]] == [
        1013,
        100,
        1010,
        100,
        1013,
    ]
    assert [row["opaque_residual_status"] for row in data["rows"]] == [
        "one",
        "composite_or_unknown",
        "probable_prime",
        "composite_or_unknown",
        "one",
    ]
    assert [row["fully_factored"] for row in data["rows"]] == [
        True,
        False,
        False,
        False,
        True,
    ]
