"""G3-I1 structural tests without corpus observation."""

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
    / "petra_vision_explicit_spectral_controls_i1.py"
)


def _load_tool():
    name = (
        "_petra_vision_gate3_i1_test_tool"
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
            "unable to load G3-I1 research tool"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(
        module
    )

    return module


i1 = _load_tool()


def _geometry() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (1, 0),
            (3, 0),
            (3, 1),
        )
    )


def _asymmetric_connected_geometry() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (1, 0),
            (1, 1),
            (2, 1),
        )
    )


def _bridge_geometry() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (1, 0),
            (3, 0),
            (4, 0),
        )
    )


def test_protocol_family_is_frozen():
    assert (
        i1.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-i1-v0"
    )

    assert i1.SUBSTRATES == (
        "B0",
        "D1",
    )

    assert (
        i1.OBSERVATION_MODES
        == (
            "minimum",
            "reflected-minimum",
            "all-vertices",
        )
    )

    assert i1.TRANSLATION_VECTOR == (
        17,
        11,
    )


def test_frozen_core_protocols_are_exact():
    assert (
        i1.b0.PROTOCOL_ID
        == "petra-vision-graph-laplacian-v1"
    )

    assert (
        i1.d1.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-distance2-v0"
    )

    assert i1.b0.EULER_DENOMINATOR == 8
    assert i1.d1.EULER_DENOMINATOR == 16

    assert tuple(
        i1.b0.SAMPLE_STEPS
    ) == (
        1,
        2,
        4,
        8,
        16,
        32,
    )

    assert tuple(
        i1.d1.SAMPLE_STEPS
    ) == (
        1,
        2,
        4,
        8,
        16,
        32,
    )


@pytest.mark.parametrize(
    "source",
    (
        0,
        1,
        4,
    ),
)
def test_unit_impulse_is_exact_mass_one(
    source,
):
    impulse = i1.unit_impulse(
        5,
        source,
    )

    assert len(impulse) == 5
    assert impulse[source] == 1
    assert sum(impulse) == 1
    assert i1.impulse_mass(
        impulse
    ) == 1

    assert all(
        value in (
            0,
            1,
        )
        for value in impulse
    )


def test_elementary_impulse_family_is_complete_and_ordered():
    family = (
        i1.elementary_impulse_family(
            4
        )
    )

    assert len(family) == 4

    assert family == (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    )


def test_step_zero_selected_impulses_depend_only_on_order():
    assert (
        i1.step_zero_signature(
            (
                1,
                0,
                0,
                0,
            )
        )
        == (
            0,
            0,
            0,
            1,
        )
    )

    assert (
        i1.step_zero_signature(
            (
                0,
                0,
                1,
                0,
            )
        )
        == (
            0,
            0,
            0,
            1,
        )
    )


def test_all_vertices_step_zero_preserves_multiplicity():
    signature = (
        i1.all_vertices_step_zero_signature(
            3
        )
    )

    assert len(signature) == 3

    assert signature == (
        (0, 0, 1),
        (0, 0, 1),
        (0, 0, 1),
    )


@pytest.mark.parametrize(
    "substrate",
    i1.SUBSTRATES,
)
def test_minimum_selects_one_complete_geometry_vertex(
    substrate,
):
    geometry = _geometry()

    cells = (
        i1.b0.build_geometry_graph(
            geometry
        ).cells
    )

    assert (
        i1.selected_source_index(
            substrate,
            geometry,
            "minimum",
        )
        == 0
    )

    impulse = i1.selected_impulse(
        substrate,
        geometry,
        "minimum",
    )

    assert len(impulse) == len(
        cells
    )

    assert i1.impulse_mass(
        impulse
    ) == 1


