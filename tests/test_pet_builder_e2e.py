from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SUPPORT_TOOL = Path("tools/pet_support_realization.py")
PLAN_TOOL = Path("tools/pet_builder_plan.py")
EXEC_TOOL = Path("tools/pet_builder_execute.py")


def _run_support(payload: dict, tmp_path: Path) -> dict:
    input_path = tmp_path / "support_input.json"
    input_path.write_text(json.dumps(payload))
    proc = subprocess.run(
        [sys.executable, str(SUPPORT_TOOL), "--json", str(input_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _run_plan(report: dict, tmp_path: Path) -> dict:
    report_path = tmp_path / "support_report.json"
    report_path.write_text(json.dumps(report))
    proc = subprocess.run(
        [sys.executable, str(PLAN_TOOL), str(report_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _run_execute(plan: dict, tmp_path: Path) -> dict:
    plan_path = tmp_path / "builder_plan.json"
    out_dir = tmp_path / "builder_out"
    plan_path.write_text(json.dumps(plan))
    proc = subprocess.run(
        [sys.executable, str(EXEC_TOOL), str(plan_path), "--output-dir", str(out_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def test_pet_builder_e2e_ready_case_for_30(tmp_path: Path) -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2, 3, 5]
                },
            }
        ],
    }

    support = _run_support(payload, tmp_path)
    assert support["builder_readiness"] == "ready"
    assert support["unknown_block_count"] == 0

    plan = _run_plan(support, tmp_path)
    assert plan["builder_readiness"] == "ready"
    assert plan["action"]["kind"] == "execute-build-known-blocks"
    assert plan["action"]["block_count"] == 3

    execution = _run_execute(plan, tmp_path)
    assert execution["execution_status"] == "executed"
    assert execution["materialized_artifact_count"] == 3
    assert execution["final_build_output"]["build_status"] == "built"
    assert execution["final_build_output"]["built_pet_object"]["component_count"] == 3


def test_pet_builder_e2e_deferred_case_for_210(tmp_path: Path) -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 210,
        "target_generator": 210,
        "shape_signature": [[], [], [], []],
        "slot_count": 4,
        "exponent_multiset": [1, 1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 4,
                "target_product": 210,
                "constraints": {
                    "known_divisors": [2, 3]
                },
            }
        ],
    }

    support = _run_support(payload, tmp_path)
    assert support["builder_readiness"] == "not-ready"
    assert support["unknown_block_count"] == 1
    assert support["builder_missing_unknown_block_ids"] == ["unknown-exp1-slots"]

    plan = _run_plan(support, tmp_path)
    assert plan["builder_readiness"] == "not-ready"
    assert plan["action"]["kind"] == "realize-missing-blocks"
    assert plan["action"]["block_ids"] == ["unknown-exp1-slots"]

    execution = _run_execute(plan, tmp_path)
    assert execution["execution_status"] == "blocked"
    assert execution["materialized_artifact_count"] == 0
    assert execution["deferred_artifact_ids"] == ["artifact::unknown-exp1-slots"]
    assert execution["final_build_output"]["build_status"] == "deferred"
    assert execution["final_build_output"]["built_pet_object"]["assembly_status"] == "deferred"


def test_pet_builder_e2e_ready_case_for_12_with_duplicate_divisors(tmp_path: Path) -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 12,
        "target_generator": 12,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 12,
                "constraints": {
                    "known_divisors": [2, 2, 3]
                },
            }
        ],
    }

    support = _run_support(payload, tmp_path)
    assert support["builder_readiness"] == "ready"
    assert support["unknown_block_count"] == 0

    plan = _run_plan(support, tmp_path)
    assert plan["builder_readiness"] == "ready"
    assert plan["action"]["kind"] == "execute-build-known-blocks"
    assert plan["action"]["block_count"] == 3

    execution = _run_execute(plan, tmp_path)
    assert execution["execution_status"] == "executed"
    assert execution["materialized_artifact_count"] == 3
    assert execution["final_build_output"]["build_status"] == "built"
    assert execution["final_build_output"]["built_pet_object"]["component_count"] == 3


