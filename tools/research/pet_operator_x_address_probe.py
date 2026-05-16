#!/usr/bin/env python3
"""Research-only PET/PEG address-aware X-axis operator probe.

This probe validates the proposed PET/PEG 2.0 uniform parent-support form:

    NEW(parent_address, q)
    DROP(parent_address, p)

The parent address resolves to the PET object whose baseline/support would be
mutated. This script only classifies hypothetical operation validity.

It does not mutate stable PET core behavior, CLI behavior, routing,
residual descent, anchor selection, verification, or factorization behavior.
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

from pet import encode, is_prime, to_jsonable  # noqa: E402
from pet.core import PET  # noqa: E402
from tools.research.pet_operator_address_probe import parse_address  # noqa: E402


SCHEMA = "pet.operator_x_address_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 X-axis parent-support address probe; "
    "no stable core/operator behavior change"
)


def baseline(tree: PET) -> list[int]:
    return [prime for prime, _exp_repr in tree]


def find_node(tree: PET, root: int) -> tuple[int, PET | None] | None:
    for index, (prime, exp_repr) in enumerate(tree):
        if prime == root:
            return index, exp_repr
    return None


def resolve_parent_support(tree: PET, parent_address: list[int]) -> dict[str, Any]:
    if not parent_address:
        return {
            "valid": True,
            "parent_address": [],
            "depth": 0,
            "target_baseline": baseline(tree),
            "target_pet": to_jsonable(tree),
            "baseline_index_path": [],
            "reason": None,
            "trace": [],
        }

    current = tree
    baseline_index_path: list[int] = []
    trace: list[dict[str, Any]] = []

    for depth, root in enumerate(parent_address, start=1):
        hit = find_node(current, root)

        if hit is None:
            return {
                "valid": False,
                "parent_address": parent_address,
                "depth": depth - 1,
                "target_baseline": baseline(current),
                "target_pet": to_jsonable(current),
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

        if exp_repr is None:
            return {
                "valid": False,
                "parent_address": parent_address,
                "depth": depth,
                "target_baseline": baseline(current),
                "target_pet": to_jsonable(current),
                "baseline_index_path": baseline_index_path,
                "reason": "parent-address-selects-leaf-exponent",
                "blocked_root": root,
                "trace": trace,
            }

        current = exp_repr

    return {
        "valid": True,
        "parent_address": parent_address,
        "depth": len(parent_address),
        "target_baseline": baseline(current),
        "target_pet": to_jsonable(current),
        "baseline_index_path": baseline_index_path,
        "reason": None,
        "trace": trace,
    }


def classify_new(parent_resolution: dict[str, Any], q: int) -> dict[str, Any]:
    if not is_prime(q):
        return {
            "op": "NEW",
            "valid": False,
            "q": q,
            "reason": "q-is-not-prime",
        }

    if not parent_resolution["valid"]:
        return {
            "op": "NEW",
            "valid": False,
            "q": q,
            "reason": "invalid-parent-address",
            "parent_reason": parent_resolution["reason"],
        }

    target_baseline = parent_resolution["target_baseline"]
    if q in target_baseline:
        return {
            "op": "NEW",
            "valid": False,
            "q": q,
            "reason": "q-already-in-target-baseline",
            "target_baseline": target_baseline,
        }

    return {
        "op": "NEW",
        "valid": True,
        "q": q,
        "reason": None,
        "target_baseline": target_baseline,
    }


def classify_drop(parent_resolution: dict[str, Any], p: int) -> dict[str, Any]:
    if not is_prime(p):
        return {
            "op": "DROP",
            "valid": False,
            "p": p,
            "reason": "p-is-not-prime",
        }

    if not parent_resolution["valid"]:
        return {
            "op": "DROP",
            "valid": False,
            "p": p,
            "reason": "invalid-parent-address",
            "parent_reason": parent_resolution["reason"],
        }

    target_baseline = parent_resolution["target_baseline"]
    if p not in target_baseline:
        return {
            "op": "DROP",
            "valid": False,
            "p": p,
            "reason": "p-not-in-target-baseline",
            "target_baseline": target_baseline,
        }

    if len(target_baseline) == 1:
        return {
            "op": "DROP",
            "valid": False,
            "p": p,
            "reason": "drop-would-create-empty-pet",
            "target_baseline": target_baseline,
        }

    return {
        "op": "DROP",
        "valid": True,
        "p": p,
        "reason": None,
        "target_baseline": target_baseline,
    }


def build_payload(
    n: int,
    parent_address: list[int],
    op: str,
    root: int,
) -> dict[str, Any]:
    tree = encode(n)
    parent_resolution = resolve_parent_support(tree, parent_address)
    op = op.upper()

    if op == "NEW":
        operation = classify_new(parent_resolution, root)
    elif op == "DROP":
        operation = classify_drop(parent_resolution, root)
    else:
        raise ValueError("op must be NEW or DROP")

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "pet": to_jsonable(tree),
        "parent_resolution": parent_resolution,
        "operation": operation,
    }


def print_text(payload: dict[str, Any]) -> None:
    parent = payload["parent_resolution"]
    operation = payload["operation"]

    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"op = {operation['op']}")
    print(f"parent_address = {parent['parent_address']}")
    print(f"parent_valid = {str(parent['valid']).lower()}")
    print(f"parent_reason = {parent['reason']}")
    print(f"target_baseline = {parent['target_baseline']}")
    print(f"operation_valid = {str(operation['valid']).lower()}")
    print(f"operation_reason = {operation['reason']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG address-aware X-axis operator probe."
    )
    parser.add_argument("n", type=int, metavar="N", help="integer N >= 2")
    parser.add_argument("op", choices=["NEW", "DROP"], help="X-axis operator")
    parser.add_argument("root", type=int, help="q for NEW, p for DROP")
    parser.add_argument(
        "--parent-address",
        default="[]",
        help='parent support address as JSON list, for example "[]" or "[7]"',
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    if args.n < 2:
        raise ValueError("N must be >= 2")

    parent_address = parse_address(args.parent_address)
    payload = build_payload(args.n, parent_address, args.op, args.root)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
