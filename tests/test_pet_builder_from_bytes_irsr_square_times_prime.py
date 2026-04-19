from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


SQUARE_TIMES_PRIME = (1000000007 * 1000000007) * 1000000009
PRIME_CUBE = 1000000007 * 1000000007 * 1000000007


def test_pet_builder_from_bytes_irsr_square_times_prime_builds_with_new_solver(tmp_path: Path) -> None:
    path = tmp_path / "p2q.bin"
    path.write_bytes(SQUARE_TIMES_PRIME.to_bytes(12, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-p2q",
        mode="irsr",
    )

    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "irsr"
    assert report["attempts"][0]["mode"] == "irsr"
    assert report["attempts"][0]["status"] == "built"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"
    assert report["builder_report"] is not None


def test_pet_builder_from_bytes_irsr_prime_cube_does_not_fake_square_times_prime(tmp_path: Path) -> None:
    path = tmp_path / "p3.bin"
    path.write_bytes(PRIME_CUBE.to_bytes(12, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-p3",
        mode="irsr",
    )

    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "irsr"
    assert report["terminal_outcome"] == "blocked"
