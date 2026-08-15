from __future__ import annotations

import ast
from fractions import Fraction
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
    / "petra_vision_explicit_spectral_controls_t1.py"
)


def _load_tool():
    name = "_petra_vision_gate3_t1_test_subject"

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
            "unable to load G3-T1 tool"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(
        module
    )

    return module


t1 = _load_tool()


def _one_cell() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=((0, 0),)
    )


def _unary_terminal_frame() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 0),
            (1, 4),
            (2, 0),
            (2, 2),
            (2, 4),
            (3, 0),
            (3, 4),
            (4, 0),
            (4, 1),
            (4, 2),
            (4, 3),
            (4, 4),
        )
    )


def _line_two() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (1, 0),
        )
    )


def _line_gap() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (2, 0),
        )
    )


def _l_shape() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (0, 1),
            (1, 0),
        )
    )


def _synthetic_trajectory(
    values,
):
    return tuple(
        ((value, 1),)
        for value in values
    )


def _normalize_raw(
    raw,
    denominator,
):
    return tuple(
        tuple(
            (
                Fraction(
                    value,
                    denominator ** step,
                ).numerator,
                Fraction(
                    value,
                    denominator ** step,
                ).denominator,
            )
            for value in snapshot
        )
        for step, snapshot in zip(
            t1.SAMPLE_STEPS,
            raw,
        )
    )


def test_protocol_constants_are_frozen():
    assert (
        t1.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-t1-v0"
    )

    assert t1.SUBSTRATES == (
        "B0",
        "D1",
        "F1",
        "L1",
    )

    assert t1.REDUCTIONS == (
        "ordered",
        "unordered",
        "endpoints",
        "terminal",
    )

    assert t1.SAMPLE_STEPS == (
        1,
        2,
        4,
        8,
        16,
        32,
    )

    assert t1.TRANSLATION_VECTOR == (
        17,
        11,
    )


def test_canonical_rational_is_exact():
    assert t1.canonical_rational(3) == (
        3,
        1,
    )

    assert t1.canonical_rational(
        Fraction(6, 8)
    ) == (
        3,
        4,
    )

    with pytest.raises(TypeError):
        t1.canonical_rational(
            0.5
        )


@pytest.mark.parametrize(
    (
        "substrate",
        "coupled",
        "denominator",
    ),
    (
        (
            "B0",
            None,
            8,
        ),
        (
            "D1",
            False,
            16,
        ),
        (
            "D1",
            True,
            16,
        ),
        (
            "L1",
            None,
            8,
        ),
    ),
)
def test_normalized_euler_trajectory_is_exact_raw_division(
    substrate,
    coupled,
    denominator,
):
    geometry = _line_gap()

    raw = t1.raw_numerator_trajectory(
        substrate,
        geometry,
        coupled=coupled,
    )

    normalized = t1.normalized_trajectory(
        substrate,
        geometry,
        coupled=coupled,
    )

    assert normalized == _normalize_raw(
        raw,
        denominator,
    )


