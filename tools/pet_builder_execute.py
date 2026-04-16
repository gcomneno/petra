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

    if can_execute_now:
        for artifact in build_artifacts:
            if artifact.get("status") != "planned":
                continue
            produced_artifact_ids.append(str(_require_field(artifact, "artifact_id")))
            produced_files.append(_materialize_artifact(artifact, plan, output_dir))
        execution_status = "executed"
        final_build_output = {
            "schema": "pet-builder-output-v0",
            "input_n": plan.get("input_n"),
            "built_block_ids": [str(artifact.get("source_block_id")) for artifact in build_artifacts if artifact.get("status") == "planned"],
            "artifact_ids": produced_artifact_ids,
            "build_status": "built",
            "assembled_from_artifacts": True,
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
