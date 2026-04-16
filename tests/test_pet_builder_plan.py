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
        "action": {
            "kind": "execute-build-known-blocks",
            "block_ids": [
                "unknown-exp1-slots::known-divisor-1",
                "unknown-exp1-slots::known-divisor-2",
            ],
            "block_count": 2,
        },
    }
