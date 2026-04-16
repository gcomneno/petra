from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOL = Path("tools/pet_builder_plan.py")


def _run_json_file_command(tool: Path, payload: dict) -> dict:
    tmp = Path("tests/.tmp_pet_builder_plan.json")
    tmp.write_text(json.dumps(payload))
    try:
        proc = subprocess.run(
            [sys.executable, str(tool), str(tmp)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        tmp.unlink(missing_ok=True)
    return json.loads(proc.stdout)


def test_pet_builder_plan_reports_realize_missing_blocks_action() -> None:
    payload = {
        "schema": "pet-support-realization-v0",
        "input_n": 1234567890123,
        "builder_readiness": "not-ready",
        "builder_plan": {
            "mode": "partial-realization",
            "next_action": "realize-missing-blocks",
            "missing_block_count": 1,
            "ready_known_block_ids": [],
            "missing_unknown_block_ids": ["unknown-exp1-slots"],
        },
    }

    report = _run_json_file_command(TOOL, payload)

    assert report == {
        "schema": "pet-builder-plan-v0",
        "source_schema": "pet-support-realization-v0",
        "input_n": 1234567890123,
        "builder_readiness": "not-ready",
        "mode": "partial-realization",
        "next_action": "realize-missing-blocks",
        "missing_block_count": 1,
        "can_execute_now": False,
        "execution_status": "blocked-on-missing-realization",
        "simulated_steps": [
            {
                "step": 1,
                "kind": "inspect-missing-unknown-blocks",
                "block_ids": ["unknown-exp1-slots"],
            },
            {
                "step": 2,
                "kind": "defer-build-until-realization",
                "block_ids": ["unknown-exp1-slots"],
            },
        ],
        "script_steps": [
            {
                "step": 1,
                "command": "inspect-missing-blocks",
                "block_ids": ["unknown-exp1-slots"],
            },
            {
                "step": 2,
                "command": "realize-blocks",
                "block_ids": ["unknown-exp1-slots"],
            },
            {
                "step": 3,
                "command": "retry-builder-plan",
                "block_ids": ["unknown-exp1-slots"],
            },
        ],
        "build_artifacts": [
            {
                "artifact_id": "artifact::unknown-exp1-slots",
                "source_block_id": "unknown-exp1-slots",
                "status": "deferred-until-realization",
            },
        ],
        "build_manifest": {
            "artifact_count": 1,
            "planned_block_ids": [],
            "deferred_block_ids": ["unknown-exp1-slots"],
            "manifest_status": "deferred",
        },
        "build_result": {
            "result_status": "deferred",
            "produced_artifact_ids": [],
            "deferred_artifact_ids": ["artifact::unknown-exp1-slots"],
        },
        "action": {
            "kind": "realize-missing-blocks",
            "block_ids": ["unknown-exp1-slots"],
            "block_count": 1,
        },
    }


def test_pet_builder_plan_reports_execute_build_known_blocks_action() -> None:
    payload = {
        "schema": "pet-support-realization-v0",
        "input_n": 6,
        "builder_readiness": "ready",
        "builder_plan": {
            "mode": "exact-realized",
            "next_action": "build-known-blocks",
            "missing_block_count": 0,
            "ready_known_block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "missing_unknown_block_ids": [],
        },
    }

    report = _run_json_file_command(TOOL, payload)

    assert report == {
        "schema": "pet-builder-plan-v0",
        "source_schema": "pet-support-realization-v0",
        "input_n": 6,
        "builder_readiness": "ready",
        "mode": "exact-realized",
        "next_action": "build-known-blocks",
        "missing_block_count": 0,
        "can_execute_now": True,
        "execution_status": "simulatable-now",
        "simulated_steps": [
            {
                "step": 1,
                "kind": "load-ready-known-blocks",
                "block_ids": [
                    "unknown-exp1-slots::known-divisor-1",
                    "unknown-exp1-slots::known-divisor-2",
                ],
            },
            {
                "step": 2,
                "kind": "execute-build-known-blocks",
                "block_ids": [
                    "unknown-exp1-slots::known-divisor-1",
                    "unknown-exp1-slots::known-divisor-2",
                ],
            },
        ],
        "script_steps": [
            {
                "step": 1,
                "command": "prepare-block",
                "block_id": "unknown-exp1-slots::known-divisor-1",
            },
            {
                "step": 2,
                "command": "build-block",
                "block_id": "unknown-exp1-slots::known-divisor-1",
            },
            {
                "step": 3,
                "command": "prepare-block",
                "block_id": "unknown-exp1-slots::known-divisor-2",
            },
            {
                "step": 4,
                "command": "build-block",
                "block_id": "unknown-exp1-slots::known-divisor-2",
            },
            {
                "step": 5,
                "command": "finalize-build",
                "block_ids": [
                    "unknown-exp1-slots::known-divisor-1",
                    "unknown-exp1-slots::known-divisor-2",
                ],
            },
        ],
        "build_artifacts": [
            {
                "artifact_id": "artifact::unknown-exp1-slots::known-divisor-1",
                "source_block_id": "unknown-exp1-slots::known-divisor-1",
                "status": "planned",
            },
            {
                "artifact_id": "artifact::unknown-exp1-slots::known-divisor-2",
                "source_block_id": "unknown-exp1-slots::known-divisor-2",
                "status": "planned",
            },
        ],
        "build_manifest": {
            "artifact_count": 2,
            "planned_block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "deferred_block_ids": [],
            "manifest_status": "planned",
        },
        "build_result": {
            "result_status": "simulated-success",
            "produced_artifact_ids": [
                "artifact::unknown-exp1-slots::known-divisor-1",
                "artifact::unknown-exp1-slots::known-divisor-2",
            ],
            "deferred_artifact_ids": [],
        },
        "action": {
            "kind": "execute-build-known-blocks",
            "block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "block_count": 2,
        },
    }


def test_pet_builder_plan_simulation_is_consistent_with_action() -> None:
    payload = {
        "schema": "pet-support-realization-v0",
        "input_n": 6,
        "builder_readiness": "ready",
        "builder_plan": {
            "mode": "exact-realized",
            "next_action": "build-known-blocks",
            "missing_block_count": 0,
            "ready_known_block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "missing_unknown_block_ids": [],
        },
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["can_execute_now"] is True
    assert report["action"]["kind"] == "execute-build-known-blocks"
    assert report["simulated_steps"][-1]["kind"] == "execute-build-known-blocks"
    assert report["simulated_steps"][-1]["block_ids"] == report["action"]["block_ids"]


def test_pet_builder_plan_reports_script_steps_consistently() -> None:
    payload = {
        "schema": "pet-support-realization-v0",
        "input_n": 6,
        "builder_readiness": "ready",
        "builder_plan": {
            "mode": "exact-realized",
            "next_action": "build-known-blocks",
            "missing_block_count": 0,
            "ready_known_block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "missing_unknown_block_ids": [],
        },
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["script_steps"][0] == {
        "step": 1,
        "command": "prepare-block",
        "block_id": "unknown-exp1-slots::known-divisor-1",
    }
    assert report["script_steps"][-1] == {
        "step": 5,
        "command": "finalize-build",
        "block_ids": [
            "unknown-exp1-slots::known-divisor-1",
            "unknown-exp1-slots::known-divisor-2",
        ],
    }


def test_pet_builder_plan_reports_build_artifacts_consistently() -> None:
    payload = {
        "schema": "pet-support-realization-v0",
        "input_n": 6,
        "builder_readiness": "ready",
        "builder_plan": {
            "mode": "exact-realized",
            "next_action": "build-known-blocks",
            "missing_block_count": 0,
            "ready_known_block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "missing_unknown_block_ids": [],
        },
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["build_artifacts"] == [
        {
            "artifact_id": "artifact::unknown-exp1-slots::known-divisor-1",
            "source_block_id": "unknown-exp1-slots::known-divisor-1",
            "status": "planned",
        },
        {
            "artifact_id": "artifact::unknown-exp1-slots::known-divisor-2",
            "source_block_id": "unknown-exp1-slots::known-divisor-2",
            "status": "planned",
        },
    ]


def test_pet_builder_plan_reports_build_result_consistently() -> None:
    payload = {
        "schema": "pet-support-realization-v0",
        "input_n": 6,
        "builder_readiness": "ready",
        "builder_plan": {
            "mode": "exact-realized",
            "next_action": "build-known-blocks",
            "missing_block_count": 0,
            "ready_known_block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "missing_unknown_block_ids": [],
        },
    }

    report = _run_json_file_command(TOOL, payload)

    assert report["build_result"] == {
        "result_status": "simulated-success",
        "produced_artifact_ids": [
            "artifact::unknown-exp1-slots::known-divisor-1",
            "artifact::unknown-exp1-slots::known-divisor-2",
        ],
        "deferred_artifact_ids": [],
    }
