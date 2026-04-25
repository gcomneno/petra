from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


HOSTILE_SEMIPRIME = 1000000007 * 1000000009


def test_pet_builder_from_bytes_irsr_incomplete_seed_reports_no_payload_candidates(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-incomplete",
        mode="irsr",
        irsr_slot_candidates={"a": [1000000007]},
    )

    assert report["terminal_outcome"] == "blocked"
    assert report["attempts"][0]["mode"] == "irsr"
    assert report["attempts"][0]["status"] == "blocked"
    assert report["attempts"][0]["detail"] == "no-payload-candidates"
    assert report["terminal_state"]["block_reason"] == "irsr-no-payload-candidates"


def test_pet_builder_from_bytes_irsr_ambiguous_seed_reports_payloads_nonexact(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-ambiguous",
        mode="irsr",
        irsr_slot_candidates={"a": [1000000007], "b": [1000000007, 1000000009]},
    )

    assert report["terminal_outcome"] == "blocked"
    assert report["attempts"][0]["mode"] == "irsr"
    assert report["attempts"][0]["status"] == "blocked"
    assert report["attempts"][0]["detail"] == "payloads-nonexact"
    assert report["terminal_state"]["block_reason"] == "irsr-payloads-nonexact"


def test_pet_builder_from_bytes_auto_fallback_preserves_irsr_nonexact_reason(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-auto-ambiguous",
        mode="auto",
        irsr_slot_candidates={"a": [1000000007], "b": [1000000007, 1000000009]},
        direct_timeout_seconds=1.0,
    )

    assert report["effective_mode"] == "irsr"
    assert report["attempts"][0]["mode"] == "direct"
    assert report["attempts"][0]["status"] == "timeout"
    assert report["attempts"][1]["mode"] == "irsr"
    assert report["attempts"][1]["status"] == "blocked"
    assert report["attempts"][1]["detail"] == "payloads-nonexact"
    assert report["terminal_outcome"] == "blocked"
    assert report["terminal_state"]["block_reason"] == "irsr-payloads-nonexact"
