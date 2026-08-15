from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

import pytest

from petra.vision import (
    OrderedGroup,
    Terminal,
)


ROOT = Path(__file__).resolve().parents[1]

RUNNER = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_o1_evidence.py"
)

O1_TOOL = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_o1.py"
)

O1_PROTOCOL = (
    ROOT
    / "docs"
    / "research"
    / "petra-vision"
    / "EXPLICIT_SPECTRAL_CONTROLS_O1_PROTOCOL.md"
)

WIDTH4 = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)


def _load():
    name = (
        "_petra_gate3_o1_"
        "evidence_test_subject"
    )

    spec = (
        importlib.util.spec_from_file_location(
            name,
            RUNNER,
        )
    )

    assert spec is not None
    assert spec.loader is not None

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    sys.modules[
        name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


runner = _load()


SYNTHETIC_SHAPES = (
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


ASYMMETRIC_SHAPE = OrderedGroup(
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


def synthetic_analysis():
    return runner.analyze_corpus(
        name="synthetic",
        shapes=SYNTHETIC_SHAPES,
        progress=False,
    )


def test_evidence_protocol_and_scope_are_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-o1-evidence-v0"
    )

    assert runner.CORPORA == (
        "phase1",
        "heldout",
        "extended",
    )

    assert runner.CHANNELS == (
        "B0",
        "D1-null",
        "D1-coupled",
        "F1-null",
        "F1-coupled",
        "L1-null",
        "L1-coupled",
    )

    assert runner.OBSERVATIONS == (
        "coordinate-free-step0",
        "oriented-step0",
        "coordinate-free-dynamic",
        "oriented-dynamic",
    )


def test_runner_locks_frozen_source_digests():
    assert (
        runner._sha256_file(
            O1_PROTOCOL
        )
        == runner.EXPECTED_PROTOCOL_SHA256
    )

    assert (
        runner._sha256_file(
            O1_TOOL
        )
        == runner.EXPECTED_TOOL_SHA256
    )

    assert (
        runner._sha256_file(
            WIDTH4
        )
        == runner.EXPECTED_WIDTH4_SHA256
    )


def test_jsonable_fraction_is_exact():
    assert runner._jsonable(
        Fraction(
            7,
            9,
        )
    ) == {
        "fraction": [
            7,
            9,
        ]
    }


def test_signature_digest_is_deterministic():
    signature = (
        (
            Fraction(
                1,
                3,
            ),
            2,
        ),
        (
            Fraction(
                5,
                7,
            ),
        ),
    )

    assert (
        runner._signature_digest(
            signature
        )
        == runner._signature_digest(
            signature
        )
    )


def test_collision_summary_is_exact():
    codes = (
        "a",
        "b",
        "c",
        "d",
    )

    signatures = (
        (1,),
        (1,),
        (2,),
        (2,),
    )

    summary = (
        runner.summarize_signatures(
            codes,
            signatures,
        )
    )

    assert summary[
        "distinct_signatures"
    ] == 2

    assert summary[
        "collision_group_count"
    ] == 2

    assert summary[
        "collision_pair_count"
    ] == 2

    assert summary[
        "collision_shape_codes"
    ] == [
        [
            "a",
            "b",
        ],
        [
            "c",
            "d",
        ],
    ]


def test_partition_comparison_reports_exact_pair_changes():
    codes = (
        "a",
        "b",
        "c",
    )

    control = (
        runner.summarize_signatures(
            codes,
            (
                1,
                1,
                2,
            ),
        )
    )

    candidate = (
        runner.summarize_signatures(
            codes,
            (
                1,
                2,
                2,
            ),
        )
    )

    comparison = (
        runner.compare_partitions(
            control,
            candidate,
        )
    )

    assert comparison[
        "split_pairs"
    ] == [
        [
            "a",
            "b",
        ]
    ]

    assert comparison[
        "introduced_pairs"
    ] == [
        [
            "b",
            "c",
        ]
    ]


def test_expected_pair_status_handles_absence():
    assert runner.expected_pair_status(
        (
            "x",
            "y",
        ),
        (
            1,
            1,
        ),
    ) == {
        "present": False,
        "collides": None,
    }


def test_parse_args_requires_explicit_corpus_and_output():
    args = runner.parse_args([
        "--corpus",
        "phase1",
        "--output",
        "example.json",
    ])

    assert args.corpus == "phase1"
    assert args.output == Path(
        "example.json"
    )


def test_parse_args_rejects_unknown_corpus():
    with pytest.raises(
        SystemExit
    ):
        runner.parse_args([
            "--corpus",
            "future",
            "--output",
            "example.json",
        ])


def test_analyze_corpus_does_not_call_frozen_selector(
    monkeypatch,
):
    def forbidden_selector(_name):
        raise AssertionError(
            "direct synthetic analysis "
            "must not open a frozen corpus"
        )

    monkeypatch.setattr(
        runner,
        "_select_corpus",
        forbidden_selector,
    )

    analysis = runner.analyze_corpus(
        name="synthetic",
        shapes=SYNTHETIC_SHAPES,
        progress=False,
    )

    assert analysis[
        "corpus"
    ] == "synthetic"

    assert analysis[
        "form_count"
    ] == len(
        SYNTHETIC_SHAPES
    )


def test_synthetic_channel_audits_are_green():
    analysis = synthetic_analysis()

    assert tuple(
        analysis[
            "channels"
        ]
    ) == runner.CHANNELS

    for channel in runner.CHANNELS:
        current = analysis[
            "channels"
        ][
            channel
        ]

        assert (
            current[
                "translation_audit_passed"
            ]
            is True
        )

        assert (
            current[
                "reflection_transport_audit_passed"
            ]
            is True
        )


def test_oriented_readers_are_exact_refinements_synthetically():
    analysis = synthetic_analysis()

    for channel in runner.CHANNELS:
        current = analysis[
            "channels"
        ][
            channel
        ]

        for comparison_name in (
            "coordinate-free-step0_to_oriented-step0",
            "coordinate-free-dynamic_to_oriented-dynamic",
        ):
            comparison = current[
                "comparisons"
            ][
                comparison_name
            ]

            assert (
                comparison[
                    "introduced_pair_count"
                ]
                == 0
            )


def test_euler_raw_and_normalized_partitions_match():
    analysis = synthetic_analysis()

    for channel in (
        "B0",
        "D1-null",
        "D1-coupled",
        "L1-null",
        "L1-coupled",
    ):
        audit = analysis[
            "channels"
        ][
            channel
        ][
            "raw_normalized_audit"
        ]

        assert audit is not None

        for observation in (
            "coordinate-free-dynamic",
            "oriented-dynamic",
        ):
            assert (
                audit[
                    "comparisons"
                ][
                    observation
                ][
                    "partition_equal"
                ]
                is True
            )


def test_f1_has_no_artificial_euler_normalization():
    analysis = synthetic_analysis()

    for channel in (
        "F1-null",
        "F1-coupled",
    ):
        assert (
            analysis[
                "channels"
            ][
                channel
            ][
                "raw_normalized_audit"
            ]
            is None
        )


def test_zero_factor_terminal_survives_runner_analysis():
    analysis = runner.analyze_corpus(
        name="synthetic-terminal",
        shapes=(
            Terminal(),
        ),
        progress=False,
    )

    for channel in (
        "F1-null",
        "F1-coupled",
    ):
        observations = analysis[
            "channels"
        ][
            channel
        ][
            "observations"
        ]

        assert observations[
            "coordinate-free-dynamic"
        ][
            "summary"
        ][
            "distinct_signatures"
        ] == 1

        assert observations[
            "oriented-dynamic"
        ][
            "summary"
        ][
            "distinct_signatures"
        ] == 1

        assert (
            observations[
                "coordinate-free-dynamic"
            ][
                "signature_digests"
            ]
            == observations[
                "oriented-dynamic"
            ][
                "signature_digests"
            ]
        )


def test_canonical_reflection_diagnostic_is_recorded():
    analysis = runner.analyze_corpus(
        name="synthetic-asymmetric",
        shapes=(
            ASYMMETRIC_SHAPE,
        ),
        progress=False,
    )

    for channel in runner.CHANNELS:
        diagnostic = analysis[
            "channels"
        ][
            channel
        ][
            "canonical_reflection_diagnostic"
        ]

        assert tuple(
            diagnostic
        ) == runner.OBSERVATIONS

        for observation in runner.OBSERVATIONS:
            assert (
                diagnostic[
                    observation
                ][
                    "equal_count"
                ]
                + diagnostic[
                    observation
                ][
                    "changed_count"
                ]
                == 1
            )


def test_f1_asymmetric_orientation_leakage_is_visible():
    analysis = runner.analyze_corpus(
        name="synthetic-asymmetric",
        shapes=(
            ASYMMETRIC_SHAPE,
        ),
        progress=False,
    )

    for channel in (
        "F1-null",
        "F1-coupled",
    ):
        diagnostic = analysis[
            "channels"
        ][
            channel
        ][
            "canonical_reflection_diagnostic"
        ]

        assert diagnostic[
            "coordinate-free-step0"
        ][
            "equal_count"
        ] == 1

        assert diagnostic[
            "oriented-step0"
        ][
            "changed_count"
        ] == 1

        assert diagnostic[
            "coordinate-free-dynamic"
        ][
            "equal_count"
        ] == 1

        assert diagnostic[
            "oriented-dynamic"
        ][
            "changed_count"
        ] == 1


def test_source_boundary_metadata_is_frozen():
    analysis = synthetic_analysis()

    assert analysis[
        "source_boundary"
    ] == {
        "shape_code_is_metadata_only": True,
        "width4_geometry_encoder_is_input_only": True,
        "s1_input": False,
        "s2_input": False,
        "h1_input": False,
        "p1_input": False,
        "i1_input": False,
        "t1_input": False,
        "gate4_input": False,
    }


def test_runner_source_has_no_forbidden_gate_inputs():
    source = RUNNER.read_text(
        encoding="utf-8"
    )

    forbidden_paths = (
        "petra_vision_explicit_spectral_controls_s1.py",
        "petra_vision_explicit_spectral_controls_s2.py",
        "petra_vision_explicit_spectral_controls_h1.py",
        "petra_vision_explicit_spectral_controls_p1.py",
        "petra_vision_explicit_spectral_controls_i1.py",
        "petra_vision_explicit_spectral_controls_t1.py",
        "petra_vision_gate4",
        "mutation_generator.py",
    )

    for item in forbidden_paths:
        assert item not in source


def test_canonical_json_is_reproducible_for_synthetic_analysis():
    first = synthetic_analysis()
    second = synthetic_analysis()

    assert (
        runner._canonical_json_bytes(
            first
        )
        == runner._canonical_json_bytes(
            second
        )
    )


def test_no_evidence_or_o1_work_artifact_exists_pre_observation():
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

    assert not evidence.exists()
    assert not work.exists()
