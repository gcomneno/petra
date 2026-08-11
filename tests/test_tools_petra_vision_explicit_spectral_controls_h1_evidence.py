"""Structural tests for the G3-H1 evidence runner without corpus execution."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

RUNNER_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_h1_evidence.py"
)


def _load_runner():
    name = "_petra_vision_gate3_h1_evidence_test_runner"

    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        RUNNER_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "unable to load G3-H1 evidence runner"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


runner = _load_runner()


def test_protocol_and_ladder_are_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-h1-evidence-v0"
    )

    assert runner.h1.TRUNCATIONS == (
        ("M1", 1),
        ("M2", 2),
        ("M4", 4),
        ("M8", 8),
    )


def test_partition_comparison_detects_only_merging():
    codes = (
        "A",
        "B",
        "C",
    )

    fine = runner.summarize_signatures(
        codes,
        (
            ("x",),
            ("y",),
            ("z",),
        ),
    )

    coarse = runner.summarize_signatures(
        codes,
        (
            ("x",),
            ("x",),
            ("z",),
        ),
    )

    comparison = (
        runner.compare_partitions(
            fine,
            coarse,
        )
    )

    assert (
        comparison[
            "split_pair_count"
        ]
        == 0
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
        == -1
    )


def test_compression_guard_rejects_s1_split():
    comparison = {
        "split_pair_count": 1,
    }

    try:
        runner._assert_h1_is_s1_compression(
            comparison,
            substrate="B0",
            truncation="M1",
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "H1 S1-split guard did not fire"
        )


def test_ladder_guard_rejects_lower_order_refinement():
    comparison = {
        "split_pair_count": 1,
    }

    try:
        runner._assert_ladder_refinement(
            comparison,
            substrate="D1",
            lower="M1",
            higher="M2",
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError(
            "H1 ladder guard did not fire"
        )


def test_expected_collision_status():
    left, right = (
        runner.EXPECTED_COLLISION
    )

    codes = (
        left,
        right,
        "other",
    )

    result = runner.expected_pair_status(
        codes,
        (
            ("same",),
            ("same",),
            ("different",),
        ),
    )

    assert result == {
        "present": True,
        "collides": True,
    }


def test_expected_collision_absent_is_explicit():
    result = runner.expected_pair_status(
        ("A", "B"),
        (
            ("x",),
            ("y",),
        ),
    )

    assert result == {
        "present": False,
        "collides": None,
    }


def test_signature_summary_is_deterministic():
    codes = (
        "B",
        "A",
        "C",
    )

    signatures = (
        ("same",),
        ("same",),
        ("other",),
    )

    first = runner.summarize_signatures(
        codes,
        signatures,
    )

    second = runner.summarize_signatures(
        codes,
        signatures,
    )

    assert first == second

    assert first[
        "collision_shape_codes"
    ] == [
        ["A", "B"],
    ]


def test_build_evidence_rejects_unknown_corpus():
    try:
        runner.build_evidence(
            "unknown"
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "unknown corpus accepted"
        )


def test_runner_source_keeps_later_gate_families_inactive():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "petra_vision_explicit_spectral_controls_s2",
        "native_fgs",
        "probe_ablation",
        "impulse_response",
        "temporal_observation",
        "orientation_control",
    )

    for fragment in forbidden:
        assert fragment not in source
