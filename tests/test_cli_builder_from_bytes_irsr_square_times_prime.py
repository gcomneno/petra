import json
import subprocess
import sys


SQUARE_TIMES_PRIME = (1000000007 * 1000000007) * 1000000009


def _run_cli(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)


def test_cli_builder_from_bytes_irsr_square_times_prime_builds_with_new_solver(tmp_path):
    path = tmp_path / "p2q.bin"
    path.write_bytes(SQUARE_TIMES_PRIME.to_bytes(12, "big"))

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
