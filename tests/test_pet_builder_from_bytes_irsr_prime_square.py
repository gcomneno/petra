from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


PRIME_SQUARE = 1000000007 * 1000000007


def test_pet_builder_from_bytes_irsr_prime_square_builds_with_square_solver(tmp_path: Path) -> None:
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
    assert report["attempts"][0]["status"] == "built"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"
    assert report["builder_report"] is not None
