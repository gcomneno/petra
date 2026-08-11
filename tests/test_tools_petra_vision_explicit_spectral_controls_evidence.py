"""Structural tests for the Gate 3 G3-S0/S1 evidence runner."""

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
    / "petra_vision_explicit_spectral_controls_evidence.py"
)


def _load_runner():
    name = "_petra_vision_gate3_s01_evidence_test"

    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        RUNNER_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-S0/S1 evidence runner"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


runner = _load_runner()


def test_evidence_protocol_identifier_is_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-s0-s1-evidence-v0"
    )

    assert runner.CORPORA == (
        "phase1",
        "heldout",
        "extended",
    )


def test_signature_summary_preserves_exact_collision_groups():
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

    assert summary[
        "distinct_signatures"
    ] == 3

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


def test_partition_delta_reports_splits_and_introductions():
    control = runner.summarize_signatures(
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
        control,
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


def test_expected_collision_is_explicitly_reported():
    left, right = (
        runner.EXPECTED_COLLISION
    )

    status = runner.expected_pair_status(
        (
            left,
            right,
            "OTHER",
        ),
        (
            ("same",),
            ("same",),
            ("different",),
        ),
    )

    assert status == {
        "present": True,
        "collides": True,
    }


def test_expected_collision_absence_is_not_fabricated():
    left, _right = (
        runner.EXPECTED_COLLISION
    )

    status = runner.expected_pair_status(
        (
            left,
            "OTHER",
        ),
        (
            ("x",),
            ("y",),
        ),
    )

    assert status == {
        "present": False,
        "collides": None,
    }


def test_runner_does_not_invoke_probe_impulse_or_temporal_apis():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
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
    }

    tree = ast.parse(source)

    called_names = set()

    for node in ast.walk(tree):
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
            called_names.add(
                function.id
            )

        elif isinstance(
            function,
            ast.Attribute,
        ):
            called_names.add(
                function.attr
            )

    assert not (
        called_names
        & forbidden_calls
    )


def test_runner_uses_shape_code_only_for_evidence_reporting():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "width4.shape_code(shape)"
        in source
    )

    assert (
        "operator_elementary_signature("
        in source
    )

    assert (
        "exact_operator_spectrum_signature("
        in source
    )
