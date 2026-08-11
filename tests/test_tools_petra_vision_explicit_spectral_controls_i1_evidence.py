"""Structural tests for the frozen G3-I1 evidence runner."""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

RUNNER_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_i1_evidence.py"
)


def _load_runner():
    name = (
        "_petra_vision_gate3_i1_evidence_test_runner"
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
            "unable to load G3-I1 evidence runner"
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


def _geometry_a() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (1, 0),
            (3, 0),
            (4, 0),
        )
    )


def _geometry_b() -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=(
            (0, 0),
            (0, 1),
            (1, 1),
            (2, 1),
        )
    )


def test_runner_protocol_is_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-i1-evidence-v0"
    )

    assert (
        runner.EXPECTED_I1_PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-i1-v0"
    )

    assert runner.CORPORA == (
        "phase1",
        "heldout",
        "extended",
    )

    assert runner.SELECTED_MODES == (
        "minimum",
        "reflected-minimum",
    )


def test_runner_import_does_not_select_any_corpus(
    monkeypatch,
):
    calls = []

    monkeypatch.setattr(
        runner.width4,
        "phase_1_corpus",
        lambda: calls.append(
            "phase1"
        ),
    )

    monkeypatch.setattr(
        runner.width4,
        "held_out_corpus",
        lambda: calls.append(
            "heldout"
        ),
    )

    monkeypatch.setattr(
        runner.width4,
        "extended_corpus",
        lambda: calls.append(
            "extended"
        ),
    )

    assert calls == []


def test_signature_summary_and_partition_comparison():
    codes = (
        "A",
        "B",
        "C",
    )

    control = runner.summarize_signatures(
        codes,
        (
            ("x",),
            ("x",),
            ("y",),
        ),
    )

    candidate = runner.summarize_signatures(
        codes,
        (
            ("x1",),
            ("x2",),
            ("y",),
        ),
    )

    assert (
        control[
            "distinct_signatures"
        ]
        == 2
    )

    assert (
        candidate[
            "distinct_signatures"
        ]
        == 3
    )

    comparison = (
        runner.compare_partitions(
            control,
            candidate,
        )
    )

    assert (
        comparison[
            "distinct_signature_delta"
        ]
        == 1
    )

    assert (
        comparison[
            "split_pair_count"
        ]
        == 1
    )

    assert (
        comparison[
            "introduced_pair_count"
        ]
        == 0
    )


def test_expected_pair_absent_is_explicit():
    status = runner.expected_pair_status(
        (
            "A",
            "B",
        ),
        (
            1,
            1,
        ),
    )

    assert status == {
        "present": False,
        "collides": None,
    }


def test_reflection_source_mapping_is_bijective():
    geometry = _geometry_b()

    cells = runner.i1._substrate_cells(
        "B0",
        geometry,
    )

    targets = []

    for source_index in range(
        len(cells)
    ):
        reflected, target_index = (
            runner._source_index_under_reflection(
                "B0",
                geometry,
                source_index,
            )
        )

        assert (
            len(
                runner.i1._substrate_cells(
                    "B0",
                    reflected,
                )
            )
            == len(cells)
        )

        targets.append(
            target_index
        )

    assert sorted(
        targets
    ) == list(
        range(
            len(cells)
        )
    )


def test_elementary_bijection_audit_matches_batched_b0():
    geometry = _geometry_b()

    aggregate = (
        runner.i1.observation_signature(
            "B0",
            geometry,
            "all-vertices",
        )
    )

    assert (
        runner._elementary_response_bijection_audit(
            "B0",
            geometry,
            coupled=None,
            expected_aggregate=aggregate,
        )
        is True
    )


def test_elementary_bijection_audit_matches_batched_d1():
    geometry = _geometry_a()

    for coupled in (
        False,
        True,
    ):
        aggregate = (
            runner.i1.observation_signature(
                "D1",
                geometry,
                "all-vertices",
                coupled=coupled,
            )
        )

        assert (
            runner._elementary_response_bijection_audit(
                "D1",
                geometry,
                coupled=coupled,
                expected_aggregate=aggregate,
            )
            is True
        )


