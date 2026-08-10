"""PETRA VISION Gate 2 G2-F1 FGS-informed proximity coupling.

Immediate native FGS factors are treated as geometry-derived dynamic regions.
Their source occurrences determine exact pairwise Manhattan proximity weights.
The final reader discards factor order and coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

FGS_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_structural_geometric_factorization.py"
)

V1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)

F0_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f0.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-fgs-proximity-v0"
)

WEIGHT_LAW = "inverse-min-manhattan"

FEATURE_CHANNELS = (
    "vertices",
    "edges",
    "components",
    "isolated_vertices",
    "total_cycle_rank",
    "maximum_degree",
)

SAMPLE_STEPS = (
    1,
    2,
    4,
    8,
    16,
    32,
)


Cell: TypeAlias = tuple[int, int]
Scalar: TypeAlias = Fraction
FactorState: TypeAlias = tuple[Scalar, ...]
SystemState: TypeAlias = tuple[FactorState, ...]
Sample: TypeAlias = tuple[FactorState, ...]
ProximitySignature: TypeAlias = tuple[Sample, ...]


@dataclass(frozen=True)
class FactorProximityGraph:
    factors: tuple[OrthogonalGeometry, ...]
    occurrences: tuple[tuple[Cell, ...], ...]
    distances: tuple[tuple[int, ...], ...]
    weights: tuple[tuple[Fraction, ...], ...]
    initial_state: SystemState


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

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


fgs = _load_module(
    FGS_TOOL_PATH,
    "_petra_vision_gate2_f1_native_fgs",
)

v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate2_f1_graph_laplacian_v1",
)

f0 = _load_module(
    F0_TOOL_PATH,
    "_petra_vision_gate2_f1_frozen_f0",
)


if v1.PROTOCOL_ID != "petra-vision-graph-laplacian-v1":
    raise RuntimeError(
        "G2-F1 requires frozen graph-Laplacian v1"
    )

if (
    f0.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-fgs-null-v0"
):
    raise RuntimeError(
        "G2-F1 requires frozen G2-F0"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G2-F1 expects an exact OrthogonalGeometry"
        )

    return geometry


def _geometry_extent(
    geometry: OrthogonalGeometry,
) -> tuple[int, int]:
    if not geometry.cells:
        raise ValueError(
            "factor geometry must not be empty"
        )

    width = max(
        x
        for x, _y in geometry.cells
    ) + 1

    height = max(
        y
        for _x, y in geometry.cells
    ) + 1

    return width, height


def _factor_feature_vector(
    factor: OrthogonalGeometry,
) -> FactorState:
    graph = v1.build_geometry_graph(factor)
    profile = v1.graph_profile(graph)

    values = (
        profile["vertices"],
        profile["edges"],
        profile["components"],
        profile["isolated_vertices"],
        sum(profile["component_cycle_ranks"]),
        profile["maximum_degree"],
    )

    return tuple(
        Fraction(value, 1)
        for value in values
    )


def _reconstruct_occurrences(
    geometry: OrthogonalGeometry,
    factors: tuple[OrthogonalGeometry, ...],
) -> tuple[tuple[Cell, ...], ...]:
    if fgs.recompose_fgs(factors) != geometry:
        raise RuntimeError(
            "native FGS factors do not exactly recompose source geometry"
        )

    if not factors:
        return ()

    extents = tuple(
        _geometry_extent(factor)
        for factor in factors
    )

    root_height = max(
        height
        for _width, height in extents
    ) + 4

    left_boundary = 0
    occurrences: list[tuple[Cell, ...]] = []

    for factor, (width, height) in zip(
        factors,
        extents,
    ):
        offset_x = left_boundary + 2
        offset_y = root_height - height - 2

        occurrence = tuple(sorted(
            (
                offset_x + x,
                offset_y + y,
            )
            for x, y in factor.cells
        ))

        occurrences.append(occurrence)

        left_boundary = (
            left_boundary
            + width
            + 3
        )

    return tuple(occurrences)


def _minimum_manhattan_distance(
    left: tuple[Cell, ...],
    right: tuple[Cell, ...],
) -> int:
    distance = min(
        abs(x1 - x2) + abs(y1 - y2)
        for x1, y1 in left
        for x2, y2 in right
    )

    if distance <= 0:
        raise RuntimeError(
            "distinct FGS occurrences must have positive distance"
        )

    return distance


def build_factor_proximity_graph(
    geometry: OrthogonalGeometry,
) -> FactorProximityGraph:
    current = _require_geometry(geometry)

    factors = fgs.native_fgs(current)
    occurrences = _reconstruct_occurrences(
        current,
        factors,
    )

    factor_count = len(factors)

    distances = [
        [0] * factor_count
        for _index in range(factor_count)
    ]

    weights = [
        [Fraction(0, 1)] * factor_count
        for _index in range(factor_count)
    ]

    for left in range(factor_count):
        for right in range(
            left + 1,
            factor_count,
        ):
            distance = _minimum_manhattan_distance(
                occurrences[left],
                occurrences[right],
            )

            weight = Fraction(
                1,
                distance,
            )

            distances[left][right] = distance
            distances[right][left] = distance

            weights[left][right] = weight
            weights[right][left] = weight

    initial_state = tuple(
        _factor_feature_vector(factor)
        for factor in factors
    )

    return FactorProximityGraph(
        factors=factors,
        occurrences=occurrences,
        distances=tuple(
            tuple(row)
            for row in distances
        ),
        weights=tuple(
            tuple(row)
            for row in weights
        ),
        initial_state=initial_state,
    )


def evolve_factor_state(
    graph: FactorProximityGraph,
    state: SystemState,
    *,
    coupled: bool,
) -> SystemState:
    if len(state) != len(graph.factors):
        raise ValueError(
            "state length must equal factor count"
        )

    if not state:
        return ()

    if any(
        len(factor_state) != len(FEATURE_CHANNELS)
        for factor_state in state
    ):
        raise ValueError(
            "every factor state must contain all frozen feature channels"
        )

    next_state: list[FactorState] = []

    for factor_index in range(
        len(graph.factors)
    ):
        if coupled:
            row = graph.weights[factor_index]
        else:
            row = tuple(
                Fraction(0, 1)
                for _factor in graph.factors
            )

        normalization = (
            Fraction(1, 1)
            + sum(row, Fraction(0, 1))
        )

        channels: list[Fraction] = []

        for channel in range(
            len(FEATURE_CHANNELS)
        ):
            numerator = state[
                factor_index
            ][channel]

            numerator += sum(
                (
                    row[neighbor]
                    * state[neighbor][channel]
                )
                for neighbor in range(
                    len(graph.factors)
                )
                if neighbor != factor_index
            )

            channels.append(
                numerator / normalization
            )

        next_state.append(
            tuple(channels)
        )

    return tuple(next_state)


def factor_proximity_signature(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
) -> ProximitySignature:
    graph = build_factor_proximity_graph(
        geometry
    )

    if not graph.factors:
        return ()

    state = graph.initial_state
    sample_steps = set(SAMPLE_STEPS)
    samples: list[Sample] = []

    for step in range(
        1,
        SAMPLE_STEPS[-1] + 1,
    ):
        state = evolve_factor_state(
            graph,
            state,
            coupled=coupled,
        )

        if step in sample_steps:
            samples.append(
                tuple(sorted(state))
            )

    return tuple(samples)


def ordered_factor_proximity_signature(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
) -> tuple[SystemState, ...]:
    """Return the labelled ordered trajectory for diagnostics only."""

    graph = build_factor_proximity_graph(
        geometry
    )

    if not graph.factors:
        return ()

    state = graph.initial_state
    sample_steps = set(SAMPLE_STEPS)
    samples: list[SystemState] = []

    for step in range(
        1,
        SAMPLE_STEPS[-1] + 1,
    ):
        state = evolve_factor_state(
            graph,
            state,
            coupled=coupled,
        )

        if step in sample_steps:
            samples.append(state)

    return tuple(samples)


def joint_f0_f1_signature(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
) -> tuple[object, ProximitySignature]:
    current = _require_geometry(geometry)

    return (
        f0.factor_multiset_signature(
            current
        ),
        factor_proximity_signature(
            current,
            coupled=coupled,
        ),
    )


__all__ = [
    "FEATURE_CHANNELS",
    "FactorProximityGraph",
    "PROTOCOL_ID",
    "SAMPLE_STEPS",
    "WEIGHT_LAW",
    "build_factor_proximity_graph",
    "evolve_factor_state",
    "factor_proximity_signature",
    "joint_f0_f1_signature",
    "ordered_factor_proximity_signature",
]
