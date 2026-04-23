from __future__ import annotations

from pathlib import Path

from pet.builder_from_bytes import build_from_bytes_pipeline


THREE_SUPPORT = 1000000007 * 1000000009 * 1000000021
FOUR_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033


def test_pet_builder_from_bytes_auto_three_support_squarefree_builds(tmp_path: Path) -> None:
    path = tmp_path / "pqr.bin"
    path.write_bytes(THREE_SUPPORT.to_bytes(12, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-pqr-auto",
        mode="auto",
        direct_timeout_seconds=1.0,
    )

    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "irsr"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"


def test_pet_builder_from_bytes_auto_four_support_squarefree_builds(tmp_path: Path) -> None:
    path = tmp_path / "pqrs.bin"
    path.write_bytes(FOUR_SUPPORT.to_bytes(15, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-pqrs-auto",
        mode="auto",
        direct_timeout_seconds=1.0,
    )

    assert report["requested_mode"] == "auto"
    assert report["effective_mode"] == "irsr"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"
