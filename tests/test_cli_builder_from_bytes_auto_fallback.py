import json
import subprocess
import sys


HOSTILE_SEMIPRIME = 1000000007 * 1000000009


def _run_cli(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)


def test_cli_builder_from_bytes_auto_falls_back_to_seeded_irsr(tmp_path):
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    payload = _run_cli(
        "builder-from-bytes",
        str(path),
        "--mode",
        "auto",
        "--irsr-slot-candidates",
        "a=1000000007",
        "--irsr-slot-candidates",
        "b=1000000009",
        "--json",
    )

    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "irsr"
    assert payload["attempts"][0]["mode"] == "direct"
    assert payload["attempts"][0]["status"] == "timeout"
    assert payload["attempts"][1]["mode"] == "irsr"
    assert payload["attempts"][1]["status"] == "built"
    assert payload["terminal_outcome"] == "built"
    assert payload["builder_report"]["schema"] == "pet-builder-from-factorization-v0"
