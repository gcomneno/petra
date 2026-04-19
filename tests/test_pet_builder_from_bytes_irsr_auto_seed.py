from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


HOSTILE_SEMIPRIME = 1000000007 * 1000000009


def test_pet_builder_from_bytes_irsr_without_explicit_seeds_uses_auto_seed_radius_1(tmp_path: Path) -> None:
    path = tmp_path / "hostile.bin"
    path.write_bytes(HOSTILE_SEMIPRIME.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-auto-seed",
        mode="irsr",
    )

    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "irsr"
    assert report["attempts"][0]["mode"] == "irsr"
    assert report["attempts"][0]["status"] == "built"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"
    assert report["builder_report"]["schema"] == "pet-builder-from-factorization-v0"
