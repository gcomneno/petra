"""Frozen G3-O1 orientation-control engine.

Oriented observations are diagnostics only. They are never evidence for
coordinate-free recovery.
"""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from itertools import permutations
from pathlib import Path
import sys
from typing import Any, Sequence


PROTOCOL_ID = "petra-vision-explicit-spectral-controls-o1-v0"

CHANNELS = (
    "B0",
    "D1-null",
    "D1-coupled",
    "F1-null",
    "F1-coupled",
    "L1-null",
    "L1-coupled",
)

OBSERVATIONS = (
    "coordinate-free-step0",
    "oriented-step0",
    "coordinate-free-dynamic",
    "oriented-dynamic",
)

SAMPLE_STEPS = (1, 2, 4, 8, 16, 32)
TRANSLATION_VECTOR = (17, 11)

_ROOT = Path(__file__).resolve().parent


def _load_module(name: str, filename: str):
    path = _ROOT / filename
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load frozen module: {filename}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b0 = _load_module(
    "_petra_gate3_o1_b0",
    "petra_vision_graph_laplacian.py",
)
d1 = _load_module(
    "_petra_gate3_o1_d1",
    "petra_vision_global_geometric_coupling.py",
)
f1 = _load_module(
    "_petra_gate3_o1_f1",
    "petra_vision_global_geometric_coupling_f1.py",
)
l1 = _load_module(
    "_petra_gate3_o1_l1",
    "petra_vision_global_geometric_coupling_l1.py",
)

OrthogonalGeometry = b0.OrthogonalGeometry


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError("G3-O1 expects an exact OrthogonalGeometry")

    if not geometry.cells:
        raise ValueError("G3-O1 requires non-empty geometry")

    return geometry


def _require_channel(channel: str) -> str:
    if type(channel) is not str or channel not in CHANNELS:
        raise ValueError(f"unsupported G3-O1 channel: {channel!r}")

    return channel


def _channel_family(channel: str) -> str:
    current = _require_channel(channel)

    if current == "B0":
        return "B0"

    return current.split("-", 1)[0]


def _channel_coupled(channel: str) -> bool | None:
    current = _require_channel(channel)

    if current == "B0":
        return None

    suffix = current.split("-", 1)[1]

    if suffix == "null":
        return False

    if suffix == "coupled":
        return True

    raise RuntimeError("unreachable channel suffix")


def translate_geometry(
    geometry: OrthogonalGeometry,
    dx: int = TRANSLATION_VECTOR[0],
    dy: int = TRANSLATION_VECTOR[1],
) -> OrthogonalGeometry:
    current = _require_geometry(geometry)

    if type(dx) is not int or type(dy) is not int:
        raise TypeError("translation offsets must be exact integers")

    return OrthogonalGeometry(
        cells=tuple(sorted(
            (x + dx, y + dy)
            for x, y in current.cells
        ))
    )


