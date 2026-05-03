#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any

from pet.core import shape_signature_dict


Shape = tuple[Any, ...]


def as_shape_tuple(obj: Any) -> Shape:
    if isinstance(obj, list):
        return tuple(as_shape_tuple(item) for item in obj)
    if isinstance(obj, tuple):
        return tuple(as_shape_tuple(item) for item in obj)
    return tuple()


def shape_key(shape: Shape) -> tuple:
    return tuple(shape_key(child) for child in shape)


def normalize_shape(shape: Shape) -> Shape:
    children = [normalize_shape(child) for child in shape]
    children.sort(key=shape_key)
    return tuple(children)


def shape_size(shape: Shape) -> int:
    return 1 + sum(shape_size(child) for child in shape)


def shape_height(shape: Shape) -> int:
    if not shape:
        return 1
    return 1 + max(shape_height(child) for child in shape)


def common_prefix_shape(left: Shape, right: Shape) -> Shape:
    common_children: list[Shape] = []
    used_right: set[int] = set()

    for left_child in left:
        best_index = None
        best_common: Shape | None = None
        best_size = 0

        for index, right_child in enumerate(right):
            if index in used_right:
                continue
            candidate = common_prefix_shape(left_child, right_child)
            candidate_size = shape_size(candidate)
            if candidate_size > best_size:
                best_index = index
                best_common = candidate
                best_size = candidate_size

        if best_index is not None and best_common is not None:
            used_right.add(best_index)
            common_children.append(best_common)

    return normalize_shape(tuple(common_children))


def structural_distance(left: Shape, right: Shape) -> int:
    common = common_prefix_shape(left, right)
    return shape_size(left) + shape_size(right) - 2 * shape_size(common)


def load_shape(n: int) -> Shape:
    payload = shape_signature_dict(n)
    return normalize_shape(as_shape_tuple(payload["signature"]))


def flat_lens_shape(leaf_count: int) -> Shape:
    if leaf_count < 1:
        raise ValueError("leaf_count must be >= 1")
    return tuple(tuple() for _ in range(leaf_count))


def flatten_root_branches(shape: Shape) -> Shape:
    """Project root branches to flat leaves without using arithmetic factors."""
    if not shape:
        return shape
    return tuple(tuple() for _ in shape)


def lens_name(leaf_count: int) -> str:
    names = {
        1: "one-leaf",
        2: "two-leaf",
        3: "three-leaf",
        4: "four-leaf",
        5: "five-leaf",
        6: "six-leaf",
    }
    return names.get(leaf_count, f"{leaf_count}-leaf")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Experimental PET stencil-transfer lens probe."
    )
    parser.add_argument("n", type=int, metavar="N")
    parser.add_argument(
        "--max-leaves",
        type=int,
        default=8,
        help="maximum flat leaf lens to test",
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="project non-flat root branches to flat leaves before probing",
    )
    args = parser.parse_args()

    if args.n < 1:
        raise SystemExit("stencil_lens_probe expects integers >= 1")
    if args.max_leaves < 1:
        raise SystemExit("--max-leaves expects integers >= 1")

    original_source = load_shape(args.n)
    original_source_size = shape_size(original_source)
    original_source_height = shape_height(original_source)
    flattening_steps = max(0, original_source_height - 2)

    source = (
        normalize_shape(flatten_root_branches(original_source))
        if args.flatten
        else original_source
    )
    source_size = shape_size(source)
    source_height = shape_height(source)

    rows = []
    for leaves in range(1, args.max_leaves + 1):
        target = normalize_shape(flat_lens_shape(leaves))
        common = common_prefix_shape(target, source)
        target_size = shape_size(target)
        common_size = shape_size(common)
        distance = structural_distance(target, source)

        target_coverage = common_size / target_size
        stencil_usage = common_size / source_size
        identical = distance == 0
        overshoots = target_coverage < 1.0

        if identical:
            role = "identical"
        elif overshoots:
            role = "overshoots"
        elif target_coverage == 1.0:
            role = "proper-lens"
        else:
            role = "partial"

        rows.append(
            {
                "leaves": leaves,
                "name": lens_name(leaves),
                "target_size": target_size,
                "common_size": common_size,
                "target_coverage": target_coverage,
                "stencil_usage": stencil_usage,
                "distance": distance,
                "role": role,
            }
        )

    candidates = [
        row
        for row in rows
        if row["role"] == "proper-lens"
    ]
    best = max(
        candidates,
        key=lambda row: (
            row["stencil_usage"],
            row["target_coverage"],
            -row["distance"],
            row["leaves"],
        ),
        default=None,
    )

    print("PET STENCIL LENS PROBE")
    print()

    print(f"N = {args.n}")
    print(f"original_source_size = {original_source_size}")
    print(f"original_source_height = {original_source_height}")
    print(f"flattening_steps = {flattening_steps}")
    print(
        "flattening_recommended = "
        f"{'yes' if flattening_steps else 'no'}"
    )
    print(f"flatten_applied = {'yes' if args.flatten else 'no'}")
    print(f"source_size = {source_size}")
    print(f"source_height = {source_height}")
    print(f"max_leaves = {args.max_leaves}")
    print()
    print("Candidate lenses")
    print(
        "  lens       | leaves | coverage | usage    | distance | role"
    )
    for row in rows:
        marker = " <-- best proper lens" if best is row else ""
        print(
            f"  {row['name']:<10} | "
            f"{row['leaves']:>6} | "
            f"{row['target_coverage']:.6f} | "
            f"{row['stencil_usage']:.6f} | "
            f"{row['distance']:>8} | "
            f"{row['role']}{marker}"
        )

    print()
    if best is None:
        print("recommended_lens = none")
        print("reason = no proper flat lens found")
    else:
        print(f"recommended_lens = {best['name']}")
        print(f"recommended_leaf_count = {best['leaves']}")
        print(f"recommended_stencil_usage = {best['stencil_usage']:.6f}")
        print(f"recommended_target_coverage = {best['target_coverage']:.6f}")
        print(
            "reason = largest fully covered proper lens with maximal stencil usage"
        )

    print()
    print("claim = PET stencil lens probe only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
