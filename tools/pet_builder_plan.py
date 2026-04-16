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
    else:
        action = {
            "kind": "realize-missing-blocks",
            "block_ids": missing_unknown_block_ids,
            "block_count": len(missing_unknown_block_ids),
        }

    return {
        "schema": "pet-builder-plan-v0",
        "source_schema": report.get("schema"),
        "input_n": report.get("input_n"),
        "builder_readiness": builder_readiness,
        "mode": mode,
        "next_action": next_action,
        "missing_block_count": missing_block_count,
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
