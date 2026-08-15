from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

RUNNER_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_t1_evidence.py"
)


def _load_runner():
    name = "_petra_vision_gate3_t1_evidence_test_subject"

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
            "unable to load T1 evidence runner"
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


def _trajectory(values):
    return tuple(
        ((value, 1),)
        for value in values
    )


def test_runner_protocol_constants_are_frozen():
    assert (
        runner.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-t1-evidence-v0"
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
        "F1",
        "L1",
    )

    assert (
        runner.t1.PROTOCOL_ID
        == "petra-vision-explicit-spectral-controls-t1-v0"
    )


def test_signature_summary_records_exact_collisions():
    codes = (
        "A",
        "B",
        "C",
        "D",
    )

    signatures = (
        (1,),
        (1,),
        (2,),
        (3,),
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
        ],
    ]


def test_partition_comparison_is_directional():
    codes = (
        "A",
        "B",
        "C",
    )

    control = runner.summarize_signatures(
        codes,
        (
            (1,),
            (1,),
            (1,),
        ),
    )

    candidate = runner.summarize_signatures(
        codes,
        (
            (1,),
            (2,),
            (1,),
        ),
    )

    comparison = runner.compare_partitions(
        control,
        candidate,
    )

    assert comparison[
        "distinct_signature_delta"
    ] == 1

    assert comparison[
        "split_pair_count"
    ] == 2

    assert comparison[
        "introduced_pair_count"
    ] == 0


def test_analyze_channel_keeps_digests_and_pair_status():
    codes = (
        runner.EXPECTED_COLLISION[
            0
        ],
        runner.EXPECTED_COLLISION[
            1
        ],
        "X",
    )

    analysis = runner.analyze_channel(
        codes=codes,
        signatures=(
            ("same",),
            ("same",),
            ("other",),
        ),
    )

    assert analysis[
        "expected_collision"
    ] == {
        "present": True,
        "collides": True,
    }

    assert len(
        analysis[
            "signature_digests"
        ]
    ) == 3


def test_reduction_signatures_use_only_declared_projection():
    trajectories = (
        _trajectory((
            1,
            2,
            3,
            4,
            5,
            6,
        )),
        _trajectory((
            2,
            1,
            3,
            4,
            5,
            6,
        )),
    )

    ordered = runner._reduction_signatures(
        trajectories,
        "ordered",
    )

    unordered = runner._reduction_signatures(
        trajectories,
        "unordered",
    )

    assert ordered[
        0
    ] != ordered[
        1
    ]

    assert unordered[
        0
    ] == unordered[
        1
    ]


def test_prefix_signatures_cover_declared_prefix_only():
    trajectory = _trajectory((
        4,
        1,
        3,
        2,
        6,
        5,
    ))

    ordered = runner._prefix_signatures(
        (
            trajectory,
        ),
        unordered=False,
        length=3,
    )

    unordered = runner._prefix_signatures(
        (
            trajectory,
        ),
        unordered=True,
        length=3,
    )

    assert ordered == (
        trajectory[:3],
    )

    assert unordered == (
        tuple(sorted(
            trajectory[:3]
        )),
    )


def test_pair_diagnostics_are_deterministic():
    codes = (
        "A",
        "B",
        "C",
    )

    step_zero = (
        ("z",),
        ("z",),
        ("other",),
    )

    trajectories = (
        _trajectory((
            1,
            2,
            3,
            4,
            5,
            6,
        )),
        _trajectory((
            1,
            2,
            9,
            4,
            5,
            6,
        )),
        _trajectory((
            8,
            8,
            8,
            8,
            8,
            8,
        )),
    )

    diagnostics = runner._pair_diagnostics(
        codes,
        step_zero,
        trajectories,
    )

    assert diagnostics[
        "first_divergence"
    ][
        "step_zero_collision_pair_count"
    ] == 1

    assert diagnostics[
        "first_divergence"
    ][
        "distribution"
    ][
        "4"
    ] == 1

    assert diagnostics[
        "first_divergence"
    ][
        "pairs"
    ][
        "4"
    ] == [
        [
            "A",
            "B",
        ],
    ]


def test_transport_state_reflects_by_cell_identity():
    original_cells = (
        (0, 0),
        (1, 0),
        (2, 0),
    )

    reflected_cells = (
        (0, 0),
        (1, 0),
        (2, 0),
    )

    assert runner._transport_state(
        original_cells,
        reflected_cells,
        (
            1,
            0,
            0,
        ),
    ) == (
        0,
        0,
        1,
    )


def test_write_evidence_is_canonical_and_replayable(
    tmp_path,
):
    evidence = {
        "b": [
            2,
            1,
        ],
        "a": {
            "x": True,
        },
    }

    left = (
        tmp_path
        / "left.json"
    )

    right = (
        tmp_path
        / "right.json"
    )

    left_digest = runner.write_evidence(
        left,
        evidence,
    )

    right_digest = runner.write_evidence(
        right,
        evidence,
    )

    assert left.read_bytes() == right.read_bytes()
    assert left_digest == right_digest


def test_select_corpus_rejects_unknown_without_enumeration():
    with pytest.raises(
        ValueError,
        match="unsupported corpus",
    ):
        runner._select_corpus(
            "unknown"
        )


def test_runner_source_boundary_is_only_t1_plus_width4():
    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    path_strings = {
        node.value
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.Constant,
            )
            and isinstance(
                node.value,
                str,
            )
        )
    }

    forbidden_fragments = (
        "explicit_spectral_controls_p1",
        "explicit_spectral_controls_i1",
        "explicit_spectral_controls_s0",
        "explicit_spectral_controls_s1",
        "explicit_spectral_controls_s2",
        "explicit_spectral_controls_h1",
        "explicit_spectral_controls_o1",
        "_work/",
    )

    for fragment in forbidden_fragments:
        assert not any(
            fragment in value
            for value in path_strings
        )

    assert (
        "petra_vision_explicit_spectral_controls_t1.py"
        in path_strings
    )

    assert (
        "petra_vision_graph_laplacian_width4.py"
        in path_strings
    )


def test_corpus_builders_are_not_called_at_import_time():
    tree = ast.parse(
        RUNNER_PATH.read_text(
            encoding="utf-8"
        )
    )

    module_level_calls = []

    for node in tree.body:
        if isinstance(
            node,
            ast.Expr,
        ) and isinstance(
            node.value,
            ast.Call,
        ):
            module_level_calls.append(
                node.value
            )

    rendered = {
        ast.unparse(
            call
        )
        for call in module_level_calls
    }

    assert not any(
        "phase_1_corpus" in call
        or "held_out_corpus" in call
        or "extended_corpus" in call
        for call in rendered
    )
