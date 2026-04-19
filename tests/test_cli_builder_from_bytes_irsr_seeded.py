import json
import subprocess
import sys


def _run_cli(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)


def test_cli_builder_from_bytes_irsr_seeded_11413(tmp_path):
    path = tmp_path / "n11413.bin"
    path.write_bytes((11413).to_bytes(2, "big"))

    payload = _run_cli(
        "builder-from-bytes",
        str(path),
        "--mode",
        "irsr",
        "--irsr-slot-candidates",
        "a=101",
        "--irsr-slot-candidates",
        "b=113",
        "--json",
    )

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["attempts"][0]["mode"] == "irsr"
    assert payload["attempts"][0]["status"] == "built"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
    assert payload["builder_report"]["schema"] == "pet-builder-from-factorization-v0"


def test_cli_builder_from_bytes_irsr_without_seed_candidates_blocks(tmp_path):
    path = tmp_path / "n11413.bin"
    path.write_bytes((11413).to_bytes(2, "big"))

    payload = _run_cli(
        "builder-from-bytes",
        str(path),
        "--mode",
        "irsr",
        "--json",
    )

    assert payload["requested_mode"] == "irsr"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "blocked"
    assert payload["terminal_state"]["block_reason"] == "irsr-no-viable-payload"
