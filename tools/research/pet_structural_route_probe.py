#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from typing import Any

from pet.structural_route import build_structural_route_result


def pet_seed_int(raw: str) -> int:
    value = int(raw)

    if value < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")

    return value


def build_result(
    *,
    source_n: int,
    target_value: int | None,
    target_shape_of: int | None,
    max_depth: int,
    max_paths: int | None,
) -> dict[str, Any]:
    return build_structural_route_result(
        source_n=source_n,
        target_value=target_value,
        target_shape_of=target_shape_of,
        max_depth=max_depth,
        max_paths=max_paths,
    )


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
    parser.add_argument("source_n", type=pet_seed_int)
    parser.add_argument("--target-value", type=pet_seed_int)
    parser.add_argument("--target-shape-of", type=pet_seed_int)
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
