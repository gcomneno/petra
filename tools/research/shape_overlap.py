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
    left_children = list(left)
    right_children = list(right)
    common_children: list[Shape] = []

    used_right: set[int] = set()
    for left_child in left_children:
        best_index = None
        best_common: Shape | None = None
        best_size = 0

        for index, right_child in enumerate(right_children):
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


def subtract_common(shape: Shape, common: Shape) -> Shape:
    shape_children = list(shape)
    common_children = list(common)
    residual_children: list[Shape] = []
    used_shape: set[int] = set()

    for common_child in common_children:
        best_index = None
        best_residual: Shape | None = None
        best_removed = -1

        for index, shape_child in enumerate(shape_children):
            if index in used_shape:
                continue
            child_common = common_prefix_shape(shape_child, common_child)
            removed = shape_size(child_common)
            if removed > best_removed:
                best_index = index
                best_residual = subtract_common(shape_child, common_child)
                best_removed = removed

        if best_index is not None and best_residual is not None:
            used_shape.add(best_index)
            if best_residual:
                residual_children.append(best_residual)

    for index, shape_child in enumerate(shape_children):
        if index not in used_shape:
            residual_children.append(shape_child)

    return normalize_shape(tuple(residual_children))


def structural_distance(left: Shape, right: Shape) -> int:
    common = common_prefix_shape(left, right)
    return shape_size(left) + shape_size(right) - 2 * shape_size(common)


def draw_shape(shape: Shape, prefix: str = "") -> list[str]:
    if not shape:
        return [prefix + "•"]

    lines = [prefix + "•"]
    for index, child in enumerate(shape):
        is_last = index == len(shape) - 1
        branch = "└─ " if is_last else "├─ "
        extension = "   " if is_last else "│  "
        child_lines = draw_shape(child, prefix + branch)
        lines.append(child_lines[0])
        for line in child_lines[1:]:
            lines.append(prefix + extension + line[len(prefix + branch):])
    return lines


def print_shape(title: str, shape: Shape) -> None:
    print(title)
    print(f"  size = {shape_size(shape)}")
    print(f"  height = {shape_height(shape)}")
    for line in draw_shape(shape):
        print(f"  {line}")


def load_shape(n: int) -> Shape:
    payload = shape_signature_dict(n)
    return normalize_shape(as_shape_tuple(payload["signature"]))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Experimental PET shape overlap viewer."
    )
    parser.add_argument("left", type=int)
    parser.add_argument("right", type=int)
    args = parser.parse_args()

    if args.left < 1 or args.right < 1:
        raise SystemExit("shape_overlap expects integers >= 1")

    left_shape = load_shape(args.left)
    right_shape = load_shape(args.right)
    common = common_prefix_shape(left_shape, right_shape)
    left_only = subtract_common(left_shape, common)
    right_only = subtract_common(right_shape, common)
    distance = structural_distance(left_shape, right_shape)

    print("PET SHAPE OVERLAP")
    print()
    print(f"left = {args.left}")
    print(f"right = {args.right}")
    print(f"distance = {distance}")
    print(f"overlap_ratio_left = {shape_size(common) / shape_size(left_shape):.6f}")
    print(f"overlap_ratio_right = {shape_size(common) / shape_size(right_shape):.6f}")
    print()
    print_shape("Left shape", left_shape)
    print()
    print_shape("Right shape", right_shape)
    print()
    print_shape("Common shape", common)
    print()
    print_shape("Left residual", left_only)
    print()
    print_shape("Right residual", right_only)
    print()
    print("claim = PET shape overlap only; this does not factor N")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
