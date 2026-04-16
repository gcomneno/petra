#!/usr/bin/env python3
from __future__ import annotations

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


def _build_plan(report: dict[str, Any]) -> dict[str, Any]:
    builder_readiness = _require_field(report, "builder_readiness")
    builder_plan = _require_field(report, "builder_plan")

    ready_known_block_ids = list(builder_plan.get("ready_known_block_ids", []))
    missing_unknown_block_ids = list(builder_plan.get("missing_unknown_block_ids", []))
    next_action = _require_field(builder_plan, "next_action")
    mode = _require_field(builder_plan, "mode")
    missing_block_count = int(_require_field(builder_plan, "missing_block_count"))

    if builder_readiness == "ready":
        action = {
            "kind": "execute-build-known-blocks",
            "block_ids": ready_known_block_ids,
            "block_count": len(ready_known_block_ids),
        }
        can_execute_now = True
        execution_status = "simulatable-now"
        simulated_steps = [
            {
                "step": 1,
                "kind": "load-ready-known-blocks",
                "block_ids": ready_known_block_ids,
            },
            {
                "step": 2,
                "kind": "execute-build-known-blocks",
                "block_ids": ready_known_block_ids,
            },
        ]
        script_steps = []
        step = 1
        for block_id in ready_known_block_ids:
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
                "block_ids": ready_known_block_ids,
            }
        )
        build_artifacts = [
            {
                "artifact_id": f"artifact::{block_id}",
                "source_block_id": block_id,
                "status": "planned",
            }
            for block_id in ready_known_block_ids
        ]
    else:
        action = {
            "kind": "realize-missing-blocks",
            "block_ids": missing_unknown_block_ids,
            "block_count": len(missing_unknown_block_ids),
        }
        can_execute_now = False
        execution_status = "blocked-on-missing-realization"
        simulated_steps = [
            {
                "step": 1,
                "kind": "inspect-missing-unknown-blocks",
                "block_ids": missing_unknown_block_ids,
            },
            {
                "step": 2,
                "kind": "defer-build-until-realization",
                "block_ids": missing_unknown_block_ids,
            },
        ]
        script_steps = [
            {
                "step": 1,
                "command": "inspect-missing-blocks",
                "block_ids": missing_unknown_block_ids,
            },
            {
                "step": 2,
                "command": "realize-blocks",
                "block_ids": missing_unknown_block_ids,
            },
            {
                "step": 3,
                "command": "retry-builder-plan",
                "block_ids": missing_unknown_block_ids,
            },
        ]
        build_artifacts = [
            {
                "artifact_id": f"artifact::{block_id}",
                "source_block_id": block_id,
                "status": "deferred-until-realization",
            }
            for block_id in missing_unknown_block_ids
        ]

    planned_block_ids = [
        artifact["source_block_id"]
        for artifact in build_artifacts
        if artifact["status"] == "planned"
    ]
    deferred_block_ids = [
        artifact["source_block_id"]
        for artifact in build_artifacts
        if artifact["status"] == "deferred-until-realization"
    ]
    build_manifest = {
        "artifact_count": len(build_artifacts),
        "planned_block_ids": planned_block_ids,
        "deferred_block_ids": deferred_block_ids,
        "manifest_status": "planned" if can_execute_now else "deferred",
    }

    return {
        "schema": "pet-builder-plan-v0",
        "source_schema": report.get("schema"),
        "input_n": report.get("input_n"),
        "builder_readiness": builder_readiness,
        "mode": mode,
        "next_action": next_action,
        "missing_block_count": missing_block_count,
        "can_execute_now": can_execute_now,
        "execution_status": execution_status,
        "simulated_steps": simulated_steps,
        "script_steps": script_steps,
        "build_artifacts": build_artifacts,
        "build_manifest": build_manifest,
        "action": action,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: pet_builder_plan.py REPORT.json", file=sys.stderr)
        return 2

    report = _load_payload(argv[1])
    plan = _build_plan(report)
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
