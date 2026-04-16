from __future__ import annotations

from pathlib import Path

import pytest

from pet.builder_from_int import build_from_int_pipeline


def test_pet_builder_from_int_runs_canonical_case_for_30(tmp_path: Path) -> None:
    report = build_from_int_pipeline(30, tmp_path / "out30")

    assert report["schema"] == "pet-builder-from-int-v0"
    assert report["input_n"] == 30
    assert report["cli_payload"]["input_n"] == 30
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["builder_plan"]["can_execute_now"] is True
    assert report["builder_execution"]["execution_status"] == "executed"
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["assembly_status"] == "assembled"
    assert report["final_build_output"]["built_pet_object"]["component_count"] == 3


def test_pet_builder_from_int_runs_partial_case_for_18(tmp_path: Path) -> None:
    report = build_from_int_pipeline(18, tmp_path / "out18")

    assert report["schema"] == "pet-builder-from-int-v0"
    assert report["input_n"] == 18
    assert report["cli_payload"]["schema"] == "pet-build-from-int-v2"
    assert report["cli_payload"]["build_status"] == "partial"
    assert report["support_report"]["builder_readiness"] == "ready"
    assert report["builder_plan"]["can_execute_now"] is True
    assert report["builder_execution"]["execution_status"] == "executed"
    assert report["final_build_output"]["build_status"] == "built"
    assert report["final_build_output"]["built_pet_object"]["assembly_status"] == "assembled"
    assert report["final_build_output"]["built_pet_object"]["component_count"] == 2


@pytest.mark.parametrize(
    ("n", "expected_component_count", "expected_cli_kind"),
    [
        (18, 2, "partial"),
        (20, 2, "partial"),
        (30, 3, "canonical"),
        (84, 3, "partial"),
        (210, 4, "canonical"),
        (240, 3, "canonical"),
        (1260, 4, "canonical"),
        (5040, 4, "canonical"),
        (1234567890, 5, "partial"),
        (1234567890123, 3, "partial"),
        (1606938044258990275541962092341162602522202993782792835301376, 1, "canonical"),
        (7858321551080267055879090, 19, "canonical"),
        (12345678901234567890, 8, "partial"),
    ],
)
def test_pet_builder_from_int_matrix_real_cases(
    tmp_path: Path,
    n: int,
    expected_component_count: int,
    expected_cli_kind: str,
) -> None:
    report = build_from_int_pipeline(n, tmp_path / f"out-{n}")

    assert report["schema"] == "pet-builder-from-int-v0"
    assert report["input_n"] == n
    assert report["builder_execution"]["execution_status"] == "executed"
    assert report["final_build_output"]["build_status"] == "built"

    built = report["final_build_output"]["built_pet_object"]
    assert built["assembly_status"] == "assembled"
    assert built["component_count"] == expected_component_count
    assert built["artifact_count"] == expected_component_count

    cli_payload = report["cli_payload"]
    if expected_cli_kind == "canonical":
        assert "schema" not in cli_payload
        assert cli_payload["input_n"] == n
        assert cli_payload["target_n"] == n
    elif expected_cli_kind == "partial":
        assert cli_payload["schema"] == "pet-build-from-int-v2"
        assert cli_payload["input_n"] == n
        assert cli_payload["build_status"] == "partial"
    else:
        raise AssertionError(f"unexpected expected_cli_kind={expected_cli_kind!r}")
