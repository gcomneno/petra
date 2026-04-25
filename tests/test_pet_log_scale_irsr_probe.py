import subprocess
import sys


def test_log_scale_irsr_probe_finds_asymmetric_semiprime() -> None:
    out = subprocess.check_output(
        [
            sys.executable,
            "tools/pet_log_scale_irsr_probe.py",
            "3465924001",
            "--radius",
            "16",
            "--max-denominator",
            "8",
        ],
        text=True,
    )

    assert "matched = True" in out
    assert "match = (71, 48815831)" in out
    assert "product_ok = True" in out
    assert "scale [1/5, 4/5]" in out


def test_log_scale_irsr_probe_builds_asymmetric_semiprime(tmp_path) -> None:
    out = subprocess.check_output(
        [
            sys.executable,
            "tools/pet_log_scale_irsr_probe.py",
            "3465924001",
            "--radius",
            "16",
            "--max-denominator",
            "8",
            "--build",
            "--artifacts-dir",
            str(tmp_path / "artifacts"),
        ],
        text=True,
    )

    assert "matched = True" in out
    assert "match = (71, 48815831)" in out
    assert "product_ok = True" in out
    assert "exponent_multiset = [1, 1]" in out
    assert "terminal_build_status = built" in out
    assert "artifact__p71-exp1.json" in out
    assert "artifact__p48815831-exp1.json" in out
