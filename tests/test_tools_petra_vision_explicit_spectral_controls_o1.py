from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

import pytest

from petra.vision import (
    OrderedGroup,
    Terminal,
    encode_geometry,
)


ROOT = Path(__file__).resolve().parents[1]
TOOL = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_o1.py"
)


def _load():
    name = "_petra_gate3_o1_test_subject"
    spec = importlib.util.spec_from_file_location(
        name,
        TOOL,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


o1 = _load()


def geometry(cells):
    return o1.OrthogonalGeometry(
        cells=tuple(sorted(cells))
    )


SIMPLE = geometry({
    (0, 0),
    (0, 1),
    (1, 0),
    (3, 0),
    (3, 1),
})

ASYMMETRIC = geometry({
    (0, 0),
    (0, 1),
    (1, 0),
    (3, 0),
    (4, 0),
    (4, 1),
    (4, 2),
})


F1_SIMPLE = encode_geometry(
    OrderedGroup(
        children=(
            Terminal(),
            Terminal(),
            Terminal(),
        )
    )
)


F1_ASYMMETRIC = encode_geometry(
    OrderedGroup(
        children=(
            Terminal(),
            OrderedGroup(
                children=(
                    Terminal(),
                )
            ),
            OrderedGroup(
                children=(
                    Terminal(),
                    Terminal(),
                )
            ),
        )
    )
)


def channel_geometry(
    channel,
    *,
    asymmetric=False,
):
    if channel.startswith("F1-"):
        return (
            F1_ASYMMETRIC
            if asymmetric
            else F1_SIMPLE
        )

    return (
        ASYMMETRIC
        if asymmetric
        else SIMPLE
    )


def test_protocol_id_and_schedule_are_frozen():
    assert (
        o1.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-o1-v0"
    )

    assert o1.SAMPLE_STEPS == (
        1,
        2,
        4,
        8,
        16,
        32,
    )

    assert o1.TRANSLATION_VECTOR == (
        17,
        11,
    )


def test_channels_are_exactly_the_frozen_o1_channels():
    assert o1.CHANNELS == (
        "B0",
        "D1-null",
        "D1-coupled",
        "F1-null",
        "F1-coupled",
        "L1-null",
        "L1-coupled",
    )


def test_observations_are_exactly_the_four_frozen_controls():
    assert o1.OBSERVATIONS == (
        "coordinate-free-step0",
        "oriented-step0",
        "coordinate-free-dynamic",
        "oriented-dynamic",
    )


def test_invalid_geometry_and_channel_fail_closed():
    with pytest.raises(TypeError):
        o1.native_state(
            object(),
            "B0",
        )

    with pytest.raises(ValueError):
        o1.native_state(
            SIMPLE,
            "P1",
        )


def test_horizontal_reflection_is_involution():
    assert (
        o1.horizontal_reflection(
            o1.horizontal_reflection(
                ASYMMETRIC
            )
        )
        == ASYMMETRIC
    )


def test_translation_is_exact():
    translated = o1.translate_geometry(
        SIMPLE
    )

    assert translated.cells == tuple(sorted(
        (x + 17, y + 11)
        for x, y in SIMPLE.cells
    ))


@pytest.mark.parametrize(
    "channel",
    o1.CHANNELS,
)
def test_step_zero_coordinate_free_is_sorted_native_state(
    channel,
):
    current = channel_geometry(
        channel
    )

    signatures = o1.step_zero_signatures(
        current,
        channel,
    )

    assert signatures[
        "coordinate-free-step0"
    ] == tuple(sorted(
        signatures[
            "oriented-step0"
        ]
    ))


@pytest.mark.parametrize(
    "channel",
    o1.CHANNELS,
)
def test_oriented_dynamic_projects_exactly_to_frozen_coordinate_free_reader(
    channel,
):
    current = channel_geometry(
        channel
    )

    signatures = o1.dynamic_signatures(
        current,
        channel,
    )

    oriented = signatures[
        "oriented-dynamic"
    ]

    coordinate_free = signatures[
        "coordinate-free-dynamic"
    ]

    assert tuple(
        tuple(sorted(sample))
        for sample in oriented
    ) == coordinate_free


def test_b0_delegates_to_existing_oriented_and_global_readers():
    graph = o1.b0.build_geometry_graph(
        SIMPLE
    )
    probe = o1.b0.canonical_component_probe(
        graph
    )

    frozen = o1.b0.dynamic_signatures_from_probe(
        graph,
        probe,
        denominator=o1.b0.EULER_DENOMINATOR,
        sample_steps=o1.SAMPLE_STEPS,
    )

    assert (
        o1.oriented_dynamic_signature(
            SIMPLE,
            "B0",
        )
        == frozen["oriented"]
    )

    assert (
        o1.coordinate_free_dynamic_signature(
            SIMPLE,
            "B0",
        )
        == frozen["global_multiset"]
    )


@pytest.mark.parametrize(
    "coupled,channel",
    (
        (False, "D1-null"),
        (True, "D1-coupled"),
    ),
)
def test_d1_coordinate_free_reader_is_the_frozen_reader(
    coupled,
    channel,
):
    graph = o1.d1.build_distance2_graph(
        SIMPLE,
        bridge_weight=(
            o1.d1.BRIDGE_WEIGHT
            if coupled
            else 0
        ),
    )

    probe = o1.d1.original_component_probe(
        graph
    )

    expected = (
        o1.d1.coordinate_free_dynamic_signature(
            graph,
            probe,
            denominator=o1.d1.EULER_DENOMINATOR,
            sample_steps=o1.SAMPLE_STEPS,
        )
    )

    assert (
        o1.coordinate_free_dynamic_signature(
            SIMPLE,
            channel,
        )
        == expected
    )


@pytest.mark.parametrize(
    "coupled,channel",
    (
        (False, "F1-null"),
        (True, "F1-coupled"),
    ),
)
def test_f1_delegates_to_existing_ordered_diagnostic_and_coordinate_free_reader(
    coupled,
    channel,
):
    current = o1.canonical_origin_geometry(
        F1_SIMPLE
    )

    assert (
        o1.oriented_dynamic_signature(
            F1_SIMPLE,
            channel,
        )
        == o1.f1.ordered_factor_proximity_signature(
            current,
            coupled=coupled,
        )
    )

    assert (
        o1.coordinate_free_dynamic_signature(
            F1_SIMPLE,
            channel,
        )
        == o1.f1.factor_proximity_signature(
            current,
            coupled=coupled,
        )
    )


@pytest.mark.parametrize(
    "coupled,channel",
    (
        (False, "L1-null"),
        (True, "L1-coupled"),
    ),
)
def test_l1_coordinate_free_reader_is_the_frozen_reader(
    coupled,
    channel,
):
    assert (
        o1.coordinate_free_dynamic_signature(
            SIMPLE,
            channel,
        )
        == o1.l1.full_lattice_signature(
            SIMPLE,
            coupled=coupled,
            denominator=o1.l1.EULER_DENOMINATOR,
            sample_steps=o1.SAMPLE_STEPS,
        )
    )


@pytest.mark.parametrize(
    "channel",
    o1.CHANNELS,
)
def test_uniform_translation_preserves_all_o1_signatures(
    channel,
):
    current = channel_geometry(
        channel
    )

    translated = o1.translate_geometry(
        current
    )

    assert (
        o1.observation_signatures(
            current,
            channel,
        )
        == o1.observation_signatures(
            translated,
            channel,
        )
    )


@pytest.mark.parametrize(
    "channel",
    o1.CHANNELS,
)
def test_reflection_transport_preserves_frozen_dynamics(
    channel,
):
    current = channel_geometry(
        channel,
        asymmetric=True,
    )

    assert (
        o1.reflection_transport_audit(
            current,
            channel,
        )
        is True
    )


@pytest.mark.parametrize(
    "channel",
    o1.CHANNELS,
)
def test_reflection_mapping_is_bijective(
    channel,
):
    current = channel_geometry(
        channel,
        asymmetric=True,
    )

    permutation = o1.reflection_permutation(
        current,
        channel,
    )

    assert sorted(
        permutation
    ) == list(
        range(
            len(permutation)
        )
    )


@pytest.mark.parametrize(
    "channel",
    (
        "B0",
        "D1-null",
        "D1-coupled",
        "L1-null",
        "L1-coupled",
    ),
)
def test_euler_normalization_is_exact_and_shape_preserving(
    channel,
):
    raw = o1.oriented_dynamic_signature(
        SIMPLE,
        channel,
    )

    normalized = (
        o1.normalized_dynamic_signature(
            SIMPLE,
            channel,
            oriented=True,
        )
    )

    assert len(raw) == len(normalized)

    assert tuple(
        len(sample)
        for sample in raw
    ) == tuple(
        len(sample)
        for sample in normalized
    )


def test_f1_rejects_artificial_euler_normalization():
    with pytest.raises(ValueError):
        o1.normalized_dynamic_signature(
            SIMPLE,
            "F1-coupled",
            oriented=True,
        )


@pytest.mark.parametrize(
    "channel",
    o1.CHANNELS,
)
def test_canonical_reflection_diagnostic_has_only_frozen_observations(
    channel,
):
    current = channel_geometry(
        channel,
        asymmetric=True,
    )

    report = (
        o1.canonical_reflection_diagnostic(
            current,
            channel,
        )
    )

    assert tuple(
        report
    ) == o1.OBSERVATIONS

    assert all(
        type(value) is bool
        for value in report.values()
    )


def test_source_boundary_excludes_other_gate3_readers_and_gate4():
    source = TOOL.read_text(
        encoding="utf-8"
    )

    forbidden_imports = (
        "explicit_spectral_controls_p1",
        "explicit_spectral_controls_i1",
        "explicit_spectral_controls_t1",
        "explicit_spectral_controls_h1",
        "explicit_spectral_controls_s2",
        "gate4",
        "mutation_generator",
    )

    for forbidden in forbidden_imports:
        assert forbidden not in source


def test_no_corpus_or_shape_identity_api_is_used_by_o1():
    source = TOOL.read_text(
        encoding="utf-8"
    )

    forbidden_calls = (
        "bounded_phase_1_corpus(",
        "shape_code(",
        "width4",
        "corpus_index",
        "serialization",
    )

    for forbidden in forbidden_calls:
        assert forbidden not in source


def test_no_runner_or_evidence_artifact_exists_pre_corpus():
    runner = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_explicit_spectral_controls_o1_evidence.py"
    )

    evidence = (
        ROOT
        / "docs"
        / "research"
        / "petra-vision"
        / "EXPLICIT_SPECTRAL_CONTROLS_O1_EVIDENCE.md"
    )

    work = (
        ROOT
        / "_work"
        / "petra-vision-gate3-o1"
    )

    assert not runner.exists()
    assert not evidence.exists()
    assert not work.exists()
