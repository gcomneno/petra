"""Geometry-only PETRA VISION Gate 2 D1 coupling research tool."""

from __future__ import annotations

from dataclasses import dataclass

from petra.vision.geometry import OrthogonalGeometry


Cell = tuple[int, int]
State = tuple[int, ...]
Signature = tuple[tuple[int, ...], ...]

PROTOCOL_ID = "petra-vision-global-geometric-coupling-distance2-v0"

LOCAL_WEIGHT = 2
BRIDGE_WEIGHT = 1
EULER_DENOMINATOR = 16
SAMPLE_STEPS = (1, 2, 4, 8, 16, 32)

MAX_WEIGHTED_DEGREE_BOUND = 12


@dataclass(frozen=True)
class WeightedEdge:
    left: int
    right: int
    weight: int
    kind: str


@dataclass(frozen=True)
class Distance2GeometryGraph:
    cells: tuple[Cell, ...]
    edges: tuple[WeightedEdge, ...]
    adjacency: tuple[tuple[tuple[int, int], ...], ...]
    original_components: tuple[tuple[int, ...], ...]


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "D1 expects an exact OrthogonalGeometry"
        )

    return geometry


def _require_bridge_weight(
    bridge_weight: int,
) -> int:
    if (
        type(bridge_weight) is not int
        or bridge_weight < 0
    ):
        raise ValueError(
            "bridge_weight must be a non-negative integer"
        )

    return bridge_weight


def _original_components(
    cell_count: int,
    local_edges: tuple[WeightedEdge, ...],
) -> tuple[tuple[int, ...], ...]:
    adjacency: list[list[int]] = [
        []
        for _index in range(cell_count)
    ]

    for edge in local_edges:
        adjacency[edge.left].append(edge.right)
        adjacency[edge.right].append(edge.left)

    unseen = set(range(cell_count))
    components: list[tuple[int, ...]] = []

    while unseen:
        start = min(unseen)
        unseen.remove(start)

        stack = [start]
        component: list[int] = []

        while stack:
            current = stack.pop()
            component.append(current)

            for neighbor in sorted(
                adjacency[current],
                reverse=True,
            ):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)

        components.append(
            tuple(sorted(component))
        )

    return tuple(components)


def build_distance2_graph(
    geometry: OrthogonalGeometry,
    *,
    bridge_weight: int = BRIDGE_WEIGHT,
) -> Distance2GeometryGraph:
    """Build the frozen D1 weighted occupied-cell graph."""

    current = _require_geometry(geometry)
    current_bridge_weight = _require_bridge_weight(
        bridge_weight
    )

    cells = tuple(sorted(current.cells))
    occupied = set(cells)

    edges: list[WeightedEdge] = []
    local_edges: list[WeightedEdge] = []

    for left_index, left_cell in enumerate(cells):
        x1, y1 = left_cell

        for right_index in range(
            left_index + 1,
            len(cells),
        ):
            x2, y2 = cells[right_index]

            dx = abs(x1 - x2)
            dy = abs(y1 - y2)

            if not (
                (x1 == x2 and y1 != y2)
                or (y1 == y2 and x1 != x2)
            ):
                continue

            distance = dx + dy

            if distance == 1:
                edge = WeightedEdge(
                    left=left_index,
                    right=right_index,
                    weight=LOCAL_WEIGHT,
                    kind="local",
                )
                edges.append(edge)
                local_edges.append(edge)
                continue

            if distance != 2:
                continue

            midpoint = (
                (x1 + x2) // 2,
                (y1 + y2) // 2,
            )

            if midpoint in occupied:
                continue

            edges.append(
                WeightedEdge(
                    left=left_index,
                    right=right_index,
                    weight=current_bridge_weight,
                    kind="bridge",
                )
            )

    frozen_edges = tuple(edges)

    adjacency_lists: list[list[tuple[int, int]]] = [
        []
        for _cell in cells
    ]

    for edge in frozen_edges:
        adjacency_lists[edge.left].append(
            (edge.right, edge.weight)
        )
        adjacency_lists[edge.right].append(
            (edge.left, edge.weight)
        )

    adjacency = tuple(
        tuple(sorted(neighbors))
        for neighbors in adjacency_lists
    )

    return Distance2GeometryGraph(
        cells=cells,
        edges=frozen_edges,
        adjacency=adjacency,
        original_components=_original_components(
            len(cells),
            tuple(local_edges),
        ),
    )


def edge_manifest(
    graph: Distance2GeometryGraph,
) -> tuple[
    tuple[Cell, Cell, int, str],
    ...,
]:
    return tuple(
        (
            graph.cells[edge.left],
            graph.cells[edge.right],
            edge.weight,
            edge.kind,
        )
        for edge in graph.edges
    )


def maximum_weighted_degree(
    graph: Distance2GeometryGraph,
) -> int:
    return max(
        (
            sum(
                weight
                for _neighbor, weight in neighbors
            )
            for neighbors in graph.adjacency
        ),
        default=0,
    )


def original_component_probe(
    graph: Distance2GeometryGraph,
) -> State:
    state = [0] * len(graph.cells)

    for component in graph.original_components:
        if component:
            state[component[0]] = 1

    return tuple(state)


def evolve_weighted_euler_numerator(
    state: State,
    graph: Distance2GeometryGraph,
    *,
    denominator: int = EULER_DENOMINATOR,
) -> State:
    if type(denominator) is not int or denominator <= 0:
        raise ValueError(
            "denominator must be a positive integer"
        )

    if len(state) != len(graph.cells):
        raise ValueError(
            "state length must equal graph vertex count"
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

    return tuple(next_state)


def coordinate_free_dynamic_signature(
    graph: Distance2GeometryGraph,
    probe: State,
    *,
    denominator: int = EULER_DENOMINATOR,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> Signature:
    if len(probe) != len(graph.cells):
        raise ValueError(
            "probe length must equal graph vertex count"
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

    state = probe
    sample_set = set(sample_steps)
    samples: list[tuple[int, ...]] = []

    for step in range(
        1,
        sample_steps[-1] + 1,
    ):
        state = evolve_weighted_euler_numerator(
            state,
            graph,
            denominator=denominator,
        )

        if step in sample_set:
            samples.append(
                tuple(sorted(state))
            )

    return tuple(samples)


__all__ = [
    "BRIDGE_WEIGHT",
    "Distance2GeometryGraph",
    "EULER_DENOMINATOR",
    "LOCAL_WEIGHT",
    "MAX_WEIGHTED_DEGREE_BOUND",
    "PROTOCOL_ID",
    "SAMPLE_STEPS",
    "WeightedEdge",
    "build_distance2_graph",
    "coordinate_free_dynamic_signature",
    "edge_manifest",
    "evolve_weighted_euler_numerator",
    "maximum_weighted_degree",
    "original_component_probe",
]
