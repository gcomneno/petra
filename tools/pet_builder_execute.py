#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _load_payload(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"input file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}")


def _require_field(payload: dict[str, Any], name: str) -> Any:
    if name not in payload:
        raise SystemExit(f"missing required field: {name}")
    return payload[name]


def _artifact_filename(artifact_id: str) -> str:
    return artifact_id.replace(":", "_") + ".json"


def _materialize_artifact(
    artifact: dict[str, Any],
    plan: dict[str, Any],
    output_dir: Path,
) -> str:
    artifact_id = str(_require_field(artifact, "artifact_id"))
    source_block_id = str(_require_field(artifact, "source_block_id"))

    payload = {
        "schema": "pet-builder-artifact-v0",
        "artifact_id": artifact_id,
        "source_block_id": source_block_id,
        "input_n": plan.get("input_n"),
        "source_plan_schema": plan.get("schema"),
        "action_kind": plan.get("action", {}).get("kind"),
        "materialization_status": "materialized",
    }

    out_path = output_dir / _artifact_filename(artifact_id)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return str(out_path)


def _execute_plan(plan: dict[str, Any], output_dir_str: str) -> dict[str, Any]:
    can_execute_now = bool(_require_field(plan, "can_execute_now"))
    build_artifacts = list(_require_field(plan, "build_artifacts"))
    action = _require_field(plan, "action")

    output_dir = Path(output_dir_str)
    output_dir.mkdir(parents=True, exist_ok=True)

    produced_artifact_ids: list[str] = []
    produced_files: list[str] = []
    deferred_artifact_ids = [
        str(artifact["artifact_id"])
        for artifact in build_artifacts
        if artifact.get("status") != "planned"
    ]

    script_steps = list(plan.get("script_steps", []))
    if not script_steps:
        planned_block_ids = [
            str(artifact.get("source_block_id"))
            for artifact in build_artifacts
            if artifact.get("status") == "planned"
        ]
        missing_block_ids = [
            str(artifact.get("source_block_id"))
            for artifact in build_artifacts
            if artifact.get("status") != "planned"
        ]
        if can_execute_now:
            step = 1
            for block_id in planned_block_ids:
                script_steps.append(
                    {
                        "step": step,
                        "command": "prepare-block",
                        "block_id": block_id,
                    }
                )
                step += 1
                script_steps.append(
                    {
                        "step": step,
                        "command": "build-block",
                        "block_id": block_id,
                    }
                )
                step += 1
            script_steps.append(
                {
                    "step": step,
                    "command": "finalize-build",
                    "block_ids": planned_block_ids,
                }
            )
        else:
            script_steps = [
                {
                    "step": 1,
                    "command": "inspect-missing-blocks",
                    "block_ids": missing_block_ids,
                },
                {
                    "step": 2,
                    "command": "realize-blocks",
                    "block_ids": missing_block_ids,
                },
                {
                    "step": 3,
                    "command": "retry-builder-plan",
                    "block_ids": missing_block_ids,
                },
            ]

    if can_execute_now:
        for artifact in build_artifacts:
            if artifact.get("status") != "planned":
                continue
            produced_artifact_ids.append(str(_require_field(artifact, "artifact_id")))
            produced_files.append(_materialize_artifact(artifact, plan, output_dir))
        execution_status = "executed"
        built_block_ids = [
            str(artifact.get("source_block_id"))
            for artifact in build_artifacts
            if artifact.get("status") == "planned"
        ]
        built_components = [
            {
                "block_id": str(artifact.get("source_block_id")),
                "artifact_id": str(artifact.get("artifact_id")),
                "component_status": "built",
            }
            for artifact in build_artifacts
            if artifact.get("status") == "planned"
        ]
        final_build_output = {
            "schema": "pet-builder-output-v0",
            "input_n": plan.get("input_n"),
            "built_block_ids": built_block_ids,
            "artifact_ids": produced_artifact_ids,
            "build_status": "built",
            "assembled_from_artifacts": True,
            "built_pet_object": {
                "schema": "pet-built-object-v0",
                "input_n": plan.get("input_n"),
                "built_block_ids": built_block_ids,
                "artifact_ids": produced_artifact_ids,
                "assembly_status": "assembled",
                "assembled_from_artifacts": True,
                "component_count": len(built_components),
                "artifact_count": len(produced_artifact_ids),
                "components": built_components,
                "assembly_trace": [step.get("command") for step in script_steps],
                "finalization": {
                    "status": "finalized",
                    "finalized_by": "finalize-build",
                },
            },
        }
    else:
        execution_status = "blocked"
        final_build_output = {
            "schema": "pet-builder-output-v0",
            "input_n": plan.get("input_n"),
            "built_block_ids": [],
            "artifact_ids": [],
            "build_status": "deferred",
            "assembled_from_artifacts": False,
            "built_pet_object": {
                "schema": "pet-built-object-v0",
                "input_n": plan.get("input_n"),
                "built_block_ids": [],
                "artifact_ids": [],
                "assembly_status": "deferred",
                "assembled_from_artifacts": False,
                "component_count": 0,
                "artifact_count": 0,
                "components": [],
                "assembly_trace": [step.get("command") for step in script_steps],
                "finalization": {
                    "status": "deferred",
                    "finalized_by": None,
                },
            },
        }

    return {
        "schema": "pet-builder-execution-v0",
        "source_schema": plan.get("schema"),
        "input_n": plan.get("input_n"),
        "action_kind": action.get("kind"),
        "can_execute_now": can_execute_now,
        "execution_status": execution_status,
        "output_dir": str(output_dir),
        "materialized_artifact_count": len(produced_artifact_ids),
        "produced_artifact_ids": produced_artifact_ids,
        "deferred_artifact_ids": deferred_artifact_ids,
        "produced_files": produced_files,
        "final_build_output": final_build_output,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Materialize builder artifacts from a PET builder plan.",
    )
    parser.add_argument("plan_json", help="input PET builder plan JSON")
    parser.add_argument(
        "--output-dir",
        default="/tmp/pet_builder_out",
        help="directory where materialized artifacts will be written",
    )
    args = parser.parse_args(argv[1:])

    plan = _load_payload(args.plan_json)
    report = _execute_plan(plan, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
