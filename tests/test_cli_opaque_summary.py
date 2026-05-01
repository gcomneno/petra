import subprocess
import sys


def _run_text(*args):
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_opaque_probe_summary_omits_raw_residual():
    out = _run_text(
        "opaque-probe",
        "147184848",
        "--trial-limit",
        "1010",
        "--summary",
    )

    assert "trial_limit = 1010" in out
    assert "known_factorization = 2^4 * 3^2 * 1009" in out
    assert "opaque_residual_digits = 4" in out
    assert "opaque_residual_status = probable_prime" in out
    assert "opaque_residual = " not in out


def test_cli_opaque_window_probe_summary_omits_raw_residual_and_reports_window():
    out = _run_text(
        "opaque-window-probe",
        "147184848",
        "--start",
        "1000",
        "--end",
        "1010",
        "--summary",
    )

    assert "window_start = 1000" in out
    assert "window_end = 1010" in out
    assert "tested_prime_count = 1" in out
    assert "known_factorization = 1009" in out
    assert "opaque_residual_digits = 6" in out
    assert "opaque_residual = " not in out


def test_cli_opaque_resume_summary_omits_raw_residual(tmp_path):
    state = tmp_path / "resume.json"

    out = _run_text(
        "opaque-resume",
        "start",
        "147184848",
        "--trial-limit",
        "100",
        "--state",
        str(state),
        "--summary",
    )

    assert "checked_until = 100" in out
    assert "known_factorization = 2^4 * 3^2" in out
    assert "opaque_residual_digits = 7" in out
    assert "opaque_residual = " not in out
