"""Gate 3 G3-P1 structural tests without corpus evaluation."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys

import pytest

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_p1.py"
)


def _load_tool():
    name = (
        "_petra_vision_gate3_p1_test_tool"
    )

    existing = sys.modules.get(
        name
    )

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        TOOL_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-P1 research tool"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(
        module
    )

    return module


p1 = _load_tool()


def _geometry() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (1, 0),
            (3, 0),
            (3, 1),
        )
    )


def _bridge_only_geometry() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (2, 0),
        )
    )


def test_protocol_and_probe_family_are_frozen():
    assert (
        p1.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-p1-v0"
    )

    assert p1.SUBSTRATES == (
        "B0",
        "D1",
    )

    assert p1.PROBE_MODES == (
        "minimum",
        "reflected-minimum",
        "local-degree",
        "constant",
        "zero",
    )

    assert p1.TRANSLATION_VECTOR == (
        17,
        11,
    )


def test_b0_minimum_reproduces_frozen_probe():
    geometry = _geometry()

    graph = p1.v1.build_geometry_graph(
        geometry
    )

    assert (
        p1.minimum_probe(
            "B0",
            geometry,
        )
        == p1.v1.canonical_component_probe(
            graph
        )
    )


def test_d1_minimum_reproduces_frozen_probe():
    geometry = _geometry()

    graph = p1.d1.build_distance2_graph(
        geometry
    )

    assert (
        p1.minimum_probe(
            "D1",
            geometry,
        )
        == p1.d1.original_component_probe(
            graph
        )
    )


def test_reflected_minimum_is_exact_transport():
    geometry = _geometry()

    reflected = p1.horizontal_reflection(
        geometry
    )

    reflected_graph = (
        p1.v1.build_geometry_graph(
            reflected
        )
    )

    reflected_minimum = (
        p1.minimum_probe(
            "B0",
            reflected,
        )
    )

    reflected_index = {
        cell: index
        for index, cell in enumerate(
            reflected_graph.cells
        )
    }

    xmin = min(
        x
        for x, _y in geometry.cells
    )

    xmax = max(
        x
        for x, _y in geometry.cells
    )

    original_graph = (
        p1.v1.build_geometry_graph(
            geometry
        )
    )

    expected = tuple(
        reflected_minimum[
            reflected_index[
                (
                    xmin + xmax - x,
                    y,
                )
            ]
        ]
        for x, y in original_graph.cells
    )

    assert (
        p1.reflected_minimum_probe(
            "B0",
            geometry,
        )
        == expected
    )


def test_local_degree_is_native_four_neighbor_degree():
    geometry = _geometry()

    graph = p1.v1.build_geometry_graph(
        geometry
    )

    expected = tuple(
        len(neighbors)
        for neighbors in graph.adjacency
    )

    assert (
        p1.local_degree_probe(
            "B0",
            geometry,
        )
        == expected
    )

    assert (
        p1.local_degree_probe(
            "D1",
            geometry,
        )
        == expected
    )


def test_d1_local_degree_contains_no_bridge_information():
    geometry = _bridge_only_geometry()

    local_graph = (
        p1.v1.build_geometry_graph(
            geometry
        )
    )

    d1_graph = (
        p1.d1.build_distance2_graph(
            geometry
        )
    )

    assert all(
        len(neighbors) == 0
        for neighbors in local_graph.adjacency
    )

    assert any(
        edge.kind == "bridge"
        and edge.weight
        == p1.d1.BRIDGE_WEIGHT
        for edge in d1_graph.edges
    )

    assert (
        p1.local_degree_probe(
            "D1",
            geometry,
        )
        == (
            0,
            0,
        )
    )


def test_constant_and_zero_probes_are_exact():
    geometry = _geometry()

    for substrate in p1.SUBSTRATES:
        count = len(
            geometry.cells
        )

        assert (
            p1.constant_probe(
                substrate,
                geometry,
            )
            == tuple(
                1
                for _index in range(
                    count
                )
            )
        )

        assert (
            p1.zero_probe(
                substrate,
                geometry,
            )
            == tuple(
                0
                for _index in range(
                    count
                )
            )
        )


def test_step_zero_signature_removes_vertex_order():
    assert (
        p1.step_zero_signature(
            (
                2,
                0,
                1,
                0,
            )
        )
        == (
            0,
            0,
            1,
            2,
        )
    )


def test_probe_mass_is_exact_integer_sum():
    assert (
        p1.probe_mass(
            (
                2,
                0,
                1,
                0,
            )
        )
        == 3
    )


def test_b0_dynamic_path_delegates_to_frozen_core():
    geometry = _geometry()

    graph = p1.v1.build_geometry_graph(
        geometry
    )

    probe = p1.minimum_probe(
        "B0",
        geometry,
    )

    expected = (
        p1.v1.dynamic_signatures_from_probe(
            graph,
            probe,
            denominator=p1.v1.EULER_DENOMINATOR,
            sample_steps=tuple(
                p1.v1.SAMPLE_STEPS
            ),
        )[
            "global_multiset"
        ]
    )

    assert (
        p1.b0_dynamic_signature_from_probe(
            geometry,
            probe,
        )
        == expected
    )


@pytest.mark.parametrize(
    "coupled",
    (
        False,
        True,
    ),
)
def test_d1_dynamic_path_delegates_to_frozen_core(
    coupled,
):
    geometry = _geometry()

    probe = p1.minimum_probe(
        "D1",
        geometry,
    )

    graph = p1.d1.build_distance2_graph(
        geometry,
        bridge_weight=(
            p1.d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )

    expected = (
        p1.d1.coordinate_free_dynamic_signature(
            graph,
            probe,
            denominator=p1.d1.EULER_DENOMINATOR,
            sample_steps=tuple(
                p1.d1.SAMPLE_STEPS
            ),
        )
    )

    assert (
        p1.d1_dynamic_signature_from_probe(
            geometry,
            probe,
            coupled=coupled,
        )
        == expected
    )


def test_d1_null_and_coupled_use_same_declared_probe_tuple():
    geometry = _geometry()

    for mode in p1.PROBE_MODES:
        first = p1.probe_state(
            "D1",
            geometry,
            mode,
        )

        second = p1.probe_state(
            "D1",
            geometry,
            mode,
        )

        assert first == second


@pytest.mark.parametrize(
    "substrate,coupled",
    (
        ("B0", None),
        ("D1", False),
        ("D1", True),
    ),
)
def test_all_probe_modes_are_translation_invariant(
    substrate,
    coupled,
):
    geometry = _geometry()

    translated = p1.translate_geometry(
        geometry
    )

    for mode in p1.PROBE_MODES:
        original_probe = (
            p1.probe_state(
                substrate,
                geometry,
                mode,
            )
        )

        translated_probe = (
            p1.probe_state(
                substrate,
                translated,
                mode,
            )
        )

        assert (
            original_probe
            == translated_probe
        )

        original_zero = (
            p1.step_zero_signature(
                original_probe
            )
        )

        translated_zero = (
            p1.step_zero_signature(
                translated_probe
            )
        )

        assert (
            original_zero
            == translated_zero
        )

        kwargs = {}

        if substrate == "D1":
            kwargs["coupled"] = coupled

        original_dynamic = (
            p1.dynamic_signature(
                substrate,
                geometry,
                mode,
                **kwargs,
            )
        )

        translated_dynamic = (
            p1.dynamic_signature(
                substrate,
                translated,
                mode,
                **kwargs,
            )
        )

        assert (
            original_dynamic
            == translated_dynamic
        )


@pytest.mark.parametrize(
    "substrate,coupled",
    (
        ("B0", None),
        ("D1", False),
        ("D1", True),
    ),
)
def test_reflection_transport_identities(
    substrate,
    coupled,
):
    geometry = _geometry()

    reflected = p1.horizontal_reflection(
        geometry
    )

    kwargs = {}

    if substrate == "D1":
        kwargs["coupled"] = coupled

    assert (
        p1.dynamic_signature(
            substrate,
            geometry,
            "minimum",
            **kwargs,
        )
        == p1.dynamic_signature(
            substrate,
            reflected,
            "reflected-minimum",
            **kwargs,
        )
    )

    assert (
        p1.dynamic_signature(
            substrate,
            geometry,
            "reflected-minimum",
            **kwargs,
        )
        == p1.dynamic_signature(
            substrate,
            reflected,
            "minimum",
            **kwargs,
        )
    )


@pytest.mark.parametrize(
    "substrate,coupled",
    (
        ("B0", None),
        ("D1", False),
        ("D1", True),
    ),
)
@pytest.mark.parametrize(
    "mode",
    (
        "local-degree",
        "constant",
        "zero",
    ),
)
def test_intrinsic_probe_signatures_are_reflection_invariant(
    substrate,
    coupled,
    mode,
):
    geometry = _geometry()

    reflected = p1.horizontal_reflection(
        geometry
    )

    kwargs = {}

    if substrate == "D1":
        kwargs["coupled"] = coupled

    assert (
        p1.step_zero_signature(
            p1.probe_state(
                substrate,
                geometry,
                mode,
            )
        )
        == p1.step_zero_signature(
            p1.probe_state(
                substrate,
                reflected,
                mode,
            )
        )
    )

    assert (
        p1.dynamic_signature(
            substrate,
            geometry,
            mode,
            **kwargs,
        )
        == p1.dynamic_signature(
            substrate,
            reflected,
            mode,
            **kwargs,
        )
    )


def test_horizontal_reflection_is_an_involution():
    geometry = _geometry()

    assert (
        p1.horizontal_reflection(
            p1.horizontal_reflection(
                geometry
            )
        )
        == geometry
    )


def test_translation_does_not_normalize_geometry():
    geometry = _geometry()

    translated = p1.translate_geometry(
        geometry
    )

    assert (
        min(
            x
            for x, _y in translated.cells
        )
        == 17
    )

    assert (
        min(
            y
            for _x, y in translated.cells
        )
        == 11
    )


def test_dynamic_signature_requires_matched_substrate_arguments():
    geometry = _geometry()

    with pytest.raises(
        ValueError
    ):
        p1.dynamic_signature(
            "B0",
            geometry,
            "minimum",
            coupled=True,
        )

    with pytest.raises(
        TypeError
    ):
        p1.dynamic_signature(
            "D1",
            geometry,
            "minimum",
        )


def test_rejects_undeclared_substrate_and_probe():
    geometry = _geometry()

    with pytest.raises(
        ValueError
    ):
        p1.probe_state(
            "F1",
            geometry,
            "minimum",
        )

    with pytest.raises(
        ValueError
    ):
        p1.probe_state(
            "B0",
            geometry,
            "invented",
        )


def test_source_boundary_contains_no_corpus_or_later_gate_reader():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    forbidden_fragments = (
        "phase_1_corpus",
        "held_out_corpus",
        "extended_corpus",
        "shape_code",
        "petra_vision_graph_laplacian_width4",
        "petra_vision_global_geometric_coupling_f1",
        "petra_vision_global_geometric_coupling_l1",
        "petra_vision_explicit_spectral_controls_s2",
        "petra_vision_explicit_spectral_controls_h1",
        "impulse_response",
        "temporal_observation",
        "orientation_control",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source

    imported_paths = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            imported_paths.append(
                ast.unparse(
                    node
                )
            )

    joined = "\n".join(
        imported_paths
    )

    assert (
        "width4"
        not in joined
    )
