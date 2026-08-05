from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import subprocess
import sys
import textwrap
from pathlib import Path

from petra.vision import OrthogonalGeometry

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)


def _load_tool_module():
    spec = importlib.util.spec_from_file_location(
        "petra_vision_graph_laplacian_width4",
        TOOL_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load width-4 graph-Laplacian tool")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tool = _load_tool_module()

EXPECTED_COLLISION = [
    "G(G(G(T)),G(T,T))",
    "G(G(T,T),G(G(T)))",
]
READERS = (
    "null_oriented",
    "global_multiset",
    "component_multiset",
    "oriented",
)


def test_corpus_cardinalities_and_held_out_partition() -> None:
    phase_1 = tool.phase_1_corpus()
    extended = tool.extended_corpus()
    held_out = tool.held_out_corpus()

    assert len(phase_1) == 110
    assert len(extended) == 137
    assert len(held_out) == 27
    assert set(held_out).isdisjoint(phase_1)
    assert set(extended) == set(phase_1) | set(held_out)


def test_experimental_encoder_matches_phase_1_grammar() -> None:
    for shape in tool.phase_1_corpus():
        assert tool.encode_experimental_geometry(shape) == (
            tool.v1.encode_geometry(shape)
        )


def test_extended_geometries_remain_within_declared_budget() -> None:
    for shape in tool.extended_corpus():
        geometry = tool.encode_experimental_geometry(shape)
        width, height = tool.geometry_extent(geometry)

        assert len(geometry.cells) <= 181
        assert width <= 25
        assert height <= 13


def test_held_out_is_distinguished_by_every_reader() -> None:
    readers = tool.analyze_experiment()["held_out"]["readers"]

    for reader in READERS:
        assert readers[reader]["distinct_signatures"] == 27
        assert readers[reader]["collision_shape_codes"] == []


def test_extended_reader_results_and_exact_preexisting_collision() -> None:
    report = tool.analyze_experiment()
    readers = report["extended"]["readers"]

    for reader in ("global_multiset", "component_multiset"):
        assert readers[reader]["distinct_signatures"] == 136
        assert readers[reader]["collision_shape_codes"] == [
            EXPECTED_COLLISION
        ]

    for reader in ("null_oriented", "oriented"):
        assert readers[reader]["distinct_signatures"] == 137
        assert readers[reader]["collision_shape_codes"] == []

    assert report["collision_audit"] == {
        "expected_preexisting_collision_shape_codes": EXPECTED_COLLISION,
        "extended_global_multiset": [EXPECTED_COLLISION],
        "extended_component_multiset": [EXPECTED_COLLISION],
        "no_new_collision_shape_codes": True,
    }


def test_analysis_replays_deterministically() -> None:
    assert tool.analyze_experiment() == tool.analyze_experiment()
    assert tool.analyze_experiment()["deterministic_replay"] is True


def test_json_cli_is_reproducible() -> None:
    command = [sys.executable, str(TOOL_PATH), "--json"]
    first = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert first.stdout == second.stdout
    assert first.stderr == second.stderr == ""
    assert json.loads(first.stdout) == tool.analyze_experiment()


def test_v1_protocol_behavior_remains_frozen() -> None:
    report = tool.v1.analyze_experiment()

    assert report["protocol"]["id"] == "petra-vision-graph-laplacian-v1"
    assert report["protocol"]["euler_denominator"] == 8
    assert report["protocol"]["sample_steps"] == [1, 2, 4, 8, 16, 32]
    assert report["readers"]["global_multiset"][
        "collision_groups"
    ] == [[23, 41]]
    assert report["readers"]["component_multiset"][
        "collision_groups"
    ] == [[23, 41]]
    assert report["readers"]["null_oriented"][
        "distinct_signatures"
    ] == 110
    assert report["readers"]["oriented"]["distinct_signatures"] == 110


def test_held_out_translation_invariance_for_all_readers() -> None:
    for shape in tool.held_out_corpus():
        geometry = tool.encode_experimental_geometry(shape)
        translated = OrthogonalGeometry(cells=tuple(sorted(
            (x + 17, y + 23)
            for x, y in geometry.cells
        )))

        assert tool.experimental_geometry_dynamic_signatures(
            translated
        ) == tool.experimental_geometry_dynamic_signatures(geometry)


def test_experimental_dynamic_core_has_no_identity_channel() -> None:
    core_functions = (
        tool.experimental_geometry_dynamic_signatures,
        tool.v1.build_geometry_graph,
        tool.v1.canonical_component_probe,
        tool.v1.probe_state,
        tool.v1.evolve_euler_numerator,
        tool.v1.dynamic_signatures_from_probe,
        tool.v1.geometry_dynamic_signatures,
    )
    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "encode_geometry",
        "decode_geometry",
        "shape_code",
        "structural_profile",
        "validate_vision_shape",
        "serialize",
        "address",
        "metadata",
    }

    for function in core_functions:
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
        loaded_names = {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
        }

        assert loaded_names.isdisjoint(forbidden_names), (
            function.__name__,
            sorted(loaded_names & forbidden_names),
        )

def test_cli_success_requires_the_expected_scientific_result(
    monkeypatch,
) -> None:
    original = tool.analyze_experiment()

    broken = dict(original)
    broken["deterministic_replay"] = False

    monkeypatch.setattr(
        tool,
        "analyze_experiment",
        lambda: broken,
    )

    assert tool.main([]) == 1