def test_b0_raw_ordered_matches_frozen_reader():
    geometry = _line_gap()

    graph = t1.b0.build_geometry_graph(
        geometry
    )

    probe = t1.b0.canonical_component_probe(
        graph
    )

    expected = t1.b0.dynamic_signatures_from_probe(
        graph,
        probe,
        denominator=t1.b0.EULER_DENOMINATOR,
        sample_steps=t1.SAMPLE_STEPS,
    )[
        "global_multiset"
    ]

    assert (
        t1.raw_numerator_signature(
            "B0",
            geometry,
            "ordered",
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
def test_d1_raw_ordered_matches_frozen_reader(
    coupled,
):
    geometry = _line_gap()

    graph = t1.d1.build_distance2_graph(
        geometry,
        bridge_weight=(
            t1.d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )

    probe = t1.d1.original_component_probe(
        graph
    )

    expected = t1.d1.coordinate_free_dynamic_signature(
        graph,
        probe,
        denominator=t1.d1.EULER_DENOMINATOR,
        sample_steps=t1.SAMPLE_STEPS,
    )

    assert (
        t1.raw_numerator_signature(
            "D1",
            geometry,
            "ordered",
            coupled=coupled,
        )
        == expected
    )


def test_l1_raw_ordered_matches_frozen_reader():
    geometry = _l_shape()

    expected = t1.l1.full_lattice_signature(
        geometry,
        coupled=True,
        denominator=t1.l1.EULER_DENOMINATOR,
        sample_steps=t1.SAMPLE_STEPS,
    )

    assert (
        t1.raw_numerator_signature(
            "L1",
            geometry,
            "ordered",
        )
        == expected
    )


def test_f1_trajectory_is_exact_and_factor_order_removed():
    geometry = _one_cell()

    trajectory = t1.normalized_trajectory(
        "F1",
        geometry,
    )

    assert len(trajectory) == 6

    for snapshot in trajectory:
        for factor_state in snapshot:
            for pair in factor_state:
                assert type(pair) is tuple
                assert len(pair) == 2
                assert type(pair[0]) is int
                assert type(pair[1]) is int
                assert pair[1] > 0

    synthetic = (
        (
            Fraction(2, 1),
            Fraction(1, 2),
        ),
        (
            Fraction(1, 1),
            Fraction(3, 2),
        ),
    )

    reversed_synthetic = tuple(
        reversed(
            synthetic
        )
    )

    assert (
        t1.canonical_factor_snapshot(
            synthetic
        )
        == t1.canonical_factor_snapshot(
            reversed_synthetic
        )
    )


def test_f1_matches_frozen_positive_reader_after_serialization():
    geometry = _unary_terminal_frame()

    frozen = t1.f1.factor_proximity_signature(
        geometry,
        coupled=True,
    )

    expected = tuple(
        t1.canonical_factor_snapshot(
            snapshot
        )
        for snapshot in frozen
    )

    assert (
        t1.normalized_trajectory(
            "F1",
            geometry,
        )
        == expected
    )


def test_d1_null_and_coupled_use_identical_cells_and_probe():
    geometry = _line_gap()

    null_graph = t1.d1.build_distance2_graph(
        geometry,
        bridge_weight=0,
    )

    coupled_graph = t1.d1.build_distance2_graph(
        geometry,
        bridge_weight=t1.d1.BRIDGE_WEIGHT,
    )

    assert (
        null_graph.cells
        == coupled_graph.cells
    )

    assert (
        t1.d1.original_component_probe(
            null_graph
        )
        == t1.d1.original_component_probe(
            coupled_graph
        )
    )


def test_temporal_reductions_are_exact_projections():
    trajectory = _synthetic_trajectory(
        (
            1,
            2,
            3,
            4,
            5,
            6,
        )
    )

    assert (
        t1.temporal_reduction(
            trajectory,
            "ordered",
        )
        == trajectory
    )

    assert (
        t1.temporal_reduction(
            trajectory,
            "unordered",
        )
        == tuple(sorted(
            trajectory
        ))
    )

    assert (
        t1.temporal_reduction(
            trajectory,
            "endpoints",
        )
        == (
            trajectory[0],
            trajectory[-1],
        )
    )

    assert (
        t1.temporal_reduction(
            trajectory,
            "terminal",
        )
        == trajectory[-1]
    )


def test_unordered_removes_time_order_but_preserves_multiplicity():
    left = _synthetic_trajectory(
        (
            1,
            2,
            2,
            4,
            5,
            6,
        )
    )

    right = _synthetic_trajectory(
        (
            2,
            1,
            2,
            4,
            5,
            6,
        )
    )

    assert left != right

    assert (
        t1.temporal_reduction(
            left,
            "ordered",
        )
        != t1.temporal_reduction(
            right,
            "ordered",
        )
    )

    assert (
        t1.temporal_reduction(
            left,
            "unordered",
        )
        == t1.temporal_reduction(
            right,
            "unordered",
        )
    )

    unordered = t1.temporal_reduction(
        left,
        "unordered",
    )

    duplicate = ((2, 1),)

    assert unordered.count(
        duplicate
    ) == 2


def test_all_six_prefixes_are_frozen():
    trajectory = _synthetic_trajectory(
        (
            4,
            1,
            3,
            2,
            6,
            5,
        )
    )

    ordered = t1.ordered_prefixes(
        trajectory
    )

    unordered = t1.unordered_prefixes(
        trajectory
    )

    assert len(ordered) == 6
    assert len(unordered) == 6

    for length in range(
        1,
        7,
    ):
        assert ordered[
            length - 1
        ] == trajectory[:length]

        assert unordered[
            length - 1
        ] == tuple(sorted(
            trajectory[:length]
        ))


def test_first_divergence_uses_frozen_sample_time():
    left = _synthetic_trajectory(
        (
            1,
            2,
            3,
            4,
            5,
            6,
        )
    )

    right = _synthetic_trajectory(
        (
            1,
            2,
            9,
            4,
            5,
            6,
        )
    )

    assert t1.first_divergence_time(
        left,
        right,
    ) == 4


def test_first_divergence_none_when_trajectories_match():
    trajectory = _synthetic_trajectory(
        (
            1,
            2,
            3,
            4,
            5,
            6,
        )
    )

    assert t1.first_divergence_time(
        trajectory,
        trajectory,
    ) is None


@pytest.mark.parametrize(
    (
        "right_values",
        "expected_label",
    ),
    (
        (
            (
                1,
                2,
                3,
                4,
                5,
                6,
            ),
            "never-diverges",
        ),
        (
            (
                1,
                9,
                9,
                9,
                9,
                9,
            ),
            "diverges-and-remains-different",
        ),
        (
            (
                1,
                9,
                9,
                4,
                5,
                6,
            ),
            "diverges-then-collides-again",
        ),
        (
            (
                1,
                9,
                3,
                9,
                5,
                6,
            ),
            "multiple-difference-collision-transitions",
        ),
    ),
)
def test_persistence_categories(
    right_values,
    expected_label,
):
    left = _synthetic_trajectory(
        (
            1,
            2,
            3,
            4,
            5,
            6,
        )
    )

    right = _synthetic_trajectory(
        right_values
    )

    label, pattern = t1.persistence_pattern(
        left,
        right,
    )

    assert label == expected_label
    assert len(pattern) == 6


@pytest.mark.parametrize(
    (
        "substrate",
        "coupled",
        "geometry",
    ),
    (
        (
            "B0",
            None,
            _line_gap(),
        ),
        (
            "D1",
            False,
            _line_gap(),
        ),
        (
            "D1",
            True,
            _line_gap(),
        ),
        (
            "F1",
            None,
            _unary_terminal_frame(),
        ),
        (
            "L1",
            None,
            _l_shape(),
        ),
    ),
)
def test_translation_invariance(
    substrate,
    coupled,
    geometry,
):
    translated = t1.translate_geometry(
        geometry
    )

    assert (
        t1.normalized_trajectory(
            substrate,
            geometry,
            coupled=coupled,
        )
        == t1.normalized_trajectory(
            substrate,
            translated,
            coupled=coupled,
        )
    )


@pytest.mark.parametrize(
    (
        "substrate",
        "geometry",
    ),
    (
        (
            "F1",
            _one_cell(),
        ),
        (
            "L1",
            _l_shape(),
        ),
    ),
)
def test_intrinsic_channels_are_reflection_equivariant(
    substrate,
    geometry,
):
    reflected = t1.horizontal_reflection(
        geometry
    )

    assert (
        t1.normalized_trajectory(
            substrate,
            geometry,
        )
        == t1.normalized_trajectory(
            substrate,
            reflected,
        )
    )


def test_geometry_transforms_are_exact_and_reflection_is_involution():
    geometry = OrthogonalGeometry(
        cells=(
            (3, 2),
            (3, 3),
            (4, 2),
        )
    )

    translated = t1.translate_geometry(
        geometry
    )

    assert translated.cells == tuple(sorted((
        (20, 13),
        (21, 13),
        (20, 14),
    )))

    reflected = t1.horizontal_reflection(
        geometry
    )

    assert (
        t1.horizontal_reflection(
            reflected
        )
        == geometry
    )


def test_step_zero_d1_is_matched_null_coupled():
    geometry = _line_gap()

    assert (
        t1.step_zero_snapshot(
            "D1",
            geometry,
            coupled=False,
        )
        == t1.step_zero_snapshot(
            "D1",
            geometry,
            coupled=True,
        )
    )


def test_raw_numerator_scale_is_removed_exactly():
    geometry = _one_cell()

    raw = t1.raw_numerator_trajectory(
        "B0",
        geometry,
    )

    normalized = t1.normalized_trajectory(
        "B0",
        geometry,
    )

    assert raw[0] != raw[-1]

    assert normalized[0] == normalized[-1]

    assert normalized[0] == (
        (
            1,
            1,
        ),
    )


def test_f1_rejects_raw_numerator_mode():
    geometry = _one_cell()

    with pytest.raises(
        ValueError,
        match="no Euler numerator",
    ):
        t1.raw_numerator_trajectory(
            "F1",
            geometry,
        )

    with pytest.raises(
        ValueError,
        match="no Euler numerator",
    ):
        t1.raw_numerator_signature(
            "F1",
            geometry,
            "ordered",
        )


@pytest.mark.parametrize(
    "substrate",
    (
        "B0",
        "F1",
        "L1",
    ),
)
def test_non_d1_substrates_reject_coupled_flag(
    substrate,
):
    with pytest.raises(
        ValueError,
        match="does not accept",
    ):
        t1.normalized_trajectory(
            substrate,
            _one_cell(),
            coupled=True,
        )


def test_d1_requires_exact_bool():
    with pytest.raises(
        TypeError,
        match="exact coupled bool",
    ):
        t1.normalized_trajectory(
            "D1",
            _line_gap(),
        )

    with pytest.raises(
        TypeError,
        match="exact coupled bool",
    ):
        t1.normalized_trajectory(
            "D1",
            _line_gap(),
            coupled=1,
        )


def test_malformed_reductions_fail():
    with pytest.raises(
        TypeError,
        match="exact tuple",
    ):
        t1.temporal_reduction(
            [],
            "ordered",
        )

    with pytest.raises(
        ValueError,
        match="exactly six",
    ):
        t1.temporal_reduction(
            (
                ((1, 1),),
            ),
            "ordered",
        )

    trajectory = _synthetic_trajectory(
        (
            1,
            2,
            3,
            4,
            5,
            6,
        )
    )

    with pytest.raises(
        ValueError,
        match="unsupported temporal reduction",
    ):
        t1.temporal_reduction(
            trajectory,
            "future",
        )


def test_invalid_geometry_and_substrate_fail():
    with pytest.raises(TypeError):
        t1.normalized_trajectory(
            "B0",
            object(),
        )

    with pytest.raises(ValueError):
        t1.normalized_trajectory(
            "NOPE",
            _one_cell(),
        )


def test_projection_monotonicity_synthetic():
    a = _synthetic_trajectory(
        (
            1,
            2,
            3,
            4,
            5,
            6,
        )
    )

    b = tuple(a)

    assert (
        t1.temporal_reduction(
            a,
            "ordered",
        )
        == t1.temporal_reduction(
            b,
            "ordered",
        )
    )

    assert (
        t1.temporal_reduction(
            a,
            "unordered",
        )
        == t1.temporal_reduction(
            b,
            "unordered",
        )
    )

    assert (
        t1.temporal_reduction(
            a,
            "endpoints",
        )
        == t1.temporal_reduction(
            b,
            "endpoints",
        )
    )

    c = _synthetic_trajectory(
        (
            1,
            9,
            8,
            7,
            6,
            6,
        )
    )

    d = _synthetic_trajectory(
        (
            1,
            5,
            4,
            3,
            2,
            6,
        )
    )

    assert (
        t1.temporal_reduction(
            c,
            "endpoints",
        )
        == t1.temporal_reduction(
            d,
            "endpoints",
        )
    )

    assert (
        t1.temporal_reduction(
            c,
            "terminal",
        )
        == t1.temporal_reduction(
            d,
            "terminal",
        )
    )


def test_source_boundary_has_no_corpus_or_completed_gate_inputs():
    source = TOOL_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    imported_names = set()

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            imported_names.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module is not None:
                imported_names.add(
                    node.module
                )

    forbidden_import_fragments = (
        "explicit_spectral_controls_p1",
        "explicit_spectral_controls_i1",
        "explicit_spectral_controls_s2",
        "explicit_spectral_controls_h1",
        "explicit_spectral_controls_o1",
        "evidence",
    )

    assert not any(
        fragment in imported
        for imported in imported_names
        for fragment in forbidden_import_fragments
    )

    forbidden_calls = (
        "bounded_phase_1_corpus",
        "heldout",
        "extended",
    )

    called_names = {
        node.func.id
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and isinstance(
                node.func,
                ast.Name,
            )
        )
    }

    assert not (
        called_names
        & set(
            forbidden_calls
        )
    )

    assert "_work/" not in source
