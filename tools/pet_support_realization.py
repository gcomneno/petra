#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def require_field(obj: dict[str, Any], key: str) -> Any:
    if key not in obj:
        raise SystemExit(f"missing required field: {key}")
    return obj[key]


def _build_from_partial_build_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(payload, "schema")
    build_status = require_field(payload, "build_status")

    if schema != "pet-build-from-int-v2":
        raise SystemExit(
            f"unsupported input schema: {schema} (expected pet-build-from-int-v2)"
        )

    if build_status != "partial":
        raise SystemExit(
            f"support realization stub expects partial build payload, got build_status={build_status!r}"
        )

    input_n = require_field(payload, "input_n")
    target_generator = require_field(payload, "target_generator")
    mode = require_field(payload, "mode")
    phase1 = require_field(payload, "phase1")
    phase2 = require_field(payload, "phase2")

    phase1_status = require_field(phase1, "status")
    phase1_target_n = require_field(phase1, "target_n")
    phase1_steps = require_field(phase1, "steps")
    phase2_status = require_field(phase2, "status")
    same_pet_shape = require_field(phase2, "same_pet_shape")

    return {
        "schema": "pet-support-realization-v0",
        "source_schema": schema,
        "input_n": input_n,
        "target_generator": target_generator,
        "mode": mode,
        "phase1": {
            "status": phase1_status,
            "target_n": phase1_target_n,
            "steps": phase1_steps,
        },
        "phase2": {
            "status": phase2_status,
            "same_pet_shape": same_pet_shape,
        },
        "known_block_count": 0,
        "unknown_block_count": 0,
        "known_blocks": [],
        "unknown_blocks": [],
        "realization_status": "pending",
        "message": (
            "support realization is not implemented yet; "
            "this stub only validates and re-exposes the partial build payload"
        ),
        "next_action": (
            "future versions should consume generator + realization constraints "
            "to attempt non-canonical support lift"
        ),
    }


# V0 realization constraints are aggregated by exponent class, not by individual slot.
#
# This means that blocks such as:
#   - slot_exp = 2, slot_multiplicity = 1
#   - slot_exp = 1, slot_multiplicity = 4
# are interpreted as exponent-class aggregates.
#
# The goal of V0 is to keep the realization contract simple and avoid introducing
# artificial ordering between shape-equivalent slots.
#
# This is appropriate for flat / root-level cases, where same-exponent slots can be
# treated as one block without loss of intended meaning.
#
# Future versions may refine this into position-aware blocks (for example via slot_path
# or subtree_path) when recursive PET shapes require distinguishing same-exponent slots
# that occur in different structural contexts.
def _build_from_constraint_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(payload, "schema")
    if schema != "pet-support-realization-input-v0":
        raise SystemExit(
            f"unsupported input schema: {schema} (expected pet-support-realization-input-v0)"
        )

    input_n = require_field(payload, "input_n")
    target_generator = require_field(payload, "target_generator")
    shape_signature = require_field(payload, "shape_signature")
    slot_count = require_field(payload, "slot_count")
    exponent_multiset = require_field(payload, "exponent_multiset")
    realization_goal = require_field(payload, "realization_goal")
    known_blocks = require_field(payload, "known_blocks")
    unknown_blocks = require_field(payload, "unknown_blocks")

    if not isinstance(known_blocks, list):
        raise SystemExit("known_blocks must be a list")
    if not isinstance(unknown_blocks, list):
        raise SystemExit("unknown_blocks must be a list")

    for i, block in enumerate(known_blocks):
        if not isinstance(block, dict):
            raise SystemExit(f"known_blocks[{i}] must be an object")
        require_field(block, "block_id")
        require_field(block, "slot_exp")
        require_field(block, "slot_multiplicity")
        require_field(block, "target_product")

    for i, block in enumerate(unknown_blocks):
        if not isinstance(block, dict):
            raise SystemExit(f"unknown_blocks[{i}] must be an object")
        require_field(block, "block_id")
        require_field(block, "slot_exp")
        require_field(block, "slot_multiplicity")
        require_field(block, "target_product")

    return {
        "schema": "pet-support-realization-v0",
        "source_schema": schema,
        "input_n": input_n,
        "target_generator": target_generator,
        "mode": "constraint-driven-support-realization",
        "shape_signature": shape_signature,
        "slot_count": slot_count,
        "exponent_multiset": exponent_multiset,
        "realization_goal": realization_goal,
        "phase1": {
            "status": "external-input",
            "target_n": target_generator,
            "steps": None,
        },
        "phase2": {
            "status": "constraint-input",
            "same_pet_shape": True,
        },
        "known_block_count": len(known_blocks),
        "unknown_block_count": len(unknown_blocks),
        "known_blocks": known_blocks,
        "unknown_blocks": unknown_blocks,
        "realization_status": "pending",
        "message": (
            "support realization is not implemented yet; "
            "this stub validates and restates realization constraints"
        ),
        "next_action": (
            "future versions should attempt support lift from the provided blocks "
            "and cheap arithmetic constraints"
        ),
    }


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    schema = require_field(payload, "schema")

    if schema == "pet-build-from-int-v2":
        return _build_from_partial_build_payload(payload)
    if schema == "pet-support-realization-input-v0":
        return _build_from_constraint_payload(payload)

    raise SystemExit(
        f"unsupported input schema: {schema} "
        f"(expected pet-build-from-int-v2 or pet-support-realization-input-v0)"
    )


def _print_block(block: dict[str, Any]) -> None:
    print(f"- block_id = {block['block_id']}")
    print(f"  slot_exp = {block['slot_exp']}")
    print(f"  slot_multiplicity = {block['slot_multiplicity']}")
    print(f"  target_product = {block['target_product']}")
    constraints = block.get("constraints")
    if constraints is not None:
        print(f"  constraints = {json.dumps(constraints, ensure_ascii=False, sort_keys=True)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and restate support-realization inputs and partial build payloads."
    )
    parser.add_argument("input_json", help="input JSON payload")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    report = build_report(payload)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"input_n = {report['input_n']}")
        print(f"target_generator = {report['target_generator']}")
        print(f"mode = {report['mode']}")
        if "shape_signature" in report:
            print(f"shape_signature = {json.dumps(report['shape_signature'], ensure_ascii=False)}")
        if "slot_count" in report:
            print(f"slot_count = {report['slot_count']}")
        if "exponent_multiset" in report:
            print(f"exponent_multiset = {report['exponent_multiset']}")
        if "realization_goal" in report:
            print(f"realization_goal = {report['realization_goal']}")
        print()
        print("[phase 1]")
        print(f"status = {report['phase1']['status']}")
        print(f"target_n = {report['phase1']['target_n']}")
        print(f"steps = {report['phase1']['steps']}")
        print()
        print("[phase 2]")
        print(f"status = {report['phase2']['status']}")
        print(f"same_pet_shape = {str(report['phase2']['same_pet_shape']).lower()}")
        print()
        print(f"known_block_count = {report['known_block_count']}")
        if report["known_blocks"]:
            print("[known blocks]")
            for block in report["known_blocks"]:
                _print_block(block)
        print(f"unknown_block_count = {report['unknown_block_count']}")
        if report["unknown_blocks"]:
            print("[unknown blocks]")
            for block in report["unknown_blocks"]:
                _print_block(block)
        print()
        print(f"realization_status = {report['realization_status']}")
        print(f"message = {report['message']}")
        print(f"next_action = {report['next_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
