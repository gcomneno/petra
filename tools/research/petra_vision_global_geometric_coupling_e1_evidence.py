#!/usr/bin/env python3
"""Deterministic evidence for PETRA VISION Gate 2 G2-E1."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from types import ModuleType


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


E1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_e1.py"
)

L1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_l1.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-occupied-empty-field-evidence-v0"
)

EXPECTED_COLLISION = tuple(sorted((
    "G(G(G(T)),G(T,T))",
    "G(G(T,T),G(G(T)))",
)))


def _load_module(
    path: Path,
    name: str,
) -> ModuleType:
    existing = sys.modules.get(name)

    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"unable to load research module: {path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


e1 = _load_module(
    E1_TOOL_PATH,
    "_petra_vision_gate2_e1_evidence_e1",
)

l1 = _load_module(
    L1_TOOL_PATH,
    "_petra_vision_gate2_e1_evidence_l1",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate2_e1_evidence_width4",
)


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _signature_sha256(
    signature: object,
) -> str:
    return hashlib.sha256(
        json.dumps(
            signature,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _summarize(
    codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> dict[str, object]:
    if len(codes) != len(signatures):
        raise ValueError(
            "shape codes and signatures must have equal length"
        )

    groups: dict[object, list[str]] = defaultdict(list)

    for code, signature in zip(
        codes,
        signatures,
    ):
        groups[signature].append(code)

    collisions = sorted(
        tuple(sorted(group))
        for group in groups.values()
        if len(group) > 1
    )

    distribution = Counter(
        len(group)
        for group in collisions
    )

    return {
        "distinct_signatures": len(groups),
        "collision_group_count": len(collisions),
        "colliding_shape_count": sum(
            len(group)
            for group in collisions
        ),
        "maximum_collision_group_size": max(
            (
                len(group)
                for group in collisions
            ),
            default=1,
        ),
        "collision_shape_codes": [
            list(group)
            for group in collisions
        ],
        "collision_size_distribution": {
            str(size): count
            for size, count in sorted(
                distribution.items()
            )
        },
    }


def _collision_pairs(
    summary: dict[str, object],
) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()

    for raw_group in summary[
        "collision_shape_codes"
    ]:
        group = tuple(raw_group)

        for left, right in combinations(
            group,
            2,
        ):
            result.add(
                tuple(sorted((left, right)))
            )

    return result


def _delta(
    null_summary: dict[str, object],
    coupled_summary: dict[str, object],
) -> dict[str, object]:
    null_pairs = _collision_pairs(
        null_summary
    )
    coupled_pairs = _collision_pairs(
        coupled_summary
    )

    split = sorted(
        null_pairs - coupled_pairs
    )
    introduced = sorted(
        coupled_pairs - null_pairs
    )

    return {
        "distinct_signature_gain": (
            int(coupled_summary[
                "distinct_signatures"
            ])
            - int(null_summary[
                "distinct_signatures"
            ])
        ),
        "null_collision_pair_count": (
            len(null_pairs)
        ),
        "coupled_collision_pair_count": (
            len(coupled_pairs)
        ),
        "split_by_heterogeneity_count": (
            len(split)
        ),
        "split_by_heterogeneity": [
            list(pair)
            for pair in split
        ],
        "introduced_by_heterogeneity_count": (
            len(introduced)
        ),
        "introduced_by_heterogeneity": [
            list(pair)
            for pair in introduced
        ],
    }


def _static_attribution(
    uniform_summary: dict[str, object],
    heterogeneous_summary: dict[str, object],
    static_summary: dict[str, object],
) -> dict[str, object]:
    uniform_pairs = _collision_pairs(
        uniform_summary
    )
    heterogeneous_pairs = _collision_pairs(
        heterogeneous_summary
    )
    static_pairs = _collision_pairs(
        static_summary
    )

    split = uniform_pairs - heterogeneous_pairs

    already_static = sorted(
        pair
        for pair in split
        if pair not in static_pairs
    )

    not_static = sorted(
        pair
        for pair in split
        if pair in static_pairs
    )

    return {
        "heterogeneity_split_pair_count": len(
            split
        ),
        "already_distinguished_by_static_material_count": (
            len(already_static)
        ),
        "already_distinguished_by_static_material": [
            list(pair)
            for pair in already_static
        ],
        "not_distinguished_by_static_material_count": (
            len(not_static)
        ),
        "not_distinguished_by_static_material": [
            list(pair)
            for pair in not_static
        ],
    }


def _known_collision_status(
    summary: dict[str, object],
) -> dict[str, object]:
    expected = set(EXPECTED_COLLISION)
    containing_group = None

    for raw_group in summary[
        "collision_shape_codes"
    ]:
        group = tuple(raw_group)

        if expected.issubset(group):
            containing_group = list(group)
            break

    return {
        "pair": list(EXPECTED_COLLISION),
        "collides": containing_group is not None,
        "containing_collision_group": (
            containing_group
        ),
    }


def _source_boundary_audit() -> dict[str, object]:
    tree = ast.parse(
        E1_TOOL_PATH.read_text(
            encoding="utf-8"
        )
    )

    petra_imports = sorted({
        node.module
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith("petra")
        )
    })

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

    forbidden_references = sorted(
        referenced_names & forbidden_names
    )

    return {
        "passed": (
            petra_imports
            == ["petra.vision.geometry"]
            and not forbidden_references
        ),
        "petra_imports": petra_imports,
        "forbidden_references": (
            forbidden_references
        ),
        "input_boundary": (
            "OrthogonalGeometry only"
        ),
        "fgs_dependency": False,
    }


def _translate_geometry(
    geometry: object,
    *,
    dx: int,
    dy: int,
):
    geometry_type = type(geometry)

    return geometry_type(
        cells=tuple(sorted(
            (
                x + dx,
                y + dy,
            )
            for x, y in geometry.cells
        ))
    )


def _reflection_audit() -> dict[str, object]:
    shapes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a, code_b = EXPECTED_COLLISION

    geometry_a = width4.encode_experimental_geometry(
        shapes[code_a]
    )
    geometry_b = width4.encode_experimental_geometry(
        shapes[code_b]
    )

    static_match = (
        e1.static_material_signature(
            geometry_a
        )
        == e1.static_material_signature(
            geometry_b
        )
    )

    uniform_match = (
        e1.occupied_empty_field_signature(
            geometry_a,
            heterogeneous=False,
        )
        == e1.occupied_empty_field_signature(
            geometry_b,
            heterogeneous=False,
        )
    )

    heterogeneous_match = (
        e1.occupied_empty_field_signature(
            geometry_a,
            heterogeneous=True,
        )
        == e1.occupied_empty_field_signature(
            geometry_b,
            heterogeneous=True,
        )
    )

    graph_a = (
        e1.build_occupied_empty_field_graph(
            geometry_a,
            heterogeneous=True,
        )
    )
    graph_b = (
        e1.build_occupied_empty_field_graph(
            geometry_b,
            heterogeneous=True,
        )
    )

    histogram_match = (
        e1.edge_weight_histogram(
            graph_a
        )
        == e1.edge_weight_histogram(
            graph_b
        )
    )

    passed = all((
        static_match,
        uniform_match,
        heterogeneous_match,
        histogram_match,
        len(graph_a.cells) == len(
            graph_b.cells
        ),
    ))

    return {
        "passed": passed,
        "pair": list(EXPECTED_COLLISION),
        "same_lattice_vertex_count": (
            len(graph_a.cells)
            == len(graph_b.cells)
        ),
        "edge_weight_histogram_match": (
            histogram_match
        ),
        "static_material_match": (
            static_match
        ),
        "matched_uniform_match": (
            uniform_match
        ),
        "heterogeneous_match": (
            heterogeneous_match
        ),
    }


def _translation_audit() -> dict[str, object]:
    corpus = width4.phase_1_corpus()

    static_matches = 0
    uniform_matches = 0
    heterogeneous_matches = 0

    for shape in corpus:
        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        translated = _translate_geometry(
            geometry,
            dx=11,
            dy=7,
        )

        if (
            e1.static_material_signature(
                geometry
            )
            == e1.static_material_signature(
                translated
            )
        ):
            static_matches += 1

        if (
            e1.occupied_empty_field_signature(
                geometry,
                heterogeneous=False,
            )
            == e1.occupied_empty_field_signature(
                translated,
                heterogeneous=False,
            )
        ):
            uniform_matches += 1

        if (
            e1.occupied_empty_field_signature(
                geometry,
                heterogeneous=True,
            )
            == e1.occupied_empty_field_signature(
                translated,
                heterogeneous=True,
            )
        ):
            heterogeneous_matches += 1

    total = len(corpus)

    return {
        "passed": (
            static_matches == total
            and uniform_matches == total
            and heterogeneous_matches == total
        ),
        "offset": [11, 7],
        "static_matches": static_matches,
        "uniform_matches": uniform_matches,
        "heterogeneous_matches": (
            heterogeneous_matches
        ),
        "total": total,
    }


def _analyze_corpus(
    corpus: tuple[object, ...],
) -> dict[str, object]:
    codes: list[str] = []

    static_signatures: list[object] = []
    uniform_signatures: list[object] = []
    heterogeneous_signatures: list[object] = []
    l1_signatures: list[object] = []

    records: list[dict[str, object]] = []

    total_lattice_vertices = 0
    total_lattice_edges = 0
    geometries_with_empty_sites = 0

    maximum_observed_weighted_degree = 0

    aggregate_edge_weights: Counter[int] = Counter()

    exact_matched_domain_count = 0
    exact_l1_domain_count = 0
    deterministic_matches = 0

    for shape in corpus:
        code = width4.shape_code(shape)

        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        heterogeneous_graph = (
            e1.build_occupied_empty_field_graph(
                geometry,
                heterogeneous=True,
            )
        )

        uniform_graph = (
            e1.build_occupied_empty_field_graph(
                geometry,
                heterogeneous=False,
            )
        )

        l1_graph = l1.build_full_lattice_graph(
            geometry,
            coupled=True,
        )

        if (
            heterogeneous_graph.cells
            == uniform_graph.cells
            and heterogeneous_graph.material
            == uniform_graph.material
            and heterogeneous_graph.initial_state
            == uniform_graph.initial_state
            and tuple(
                (edge.left, edge.right)
                for edge in heterogeneous_graph.edges
            )
            == tuple(
                (edge.left, edge.right)
                for edge in uniform_graph.edges
            )
        ):
            exact_matched_domain_count += 1

        if (
            heterogeneous_graph.cells
            == l1_graph.cells
            and heterogeneous_graph.initial_state
            == l1_graph.initial_state
            and tuple(
                (edge.left, edge.right)
                for edge in heterogeneous_graph.edges
            )
            == tuple(
                (edge.left, edge.right)
                for edge in l1_graph.edges
            )
        ):
            exact_l1_domain_count += 1

        lattice_vertices = len(
            heterogeneous_graph.cells
        )
        lattice_edges = len(
            heterogeneous_graph.edges
        )
        occupied = sum(
            heterogeneous_graph.material
        )
        empty = lattice_vertices - occupied

        total_lattice_vertices += (
            lattice_vertices
        )
        total_lattice_edges += (
            lattice_edges
        )

        if empty:
            geometries_with_empty_sites += 1

        observed_weighted_degree = (
            e1.maximum_weighted_degree(
                heterogeneous_graph
            )
        )

        maximum_observed_weighted_degree = max(
            maximum_observed_weighted_degree,
            observed_weighted_degree,
        )

        for edge in heterogeneous_graph.edges:
            aggregate_edge_weights[
                edge.weight
            ] += 1

        static_signature = (
            e1.static_material_signature(
                geometry
            )
        )

        uniform_signature = (
            e1.occupied_empty_field_signature(
                geometry,
                heterogeneous=False,
            )
        )

        heterogeneous_signature = (
            e1.occupied_empty_field_signature(
                geometry,
                heterogeneous=True,
            )
        )

        l1_signature = (
            l1.full_lattice_signature(
                geometry,
                coupled=True,
            )
        )

        replay = (
            e1.occupied_empty_field_signature(
                geometry,
                heterogeneous=True,
            )
        )

        if replay == heterogeneous_signature:
            deterministic_matches += 1

        codes.append(code)
        static_signatures.append(
            static_signature
        )
        uniform_signatures.append(
            uniform_signature
        )
        heterogeneous_signatures.append(
            heterogeneous_signature
        )
        l1_signatures.append(
            l1_signature
        )

        records.append({
            "shape": code,
            "lattice_vertices": (
                lattice_vertices
            ),
            "occupied_sites": occupied,
            "empty_sites": empty,
            "lattice_edges": (
                lattice_edges
            ),
            "maximum_weighted_degree": (
                observed_weighted_degree
            ),
            "edge_weight_histogram": [
                list(item)
                for item in e1.edge_weight_histogram(
                    heterogeneous_graph
                )
            ],
            "static_material_sha256": (
                _signature_sha256(
                    static_signature
                )
            ),
            "matched_uniform_sha256": (
                _signature_sha256(
                    uniform_signature
                )
            ),
            "heterogeneous_sha256": (
                _signature_sha256(
                    heterogeneous_signature
                )
            ),
            "frozen_l1_sha256": (
                _signature_sha256(
                    l1_signature
                )
            ),
        })

    frozen_codes = tuple(codes)

    static_summary = _summarize(
        frozen_codes,
        tuple(static_signatures),
    )

    uniform_summary = _summarize(
        frozen_codes,
        tuple(uniform_signatures),
    )

    heterogeneous_summary = _summarize(
        frozen_codes,
        tuple(heterogeneous_signatures),
    )

    l1_summary = _summarize(
        frozen_codes,
        tuple(l1_signatures),
    )

    return {
        "size": len(corpus),
        "construction": {
            "total_lattice_vertices": (
                total_lattice_vertices
            ),
            "total_lattice_edges": (
                total_lattice_edges
            ),
            "geometries_with_empty_sites": (
                geometries_with_empty_sites
            ),
            "maximum_observed_weighted_degree": (
                maximum_observed_weighted_degree
            ),
            "maximum_weighted_degree_bound": (
                e1.MAXIMUM_WEIGHTED_DEGREE_BOUND
            ),
            "euler_denominator": (
                e1.EULER_DENOMINATOR
            ),
            "degree_bound_passed": (
                maximum_observed_weighted_degree
                <= e1.MAXIMUM_WEIGHTED_DEGREE_BOUND
                < e1.EULER_DENOMINATOR
            ),
            "aggregate_edge_weight_histogram": {
                str(weight): (
                    aggregate_edge_weights.get(
                        weight,
                        0,
                    )
                )
                for weight in (
                    1,
                    2,
                    3,
                )
            },
            "exact_matched_domain_count": (
                exact_matched_domain_count
            ),
            "exact_l1_domain_count": (
                exact_l1_domain_count
            ),
        },
        "readers": {
            "static_material_diagnostic": (
                static_summary
            ),
            "e1_matched_uniform": (
                uniform_summary
            ),
            "e1_heterogeneous": (
                heterogeneous_summary
            ),
            "frozen_l1_q8": (
                l1_summary
            ),
        },
        "incremental_vs_matched_uniform": (
            _delta(
                uniform_summary,
                heterogeneous_summary,
            )
        ),
        "static_attribution": (
            _static_attribution(
                uniform_summary,
                heterogeneous_summary,
                static_summary,
            )
        ),
        "known_gate1a_collision": {
            "static_material_diagnostic": (
                _known_collision_status(
                    static_summary
                )
            ),
            "e1_matched_uniform": (
                _known_collision_status(
                    uniform_summary
                )
            ),
            "e1_heterogeneous": (
                _known_collision_status(
                    heterogeneous_summary
                )
            ),
            "frozen_l1_q8": (
                _known_collision_status(
                    l1_summary
                )
            ),
        },
        "exact_matched_domain": (
            exact_matched_domain_count
            == len(corpus)
        ),
        "exact_l1_domain": (
            exact_l1_domain_count
            == len(corpus)
        ),
        "deterministic_replay": (
            deterministic_matches
            == len(corpus)
        ),
        "shapes": records,
    }


@lru_cache(maxsize=1)
def analyze_evidence() -> dict[str, object]:
    phase_1 = width4.phase_1_corpus()
    held_out = width4.held_out_corpus()
    extended = width4.extended_corpus()

    if set(phase_1) & set(held_out):
        raise RuntimeError(
            "held-out overlaps Phase 1"
        )

    if (
        set(phase_1) | set(held_out)
        != set(extended)
    ):
        raise RuntimeError(
            "Phase 1 + held-out is not extended"
        )

    source_audit = (
        _source_boundary_audit()
    )

    if not source_audit["passed"]:
        raise RuntimeError(
            "E1 source boundary audit failed"
        )

    reflection = _reflection_audit()

    if not reflection["passed"]:
        raise RuntimeError(
            "E1 reflection control failed"
        )

    translation = _translation_audit()

    if not translation["passed"]:
        raise RuntimeError(
            "E1 translation control failed"
        )

    phase_1_report = _analyze_corpus(
        phase_1
    )
    held_out_report = _analyze_corpus(
        held_out
    )
    extended_report = _analyze_corpus(
        extended
    )

    reports = (
        phase_1_report,
        held_out_report,
        extended_report,
    )

    for report in (
        phase_1_report,
        extended_report,
    ):
        known = report[
            "known_gate1a_collision"
        ]

        for reader in (
            "static_material_diagnostic",
            "e1_matched_uniform",
            "e1_heterogeneous",
            "frozen_l1_q8",
        ):
            if not known[reader]["collides"]:
                raise RuntimeError(
                    "E1 violated frozen reflected-pair "
                    f"control in {reader}"
                )

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "e1_protocol": e1.PROTOCOL_ID,
            "edge_weight_rule": (
                e1.EDGE_WEIGHT_RULE
            ),
            "euler_denominator": (
                e1.EULER_DENOMINATOR
            ),
            "maximum_edge_weight": (
                e1.MAXIMUM_EDGE_WEIGHT
            ),
            "maximum_weighted_degree_bound": (
                e1.MAXIMUM_WEIGHTED_DEGREE_BOUND
            ),
            "sample_steps": list(
                e1.SAMPLE_STEPS
            ),
            "matched_control": (
                "same domain/state/schedule/reader/q=16 "
                "with all edge weights set to 1"
            ),
            "frozen_l1_comparison": (
                "reported separately at q=8"
            ),
        },
        "source_provenance": {
            "e1_source_sha256": (
                _source_sha256(
                    E1_TOOL_PATH
                )
            ),
            "l1_source_sha256": (
                _source_sha256(
                    L1_TOOL_PATH
                )
            ),
            "width4_source_sha256": (
                _source_sha256(
                    WIDTH4_TOOL_PATH
                )
            ),
        },
        "source_boundary_audit": (
            source_audit
        ),
        "reflection_audit": (
            reflection
        ),
        "translation_audit": (
            translation
        ),
        "corpora": {
            "phase_1": {
                "size": len(phase_1),
            },
            "held_out": {
                "size": len(held_out),
                "disjoint_from_phase_1": True,
            },
            "extended": {
                "size": len(extended),
                "exact_partition": True,
            },
        },
        "phase_1": phase_1_report,
        "held_out": held_out_report,
        "extended": extended_report,
        "degree_bound_passed": all(
            report["construction"][
                "degree_bound_passed"
            ]
            for report in reports
        ),
        "exact_matched_domain": all(
            report["exact_matched_domain"]
            for report in reports
        ),
        "exact_l1_domain": all(
            report["exact_l1_domain"]
            for report in reports
        ),
        "deterministic_replay": all(
            report["deterministic_replay"]
            for report in reports
        ),
        "known_reflected_pair_preserved": (
            reflection["static_material_match"]
            and reflection["matched_uniform_match"]
            and reflection["heterogeneous_match"]
        ),
        "claim_boundary": (
            "bounded Gate 2 E1 heterogeneous-medium evidence only; "
            "causal comparison is E1 heterogeneous q=16 versus "
            "matched uniform q=16; frozen L1 q=8 is separate; "
            "no FGS, structural identity, intrinsic reflection "
            "breaking, spectral, robustness, physical, decoding, "
            "or theorem-level claim"
        ),
    }


def render_text_report(
    report: dict[str, object],
) -> str:
    lines = [
        "===== PETRA VISION GATE 2 — E1 EVIDENCE =====",
        f"Protocol: {report['protocol']['id']}",
        (
            "E1 source SHA256: "
            f"{report['source_provenance']['e1_source_sha256']}"
        ),
        "",
        "===== G2-E1 =====",
    ]

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = report[name]
        readers = item["readers"]

        static = readers[
            "static_material_diagnostic"
        ]
        uniform = readers[
            "e1_matched_uniform"
        ]
        heterogeneous = readers[
            "e1_heterogeneous"
        ]
        frozen_l1 = readers[
            "frozen_l1_q8"
        ]

        delta = item[
            "incremental_vs_matched_uniform"
        ]

        attribution = item[
            "static_attribution"
        ]

        known = item[
            "known_gate1a_collision"
        ]

        lines.extend([
            f"{label}: {item['size']} forme",
            (
                "  static material: "
                f"{static['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  matched uniform q16: "
                f"{uniform['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  E1 heterogeneous q16: "
                f"{heterogeneous['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  E1 gain: "
                f"{delta['distinct_signature_gain']}"
            ),
            (
                "  split collision-pairs: "
                f"{delta['split_by_heterogeneity_count']}"
            ),
            (
                "  new collision-pairs: "
                f"{delta['introduced_by_heterogeneity_count']}"
            ),
            (
                "  split già distinti staticamente: "
                f"{attribution['already_distinguished_by_static_material_count']}"
            ),
            (
                "  split NON distinti staticamente: "
                f"{attribution['not_distinguished_by_static_material_count']}"
            ),
            (
                "  frozen L1 q8: "
                f"{frozen_l1['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  #23/#41 static/uniform/E1: "
                f"{known['static_material_diagnostic']['collides']} / "
                f"{known['e1_matched_uniform']['collides']} / "
                f"{known['e1_heterogeneous']['collides']}"
            ),
            (
                "  geometrie con empty sites: "
                f"{item['construction']['geometries_with_empty_sites']}/"
                f"{item['size']}"
            ),
            (
                "  max weighted degree: "
                f"{item['construction']['maximum_observed_weighted_degree']}"
            ),
            (
                "  edge weights aggregate 1/2/3: "
                f"{item['construction']['aggregate_edge_weight_histogram']}"
            ),
            "",
        ])

    lines.extend([
        "===== AUDIT =====",
        (
            "Source boundary: "
            f"{report['source_boundary_audit']['passed']}"
        ),
        (
            "Translation control: "
            f"{report['translation_audit']['passed']}"
        ),
        (
            "Reflection control: "
            f"{report['reflection_audit']['passed']}"
        ),
        (
            "Reflected pair preserved: "
            f"{report['known_reflected_pair_preserved']}"
        ),
        (
            "Matched E1 domain exact: "
            f"{report['exact_matched_domain']}"
        ),
        (
            "Same lattice domain as frozen L1: "
            f"{report['exact_l1_domain']}"
        ),
        (
            "Weighted-degree bound 12 < 16: "
            f"{report['degree_bound_passed']}"
        ),
        (
            "Deterministic replay interno: "
            f"{report['deterministic_replay']}"
        ),
        "",
        f"Claim: {report['claim_boundary']}",
    ])

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run PETRA VISION Gate 2 G2-E1 evidence."
        )
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="emit deterministic JSON",
    )

    parser.add_argument(
        "--write-json",
        type=Path,
        metavar="PATH",
        help="write deterministic JSON to PATH",
    )

    return parser


def main(
    argv: list[str] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_evidence()

    payload = json.dumps(
        report,
        indent=2,
        sort_keys=True,
    )

    if args.write_json is not None:
        args.write_json.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.write_json.write_text(
            payload + "\n",
            encoding="utf-8",
        )

    print(
        payload
        if args.json
        else render_text_report(report)
    )

    if not (
        report["source_boundary_audit"][
            "passed"
        ]
        and report["translation_audit"][
            "passed"
        ]
        and report["reflection_audit"][
            "passed"
        ]
        and report["degree_bound_passed"]
        and report["exact_matched_domain"]
        and report["exact_l1_domain"]
        and report["deterministic_replay"]
        and report[
            "known_reflected_pair_preserved"
        ]
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