def test_analyze_corpus_uses_only_injected_tiny_synthetic_domain(
    monkeypatch,
):
    shapes = (
        "synthetic-a",
        "synthetic-b",
    )

    geometries = {
        "synthetic-a": _geometry_a(),
        "synthetic-b": _geometry_b(),
    }

    monkeypatch.setattr(
        runner,
        "_select_corpus",
        lambda name: (
            shapes
            if name == "phase1"
            else ()
        ),
    )

    monkeypatch.setattr(
        runner.width4,
        "shape_code",
        lambda shape: shape,
    )

    monkeypatch.setattr(
        runner.width4,
        "encode_experimental_geometry",
        lambda shape: geometries[
            shape
        ],
    )

    analysis = runner.analyze_corpus(
        "phase1"
    )

    assert (
        analysis[
            "corpus"
        ]
        == "phase1"
    )

    assert (
        analysis[
            "form_count"
        ]
        == 2
    )

    assert set(
        analysis[
            "step_zero"
        ]
    ) == {
        "minimum",
        "reflected-minimum",
        "all-vertices",
    }

    assert set(
        analysis[
            "substrates"
        ]
    ) == {
        "B0",
        "D1",
    }

    all_vertices = analysis[
        "substrates"
    ][
        "D1"
    ][
        "modes"
    ][
        "all-vertices"
    ]

    assert (
        all_vertices[
            "mass_one_invariant"
        ]
        is True
    )

    assert (
        all_vertices[
            "matched_impulse_identity"
        ]
        is True
    )

    assert (
        all_vertices[
            "null"
        ][
            "elementary_aggregation_bijection_audit_passed"
        ]
        is True
    )

    assert (
        all_vertices[
            "coupled"
        ][
            "elementary_aggregation_bijection_audit_passed"
        ]
        is True
    )


def test_evidence_document_contains_frozen_provenance(
    monkeypatch,
):
    monkeypatch.setattr(
        runner,
        "analyze_corpus",
        lambda corpus_name: {
            "corpus": corpus_name,
            "form_count": 2,
        },
    )

    document = runner.evidence_document(
        "phase1"
    )

    assert (
        document[
            "protocol_id"
        ]
        == runner.PROTOCOL_ID
    )

    assert (
        document[
            "i1_protocol_id"
        ]
        == runner.i1.PROTOCOL_ID
    )

    assert (
        document[
            "frozen_parameters"
        ][
            "elementary_impulse_mass"
        ]
        == 1
    )

    assert set(
        document[
            "source_sha256"
        ]
    ) == {
        "i1_protocol",
        "i1_tool",
        "b0_tool",
        "d1_tool",
        "width4_corpus_tool",
        "evidence_runner",
    }


def test_write_evidence_is_deterministic(
    tmp_path,
):
    document = {
        "z": 1,
        "a": {
            "y": 2,
            "x": 3,
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
        first,
        document,
    )

    runner.write_evidence(
        second,
        document,
    )

    assert (
        first.read_bytes()
        == second.read_bytes()
    )

    parsed = json.loads(
        first.read_text(
            encoding="utf-8"
        )
    )

    assert parsed == document


def test_cli_requires_exactly_one_declared_corpus_and_output():
    args = runner._parse_args([
        "--corpus",
        "phase1",
        "--output",
        "artifact.json",
    ])

    assert args.corpus == "phase1"

    assert (
        str(
            args.output
        )
        == "artifact.json"
    )


def test_runner_source_boundary():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    forbidden_fragments = (
        "explicit_spectral_controls_p1",
        "explicit_spectral_controls_s2",
        "explicit_spectral_controls_h1",
        "TEMPORAL_DYNAMICS_HYPOTHESIS",
        "temporal_observation",
        "orientation_control",
        "numpy",
        "scipy",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source

    tree = ast.parse(
        source
    )

    imported_names = []

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
            imported_names.append(
                ast.unparse(
                    node
                )
            )

    joined = "\n".join(
        imported_names
    )

    assert "numpy" not in joined
    assert "scipy" not in joined


def test_test_suite_itself_does_not_call_frozen_corpora():
    source = Path(__file__).read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    forbidden_attributes = {
        "phase_1_corpus",
        "held_out_corpus",
        "extended_corpus",
    }

    actual_calls = []

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
            ast.Attribute,
        ):
            actual_calls.append(
                function.attr
            )

    assert not (
        forbidden_attributes
        & set(
            actual_calls
        )
    )


def test_runner_tests_leave_i1_work_directory_absent():
    work = (
        REPOSITORY_ROOT
        / "_work"
        / "petra-vision-gate3-i1"
    )

    assert not work.exists()
