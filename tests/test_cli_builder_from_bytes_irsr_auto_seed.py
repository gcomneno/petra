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


def test_cli_builder_from_bytes_irsr_without_explicit_seeds_uses_auto_seed_radius_1(tmp_path):
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    payload = _run_cli(
        "builder-from-bytes",
        str(path),
        "--mode",
        "irsr",
        "--json",
    )

    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["attempts"][0]["mode"] == "irsr"
    assert payload["attempts"][0]["status"] == "built"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
