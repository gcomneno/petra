#!/usr/bin/env python3
"""Research-only PET/PEG address stability probe.

This probe resolves a tracked recursive address before and after one
research-only operator invocation.

It observes whether the tracked address remains stable, is created, is
destroyed, becomes leaf-blocked, or survives while resolving to a changed
target.

This is research-only. It does not change stable PET core behavior, CLI
behavior, routing, residual descent, anchor selection, verification, or
factorization behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pet import encode, to_jsonable  # noqa: E402
from tools.research.pet_operator_address_probe import (  # noqa: E402
    parse_address,
    resolve_address,
)
from tools.research.pet_operator_xy_commutativity_probe import (  # noqa: E402
    apply_x_operation,
    apply_y_operation,
)


SCHEMA = "pet.operator_address_stability_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 address stability probe; "
    "no stable core/operator behavior change"
)


def resolution_target_signature(resolution: dict[str, Any]) -> dict[str, Any]:
    if not resolution["valid"]:
        return {
            "valid": False,
            "reason": resolution["reason"],
            "depth": resolution["depth"],
            "terminal_baseline": resolution["terminal_baseline"],
        }

    return {
        "valid": True,
        "selected_root": resolution["selected_root"],
        "selected_exponent_kind": resolution["selected_exponent_kind"],
        "selected_exponent_object": resolution["selected_exponent_object"],
        "baseline_index_path": resolution["baseline_index_path"],
    }


def classify_stability(
    before: dict[str, Any],
    after: dict[str, Any] | None,
    operator: dict[str, Any],
) -> str:
    if not operator["valid"]:
        return "operator-invalid"

    if after is None:
        raise AssertionError("after resolution must exist for valid operators")

    before_valid = before["valid"]
    after_valid = after["valid"]

    if not before_valid and not after_valid:
        return "still-invalid"

    if not before_valid and after_valid:
        return "created"

    if before_valid and not after_valid:
        if after["reason"] == "selected-root-has-leaf-exponent":
            return "leaf-blocked"
        return "destroyed"

    before_sig = resolution_target_signature(before)
    after_sig = resolution_target_signature(after)

    if before_sig == after_sig:
        return "stable"

    return "retargeted"


def apply_operator(
    tree: Any,
    op: str,
    root: int | None,
    parent_address: list[int],
    operator_address: list[int] | None,
) -> dict[str, Any]:
    op = op.upper()

    if op in {"NEW", "DROP"}:
        if root is None:
            raise ValueError("--root is required for NEW and DROP")
        return apply_x_operation(tree, parent_address, op, root)

    if op in {"INC", "DEC"}:
        if operator_address is None:
            raise ValueError("--operator-address is required for INC and DEC")
        return apply_y_operation(tree, operator_address, op)

    raise ValueError("op must be NEW, DROP, INC, or DEC")


def build_payload(
    n: int,
    tracked_address: list[int],
    op: str,
    root: int | None = None,
    parent_address: list[int] | None = None,
    operator_address: list[int] | None = None,
) -> dict[str, Any]:
    tree = encode(n)
    parent_address = [] if parent_address is None else parent_address

    before = resolve_address(tree, tracked_address)
    operation = apply_operator(tree, op, root, parent_address, operator_address)

    after = None
    if operation["valid"]:
        after_tree = encode(operation["mutated_value"])
        after = resolve_address(after_tree, tracked_address)

    relation = classify_stability(before, after, operation)

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "original_pet": to_jsonable(tree),
        "tracked_address": tracked_address,
        "operator": {
            "op": op.upper(),
            "root": root,
            "parent_address": parent_address,
            "operator_address": operator_address,
            "valid": operation["valid"],
            "reason": operation["reason"],
            "mutated_value": operation["mutated_value"],
        },
        "before": before,
        "after": after,
        "stability": relation,
    }


def print_text(payload: dict[str, Any]) -> None:
    after = payload["after"]
    operator = payload["operator"]

    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"tracked_address = {payload['tracked_address']}")
    print(f"op = {operator['op']}")
    print(f"operator_valid = {str(operator['valid']).lower()}")
    print(f"operator_reason = {operator['reason']}")
    print(f"mutated_value = {operator['mutated_value']}")
    print(f"before_valid = {str(payload['before']['valid']).lower()}")
    print(f"before_reason = {payload['before']['reason']}")
    print(f"after_valid = {None if after is None else str(after['valid']).lower()}")
    print(f"after_reason = {None if after is None else after['reason']}")
    print(f"stability = {payload['stability']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG address stability probe."
    )
    parser.add_argument("n", type=int, metavar="N", help="integer N >= 2")
    parser.add_argument("--tracked-address", required=True)
    parser.add_argument("--op", choices=["NEW", "DROP", "INC", "DEC"], required=True)
    parser.add_argument("--root", type=int, help="q for NEW, p for DROP")
    parser.add_argument(
        "--parent-address",
        default="[]",
        help='X parent support address as JSON list, for example "[]" or "[2]"',
    )
    parser.add_argument(
        "--operator-address",
        help='Y operator address as JSON list, for example "[2]" or "[2,2]"',
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    if args.n < 2:
        raise ValueError("N must be >= 2")

    payload = build_payload(
        args.n,
        tracked_address=parse_address(args.tracked_address),
        op=args.op,
        root=args.root,
        parent_address=parse_address(args.parent_address),
        operator_address=(
            None if args.operator_address is None else parse_address(args.operator_address)
        ),
    )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
