import json
import subprocess
import sys


NONPRIME_SQUARE = 1000000008 * 1000000008


def _run_cli(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)


def test_cli_builder_from_bytes_irsr_auto_seed_nonprime_square_reports_semiprime_model_mismatch(tmp_path):
    path = tmp_path / "square.bin"
    path.write_bytes(NONPRIME_SQUARE.to_bytes(8, "big"))

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
    assert payload["attempts"][0]["status"] == "blocked"
    assert payload["attempts"][0]["detail"] == "semiprime-model-mismatch"
    assert payload["terminal_outcome"] == "blocked"
    assert payload["terminal_state"]["block_reason"] == "irsr-semiprime-model-mismatch"
