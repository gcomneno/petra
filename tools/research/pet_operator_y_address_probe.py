#!/usr/bin/env python3
"""Research-only PET/PEG address-aware Y-axis operator target probe.

This probe validates the PET/PEG 2.0 address-aware Y-axis target form:

    INC(address)
    DEC(address)

The address resolves to a selected primal root. The Y-axis target is the
exponent-object associated with that selected root.

This script only classifies target validity. It does not mutate PET objects,
stable PET core behavior, CLI behavior, routing, residual descent,
anchor selection, verification, or factorization behavior.
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
from pet.core import PET, PETExp  # noqa: E402
from tools.research.pet_operator_address_probe import parse_address  # noqa: E402


SCHEMA = "pet.operator_y_address_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 Y-axis address target probe; "
    "no stable core/operator behavior change"
)


def baseline(tree: PET) -> list[int]:
    return [prime for prime, _exp_repr in tree]


def find_node(tree: PET, root: int) -> tuple[int, PETExp] | None:
    for index, (prime, exp_repr) in enumerate(tree):
        if prime == root:
            return index, exp_repr
    return None


def exp_to_jsonable(exp_repr: PETExp) -> list[dict[str, Any]] | None:
    if exp_repr is None:
        return None
    return to_jsonable(exp_repr)


def resolve_y_target(tree: PET, address: list[int]) -> dict[str, Any]:
    if not address:
        return {
            "valid": False,
            "address": [],
            "depth": 0,
            "selected_root": None,
            "selected_exponent_kind": None,
            "selected_exponent_object": None,
            "parent_baseline": baseline(tree),
            "baseline_index_path": [],
            "reason": "empty-address-does-not-select-root",
            "trace": [],
        }

    current = tree
    baseline_index_path: list[int] = []
    trace: list[dict[str, Any]] = []

    for depth, root in enumerate(address, start=1):
        hit = find_node(current, root)

        if hit is None:
            return {
                "valid": False,
                "address": address,
                "depth": depth - 1,
                "selected_root": None,
                "selected_exponent_kind": None,
                "selected_exponent_object": None,
                "parent_baseline": baseline(current),
                "baseline_index_path": baseline_index_path,
                "reason": "root-not-in-current-baseline",
                "missing_root": root,
                "trace": trace,
            }

        index, exp_repr = hit
        baseline_index_path.append(index)

        trace.append(
            {
                "depth": depth,
                "root": root,
                "baseline": baseline(current),
                "baseline_index": index,
                "exponent_kind": "leaf" if exp_repr is None else "pet",
            }
        )

        is_last = depth == len(address)
        if is_last:
            return {
                "valid": True,
                "address": address,
                "depth": depth,
                "selected_root": root,
                "selected_exponent_kind": "leaf" if exp_repr is None else "pet",
                "selected_exponent_object": exp_to_jsonable(exp_repr),
                "parent_baseline": baseline(current),
                "baseline_index_path": baseline_index_path,
                "reason": None,
                "trace": trace,
            }

        if exp_repr is None:
            return {
                "valid": False,
                "address": address,
                "depth": depth,
                "selected_root": root,
                "selected_exponent_kind": "leaf",
                "selected_exponent_object": None,
                "parent_baseline": baseline(current),
                "baseline_index_path": baseline_index_path,
                "reason": "selected-root-has-leaf-exponent",
                "blocked_root": root,
                "trace": trace,
            }

        current = exp_repr

    raise AssertionError("unreachable Y-target resolution state")


def classify_inc(target: dict[str, Any]) -> dict[str, Any]:
    if not target["valid"]:
        return {
            "op": "INC",
            "valid": False,
            "reason": "invalid-address",
            "target_reason": target["reason"],
        }

    return {
        "op": "INC",
        "valid": True,
        "reason": None,
        "selected_root": target["selected_root"],
        "selected_exponent_kind": target["selected_exponent_kind"],
    }


def classify_dec(target: dict[str, Any]) -> dict[str, Any]:
    if not target["valid"]:
        return {
            "op": "DEC",
            "valid": False,
            "reason": "invalid-address",
            "target_reason": target["reason"],
        }

    if target["selected_exponent_kind"] == "leaf":
        return {
            "op": "DEC",
            "valid": False,
            "reason": "selected-exponent-has-no-defined-predecessor",
            "selected_root": target["selected_root"],
            "selected_exponent_kind": target["selected_exponent_kind"],
        }

    return {
        "op": "DEC",
        "valid": True,
        "reason": None,
        "selected_root": target["selected_root"],
        "selected_exponent_kind": target["selected_exponent_kind"],
    }


def build_payload(n: int, address: list[int], op: str) -> dict[str, Any]:
    tree = encode(n)
    target = resolve_y_target(tree, address)
    op = op.upper()

    if op == "INC":
        operation = classify_inc(target)
    elif op == "DEC":
        operation = classify_dec(target)
    else:
        raise ValueError("op must be INC or DEC")

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "pet": to_jsonable(tree),
        "target_resolution": target,
        "operation": operation,
    }


def print_text(payload: dict[str, Any]) -> None:
    target = payload["target_resolution"]
    operation = payload["operation"]

    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"op = {operation['op']}")
    print(f"address = {target['address']}")
    print(f"target_valid = {str(target['valid']).lower()}")
    print(f"target_reason = {target['reason']}")
    print(f"selected_root = {target['selected_root']}")
    print(f"selected_exponent_kind = {target['selected_exponent_kind']}")
    print(f"parent_baseline = {target['parent_baseline']}")
    print(f"baseline_index_path = {target['baseline_index_path']}")
    print(f"operation_valid = {str(operation['valid']).lower()}")
    print(f"operation_reason = {operation['reason']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG address-aware Y-axis operator target probe."
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
