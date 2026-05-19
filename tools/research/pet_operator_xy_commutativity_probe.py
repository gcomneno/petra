#!/usr/bin/env python3
"""Research-only PET/PEG X/Y operator commutativity probe.

This probe compares two operation orderings from the same starting PET object:

    left path:  X then Y
    right path: Y then X

It explores whether address-aware X-axis support mutations and Y-axis
hypothetical exponent mutations commute, diverge, or become invalid
asymmetrically.

This is research-only. It does not change stable PET core behavior, CLI
behavior, routing, residual descent, anchor selection, verification, or
factorization behavior.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pet import decode, encode, to_jsonable, validate  # noqa: E402
from pet.core import PET, PETExp  # noqa: E402
from tools.research.pet_operator_address_probe import parse_address  # noqa: E402
from tools.research.pet_operator_x_address_probe import (  # noqa: E402
    classify_drop,
    classify_new,
    resolve_parent_support,
)
from tools.research.pet_operator_y_address_probe import resolve_y_target  # noqa: E402
from tools.research.pet_operator_y_mutation_probe import classify_mutation  # noqa: E402


SCHEMA = "pet.operator_xy_commutativity_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 X/Y operator commutativity probe; "
    "no stable core/operator behavior change"
)


def find_node(tree: PET, root: int) -> tuple[int, PETExp] | None:
    for index, (prime, exp_repr) in enumerate(tree):
        if prime == root:
            return index, exp_repr
    return None


def resolve_mutable_parent(tree: PET, parent_address: list[int]) -> PET:
    current = tree

    for root in parent_address:
        hit = find_node(current, root)
        if hit is None:
            raise AssertionError("parent address should have been validated")

        _index, exp_repr = hit
        if exp_repr is None:
            raise AssertionError("parent address should not select a leaf exponent")

        current = exp_repr

    return current


def mutate_x_support(
    tree: PET,
    parent_address: list[int],
    op: str,
    root: int,
) -> dict[str, Any]:
    mutated = copy.deepcopy(tree)
    target = resolve_mutable_parent(mutated, parent_address)

    if op == "NEW":
        target.append((root, None))
        target.sort(key=lambda item: item[0])
    elif op == "DROP":
        target[:] = [
            (prime, exp_repr)
            for prime, exp_repr in target
            if prime != root
        ]
    else:
        raise ValueError("X op must be NEW or DROP")

    validate(mutated)

    return {
        "mutated_pet": to_jsonable(mutated),
        "mutated_value": decode(mutated),
    }


def apply_x_operation(
    tree: PET,
    parent_address: list[int],
    op: str,
    root: int,
) -> dict[str, Any]:
    op = op.upper()
    parent_resolution = resolve_parent_support(tree, parent_address)

    if op == "NEW":
        operation = classify_new(parent_resolution, root)
    elif op == "DROP":
        operation = classify_drop(parent_resolution, root)
    else:
        raise ValueError("X op must be NEW or DROP")

    result: dict[str, Any] = {
        "axis": "X",
        "op": op,
        "parent_address": parent_address,
        "root": root,
        "parent_resolution": parent_resolution,
        "operation": operation,
        "valid": operation["valid"],
        "reason": operation["reason"],
        "mutated_pet": None,
        "mutated_value": None,
    }

    if not operation["valid"]:
        return result

    result.update(mutate_x_support(tree, parent_address, op, root))
    return result


def apply_y_operation(tree: PET, address: list[int], op: str) -> dict[str, Any]:
    op = op.upper()
    target_resolution = resolve_y_target(tree, address)
    operation = classify_mutation(tree, address, op)

    return {
        "axis": "Y",
        "op": op,
        "address": address,
        "target_resolution": target_resolution,
        "operation": operation,
        "valid": operation["valid"],
        "reason": operation["reason"],
        "mutated_pet": operation["mutated_pet"],
        "mutated_value": operation["mutated_value"],
    }


def apply_operation(
    tree: PET,
    x_parent_address: list[int],
    x_op: str,
    x_root: int,
    y_address: list[int],
    y_op: str,
    axis: str,
) -> dict[str, Any]:
    if axis == "X":
        return apply_x_operation(tree, x_parent_address, x_op, x_root)
    if axis == "Y":
        return apply_y_operation(tree, y_address, y_op)
    raise ValueError("axis must be X or Y")


def evaluate_sequence(
    n: int,
    axes: list[str],
    x_parent_address: list[int],
    x_op: str,
    x_root: int,
    y_address: list[int],
    y_op: str,
) -> dict[str, Any]:
    current = encode(n)
    steps: list[dict[str, Any]] = []

    for index, axis in enumerate(axes, start=1):
        step = apply_operation(
            current,
            x_parent_address,
            x_op,
            x_root,
            y_address,
            y_op,
            axis,
        )
        step["step_index"] = index
        steps.append(step)

        if not step["valid"]:
            return {
                "valid": False,
                "invalid_step_index": index,
                "invalid_axis": axis,
                "invalid_reason": step["reason"],
                "final_value": None,
                "final_pet": None,
                "steps": steps,
            }

        current = encode(step["mutated_value"])

    return {
        "valid": True,
        "invalid_step_index": None,
        "invalid_axis": None,
        "invalid_reason": None,
        "final_value": decode(current),
        "final_pet": to_jsonable(current),
        "steps": steps,
    }


def classify_relation(
    left: dict[str, Any],
    right: dict[str, Any],
    x_op: str,
    x_root: int,
    y_address: list[int],
) -> str:
    if not left["valid"] and not right["valid"]:
        return "both-invalid"

    if not left["valid"]:
        if x_op == "DROP" and y_address and y_address[0] == x_root:
            return "support-removed-y-target"
        return "left-invalid"

    if not right["valid"]:
        if x_op == "NEW" and y_address and y_address[0] == x_root:
            return "support-created-y-target"
        return "right-invalid"

    if left["final_value"] == right["final_value"]:
        return "commutes"

    return "non-commutes"


def build_payload(
    n: int,
    x_parent_address: list[int],
    x_op: str,
    x_root: int,
    y_address: list[int],
    y_op: str,
) -> dict[str, Any]:
    x_op = x_op.upper()
    y_op = y_op.upper()

    left = evaluate_sequence(
        n,
        ["X", "Y"],
        x_parent_address,
        x_op,
        x_root,
        y_address,
        y_op,
    )
    right = evaluate_sequence(
        n,
        ["Y", "X"],
        x_parent_address,
        x_op,
        x_root,
        y_address,
        y_op,
    )
    relation = classify_relation(left, right, x_op, x_root, y_address)

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "original_pet": to_jsonable(encode(n)),
        "x_operation": {
            "op": x_op,
            "parent_address": x_parent_address,
            "root": x_root,
        },
        "y_operation": {
            "op": y_op,
            "address": y_address,
        },
        "left_order": "X_THEN_Y",
        "right_order": "Y_THEN_X",
        "left": left,
        "right": right,
        "relation": relation,
    }


def print_text(payload: dict[str, Any]) -> None:
    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"x_operation = {payload['x_operation']}")
    print(f"y_operation = {payload['y_operation']}")
    print(f"left_order = {payload['left_order']}")
    print(f"left_valid = {str(payload['left']['valid']).lower()}")
    print(f"left_invalid_reason = {payload['left']['invalid_reason']}")
    print(f"left_final_value = {payload['left']['final_value']}")
    print(f"right_order = {payload['right_order']}")
    print(f"right_valid = {str(payload['right']['valid']).lower()}")
    print(f"right_invalid_reason = {payload['right']['invalid_reason']}")
    print(f"right_final_value = {payload['right']['final_value']}")
    print(f"relation = {payload['relation']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG X/Y operator commutativity probe."
    )
    parser.add_argument("n", type=int, metavar="N", help="integer N >= 2")
    parser.add_argument("--x-op", choices=["NEW", "DROP"], required=True)
    parser.add_argument("--x-root", type=int, required=True)
    parser.add_argument(
        "--x-parent-address",
        default="[]",
        help='X parent support address as JSON list, for example "[]" or "[7]"',
    )
    parser.add_argument("--y-op", choices=["INC", "DEC"], required=True)
    parser.add_argument(
        "--y-address",
        required=True,
        help='Y address as JSON list, for example "[2]" or "[7,2]"',
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    if args.n < 2:
        raise ValueError("N must be >= 2")

    payload = build_payload(
        args.n,
        parse_address(args.x_parent_address),
        args.x_op,
        args.x_root,
        parse_address(args.y_address),
        args.y_op,
    )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
