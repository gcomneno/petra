"""Gate 3 G3-S0/S1 implementation tests without corpus evaluation."""

from __future__ import annotations

import ast
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys

import pytest
import sympy as sp

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls.py"
)


def _load_tool():
    name = "_petra_vision_gate3_s01_test_tool"

    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        TOOL_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load Gate 3 S0/S1 research tool"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


s01 = _load_tool()


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

    if len(permutation) != order:
        raise ValueError(
            "permutation length mismatch"
        )

    permutation_matrix = sp.zeros(
        order,
        order,
    )

    for row, column in enumerate(
        permutation
    ):
        permutation_matrix[row, column] = 1

    return (
        permutation_matrix
        * matrix
        * permutation_matrix.T
    )


def test_protocol_identifier_is_frozen():
    assert (
        s01.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-s0-s1-v0"
    )

    assert s01.SUBSTRATES == (
        "B0",
        "D1",
        "F1",
        "L1",
    )


def test_canonical_rational_is_exact_and_reduced():
    assert s01.canonical_rational(3) == (
        3,
        1,
    )

    assert s01.canonical_rational(
        Fraction(6, 8)
    ) == (
        3,
        4,
    )

    assert s01.canonical_rational(
        sp.Rational(-10, 15)
    ) == (
        -2,
        3,
    )

    with pytest.raises(
        TypeError,
        match="floating-point",
    ):
        s01.canonical_rational(0.5)


def test_characteristic_polynomial_is_exact_monic_and_full_degree():
    matrix = sp.Matrix([
        [2, -1],
        [-1, 2],
    ])

    signature = (
        s01.characteristic_polynomial_signature(
            matrix
        )
    )

    assert signature == (
        (1, 1),
        (-4, 1),
        (3, 1),
    )

    assert len(signature) == 3


def test_zero_order_characteristic_polynomial_is_one():
    matrix = sp.zeros(
        0,
        0,
    )

    assert (
        s01.characteristic_polynomial_signature(
            matrix
        )
        == ((1, 1),)
    )


def test_b0_operator_profile_is_coordinate_free_static_graph_data():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (2, 0),
    )

    profile = s01.b0_operator_profile(
        geometry
    )

    assert profile == (
        3,
        2,
        1,
        (
            (1, 1),
            (1, 1),
            (2, 1),
        ),
    )


def test_d1_profile_uses_frozen_clearance_bridge_weight():
    geometry = _geometry(
        (0, 0),
        (2, 0),
    )

    profile = s01.d1_operator_profile(
        geometry
    )

    assert profile == (
        2,
        1,
        1,
        (
            (1, 1),
            (1, 1),
        ),
    )


def test_b0_d1_and_l1_laplacians_are_exact_symmetric():
    b0_geometry = _geometry(
        (0, 0),
        (1, 0),
        (2, 0),
    )

    d1_geometry = _geometry(
        (0, 0),
        (1, 0),
        (3, 0),
    )

    l1_geometry = _geometry(
        (0, 0),
        (2, 1),
    )

    for matrix in (
        s01.b0_operator_matrix(
            b0_geometry
        ),
        s01.d1_operator_matrix(
            d1_geometry
        ),
        s01.l1_operator_matrix(
            l1_geometry
        ),
    ):
        assert matrix == matrix.T

        for value in matrix:
            assert value.is_Rational


def test_f1_propagation_matrix_preserves_frozen_normalization_exactly():
    weights = (
        (
            Fraction(0, 1),
            Fraction(1, 1),
            Fraction(0, 1),
        ),
        (
            Fraction(1, 1),
            Fraction(0, 1),
            Fraction(1, 2),
        ),
        (
            Fraction(0, 1),
            Fraction(1, 2),
            Fraction(0, 1),
        ),
    )

    matrix = (
        s01.f1_propagation_matrix_from_weights(
            weights
        )
    )

    expected = sp.Matrix([
        [
            sp.Rational(1, 2),
            sp.Rational(1, 2),
            0,
        ],
        [
            sp.Rational(2, 5),
            sp.Rational(2, 5),
            sp.Rational(1, 5),
        ],
        [
            0,
            sp.Rational(1, 3),
            sp.Rational(2, 3),
        ],
    ])

    assert matrix == expected

    assert matrix != matrix.T

    for row in range(matrix.rows):
        assert sum(
            matrix[row, column]
            for column in range(
                matrix.cols
            )
        ) == 1


