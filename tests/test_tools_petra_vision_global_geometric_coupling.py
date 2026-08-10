"""Gate 2 contract tests for global geometric coupling D1."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest

from petra.vision.geometry import OrthogonalGeometry


ROOT = Path(__file__).resolve().parents[1]

BASELINE_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)

D1_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling.py"
)


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load research module: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


def _load_baseline_module() -> ModuleType:
    assert BASELINE_MODULE_PATH.is_file()
    return _load_module(
        BASELINE_MODULE_PATH,
        "_petra_vision_graph_laplacian_gate2_baseline",
    )


def _load_d1_module() -> ModuleType:
    if not D1_MODULE_PATH.is_file():
        pytest.fail(
            "Gate 2 D1 research module is not implemented yet",
            pytrace=False,
        )

    return _load_module(
        D1_MODULE_PATH,
        "_petra_vision_global_geometric_coupling_d1",
    )


def _geometry(
    *cells: tuple[int, int],
) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(cells))
    )


def _translate(
    geometry: OrthogonalGeometry,
    *,
    dx: int,
    dy: int,
) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(
            (x + dx, y + dy)
            for x, y in geometry.cells
        ))
    )


def test_frozen_b0_protocol_is_still_graph_laplacian_v1() -> None:
    module = _load_baseline_module()

    assert module.PROTOCOL_ID == "petra-vision-graph-laplacian-v1"
    assert module.EULER_DENOMINATOR == 8
    assert module.SAMPLE_STEPS == (1, 2, 4, 8, 16, 32)


def test_d1_protocol_constants_are_frozen_before_results() -> None:
    module = _load_d1_module()

    assert (
        module.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-distance2-v0"
    )
    assert module.LOCAL_WEIGHT == 2
    assert module.BRIDGE_WEIGHT == 1
    assert module.EULER_DENOMINATOR == 16
    assert module.SAMPLE_STEPS == (1, 2, 4, 8, 16, 32)
    assert module.MAX_WEIGHTED_DEGREE_BOUND == 12


def test_d1_graph_contains_only_declared_local_and_clearance_edges() -> None:
    module = _load_d1_module()

    geometry = _geometry(
        (0, 0),
        (1, 0),
        (1, 1),
        (2, 2),
        (3, 0),
        (5, 0),
    )

    graph = module.build_distance2_graph(geometry)

    assert module.edge_manifest(graph) == (
        ((0, 0), (1, 0), 2, "local"),
        ((1, 0), (1, 1), 2, "local"),
        ((1, 0), (3, 0), 1, "bridge"),
        ((3, 0), (5, 0), 1, "bridge"),
    )

    assert module.maximum_weighted_degree(graph) <= 12


def test_d1_does_not_bridge_across_occupied_midpoint_or_diagonal() -> None:
    module = _load_d1_module()

    geometry = _geometry(
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 1),
    )

    graph = module.build_distance2_graph(geometry)

    manifest = module.edge_manifest(graph)

    assert ((0, 0), (2, 0), 1, "bridge") not in manifest
    assert ((1, 0), (3, 1), 1, "bridge") not in manifest

    assert manifest == (
        ((0, 0), (1, 0), 2, "local"),
        ((1, 0), (2, 0), 2, "local"),
    )


def test_d1_matched_null_changes_only_bridge_weight() -> None:
    module = _load_d1_module()

    geometry = _geometry(
        (0, 0),
        (1, 0),
        (3, 0),
    )

    coupled = module.build_distance2_graph(
        geometry,
        bridge_weight=module.BRIDGE_WEIGHT,
    )
    null = module.build_distance2_graph(
        geometry,
        bridge_weight=0,
    )

    assert module.edge_manifest(coupled) == (
        ((0, 0), (1, 0), 2, "local"),
        ((1, 0), (3, 0), 1, "bridge"),
    )

    assert module.edge_manifest(null) == (
        ((0, 0), (1, 0), 2, "local"),
        ((1, 0), (3, 0), 0, "bridge"),
    )

    assert coupled.cells == null.cells
    assert coupled.original_components == null.original_components


def test_d1_weighted_euler_uses_exact_declared_integer_update() -> None:
    module = _load_d1_module()

    local = module.build_distance2_graph(
        _geometry(
            (0, 0),
            (1, 0),
        )
    )

    assert module.evolve_weighted_euler_numerator(
        (1, 0),
        local,
    ) == (14, 2)

    bridge = module.build_distance2_graph(
        _geometry(
            (0, 0),
            (2, 0),
        )
    )

    assert module.evolve_weighted_euler_numerator(
        (1, 0),
        bridge,
    ) == (15, 1)

    bridge_null = module.build_distance2_graph(
        _geometry(
            (0, 0),
            (2, 0),
        ),
        bridge_weight=0,
    )

    assert module.evolve_weighted_euler_numerator(
        (1, 0),
        bridge_null,
    ) == (16, 0)


def test_d1_coordinate_free_signature_is_translation_invariant() -> None:
    module = _load_d1_module()

    source = _geometry(
        (0, 0),
        (0, 1),
        (2, 0),
        (2, 1),
    )

    translated = _translate(
        source,
        dx=11,
        dy=7,
    )

    source_graph = module.build_distance2_graph(source)
    translated_graph = module.build_distance2_graph(translated)

    source_probe = module.original_component_probe(source_graph)
    translated_probe = module.original_component_probe(
        translated_graph
    )

    assert module.coordinate_free_dynamic_signature(
        source_graph,
        source_probe,
    ) == module.coordinate_free_dynamic_signature(
        translated_graph,
        translated_probe,
    )


def test_d1_source_boundary_is_geometry_only() -> None:
    module = _load_d1_module()

    tree = ast.parse(
        D1_MODULE_PATH.read_text(encoding="utf-8")
    )

    petra_imports = {
        node.module
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("petra")
        )
    }

    assert petra_imports == {
        "petra.vision.geometry",
    }

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "native_fgs",
        "recompose_fgs",
        "shape_code",
        "resolve_address",
        "serialize_shape",
        "adapt_petra_shape",
        "restore_petra_shape",
    }

    referenced_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    assert referenced_names.isdisjoint(forbidden_names)

    assert module.PROTOCOL_ID.endswith("distance2-v0")


def test_gate2_d1_evidence_contract_and_frozen_baseline() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_evidence_test",
    )

    report = evidence.analyze_evidence()

    assert (
        report["protocol"]["id"]
        == "petra-vision-global-geometric-coupling-distance2-evidence-v0"
    )

    assert report["frozen_b0_replay"][
        "matches_frozen_expectation"
    ]

    assert report["phase_1_encoder_continuity"] == {
        "matches": 110,
        "total": 110,
        "exact": True,
    }

    assert report["corpora"]["phase_1"]["size"] == 110
    assert report["corpora"]["held_out"]["size"] == 27
    assert report["corpora"]["extended"]["size"] == 137

    assert report["d1_source_boundary_audit"]["passed"]
    assert report["translation_control"]
    assert report["weighted_degree_bound"]
    assert report["deterministic_replay"]

    for corpus_name in (
        "phase_1",
        "held_out",
        "extended",
    ):
        corpus = report[corpus_name]

        assert "d1_matched_null" in corpus["readers"]
        assert "d1_coupled" in corpus["readers"]
        assert "incremental_vs_null" in corpus
        assert "known_gate1a_collision" in corpus

    # Deliberately no expected D1 distinct-signature count:
    # the first evidence replay must be allowed to report
    # a positive, neutral, or negative scientific result.


def test_gate2_d1_reflection_causality_is_explicit() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_causality_test",
    )

    audit = evidence._reflection_causality_audit()

    assert audit["passed"]
    assert audit["exact_geometry_reflection"]
    assert audit["coupled_graph_reflection_equivariant"]
    assert audit["matched_null_reflection_equivariant"]
    assert audit[
        "original_component_partition_reflection_equivariant"
    ]

    assert audit[
        "frozen_probe_reflection_equivariant"
    ] == {
        "minimum": False,
        "maximum": False,
        "endpoints": False,
    }

    assert audit[
        "transported_minimum_probe_signature_matches"
    ] == {
        "null": True,
        "coupled": True,
    }

    assert audit[
        "independent_minimum_probe_signature_matches"
    ] == {
        "null": True,
        "coupled": False,
    }

    assert audit[
        "first_coupled_minimum_multiset_divergence_step"
    ] == 2

    assert audit[
        "intrinsic_local_degree_probe_reflection_equivariant"
    ]
    assert audit[
        "intrinsic_local_degree_coupled_signatures_match"
    ]

F0_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f0.py"
)


def _load_f0_module() -> ModuleType:
    if not F0_MODULE_PATH.is_file():
        pytest.fail(
            "Gate 2 F0 research module is not implemented yet",
            pytrace=False,
        )

    return _load_module(
        F0_MODULE_PATH,
        "_petra_vision_global_geometric_coupling_f0",
    )


def test_f0_protocol_is_frozen_before_results() -> None:
    module = _load_f0_module()

    assert (
        module.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-fgs-null-v0"
    )
    assert (
        module.DYNAMIC_PROTOCOL_ID
        == "petra-vision-graph-laplacian-v1"
    )
    assert module.READER_ID == "unordered-factor-global-multiset"


def test_f0_terminal_has_empty_immediate_factor_multiset() -> None:
    module = _load_f0_module()

    terminal = _geometry((0, 0))

    assert module.factor_multiset_signature(
        terminal
    ) == ()


def test_f0_discards_factor_order_but_preserves_multiplicity() -> None:
    module = _load_f0_module()

    from petra.vision import (
        OrderedGroup,
        Terminal,
        encode_geometry,
    )

    unary = OrderedGroup(
        children=(Terminal(),)
    )
    binary = OrderedGroup(
        children=(Terminal(), Terminal())
    )

    left_right = encode_geometry(
        OrderedGroup(
            children=(unary, binary)
        )
    )
    right_left = encode_geometry(
        OrderedGroup(
            children=(binary, unary)
        )
    )

    signature_ab = module.factor_multiset_signature(
        left_right
    )
    signature_ba = module.factor_multiset_signature(
        right_left
    )

    assert signature_ab == signature_ba
    assert len(signature_ab) == 2

    repeated = encode_geometry(
        OrderedGroup(
            children=(unary, unary)
        )
    )

    repeated_signature = (
        module.factor_multiset_signature(
            repeated
        )
    )

    assert len(repeated_signature) == 2
    assert (
        repeated_signature[0]
        == repeated_signature[1]
    )


def test_f0_matches_independent_native_fgs_v1_factor_observation() -> None:
    module = _load_f0_module()

    from petra.vision import (
        OrderedGroup,
        Terminal,
        encode_geometry,
    )

    fgs_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_structural_geometric_factorization.py"
    )
    v1_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_graph_laplacian.py"
    )

    fgs = _load_module(
        fgs_path,
        "_petra_vision_f0_expected_fgs",
    )
    v1 = _load_module(
        v1_path,
        "_petra_vision_f0_expected_v1",
    )

    shape = OrderedGroup(
        children=(
            OrderedGroup(
                children=(Terminal(),)
            ),
            OrderedGroup(
                children=(
                    Terminal(),
                    Terminal(),
                )
            ),
        )
    )

    geometry = encode_geometry(shape)
    factors = fgs.native_fgs(geometry)

    expected = tuple(sorted(
        v1.geometry_dynamic_signatures(
            factor
        )["global_multiset"]
        for factor in factors
    ))

    assert module.factor_multiset_signature(
        geometry
    ) == expected


def test_f0_preserves_known_reflected_reordering_collision() -> None:
    module = _load_f0_module()

    width4_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_graph_laplacian_width4.py"
    )

    width4 = _load_module(
        width4_path,
        "_petra_vision_f0_width4_control",
    )

    codes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a = "G(G(G(T)),G(T,T))"
    code_b = "G(G(T,T),G(G(T)))"

    geometry_a = (
        width4.encode_experimental_geometry(
            codes[code_a]
        )
    )
    geometry_b = (
        width4.encode_experimental_geometry(
            codes[code_b]
        )
    )

    assert module.factor_multiset_signature(
        geometry_a
    ) == module.factor_multiset_signature(
        geometry_b
    )



def test_f0_evidence_boundary_and_reflected_control() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_f0_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_f0_evidence_test",
    )

    report = evidence.analyze_evidence()

    assert (
        report["protocol"]["id"]
        == "petra-vision-global-geometric-coupling-fgs-null-evidence-v0"
    )

    assert (
        report["protocol"]["f0_protocol"]
        == "petra-vision-global-geometric-coupling-fgs-null-v0"
    )

    assert (
        report["protocol"]["dynamic_protocol"]
        == "petra-vision-graph-laplacian-v1"
    )

    assert report["corpora"]["phase_1"]["size"] == 110
    assert report["corpora"]["held_out"]["size"] == 27
    assert report["corpora"]["extended"]["size"] == 137

    assert report["frozen_b0_replay"][
        "matches_frozen_expectation"
    ]

    assert report["source_boundary_audit"]["passed"]
    assert report["exact_recomposition"]
    assert report["multiplicity_preserved"]
    assert report["known_reflected_pair_preserved"]
    assert report["deterministic_replay"]

    assert report["phase_1"][
        "known_gate1a_collision"
    ]["f0_unordered_factor_dynamic"][
        "collides"
    ]

    assert report["extended"][
        "known_gate1a_collision"
    ]["f0_unordered_factor_dynamic"][
        "collides"
    ]

    # Deliberately no expected F0 corpus discrimination count.
    # The first replay must be free to report the actual control result.


F1_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f1.py"
)


def _load_f1_module() -> ModuleType:
    if not F1_MODULE_PATH.is_file():
        pytest.fail(
            "Gate 2 F1 research module is not implemented yet",
            pytrace=False,
        )

    return _load_module(
        F1_MODULE_PATH,
        "_petra_vision_global_geometric_coupling_f1",
    )


def test_f1_protocol_is_frozen_before_results() -> None:
    module = _load_f1_module()

    assert (
        module.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-fgs-proximity-v0"
    )

    assert module.WEIGHT_LAW == "inverse-min-manhattan"

    assert module.FEATURE_CHANNELS == (
        "vertices",
        "edges",
        "components",
        "isolated_vertices",
        "total_cycle_rank",
        "maximum_degree",
    )

    assert module.SAMPLE_STEPS == (
        1,
        2,
        4,
        8,
        16,
        32,
    )


def test_f1_terminal_and_single_factor_have_no_interfactor_effect() -> None:
    module = _load_f1_module()

    from petra.vision import (
        OrderedGroup,
        Terminal,
        encode_geometry,
    )

    terminal = encode_geometry(Terminal())

    assert module.factor_proximity_signature(
        terminal,
        coupled=False,
    ) == ()

    assert module.factor_proximity_signature(
        terminal,
        coupled=True,
    ) == ()

    unary = encode_geometry(
        OrderedGroup(
            children=(Terminal(),)
        )
    )

    assert module.factor_proximity_signature(
        unary,
        coupled=False,
    ) == module.factor_proximity_signature(
        unary,
        coupled=True,
    )


def test_f1_factor_proximity_weights_are_exact_inverse_distances() -> None:
    module = _load_f1_module()

    from fractions import Fraction

    from petra.vision import (
        OrderedGroup,
        Terminal,
        encode_geometry,
    )

    geometry = encode_geometry(
        OrderedGroup(
            children=(
                Terminal(),
                Terminal(),
                Terminal(),
            )
        )
    )

    graph = module.build_factor_proximity_graph(
        geometry
    )

    assert len(graph.factors) == 3

    assert graph.distances == (
        (0, 4, 8),
        (4, 0, 4),
        (8, 4, 0),
    )

    assert graph.weights == (
        (
            Fraction(0, 1),
            Fraction(1, 4),
            Fraction(1, 8),
        ),
        (
            Fraction(1, 4),
            Fraction(0, 1),
            Fraction(1, 4),
        ),
        (
            Fraction(1, 8),
            Fraction(1, 4),
            Fraction(0, 1),
        ),
    )


def test_f1_reflected_pair_remains_coordinate_free_collision() -> None:
    module = _load_f1_module()

    width4_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_graph_laplacian_width4.py"
    )

    width4 = _load_module(
        width4_path,
        "_petra_vision_f1_width4_control",
    )

    shapes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a = "G(G(G(T)),G(T,T))"
    code_b = "G(G(T,T),G(G(T)))"

    geometry_a = width4.encode_experimental_geometry(
        shapes[code_a]
    )
    geometry_b = width4.encode_experimental_geometry(
        shapes[code_b]
    )

    assert module.factor_proximity_signature(
        geometry_a,
        coupled=False,
    ) == module.factor_proximity_signature(
        geometry_b,
        coupled=False,
    )

    assert module.factor_proximity_signature(
        geometry_a,
        coupled=True,
    ) == module.factor_proximity_signature(
        geometry_b,
        coupled=True,
    )

    assert module.joint_f0_f1_signature(
        geometry_a,
        coupled=True,
    ) == module.joint_f0_f1_signature(
        geometry_b,
        coupled=True,
    )


def test_f1_joint_signature_retains_frozen_f0_channel() -> None:
    module = _load_f1_module()

    f0_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_f0.py"
    )

    f0 = _load_module(
        f0_path,
        "_petra_vision_f1_expected_f0",
    )

    from petra.vision import (
        OrderedGroup,
        Terminal,
        encode_geometry,
    )

    geometry = encode_geometry(
        OrderedGroup(
            children=(
                OrderedGroup(
                    children=(Terminal(),)
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

    null_joint = module.joint_f0_f1_signature(
        geometry,
        coupled=False,
    )

    coupled_joint = module.joint_f0_f1_signature(
        geometry,
        coupled=True,
    )

    assert null_joint[0] == (
        f0.factor_multiset_signature(
            geometry
        )
    )

    assert coupled_joint[0] == null_joint[0]


def test_f1_source_boundary_excludes_structural_identity_channels() -> None:
    module = _load_f1_module()

    tree = ast.parse(
        F1_MODULE_PATH.read_text(
            encoding="utf-8"
        )
    )

    petra_imports = {
        node.module
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("petra")
        )
    }

    assert petra_imports == {
        "petra.vision.geometry",
    }

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "shape_code",
        "resolve_address",
        "serialize_shape",
        "adapt_petra_shape",
        "restore_petra_shape",
    }

    referenced_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    assert referenced_names.isdisjoint(
        forbidden_names
    )

    assert module.PROTOCOL_ID.endswith(
        "fgs-proximity-v0"
    )


def test_f1_evidence_boundary_and_symmetry_control() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_f1_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_f1_evidence_test",
    )

    report = evidence.analyze_evidence()

    assert (
        report["protocol"]["id"]
        == "petra-vision-global-geometric-coupling-fgs-proximity-evidence-v0"
    )

    assert (
        report["protocol"]["f1_protocol"]
        == "petra-vision-global-geometric-coupling-fgs-proximity-v0"
    )

    assert report["corpora"]["phase_1"]["size"] == 110
    assert report["corpora"]["held_out"]["size"] == 27
    assert report["corpora"]["extended"]["size"] == 137

    assert report["source_boundary_audit"]["passed"]
    assert report["reflection_audit"]["passed"]
    assert report["exact_recomposition"]
    assert report["deterministic_replay"]
    assert report["known_reflected_pair_preserved"]

    reflection = report["reflection_audit"]

    assert reflection["distances_equivariant"]
    assert reflection["weights_equivariant"]
    assert reflection[
        "intrinsic_features_equivariant"
    ]
    assert reflection["f1_null_match"]
    assert reflection["f1_coupled_match"]
    assert reflection["joint_null_match"]
    assert reflection["joint_coupled_match"]

    for corpus_name in (
        "phase_1",
        "held_out",
        "extended",
    ):
        readers = report[
            corpus_name
        ]["readers"]

        assert "f0_unordered_dynamic" in readers
        assert "f1_matched_null" in readers
        assert "f1_coupled" in readers
        assert "joint_f0_f1_null" in readers
        assert "joint_f0_f1_coupled" in readers

    # Deliberately no expected F1 or joint discrimination counts.
    # The first replay must report the actual scientific outcome.


L1_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_l1.py"
)


def _load_l1_module() -> ModuleType:
    if not L1_MODULE_PATH.is_file():
        pytest.fail(
            "Gate 2 L1 research module is not implemented yet",
            pytrace=False,
        )

    return _load_module(
        L1_MODULE_PATH,
        "_petra_vision_global_geometric_coupling_l1",
    )


def test_l1_protocol_is_frozen_before_results() -> None:
    module = _load_l1_module()

    assert (
        module.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-full-lattice-v0"
    )
    assert module.EULER_DENOMINATOR == 8
    assert module.MAXIMUM_DEGREE_BOUND == 4
    assert module.SAMPLE_STEPS == (
        1,
        2,
        4,
        8,
        16,
        32,
    )


def test_l1_domain_is_exact_minimal_bounding_rectangle() -> None:
    module = _load_l1_module()

    geometry = _geometry(
        (3, 4),
        (5, 5),
    )

    graph = module.build_full_lattice_graph(
        geometry
    )

    assert graph.cells == (
        (3, 4),
        (3, 5),
        (4, 4),
        (4, 5),
        (5, 4),
        (5, 5),
    )

    assert graph.initial_state == (
        1,
        0,
        0,
        0,
        0,
        1,
    )

    assert len(graph.edges) == 7
    assert module.maximum_degree(graph) == 3


def test_l1_uses_only_uniform_four_neighbor_edges() -> None:
    module = _load_l1_module()

    graph = module.build_full_lattice_graph(
        _geometry(
            (0, 0),
            (2, 1),
        )
    )

    manifest = module.edge_manifest(graph)

    assert all(
        weight == 1
        for _left, _right, weight
        in manifest
    )

    assert all(
        (
            abs(left[0] - right[0])
            + abs(left[1] - right[1])
        ) == 1
        for left, right, _weight
        in manifest
    )

    assert len(manifest) == 7


def test_l1_matched_null_changes_only_propagation() -> None:
    module = _load_l1_module()

    geometry = _geometry(
        (0, 0),
        (2, 0),
    )

    coupled = module.build_full_lattice_graph(
        geometry,
        coupled=True,
    )
    null = module.build_full_lattice_graph(
        geometry,
        coupled=False,
    )

    assert coupled.cells == null.cells
    assert coupled.initial_state == null.initial_state

    assert module.edge_manifest(coupled) == (
        ((0, 0), (1, 0), 1),
        ((1, 0), (2, 0), 1),
    )

    assert module.edge_manifest(null) == (
        ((0, 0), (1, 0), 0),
        ((1, 0), (2, 0), 0),
    )

    assert module.evolve_lattice_numerator(
        coupled.initial_state,
        coupled,
    ) == (
        7,
        2,
        7,
    )

    assert module.evolve_lattice_numerator(
        null.initial_state,
        null,
    ) == (
        8,
        0,
        8,
    )


def test_l1_signature_is_translation_invariant() -> None:
    module = _load_l1_module()

    source = _geometry(
        (0, 0),
        (0, 2),
        (2, 1),
    )

    translated = _translate(
        source,
        dx=17,
        dy=9,
    )

    assert module.full_lattice_signature(
        source,
        coupled=False,
    ) == module.full_lattice_signature(
        translated,
        coupled=False,
    )

    assert module.full_lattice_signature(
        source,
        coupled=True,
    ) == module.full_lattice_signature(
        translated,
        coupled=True,
    )


def test_l1_reflected_pair_remains_coordinate_free_collision() -> None:
    module = _load_l1_module()

    width4_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_graph_laplacian_width4.py"
    )

    width4 = _load_module(
        width4_path,
        "_petra_vision_l1_width4_control",
    )

    shapes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a = "G(G(G(T)),G(T,T))"
    code_b = "G(G(T,T),G(G(T)))"

    geometry_a = width4.encode_experimental_geometry(
        shapes[code_a]
    )
    geometry_b = width4.encode_experimental_geometry(
        shapes[code_b]
    )

    assert module.full_lattice_signature(
        geometry_a,
        coupled=False,
    ) == module.full_lattice_signature(
        geometry_b,
        coupled=False,
    )

    assert module.full_lattice_signature(
        geometry_a,
        coupled=True,
    ) == module.full_lattice_signature(
        geometry_b,
        coupled=True,
    )


def test_l1_source_boundary_is_geometry_only() -> None:
    module = _load_l1_module()

    tree = ast.parse(
        L1_MODULE_PATH.read_text(
            encoding="utf-8"
        )
    )

    petra_imports = {
        node.module
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("petra")
        )
    }

    assert petra_imports == {
        "petra.vision.geometry",
    }

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "native_fgs",
        "recompose_fgs",
        "shape_code",
        "resolve_address",
        "serialize_shape",
        "adapt_petra_shape",
        "restore_petra_shape",
    }

    referenced_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    assert referenced_names.isdisjoint(
        forbidden_names
    )

    assert module.PROTOCOL_ID.endswith(
        "full-lattice-v0"
    )


def test_l1_evidence_boundary_and_symmetry_controls() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_l1_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_l1_evidence_test",
    )

    report = evidence.analyze_evidence()

    assert (
        report["protocol"]["id"]
        == "petra-vision-global-geometric-coupling-full-lattice-evidence-v0"
    )

    assert (
        report["protocol"]["l1_protocol"]
        == "petra-vision-global-geometric-coupling-full-lattice-v0"
    )

    assert report["corpora"]["phase_1"]["size"] == 110
    assert report["corpora"]["held_out"]["size"] == 27
    assert report["corpora"]["extended"]["size"] == 137

    assert report["source_boundary_audit"]["passed"]
    assert report["translation_audit"]["passed"]
    assert report["reflection_audit"]["passed"]
    assert report["degree_bound_passed"]
    assert report["null_equals_static_partition"]
    assert report["deterministic_replay"]
    assert report["known_reflected_pair_preserved"]

    assert (
        report["translation_audit"]["null_matches"]
        == 110
    )
    assert (
        report["translation_audit"]["coupled_matches"]
        == 110
    )

    assert report["reflection_audit"]["null_match"]
    assert report["reflection_audit"]["coupled_match"]

    for corpus_name in (
        "phase_1",
        "held_out",
        "extended",
    ):
        readers = report[
            corpus_name
        ]["readers"]

        assert "step0_static_multiset" in readers
        assert "l1_matched_null" in readers
        assert "l1_coupled" in readers

    # Deliberately no expected L1 discrimination count.
    # The first replay reports the actual scientific result.


E1_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_e1.py"
)


def _load_e1_module() -> ModuleType:
    if not E1_MODULE_PATH.is_file():
        pytest.fail(
            "Gate 2 E1 research module is not implemented yet",
            pytrace=False,
        )

    return _load_module(
        E1_MODULE_PATH,
        "_petra_vision_global_geometric_coupling_e1",
    )


def test_e1_protocol_is_frozen_before_results() -> None:
    module = _load_e1_module()

    assert (
        module.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-occupied-empty-field-v0"
    )
    assert (
        module.EDGE_WEIGHT_RULE
        == "1+occupancy(u)+occupancy(v)"
    )
    assert module.EULER_DENOMINATOR == 16
    assert module.MAXIMUM_EDGE_WEIGHT == 3
    assert module.MAXIMUM_WEIGHTED_DEGREE_BOUND == 12
    assert module.SAMPLE_STEPS == (
        1,
        2,
        4,
        8,
        16,
        32,
    )


def test_e1_domain_and_initial_field_match_full_lattice_definition() -> None:
    module = _load_e1_module()

    geometry = _geometry(
        (3, 4),
        (5, 5),
    )

    graph = module.build_occupied_empty_field_graph(
        geometry,
        heterogeneous=True,
    )

    assert graph.cells == (
        (3, 4),
        (3, 5),
        (4, 4),
        (4, 5),
        (5, 4),
        (5, 5),
    )

    assert graph.material == (
        1,
        0,
        0,
        0,
        0,
        1,
    )

    assert graph.initial_state == graph.material


def test_e1_edge_law_covers_all_material_pair_types() -> None:
    module = _load_e1_module()

    occupied_pair = (
        module.build_occupied_empty_field_graph(
            _geometry(
                (0, 0),
                (1, 0),
                (3, 0),
            ),
            heterogeneous=True,
        )
    )

    manifest = module.edge_manifest(
        occupied_pair
    )

    assert (
        ((0, 0), (1, 0), 3)
        in manifest
    )
    assert (
        ((1, 0), (2, 0), 2)
        in manifest
    )
    assert (
        ((2, 0), (3, 0), 2)
        in manifest
    )

    empty_pair = (
        module.build_occupied_empty_field_graph(
            _geometry(
                (0, 0),
                (3, 0),
            ),
            heterogeneous=True,
        )
    )

    assert module.edge_manifest(
        empty_pair
    ) == (
        ((0, 0), (1, 0), 2),
        ((1, 0), (2, 0), 1),
        ((2, 0), (3, 0), 2),
    )


def test_e1_matched_uniform_changes_only_edge_weights() -> None:
    module = _load_e1_module()

    geometry = _geometry(
        (0, 0),
        (2, 0),
    )

    heterogeneous = (
        module.build_occupied_empty_field_graph(
            geometry,
            heterogeneous=True,
        )
    )

    uniform = (
        module.build_occupied_empty_field_graph(
            geometry,
            heterogeneous=False,
        )
    )

    assert heterogeneous.cells == uniform.cells
    assert heterogeneous.material == uniform.material
    assert heterogeneous.initial_state == uniform.initial_state

    assert module.edge_manifest(
        heterogeneous
    ) == (
        ((0, 0), (1, 0), 2),
        ((1, 0), (2, 0), 2),
    )

    assert module.edge_manifest(
        uniform
    ) == (
        ((0, 0), (1, 0), 1),
        ((1, 0), (2, 0), 1),
    )


def test_e1_exact_weighted_euler_step() -> None:
    module = _load_e1_module()

    geometry = _geometry(
        (0, 0),
        (2, 0),
    )

    heterogeneous = (
        module.build_occupied_empty_field_graph(
            geometry,
            heterogeneous=True,
        )
    )

    uniform = (
        module.build_occupied_empty_field_graph(
            geometry,
            heterogeneous=False,
        )
    )

    assert module.evolve_field_numerator(
        heterogeneous.initial_state,
        heterogeneous,
    ) == (
        14,
        4,
        14,
    )

    assert module.evolve_field_numerator(
        uniform.initial_state,
        uniform,
    ) == (
        15,
        2,
        15,
    )


def test_e1_signature_and_static_diagnostic_are_translation_invariant() -> None:
    module = _load_e1_module()

    source = _geometry(
        (0, 0),
        (0, 2),
        (2, 1),
    )

    translated = _translate(
        source,
        dx=13,
        dy=21,
    )

    assert module.static_material_signature(
        source
    ) == module.static_material_signature(
        translated
    )

    assert module.occupied_empty_field_signature(
        source,
        heterogeneous=False,
    ) == module.occupied_empty_field_signature(
        translated,
        heterogeneous=False,
    )

    assert module.occupied_empty_field_signature(
        source,
        heterogeneous=True,
    ) == module.occupied_empty_field_signature(
        translated,
        heterogeneous=True,
    )


def test_e1_reflected_pair_preserves_declared_symmetry() -> None:
    module = _load_e1_module()

    width4_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_graph_laplacian_width4.py"
    )

    width4 = _load_module(
        width4_path,
        "_petra_vision_e1_width4_control",
    )

    shapes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a = "G(G(G(T)),G(T,T))"
    code_b = "G(G(T,T),G(G(T)))"

    geometry_a = width4.encode_experimental_geometry(
        shapes[code_a]
    )
    geometry_b = width4.encode_experimental_geometry(
        shapes[code_b]
    )

    assert module.static_material_signature(
        geometry_a
    ) == module.static_material_signature(
        geometry_b
    )

    assert module.occupied_empty_field_signature(
        geometry_a,
        heterogeneous=False,
    ) == module.occupied_empty_field_signature(
        geometry_b,
        heterogeneous=False,
    )

    assert module.occupied_empty_field_signature(
        geometry_a,
        heterogeneous=True,
    ) == module.occupied_empty_field_signature(
        geometry_b,
        heterogeneous=True,
    )


def test_e1_source_boundary_is_geometry_only() -> None:
    module = _load_e1_module()

    tree = ast.parse(
        E1_MODULE_PATH.read_text(
            encoding="utf-8"
        )
    )

    petra_imports = {
        node.module
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("petra")
        )
    }

    assert petra_imports == {
        "petra.vision.geometry",
    }

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "native_fgs",
        "recompose_fgs",
        "shape_code",
        "resolve_address",
        "serialize_shape",
        "adapt_petra_shape",
        "restore_petra_shape",
    }

    referenced_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    assert referenced_names.isdisjoint(
        forbidden_names
    )

    assert module.PROTOCOL_ID.endswith(
        "occupied-empty-field-v0"
    )


def test_e1_evidence_boundary_and_causal_controls() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_e1_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_e1_evidence_test",
    )

    report = evidence.analyze_evidence()

    assert (
        report["protocol"]["id"]
        == "petra-vision-global-geometric-coupling-occupied-empty-field-evidence-v0"
    )

    assert (
        report["protocol"]["e1_protocol"]
        == "petra-vision-global-geometric-coupling-occupied-empty-field-v0"
    )

    assert report["corpora"]["phase_1"]["size"] == 110
    assert report["corpora"]["held_out"]["size"] == 27
    assert report["corpora"]["extended"]["size"] == 137

    assert report["source_boundary_audit"]["passed"]
    assert report["translation_audit"]["passed"]
    assert report["reflection_audit"]["passed"]
    assert report["degree_bound_passed"]
    assert report["exact_matched_domain"]
    assert report["exact_l1_domain"]
    assert report["deterministic_replay"]
    assert report["known_reflected_pair_preserved"]

    assert (
        report["translation_audit"]["static_matches"]
        == 110
    )
    assert (
        report["translation_audit"]["uniform_matches"]
        == 110
    )
    assert (
        report["translation_audit"]["heterogeneous_matches"]
        == 110
    )

    assert report["reflection_audit"][
        "static_material_match"
    ]
    assert report["reflection_audit"][
        "matched_uniform_match"
    ]
    assert report["reflection_audit"][
        "heterogeneous_match"
    ]

    for corpus_name in (
        "phase_1",
        "held_out",
        "extended",
    ):
        item = report[corpus_name]
        readers = item["readers"]

        assert "static_material_diagnostic" in readers
        assert "e1_matched_uniform" in readers
        assert "e1_heterogeneous" in readers
        assert "frozen_l1_q8" in readers

        attribution = item[
            "static_attribution"
        ]

        assert (
            attribution[
                "heterogeneity_split_pair_count"
            ]
            == attribution[
                "already_distinguished_by_static_material_count"
            ]
            + attribution[
                "not_distinguished_by_static_material_count"
            ]
        )

    # Deliberately no expected E1 discrimination count.
    # The first replay reports the actual heterogeneous-medium result.


C0_MODULE_PATH = (
    ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_c0.py"
)


def _load_c0_module() -> ModuleType:
    if not C0_MODULE_PATH.is_file():
        pytest.fail(
            "Gate 2 C0 research module is not implemented yet",
            pytrace=False,
        )

    return _load_module(
        C0_MODULE_PATH,
        "_petra_vision_global_geometric_coupling_c0",
    )


def test_c0_protocol_is_frozen_before_results() -> None:
    module = _load_c0_module()

    assert (
        module.PROTOCOL_ID
        == "petra-vision-global-geometric-coupling-component-null-v0"
    )
    assert (
        module.INNER_PROTOCOL_ID
        == "petra-vision-graph-laplacian-v1"
    )
    assert module.COMPONENT_ADJACENCY == "four-neighbor"
    assert module.SAMPLE_STEPS == (
        1,
        2,
        4,
        8,
        16,
        32,
    )


def test_c0_components_are_normalized_and_multiplicity_preserving() -> None:
    module = _load_c0_module()

    geometry = _geometry(
        (10, 5),
        (11, 5),
        (20, 8),
        (30, 8),
    )

    components = module.connected_component_geometries(
        geometry
    )

    cell_sets = [
        component.cells
        for component in components
    ]

    assert len(cell_sets) == 3

    assert cell_sets.count(
        ((0, 0),)
    ) == 2

    assert cell_sets.count(
        (
            (0, 0),
            (1, 0),
        )
    ) == 1


def test_c0_discards_intercomponent_position_and_order() -> None:
    module = _load_c0_module()

    left_domino = _geometry(
        (0, 0),
        (1, 0),
        (8, 3),
    )

    right_domino = _geometry(
        (0, 3),
        (20, 0),
        (21, 0),
    )

    assert module.component_null_signature(
        left_domino
    ) == module.component_null_signature(
        right_domino
    )


def test_c0_single_component_reader_wraps_one_frozen_component_signature() -> None:
    module = _load_c0_module()

    geometry = _geometry(
        (4, 7),
        (5, 7),
        (5, 8),
    )

    components = module.connected_component_geometries(
        geometry
    )

    assert len(components) == 1

    expected = (
        module.component_signature(
            components[0]
        ),
    )

    assert module.component_null_signature(
        geometry
    ) == expected


def test_c0_reflected_pair_remains_component_order_collision() -> None:
    module = _load_c0_module()

    width4_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_graph_laplacian_width4.py"
    )

    width4 = _load_module(
        width4_path,
        "_petra_vision_c0_width4_control",
    )

    shapes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a = "G(G(G(T)),G(T,T))"
    code_b = "G(G(T,T),G(G(T)))"

    geometry_a = width4.encode_experimental_geometry(
        shapes[code_a]
    )

    geometry_b = width4.encode_experimental_geometry(
        shapes[code_b]
    )

    assert module.component_null_signature(
        geometry_a
    ) == module.component_null_signature(
        geometry_b
    )


def test_c0_source_boundary_is_geometry_only() -> None:
    module = _load_c0_module()

    tree = ast.parse(
        C0_MODULE_PATH.read_text(
            encoding="utf-8"
        )
    )

    petra_imports = {
        node.module
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("petra")
        )
    }

    assert petra_imports == {
        "petra.vision.geometry",
    }

    forbidden_names = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "native_fgs",
        "recompose_fgs",
        "shape_code",
        "resolve_address",
        "serialize_shape",
        "build_factor_proximity_graph",
        "build_full_lattice_graph",
        "occupied_empty_field_signature",
        "adapt_petra_shape",
        "restore_petra_shape",
    }

    referenced_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    assert referenced_names.isdisjoint(
        forbidden_names
    )

    assert module.PROTOCOL_ID.endswith(
        "component-null-v0"
    )


def test_c0_evidence_boundary_and_representation_controls() -> None:
    evidence_path = (
        ROOT
        / "tools"
        / "research"
        / "petra_vision_global_geometric_coupling_c0_evidence.py"
    )

    evidence = _load_module(
        evidence_path,
        "_petra_vision_global_geometric_coupling_c0_evidence_test",
    )

    report = evidence.analyze_evidence()

    assert (
        report["protocol"]["id"]
        == "petra-vision-global-geometric-coupling-component-null-evidence-v0"
    )

    assert (
        report["protocol"]["c0_protocol"]
        == "petra-vision-global-geometric-coupling-component-null-v0"
    )

    assert (
        report["protocol"]["inner_protocol"]
        == "petra-vision-graph-laplacian-v1"
    )

    assert report["corpora"]["phase_1"]["size"] == 110
    assert report["corpora"]["held_out"]["size"] == 27
    assert report["corpora"]["extended"]["size"] == 137

    assert report["source_boundary_audit"]["passed"]
    assert report[
        "translation_displacement_audit"
    ]["passed"]
    assert report["reflection_audit"]["passed"]
    assert report["exact_component_partition"]
    assert report["component_multiplicity_preserved"]
    assert report["deterministic_replay"]
    assert report["known_reflected_pair_preserved"]

    assert (
        report[
            "translation_displacement_audit"
        ]["translation_matches"]
        == 110
    )

    assert (
        report[
            "translation_displacement_audit"
        ]["displacement_and_order_matches"]
        == 110
    )

    for corpus_name in (
        "phase_1",
        "held_out",
        "extended",
    ):
        readers = report[
            corpus_name
        ]["readers"]

        assert "component_count_only" in readers
        assert "static_component_profile" in readers
        assert "frozen_b0_global_multiset" in readers
        assert "c0_component_multiset" in readers

    # Deliberately no expected C0 discrimination count.
    # The first replay reports the actual representation-control result.
