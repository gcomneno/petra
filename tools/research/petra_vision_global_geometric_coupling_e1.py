"""PETRA VISION Gate 2 G2-E1 occupied/empty heterogeneous field.

The dynamic domain is the exact minimal axis-aligned lattice rectangle.
Every site has a frozen occupied/empty material label. The heterogeneous
medium assigns symmetric edge conductance from the material labels only.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


Cell: TypeAlias = tuple[int, int]
State: TypeAlias = tuple[int, ...]
Signature: TypeAlias = tuple[tuple[int, ...], ...]
StaticMaterialSignature: TypeAlias = tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
]


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-occupied-empty-field-v0"
)

EDGE_WEIGHT_RULE = "1+occupancy(u)+occupancy(v)"

EULER_DENOMINATOR = 16
MAXIMUM_EDGE_WEIGHT = 3
MAXIMUM_WEIGHTED_DEGREE_BOUND = 12

SAMPLE_STEPS = (
    1,
    2,
    4,
    8,
    16,
    32,
)


@dataclass(frozen=True)
class FieldEdge:
    left: int
    right: int
    weight: int


@dataclass(frozen=True)
class OccupiedEmptyFieldGraph:
    cells: tuple[Cell, ...]
    material: tuple[int, ...]
    edges: tuple[FieldEdge, ...]
    adjacency: tuple[
        tuple[tuple[int, int], ...],
        ...,
    ]
    initial_state: State


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G2-E1 expects an exact OrthogonalGeometry"
        )

    if not geometry.cells:
        raise ValueError(
            "G2-E1 requires non-empty geometry"
        )

    return geometry


def _lattice_cells(
    geometry: OrthogonalGeometry,
) -> tuple[Cell, ...]:
    occupied = geometry.cells

    xmin = min(
        x
        for x, _y in occupied
    )
    xmax = max(
        x
        for x, _y in occupied
    )
    ymin = min(
        y
        for _x, y in occupied
    )
    ymax = max(
        y
        for _x, y in occupied
    )

    return tuple(
        (x, y)
        for x in range(xmin, xmax + 1)
        for y in range(ymin, ymax + 1)
    )


def _heterogeneous_edge_weight(
    left_material: int,
    right_material: int,
) -> int:
    if left_material not in (0, 1):
        raise ValueError(
            "material labels must be binary"
        )

    if right_material not in (0, 1):
        raise ValueError(
            "material labels must be binary"
        )

    return (
        1
        + left_material
        + right_material
    )


def build_occupied_empty_field_graph(
    geometry: OrthogonalGeometry,
    *,
    heterogeneous: bool = True,
) -> OccupiedEmptyFieldGraph:
    """Build the frozen E1 heterogeneous or matched-uniform lattice."""

    current = _require_geometry(
        geometry
    )

    if type(heterogeneous) is not bool:
        raise TypeError(
            "heterogeneous must be an exact bool"
        )

    cells = _lattice_cells(
        current
    )

    index = {
        cell: position
        for position, cell in enumerate(
            cells
        )
    }

    occupied_set = set(
        current.cells
    )

    material = tuple(
        1 if cell in occupied_set else 0
        for cell in cells
    )

    edges: list[FieldEdge] = []

    for left_index, (x, y) in enumerate(
        cells
    ):
        for neighbor_cell in (
            (x + 1, y),
            (x, y + 1),
        ):
            right_index = index.get(
                neighbor_cell
            )

            if right_index is None:
                continue

            if heterogeneous:
                weight = _heterogeneous_edge_weight(
                    material[left_index],
                    material[right_index],
                )
            else:
                weight = 1

            edges.append(
                FieldEdge(
                    left=left_index,
                    right=right_index,
                    weight=weight,
                )
            )

    frozen_edges = tuple(
        edges
    )

    adjacency_lists: list[
        list[tuple[int, int]]
    ] = [
        []
        for _cell in cells
    ]

    for edge in frozen_edges:
        adjacency_lists[
            edge.left
        ].append(
            (
                edge.right,
                edge.weight,
            )
        )
        adjacency_lists[
            edge.right
        ].append(
            (
                edge.left,
                edge.weight,
            )
        )

    adjacency = tuple(
        tuple(sorted(neighbors))
        for neighbors in adjacency_lists
    )

    return OccupiedEmptyFieldGraph(
        cells=cells,
        material=material,
        edges=frozen_edges,
        adjacency=adjacency,
        initial_state=material,
    )


def edge_manifest(
    graph: OccupiedEmptyFieldGraph,
) -> tuple[
    tuple[Cell, Cell, int],
    ...,
]:
    return tuple(
        (
            graph.cells[edge.left],
            graph.cells[edge.right],
            edge.weight,
        )
        for edge in graph.edges
    )


def weighted_degrees(
    graph: OccupiedEmptyFieldGraph,
) -> tuple[int, ...]:
    return tuple(
        sum(
            weight
            for _neighbor, weight in neighbors
        )
        for neighbors in graph.adjacency
    )


def maximum_weighted_degree(
    graph: OccupiedEmptyFieldGraph,
) -> int:
    return max(
        weighted_degrees(graph),
        default=0,
    )


def edge_weight_histogram(
    graph: OccupiedEmptyFieldGraph,
) -> tuple[tuple[int, int], ...]:
    counts = Counter(
        edge.weight
        for edge in graph.edges
    )

    return tuple(
        (
            weight,
            counts.get(weight, 0),
        )
        for weight in (
            1,
            2,
            3,
        )
    )


def static_material_signature(
    geometry: OrthogonalGeometry,
) -> StaticMaterialSignature:
    """Return the frozen coordinate-free static material diagnostic."""

    graph = build_occupied_empty_field_graph(
        geometry,
        heterogeneous=True,
    )

    degrees = weighted_degrees(
        graph
    )

    vertex_material_degree_multiset = tuple(sorted(
        (
            graph.material[index],
            degrees[index],
        )
        for index in range(
            len(graph.cells)
        )
    ))

    return (
        vertex_material_degree_multiset,
        edge_weight_histogram(
            graph
        ),
    )


def evolve_field_numerator(
    state: State,
    graph: OccupiedEmptyFieldGraph,
    *,
    denominator: int = EULER_DENOMINATOR,
) -> State:
    """Apply one exact weighted Euler numerator step."""

    if type(denominator) is not int or denominator <= 0:
        raise ValueError(
            "denominator must be a positive integer"
        )

    if len(state) != len(
        graph.cells
    ):
        raise ValueError(
            "state length must equal lattice vertex count"
        )

    next_state: list[int] = []

    for vertex, neighbors in enumerate(
        graph.adjacency
    ):
        weighted_degree = sum(
            weight
            for _neighbor, weight in neighbors
        )

        weighted_neighbors = sum(
            weight * state[neighbor]
            for neighbor, weight in neighbors
        )

        laplacian_value = (
            weighted_degree * state[vertex]
            - weighted_neighbors
        )

        next_state.append(
            denominator * state[vertex]
            - laplacian_value
        )

    return tuple(
        next_state
    )


def occupied_empty_field_signature(
    geometry: OrthogonalGeometry,
    *,
    heterogeneous: bool,
    denominator: int = EULER_DENOMINATOR,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> Signature:
    """Return the frozen coordinate-free E1 dynamic signature."""

    graph = build_occupied_empty_field_graph(
        geometry,
        heterogeneous=heterogeneous,
    )

    if type(denominator) is not int or denominator <= 0:
        raise ValueError(
            "denominator must be a positive integer"
        )

    if not sample_steps:
        raise ValueError(
            "sample_steps must not be empty"
        )

    if (
        tuple(sorted(set(sample_steps)))
        != sample_steps
        or sample_steps[0] <= 0
    ):
        raise ValueError(
            "sample_steps must be strictly increasing "
            "positive integers"
        )

    state = graph.initial_state

    sample_set = set(
        sample_steps
    )

    samples: list[tuple[int, ...]] = []

    for step in range(
        1,
        sample_steps[-1] + 1,
    ):
        state = evolve_field_numerator(
            state,
            graph,
            denominator=denominator,
        )

        if step in sample_set:
            samples.append(
                tuple(sorted(state))
            )

    return tuple(
        samples
    )


__all__ = [
    "EDGE_WEIGHT_RULE",
    "EULER_DENOMINATOR",
    "FieldEdge",
    "MAXIMUM_EDGE_WEIGHT",
    "MAXIMUM_WEIGHTED_DEGREE_BOUND",
    "OccupiedEmptyFieldGraph",
    "PROTOCOL_ID",
    "SAMPLE_STEPS",
    "build_occupied_empty_field_graph",
    "edge_manifest",
    "edge_weight_histogram",
    "evolve_field_numerator",
    "maximum_weighted_degree",
    "occupied_empty_field_signature",
    "static_material_signature",
    "weighted_degrees",
]
