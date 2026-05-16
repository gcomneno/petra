#!/usr/bin/env python3
"""Research-only PET/PEG address-aware Y-axis hypothetical mutation probe.

This probe explores candidate value-level exponent mutation semantics:

    INC(address): exponent k -> k + 1
    DEC(address): exponent k -> k - 1, only when k > 1

It mutates only an in-memory copy of the PET object produced by pet.encode(N).

It does not change stable PET core behavior, CLI behavior, routing,
residual descent, anchor selection, verification, or factorization behavior.
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
from tools.research.pet_operator_y_address_probe import resolve_y_target  # noqa: E402


SCHEMA = "pet.operator_y_mutation_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 Y-axis hypothetical value-level exponent "
    "mutation probe; no stable core/operator behavior change"
)


def find_node(tree: PET, root: int) -> tuple[int, PETExp] | None:
    for index, (prime, exp_repr) in enumerate(tree):
        if prime == root:
            return index, exp_repr
    return None


def exponent_value(exp_repr: PETExp) -> int:
    return 1 if exp_repr is None else decode(exp_repr)


def mutate_y_target(tree: PET, address: list[int], op: str) -> dict[str, Any]:
    mutated = copy.deepcopy(tree)
    current = mutated

    for depth, root in enumerate(address, start=1):
        hit = find_node(current, root)
        if hit is None:
            raise AssertionError("address should have been validated before mutation")

        index, exp_repr = hit
        is_last = depth == len(address)

        if not is_last:
            if exp_repr is None:
                raise AssertionError("address should not descend through a leaf")
            current = exp_repr
            continue

        old_exp = exponent_value(exp_repr)

        if op == "INC":
            new_exp = old_exp + 1
        elif op == "DEC":
            if old_exp <= 1:
                raise AssertionError("DEC should have been rejected for leaf exponent")
            new_exp = old_exp - 1
        else:
            raise ValueError("op must be INC or DEC")

        new_exp_repr: PETExp = None if new_exp == 1 else encode(new_exp)
        prime, _old_exp_repr = current[index]
        current[index] = (prime, new_exp_repr)

        validate(mutated)

        return {
            "mutated_pet": to_jsonable(mutated),
            "old_exponent_value": old_exp,
            "new_exponent_value": new_exp,
            "mutated_value": decode(mutated),
        }

    raise AssertionError("unreachable mutation state")


def classify_mutation(tree: PET, address: list[int], op: str) -> dict[str, Any]:
    target = resolve_y_target(tree, address)
    op = op.upper()

    if op not in {"INC", "DEC"}:
        raise ValueError("op must be INC or DEC")

    if not target["valid"]:
        return {
            "op": op,
            "valid": False,
            "reason": "invalid-address",
            "target_reason": target["reason"],
            "mutated_pet": None,
            "mutated_value": None,
            "old_exponent_value": None,
            "new_exponent_value": None,
        }

    if op == "DEC" and target["selected_exponent_kind"] == "leaf":
        return {
            "op": op,
            "valid": False,
            "reason": "selected-exponent-has-no-defined-predecessor",
            "selected_root": target["selected_root"],
            "selected_exponent_kind": target["selected_exponent_kind"],
            "mutated_pet": None,
            "mutated_value": None,
            "old_exponent_value": 1,
            "new_exponent_value": None,
        }

    mutation = mutate_y_target(tree, address, op)

    return {
        "op": op,
        "valid": True,
        "reason": None,
        "selected_root": target["selected_root"],
        "selected_exponent_kind": target["selected_exponent_kind"],
        **mutation,
    }


def build_payload(n: int, address: list[int], op: str) -> dict[str, Any]:
    tree = encode(n)
    target = resolve_y_target(tree, address)
    operation = classify_mutation(tree, address, op)

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "original_value": decode(tree),
        "original_pet": to_jsonable(tree),
        "target_resolution": target,
        "operation": operation,
    }


def print_text(payload: dict[str, Any]) -> None:
    target = payload["target_resolution"]
    operation = payload["operation"]

    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"original_value = {payload['original_value']}")
    print(f"op = {operation['op']}")
    print(f"address = {target['address']}")
    print(f"target_valid = {str(target['valid']).lower()}")
    print(f"target_reason = {target['reason']}")
    print(f"selected_root = {target['selected_root']}")
    print(f"selected_exponent_kind = {target['selected_exponent_kind']}")
    print(f"old_exponent_value = {operation['old_exponent_value']}")
    print(f"new_exponent_value = {operation['new_exponent_value']}")
    print(f"operation_valid = {str(operation['valid']).lower()}")
    print(f"operation_reason = {operation['reason']}")
    print(f"mutated_value = {operation['mutated_value']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Research-only PET/PEG address-aware Y-axis hypothetical mutation probe."
        )
    )
    parser.add_argument("n", type=int, metavar="N", help="integer N >= 2")
    parser.add_argument("op", choices=["INC", "DEC"], help="Y-axis operator")
    parser.add_argument(
        "--address",
        default="[]",
        help='recursive address as JSON list, for example "[2]" or "[7,2]"',
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    if args.n < 2:
        raise ValueError("N must be >= 2")

    address = parse_address(args.address)
    payload = build_payload(args.n, address, args.op)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