@pytest.mark.parametrize(
    "substrate",
    i1.SUBSTRATES,
)
def test_reflected_minimum_is_true_transport(
    substrate,
):
    geometry = _geometry()

    reflected = i1.horizontal_reflection(
        geometry
    )

    original_cells = (
        i1._substrate_cells(
            substrate,
            geometry,
        )
    )

    reflected_cells = (
        i1._substrate_cells(
            substrate,
            reflected,
        )
    )

    reflected_minimum = (
        reflected_cells[0]
    )

    expected_cell = (
        i1._reflection_cell(
            geometry,
            reflected_minimum,
        )
    )

    expected_index = (
        original_cells.index(
            expected_cell
        )
    )

    assert (
        i1.selected_source_index(
            substrate,
            geometry,
            "reflected-minimum",
        )
        == expected_index
    )


def test_horizontal_reflection_is_an_involution():
    geometry = _geometry()

    assert (
        i1.horizontal_reflection(
            i1.horizontal_reflection(
                geometry
            )
        )
        == geometry
    )


def test_translation_is_exact_without_normalization():
    geometry = _geometry()

    translated = i1.translate_geometry(
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


def test_b0_elementary_response_delegates_to_frozen_core():
    geometry = _geometry()

    graph = i1.b0.build_geometry_graph(
        geometry
    )

    impulse = i1.unit_impulse(
        len(graph.cells),
        1,
    )

    expected = (
        i1.b0.dynamic_signatures_from_probe(
            graph,
            impulse,
            denominator=i1.b0.EULER_DENOMINATOR,
            sample_steps=tuple(
                i1.b0.SAMPLE_STEPS
            ),
        )[
            "global_multiset"
        ]
    )

    assert (
        i1.b0_elementary_response(
            geometry,
            impulse,
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
def test_d1_elementary_response_delegates_to_frozen_core(
    coupled,
):
    geometry = _bridge_geometry()

    graph = i1.d1.build_distance2_graph(
        geometry,
        bridge_weight=(
            i1.d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )

    impulse = i1.unit_impulse(
        len(graph.cells),
        2,
    )

    expected = (
        i1.d1.coordinate_free_dynamic_signature(
            graph,
            impulse,
            denominator=i1.d1.EULER_DENOMINATOR,
            sample_steps=tuple(
                i1.d1.SAMPLE_STEPS
            ),
        )
    )

    assert (
        i1.d1_elementary_response(
            geometry,
            impulse,
            coupled=coupled,
        )
        == expected
    )


def test_b0_all_vertices_batched_equals_independent():
    geometry = (
        _asymmetric_connected_geometry()
    )

    independent = (
        i1.b0_all_vertices_response_independent(
            geometry
        )
    )

    batched = (
        i1.b0_all_vertices_response_batched(
            geometry
        )
    )

    assert batched == independent

    assert len(batched) == len(
        geometry.cells
    )


@pytest.mark.parametrize(
    "coupled",
    (
        False,
        True,
    ),
)
def test_d1_all_vertices_batched_equals_independent(
    coupled,
):
    geometry = _bridge_geometry()

    independent = (
        i1.d1_all_vertices_response_independent(
            geometry,
            coupled=coupled,
        )
    )

    batched = (
        i1.d1_all_vertices_response_batched(
            geometry,
            coupled=coupled,
        )
    )

    assert batched == independent

    assert len(batched) == len(
        geometry.cells
    )


def test_batched_path_is_not_alias_of_independent_path(
    monkeypatch,
):
    geometry = (
        _asymmetric_connected_geometry()
    )

    def fail(*_args, **_kwargs):
        raise AssertionError(
            "independent path must not run"
        )

    monkeypatch.setattr(
        i1,
        "b0_all_vertices_response_independent",
        fail,
    )

    result = (
        i1.b0_all_vertices_response_batched(
            geometry
        )
    )

    assert len(result) == len(
        geometry.cells
    )


def test_d1_null_and_coupled_use_identical_impulse_family():
    geometry = _bridge_geometry()

    null_graph = (
        i1.d1.build_distance2_graph(
            geometry,
            bridge_weight=0,
        )
    )

    coupled_graph = (
        i1.d1.build_distance2_graph(
            geometry,
            bridge_weight=i1.d1.BRIDGE_WEIGHT,
        )
    )

    assert (
        null_graph.cells
        == coupled_graph.cells
    )

    null_family = (
        i1.elementary_impulse_family(
            len(
                null_graph.cells
            )
        )
    )

    coupled_family = (
        i1.elementary_impulse_family(
            len(
                coupled_graph.cells
            )
        )
    )

    assert (
        null_family
        == coupled_family
    )

    assert all(
        i1.impulse_mass(
            impulse
        )
        == 1
        for impulse in null_family
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
        "minimum",
        "reflected-minimum",
        "all-vertices",
    ),
)
def test_every_i1_observation_is_translation_invariant(
    substrate,
    coupled,
    mode,
):
    geometry = _geometry()

    translated = i1.translate_geometry(
        geometry
    )

    kwargs = {}

    if substrate == "D1":
        kwargs[
            "coupled"
        ] = coupled

    original_zero = (
        i1.observation_step_zero_signature(
            substrate,
            geometry,
            mode,
        )
    )

    translated_zero = (
        i1.observation_step_zero_signature(
            substrate,
            translated,
            mode,
        )
    )

    assert (
        original_zero
        == translated_zero
    )

    original = (
        i1.observation_signature(
            substrate,
            geometry,
            mode,
            **kwargs,
        )
    )

    translated_signature = (
        i1.observation_signature(
            substrate,
            translated,
            mode,
            **kwargs,
        )
    )

    assert (
        original
        == translated_signature
    )


@pytest.mark.parametrize(
    "substrate,coupled",
    (
        ("B0", None),
        ("D1", False),
        ("D1", True),
    ),
)
def test_selected_impulse_reflection_transport_identity(
    substrate,
    coupled,
):
    geometry = (
        _asymmetric_connected_geometry()
    )

    reflected = (
        i1.horizontal_reflection(
            geometry
        )
    )

    kwargs = {}

    if substrate == "D1":
        kwargs[
            "coupled"
        ] = coupled

    assert (
        i1.observation_signature(
            substrate,
            geometry,
            "minimum",
            **kwargs,
        )
        == i1.observation_signature(
            substrate,
            reflected,
            "reflected-minimum",
            **kwargs,
        )
    )

    assert (
        i1.observation_signature(
            substrate,
            geometry,
            "reflected-minimum",
            **kwargs,
        )
        == i1.observation_signature(
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
def test_all_vertices_response_is_reflection_invariant(
    substrate,
    coupled,
):
    geometry = _bridge_geometry()

    reflected = (
        i1.horizontal_reflection(
            geometry
        )
    )

    kwargs = {}

    if substrate == "D1":
        kwargs[
            "coupled"
        ] = coupled

    assert (
        i1.observation_signature(
            substrate,
            geometry,
            "all-vertices",
            **kwargs,
        )
        == i1.observation_signature(
            substrate,
            reflected,
            "all-vertices",
            **kwargs,
        )
    )


@pytest.mark.parametrize(
    "substrate",
    i1.SUBSTRATES,
)
def test_reflection_maps_elementary_response_family_bijectively(
    substrate,
):
    geometry = (
        _asymmetric_connected_geometry()
    )

    reflected = (
        i1.horizontal_reflection(
            geometry
        )
    )

    original_cells = (
        i1._substrate_cells(
            substrate,
            geometry,
        )
    )

    reflected_cells = (
        i1._substrate_cells(
            substrate,
            reflected,
        )
    )

    reflected_index = {
        cell: index
        for index, cell in enumerate(
            reflected_cells
        )
    }

    kwargs = {}

    if substrate == "D1":
        kwargs[
            "coupled"
        ] = True

    for source_index, cell in enumerate(
        original_cells
    ):
        reflected_cell = (
            i1._reflection_cell(
                geometry,
                cell,
            )
        )

        target_index = (
            reflected_index[
                reflected_cell
            ]
        )

        original_impulse = (
            i1.unit_impulse(
                len(
                    original_cells
                ),
                source_index,
            )
        )

        reflected_impulse = (
            i1.unit_impulse(
                len(
                    reflected_cells
                ),
                target_index,
            )
        )

        assert (
            i1.elementary_response(
                substrate,
                geometry,
                original_impulse,
                **kwargs,
            )
            == i1.elementary_response(
                substrate,
                reflected,
                reflected_impulse,
                **kwargs,
            )
        )


def test_all_vertices_aggregation_removes_source_order():
    geometry = (
        _asymmetric_connected_geometry()
    )

    graph = i1.b0.build_geometry_graph(
        geometry
    )

    family = (
        i1.elementary_impulse_family(
            len(graph.cells)
        )
    )

    forward = tuple(sorted(
        i1.b0_elementary_response(
            geometry,
            impulse,
        )
        for impulse in family
    ))

    reverse = tuple(sorted(
        i1.b0_elementary_response(
            geometry,
            impulse,
        )
        for impulse in reversed(
            family
        )
    ))

    assert forward == reverse


def test_i1_minimum_is_not_component_wise_gate2_probe():
    geometry = _geometry()

    graph = i1.b0.build_geometry_graph(
        geometry
    )

    assert len(
        graph.components
    ) > 1

    i1_minimum = (
        i1.selected_impulse(
            "B0",
            geometry,
            "minimum",
        )
    )

    gate2_probe = (
        i1.b0.canonical_component_probe(
            graph
        )
    )

    assert sum(
        i1_minimum
    ) == 1

    assert sum(
        gate2_probe
    ) == len(
        graph.components
    )

    assert (
        i1_minimum
        != gate2_probe
    )


def test_rejects_non_mass_one_elementary_response():
    geometry = _geometry()

    with pytest.raises(
        ValueError
    ):
        i1.b0_elementary_response(
            geometry,
            (
                1,
                1,
                0,
                0,
            ),
        )


def test_rejects_undeclared_substrate_and_mode():
    geometry = _geometry()

    with pytest.raises(
        ValueError
    ):
        i1.observation_signature(
            "F1",
            geometry,
            "minimum",
        )

    with pytest.raises(
        ValueError
    ):
        i1.observation_signature(
            "B0",
            geometry,
            "invented",
        )


def test_all_vertices_has_no_selected_source():
    geometry = _geometry()

    with pytest.raises(
        ValueError
    ):
        i1.selected_source_index(
            "B0",
            geometry,
            "all-vertices",
        )


def test_dynamic_argument_boundary_is_strict():
    geometry = _geometry()

    with pytest.raises(
        ValueError
    ):
        i1.observation_signature(
            "B0",
            geometry,
            "minimum",
            coupled=True,
        )

    with pytest.raises(
        TypeError
    ):
        i1.observation_signature(
            "D1",
            geometry,
            "minimum",
        )


def test_source_boundary_excludes_corpora_and_other_gate_readers():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    forbidden_fragments = (
        "phase_1_corpus",
        "held_out_corpus",
        "extended_corpus",
        "shape_code",
        "petra_vision_graph_laplacian_width4",
        "petra_vision_explicit_spectral_controls_p1",
        "petra_vision_explicit_spectral_controls_s2",
        "petra_vision_explicit_spectral_controls_h1",
        "temporal_observation",
        "orientation_control",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source

    tree = ast.parse(
        source
    )

    imports = []

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
            imports.append(
                ast.unparse(
                    node
                )
            )

    joined = "\n".join(
        imports
    )

    assert "numpy" not in joined
    assert "scipy" not in joined


def test_no_i1_corpus_artifact_is_created_by_structural_tests():
    work = (
        REPOSITORY_ROOT
        / "_work"
        / "petra-vision-gate3-i1"
    )

    assert not work.exists()
