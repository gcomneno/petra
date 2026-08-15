"""Exact PETRA VISION Gate 3 G3-T1 temporal-observation controls."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

from petra.vision.geometry import (
    OrthogonalGeometry,
    normalize_geometry,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

B0_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)

D1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling.py"
)

F1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f1.py"
)

L1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_l1.py"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-t1-v0"
)

SUBSTRATES = (
    "B0",
    "D1",
    "F1",
    "L1",
)

REDUCTIONS = (
    "ordered",
    "unordered",
    "endpoints",
    "terminal",
)

SAMPLE_STEPS = (
    1,
    2,
    4,
    8,
    16,
    32,
)

TRANSLATION_VECTOR = (
    17,
    11,
)


RationalPair: TypeAlias = tuple[int, int]
ScalarSnapshot: TypeAlias = tuple[RationalPair, ...]
FactorSnapshot: TypeAlias = tuple[
    tuple[RationalPair, ...],
    ...,
]
Snapshot: TypeAlias = tuple[object, ...]
Trajectory: TypeAlias = tuple[Snapshot, ...]
RawSnapshot: TypeAlias = tuple[int, ...]
RawTrajectory: TypeAlias = tuple[RawSnapshot, ...]


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
            f"unable to load frozen research module: {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


b0 = _load_module(
    B0_TOOL_PATH,
    "_petra_vision_gate3_t1_b0",
)

d1 = _load_module(
    D1_TOOL_PATH,
    "_petra_vision_gate3_t1_d1",
)

f1 = _load_module(
    F1_TOOL_PATH,
    "_petra_vision_gate3_t1_f1",
)

l1 = _load_module(
    L1_TOOL_PATH,
    "_petra_vision_gate3_t1_l1",
)


if (
    b0.PROTOCOL_ID
    != "petra-vision-graph-laplacian-v1"
):
    raise RuntimeError(
        "G3-T1 requires frozen graph-Laplacian v1"
    )

if (
    d1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-distance2-v0"
):
    raise RuntimeError(
        "G3-T1 requires frozen Gate 2 D1"
    )

if (
    f1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-fgs-proximity-v0"
):
    raise RuntimeError(
        "G3-T1 requires frozen Gate 2 F1"
    )

if (
    l1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-full-lattice-v0"
):
    raise RuntimeError(
        "G3-T1 requires frozen Gate 2 L1"
    )

if tuple(b0.SAMPLE_STEPS) != SAMPLE_STEPS:
    raise RuntimeError(
        "B0 sample schedule differs from frozen T1 schedule"
    )

if tuple(d1.SAMPLE_STEPS) != SAMPLE_STEPS:
    raise RuntimeError(
        "D1 sample schedule differs from frozen T1 schedule"
    )

if tuple(f1.SAMPLE_STEPS) != SAMPLE_STEPS:
    raise RuntimeError(
        "F1 sample schedule differs from frozen T1 schedule"
    )

if tuple(l1.SAMPLE_STEPS) != SAMPLE_STEPS:
    raise RuntimeError(
        "L1 sample schedule differs from frozen T1 schedule"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G3-T1 expects an exact OrthogonalGeometry"
        )

    if not geometry.cells:
        raise ValueError(
            "G3-T1 requires non-empty geometry"
        )

    return geometry


def _require_substrate(
    substrate: str,
) -> str:
    if substrate not in SUBSTRATES:
        raise ValueError(
            f"unsupported G3-T1 substrate: {substrate}"
        )

    return substrate


def _require_reduction(
    reduction: str,
) -> str:
    if reduction not in REDUCTIONS:
        raise ValueError(
            f"unsupported temporal reduction: {reduction}"
        )

    return reduction


def _require_coupled(
    substrate: str,
    coupled: bool | None,
) -> bool | None:
    current = _require_substrate(
        substrate
    )

    if current == "D1":
        if type(coupled) is not bool:
            raise TypeError(
                "D1 requires an exact coupled bool"
            )

        return coupled

    if coupled is not None:
        raise ValueError(
            f"{current} does not accept a coupled flag"
        )

    return None


def _require_translation(
    translation: tuple[int, int],
) -> tuple[int, int]:
    if (
        type(translation) is not tuple
        or len(translation) != 2
        or any(
            type(value) is not int
            for value in translation
        )
    ):
        raise TypeError(
            "translation must be an exact integer pair"
        )

    return translation


def canonical_rational(
    value: int | Fraction,
) -> RationalPair:
    if type(value) is int:
        return (
            value,
            1,
        )

    if isinstance(value, Fraction):
        return (
            value.numerator,
            value.denominator,
        )

    raise TypeError(
        "T1 rational values must be exact int/Fraction scalars"
    )


def _fraction_from_pair(
    pair: RationalPair,
) -> Fraction:
    if (
        type(pair) is not tuple
        or len(pair) != 2
        or any(
            type(value) is not int
            for value in pair
        )
        or pair[1] <= 0
    ):
        raise TypeError(
            "rational pair must be an exact (numerator, denominator)"
        )

    return Fraction(
        pair[0],
        pair[1],
    )


def _canonical_scalar_snapshot(
    values: tuple[
        int | Fraction,
        ...,
    ],
) -> ScalarSnapshot:
    fractions = tuple(
        Fraction(value)
        for value in values
    )

    return tuple(
        canonical_rational(value)
        for value in sorted(
            fractions
        )
    )


def canonical_factor_snapshot(
    state: tuple[
        tuple[Fraction, ...],
        ...,
    ],
) -> FactorSnapshot:
    if type(state) is not tuple:
        raise TypeError(
            "F1 state must be an exact tuple"
        )

    rows: list[
        tuple[Fraction, ...]
    ] = []

    for factor_state in state:
        if type(factor_state) is not tuple:
            raise TypeError(
                "F1 factor state must be an exact tuple"
            )

        if any(
            not isinstance(value, Fraction)
            for value in factor_state
        ):
            raise TypeError(
                "F1 factor state must contain exact Fractions"
            )

        rows.append(
            factor_state
        )

    ordered_rows = tuple(sorted(
        rows
    ))

    return tuple(
        tuple(
            canonical_rational(value)
            for value in row
        )
        for row in ordered_rows
    )


def translate_geometry(
    geometry: OrthogonalGeometry,
    translation: tuple[int, int] = TRANSLATION_VECTOR,
) -> OrthogonalGeometry:
    current = _require_geometry(
        geometry
    )

    dx, dy = _require_translation(
        translation
    )

    return OrthogonalGeometry(
        cells=tuple(sorted(
            (
                x + dx,
                y + dy,
            )
            for x, y in current.cells
        ))
    )


def horizontal_reflection(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    current = _require_geometry(
        geometry
    )

    xmin = min(
        x
        for x, _y in current.cells
    )

    xmax = max(
        x
        for x, _y in current.cells
    )

    return OrthogonalGeometry(
        cells=tuple(sorted(
            (
                xmin + xmax - x,
                y,
            )
            for x, y in current.cells
        ))
    )


def _euler_raw_trajectory(
    initial_state: tuple[int, ...],
    evolve,
    *,
    sample_steps: tuple[int, ...],
) -> RawTrajectory:
    state = initial_state
    sample_set = set(
        sample_steps
    )
    samples: list[
        RawSnapshot
    ] = []

    for step in range(
        1,
        sample_steps[-1] + 1,
    ):
        state = evolve(
            state
        )

        if step in sample_set:
            samples.append(
                tuple(sorted(
                    state
                ))
            )

    return tuple(
        samples
    )


def _normalize_raw_trajectory(
    trajectory: RawTrajectory,
    *,
    denominator: int,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> Trajectory:
    if (
        type(denominator) is not int
        or denominator <= 0
    ):
        raise ValueError(
            "denominator must be a positive integer"
        )

    if len(trajectory) != len(
        sample_steps
    ):
        raise ValueError(
            "trajectory/sample schedule length mismatch"
        )

    snapshots: list[
        ScalarSnapshot
    ] = []

    for step, snapshot in zip(
        sample_steps,
        trajectory,
    ):
        scale = denominator ** step

        values = tuple(
            Fraction(
                value,
                scale,
            )
            for value in snapshot
        )

        snapshots.append(
            _canonical_scalar_snapshot(
                values
            )
        )

    return tuple(
        snapshots
    )


def raw_numerator_trajectory(
    substrate: str,
    geometry: OrthogonalGeometry,
    *,
    coupled: bool | None = None,
) -> RawTrajectory:
    current_substrate = _require_substrate(
        substrate
    )

    current = _require_geometry(
        geometry
    )

    current_coupled = _require_coupled(
        current_substrate,
        coupled,
    )

    if current_substrate == "F1":
        raise ValueError(
            "F1 has no Euler numerator audit trajectory"
        )

    if current_substrate == "B0":
        graph = b0.build_geometry_graph(
            current
        )

        initial_state = b0.canonical_component_probe(
            graph
        )

        return _euler_raw_trajectory(
            initial_state,
            lambda state: b0.evolve_euler_numerator(
                state,
                graph,
                denominator=b0.EULER_DENOMINATOR,
            ),
            sample_steps=SAMPLE_STEPS,
        )

    if current_substrate == "D1":
        graph = d1.build_distance2_graph(
            current,
            bridge_weight=(
                d1.BRIDGE_WEIGHT
                if current_coupled
                else 0
            ),
        )

        initial_state = d1.original_component_probe(
            graph
        )

        return _euler_raw_trajectory(
            initial_state,
            lambda state: d1.evolve_weighted_euler_numerator(
                state,
                graph,
                denominator=d1.EULER_DENOMINATOR,
            ),
            sample_steps=SAMPLE_STEPS,
        )

    graph = l1.build_full_lattice_graph(
        current,
        coupled=True,
    )

    return _euler_raw_trajectory(
        graph.initial_state,
        lambda state: l1.evolve_lattice_numerator(
            state,
            graph,
            denominator=l1.EULER_DENOMINATOR,
        ),
        sample_steps=SAMPLE_STEPS,
    )


def _f1_trajectory(
    geometry: OrthogonalGeometry,
) -> Trajectory:
    canonical_geometry = normalize_geometry(
        geometry
    )

    graph = f1.build_factor_proximity_graph(
        canonical_geometry
    )

    state = graph.initial_state
    sample_set = set(
        SAMPLE_STEPS
    )

    snapshots: list[
        FactorSnapshot
    ] = []

    for step in range(
        1,
        SAMPLE_STEPS[-1] + 1,
    ):
        state = f1.evolve_factor_state(
            graph,
            state,
            coupled=True,
        )

        if step in sample_set:
            snapshots.append(
                canonical_factor_snapshot(
                    state
                )
            )

    return tuple(
        snapshots
    )


def normalized_trajectory(
    substrate: str,
    geometry: OrthogonalGeometry,
    *,
    coupled: bool | None = None,
) -> Trajectory:
    current_substrate = _require_substrate(
        substrate
    )

    current = _require_geometry(
        geometry
    )

    _require_coupled(
        current_substrate,
        coupled,
    )

    if current_substrate == "F1":
        return _f1_trajectory(
            current
        )

    raw = raw_numerator_trajectory(
        current_substrate,
        current,
        coupled=coupled,
    )

    denominator = {
        "B0": b0.EULER_DENOMINATOR,
        "D1": d1.EULER_DENOMINATOR,
        "L1": l1.EULER_DENOMINATOR,
    }[
        current_substrate
    ]

    return _normalize_raw_trajectory(
        raw,
        denominator=denominator,
        sample_steps=SAMPLE_STEPS,
    )


def step_zero_snapshot(
    substrate: str,
    geometry: OrthogonalGeometry,
    *,
    coupled: bool | None = None,
    normalized: bool = True,
) -> Snapshot:
    current_substrate = _require_substrate(
        substrate
    )

    current = _require_geometry(
        geometry
    )

    current_coupled = _require_coupled(
        current_substrate,
        coupled,
    )

    if type(normalized) is not bool:
        raise TypeError(
            "normalized must be an exact bool"
        )

    if current_substrate == "F1":
        if not normalized:
            raise ValueError(
                "F1 has no raw numerator step-zero channel"
            )

        canonical_geometry = normalize_geometry(
            current
        )

        graph = f1.build_factor_proximity_graph(
            canonical_geometry
        )

        return canonical_factor_snapshot(
            graph.initial_state
        )

    if current_substrate == "B0":
        graph = b0.build_geometry_graph(
            current
        )

        state = b0.canonical_component_probe(
            graph
        )

    elif current_substrate == "D1":
        graph = d1.build_distance2_graph(
            current,
            bridge_weight=(
                d1.BRIDGE_WEIGHT
                if current_coupled
                else 0
            ),
        )

        state = d1.original_component_probe(
            graph
        )

    else:
        graph = l1.build_full_lattice_graph(
            current,
            coupled=True,
        )

        state = graph.initial_state

    ordered = tuple(sorted(
        state
    ))

    if not normalized:
        return ordered

    return _canonical_scalar_snapshot(
        tuple(
            Fraction(value, 1)
            for value in ordered
        )
    )


def _require_primary_trajectory(
    trajectory: tuple[object, ...],
) -> tuple[Snapshot, ...]:
    if type(trajectory) is not tuple:
        raise TypeError(
            "trajectory must be an exact tuple"
        )

    if len(trajectory) != len(
        SAMPLE_STEPS
    ):
        raise ValueError(
            "primary T1 trajectory must contain exactly six snapshots"
        )

    for snapshot in trajectory:
        if type(snapshot) is not tuple:
            raise TypeError(
                "every T1 snapshot must be an exact tuple"
            )

    return trajectory


def temporal_reduction(
    trajectory: tuple[object, ...],
    reduction: str,
) -> object:
    current = _require_primary_trajectory(
        trajectory
    )

    mode = _require_reduction(
        reduction
    )

    if mode == "ordered":
        return current

    if mode == "unordered":
        return tuple(sorted(
            current
        ))

    if mode == "endpoints":
        return (
            current[0],
            current[-1],
        )

    return current[-1]


def normalized_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
    reduction: str,
    *,
    coupled: bool | None = None,
) -> object:
    trajectory = normalized_trajectory(
        substrate,
        geometry,
        coupled=coupled,
    )

    return temporal_reduction(
        trajectory,
        reduction,
    )


def raw_numerator_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
    reduction: str,
    *,
    coupled: bool | None = None,
) -> object:
    trajectory = raw_numerator_trajectory(
        substrate,
        geometry,
        coupled=coupled,
    )

    return temporal_reduction(
        trajectory,
        reduction,
    )


def ordered_prefixes(
    trajectory: tuple[object, ...],
) -> tuple[
    tuple[Snapshot, ...],
    ...,
]:
    current = _require_primary_trajectory(
        trajectory
    )

    return tuple(
        current[:length]
        for length in range(
            1,
            len(current) + 1,
        )
    )


def unordered_prefixes(
    trajectory: tuple[object, ...],
) -> tuple[
    tuple[Snapshot, ...],
    ...,
]:
    current = _require_primary_trajectory(
        trajectory
    )

    return tuple(
        tuple(sorted(
            current[:length]
        ))
        for length in range(
            1,
            len(current) + 1,
        )
    )


def _require_sample_steps(
    sample_steps: tuple[int, ...],
) -> tuple[int, ...]:
    if (
        type(sample_steps) is not tuple
        or not sample_steps
        or any(
            type(step) is not int
            for step in sample_steps
        )
        or tuple(sorted(set(sample_steps)))
        != sample_steps
        or sample_steps[0] <= 0
    ):
        raise ValueError(
            "sample_steps must be strictly increasing positive integers"
        )

    return sample_steps


def first_divergence_time(
    left_trajectory: tuple[object, ...],
    right_trajectory: tuple[object, ...],
    *,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> int | None:
    left = _require_primary_trajectory(
        left_trajectory
    )

    right = _require_primary_trajectory(
        right_trajectory
    )

    steps = _require_sample_steps(
        sample_steps
    )

    if len(steps) != len(left):
        raise ValueError(
            "sample_steps must match trajectory length"
        )

    for step, left_snapshot, right_snapshot in zip(
        steps,
        left,
        right,
    ):
        if left_snapshot != right_snapshot:
            return step

    return None


def persistence_pattern(
    left_trajectory: tuple[object, ...],
    right_trajectory: tuple[object, ...],
) -> tuple[
    str,
    tuple[bool, ...],
]:
    left = _require_primary_trajectory(
        left_trajectory
    )

    right = _require_primary_trajectory(
        right_trajectory
    )

    pattern = tuple(
        left_snapshot != right_snapshot
        for left_snapshot, right_snapshot in zip(
            left,
            right,
        )
    )

    if not any(pattern):
        return (
            "never-diverges",
            pattern,
        )

    first_difference = pattern.index(
        True
    )

    if all(
        pattern[first_difference:]
    ):
        return (
            "diverges-and-remains-different",
            pattern,
        )

    first_collision_after_difference = next(
        index
        for index in range(
            first_difference + 1,
            len(pattern),
        )
        if not pattern[index]
    )

    if not any(
        pattern[
            first_collision_after_difference + 1:
        ]
    ):
        return (
            "diverges-then-collides-again",
            pattern,
        )

    return (
        "multiple-difference-collision-transitions",
        pattern,
    )


__all__ = [
    "PROTOCOL_ID",
    "REDUCTIONS",
    "SAMPLE_STEPS",
    "SUBSTRATES",
    "TRANSLATION_VECTOR",
    "canonical_factor_snapshot",
    "canonical_rational",
    "first_divergence_time",
    "horizontal_reflection",
    "normalized_signature",
    "normalized_trajectory",
    "ordered_prefixes",
    "persistence_pattern",
    "raw_numerator_signature",
    "raw_numerator_trajectory",
    "step_zero_snapshot",
    "temporal_reduction",
    "translate_geometry",
    "unordered_prefixes",
]
