from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)


def _load_tool_module():
    spec = importlib.util.spec_from_file_location(
        "petra_vision_graph_laplacian",
        TOOL_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load graph-Laplacian tool")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tool = _load_tool_module()


def test_primary_protocol_reproduces_bounded_evidence() -> None:
    report = tool.analyze_experiment()

    assert report["protocol"]["id"] == (
        "petra-vision-graph-laplacian-v1"
    )
    assert report["corpus"] == {
        "size": 110,
        "maximum_degree": 3,
        "minimum_components": 1,
        "maximum_components": 7,
    }
    assert report["deterministic_replay"] is True

    readers = report["readers"]

    assert readers["null_oriented"]["distinct_signatures"] == 110
    assert readers["null_oriented"]["collision_groups"] == []

    assert readers["global_multiset"]["distinct_signatures"] == 109
    assert readers["global_multiset"]["collision_groups"] == [
        [23, 41]
    ]

    assert (
        readers["component_multiset"]["distinct_signatures"]
        == 109
    )
    assert readers["component_multiset"]["collision_groups"] == [
        [23, 41]
    ]

    assert readers["oriented"]["distinct_signatures"] == 110
    assert readers["oriented"]["collision_groups"] == []


def test_geometry_graph_controls_match_bounded_structure() -> None:
    controls = tool.analyze_experiment()[
        "structural_controls"
    ]

    assert controls == {
        "components_equal_structural_nodes": 110,
        "isolated_vertices_equal_terminals": 110,
        "component_cycle_ranks_equal_local_arities": 110,
    }


def test_primary_collision_is_a_reflected_component_reordering() -> None:
    collision = tool.analyze_experiment()["primary_collision"]

    assert collision == {
        "indices": [23, 41],
        "geometries_identical": False,
        "horizontal_reflections": True,
        "same_normalized_component_multiset": True,
    }


def test_json_cli_contract() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(TOOL_PATH),
            "--json",
        ],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    report = json.loads(completed.stdout)

    assert report["corpus"]["size"] == 110
    assert report["readers"]["global_multiset"][
        "collision_groups"
    ] == [[23, 41]]
    assert completed.stderr == ""

def test_all_readers_are_translation_invariant() -> None:
    from petra.vision import OrthogonalGeometry, encode_geometry

    readers = (
        "null_oriented",
        "global_multiset",
        "component_multiset",
        "oriented",
    )

    for shape in tool.bounded_phase_1_corpus():
        geometry = encode_geometry(shape)

        translated = OrthogonalGeometry(
            cells=tuple(sorted(
                (x + 17, y + 23)
                for x, y in geometry.cells
            ))
        )

        original = tool.geometry_dynamic_signatures(geometry)
        shifted = tool.geometry_dynamic_signatures(translated)

        for reader in readers:
            assert shifted[reader] == original[reader]


def test_dynamic_core_has_no_structural_identity_channel() -> None:
    import ast
    import inspect

    core_functions = (
        tool.build_geometry_graph,
        tool.canonical_component_probe,
        tool.probe_state,
        tool.evolve_euler_numerator,
        tool.dynamic_signatures_from_probe,
        tool.geometry_dynamic_signatures,
    )

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "encode_geometry",
        "decode_geometry",
        "adapt_petra_shape",
        "restore_petra_shape",
        "shape_code",
        "structural_profile",
        "bounded_phase_1_corpus",
    }

    for function in core_functions:
        tree = ast.parse(
            inspect.getsource(function)
        )

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

def test_probe_sensitivity_controls_are_reproduced() -> None:
    probes = tool.analyze_experiment()["probe_sensitivity"]

    assert probes["minimum"]["global_multiset"][
        "distinct_signatures"
    ] == 109
    assert probes["minimum"]["global_multiset"][
        "collision_groups"
    ] == [[23, 41]]

    assert probes["maximum"]["global_multiset"][
        "distinct_signatures"
    ] == 109
    assert probes["maximum"]["global_multiset"][
        "collision_groups"
    ] == [[23, 41]]

    assert probes["endpoints"]["global_multiset"][
        "distinct_signatures"
    ] == 62

    assert probes["zero"]["global_multiset"][
        "distinct_signatures"
    ] == 29
    assert probes["zero"]["component_multiset"][
        "distinct_signatures"
    ] == 47

    assert probes["constant"]["global_multiset"][
        "distinct_signatures"
    ] == 29
    assert probes["constant"]["component_multiset"][
        "distinct_signatures"
    ] == 47


def test_temporal_sensitivity_controls_are_reproduced() -> None:
    temporal = tool.analyze_experiment()[
        "temporal_sensitivity"
    ]

    for probe_name in ("minimum", "maximum"):
        for denominator in ("4", "8", "16"):
            controls = temporal[probe_name][denominator]

            assert controls["early"][
                "distinct_signatures"
            ] == 71
            assert controls["early"][
                "collision_group_count"
            ] == 26

            for schedule in (
                "final_32",
                "sparse",
                "primary",
                "extended",
            ):
                assert controls[schedule][
                    "distinct_signatures"
                ] == 109
                assert controls[schedule][
                    "collision_groups"
                ] == [[23, 41]]



def test_text_report_keeps_probe_controls_compact() -> None:
    report = tool.analyze_experiment()
    rendered = tool.render_text_report(report)
    lines = rendered.splitlines()

    probe_lines = [
        line
        for line in lines
        if line.lstrip().startswith((
            "zero",
            "minimum",
            "maximum",
            "endpoints",
            "constant",
        ))
    ]

    assert len(probe_lines) == 5
    assert all(len(line) < 150 for line in probe_lines)
    assert all("gruppi=" in line for line in probe_lines)
    assert all("forme=" in line for line in probe_lines)

    assert report["probe_sensitivity"]["zero"][
        "global_multiset"
    ]["collision_group_count"] == 22


def test_local_mutation_sensitivity_is_reproduced() -> None:
    result = tool.analyze_experiment()[
        "local_mutation_sensitivity"
    ]

    assert result["valid_pair_count"] == 99
    assert result["detected_pair_count"] == 99
    assert result["undetected_pair_count"] == 0
    assert result["mutable_source_count"] == 45
    assert result["reached_target_count"] == 74
    assert result["undetected_pairs"] == []

    assert result["detected_pairs"][:4] == [
        [2, 0],
        [5, 4],
        [16, 12],
        [16, 15],
    ]


def test_elementary_statistics_control_is_reproduced() -> None:
    result = tool.analyze_experiment()[
        "elementary_statistics_control"
    ]

    assert result["shared_group_count"] == 28
    assert result["involved_shape_count"] == 96
    assert result["comparable_pair_count"] == 165
    assert result["detected_pair_count"] == 164
    assert result["undetected_pair_count"] == 1
    assert result["undetected_pairs"] == [[23, 41]]

    assert result["first_detected_pairs"][:4] == [
        [0, 11],
        [1, 30],
        [1, 73],
        [1, 84],
    ]
