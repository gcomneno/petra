from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


HOSTILE_SEMIPRIME = 1000000007 * 1000000009


def test_pet_builder_from_bytes_auto_falls_back_to_seeded_irsr_on_direct_timeout(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-hostile",
        mode="auto",
        irsr_slot_candidates={"a": [1000000007], "b": [1000000009]},
        direct_timeout_seconds=1.0,
    )

    assert report["schema"] == "pet-builder-from-bytes-v1"
    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "irsr"
    assert report["attempts"][0]["mode"] == "direct"
    assert report["attempts"][0]["status"] == "timeout"
    assert report["attempts"][1]["mode"] == "irsr"
    assert report["attempts"][1]["status"] == "built"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"
    assert report["builder_report"]["schema"] == "pet-builder-from-factorization-v0"


def test_pet_builder_from_bytes_auto_blocks_on_direct_timeout_without_irsr_seed_candidates(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-hostile-no-seeds",
        mode="auto",
        direct_timeout_seconds=1.0,
    )

    assert report["schema"] == "pet-builder-from-bytes-v1"
    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "direct"
    assert report["attempts"] == [
        {
            "mode": "direct",
            "status": "timeout",
            "detail": "direct factoring budget exceeded",
        }
    ]
    assert report["builder_report"] is None
    assert report["terminal_outcome"] == "blocked"
    assert report["terminal_state"]["terminal_status"] == "blocked"
    assert report["terminal_state"]["block_reason"] == "direct-timeout"
