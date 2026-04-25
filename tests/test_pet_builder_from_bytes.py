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


def test_pet_builder_from_bytes_irsr_blocks_large_input_before_running_irsr(
    tmp_path: Path,
) -> None:
    path = tmp_path / "large-randomish.bin"
    path.write_bytes(bytes(range(1, 33)))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-large",
        mode="irsr",
    )

    assert report["schema"] == "pet-builder-from-bytes-v1"
    assert report["byte_count"] == 32
    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "none"
    assert report["attempts"] == []
    assert report["builder_report"] is None
    assert report["terminal_outcome"] == "blocked"
    assert report["terminal_state"] == {
        "terminal_status": "blocked",
        "block_reason": "input-too-large-for-default-irsr-budget",
        "byte_count": 32,
        "effective_byte_count": 32,
        "max_input_bytes": 20,
    }


def test_pet_builder_from_bytes_irsr_allows_padded_supported_input(
    tmp_path: Path,
) -> None:
    n = 101 * 103 * 107
    path = tmp_path / "padded-squarefree.bin"
    path.write_bytes(n.to_bytes(20, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-padded-squarefree",
        mode="irsr",
    )

    assert report["byte_count"] == 20
    assert report["input_n"] == n
    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "irsr"
    assert report["terminal_outcome"] == "built"


def test_pet_builder_from_bytes_accepts_injected_irsr_structural_policy(
    tmp_path: Path,
) -> None:
    policy = {
        "allowed_exponent_profiles": {
            "max_support_size": 3,
            "max_total_weight": 4,
            "radius_default": 16,
            "deferred_profiles": [],
        },
        "squarefree_support_size_range": [3, 3],
        "squarefree_radius_default": 16,
        "squarefree_radius_overrides": {},
    }

    n = 100003**2 * 100019 * 100043
    path = tmp_path / "square-times-two-primes.bin"
    path.write_bytes(n.to_bytes((n.bit_length() + 7) // 8, "big"))

    report = build_from_bytes_pipeline(
        path,
        tmp_path / "out-policy-injected",
        mode="irsr",
        irsr_structural_radius=64,
        irsr_structural_policy=policy,
    )

    assert report["input_n"] == n
    assert report["requested_mode"] == "irsr"
    assert report["effective_mode"] == "irsr"
    assert report["terminal_outcome"] == "built"
    assert report["terminal_state"]["terminal_status"] == "built"
    assert report["builder_report"]["support_report"]["exponent_multiset"] == [2, 1, 1]
