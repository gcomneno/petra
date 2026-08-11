"""PETRA VISION Gate 3 G3-I1 impulse-response attribution controls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


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

PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-i1-v0"
)

SUBSTRATES = (
    "B0",
    "D1",
)

OBSERVATION_MODES = (
    "minimum",
    "reflected-minimum",
    "all-vertices",
)

TRANSLATION_VECTOR = (
    17,
    11,
)

State: TypeAlias = tuple[int, ...]
ElementaryResponse: TypeAlias = tuple[
    tuple[int, ...],
    ...,
]
ImpulseFamilyResponse: TypeAlias = tuple[
    ElementaryResponse,
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
    "_petra_vision_gate3_i1_b0",
)

d1 = _load_module(
    D1_TOOL_PATH,
    "_petra_vision_gate3_i1_d1",
)


if (
    b0.PROTOCOL_ID
    != "petra-vision-graph-laplacian-v1"
):
    raise RuntimeError(
        "G3-I1 requires frozen graph-Laplacian v1"
    )

if (
    d1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-distance2-v0"
):
    raise RuntimeError(
        "G3-I1 requires frozen Gate 2 D1"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G3-I1 expects an exact OrthogonalGeometry"
        )

    if not geometry.cells:
        raise ValueError(
            "G3-I1 requires non-empty geometry"
        )

    return geometry


def _require_substrate(
    substrate: str,
) -> str:
    if substrate not in SUBSTRATES:
        raise ValueError(
            f"unsupported G3-I1 substrate: {substrate}"
        )

    return substrate


def _require_mode(
    mode: str,
) -> str:
    if mode not in OBSERVATION_MODES:
        raise ValueError(
            f"unsupported G3-I1 observation mode: {mode}"
        )

    return mode


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


def _require_coupled(
    coupled: bool,
) -> bool:
    if type(coupled) is not bool:
        raise TypeError(
            "coupled must be an exact bool"
        )

    return coupled


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


def _reflection_cell(
    geometry: OrthogonalGeometry,
    cell: tuple[int, int],
) -> tuple[int, int]:
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

    x, y = cell

    return (
        xmin + xmax - x,
        y,
    )


def _substrate_cells(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> tuple[tuple[int, int], ...]:
    current_substrate = _require_substrate(
        substrate
    )

    current = _require_geometry(
        geometry
    )

    if current_substrate == "B0":
        return b0.build_geometry_graph(
            current
        ).cells

    return d1.build_distance2_graph(
        current,
        bridge_weight=0,
    ).cells


def unit_impulse(
    vertex_count: int,
    source_index: int,
) -> State:
    if (
        type(vertex_count) is not int
        or vertex_count <= 0
    ):
        raise ValueError(
            "vertex_count must be a positive integer"
        )

    if (
        type(source_index) is not int
        or source_index < 0
        or source_index >= vertex_count
    ):
        raise ValueError(
            "source_index must identify one vertex"
        )

    return tuple(
        1 if index == source_index else 0
        for index in range(
            vertex_count
        )
    )


def impulse_mass(
    impulse: State,
) -> int:
    if (
        type(impulse) is not tuple
        or not impulse
        or any(
            type(value) is not int
            for value in impulse
        )
    ):
        raise TypeError(
            "impulse must be a non-empty exact integer tuple"
        )

    return sum(
        impulse
    )


def elementary_impulse_family(
    vertex_count: int,
) -> tuple[State, ...]:
    if (
        type(vertex_count) is not int
        or vertex_count <= 0
    ):
        raise ValueError(
            "vertex_count must be a positive integer"
        )

    return tuple(
        unit_impulse(
            vertex_count,
            source_index,
        )
        for source_index in range(
            vertex_count
        )
    )


def selected_source_index(
    substrate: str,
    geometry: OrthogonalGeometry,
    mode: str,
) -> int:
    current_mode = _require_mode(
        mode
    )

    if current_mode == "all-vertices":
        raise ValueError(
            "all-vertices has no selected source"
        )

    current = _require_geometry(
        geometry
    )

    cells = _substrate_cells(
        substrate,
        current,
    )

    if current_mode == "minimum":
        return 0

    reflected = horizontal_reflection(
        current
    )

    reflected_cells = _substrate_cells(
        substrate,
        reflected,
    )

    reflected_minimum_cell = (
        reflected_cells[0]
    )

    transported_cell = _reflection_cell(
        current,
        reflected_minimum_cell,
    )

    index_by_cell = {
        cell: index
        for index, cell in enumerate(
            cells
        )
    }

    return index_by_cell[
        transported_cell
    ]


def selected_impulse(
    substrate: str,
    geometry: OrthogonalGeometry,
    mode: str,
) -> State:
    cells = _substrate_cells(
        substrate,
        geometry,
    )

    source_index = selected_source_index(
        substrate,
        geometry,
        mode,
    )

    return unit_impulse(
        len(cells),
        source_index,
    )


def step_zero_signature(
    impulse: State,
) -> tuple[int, ...]:
    if (
        type(impulse) is not tuple
        or not impulse
        or any(
            type(value) is not int
            for value in impulse
        )
    ):
        raise TypeError(
            "impulse must be a non-empty exact integer tuple"
        )

    return tuple(sorted(
        impulse
    ))


def all_vertices_step_zero_signature(
    vertex_count: int,
) -> tuple[
    tuple[int, ...],
    ...,
]:
    family = elementary_impulse_family(
        vertex_count
    )

    return tuple(sorted(
        step_zero_signature(
            impulse
        )
        for impulse in family
    ))


def b0_elementary_response(
    geometry: OrthogonalGeometry,
    impulse: State,
) -> ElementaryResponse:
    current = _require_geometry(
        geometry
    )

    graph = b0.build_geometry_graph(
        current
    )

    if len(impulse) != len(graph.cells):
        raise ValueError(
            "impulse length must equal B0 vertex count"
        )

    if impulse_mass(impulse) != 1:
        raise ValueError(
            "I1 elementary impulse must have mass one"
        )

    signatures = b0.dynamic_signatures_from_probe(
        graph,
        impulse,
        denominator=b0.EULER_DENOMINATOR,
        sample_steps=tuple(
            b0.SAMPLE_STEPS
        ),
    )

    return signatures[
        "global_multiset"
    ]


def d1_elementary_response(
    geometry: OrthogonalGeometry,
    impulse: State,
    *,
    coupled: bool,
) -> ElementaryResponse:
    current = _require_geometry(
        geometry
    )

    current_coupled = _require_coupled(
        coupled
    )

    graph = d1.build_distance2_graph(
        current,
        bridge_weight=(
            d1.BRIDGE_WEIGHT
            if current_coupled
            else 0
        ),
    )

    if len(impulse) != len(graph.cells):
        raise ValueError(
            "impulse length must equal D1 vertex count"
        )

    if impulse_mass(impulse) != 1:
        raise ValueError(
            "I1 elementary impulse must have mass one"
        )

    return d1.coordinate_free_dynamic_signature(
        graph,
        impulse,
        denominator=d1.EULER_DENOMINATOR,
        sample_steps=tuple(
            d1.SAMPLE_STEPS
        ),
    )


def elementary_response(
    substrate: str,
    geometry: OrthogonalGeometry,
    impulse: State,
    *,
    coupled: bool | None = None,
) -> ElementaryResponse:
    current_substrate = _require_substrate(
        substrate
    )

    if current_substrate == "B0":
        if coupled is not None:
            raise ValueError(
                "B0 does not accept a coupled flag"
            )

        return b0_elementary_response(
            geometry,
            impulse,
        )

    if type(coupled) is not bool:
        raise TypeError(
            "D1 requires an exact coupled bool"
        )

    return d1_elementary_response(
        geometry,
        impulse,
        coupled=coupled,
    )


def _batched_response_from_weighted_adjacency(
    adjacency: tuple[
        tuple[
            tuple[int, int],
            ...,
        ],
        ...,
    ],
    *,
    denominator: int,
    sample_steps: tuple[int, ...],
) -> ImpulseFamilyResponse:
    vertex_count = len(
        adjacency
    )

    if vertex_count <= 0:
        raise ValueError(
            "batched response requires vertices"
        )

    if (
        type(denominator) is not int
        or denominator <= 0
    ):
        raise ValueError(
            "denominator must be a positive integer"
        )

    if (
        not sample_steps
        or tuple(sorted(set(sample_steps)))
        != sample_steps
        or sample_steps[0] <= 0
    ):
        raise ValueError(
            "sample_steps must be strictly increasing positive integers"
        )

    rows = [
        [
            1 if vertex == source else 0
            for source in range(
                vertex_count
            )
        ]
        for vertex in range(
            vertex_count
        )
    ]

    samples_by_source: list[
        list[tuple[int, ...]]
    ] = [
        []
        for _source in range(
            vertex_count
        )
    ]

    sample_set = set(
        sample_steps
    )

    for step in range(
        1,
        sample_steps[-1] + 1,
    ):
        next_rows: list[
            list[int]
        ] = []

        for vertex, neighbors in enumerate(
            adjacency
        ):
            weighted_degree = sum(
                weight
                for _neighbor, weight in neighbors
            )

            next_row = []

            for source in range(
                vertex_count
            ):
                weighted_neighbors = sum(
                    weight
                    * rows[neighbor][source]
                    for neighbor, weight
                    in neighbors
                )

                laplacian_value = (
                    weighted_degree
                    * rows[vertex][source]
                    - weighted_neighbors
                )

                next_row.append(
                    denominator
                    * rows[vertex][source]
                    - laplacian_value
                )

            next_rows.append(
                next_row
            )

        rows = next_rows

        if step not in sample_set:
            continue

        for source in range(
            vertex_count
        ):
            samples_by_source[
                source
            ].append(
                tuple(sorted(
                    rows[vertex][source]
                    for vertex in range(
                        vertex_count
                    )
                ))
            )

    return tuple(sorted(
        tuple(samples)
        for samples in samples_by_source
    ))


def b0_all_vertices_response_independent(
    geometry: OrthogonalGeometry,
) -> ImpulseFamilyResponse:
    current = _require_geometry(
        geometry
    )

    graph = b0.build_geometry_graph(
        current
    )

    responses = (
        b0_elementary_response(
            current,
            impulse,
        )
        for impulse in elementary_impulse_family(
            len(graph.cells)
        )
    )

    return tuple(sorted(
        responses
    ))


def b0_all_vertices_response_batched(
    geometry: OrthogonalGeometry,
) -> ImpulseFamilyResponse:
    current = _require_geometry(
        geometry
    )

    graph = b0.build_geometry_graph(
        current
    )

    weighted_adjacency = tuple(
        tuple(
            (
                neighbor,
                1,
            )
            for neighbor in neighbors
        )
        for neighbors in graph.adjacency
    )

    return _batched_response_from_weighted_adjacency(
        weighted_adjacency,
        denominator=b0.EULER_DENOMINATOR,
        sample_steps=tuple(
            b0.SAMPLE_STEPS
        ),
    )


def d1_all_vertices_response_independent(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
) -> ImpulseFamilyResponse:
    current = _require_geometry(
        geometry
    )

    current_coupled = _require_coupled(
        coupled
    )

    graph = d1.build_distance2_graph(
        current,
        bridge_weight=(
            d1.BRIDGE_WEIGHT
            if current_coupled
            else 0
        ),
    )

    responses = (
        d1_elementary_response(
            current,
            impulse,
            coupled=current_coupled,
        )
        for impulse in elementary_impulse_family(
            len(graph.cells)
        )
    )

    return tuple(sorted(
        responses
    ))


def d1_all_vertices_response_batched(
    geometry: OrthogonalGeometry,
    *,
    coupled: bool,
) -> ImpulseFamilyResponse:
    current = _require_geometry(
        geometry
    )

    current_coupled = _require_coupled(
        coupled
    )

    graph = d1.build_distance2_graph(
        current,
        bridge_weight=(
            d1.BRIDGE_WEIGHT
            if current_coupled
            else 0
        ),
    )

    return _batched_response_from_weighted_adjacency(
        graph.adjacency,
        denominator=d1.EULER_DENOMINATOR,
        sample_steps=tuple(
            d1.SAMPLE_STEPS
        ),
    )


def all_vertices_response(
    substrate: str,
    geometry: OrthogonalGeometry,
    *,
    coupled: bool | None = None,
    batched: bool = True,
) -> ImpulseFamilyResponse:
    current_substrate = _require_substrate(
        substrate
    )

    if type(batched) is not bool:
        raise TypeError(
            "batched must be an exact bool"
        )

    if current_substrate == "B0":
        if coupled is not None:
            raise ValueError(
                "B0 does not accept a coupled flag"
            )

        if batched:
            return b0_all_vertices_response_batched(
                geometry
            )

        return b0_all_vertices_response_independent(
            geometry
        )

    if type(coupled) is not bool:
        raise TypeError(
            "D1 requires an exact coupled bool"
        )

    if batched:
        return d1_all_vertices_response_batched(
            geometry,
            coupled=coupled,
        )

    return d1_all_vertices_response_independent(
        geometry,
        coupled=coupled,
    )


def observation_step_zero_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
    mode: str,
) -> object:
    current_mode = _require_mode(
        mode
    )

    cells = _substrate_cells(
        substrate,
        geometry,
    )

    if current_mode == "all-vertices":
        return all_vertices_step_zero_signature(
            len(cells)
        )

    return step_zero_signature(
        selected_impulse(
            substrate,
            geometry,
            current_mode,
        )
    )


def observation_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
    mode: str,
    *,
    coupled: bool | None = None,
    batched: bool = True,
) -> object:
    current_mode = _require_mode(
        mode
    )

    if current_mode == "all-vertices":
        return all_vertices_response(
            substrate,
            geometry,
            coupled=coupled,
            batched=batched,
        )

    impulse = selected_impulse(
        substrate,
        geometry,
        current_mode,
    )

    return elementary_response(
        substrate,
        geometry,
        impulse,
        coupled=coupled,
    )


__all__ = [
    "B0_TOOL_PATH",
    "D1_TOOL_PATH",
    "OBSERVATION_MODES",
    "PROTOCOL_ID",
    "SUBSTRATES",
    "TRANSLATION_VECTOR",
    "all_vertices_response",
    "all_vertices_step_zero_signature",
    "b0",
    "b0_all_vertices_response_batched",
    "b0_all_vertices_response_independent",
    "b0_elementary_response",
    "d1",
    "d1_all_vertices_response_batched",
    "d1_all_vertices_response_independent",
    "d1_elementary_response",
    "elementary_impulse_family",
    "elementary_response",
    "horizontal_reflection",
    "impulse_mass",
    "observation_signature",
    "observation_step_zero_signature",
    "selected_impulse",
    "selected_source_index",
    "step_zero_signature",
    "translate_geometry",
    "unit_impulse",
]