def test_pet_builder_e2e_deferred_not_attempted_case_for_1234567890123(tmp_path: Path) -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 1234567890123,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [
            {
                "block_id": "known-exp1-slot",
                "slot_exp": 1,
                "slot_multiplicity": 1,
                "target_product": 3,
                "constraints": {"prime_only": True, "count": 1},
            }
        ],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 2,
                "target_product": 411522630041,
                "constraints": {"prime_only": True, "count": 2},
            }
        ],
    }

    support = _run_support(payload, tmp_path)
    assert support["builder_readiness"] == "not-ready"
    assert support["unknown_block_count"] == 1
    assert support["peeling_summary"]["not_attempted_block_ids"] == ["unknown-exp1-slots"]

    plan = _run_plan(support, tmp_path)
    assert plan["builder_readiness"] == "not-ready"
    assert plan["action"]["kind"] == "realize-missing-blocks"
    assert plan["action"]["block_ids"] == ["unknown-exp1-slots"]

    execution = _run_execute(plan, tmp_path)
    assert execution["execution_status"] == "blocked"
    assert execution["materialized_artifact_count"] == 0
    assert execution["deferred_artifact_ids"] == ["artifact::unknown-exp1-slots"]
    assert execution["final_build_output"]["build_status"] == "deferred"
    assert execution["final_build_output"]["built_pet_object"]["assembly_status"] == "deferred"


def test_pet_builder_e2e_deferred_blocked_conflict_case_for_30(tmp_path: Path) -> None:
    payload = {
        "schema": "pet-support-realization-input-v0",
        "input_n": 30,
        "target_generator": 30,
        "shape_signature": [[], [], []],
        "slot_count": 3,
        "exponent_multiset": [1, 1, 1],
        "realization_goal": "exact-target",
        "known_blocks": [],
        "unknown_blocks": [
            {
                "block_id": "unknown-exp1-slots",
                "slot_exp": 1,
                "slot_multiplicity": 3,
                "target_product": 30,
                "constraints": {
                    "known_divisors": [2],
                    "forbidden_divisors": [2],
                },
            }
        ],
    }

    support = _run_support(payload, tmp_path)
    assert support["builder_readiness"] == "not-ready"
    assert support["unknown_block_count"] == 1
    assert support["peeling_summary"]["blocked_block_ids"] == ["unknown-exp1-slots"]

    plan = _run_plan(support, tmp_path)
    assert plan["builder_readiness"] == "not-ready"
    assert plan["action"]["kind"] == "realize-missing-blocks"
    assert plan["action"]["block_ids"] == ["unknown-exp1-slots"]

    execution = _run_execute(plan, tmp_path)
    assert execution["execution_status"] == "blocked"
    assert execution["materialized_artifact_count"] == 0
    assert execution["deferred_artifact_ids"] == ["artifact::unknown-exp1-slots"]
    assert execution["final_build_output"]["build_status"] == "deferred"


def test_pet_builder_e2e_from_real_cli_partial_build_payload(tmp_path: Path) -> None:
    import os

    env = os.environ.copy()
    src_path = str(Path.cwd() / "src")
    env["PYTHONPATH"] = src_path + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    cli_proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "build-from-int",
            "1234567890",
            "--allow-non-canonical-support",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    cli_payload = json.loads(cli_proc.stdout)

    assert cli_payload["schema"] == "pet-build-from-int-v2"
    assert cli_payload["input_n"] == 1234567890
    assert cli_payload["build_status"] == "partial"

    support = _run_support(cli_payload, tmp_path)
    assert support["source_schema"] == "pet-build-from-int-v2"
    assert support["builder_readiness"] == "not-ready"
    assert support["unknown_block_count"] > 0

    plan = _run_plan(support, tmp_path)
    assert plan["builder_readiness"] == "not-ready"
    assert plan["action"]["kind"] == "realize-missing-blocks"
    assert plan["can_execute_now"] is False

    execution = _run_execute(plan, tmp_path)
    assert execution["execution_status"] == "blocked"
    assert execution["materialized_artifact_count"] == 0
    assert execution["final_build_output"]["build_status"] == "deferred"
    assert execution["final_build_output"]["built_pet_object"]["assembly_status"] == "deferred"
