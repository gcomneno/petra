from __future__ import annotations

from pathlib import Path

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
