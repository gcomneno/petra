#!/usr/bin/env python3
"""Experimental PET/PEG operator semantics report.

This tool aggregates the PET/PEG 2.0 executable operator semantics probes into
one deterministic inspection report for a given integer N.

It is experimental documented tooling. It does not change stable PET core behavior,
CLI behavior, routing, residual descent, anchor selection, verification, or
factorization behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pet import encode, is_prime, to_jsonable  # noqa: E402
from pet.core import PET  # noqa: E402
from tools.research.pet_operator_address_probe import resolve_address  # noqa: E402
from tools.research.pet_operator_address_stability_probe import (  # noqa: E402
    build_payload as build_address_stability_payload,
)
from tools.research.pet_operator_axis_invariant_probe import (  # noqa: E402
    build_payload as build_axis_invariant_payload,
)
from tools.research.pet_operator_x_address_probe import (  # noqa: E402
    build_payload as build_x_payload,
)
from tools.research.pet_operator_xy_commutativity_probe import (  # noqa: E402
    build_payload as build_xy_payload,
)
from tools.research.pet_operator_y_address_probe import (  # noqa: E402
    build_payload as build_y_target_payload,
)
from tools.research.pet_operator_y_mutation_probe import (  # noqa: E402
    build_payload as build_y_mutation_payload,
)


SCHEMA = "pet.operator_semantics_report.v0"
CLAIM = (
    "experimental PET/PEG 2.0 operator semantics report; "
    "aggregates executable probes without changing stable behavior"
)

BOUNDARIES = [
    "experimental documented tooling",
    "no stable CLI behavior change",
    "no PET core factorization behavior change",
    "no residual routing change",
    "no anchor selection change",
    "no verification logic change",
    "no default operator semantics change",
    "no PEG algebra completeness claim",
]


def baseline(tree: PET) -> list[int]:
    return [prime for prime, _exp_repr in tree]


def first_recursive_address(tree: PET) -> list[int] | None:
    for prime, exp_repr in tree:
        if exp_repr is not None and exp_repr:
            child_prime = exp_repr[0][0]
            return [prime, child_prime]
    return None


def first_leaf_address(tree: PET) -> list[int] | None:
    for prime, exp_repr in tree:
        if exp_repr is None:
            return [prime]
    return None


def next_new_prime(existing_roots: list[int]) -> int:
    candidate = 2
    while True:
        if candidate not in existing_roots and is_prime(candidate):
            return candidate
        candidate += 1


def sample_addresses(tree: PET) -> list[list[int]]:
    samples: list[list[int]] = [[]]

    for root in baseline(tree)[:3]:
        samples.append([root])

    recursive = first_recursive_address(tree)
    if recursive is not None:
        samples.append(recursive)

    deduped: list[list[int]] = []
    for address in samples:
        if address not in deduped:
            deduped.append(address)

    return deduped


def compact_resolution(tree: PET, address: list[int]) -> dict[str, Any]:
    resolution = resolve_address(tree, address)

    return {
        "address": address,
        "valid": resolution["valid"],
        "reason": resolution["reason"],
        "selected_root": resolution["selected_root"],
        "selected_exponent_kind": resolution["selected_exponent_kind"],
        "terminal_baseline": resolution["terminal_baseline"],
        "baseline_index_path": resolution["baseline_index_path"],
    }


def try_sample(label: str, factory: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        payload = factory()
    except Exception as exc:  # pragma: no cover - defensive report guard
        return {
            "label": label,
            "available": False,
            "error": type(exc).__name__,
            "reason": str(exc),
        }

    return {
        "label": label,
        "available": True,
        "payload": payload,
    }


def compact_x_sample(sample: dict[str, Any]) -> dict[str, Any]:
    payload = sample["payload"]
    operation = payload["operation"]
    parent = payload["parent_resolution"]

    return {
        "label": sample["label"],
        "available": True,
        "op": operation["op"],
        "valid": operation["valid"],
        "reason": operation["reason"],
        "parent_address": parent["parent_address"],
        "target_baseline": parent["target_baseline"],
    }


def compact_y_sample(sample: dict[str, Any]) -> dict[str, Any]:
    payload = sample["payload"]
    operation = payload["operation"]
    target = payload["target_resolution"]

    return {
        "label": sample["label"],
        "available": True,
        "op": operation["op"],
        "valid": operation["valid"],
        "reason": operation["reason"],
        "address": target["address"],
        "selected_root": target["selected_root"],
        "selected_exponent_kind": target["selected_exponent_kind"],
        "mutated_value": operation.get("mutated_value"),
    }


def compact_xy_sample(sample: dict[str, Any]) -> dict[str, Any]:
    payload = sample["payload"]

    return {
        "label": sample["label"],
        "available": True,
        "x_operation": payload["x_operation"],
        "y_operation": payload["y_operation"],
        "left_valid": payload["left"]["valid"],
        "left_final_value": payload["left"]["final_value"],
        "right_valid": payload["right"]["valid"],
        "right_final_value": payload["right"]["final_value"],
        "relation": payload["relation"],
    }


def compact_stability_sample(sample: dict[str, Any]) -> dict[str, Any]:
    payload = sample["payload"]

    return {
        "label": sample["label"],
        "available": True,
        "tracked_address": payload["tracked_address"],
        "operator": payload["operator"],
        "before_valid": payload["before"]["valid"],
        "after_valid": None if payload["after"] is None else payload["after"]["valid"],
        "stability": payload["stability"],
    }


def unavailable(label: str, reason: str) -> dict[str, Any]:
    return {
        "label": label,
        "available": False,
        "reason": reason,
    }


def build_payload(n: int) -> dict[str, Any]:
    tree = encode(n)
    roots = baseline(tree)
    q_new = next_new_prime(roots)
    first_root = roots[0]
    second_or_first_root = roots[1] if len(roots) > 1 else roots[0]
    leaf_address = first_leaf_address(tree) or [first_root]
    recursive_address = first_recursive_address(tree)

    address_samples = [
        compact_resolution(tree, address)
        for address in sample_addresses(tree)
    ]

    x_samples: list[dict[str, Any]] = [
        compact_x_sample(
            try_sample(
                "new-top-level-fresh-root",
                lambda: build_x_payload(n, [], "NEW", q_new),
            )
        )
    ]

    if len(roots) > 1:
        x_samples.append(
            compact_x_sample(
                try_sample(
                    "drop-top-level-first-root",
                    lambda: build_x_payload(n, [], "DROP", first_root),
                )
            )
        )
    else:
        x_samples.append(unavailable("drop-top-level-first-root", "single-root-baseline"))

    y_samples: list[dict[str, Any]] = [
        compact_y_sample(
            try_sample(
                "inc-first-root-target",
                lambda: build_y_mutation_payload(n, [first_root], "INC"),
            )
        ),
        compact_y_sample(
            try_sample(
                "dec-first-root-target",
                lambda: build_y_mutation_payload(n, [first_root], "DEC"),
            )
        ),
        compact_y_sample(
            try_sample(
                "inc-leaf-or-first-root-target",
                lambda: build_y_target_payload(n, leaf_address, "INC"),
            )
        ),
    ]

    xy_samples: list[dict[str, Any]] = [
        compact_xy_sample(
            try_sample(
                "new-fresh-root-with-existing-y-target",
                lambda: build_xy_payload(n, [], "NEW", q_new, [second_or_first_root], "INC"),
            )
        ),
        compact_xy_sample(
            try_sample(
                "new-fresh-root-creates-y-target",
                lambda: build_xy_payload(n, [], "NEW", q_new, [q_new], "INC"),
            )
        ),
    ]

    if len(roots) > 1:
        xy_samples.append(
            compact_xy_sample(
                try_sample(
                    "drop-root-removes-y-target",
                    lambda: build_xy_payload(n, [], "DROP", first_root, [first_root], "INC"),
                )
            )
        )
    else:
        xy_samples.append(unavailable("drop-root-removes-y-target", "single-root-baseline"))

    stability_samples: list[dict[str, Any]] = [
        compact_stability_sample(
            try_sample(
                "unrelated-new-keeps-existing-address-stable",
                lambda: build_address_stability_payload(
                    n,
                    [second_or_first_root],
                    "NEW",
                    root=q_new,
                ),
            )
        ),
        compact_stability_sample(
            try_sample(
                "new-creates-fresh-address",
                lambda: build_address_stability_payload(n, [q_new], "NEW", root=q_new),
            )
        ),
    ]

    if len(roots) > 1:
        stability_samples.append(
            compact_stability_sample(
                try_sample(
                    "drop-destroys-existing-address",
                    lambda: build_address_stability_payload(
                        n,
                        [first_root],
                        "DROP",
                        root=first_root,
                    ),
                )
            )
        )
    else:
        stability_samples.append(unavailable("drop-destroys-existing-address", "single-root-baseline"))

    stability_samples.append(
        compact_stability_sample(
            try_sample(
                "inc-can-retarget-address",
                lambda: build_address_stability_payload(
                    n,
                    [first_root],
                    "INC",
                    operator_address=[first_root],
                ),
            )
        )
    )

    if recursive_address is not None:
        stability_samples.append(
            compact_stability_sample(
                try_sample(
                    "dec-can-leaf-block-recursive-address",
                    lambda: build_address_stability_payload(
                        n,
                        recursive_address,
                        "DEC",
                        operator_address=[recursive_address[0]],
                    ),
                )
            )
        )
    else:
        stability_samples.append(unavailable("dec-can-leaf-block-recursive-address", "no-recursive-address"))

    axis_payload = build_axis_invariant_payload()

    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "n": n,
        "pet": to_jsonable(tree),
        "top_level_baseline": roots,
        "sample_addresses": address_samples,
        "axis_invariants": {
            "schema": axis_payload["schema"],
            "summary": axis_payload["summary"],
            "rows": axis_payload["rows"],
        },
        "x_axis_samples": x_samples,
        "y_axis_samples": y_samples,
        "xy_composition_samples": xy_samples,
        "address_stability_samples": stability_samples,
        "boundaries": BOUNDARIES,
    }


def print_text(payload: dict[str, Any]) -> None:
    print(f"schema = {payload['schema']}")
    print(f"claim = {payload['claim']}")
    print(f"n = {payload['n']}")
    print(f"top_level_baseline = {payload['top_level_baseline']}")
    print(f"axis_invariant_summary = {payload['axis_invariants']['summary']}")
    print()

    print("sample_addresses:")
    for row in payload["sample_addresses"]:
        print(
            f"- address={row['address']} "
            f"valid={str(row['valid']).lower()} "
            f"reason={row['reason']} "
            f"selected_root={row['selected_root']} "
            f"kind={row['selected_exponent_kind']}"
        )

    print()
    print("x_axis_samples:")
    for row in payload["x_axis_samples"]:
        print(f"- {row['label']}: valid={row.get('valid')} reason={row.get('reason')}")

    print()
    print("y_axis_samples:")
    for row in payload["y_axis_samples"]:
        print(
            f"- {row['label']}: valid={row.get('valid')} "
            f"reason={row.get('reason')} mutated_value={row.get('mutated_value')}"
        )

    print()
    print("xy_composition_samples:")
    for row in payload["xy_composition_samples"]:
        print(f"- {row['label']}: relation={row.get('relation')}")

    print()
    print("address_stability_samples:")
    for row in payload["address_stability_samples"]:
        print(f"- {row['label']}: stability={row.get('stability')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Experimental PET/PEG operator semantics report."
    )
    parser.add_argument("n", type=int, metavar="N", help="integer N >= 2")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args(argv)

    if args.n < 2:
        raise ValueError("N must be >= 2")

    payload = build_payload(args.n)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
