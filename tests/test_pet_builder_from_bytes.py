from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


def test_pet_builder_from_bytes_runs_canonical_case_for_240(tmp_path: Path) -> None:
    path = tmp_path / "n240.bin"
    path.write_bytes((240).to_bytes(2, "big"))

    report = build_from_bytes_pipeline(path, tmp_path / "out240")

    assert report["schema"] == "pet-builder-from-bytes-v1"
    assert report["file"] == str(path)
    assert report["byteorder"] == "big"
    assert report["signed"] is False
    assert report["byte_count"] == 2
    assert report["hex"] == "00f0"
    assert report["input_n"] == 240
    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "direct"
    assert report["attempts"][0]["mode"] == "direct"
    assert report["terminal_outcome"] == "built"

    builder = report["builder_report"]
    assert builder["schema"] == "pet-builder-from-int-v0"
    assert builder["input_n"] == 240
    assert builder["final_build_output"]["build_status"] == "built"
    assert builder["final_build_output"]["built_pet_object"]["assembly_status"] == "assembled"


def test_pet_builder_from_bytes_reports_exact_terminal_state_for_11413(tmp_path: Path) -> None:
    path = tmp_path / "n11413.bin"
    path.write_bytes((11413).to_bytes(2, "big"))

    report = build_from_bytes_pipeline(path, tmp_path / "out11413")

    assert report["schema"] == "pet-builder-from-bytes-v1"
    assert report["input_n"] == 11413
    assert report["byte_count"] == 2
    assert report["hex"] == "2c95"
    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "direct"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"

    builder = report["builder_report"]
    assert builder["schema"] == "pet-builder-from-int-v0"
    assert builder["support_report"]["exact_target_match"] is True
    assert builder["support_report"]["reconstructed_target_n"] == 11413
    assert builder["final_build_output"]["build_status"] == "built"
    assert builder["final_build_output"]["built_pet_object"]["assembly_status"] == "assembled"


def test_pet_builder_from_bytes_blocks_empty_input_cleanly(tmp_path: Path) -> None:
    path = tmp_path / "empty.bin"
    path.write_bytes(b"")

    report = build_from_bytes_pipeline(path, tmp_path / "out-empty")

    assert report["schema"] == "pet-builder-from-bytes-v1"
    assert report["file"] == str(path)
    assert report["byte_count"] == 0
    assert report["hex"] == ""
    assert report["input_n"] == 0
    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "none"
    assert report["attempts"] == []
    assert report["terminal_outcome"] == "blocked"
    assert report["terminal_state"]["terminal_status"] == "blocked"
    assert report["terminal_state"]["block_reason"] == "empty-input"
    assert report["builder_report"] is None
