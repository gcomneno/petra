from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import build_from_irsr_pipeline


def test_pet_builder_from_irsr_seeded_11413_exact_build(tmp_path: Path) -> None:
    report = build_from_irsr_pipeline(
        11413,
        tmp_path / "out11413",
        slot_candidates={"a": [101], "b": [113]},
        max_steps=5,
    )

    assert report["schema"] == "pet-builder-from-irsr-v0"
    assert report["input_n"] == 11413
    assert report["strategy"] == "seed-candidates"
    assert report["irsr_final_status"] == "built-exact-match"

    terminal = report["terminal_state"]
    assert terminal["status"] == "built"
    assert terminal["builder_readiness"] == "ready"
    assert terminal["build_status"] == "built"
    assert terminal["assembly_status"] == "assembled"

    builder = report["builder_report"]
    assert builder["schema"] == "pet-builder-from-factorization-v0"
    assert builder["support_report"]["exact_target_match"] is True
