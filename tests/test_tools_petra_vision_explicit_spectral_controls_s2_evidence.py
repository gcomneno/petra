"""Structural tests for the Gate 3 G3-S2 evidence runner."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

RUNNER_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_s2_evidence.py"
)


def _load_runner():
    name = "_petra_vision_gate3_s2_evidence_test"

    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        RUNNER_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-S2 evidence runner"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


runner = _load_runner()


def test_evidence_protocol_identifier_is_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-s2-evidence-v0"
    )

    assert runner.SUBSTRATES == (
        "B0",
        "D1",
        "F1",
    )

    assert runner.CORPORA == (
        "phase1",
        "heldout",
        "extended",
    )


def test_summary_preserves_exact_collision_groups():
    summary = runner.summarize_signatures(
        (
            "A",
            "B",
            "C",
        ),
        (
            ("x",),
            ("x",),
            ("y",),
        ),
    )

    assert summary[
        "distinct_signatures"
    ] == 2

    assert summary[
        "collision_pair_count"
    ] == 1

    assert summary[
        "collision_shape_codes"
    ] == [
        [
            "A",
            "B",
        ]
    ]


def test_partition_comparison_allows_both_splits_and_introductions():
    reference = runner.summarize_signatures(
        (
            "A",
            "B",
            "C",
            "D",
        ),
        (
            (1,),
            (1,),
            (2,),
            (3,),
        ),
    )

    candidate = runner.summarize_signatures(
        (
            "A",
            "B",
            "C",
            "D",
        ),
        (
            (1,),
            (2,),
            (3,),
            (3,),
        ),
    )

    delta = runner.compare_partitions(
        reference,
        candidate,
    )

    assert delta[
        "split_pairs"
    ] == [
        [
            "A",
            "B",
        ]
    ]

    assert delta[
        "introduced_pairs"
    ] == [
        [
            "C",
            "D",
        ]
    ]


def test_expected_collision_status_is_explicit():
    left, right = (
        runner.EXPECTED_COLLISION
    )

    status = runner.expected_pair_status(
        (
            left,
            right,
        ),
        (
            ("same",),
            ("same",),
        ),
    )

    assert status == {
        "present": True,
        "collides": True,
    }


def test_runner_keeps_l1_out_of_applicable_substrates():
    assert "L1" not in runner.SUBSTRATES

    assert (
        runner.s2.NOT_APPLICABLE
        == "not_applicable"
    )


def test_runner_does_not_call_probe_dynamic_temporal_or_oriented_readers():
    source = RUNNER_PATH.read_text(
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
        "ordered_factor_proximity_signature",
        "full_lattice_signature",
        "evolve_euler_numerator",
        "evolve_weighted_euler_numerator",
        "evolve_factor_state",
        "evolve_lattice_numerator",
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


def test_shape_code_is_used_only_after_signature_construction_boundary():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "width4.shape_code(shape)"
        in source
    )

    assert (
        "s2.local_spectrum_signature("
        in source
    )

    assert (
        "s01.exact_operator_spectrum_signature("
        in source
    )
