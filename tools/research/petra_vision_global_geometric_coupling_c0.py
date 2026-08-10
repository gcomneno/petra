"""PETRA VISION Gate 2 G2-C0 component-null representation.

Disconnected occupied components are extracted geometrically, independently
translated to the origin, observed through the frozen graph-Laplacian v1
global-multiset reader, and finally collected as an unordered
multiplicity-preserving multiset.

No inter-component placement or coupling is retained.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

V1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-component-null-v0"
)

INNER_PROTOCOL_ID = "petra-vision-graph-laplacian-v1"
COMPONENT_ADJACENCY = "four-neighbor"
SAMPLE_STEPS = (
    1,
    2,
    4,
    8,
    16,
    32,
)


ComponentSignature: TypeAlias = tuple[object, ...]
ComponentNullSignature: TypeAlias = tuple[
    ComponentSignature,
    ...,
]


def _load_module(
    path: Path,
    name: str,
) -> ModuleType:
    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"unable to load research module: {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate2_c0_graph_laplacian_v1",
)


if v1.PROTOCOL_ID != INNER_PROTOCOL_ID:
    raise RuntimeError(
        "G2-C0 requires frozen graph-Laplacian v1"
    )

if v1.SAMPLE_STEPS != SAMPLE_STEPS:
    raise RuntimeError(
        "G2-C0 requires frozen graph-Laplacian v1 sample schedule"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G2-C0 expects an exact OrthogonalGeometry"
        )

    if not geometry.cells:
        raise ValueError(
            "G2-C0 requires non-empty geometry"
        )

    return geometry


def _normalize_cells(
    cells: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int], ...]:
    min_x = min(
        x
        for x, _y in cells
    )
    min_y = min(
        y
        for _x, y in cells
    )

    return tuple(sorted(
        (
            x - min_x,
            y - min_y,
        )
        for x, y in cells
    ))


def connected_component_geometries(
    geometry: OrthogonalGeometry,
) -> tuple[OrthogonalGeometry, ...]:
    """Return independently translated occupied components.

    The extraction itself is delegated to the frozen v1 occupied-cell graph,
    whose components use orthogonal four-neighbor connectivity.
    """

    current = _require_geometry(
        geometry
    )

    graph = v1.build_geometry_graph(
        current
    )

    components: list[
        OrthogonalGeometry
    ] = []

    for component in graph.components:
        source_cells = tuple(
            graph.cells[vertex]
            for vertex in component
        )

        normalized = _normalize_cells(
            source_cells
        )

        components.append(
            OrthogonalGeometry(
                cells=normalized
            )
        )

    return tuple(
        components
    )


def component_signature(
    component: OrthogonalGeometry,
) -> ComponentSignature:
    """Observe one normalized component through frozen v1."""

    current = _require_geometry(
        component
    )

    signatures = (
        v1.geometry_dynamic_signatures(
            current
        )
    )

    return signatures[
        "global_multiset"
    ]


def ordered_component_signatures(
    geometry: OrthogonalGeometry,
) -> tuple[
    ComponentSignature,
    ...,
]:
    """Return extraction-order signatures for audit only.

    Component order is not part of the primary C0 reader.
    """

    return tuple(
        component_signature(component)
        for component in (
            connected_component_geometries(
                geometry
            )
        )
    )


def component_null_signature(
    geometry: OrthogonalGeometry,
) -> ComponentNullSignature:
    """Return the unordered multiplicity-preserving C0 signature."""

    return tuple(sorted(
        ordered_component_signatures(
            geometry
        )
    ))


def component_count(
    geometry: OrthogonalGeometry,
) -> int:
    """Static control: number of disconnected occupied components."""

    return len(
        connected_component_geometries(
            geometry
        )
    )


def static_component_profile_signature(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[object, ...], ...]:
    """Return an unordered static graph-profile control.

    Each component is independently normalized before its frozen v1 graph
    profile is read. No dynamic propagation is involved.
    """

    profiles = []

    for component in (
        connected_component_geometries(
            geometry
        )
    ):
        graph = v1.build_geometry_graph(
            component
        )
        profile = v1.graph_profile(
            graph
        )

        profiles.append((
            profile["vertices"],
            profile["edges"],
            profile["components"],
            profile["isolated_vertices"],
            tuple(
                profile[
                    "component_cycle_ranks"
                ]
            ),
            profile["maximum_degree"],
        ))

    return tuple(sorted(
        profiles
    ))


__all__ = [
    "COMPONENT_ADJACENCY",
    "INNER_PROTOCOL_ID",
    "PROTOCOL_ID",
    "SAMPLE_STEPS",
    "component_count",
    "component_null_signature",
    "component_signature",
    "connected_component_geometries",
    "ordered_component_signatures",
    "static_component_profile_signature",
]
