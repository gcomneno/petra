"""PETRA VISION Gate 3 G3-P1 probe-ablation controls."""

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

D1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling.py"
)

PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-p1-v0"
)

SUBSTRATES = (
    "B0",
    "D1",
)

PROBE_MODES = (
    "minimum",
    "reflected-minimum",
    "local-degree",
    "constant",
    "zero",
)

TRANSLATION_VECTOR = (
    17,
    11,
)

State: TypeAlias = tuple[int, ...]
Signature: TypeAlias = tuple[object, ...]


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


v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate3_p1_v1",
)

d1 = _load_module(
    D1_TOOL_PATH,
    "_petra_vision_gate3_p1_d1",
)


if (
    v1.PROTOCOL_ID
    != "petra-vision-graph-laplacian-v1"
):
    raise RuntimeError(
        "G3-P1 requires frozen graph-Laplacian v1"
    )

if (
    d1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-distance2-v0"
):
    raise RuntimeError(
        "G3-P1 requires frozen Gate 2 D1"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G3-P1 expects an exact OrthogonalGeometry"
        )

    if not geometry.cells:
        raise ValueError(
            "G3-P1 requires non-empty geometry"
        )

    return geometry


def _require_substrate(
    substrate: str,
) -> str:
    if substrate not in SUBSTRATES:
        raise ValueError(
            f"unsupported G3-P1 substrate: {substrate}"
        )

    return substrate


def _require_probe_mode(
    mode: str,
) -> str:
    if mode not in PROBE_MODES:
        raise ValueError(
            f"unsupported G3-P1 probe mode: {mode}"
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
    xmin = min(
        x
        for x, _y in geometry.cells
    )

    xmax = max(
        x
        for x, _y in geometry.cells
    )

    x, y = cell

    return (
        xmin + xmax - x,
        y,
    )


def _cells_and_components(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, ...], ...],
]:
    current_substrate = _require_substrate(
        substrate
    )

    current = _require_geometry(
        geometry
    )

    if current_substrate == "B0":
        graph = v1.build_geometry_graph(
            current
        )

        return (
            graph.cells,
            graph.components,
        )

    graph = d1.build_distance2_graph(
        current,
        bridge_weight=0,
    )

    return (
        graph.cells,
        graph.original_components,
    )


