import json
import subprocess
import sys


def _run_cli(*args: str) -> str:
    return subprocess.check_output(
        [sys.executable, "-m", "pet.cli", *args],
        text=True,
    )


def test_cli_builder_from_bytes_json_smoke_for_240(tmp_path):
    path = tmp_path / "blob.bin"
    path.write_bytes(bytes([0x00, 0xF0]))  # 240 big-endian

    out = _run_cli("builder-from-bytes", str(path), "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["file"] == str(path)
    assert payload["byteorder"] == "big"
    assert payload["signed"] is False
    assert payload["byte_count"] == 2
    assert payload["hex"] == "00f0"
    assert payload["input_n"] == 240
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "direct"
    assert payload["attempts"][0]["mode"] == "direct"
    assert payload["terminal_outcome"] == "built"
    assert payload["builder_report"]["schema"] == "pet-builder-from-int-v0"


def test_cli_builder_from_bytes_empty_file_is_structured_blocked(tmp_path):
    path = tmp_path / "empty.bin"
    path.write_bytes(b"")

    out = _run_cli("builder-from-bytes", str(path), "--json")
    payload = json.loads(out)

    assert payload["schema"] == "pet-builder-from-bytes-v1"
    assert payload["requested_mode"] == "auto"
    assert payload["effective_mode"] == "none"
    assert payload["attempts"] == []
    assert payload["byte_count"] == 0
    assert payload["input_n"] == 0
    assert payload["terminal_outcome"] == "blocked"
    assert payload["terminal_state"]["terminal_status"] == "blocked"
    assert payload["terminal_state"]["block_reason"] == "empty-input"
    assert payload["builder_report"] is None
