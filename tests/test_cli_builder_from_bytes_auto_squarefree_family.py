import json
import subprocess
import sys


THREE_SUPPORT = 1000000007 * 1000000009 * 1000000021
FOUR_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033


def _run_cli(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)


def test_cli_builder_from_bytes_auto_three_support_squarefree_builds(tmp_path):
    path = tmp_path / "pqr.bin"
    path.write_bytes(THREE_SUPPORT.to_bytes(12, "big"))

    payload = _run_cli(
        "builder-from-bytes",
        str(path),
        "--mode",
        "auto",
        "--json",
    )

    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"


def test_cli_builder_from_bytes_auto_four_support_squarefree_builds(tmp_path):
    path = tmp_path / "pqrs.bin"
    path.write_bytes(FOUR_SUPPORT.to_bytes(15, "big"))

    payload = _run_cli(
        "builder-from-bytes",
        str(path),
        "--mode",
        "auto",
        "--json",
    )

    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "irsr"
    assert payload["terminal_outcome"] == "built"
    assert payload["terminal_state"]["terminal_status"] == "built"
