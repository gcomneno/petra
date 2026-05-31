#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from typing import Any

from pet import (
    certificate_from_path,
    pet_object_from_int,
    traverse_operator_graph_by_value,
)


SCHEMA = "pet.structural_route_probe.v0"
CLAIM = (
    "bounded PET/PEG operator graph route probe only; "
    "selected path is first match in deterministic bounded traversal, "
    "not a global optimality claim"
)


def positive_int(raw: str) -> int:
    value = int(raw)

    if value < 2:
        raise argparse.ArgumentTypeError("value must be >= 2")

    return value


def build_result(
    *,
    source_n: int,
    target_value: int | None,
    target_shape_of: int | None,
    max_depth: int,
    max_paths: int | None,
) -> dict[str, Any]:
    source_obj = pet_object_from_int(source_n)
    target_signature = None

    if target_shape_of is not None:
        target_signature = pet_object_from_int(target_shape_of).structural_signature()

    traversal = traverse_operator_graph_by_value(
        source_obj,
        max_depth=max_depth,
        max_paths=max_paths,
    )

    selected_path = None

    for path in traversal.paths:
        if target_value is not None and path.target.value != target_value:
            continue

        if (
            target_signature is not None
            and path.target.pet_object.structural_signature() != target_signature
        ):
            continue

        selected_path = path
        break

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "claim": CLAIM,
        "source_n": source_n,
        "target_value": target_value,
        "target_shape_of": target_shape_of,
        "max_depth": max_depth,
        "max_paths": max_paths,
        "traversal": {
            "path_count": traversal.path_count,
            "truncated": traversal.truncated,
        },
        "found": selected_path is not None,
        "reason": "path-found" if selected_path is not None else "no-path-within-bound",
        "selection_policy": "first-match-in-deterministic-bounded-bfs",
    }

    if selected_path is None:
        result["selected_path"] = None
        result["trace_certificate"] = None
        return result

    certificate = certificate_from_path(selected_path)

    result["selected_path"] = selected_path.to_dict()
    result["selected_cost"] = {
        "depth": selected_path.depth,
        "cost_model": "shortest-found-within-current-bounded-bfs-order",
    }
    result["trace_certificate"] = certificate.to_dict()

    return result


def print_text(result: dict[str, Any]) -> None:
    print("PET STRUCTURAL ROUTE PROBE")
    print(f"schema = {result['schema']}")
    print(f"claim = {result['claim']}")
    print()
    print(f"source_n = {result['source_n']}")
    print(f"target_value = {result['target_value']}")
    print(f"target_shape_of = {result['target_shape_of']}")
    print(f"max_depth = {result['max_depth']}")
    print(f"max_paths = {result['max_paths']}")
    print(f"path_count = {result['traversal']['path_count']}")
    print(f"truncated = {str(result['traversal']['truncated']).lower()}")
    print(f"found = {str(result['found']).lower()}")
    print(f"reason = {result['reason']}")

    if not result["found"]:
        return

    path = result["selected_path"]
    certificate = result["trace_certificate"]

    print()
    print("selected_path:")
    print(f"depth = {path['depth']}")
    print(f"values = {path['values']}")
    print(f"labels = {path['labels']}")
    print()
    print("trace_certificate:")
    print(f"valid = {str(certificate['valid']).lower()}")
    print(f"reason = {certificate['reason']}")
    print(f"checked_steps = {certificate['checked_steps']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research-only bounded PET/PEG structural route probe."
    )
    parser.add_argument("source_n", type=positive_int)
    parser.add_argument("--target-value", type=positive_int)
    parser.add_argument("--target-shape-of", type=positive_int)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-paths", type=int, default=200)
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.target_value is None and args.target_shape_of is None:
        raise SystemExit(
            "at least one of --target-value or --target-shape-of is required"
        )

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be >= 0")

    if args.max_paths < 1:
        raise SystemExit("--max-paths must be >= 1")

    result = build_result(
        source_n=args.source_n,
        target_value=args.target_value,
        target_shape_of=args.target_shape_of,
        max_depth=args.max_depth,
        max_paths=args.max_paths,
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
