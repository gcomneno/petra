#!/usr/bin/env python3
"""Deterministic evidence for PETRA VISION Gate 2 G2-F1."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from types import ModuleType


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


F1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f1.py"
)

F0_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f0.py"
)

FGS_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_structural_geometric_factorization.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-fgs-proximity-evidence-v0"
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


f1 = _load_module(
    F1_TOOL_PATH,
    "_petra_vision_gate2_f1_evidence_f1",
)

f0 = _load_module(
    F0_TOOL_PATH,
    "_petra_vision_gate2_f1_evidence_f0",
)

fgs = _load_module(
    FGS_TOOL_PATH,
    "_petra_vision_gate2_f1_evidence_fgs",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate2_f1_evidence_width4",
)


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _jsonable(value):
    if isinstance(value, Fraction):
        return [
            value.numerator,
            value.denominator,
        ]

    if isinstance(value, tuple):
        return [
            _jsonable(item)
            for item in value
        ]

    if isinstance(value, list):
        return [
            _jsonable(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _jsonable(item)
            for key, item in value.items()
        }

    return value


def _signature_sha256(signature: object) -> str:
    payload = json.dumps(
        _jsonable(signature),
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


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
        "split_by_coupling_count": len(
            split
        ),
        "split_by_coupling": [
            list(pair)
            for pair in split
        ],
        "introduced_by_coupling_count": (
            len(introduced)
        ),
        "introduced_by_coupling": [
            list(pair)
            for pair in introduced
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
        F1_TOOL_PATH.read_text(
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

    passed = (
        petra_imports
        == ["petra.vision.geometry"]
        and not forbidden_references
    )

    return {
        "passed": passed,
        "input_boundary": (
            "OrthogonalGeometry only"
        ),
        "petra_imports": petra_imports,
        "forbidden_references": (
            forbidden_references
        ),
    }


def _reflection_audit() -> dict[str, object]:
    shapes = {
        width4.shape_code(shape): shape
        for shape in width4.phase_1_corpus()
    }

    code_a, code_b = EXPECTED_COLLISION

    geometry_a = (
        width4.encode_experimental_geometry(
            shapes[code_a]
        )
    )
    geometry_b = (
        width4.encode_experimental_geometry(
            shapes[code_b]
        )
    )

    graph_a = f1.build_factor_proximity_graph(
        geometry_a
    )
    graph_b = f1.build_factor_proximity_graph(
        geometry_b
    )

    if len(graph_a.factors) != len(
        graph_b.factors
    ):
        raise RuntimeError(
            "reflected control changed factor count"
        )

    unused_b = set(
        range(len(graph_b.factors))
    )
    permutation = []

    for factor_a in graph_a.factors:
        candidates = [
            index
            for index in sorted(unused_b)
            if graph_b.factors[index] == factor_a
        ]

        if len(candidates) != 1:
            raise RuntimeError(
                "reflected control factor mapping "
                "is not uniquely recoverable"
            )

        chosen = candidates[0]
        permutation.append(chosen)
        unused_b.remove(chosen)

    permutation = tuple(permutation)

    distances_equivariant = all(
        graph_a.distances[left][right]
        == graph_b.distances[
            permutation[left]
        ][permutation[right]]
        for left in range(
            len(graph_a.factors)
        )
        for right in range(
            len(graph_a.factors)
        )
    )

    weights_equivariant = all(
        graph_a.weights[left][right]
        == graph_b.weights[
            permutation[left]
        ][permutation[right]]
        for left in range(
            len(graph_a.factors)
        )
        for right in range(
            len(graph_a.factors)
        )
    )

    features_equivariant = all(
        graph_a.initial_state[index]
        == graph_b.initial_state[
            permutation[index]
        ]
        for index in range(
            len(graph_a.factors)
        )
    )

    f0_match = (
        f0.factor_multiset_signature(
            geometry_a
        )
        == f0.factor_multiset_signature(
            geometry_b
        )
    )

    null_match = (
        f1.factor_proximity_signature(
            geometry_a,
            coupled=False,
        )
        == f1.factor_proximity_signature(
            geometry_b,
            coupled=False,
        )
    )

    coupled_match = (
        f1.factor_proximity_signature(
            geometry_a,
            coupled=True,
        )
        == f1.factor_proximity_signature(
            geometry_b,
            coupled=True,
        )
    )

    joint_null_match = (
        f1.joint_f0_f1_signature(
            geometry_a,
            coupled=False,
        )
        == f1.joint_f0_f1_signature(
            geometry_b,
            coupled=False,
        )
    )

    joint_coupled_match = (
        f1.joint_f0_f1_signature(
            geometry_a,
            coupled=True,
        )
        == f1.joint_f0_f1_signature(
            geometry_b,
            coupled=True,
        )
    )

    ordered_coupled_match = (
        f1.ordered_factor_proximity_signature(
            geometry_a,
            coupled=True,
        )
        == f1.ordered_factor_proximity_signature(
            geometry_b,
            coupled=True,
        )
    )

    passed = all((
        distances_equivariant,
        weights_equivariant,
        features_equivariant,
        f0_match,
        null_match,
        coupled_match,
        joint_null_match,
        joint_coupled_match,
    ))

    return {
        "passed": passed,
        "pair": list(EXPECTED_COLLISION),
        "factor_permutation_a_to_b": list(
            permutation
        ),
        "distances_equivariant": (
            distances_equivariant
        ),
        "weights_equivariant": (
            weights_equivariant
        ),
        "intrinsic_features_equivariant": (
            features_equivariant
        ),
        "f0_unordered_match": f0_match,
        "f1_null_match": null_match,
        "f1_coupled_match": coupled_match,
        "joint_null_match": (
            joint_null_match
        ),
        "joint_coupled_match": (
            joint_coupled_match
        ),
        "ordered_coupled_diagnostic_match": (
            ordered_coupled_match
        ),
    }


def _analyze_corpus(
    corpus: tuple[object, ...],
) -> dict[str, object]:
    codes: list[str] = []

    f0_signatures: list[object] = []
    null_signatures: list[object] = []
    coupled_signatures: list[object] = []
    joint_null_signatures: list[object] = []
    joint_coupled_signatures: list[object] = []
    ordered_null_signatures: list[object] = []
    ordered_coupled_signatures: list[object] = []

    records: list[dict[str, object]] = []

    factor_count_distribution: Counter[int] = Counter()
    total_pairwise_edges = 0
    geometries_with_coupling = 0
    observed_distances: Counter[int] = Counter()

    deterministic_matches = 0
    recomposition_matches = 0

    for shape in corpus:
        code = width4.shape_code(shape)

        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        graph = f1.build_factor_proximity_graph(
            geometry
        )

        factor_count = len(
            graph.factors
        )

        factor_count_distribution[
            factor_count
        ] += 1

        pair_count = (
            factor_count
            * (factor_count - 1)
            // 2
        )

        total_pairwise_edges += pair_count

        if pair_count:
            geometries_with_coupling += 1

        for left, right in combinations(
            range(factor_count),
            2,
        ):
            observed_distances[
                graph.distances[left][right]
            ] += 1

        if fgs.recompose_fgs(
            graph.factors
        ) == geometry:
            recomposition_matches += 1

        f0_signature = (
            f0.factor_multiset_signature(
                geometry
            )
        )

        null_signature = (
            f1.factor_proximity_signature(
                geometry,
                coupled=False,
            )
        )

        coupled_signature = (
            f1.factor_proximity_signature(
                geometry,
                coupled=True,
            )
        )

        joint_null = (
            f1.joint_f0_f1_signature(
                geometry,
                coupled=False,
            )
        )

        joint_coupled = (
            f1.joint_f0_f1_signature(
                geometry,
                coupled=True,
            )
        )

        ordered_null = (
            f1.ordered_factor_proximity_signature(
                geometry,
                coupled=False,
            )
        )

        ordered_coupled = (
            f1.ordered_factor_proximity_signature(
                geometry,
                coupled=True,
            )
        )

        if (
            f1.factor_proximity_signature(
                geometry,
                coupled=True,
            )
            == coupled_signature
            and f1.joint_f0_f1_signature(
                geometry,
                coupled=True,
            )
            == joint_coupled
        ):
            deterministic_matches += 1

        codes.append(code)
        f0_signatures.append(
            f0_signature
        )
        null_signatures.append(
            null_signature
        )
        coupled_signatures.append(
            coupled_signature
        )
        joint_null_signatures.append(
            joint_null
        )
        joint_coupled_signatures.append(
            joint_coupled
        )
        ordered_null_signatures.append(
            ordered_null
        )
        ordered_coupled_signatures.append(
            ordered_coupled
        )

        records.append({
            "shape": code,
            "factor_count": factor_count,
            "pairwise_edge_count": pair_count,
            "f0_sha256": (
                _signature_sha256(
                    f0_signature
                )
            ),
            "f1_null_sha256": (
                _signature_sha256(
                    null_signature
                )
            ),
            "f1_coupled_sha256": (
                _signature_sha256(
                    coupled_signature
                )
            ),
            "joint_null_sha256": (
                _signature_sha256(
                    joint_null
                )
            ),
            "joint_coupled_sha256": (
                _signature_sha256(
                    joint_coupled
                )
            ),
        })

    frozen_codes = tuple(codes)

    f0_summary = _summarize(
        frozen_codes,
        tuple(f0_signatures),
    )

    null_summary = _summarize(
        frozen_codes,
        tuple(null_signatures),
    )

    coupled_summary = _summarize(
        frozen_codes,
        tuple(coupled_signatures),
    )

    joint_null_summary = _summarize(
        frozen_codes,
        tuple(joint_null_signatures),
    )

    joint_coupled_summary = _summarize(
        frozen_codes,
        tuple(joint_coupled_signatures),
    )

    ordered_null_summary = _summarize(
        frozen_codes,
        tuple(ordered_null_signatures),
    )

    ordered_coupled_summary = _summarize(
        frozen_codes,
        tuple(ordered_coupled_signatures),
    )

    return {
        "size": len(corpus),
        "construction": {
            "factor_count_distribution": {
                str(count): occurrences
                for count, occurrences in sorted(
                    factor_count_distribution.items()
                )
            },
            "geometries_with_interfactor_coupling": (
                geometries_with_coupling
            ),
            "total_pairwise_edges": (
                total_pairwise_edges
            ),
            "distance_distribution": {
                str(distance): count
                for distance, count in sorted(
                    observed_distances.items()
                )
            },
            "minimum_observed_distance": (
                min(
                    observed_distances,
                    default=None,
                )
            ),
            "maximum_observed_distance": (
                max(
                    observed_distances,
                    default=None,
                )
            ),
        },
        "readers": {
            "f0_unordered_dynamic": (
                f0_summary
            ),
            "f1_matched_null": (
                null_summary
            ),
            "f1_coupled": (
                coupled_summary
            ),
            "joint_f0_f1_null": (
                joint_null_summary
            ),
            "joint_f0_f1_coupled": (
                joint_coupled_summary
            ),
            "ordered_f1_null_control": (
                ordered_null_summary
            ),
            "ordered_f1_coupled_control": (
                ordered_coupled_summary
            ),
        },
        "incremental_f1_vs_null": (
            _delta(
                null_summary,
                coupled_summary,
            )
        ),
        "incremental_joint_vs_null": (
            _delta(
                joint_null_summary,
                joint_coupled_summary,
            )
        ),
        "known_gate1a_collision": {
            reader: _known_collision_status(
                summary
            )
            for reader, summary in (
                (
                    "f0_unordered_dynamic",
                    f0_summary,
                ),
                (
                    "f1_matched_null",
                    null_summary,
                ),
                (
                    "f1_coupled",
                    coupled_summary,
                ),
                (
                    "joint_f0_f1_null",
                    joint_null_summary,
                ),
                (
                    "joint_f0_f1_coupled",
                    joint_coupled_summary,
                ),
                (
                    "ordered_f1_coupled_control",
                    ordered_coupled_summary,
                ),
            )
        },
        "exact_recomposition": (
            recomposition_matches
            == len(corpus)
        ),
        "recomposition_matches": (
            recomposition_matches
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
            "F1 source boundary audit failed"
        )

    reflection = _reflection_audit()

    if not reflection["passed"]:
        raise RuntimeError(
            "F1 reflected-pair symmetry audit failed"
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
            "f0_unordered_dynamic",
            "f1_matched_null",
            "f1_coupled",
            "joint_f0_f1_null",
            "joint_f0_f1_coupled",
        ):
            if not known[reader]["collides"]:
                raise RuntimeError(
                    "F1 violated frozen reflected-pair "
                    f"control in reader {reader}"
                )

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "f1_protocol": f1.PROTOCOL_ID,
            "f0_protocol": f0.PROTOCOL_ID,
            "weight_law": f1.WEIGHT_LAW,
            "feature_channels": list(
                f1.FEATURE_CHANNELS
            ),
            "sample_steps": list(
                f1.SAMPLE_STEPS
            ),
            "arithmetic": "exact Fraction",
            "primary_reader": (
                "coordinate-free multiset of "
                "factor-state vectors"
            ),
            "joint_reader_predeclared": True,
        },
        "source_provenance": {
            "f1_source_sha256": (
                _source_sha256(
                    F1_TOOL_PATH
                )
            ),
            "f0_source_sha256": (
                _source_sha256(
                    F0_TOOL_PATH
                )
            ),
            "fgs_source_sha256": (
                _source_sha256(
                    FGS_TOOL_PATH
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
        "exact_recomposition": all(
            report["exact_recomposition"]
            for report in reports
        ),
        "deterministic_replay": all(
            report["deterministic_replay"]
            for report in reports
        ),
        "known_reflected_pair_preserved": all((
            reflection["f1_null_match"],
            reflection["f1_coupled_match"],
            reflection["joint_null_match"],
            reflection["joint_coupled_match"],
        )),
        "claim_boundary": (
            "bounded Gate 2 F1 proximity-coupling "
            "evidence only; no factor ordinal in primary "
            "reader, no intrinsic reflection breaking, "
            "no spectral, decoding, robustness, physical, "
            "or theorem-level claim"
        ),
    }


def render_text_report(
    report: dict[str, object],
) -> str:
    lines = [
        "===== PETRA VISION GATE 2 — F1 EVIDENCE =====",
        f"Protocol: {report['protocol']['id']}",
        (
            "F1 source SHA256: "
            f"{report['source_provenance']['f1_source_sha256']}"
        ),
        "",
        "===== G2-F1 =====",
    ]

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = report[name]

        f0_reader = item["readers"][
            "f0_unordered_dynamic"
        ]
        null = item["readers"][
            "f1_matched_null"
        ]
        coupled = item["readers"][
            "f1_coupled"
        ]
        joint_null = item["readers"][
            "joint_f0_f1_null"
        ]
        joint_coupled = item["readers"][
            "joint_f0_f1_coupled"
        ]
        delta = item[
            "incremental_f1_vs_null"
        ]
        joint_delta = item[
            "incremental_joint_vs_null"
        ]
        known = item[
            "known_gate1a_collision"
        ]

        lines.extend([
            f"{label}: {item['size']} forme",
            (
                "  F0:            "
                f"{f0_reader['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  F1 null:       "
                f"{null['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  F1 coupled:    "
                f"{coupled['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  F1 gain:       "
                f"{delta['distinct_signature_gain']}"
            ),
            (
                "  joint null:    "
                f"{joint_null['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  joint coupled: "
                f"{joint_coupled['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  joint gain:    "
                f"{joint_delta['distinct_signature_gain']}"
            ),
            (
                "  joint split collision-pairs: "
                f"{joint_delta['split_by_coupling_count']}"
            ),
            (
                "  joint new collision-pairs:   "
                f"{joint_delta['introduced_by_coupling_count']}"
            ),
            (
                "  #23/#41 null/coupled/joint: "
                f"{known['f1_matched_null']['collides']} / "
                f"{known['f1_coupled']['collides']} / "
                f"{known['joint_f0_f1_coupled']['collides']}"
            ),
            (
                "  geometrie con coupling: "
                f"{item['construction']['geometries_with_interfactor_coupling']}/"
                f"{item['size']}"
            ),
            (
                "  pairwise edges: "
                f"{item['construction']['total_pairwise_edges']}"
            ),
            (
                "  distance range: "
                f"{item['construction']['minimum_observed_distance']}"
                ".."
                f"{item['construction']['maximum_observed_distance']}"
            ),
            "",
        ])

    reflection = report[
        "reflection_audit"
    ]

    lines.extend([
        "===== AUDIT =====",
        (
            "Source boundary: "
            f"{report['source_boundary_audit']['passed']}"
        ),
        (
            "Reflection distances equivariant: "
            f"{reflection['distances_equivariant']}"
        ),
        (
            "Reflection weights equivariant: "
            f"{reflection['weights_equivariant']}"
        ),
        (
            "Reflection features equivariant: "
            f"{reflection['intrinsic_features_equivariant']}"
        ),
        (
            "Reflected pair preserved: "
            f"{report['known_reflected_pair_preserved']}"
        ),
        (
            "Exact FGS recomposition: "
            f"{report['exact_recomposition']}"
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
            "Run PETRA VISION Gate 2 G2-F1 evidence."
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
        _jsonable(report),
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
        and report["reflection_audit"][
            "passed"
        ]
        and report["exact_recomposition"]
        and report["deterministic_replay"]
        and report[
            "known_reflected_pair_preserved"
        ]
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