def minimum_probe(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> State:
    cells, components = (
        _cells_and_components(
            substrate,
            geometry,
        )
    )

    state = [
        0
        for _cell in cells
    ]

    for component in components:
        if component:
            state[component[0]] = 1

    return tuple(
        state
    )


def reflected_minimum_probe(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> State:
    current = _require_geometry(
        geometry
    )

    original_cells, _components = (
        _cells_and_components(
            substrate,
            current,
        )
    )

    reflected = horizontal_reflection(
        current
    )

    reflected_cells, _reflected_components = (
        _cells_and_components(
            substrate,
            reflected,
        )
    )

    reflected_probe = minimum_probe(
        substrate,
        reflected,
    )

    reflected_index = {
        cell: index
        for index, cell in enumerate(
            reflected_cells
        )
    }

    transported = []

    for cell in original_cells:
        reflected_cell = _reflection_cell(
            current,
            cell,
        )

        transported.append(
            reflected_probe[
                reflected_index[
                    reflected_cell
                ]
            ]
        )

    return tuple(
        transported
    )


def local_degree_probe(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> State:
    _require_substrate(
        substrate
    )

    current = _require_geometry(
        geometry
    )

    local_graph = v1.build_geometry_graph(
        current
    )

    substrate_cells, _components = (
        _cells_and_components(
            substrate,
            current,
        )
    )

    if local_graph.cells != substrate_cells:
        raise RuntimeError(
            "native local graph and substrate vertex order differ"
        )

    return tuple(
        len(neighbors)
        for neighbors in local_graph.adjacency
    )


def constant_probe(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> State:
    cells, _components = (
        _cells_and_components(
            substrate,
            geometry,
        )
    )

    return tuple(
        1
        for _cell in cells
    )


def zero_probe(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> State:
    cells, _components = (
        _cells_and_components(
            substrate,
            geometry,
        )
    )

    return tuple(
        0
        for _cell in cells
    )


def probe_state(
    substrate: str,
    geometry: OrthogonalGeometry,
    mode: str,
) -> State:
    current_mode = _require_probe_mode(
        mode
    )

    constructors = {
        "minimum": minimum_probe,
        "reflected-minimum": reflected_minimum_probe,
        "local-degree": local_degree_probe,
        "constant": constant_probe,
        "zero": zero_probe,
    }

    return constructors[
        current_mode
    ](
        substrate,
        geometry,
    )


def probe_mass(
    probe: State,
) -> int:
    if (
        type(probe) is not tuple
        or any(
            type(value) is not int
            for value in probe
        )
    ):
        raise TypeError(
            "probe must be an exact integer tuple"
        )

    return sum(
        probe
    )


def step_zero_signature(
    probe: State,
) -> tuple[int, ...]:
    if (
        type(probe) is not tuple
        or any(
            type(value) is not int
            for value in probe
        )
    ):
        raise TypeError(
            "probe must be an exact integer tuple"
        )

    return tuple(sorted(
        probe
    ))


def b0_dynamic_signature_from_probe(
    geometry: OrthogonalGeometry,
    probe: State,
) -> Signature:
    current = _require_geometry(
        geometry
    )

    graph = v1.build_geometry_graph(
        current
    )

    if len(probe) != len(graph.cells):
        raise ValueError(
            "probe length must equal B0 vertex count"
        )

    signatures = (
        v1.dynamic_signatures_from_probe(
            graph,
            probe,
            denominator=v1.EULER_DENOMINATOR,
            sample_steps=tuple(
                v1.SAMPLE_STEPS
            ),
        )
    )

    return signatures[
        "global_multiset"
    ]


def d1_dynamic_signature_from_probe(
    geometry: OrthogonalGeometry,
    probe: State,
    *,
    coupled: bool,
) -> Signature:
    current = _require_geometry(
        geometry
    )

    if type(coupled) is not bool:
        raise TypeError(
            "coupled must be an exact bool"
        )

    graph = d1.build_distance2_graph(
        current,
        bridge_weight=(
            d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )

    if len(probe) != len(graph.cells):
        raise ValueError(
            "probe length must equal D1 vertex count"
        )

    return d1.coordinate_free_dynamic_signature(
        graph,
        probe,
        denominator=d1.EULER_DENOMINATOR,
        sample_steps=tuple(
            d1.SAMPLE_STEPS
        ),
    )


def dynamic_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
    mode: str,
    *,
    coupled: bool | None = None,
) -> Signature:
    current_substrate = (
        _require_substrate(
            substrate
        )
    )

    probe = probe_state(
        current_substrate,
        geometry,
        mode,
    )

    if current_substrate == "B0":
        if coupled is not None:
            raise ValueError(
                "B0 does not accept a coupled flag"
            )

        return b0_dynamic_signature_from_probe(
            geometry,
            probe,
        )

    if type(coupled) is not bool:
        raise TypeError(
            "D1 requires an exact coupled bool"
        )

    return d1_dynamic_signature_from_probe(
        geometry,
        probe,
        coupled=coupled,
    )


__all__ = [
    "PROBE_MODES",
    "PROTOCOL_ID",
    "SUBSTRATES",
    "TRANSLATION_VECTOR",
    "b0_dynamic_signature_from_probe",
    "constant_probe",
    "d1",
    "d1_dynamic_signature_from_probe",
    "dynamic_signature",
    "horizontal_reflection",
    "local_degree_probe",
    "minimum_probe",
    "probe_mass",
    "probe_state",
    "reflected_minimum_probe",
    "step_zero_signature",
    "translate_geometry",
    "v1",
    "zero_probe",
]
