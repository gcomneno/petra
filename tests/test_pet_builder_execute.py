from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOL = Path("tools/pet_builder_execute.py")


def _run_json_file_command(tool: Path, payload: dict, output_dir: Path) -> dict:
    tmp = output_dir.parent / ".tmp_pet_builder_execute_plan.json"
    tmp.write_text(json.dumps(payload))
    try:
        proc = subprocess.run(
            [sys.executable, str(tool), str(tmp), "--output-dir", str(output_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        tmp.unlink(missing_ok=True)
    return json.loads(proc.stdout)


def test_pet_builder_execute_materializes_planned_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    payload = {
        "schema": "pet-builder-plan-v0",
        "input_n": 6,
        "can_execute_now": True,
        "action": {"kind": "execute-build-known-blocks"},
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
    }

    report = _run_json_file_command(TOOL, payload, output_dir)

    assert report["schema"] == "pet-builder-execution-v0"
    assert report["source_schema"] == "pet-builder-plan-v0"
    assert report["input_n"] == 6
    assert report["action_kind"] == "execute-build-known-blocks"
    assert report["can_execute_now"] is True
    assert report["execution_status"] == "executed"
    assert report["materialized_artifact_count"] == 2
    assert report["produced_artifact_ids"] == [
        "artifact::unknown-exp1-slots::known-divisor-1",
        "artifact::unknown-exp1-slots::known-divisor-2",
    ]
    assert report["deferred_artifact_ids"] == []
    assert len(report["produced_files"]) == 2

    produced_paths = [Path(p) for p in report["produced_files"]]
    for produced_path in produced_paths:
        assert produced_path.exists()

    first_artifact = json.loads(produced_paths[0].read_text())
    assert first_artifact["schema"] == "pet-builder-artifact-v0"
    assert first_artifact["action_kind"] == "execute-build-known-blocks"
    assert first_artifact["materialization_status"] == "materialized"


def test_pet_builder_execute_reports_blocked_without_materializing(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    payload = {
        "schema": "pet-builder-plan-v0",
        "input_n": 1234567890123,
        "can_execute_now": False,
        "action": {"kind": "realize-missing-blocks"},
        "build_artifacts": [
            {
                "artifact_id": "artifact::unknown-exp1-slots",
                "source_block_id": "unknown-exp1-slots",
                "status": "deferred-until-realization",
            }
        ],
    }

    report = _run_json_file_command(TOOL, payload, output_dir)

    assert report["schema"] == "pet-builder-execution-v0"
    assert report["source_schema"] == "pet-builder-plan-v0"
    assert report["input_n"] == 1234567890123
    assert report["action_kind"] == "realize-missing-blocks"
    assert report["can_execute_now"] is False
    assert report["execution_status"] == "blocked"
    assert report["materialized_artifact_count"] == 0
    assert report["produced_artifact_ids"] == []
    assert report["deferred_artifact_ids"] == ["artifact::unknown-exp1-slots"]
    assert report["produced_files"] == []

    assert output_dir.exists()
    assert list(output_dir.iterdir()) == []
