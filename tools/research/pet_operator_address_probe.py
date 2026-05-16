#!/usr/bin/env python3
"""Research-only PET/PEG recursive operator address resolver probe.

This probe resolves PET/PEG 2.0-style recursive addresses against the existing
PET core representation produced by pet.encode(N).

It does not implement address-aware operators in the stable core.
It does not change CLI behavior, routing, residual descent, anchor selection,
verification, or factorization behavior.
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


SCHEMA = "pet.operator_address_probe.v0"
CLAIM = (
    "research-only PET/PEG 2.0 address resolver probe; "
    "no stable core/operator behavior change"
)


def parse_address(raw: str) -> list[int]:
    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError("address must be a JSON list")

    address: list[int] = []
    for item in data:
        if not isinstance(item, int):
            raise ValueError("address entries must be integers")
        if item < 2:
            raise ValueError("address entries must be primal roots >= 2")
        address.append(item)

    return address


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


def resolve_address(tree: PET, address: list[int]) -> dict[str, Any]:
    if not address:
        return {
            "valid": True,
            "address": [],
            "depth": 0,
            "selected_root": None,
            "selected_exponent_object": None,
            "selected_exponent_kind": None,
            "baseline_index_path": [],
            "terminal_baseline": baseline(tree),
            "reason": None,
            "trace": [],
        }

    current = tree
    baseline_index_path: list[int] = []
    trace: list[dict[str, Any]] = []
    selected_root: int | None = None
    selected_exp: PETExp = None

    for depth, root in enumerate(address, start=1):
        hit = find_node(current, root)

        if hit is None:
            return {
                "valid": False,
                "address": address,
                "depth": depth - 1,
                "selected_root": selected_root,
                "selected_exponent_object": exp_to_jsonable(selected_exp),
                "selected_exponent_kind": (
                    None
                    if selected_root is None
                    else "leaf"
                    if selected_exp is None
                    else "pet"
                ),
                "baseline_index_path": baseline_index_path,
                "terminal_baseline": baseline(current),
                "reason": "root-not-in-current-baseline",
                "missing_root": root,
                "trace": trace,
            }

        index, exp_repr = hit
        selected_root = root
        selected_exp = exp_repr
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
                "selected_root": selected_root,
                "selected_exponent_object": exp_to_jsonable(selected_exp),
                "selected_exponent_kind": "leaf" if selected_exp is None else "pet",
                "baseline_index_path": baseline_index_path,
                "terminal_baseline": baseline(current),
                "reason": None,
                "trace": trace,
            }

        if exp_repr is None:
            return {
                "valid": False,
                "address": address,
                "depth": depth,
                "selected_root": selected_root,
                "selected_exponent_object": None,
                "selected_exponent_kind": "leaf",
                "baseline_index_path": baseline_index_path,
                "terminal_baseline": baseline(current),
                "reason": "selected-root-has-leaf-exponent",
                "blocked_root": root,
                "trace": trace,
            }

        current = exp_repr

    raise AssertionError("unreachable address resolution state")


def build_payload(n: int, address: list[int]) -> dict[str, Any]:
    tree = encode(n)
    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "pet": to_jsonable(tree),
        "resolution": resolve_address(tree, address),
    }


def print_text(payload: dict[str, Any]) -> None:
    resolution = payload["resolution"]

    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"address = {resolution['address']}")
    print(f"valid = {str(resolution['valid']).lower()}")
    print(f"depth = {resolution['depth']}")
    print(f"selected_root = {resolution['selected_root']}")
    print(f"selected_exponent_kind = {resolution['selected_exponent_kind']}")
    print(f"baseline_index_path = {resolution['baseline_index_path']}")
    print(f"terminal_baseline = {resolution['terminal_baseline']}")
    print(f"reason = {resolution['reason']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Research-only PET/PEG recursive operator address resolver probe."
    )
    parser.add_argument("n", type=int, metavar="N", help="integer N >= 2")
    parser.add_argument(
        "--address",
        default="[]",
        help='recursive address as JSON list, for example "[]" or "[7,2]"',
    )
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    if args.n < 2:
        raise ValueError("N must be >= 2")

    address = parse_address(args.address)
    payload = build_payload(args.n, address)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