def horizontal_reflection(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    current = _require_geometry(geometry)

    xmin = min(x for x, _y in current.cells)
    xmax = max(x for x, _y in current.cells)

    return OrthogonalGeometry(
        cells=tuple(sorted(
            (xmin + xmax - x, y)
            for x, y in current.cells
        ))
    )


def canonical_origin_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    current = _require_geometry(geometry)

    xmin = min(x for x, _y in current.cells)
    ymin = min(y for _x, y in current.cells)

    return OrthogonalGeometry(
        cells=tuple(sorted(
            (x - xmin, y - ymin)
            for x, y in current.cells
        ))
    )


def _f1_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    # Native FGS is evaluated after removing uniform translation only.
    return canonical_origin_geometry(geometry)


def _b0_graph_and_state(
    geometry: OrthogonalGeometry,
):
    graph = b0.build_geometry_graph(
        _require_geometry(geometry)
    )
    state = b0.canonical_component_probe(graph)
    return graph, state


def _d1_graph_and_state(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
):
    graph = d1.build_distance2_graph(
        _require_geometry(geometry),
        bridge_weight=(
            d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )
    state = d1.original_component_probe(graph)
    return graph, state


def _f1_graph_and_state(
    geometry: OrthogonalGeometry,
):
    graph = f1.build_factor_proximity_graph(
        _f1_geometry(geometry)
    )
    return graph, graph.initial_state


def _l1_graph_and_state(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
):
    graph = l1.build_full_lattice_graph(
        _require_geometry(geometry),
        coupled=coupled,
    )
    return graph, graph.initial_state


def native_state(
    geometry: OrthogonalGeometry,
    channel: str,
):
    family = _channel_family(channel)
    coupled = _channel_coupled(channel)

    if family == "B0":
        _graph, state = _b0_graph_and_state(geometry)
        return state

    if family == "D1":
        _graph, state = _d1_graph_and_state(
            geometry,
            coupled=bool(coupled),
        )
        return state

    if family == "F1":
        _graph, state = _f1_graph_and_state(geometry)
        return state

    if family == "L1":
        _graph, state = _l1_graph_and_state(
            geometry,
            coupled=bool(coupled),
        )
        return state

    raise RuntimeError("unreachable family")


def coordinate_free_state(state: Sequence[Any]):
    return tuple(sorted(state))


def step_zero_signatures(
    geometry: OrthogonalGeometry,
    channel: str,
) -> dict[str, object]:
    state = native_state(
        geometry,
        channel,
    )

    return {
        "oriented-step0": state,
        "coordinate-free-step0": coordinate_free_state(state),
    }


def _evolve_b0_from_state(
    geometry: OrthogonalGeometry,
    state: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    graph = b0.build_geometry_graph(
        _require_geometry(geometry)
    )

    if len(state) != len(graph.cells):
        raise ValueError("B0 state length mismatch")

    current = state
    sample_set = set(SAMPLE_STEPS)
    samples = []

    for step in range(1, SAMPLE_STEPS[-1] + 1):
        current = b0.evolve_euler_numerator(
            current,
            graph,
            denominator=b0.EULER_DENOMINATOR,
        )

        if step in sample_set:
            samples.append(current)

    return tuple(samples)


def _evolve_d1_from_state(
    geometry: OrthogonalGeometry,
    state: tuple[int, ...],
    *,
    coupled: bool,
) -> tuple[tuple[int, ...], ...]:
    graph = d1.build_distance2_graph(
        _require_geometry(geometry),
        bridge_weight=(
            d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )

    if len(state) != len(graph.cells):
        raise ValueError("D1 state length mismatch")

    current = state
    sample_set = set(SAMPLE_STEPS)
    samples = []

    for step in range(1, SAMPLE_STEPS[-1] + 1):
        current = d1.evolve_weighted_euler_numerator(
            current,
            graph,
            denominator=d1.EULER_DENOMINATOR,
        )

        if step in sample_set:
            samples.append(current)

    return tuple(samples)


def _evolve_f1_from_state(
    geometry: OrthogonalGeometry,
    state,
    *,
    coupled: bool,
):
    graph = f1.build_factor_proximity_graph(
        _f1_geometry(geometry)
    )

    if len(state) != len(graph.factors):
        raise ValueError("F1 state length mismatch")

    # The frozen F1 readers define the zero-factor terminal case as
    # the empty dynamic signature itself, not as six empty snapshots.
    if not graph.factors:
        return ()

    current = state
    sample_set = set(SAMPLE_STEPS)
    samples = []

    for step in range(1, SAMPLE_STEPS[-1] + 1):
        current = f1.evolve_factor_state(
            graph,
            current,
            coupled=coupled,
        )

        if step in sample_set:
            samples.append(current)

    return tuple(samples)


def _evolve_l1_from_state(
    geometry: OrthogonalGeometry,
    state: tuple[int, ...],
    *,
    coupled: bool,
) -> tuple[tuple[int, ...], ...]:
    graph = l1.build_full_lattice_graph(
        _require_geometry(geometry),
        coupled=coupled,
    )

    if len(state) != len(graph.cells):
        raise ValueError("L1 state length mismatch")

    current = state
    sample_set = set(SAMPLE_STEPS)
    samples = []

    for step in range(1, SAMPLE_STEPS[-1] + 1):
        current = l1.evolve_lattice_numerator(
            current,
            graph,
            denominator=l1.EULER_DENOMINATOR,
        )

        if step in sample_set:
            samples.append(current)

    return tuple(samples)


def oriented_trajectory_from_state(
    geometry: OrthogonalGeometry,
    channel: str,
    state,
):
    family = _channel_family(channel)
    coupled = _channel_coupled(channel)

    if family == "B0":
        return _evolve_b0_from_state(
            geometry,
            state,
        )

    if family == "D1":
        return _evolve_d1_from_state(
            geometry,
            state,
            coupled=bool(coupled),
        )

    if family == "F1":
        return _evolve_f1_from_state(
            geometry,
            state,
            coupled=bool(coupled),
        )

    if family == "L1":
        return _evolve_l1_from_state(
            geometry,
            state,
            coupled=bool(coupled),
        )

    raise RuntimeError("unreachable family")


def oriented_dynamic_signature(
    geometry: OrthogonalGeometry,
    channel: str,
):
    state = native_state(
        geometry,
        channel,
    )

    return oriented_trajectory_from_state(
        geometry,
        channel,
        state,
    )


def coordinate_free_dynamic_signature(
    geometry: OrthogonalGeometry,
    channel: str,
):
    family = _channel_family(channel)
    coupled = _channel_coupled(channel)

    if family == "B0":
        graph, state = _b0_graph_and_state(geometry)

        return b0.dynamic_signatures_from_probe(
            graph,
            state,
            denominator=b0.EULER_DENOMINATOR,
            sample_steps=SAMPLE_STEPS,
        )["global_multiset"]

    if family == "D1":
        graph, state = _d1_graph_and_state(
            geometry,
            coupled=bool(coupled),
        )

        return d1.coordinate_free_dynamic_signature(
            graph,
            state,
            denominator=d1.EULER_DENOMINATOR,
            sample_steps=SAMPLE_STEPS,
        )

    if family == "F1":
        return f1.factor_proximity_signature(
            _f1_geometry(geometry),
            coupled=bool(coupled),
        )

    if family == "L1":
        return l1.full_lattice_signature(
            _require_geometry(geometry),
            coupled=bool(coupled),
            denominator=l1.EULER_DENOMINATOR,
            sample_steps=SAMPLE_STEPS,
        )

    raise RuntimeError("unreachable family")


def dynamic_signatures(
    geometry: OrthogonalGeometry,
    channel: str,
) -> dict[str, object]:
    oriented = oriented_dynamic_signature(
        geometry,
        channel,
    )
    coordinate_free = coordinate_free_dynamic_signature(
        geometry,
        channel,
    )

    projected = tuple(
        coordinate_free_state(sample)
        for sample in oriented
    )

    if projected != coordinate_free:
        raise RuntimeError(
            "oriented state does not project to frozen coordinate-free reader"
        )

    return {
        "oriented-dynamic": oriented,
        "coordinate-free-dynamic": coordinate_free,
    }


def observation_signatures(
    geometry: OrthogonalGeometry,
    channel: str,
) -> dict[str, object]:
    step_zero = step_zero_signatures(
        geometry,
        channel,
    )

    dynamic = dynamic_signatures(
        geometry,
        channel,
    )

    return {
        "coordinate-free-step0": step_zero[
            "coordinate-free-step0"
        ],
        "oriented-step0": step_zero[
            "oriented-step0"
        ],
        "coordinate-free-dynamic": dynamic[
            "coordinate-free-dynamic"
        ],
        "oriented-dynamic": dynamic[
            "oriented-dynamic"
        ],
    }


def _native_cells(
    geometry: OrthogonalGeometry,
    channel: str,
):
    family = _channel_family(channel)
    coupled = _channel_coupled(channel)

    if family == "B0":
        graph, _state = _b0_graph_and_state(geometry)
        return graph.cells

    if family == "D1":
        graph, _state = _d1_graph_and_state(
            geometry,
            coupled=bool(coupled),
        )
        return graph.cells

    if family == "L1":
        graph, _state = _l1_graph_and_state(
            geometry,
            coupled=bool(coupled),
        )
        return graph.cells

    raise ValueError("native cells are not defined for F1")


def _reflection_cell(
    geometry: OrthogonalGeometry,
    cell,
):
    current = _require_geometry(geometry)
    xmin = min(x for x, _y in current.cells)
    xmax = max(x for x, _y in current.cells)
    x, y = cell
    return (xmin + xmax - x, y)


def _cell_reflection_permutation(
    geometry: OrthogonalGeometry,
    channel: str,
) -> tuple[int, ...]:
    reflected = horizontal_reflection(geometry)

    source_cells = _native_cells(
        geometry,
        channel,
    )
    target_cells = _native_cells(
        reflected,
        channel,
    )

    target_index = {
        cell: index
        for index, cell in enumerate(target_cells)
    }

    permutation = tuple(
        target_index[
            _reflection_cell(
                geometry,
                cell,
            )
        ]
        for cell in source_cells
    )

    if sorted(permutation) != list(
        range(len(source_cells))
    ):
        raise RuntimeError(
            "reflection cell mapping is not bijective"
        )

    return permutation


def _canonical_cells(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[int, int], ...]:
    return canonical_origin_geometry(
        geometry
    ).cells


def _reflected_canonical_cells(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[int, int], ...]:
    return _canonical_cells(
        horizontal_reflection(
            geometry
        )
    )


def _f1_reflection_permutation(
    geometry: OrthogonalGeometry,
    channel: str,
) -> tuple[int, ...]:
    coupled = _channel_coupled(channel)

    if _channel_family(channel) != "F1":
        raise ValueError("F1 channel required")

    source_geometry = _f1_geometry(geometry)
    reflected_geometry = _f1_geometry(
        horizontal_reflection(geometry)
    )

    source = f1.build_factor_proximity_graph(
        source_geometry
    )
    target = f1.build_factor_proximity_graph(
        reflected_geometry
    )

    if len(source.factors) != len(target.factors):
        raise RuntimeError(
            "reflection changed F1 factor count"
        )

    count = len(source.factors)

    if count == 0:
        return ()

    source_shapes = tuple(
        _reflected_canonical_cells(factor)
        for factor in source.factors
    )
    target_shapes = tuple(
        _canonical_cells(factor)
        for factor in target.factors
    )

    candidates = []

    for permutation in permutations(range(count)):
        if any(
            source_shapes[left]
            != target_shapes[permutation[left]]
            for left in range(count)
        ):
            continue

        if any(
            source.initial_state[left]
            != target.initial_state[permutation[left]]
            for left in range(count)
        ):
            continue

        if any(
            source.distances[left][right]
            != target.distances[
                permutation[left]
            ][
                permutation[right]
            ]
            for left in range(count)
            for right in range(count)
        ):
            continue

        if any(
            source.weights[left][right]
            != target.weights[
                permutation[left]
            ][
                permutation[right]
            ]
            for left in range(count)
            for right in range(count)
        ):
            continue

        candidates.append(
            tuple(permutation)
        )

    if not candidates:
        raise RuntimeError(
            "no exact F1 reflection transport bijection"
        )

    # Multiple mappings can exist only through exact factor automorphisms.
    # The lexicographically first mapping is deterministic and does not tune
    # any corpus discrimination parameter.
    return min(candidates)


def reflection_permutation(
    geometry: OrthogonalGeometry,
    channel: str,
) -> tuple[int, ...]:
    family = _channel_family(channel)

    if family == "F1":
        return _f1_reflection_permutation(
            geometry,
            channel,
        )

    return _cell_reflection_permutation(
        geometry,
        channel,
    )


def transport_state(
    state: Sequence[Any],
    permutation: Sequence[int],
):
    if len(state) != len(permutation):
        raise ValueError(
            "state/permutation length mismatch"
        )

    result = [None] * len(state)

    for source, target in enumerate(
        permutation
    ):
        result[target] = state[source]

    if any(item is None for item in result):
        raise RuntimeError(
            "transport permutation is not surjective"
        )

    return tuple(result)


def transport_trajectory(
    trajectory: Sequence[Sequence[Any]],
    permutation: Sequence[int],
):
    return tuple(
        transport_state(
            state,
            permutation,
        )
        for state in trajectory
    )


def reflection_transport_audit(
    geometry: OrthogonalGeometry,
    channel: str,
) -> bool:
    reflected = horizontal_reflection(
        geometry
    )

    permutation = reflection_permutation(
        geometry,
        channel,
    )

    source_state = native_state(
        geometry,
        channel,
    )

    transported_state = transport_state(
        source_state,
        permutation,
    )

    source_trajectory = oriented_trajectory_from_state(
        geometry,
        channel,
        source_state,
    )

    reflected_trajectory = oriented_trajectory_from_state(
        reflected,
        channel,
        transported_state,
    )

    return (
        transport_trajectory(
            source_trajectory,
            permutation,
        )
        == reflected_trajectory
    )


def canonical_reflection_diagnostic(
    geometry: OrthogonalGeometry,
    channel: str,
) -> dict[str, bool]:
    reflected = horizontal_reflection(
        geometry
    )

    original = observation_signatures(
        geometry,
        channel,
    )
    mirrored = observation_signatures(
        reflected,
        channel,
    )

    return {
        observation: (
            original[observation]
            == mirrored[observation]
        )
        for observation in OBSERVATIONS
    }


def normalize_euler_trajectory(
    trajectory: Sequence[Sequence[int]],
    *,
    denominator: int,
):
    if type(denominator) is not int or denominator <= 0:
        raise ValueError(
            "denominator must be a positive integer"
        )

    if len(trajectory) != len(SAMPLE_STEPS):
        raise ValueError(
            "trajectory must use the frozen sample schedule"
        )

    return tuple(
        tuple(
            Fraction(
                value,
                denominator ** step,
            )
            for value in state
        )
        for step, state in zip(
            SAMPLE_STEPS,
            trajectory,
        )
    )


def normalized_dynamic_signature(
    geometry: OrthogonalGeometry,
    channel: str,
    *,
    oriented: bool,
):
    family = _channel_family(channel)

    if family == "F1":
        raise ValueError(
            "F1 already uses exact rational propagation"
        )

    raw = (
        oriented_dynamic_signature(
            geometry,
            channel,
        )
        if oriented
        else coordinate_free_dynamic_signature(
            geometry,
            channel,
        )
    )

    denominator = {
        "B0": b0.EULER_DENOMINATOR,
        "D1": d1.EULER_DENOMINATOR,
        "L1": l1.EULER_DENOMINATOR,
    }[family]

    return normalize_euler_trajectory(
        raw,
        denominator=denominator,
    )


__all__ = [
    "CHANNELS",
    "OBSERVATIONS",
    "OrthogonalGeometry",
    "PROTOCOL_ID",
    "SAMPLE_STEPS",
    "TRANSLATION_VECTOR",
    "canonical_origin_geometry",
    "canonical_reflection_diagnostic",
    "coordinate_free_dynamic_signature",
    "coordinate_free_state",
    "dynamic_signatures",
    "horizontal_reflection",
    "native_state",
    "normalized_dynamic_signature",
    "normalize_euler_trajectory",
    "observation_signatures",
    "oriented_dynamic_signature",
    "oriented_trajectory_from_state",
    "reflection_permutation",
    "reflection_transport_audit",
    "step_zero_signatures",
    "translate_geometry",
    "transport_state",
    "transport_trajectory",
]