def test_f1_weight_validation_rejects_hidden_asymmetry():
    with pytest.raises(
        ValueError,
        match="symmetric",
    ):
        s01.f1_propagation_matrix_from_weights(
            (
                (
                    0,
                    1,
                ),
                (
                    0,
                    0,
                ),
            )
        )


@pytest.mark.parametrize(
    ("width", "height"),
    (
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 3),
        (3, 4),
    ),
)
def test_l1_resultant_equals_direct_small_rectangle_charpoly(
    width: int,
    height: int,
):
    direct = (
        s01.characteristic_polynomial_signature(
            s01.rectangular_laplacian_matrix(
                width,
                height,
            )
        )
    )

    resultant = (
        s01.l1_resultant_spectrum_signature(
            width,
            height,
        )
    )

    assert resultant == direct

    assert len(resultant) == (
        width * height + 1
    )

    assert resultant[0] == (
        1,
        1,
    )


@pytest.mark.parametrize(
    ("width", "height"),
    (
        (1, 4),
        (2, 5),
        (3, 4),
    ),
)
def test_l1_resultant_is_axis_exchange_invariant(
    width: int,
    height: int,
):
    assert (
        s01.l1_resultant_spectrum_signature(
            width,
            height,
        )
        == s01.l1_resultant_spectrum_signature(
            height,
            width,
        )
    )


def test_b0_charpoly_is_invariant_under_vertex_relabelling():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (2, 0),
        (2, 1),
    )

    matrix = s01.b0_operator_matrix(
        geometry
    )

    permuted = _permuted_matrix(
        matrix,
        (
            2,
            0,
            3,
            1,
        ),
    )

    assert (
        s01.characteristic_polynomial_signature(
            matrix
        )
        == s01.characteristic_polynomial_signature(
            permuted
        )
    )


def test_d1_charpoly_is_invariant_under_vertex_relabelling():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (3, 0),
        (3, 1),
    )

    matrix = s01.d1_operator_matrix(
        geometry
    )

    permuted = _permuted_matrix(
        matrix,
        (
            3,
            1,
            0,
            2,
        ),
    )

    assert (
        s01.characteristic_polynomial_signature(
            matrix
        )
        == s01.characteristic_polynomial_signature(
            permuted
        )
    )


def test_l1_intrinsic_state_is_unordered_binary_multiset_only():
    geometry = _geometry(
        (0, 0),
        (2, 1),
    )

    signature = (
        s01.l1_intrinsic_state_signature(
            geometry
        )
    )

    assert len(signature) == 6

    assert signature.count(
        (1, 1)
    ) == 2

    assert signature.count(
        (0, 1)
    ) == 4


def test_b0_and_d1_have_no_intrinsic_state_control():
    geometry = _geometry(
        (0, 0),
    )

    assert (
        s01.intrinsic_state_signature(
            "B0",
            geometry,
        )
        is None
    )

    assert (
        s01.intrinsic_state_signature(
            "D1",
            geometry,
        )
        is None
    )


def test_signature_serialization_is_byte_deterministic():
    geometry = _geometry(
        (0, 0),
        (1, 0),
        (2, 0),
    )

    signature_a = (
        s01.exact_operator_spectrum_signature(
            "B0",
            geometry,
        )
    )

    signature_b = (
        s01.exact_operator_spectrum_signature(
            "B0",
            geometry,
        )
    )

    assert signature_a == signature_b

    assert (
        s01.signature_bytes(signature_a)
        == s01.signature_bytes(signature_b)
    )

    json.loads(
        s01.signature_bytes(
            signature_a
        )
    )


def test_primary_source_boundary_excludes_identity_and_decoder_inputs():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "shape_code",
    }

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
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

    for forbidden in forbidden_names:
        assert forbidden not in source


def test_invalid_substrate_is_rejected_before_any_reader_work():
    geometry = _geometry(
        (0, 0),
    )

    with pytest.raises(
        ValueError,
        match="unsupported Gate 3 substrate",
    ):
        s01.operator_elementary_signature(
            "UNKNOWN",
            geometry,
        )
