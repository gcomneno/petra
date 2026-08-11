"""Pre-corpus tests for the deterministic G3-P1 evidence runner."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys

import pytest

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

RUNNER_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_p1_evidence.py"
)


def _load_runner():
    name = (
        "_petra_vision_gate3_p1_evidence_test_runner"
    )

    existing = sys.modules.get(
        name
    )

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        RUNNER_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-P1 evidence runner"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(
        module
    )

    return module


runner = _load_runner()


def test_protocol_constants_are_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-p1-evidence-v0"
    )

    assert (
        runner.EXPECTED_P1_PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-p1-v0"
    )

    assert runner.CORPORA == (
        "phase1",
        "heldout",
        "extended",
    )

    assert (
        runner.INTRINSIC_PROBE_MODES
        == (
            "local-degree",
            "constant",
            "zero",
        )
    )


def test_runner_matches_frozen_probe_family():
    assert runner.p1.PROBE_MODES == (
        "minimum",
        "reflected-minimum",
        "local-degree",
        "constant",
        "zero",
    )

    assert (
        runner.TRANSPORTED_PROBE_PAIRS
        == {
            "minimum": (
                "reflected-minimum"
            ),
            "reflected-minimum": (
                "minimum"
            ),
        }
    )


def test_signature_summary_is_exact():
    codes = (
        "A",
        "B",
        "C",
        "D",
    )

    signatures = (
        ("x",),
        ("x",),
        ("y",),
        ("z",),
    )

    summary = runner.summarize_signatures(
        codes,
        signatures,
    )

    assert (
        summary[
            "distinct_signatures"
        ]
        == 3
    )

    assert (
        summary[
            "collision_pair_count"
        ]
        == 1
    )

    assert (
        summary[
            "collision_shape_codes"
        ]
        == [
            [
                "A",
                "B",
            ]
        ]
    )


def test_partition_comparison_reports_splits_and_introductions():
    codes = (
        "A",
        "B",
        "C",
        "D",
    )

    control = (
        ("x",),
        ("x",),
        ("y",),
        ("y",),
    )

    candidate = (
        ("a",),
        ("b",),
        ("c",),
        ("b",),
    )

    control_summary = (
        runner.summarize_signatures(
            codes,
            control,
        )
    )

    candidate_summary = (
        runner.summarize_signatures(
            codes,
            candidate,
        )
    )

    comparison = (
        runner.compare_partitions(
            control_summary,
            candidate_summary,
        )
    )

    assert (
        comparison[
            "split_pair_count"
        ]
        == 2
    )

    assert (
        comparison[
            "introduced_pair_count"
        ]
        == 1
    )

    assert (
        comparison[
            "distinct_signature_delta"
        ]
        == 1
    )


def test_expected_pair_status_handles_presence_and_absence():
    pair = runner.EXPECTED_COLLISION

    assert (
        runner.expected_pair_status(
            pair,
            (
                ("same",),
                ("same",),
            ),
        )
        == {
            "present": True,
            "collides": True,
        }
    )

    assert (
        runner.expected_pair_status(
            (
                "A",
                "B",
            ),
            (
                ("same",),
                ("same",),
            ),
        )
        == {
            "present": False,
            "collides": None,
        }
    )


def test_intrinsic_pair_guard_rejects_separation():
    result = {
        "expected_collision": {
            "present": True,
            "collides": False,
        }
    }

    with pytest.raises(
        RuntimeError
    ):
        runner._assert_intrinsic_pair_control(
            result,
            substrate="D1",
            operator="coupled",
            mode="local-degree",
        )


def test_coordinate_derived_modes_are_not_subject_to_intrinsic_pair_guard():
    result = {
        "expected_collision": {
            "present": True,
            "collides": False,
        }
    }

    runner._assert_intrinsic_pair_control(
        result,
        substrate="D1",
        operator="coupled",
        mode="minimum",
    )

    runner._assert_intrinsic_pair_control(
        result,
        substrate="D1",
        operator="coupled",
        mode="reflected-minimum",
    )


def test_mass_distribution_is_deterministic():
    assert (
        runner._mass_distribution(
            (
                3,
                1,
                3,
                2,
                1,
            )
        )
        == {
            "1": 2,
            "2": 1,
            "3": 2,
        }
    )


def test_canonical_signature_digest_is_deterministic():
    value = {
        "b": [
            2,
            1,
        ],
        "a": {
            "x": True,
        },
    }

    assert (
        runner._signature_digest(
            value
        )
        == runner._signature_digest(
            value
        )
    )


def test_write_evidence_is_byte_deterministic(
    tmp_path,
):
    evidence = {
        "z": 2,
        "a": {
            "x": 1,
        },
    }

    first = (
        tmp_path
        / "first.json"
    )

    second = (
        tmp_path
        / "second.json"
    )

    runner.write_evidence(
        evidence,
        first,
    )

    runner.write_evidence(
        evidence,
        second,
    )

    assert (
        first.read_bytes()
        == second.read_bytes()
    )


def test_build_evidence_rejects_unknown_corpus_before_selection(
    monkeypatch,
):
    def fail_select(_name):
        raise AssertionError(
            "corpus selector must not run"
        )

    monkeypatch.setattr(
        runner,
        "_select_corpus",
        fail_select,
    )

    with pytest.raises(
        ValueError
    ):
        runner.build_evidence(
            "invented"
        )


def test_cli_requires_frozen_corpus_choice():
    args = runner._parse_args([
        "--corpus",
        "phase1",
        "--output",
        "evidence.json",
    ])

    assert args.corpus == "phase1"
    assert args.output == Path(
        "evidence.json"
    )

    with pytest.raises(
        SystemExit
    ):
        runner._parse_args([
            "--corpus",
            "invented",
            "--output",
            "evidence.json",
        ])


def test_full_analysis_smoke_uses_only_synthetic_geometries(
    monkeypatch,
):
    geometries = (
        OrthogonalGeometry(
            cells=(
                (0, 0),
            )
        ),
        OrthogonalGeometry(
            cells=(
                (0, 0),
                (1, 0),
            )
        ),
    )

    codes = {
        id(geometries[0]): "SYNTH-A",
        id(geometries[1]): "SYNTH-B",
    }

    monkeypatch.setattr(
        runner,
        "_select_corpus",
        lambda _name: geometries,
    )

    monkeypatch.setattr(
        runner.width4,
        "shape_code",
        lambda shape: codes[
            id(shape)
        ],
    )

    monkeypatch.setattr(
        runner.width4,
        "encode_experimental_geometry",
        lambda shape: shape,
    )

    analysis = runner.analyze_corpus(
        "phase1"
    )

    assert (
        analysis[
            "form_count"
        ]
        == 2
    )

    assert set(
        analysis[
            "probes"
        ]
    ) == set(
        runner.p1.PROBE_MODES
    )

    assert set(
        analysis[
            "substrates"
        ]
    ) == {
        "B0",
        "D1",
    }

    for mode in runner.p1.PROBE_MODES:
        assert (
            analysis[
                "substrates"
            ][
                "B0"
            ][
                "modes"
            ][mode][
                "translation_audit_passed"
            ]
            is True
        )

        assert (
            analysis[
                "substrates"
            ][
                "B0"
            ][
                "modes"
            ][mode][
                "reflection_audit_passed"
            ]
            is True
        )

        d1_mode = analysis[
            "substrates"
        ][
            "D1"
        ][
            "modes"
        ][mode]

        assert (
            d1_mode[
                "matched_probe_identity"
            ]
            is True
        )

        assert (
            d1_mode[
                "null"
            ][
                "translation_audit_passed"
            ]
            is True
        )

        assert (
            d1_mode[
                "coupled"
            ][
                "reflection_audit_passed"
            ]
            is True
        )


def test_source_boundary_has_only_p1_and_corpus_runner_dependencies():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    forbidden_fragments = (
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

    assert (
        "scipy"
        not in joined
    )

    assert (
        "numpy"
        not in joined
    )


def test_test_suite_itself_does_not_call_frozen_corpora():
    source = Path(
        __file__
    ).read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    frozen_corpus_calls = {
        "phase_1_corpus",
        "held_out_corpus",
        "extended_corpus",
    }

    frozen_build_evidence_args = {
        "phase1",
        "heldout",
        "extended",
    }

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        function = node.func

        if isinstance(
            function,
            ast.Name,
        ):
            function_name = function.id
        elif isinstance(
            function,
            ast.Attribute,
        ):
            function_name = function.attr
        else:
            function_name = None

        assert (
            function_name
            not in frozen_corpus_calls
        )

        if (
            function_name == "build_evidence"
            and node.args
            and isinstance(
                node.args[0],
                ast.Constant,
            )
            and node.args[0].value
            in frozen_build_evidence_args
        ):
            raise AssertionError(
                "test suite executes a frozen P1 corpus"
            )
