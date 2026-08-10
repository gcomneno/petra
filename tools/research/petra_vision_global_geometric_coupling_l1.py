"""PETRA VISION Gate 2 G2-L1 uniform full-lattice propagation.

The dynamic domain is the exact minimal axis-aligned lattice rectangle
containing the source occupied geometry. Occupancy affects only the initial
scalar field; the propagation medium itself is uniform.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


Cell: TypeAlias = tuple[int, int]
State: TypeAlias = tuple[int, ...]
Signature: TypeAlias = tuple[tuple[int, ...], ...]


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-full-lattice-v0"
)

EULER_DENOMINATOR = 8
MAXIMUM_DEGREE_BOUND = 4

SAMPLE_STEPS = (
    1,
    2,
    4,
    8,
    16,
    32,
)


@dataclass(frozen=True)
class LatticeEdge:
    left: int
    right: int
    weight: int


@dataclass(frozen=True)
class FullLatticeGraph:
    cells: tuple[Cell, ...]
    edges: tuple[LatticeEdge, ...]
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
            "G2-L1 expects an exact OrthogonalGeometry"
        )

    if not geometry.cells:
        raise ValueError(
            "G2-L1 requires non-empty geometry"
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


def build_full_lattice_graph(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool = True,
) -> FullLatticeGraph:
    """Build the frozen uniform bounded L1 lattice."""

    current = _require_geometry(
        geometry
    )

    if type(coupled) is not bool:
        raise TypeError(
            "coupled must be an exact bool"
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

    edge_weight = 1 if coupled else 0

    edges: list[LatticeEdge] = []

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

            edges.append(
                LatticeEdge(
                    left=left_index,
                    right=right_index,
                    weight=edge_weight,
                )
            )

    frozen_edges = tuple(edges)

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

    occupied_set = set(
        current.cells
    )

    initial_state = tuple(
        1 if cell in occupied_set else 0
        for cell in cells
    )

    return FullLatticeGraph(
        cells=cells,
        edges=frozen_edges,
        adjacency=adjacency,
        initial_state=initial_state,
    )


def edge_manifest(
    graph: FullLatticeGraph,
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


def maximum_degree(
    graph: FullLatticeGraph,
) -> int:
    """Return the unweighted lattice degree bound actually present."""

    return max(
        (
            len(neighbors)
            for neighbors in graph.adjacency
        ),
        default=0,
    )


def evolve_lattice_numerator(
    state: State,
    graph: FullLatticeGraph,
    *,
    denominator: int = EULER_DENOMINATOR,
) -> State:
    """Apply one exact integer Euler numerator step."""

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


def full_lattice_signature(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
    denominator: int = EULER_DENOMINATOR,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> Signature:
    """Return the frozen coordinate-free L1 dynamic signature."""

    graph = build_full_lattice_graph(
        geometry,
        coupled=coupled,
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
        state = evolve_lattice_numerator(
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
    "EULER_DENOMINATOR",
    "FullLatticeGraph",
    "LatticeEdge",
    "MAXIMUM_DEGREE_BOUND",
    "PROTOCOL_ID",
    "SAMPLE_STEPS",
    "build_full_lattice_graph",
    "edge_manifest",
    "evolve_lattice_numerator",
    "full_lattice_signature",
    "maximum_degree",
]
