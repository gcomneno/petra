from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


HOSTILE_SEMIPRIME = 1000000007 * 1000000009


def test_pet_builder_from_bytes_auto_without_explicit_seeds_falls_back_to_irsr_auto_seed(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-auto-auto-seed",
        mode="auto",
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
