from __future__ import annotations

from typing import Any

from .graph import traverse_operator_graph_by_value
from .object_model import pet_object_from_int
from .traces import certificate_from_path


STRUCTURAL_ROUTE_SCHEMA = "pet.structural_route.v0"
STRUCTURAL_ROUTE_CLAIM = (
    "bounded PET/PEG structural route planning; "
    "selected path is first match in deterministic bounded traversal, "
    "not a global optimality claim"
)


def build_structural_route_result(
    *,
    source_n: int,
    target_value: int | None,
    target_shape_of: int | None,
    max_depth: int,
    max_paths: int | None,
) -> dict[str, Any]:
    """Build a bounded PET/PEG structural route result.

    The route starts from a PET object seed and searches the bounded operator
    graph for the first deterministic match by value and/or structural shape.
    """

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
        "schema": STRUCTURAL_ROUTE_SCHEMA,
        "claim": STRUCTURAL_ROUTE_CLAIM,
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
