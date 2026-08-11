"""Gate 3 G3-S2 structural tests without frozen-corpus evaluation."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys

import sympy as sp

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_s2.py"
)


def _load_tool():
    name = "_petra_vision_gate3_s2_test_tool"

    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        TOOL_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-S2 research tool"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


s2 = _load_tool()


def _geometry(
    *cells: tuple[int, int],
) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(cells))
    )


def _permuted_matrix(
    matrix: sp.MatrixBase,
    permutation: tuple[int, ...],
) -> sp.Matrix:
    order = matrix.rows

    assert len(permutation) == order

    permutation_matrix = sp.zeros(
        order,
        order,
    )

    for row, column in enumerate(
        permutation
    ):
        permutation_matrix[
            row,
            column,
        ] = 1

    return (
        permutation_matrix
        * matrix
        * permutation_matrix.T
    )


def test_protocol_identifier_is_frozen():
    assert (
        s2.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-s2-v0"
    )

    assert s2.APPLICABLE_SUBSTRATES == (
        "B0",
        "D1",
        "F1",
    )


def test_b0_units_are_exact_frozen_graph_components():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (4, 0),
    )

    graph = s2.s01.v1.build_geometry_graph(
        geometry
    )

    matrices = s2.b0_component_matrices(
        geometry
    )

    assert len(matrices) == len(
        graph.components
    ) == 2

    assert matrices[0] == sp.Matrix([
        [1, -1],
        [-1, 1],
    ])

    assert matrices[1] == sp.Matrix([
        [0],
    ])


def test_b0_component_product_equals_global_charpoly():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (4, 0),
        (4, 1),
        (4, 2),
    )

    local_signature = (
        s2.b0_component_spectrum_signature(
            geometry
        )
    )

    product = (
        s2.multiply_polynomial_signatures(
            local_signature
        )
    )

    global_signature = (
        s2.s01.exact_operator_spectrum_signature(
            "B0",
            geometry,
        )
    )

    assert product == global_signature


def test_local_multiset_discards_component_presentation_order():
    first = sp.Matrix([
        [1, -1],
        [-1, 1],
    ])

    second = sp.Matrix([
        [0],
    ])

    assert (
        s2.local_spectral_multiset(
            (
                first,
                second,
            )
        )
        == s2.local_spectral_multiset(
            (
                second,
                first,
            )
        )
    )


def test_b0_local_spectrum_is_vertex_relabelling_invariant():
    matrix = sp.Matrix([
        [1, -1, 0],
        [-1, 2, -1],
        [0, -1, 1],
    ])

    permuted = _permuted_matrix(
        matrix,
        (
            2,
            0,
            1,
        ),
    )

    assert (
        s2.local_spectral_multiset(
            (matrix,)
        )
        == s2.local_spectral_multiset(
            (permuted,)
        )
    )


def test_d1_units_equal_original_components_and_exclude_bridge():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (3, 0),
    )

    graph = (
        s2.s01.d1.build_distance2_graph(
            geometry
        )
    )

    assert any(
        edge.kind == "bridge"
        for edge in graph.edges
    )

    assert any(
        edge.kind == "local"
        for edge in graph.edges
    )

    matrices = (
        s2.d1_original_component_matrices(
            geometry
        )
    )

    assert len(matrices) == len(
        graph.original_components
    ) == 2

    assert matrices[0] == sp.Matrix([
        [2, -2],
        [-2, 2],
    ])

    assert matrices[1] == sp.Matrix([
        [0],
    ])

    assert all(
        entry in {
            -2,
            0,
            2,
        }
        for matrix in matrices
        for entry in matrix
    )


def test_d1_bridge_only_geometry_remains_two_local_singletons():
    geometry = _geometry(
        (0, 0),
        (2, 0),
    )

    graph = (
        s2.s01.d1.build_distance2_graph(
            geometry
        )
    )

    assert len(graph.edges) == 1
    assert graph.edges[0].kind == "bridge"

    matrices = (
        s2.d1_original_component_matrices(
            geometry
        )
    )

    assert matrices == (
        sp.Matrix([[0]]),
        sp.Matrix([[0]]),
    )

    signature = (
        s2.d1_original_component_spectrum_signature(
            geometry
        )
    )

    singleton = (
        (1, 1),
        (0, 1),
    )

    assert signature == (
        singleton,
        singleton,
    )


def test_d1_local_multiset_is_component_order_invariant():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (4, 0),
    )

    matrices = (
        s2.d1_original_component_matrices(
            geometry
        )
    )

    assert (
        s2.local_spectral_multiset(
            matrices
        )
        == s2.local_spectral_multiset(
            tuple(reversed(matrices))
        )
    )


def test_f1_immediate_factors_use_native_fgs_and_recompose_exactly():
    terminal = _geometry(
        (0, 0),
    )

    source = s2.fgs.recompose_fgs(
        (
            terminal,
            terminal,
        )
    )

    factors = s2.f1_immediate_factors(
        source
    )

    assert factors == s2.fgs.native_fgs(
        source
    )

    assert s2.fgs.recompose_fgs(
        factors
    ) == source

    assert factors == (
        terminal,
        terminal,
    )


def test_f1_factor_spectrum_discards_factor_order_and_preserves_multiplicity():
    terminal = _geometry(
        (0, 0),
    )

    source = s2.fgs.recompose_fgs(
        (
            terminal,
            terminal,
        )
    )

    matrices = s2.f1_factor_matrices(
        source
    )

    assert len(matrices) == 2

    assert (
        s2.local_spectral_multiset(
            matrices
        )
        == s2.local_spectral_multiset(
            tuple(reversed(matrices))
        )
    )

    signature = (
        s2.f1_factor_spectrum_signature(
            source
        )
    )

    singleton = (
        (1, 1),
        (0, 1),
    )

    assert signature == (
        singleton,
        singleton,
    )


def test_terminal_f1_has_empty_local_spectral_multiset():
    terminal = _geometry(
        (0, 0),
    )

    assert s2.f1_immediate_factors(
        terminal
    ) == ()

    assert s2.f1_factor_matrices(
        terminal
    ) == ()

    assert (
        s2.f1_factor_spectrum_signature(
            terminal
        )
        == ()
    )

    assert s2.local_unit_count(
        "F1",
        terminal,
    ) == 0


def test_l1_is_explicitly_not_applicable():
    geometry = _geometry(
        (0, 0),
    )

    assert s2.local_unit_count(
        "L1",
        geometry,
    ) is None

    assert s2.local_spectrum_signature(
        "L1",
        geometry,
    ) == s2.NOT_APPLICABLE


def test_signature_serialization_is_byte_deterministic():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (4, 0),
    )

    first = s2.local_spectrum_signature(
        "B0",
        geometry,
    )

    second = s2.local_spectrum_signature(
        "B0",
        geometry,
    )

    assert first == second

    assert (
        s2.signature_bytes(first)
        == s2.signature_bytes(second)
    )


def test_primary_source_boundary_excludes_structural_identity_inputs():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    forbidden = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "shape_code",
        "corpus_index",
    }

    for name in forbidden:
        assert name not in source

    tree = ast.parse(
        source
    )

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.ImportFrom,
        ):
            continue

        if (
            node.module
            and node.module.startswith(
                "petra.vision"
            )
        ):
            imported = {
                alias.name
                for alias in node.names
            }

            assert imported <= {
                "OrthogonalGeometry",
            }


def test_s2_source_does_not_call_probe_dynamic_or_temporal_readers():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    forbidden_calls = {
        "probe_state",
        "canonical_component_probe",
        "original_component_probe",
        "dynamic_signatures_from_probe",
        "coordinate_free_dynamic_signature",
        "factor_proximity_signature",
        "full_lattice_signature",
        "evolve_euler_numerator",
        "evolve_weighted_euler_numerator",
        "evolve_factor_state",
        "evolve_lattice_numerator",
        "ordered_factor_proximity_signature",
    }

    called_names = set()

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if isinstance(
            node.func,
            ast.Name,
        ):
            called_names.add(
                node.func.id
            )

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            called_names.add(
                node.func.attr
            )

    assert not (
        called_names
        & forbidden_calls
    )


def test_invalid_substrate_is_rejected():
    geometry = _geometry(
        (0, 0),
    )

    try:
        s2.local_spectrum_signature(
            "UNKNOWN",
            geometry,
        )
    except ValueError as error:
        assert (
            "unsupported Gate 3 S2 substrate"
            in str(error)
        )
    else:
        raise AssertionError(
            "invalid substrate unexpectedly accepted"
        )
