import json
import subprocess
import sys


def _run_json(*args):
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args, "--json"],
        text=True,
    )
    return json.loads(out)


def _run_text(*args):
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_opaque_report_combines_low_peel_and_window_probe():
    data = _run_json(
        "opaque-report",
        "72008064308020281994285704",
        "--trial-limit",
        "1000000",
        "--window-start",
        "1000000",
        "--window-end",
        "1000040",
    )

    assert data["digits"] == 26
    assert data["low_peel"]["known_factorization"] == "2^3 * 3^2"
    assert data["window_probe"]["known_factorization"] == (
        "1000003 * 1000033 * 1000037 * 1000039"
    )
    assert data["window_probe"]["tested_prime_count"] == 4
    assert data["verdict"] == "partially peeled; an opaque residual remains"
    assert "does not solve general factorization" in data["claim"]


def test_cli_opaque_report_text_is_monkey_friendly():
    out = _run_text(
        "opaque-report",
        "147184848",
        "--trial-limit",
        "1013",
    )

    assert "PET OPAQUE REPORT" in out
    assert "1) Low peel" in out
    assert "known PET part = 2^4 * 3^2 * 1009 * 1013" in out
    assert "Verdict" in out
    assert "fully peeled under the selected bounded analysis" in out
    assert "opaque_residual =" not in out
