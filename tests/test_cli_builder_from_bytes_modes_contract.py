import json
import subprocess
import sys


def _run_cli(*args: str) -> dict:
    out = subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )
    return json.loads(out)


def test_builder_from_bytes_v1_contract_blocked_empty(tmp_path):
    path = tmp_path / "empty.bin"
    path.write_bytes(b"")

    payload = _run_cli("builder-from-bytes", str(path), "--mode", "auto", "--json")

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "none"
    assert payload["attempts"] == []
    assert payload["builder_report"] is None
    assert payload["terminal_outcome"] == "blocked"
    assert payload["terminal_state"]["terminal_status"] == "blocked"
    assert payload["terminal_state"]["block_reason"] == "empty-input"


def test_builder_from_bytes_v1_contract_auto_direct(tmp_path):
    path = tmp_path / "n240.bin"
    path.write_bytes((240).to_bytes(2, "big"))

    payload = _run_cli("builder-from-bytes", str(path), "--mode", "auto", "--json")

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] in {"direct", "irsr"}
    assert isinstance(payload["attempts"], list)
    assert payload["terminal_outcome"] in {"built", "assembled", "blocked"}


def test_builder_from_bytes_v1_contract_direct_mode_declares_itself(tmp_path):
    path = tmp_path / "n240.bin"
    path.write_bytes((240).to_bytes(2, "big"))

    payload = _run_cli("builder-from-bytes", str(path), "--mode", "direct", "--json")

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["requested_mode"] == "direct"
    assert payload["effective_mode"] == "direct"
    assert payload["attempts"][0]["mode"] == "direct"
