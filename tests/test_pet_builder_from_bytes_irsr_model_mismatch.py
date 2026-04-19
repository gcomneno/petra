from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


PRIME_SQUARE = 1000000007 * 1000000007


def test_pet_builder_from_bytes_irsr_auto_seed_prime_square_reports_semiprime_model_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "square.bin"
    path.write_bytes(PRIME_SQUARE.to_bytes(8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-square",
        mode="irsr",
    )

    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "irsr"
    assert report["attempts"][0]["mode"] == "irsr"
    assert report["attempts"][0]["status"] == "blocked"
    assert report["attempts"][0]["detail"] == "semiprime-model-mismatch"
    assert report["terminal_outcome"] == "blocked"
    assert report["terminal_state"]["block_reason"] == "irsr-semiprime-model-mismatch"
