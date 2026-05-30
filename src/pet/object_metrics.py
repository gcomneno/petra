from __future__ import annotations

from typing import Any

from .object_model import PETObject


def _metric_roots(obj: PETObject) -> tuple[PETObject, ...]:
    """Return the metric roots for a PET object.

    The PET/PEG 2.0 root object is a container for the top-level baseline, while
    a child object is itself a represented primal-root node.
    """

    if obj.is_root:
        return obj.children

    return (obj,)


def _node_count(nodes: tuple[PETObject, ...]) -> int:
    total = 0

    for node in nodes:
        total += 1
        total += _node_count(node.children)

    return total


def pet_object_node_count(obj: PETObject) -> int:
    """Return the legacy-compatible node count for a PETObject."""

    return _node_count(_metric_roots(obj))


def _leaf_count(nodes: tuple[PETObject, ...]) -> int:
    total = 0

    for node in nodes:
        if not node.children:
            total += 1
        else:
            total += _leaf_count(node.children)

    return total


def pet_object_leaf_count(obj: PETObject) -> int:
    """Return the legacy-compatible leaf count for a PETObject."""

    return _leaf_count(_metric_roots(obj))


def _height(nodes: tuple[PETObject, ...]) -> int:
    if not nodes:
        return 0

    child_heights = [_height(node.children) for node in nodes]
    return 1 + max(child_heights, default=0)


def pet_object_height(obj: PETObject) -> int:
    """Return the legacy-compatible height for a PETObject."""

    return _height(_metric_roots(obj))


def _max_branching(nodes: tuple[PETObject, ...]) -> int:
    current = len(nodes)
    child_max = max((_max_branching(node.children) for node in nodes), default=0)
    return max(current, child_max)


def pet_object_max_branching(obj: PETObject) -> int:
    """Return the legacy-compatible max branching for a PETObject."""

    return _max_branching(_metric_roots(obj))


def _collect_leaf_depths(
    nodes: tuple[PETObject, ...],
    depth: int,
    depths: list[int],
) -> None:
    for node in nodes:
        if not node.children:
            depths.append(depth)
        else:
            _collect_leaf_depths(node.children, depth + 1, depths)


def pet_object_average_leaf_depth(obj: PETObject) -> float:
    """Return the legacy-compatible average leaf depth for a PETObject."""

    depths: list[int] = []
    _collect_leaf_depths(_metric_roots(obj), 1, depths)
    return sum(depths) / len(depths)


def pet_object_leaf_depth_variance(obj: PETObject) -> float:
    """Return the legacy-compatible leaf depth variance for a PETObject."""

    depths: list[int] = []
    _collect_leaf_depths(_metric_roots(obj), 1, depths)
    mean = sum(depths) / len(depths)
    return sum((depth - mean) ** 2 for depth in depths) / len(depths)


def _branch_profile(nodes: tuple[PETObject, ...]) -> list[int]:
    profile: list[int] = []
    current = nodes

    while current:
        profile.append(len(current))
        next_level: list[PETObject] = []

        for node in current:
            next_level.extend(node.children)

        current = tuple(next_level)

    return profile


def pet_object_branch_profile(obj: PETObject) -> list[int]:
    """Return the legacy-compatible branch profile for a PETObject."""

    return _branch_profile(_metric_roots(obj))


def pet_object_recursive_mass(obj: PETObject) -> int:
    """Return the legacy-compatible recursive mass for a PETObject."""

    return pet_object_node_count(obj) - pet_object_leaf_count(obj)


def pet_object_metrics_dict(obj: PETObject) -> dict[str, Any]:
    """Return legacy-compatible metrics directly from a PETObject."""

    return {
        "node_count": pet_object_node_count(obj),
        "leaf_count": pet_object_leaf_count(obj),
        "height": pet_object_height(obj),
        "max_branching": pet_object_max_branching(obj),
        "recursive_mass": pet_object_recursive_mass(obj),
        "average_leaf_depth": pet_object_average_leaf_depth(obj),
        "leaf_depth_variance": pet_object_leaf_depth_variance(obj),
        "branch_profile": pet_object_branch_profile(obj),
    }
