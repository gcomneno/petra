"""Gate 3 G3-H1 structural tests without frozen-corpus evaluation."""

from __future__ import annotations

import ast
from fractions import Fraction
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
    / "petra_vision_explicit_spectral_controls_h1.py"
)


def _load_tool():
    name = "_petra_vision_gate3_h1_test_tool"

    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        TOOL_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-H1 research tool"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


h1 = _load_tool()


def _pair(
    value: object,
) -> tuple[int, int]:
    fraction = Fraction(value)

    return (
        fraction.numerator,
        fraction.denominator,
    )


def test_protocol_identifier_and_ladder_are_frozen():
    assert (
        h1.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-h1-v0"
    )

    assert h1.TRUNCATIONS == (
        ("M1", 1),
        ("M2", 2),
        ("M4", 4),
        ("M8", 8),
    )

    assert h1.MAX_MOMENT == 8


def test_power_sums_match_known_integer_roots():
    # Roots: 0, 1, 2.
    signature = (
        (1, 1),
        (-3, 1),
        (2, 1),
        (0, 1),
    )

    assert (
        h1.power_sums_from_charpoly(
            signature
        )
        == tuple(
            (value, 1)
            for value in (
                3,
                3,
                5,
                9,
                17,
                33,
                65,
                129,
                257,
            )
        )
    )


def test_power_sums_preserve_exact_rational_arithmetic():
    # Roots: 1/2 and 1/3.
    signature = (
        (1, 1),
        (-5, 6),
        (1, 6),
    )

    moments = (
        h1.power_sums_from_charpoly(
            signature,
            max_moment=4,
        )
    )

    assert moments == (
        (2, 1),
        (5, 6),
        (13, 36),
        (35, 216),
        (97, 1296),
    )


def test_power_sums_match_exact_matrix_traces():
    matrix = sp.Matrix([
        [1, -1, 0],
        [-1, 2, -1],
        [0, -1, 1],
    ])

    spectrum = (
        h1.s01.characteristic_polynomial_signature(
            matrix
        )
    )

    moments = (
        h1.power_sums_from_charpoly(
            spectrum
        )
    )

    assert moments[0] == (
        matrix.rows,
        1,
    )

    for power in range(
        1,
        h1.MAX_MOMENT + 1,
    ):
        expected = sp.trace(
            matrix ** power
        )

        assert moments[power] == (
            int(expected),
            1,
        )


def test_empty_operator_has_zero_order_and_zero_positive_moments():
    signature = (
        (1, 1),
    )

    assert (
        h1.power_sums_from_charpoly(
            signature
        )
        == (
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
        )
    )


def test_declared_truncations_are_exact_prefixes():
    signature = (
        (1, 1),
        (-6, 1),
        (11, 1),
        (-6, 1),
    )

    signatures = dict(
        h1.all_heat_trace_moment_signatures_from_spectrum(
            signature
        )
    )

    assert len(signatures["M1"]) == 2
    assert len(signatures["M2"]) == 3
    assert len(signatures["M4"]) == 5
    assert len(signatures["M8"]) == 9

    assert (
        signatures["M2"][:2]
        == signatures["M1"]
    )

    assert (
        signatures["M4"][:3]
        == signatures["M2"]
    )

    assert (
        signatures["M8"][:5]
        == signatures["M4"]
    )


def test_equal_s1_spectra_cannot_be_split_by_h1():
    spectrum = (
        (1, 1),
        (-4, 1),
        (3, 1),
    )

    first = (
        h1.all_heat_trace_moment_signatures_from_spectrum(
            spectrum
        )
    )

    second = (
        h1.all_heat_trace_moment_signatures_from_spectrum(
            tuple(spectrum)
        )
    )

    assert first == second


def test_m4_distinguishes_synthetic_degree_four_spectra():
    first = (
        (1, 1),
        (-10, 1),
        (35, 1),
        (-50, 1),
        (24, 1),
    )

    second = (
        (1, 1),
        (-11, 1),
        (41, 1),
        (-61, 1),
        (30, 1),
    )

    assert (
        h1.heat_trace_moment_signature_from_spectrum(
            first,
            "M4",
        )
        != h1.heat_trace_moment_signature_from_spectrum(
            second,
            "M4",
        )
    )


def test_geometry_reader_delegates_only_to_frozen_s1_spectrum(
    monkeypatch,
):
    geometry = OrthogonalGeometry(
        cells=((0, 0),)
    )

    expected_spectrum = (
        (1, 1),
        (-2, 1),
        (0, 1),
    )

    calls = []

    def fake_spectrum(
        substrate,
        supplied_geometry,
    ):
        calls.append(
            (
                substrate,
                supplied_geometry,
            )
        )

        return expected_spectrum

    monkeypatch.setattr(
        h1.s01,
        "exact_operator_spectrum_signature",
        fake_spectrum,
    )

    result = h1.heat_trace_moment_signature(
        "F1",
        geometry,
        "M2",
    )

    assert calls == [
        (
            "F1",
            geometry,
        )
    ]

    assert result == (
        (2, 1),
        (2, 1),
        (4, 1),
    )


def test_signature_bytes_are_deterministic():
    signature = (
        ("M1", ((2, 1), (4, 1))),
        ("M2", ((2, 1), (4, 1), (10, 1))),
    )

    assert (
        h1.signature_bytes(signature)
        == h1.signature_bytes(signature)
    )


def test_rejects_non_monic_or_noncanonical_polynomials():
    try:
        h1.power_sums_from_charpoly(
            (
                (2, 1),
                (1, 1),
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "non-monic polynomial accepted"
        )

    try:
        h1.power_sums_from_charpoly(
            (
                (1, 1),
                (2, 2),
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "noncanonical rational pair accepted"
        )


def test_rejects_undeclared_truncation_and_excess_moment():
    signature = (
        (1, 1),
        (-1, 1),
    )

    try:
        h1.heat_trace_moment_signature_from_spectrum(
            signature,
            "M3",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "undeclared H1 truncation accepted"
        )

    try:
        h1.power_sums_from_charpoly(
            signature,
            max_moment=9,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "moment above frozen maximum accepted"
        )


def test_source_boundary_contains_no_corpus_or_dynamic_reader():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    forbidden_fragments = (
        "phase_1_corpus",
        "held_out_corpus",
        "extended_corpus",
        "shape_code",
        "native_fgs",
        "probe",
        "impulse",
        "trajectory",
        "temporal",
        "orientation",
        "petra_vision_explicit_spectral_controls_s2",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source

    imported_paths = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            imported_paths.append(
                ast.unparse(node)
            )

    joined = "\n".join(
        imported_paths
    )

    assert (
        "petra_vision_graph_laplacian_width4"
        not in joined
    )
