#!/usr/bin/env python3
"""Deterministic evidence for PETRA VISION Gate 2 D1 coupling."""

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
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from petra.vision import (  # noqa: E402
    OrthogonalGeometry,
    encode_geometry,
)


D1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)

BASELINE_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-distance2-evidence-v0"
)

TRANSLATION = (11, 7)

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


d1 = _load_module(
    D1_TOOL_PATH,
    "_petra_vision_gate2_d1",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate2_width4",
)


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _signature_sha256(
    signature: object,
) -> str:
    payload = json.dumps(
        signature,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def _translate_geometry(
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


def _summarize(
    shape_codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> dict[str, object]:
    if len(shape_codes) != len(signatures):
        raise ValueError(
            "shape codes and signatures must have equal length"
        )

    groups: dict[object, list[str]] = defaultdict(list)

    for code, signature in zip(
        shape_codes,
        signatures,
    ):
        groups[signature].append(code)

    collision_groups = sorted(
        tuple(sorted(codes))
        for codes in groups.values()
        if len(codes) > 1
    )

    distribution = Counter(
        len(group)
        for group in collision_groups
    )

    return {
        "distinct_signatures": len(groups),
        "collision_group_count": len(collision_groups),
        "colliding_shape_count": sum(
            len(group)
            for group in collision_groups
        ),
        "collision_shape_codes": [
            list(group)
            for group in collision_groups
        ],
        "collision_size_distribution": {
            str(size): count
            for size, count in sorted(
                distribution.items()
            )
        },
    }


def _pair_set_from_summary(
    summary: dict[str, object],
) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    for raw_group in summary[
        "collision_shape_codes"
    ]:
        group = tuple(raw_group)

        for left, right in combinations(group, 2):
            pairs.add(
                tuple(sorted((left, right)))
            )

    return pairs


def _incremental_delta(
    null_summary: dict[str, object],
    coupled_summary: dict[str, object],
) -> dict[str, object]:
    null_pairs = _pair_set_from_summary(
        null_summary
    )
    coupled_pairs = _pair_set_from_summary(
        coupled_summary
    )

    split_pairs = sorted(
        null_pairs - coupled_pairs
    )
    introduced_pairs = sorted(
        coupled_pairs - null_pairs
    )

    return {
        "null_collision_pair_count": len(null_pairs),
        "coupled_collision_pair_count": len(
            coupled_pairs
        ),
        "split_by_coupling_count": len(
            split_pairs
        ),
        "split_by_coupling": [
            list(pair)
            for pair in split_pairs
        ],
        "introduced_by_coupling_count": len(
            introduced_pairs
        ),
        "introduced_by_coupling": [
            list(pair)
            for pair in introduced_pairs
        ],
        "distinct_signature_gain": (
            int(coupled_summary[
                "distinct_signatures"
            ])
            - int(null_summary[
                "distinct_signatures"
            ])
        ),
    }


def _known_collision_status(
    summary: dict[str, object],
) -> dict[str, object]:
    pair = set(EXPECTED_COLLISION)
    containing_group = None

    for raw_group in summary[
        "collision_shape_codes"
    ]:
        group = tuple(raw_group)

        if pair.issubset(group):
            containing_group = list(group)
            break

    return {
        "pair": list(EXPECTED_COLLISION),
        "collides": containing_group is not None,
        "containing_collision_group": (
            containing_group
        ),
    }


def _edge_statistics(
    graph: object,
) -> dict[str, int]:
    kinds = Counter(
        edge.kind
        for edge in graph.edges
    )

    return {
        "vertices": len(graph.cells),
        "local_edges": kinds.get(
            "local",
            0,
        ),
        "bridge_edges": kinds.get(
            "bridge",
            0,
        ),
        "maximum_weighted_degree": (
            d1.maximum_weighted_degree(
                graph
            )
        ),
    }


def _source_boundary_audit() -> dict[str, object]:
    tree = ast.parse(
        D1_TOOL_PATH.read_text(
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

    passed = (
        petra_imports
        == ["petra.vision.geometry"]
        and not forbidden_references
    )

    return {
        "passed": passed,
        "petra_imports": petra_imports,
        "forbidden_references": (
            forbidden_references
        ),
        "input_boundary": (
            "OrthogonalGeometry only"
        ),
    }


def _phase1_encoder_continuity() -> dict[str, object]:
    corpus = width4.phase_1_corpus()
    matches = 0

    for shape in corpus:
        production = encode_geometry(shape)
        experimental = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        if production == experimental:
            matches += 1

    return {
        "matches": matches,
        "total": len(corpus),
        "exact": matches == len(corpus),
    }


def _frozen_b0_replay() -> dict[str, object]:
    report = width4.analyze_experiment()

    result = {
        "protocol": (
            report["protocol"][
                "dynamic_protocol_imported_from"
            ]
        ),
        "phase_1": {
            "size": report["phase_1"]["size"],
            "distinct_signatures": (
                report["phase_1"]["readers"][
                    "global_multiset"
                ]["distinct_signatures"]
            ),
            "collision_shape_codes": (
                report["phase_1"]["readers"][
                    "global_multiset"
                ]["collision_shape_codes"]
            ),
        },
        "held_out": {
            "size": report["held_out"]["size"],
            "distinct_signatures": (
                report["held_out"]["readers"][
                    "global_multiset"
                ]["distinct_signatures"]
            ),
            "collision_shape_codes": (
                report["held_out"]["readers"][
                    "global_multiset"
                ]["collision_shape_codes"]
            ),
        },
        "extended": {
            "size": report["extended"]["size"],
            "distinct_signatures": (
                report["extended"]["readers"][
                    "global_multiset"
                ]["distinct_signatures"]
            ),
            "collision_shape_codes": (
                report["extended"]["readers"][
                    "global_multiset"
                ]["collision_shape_codes"]
            ),
        },
        "deterministic_replay": (
            report["deterministic_replay"]
        ),
    }

    expected = (
        result["protocol"]
        == "petra-vision-graph-laplacian-v1"
        and result["phase_1"][
            "distinct_signatures"
        ] == 109
        and result["held_out"][
            "distinct_signatures"
        ] == 27
        and result["extended"][
            "distinct_signatures"
        ] == 136
        and result["deterministic_replay"]
    )

    result["matches_frozen_expectation"] = expected

    return result


def _analyze_corpus(
    corpus: tuple[object, ...],
) -> dict[str, object]:
    shape_codes: list[str] = []

    static_signatures: list[object] = []
    baseline_signatures: list[object] = []
    null_signatures: list[object] = []
    coupled_signatures: list[object] = []

    shape_records: list[dict[str, object]] = []

    deterministic = True
    translation_matches_null = 0
    translation_matches_coupled = 0

    total_local_edges = 0
    total_bridge_edges = 0
    maximum_weighted_degree = 0
    geometries_with_bridges = 0

    for shape in corpus:
        code = width4.shape_code(shape)
        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        baseline_signature = (
            width4.experimental_geometry_dynamic_signatures(
                geometry
            )["global_multiset"]
        )

        null_graph = d1.build_distance2_graph(
            geometry,
            bridge_weight=0,
        )

        coupled_graph = d1.build_distance2_graph(
            geometry,
            bridge_weight=d1.BRIDGE_WEIGHT,
        )

        if (
            null_graph.cells
            != coupled_graph.cells
        ):
            raise RuntimeError(
                "matched null changed D1 vertex set"
            )

        if (
            null_graph.original_components
            != coupled_graph.original_components
        ):
            raise RuntimeError(
                "matched null changed original components"
            )

        null_probe = d1.original_component_probe(
            null_graph
        )

        coupled_probe = (
            d1.original_component_probe(
                coupled_graph
            )
        )

        if null_probe != coupled_probe:
            raise RuntimeError(
                "matched null changed the frozen probe"
            )

        static_signature = tuple(
            sorted(null_probe)
        )

        null_signature = (
            d1.coordinate_free_dynamic_signature(
                null_graph,
                null_probe,
            )
        )

        coupled_signature = (
            d1.coordinate_free_dynamic_signature(
                coupled_graph,
                coupled_probe,
            )
        )

        deterministic = (
            deterministic
            and (
                d1.coordinate_free_dynamic_signature(
                    null_graph,
                    null_probe,
                )
                == null_signature
            )
            and (
                d1.coordinate_free_dynamic_signature(
                    coupled_graph,
                    coupled_probe,
                )
                == coupled_signature
            )
        )

        dx, dy = TRANSLATION
        translated = _translate_geometry(
            geometry,
            dx=dx,
            dy=dy,
        )

        translated_null = (
            d1.build_distance2_graph(
                translated,
                bridge_weight=0,
            )
        )

        translated_coupled = (
            d1.build_distance2_graph(
                translated,
                bridge_weight=d1.BRIDGE_WEIGHT,
            )
        )

        translated_null_probe = (
            d1.original_component_probe(
                translated_null
            )
        )

        translated_coupled_probe = (
            d1.original_component_probe(
                translated_coupled
            )
        )

        translated_null_signature = (
            d1.coordinate_free_dynamic_signature(
                translated_null,
                translated_null_probe,
            )
        )

        translated_coupled_signature = (
            d1.coordinate_free_dynamic_signature(
                translated_coupled,
                translated_coupled_probe,
            )
        )

        if translated_null_signature == null_signature:
            translation_matches_null += 1

        if (
            translated_coupled_signature
            == coupled_signature
        ):
            translation_matches_coupled += 1

        stats = _edge_statistics(
            coupled_graph
        )

        total_local_edges += stats[
            "local_edges"
        ]
        total_bridge_edges += stats[
            "bridge_edges"
        ]

        maximum_weighted_degree = max(
            maximum_weighted_degree,
            stats["maximum_weighted_degree"],
        )

        if stats["bridge_edges"] > 0:
            geometries_with_bridges += 1

        shape_codes.append(code)
        static_signatures.append(
            static_signature
        )
        baseline_signatures.append(
            baseline_signature
        )
        null_signatures.append(
            null_signature
        )
        coupled_signatures.append(
            coupled_signature
        )

        shape_records.append({
            "shape": code,
            "occupied_cells": len(
                geometry.cells
            ),
            "d1_graph": stats,
            "signature_sha256": {
                "baseline_b0": (
                    _signature_sha256(
                        baseline_signature
                    )
                ),
                "static_probe_multiset": (
                    _signature_sha256(
                        static_signature
                    )
                ),
                "d1_null": (
                    _signature_sha256(
                        null_signature
                    )
                ),
                "d1_coupled": (
                    _signature_sha256(
                        coupled_signature
                    )
                ),
            },
        })

    codes = tuple(shape_codes)

    static_summary = _summarize(
        codes,
        tuple(static_signatures),
    )

    baseline_summary = _summarize(
        codes,
        tuple(baseline_signatures),
    )

    null_summary = _summarize(
        codes,
        tuple(null_signatures),
    )

    coupled_summary = _summarize(
        codes,
        tuple(coupled_signatures),
    )

    return {
        "size": len(corpus),
        "construction": {
            "geometries_with_bridges": (
                geometries_with_bridges
            ),
            "total_local_edges": (
                total_local_edges
            ),
            "total_bridge_edges": (
                total_bridge_edges
            ),
            "maximum_observed_weighted_degree": (
                maximum_weighted_degree
            ),
            "declared_weighted_degree_bound": (
                d1.MAX_WEIGHTED_DEGREE_BOUND
            ),
            "bound_respected": (
                maximum_weighted_degree
                <= d1.MAX_WEIGHTED_DEGREE_BOUND
            ),
        },
        "readers": {
            "static_probe_multiset": (
                static_summary
            ),
            "baseline_b0_global_multiset": (
                baseline_summary
            ),
            "d1_matched_null": (
                null_summary
            ),
            "d1_coupled": (
                coupled_summary
            ),
        },
        "incremental_vs_null": (
            _incremental_delta(
                null_summary,
                coupled_summary,
            )
        ),
        "known_gate1a_collision": {
            "baseline_b0": (
                _known_collision_status(
                    baseline_summary
                )
            ),
            "d1_matched_null": (
                _known_collision_status(
                    null_summary
                )
            ),
            "d1_coupled": (
                _known_collision_status(
                    coupled_summary
                )
            ),
        },
        "deterministic_replay": deterministic,
        "translation_control": {
            "offset": list(TRANSLATION),
            "matched_null_matches": (
                translation_matches_null
            ),
            "coupled_matches": (
                translation_matches_coupled
            ),
            "total": len(corpus),
            "passed": (
                translation_matches_null
                == len(corpus)
                and translation_matches_coupled
                == len(corpus)
            ),
        },
        "shapes": shape_records,
    }



def _reflection_causality_audit() -> dict[str, object]:
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

    width = max(
        x
        for x, _y in geometry_a.cells
    ) + 1

    def reflect_cell(
        cell: tuple[int, int],
    ) -> tuple[int, int]:
        x, y = cell
        return (width - 1 - x, y)

    reflected_geometry_a = OrthogonalGeometry(
        cells=tuple(sorted(
            reflect_cell(cell)
            for cell in geometry_a.cells
        ))
    )

    exact_geometry_reflection = (
        reflected_geometry_a == geometry_b
    )

    coupled_a = d1.build_distance2_graph(
        geometry_a,
        bridge_weight=d1.BRIDGE_WEIGHT,
    )
    coupled_b = d1.build_distance2_graph(
        geometry_b,
        bridge_weight=d1.BRIDGE_WEIGHT,
    )
    null_a = d1.build_distance2_graph(
        geometry_a,
        bridge_weight=0,
    )
    null_b = d1.build_distance2_graph(
        geometry_b,
        bridge_weight=0,
    )

    index_b = {
        cell: index
        for index, cell in enumerate(
            coupled_b.cells
        )
    }

    reflection_permutation = tuple(
        index_b[reflect_cell(cell)]
        for cell in coupled_a.cells
    )

    def reflected_edge_manifest(
        graph: object,
    ) -> tuple[tuple[int, int, int, str], ...]:
        rows = []

        for edge in graph.edges:
            left = reflection_permutation[
                edge.left
            ]
            right = reflection_permutation[
                edge.right
            ]

            if left > right:
                left, right = right, left

            rows.append((
                left,
                right,
                edge.weight,
                edge.kind,
            ))

        return tuple(sorted(rows))

    def indexed_edge_manifest(
        graph: object,
    ) -> tuple[tuple[int, int, int, str], ...]:
        return tuple(sorted(
            (
                min(edge.left, edge.right),
                max(edge.left, edge.right),
                edge.weight,
                edge.kind,
            )
            for edge in graph.edges
        ))

    coupled_graph_equivariant = (
        reflected_edge_manifest(coupled_a)
        == indexed_edge_manifest(coupled_b)
    )

    null_graph_equivariant = (
        reflected_edge_manifest(null_a)
        == indexed_edge_manifest(null_b)
    )

    reflected_components_a = {
        frozenset(
            reflection_permutation[vertex]
            for vertex in component
        )
        for component
        in coupled_a.original_components
    }

    components_b = {
        frozenset(component)
        for component
        in coupled_b.original_components
    }

    component_partition_equivariant = (
        reflected_components_a
        == components_b
    )

    def frozen_probe(
        graph: object,
        mode: str,
    ) -> tuple[int, ...]:
        state = [0] * len(graph.cells)

        for component in graph.original_components:
            if mode == "minimum":
                state[component[0]] = 1
            elif mode == "maximum":
                state[component[-1]] = 1
            elif mode == "endpoints":
                state[component[0]] = 1
                state[component[-1]] = 1
            else:
                raise ValueError(mode)

        return tuple(state)

    def reflect_state(
        state_a: tuple[int, ...],
    ) -> tuple[int, ...]:
        state_b = [0] * len(state_a)

        for index_a, value in enumerate(
            state_a
        ):
            state_b[
                reflection_permutation[
                    index_a
                ]
            ] = value

        return tuple(state_b)

    frozen_probe_equivariance = {}

    for mode in (
        "minimum",
        "maximum",
        "endpoints",
    ):
        frozen_probe_equivariance[mode] = (
            reflect_state(
                frozen_probe(
                    coupled_a,
                    mode,
                )
            )
            == frozen_probe(
                coupled_b,
                mode,
            )
        )

    transported_matches = {}

    for construction, graph_a, graph_b in (
        ("null", null_a, null_b),
        ("coupled", coupled_a, coupled_b),
    ):
        probe_a = frozen_probe(
            graph_a,
            "minimum",
        )
        reflected_probe_a = reflect_state(
            probe_a
        )

        signature_a = (
            d1.coordinate_free_dynamic_signature(
                graph_a,
                probe_a,
            )
        )
        signature_b = (
            d1.coordinate_free_dynamic_signature(
                graph_b,
                reflected_probe_a,
            )
        )

        transported_matches[construction] = (
            signature_a == signature_b
        )

    independent_minimum_matches = {}

    for construction, graph_a, graph_b in (
        ("null", null_a, null_b),
        ("coupled", coupled_a, coupled_b),
    ):
        signature_a = (
            d1.coordinate_free_dynamic_signature(
                graph_a,
                frozen_probe(
                    graph_a,
                    "minimum",
                ),
            )
        )
        signature_b = (
            d1.coordinate_free_dynamic_signature(
                graph_b,
                frozen_probe(
                    graph_b,
                    "minimum",
                ),
            )
        )

        independent_minimum_matches[
            construction
        ] = signature_a == signature_b

    state_a = frozen_probe(
        coupled_a,
        "minimum",
    )
    state_b = frozen_probe(
        coupled_b,
        "minimum",
    )

    first_divergence = None

    for step in range(1, 33):
        state_a = (
            d1.evolve_weighted_euler_numerator(
                state_a,
                coupled_a,
            )
        )
        state_b = (
            d1.evolve_weighted_euler_numerator(
                state_b,
                coupled_b,
            )
        )

        if (
            first_divergence is None
            and tuple(sorted(state_a))
            != tuple(sorted(state_b))
        ):
            first_divergence = step

    def local_degree_probe(
        graph: object,
    ) -> tuple[int, ...]:
        degree = [0] * len(graph.cells)

        for edge in graph.edges:
            if edge.kind != "local":
                continue

            degree[edge.left] += 1
            degree[edge.right] += 1

        return tuple(degree)

    intrinsic_a = local_degree_probe(
        coupled_a
    )
    intrinsic_b = local_degree_probe(
        coupled_b
    )

    intrinsic_probe_equivariant = (
        reflect_state(intrinsic_a)
        == intrinsic_b
    )

    intrinsic_signatures_match = (
        d1.coordinate_free_dynamic_signature(
            coupled_a,
            intrinsic_a,
        )
        == d1.coordinate_free_dynamic_signature(
            coupled_b,
            intrinsic_b,
        )
    )

    passed = all((
        exact_geometry_reflection,
        coupled_graph_equivariant,
        null_graph_equivariant,
        component_partition_equivariant,
        transported_matches["null"],
        transported_matches["coupled"],
        not independent_minimum_matches[
            "coupled"
        ],
        independent_minimum_matches["null"],
        intrinsic_probe_equivariant,
        intrinsic_signatures_match,
        first_divergence == 2,
    ))

    return {
        "passed": passed,
        "pair": list(EXPECTED_COLLISION),
        "exact_geometry_reflection": (
            exact_geometry_reflection
        ),
        "coupled_graph_reflection_equivariant": (
            coupled_graph_equivariant
        ),
        "matched_null_reflection_equivariant": (
            null_graph_equivariant
        ),
        "original_component_partition_reflection_equivariant": (
            component_partition_equivariant
        ),
        "frozen_probe_reflection_equivariant": (
            frozen_probe_equivariance
        ),
        "transported_minimum_probe_signature_matches": (
            transported_matches
        ),
        "independent_minimum_probe_signature_matches": (
            independent_minimum_matches
        ),
        "first_coupled_minimum_multiset_divergence_step": (
            first_divergence
        ),
        "intrinsic_local_degree_probe_reflection_equivariant": (
            intrinsic_probe_equivariant
        ),
        "intrinsic_local_degree_coupled_signatures_match": (
            intrinsic_signatures_match
        ),
        "classification": (
            "D1 coupling is reflection-equivariant. "
            "The primary 110/110 result is an "
            "incremental effect relative to the matched "
            "null, but the split reflected pair is "
            "produced by global coupling making the "
            "coordinate-derived asymmetric frozen probe "
            "dynamically observable. It is not evidence "
            "that the weighted D1 graph intrinsically "
            "breaks reflection symmetry."
        ),
    }


@lru_cache(maxsize=1)
def analyze_evidence() -> dict[str, object]:
    phase_1 = width4.phase_1_corpus()
    held_out = width4.held_out_corpus()
    extended = width4.extended_corpus()

    if set(phase_1) & set(held_out):
        raise RuntimeError(
            "held-out corpus overlaps Phase 1"
        )

    if set(phase_1) | set(held_out) != set(
        extended
    ):
        raise RuntimeError(
            "Phase 1 + held-out is not the extended domain"
        )

    frozen_b0 = _frozen_b0_replay()

    if not frozen_b0[
        "matches_frozen_expectation"
    ]:
        raise RuntimeError(
            "G2-B0 frozen replay diverged"
        )

    continuity = _phase1_encoder_continuity()

    if not continuity["exact"]:
        raise RuntimeError(
            "Phase 1 experimental encoder diverged "
            "from production geometry"
        )

    source_audit = _source_boundary_audit()

    if not source_audit["passed"]:
        raise RuntimeError(
            "D1 source boundary audit failed"
        )

    reflection_causality = (
        _reflection_causality_audit()
    )

    if not reflection_causality["passed"]:
        raise RuntimeError(
            "D1 reflection causality audit failed"
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

    all_reports = (
        phase_1_report,
        held_out_report,
        extended_report,
    )

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "d1_protocol": d1.PROTOCOL_ID,
            "local_weight": d1.LOCAL_WEIGHT,
            "bridge_weight": d1.BRIDGE_WEIGHT,
            "euler_denominator": (
                d1.EULER_DENOMINATOR
            ),
            "sample_steps": list(
                d1.SAMPLE_STEPS
            ),
            "reader": (
                "global coordinate-free "
                "state multiset"
            ),
            "probe": (
                "unit impulse at the "
                "lexicographically minimum "
                "vertex of each original "
                "four-neighbor occupied "
                "component"
            ),
            "translation_control": list(
                TRANSLATION
            ),
        },
        "source_provenance": {
            "d1_source_sha256": (
                _source_sha256(
                    D1_TOOL_PATH
                )
            ),
            "baseline_v1_source_sha256": (
                _source_sha256(
                    BASELINE_TOOL_PATH
                )
            ),
            "width4_source_sha256": (
                _source_sha256(
                    WIDTH4_TOOL_PATH
                )
            ),
        },
        "frozen_b0_replay": frozen_b0,
        "phase_1_encoder_continuity": (
            continuity
        ),
        "d1_source_boundary_audit": (
            source_audit
        ),
        "reflection_causality_audit": (
            reflection_causality
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
        "deterministic_replay": all(
            report["deterministic_replay"]
            for report in all_reports
        ),
        "translation_control": all(
            report[
                "translation_control"
            ]["passed"]
            for report in all_reports
        ),
        "weighted_degree_bound": all(
            report[
                "construction"
            ]["bound_respected"]
            for report in all_reports
        ),
        "claim_boundary": (
            "bounded Gate 2 D1 coupling "
            "evidence only; no physical, "
            "spectral, decoding, robustness, "
            "or theorem-level claim"
        ),
    }


def render_text_report(
    report: dict[str, object],
) -> str:
    lines = [
        "===== PETRA VISION GATE 2 — D1 EVIDENCE =====",
        f"Protocol: {report['protocol']['id']}",
        (
            "D1 source SHA256: "
            f"{report['source_provenance']['d1_source_sha256']}"
        ),
        "",
        "===== FROZEN G2-B0 REPLAY =====",
    ]

    b0 = report["frozen_b0_replay"]

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = b0[name]
        lines.append(
            f"{label}: "
            f"{item['distinct_signatures']}/"
            f"{item['size']}; "
            f"collisioni="
            f"{item['collision_shape_codes']}"
        )

    lines.extend([
        (
            "B0 conforme al congelato: "
            f"{b0['matches_frozen_expectation']}"
        ),
        "",
        "===== D1 NULL / COUPLED =====",
    ])

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = report[name]
        null = item["readers"][
            "d1_matched_null"
        ]
        coupled = item["readers"][
            "d1_coupled"
        ]
        delta = item[
            "incremental_vs_null"
        ]
        collision = item[
            "known_gate1a_collision"
        ]

        lines.extend([
            (
                f"{label}: "
                f"{item['size']} forme"
            ),
            (
                "  null:    "
                f"{null['distinct_signatures']}/"
                f"{item['size']}; "
                f"collisioni="
                f"{null['collision_shape_codes']}"
            ),
            (
                "  coupled: "
                f"{coupled['distinct_signatures']}/"
                f"{item['size']}; "
                f"collisioni="
                f"{coupled['collision_shape_codes']}"
            ),
            (
                "  gain distinct: "
                f"{delta['distinct_signature_gain']}"
            ),
            (
                "  collision-pairs split: "
                f"{delta['split_by_coupling_count']}"
            ),
            (
                "  collision-pairs introdotte: "
                f"{delta['introduced_by_coupling_count']}"
            ),
            (
                "  #23/#41 baseline/null/coupled: "
                f"{collision['baseline_b0']['collides']} / "
                f"{collision['d1_matched_null']['collides']} / "
                f"{collision['d1_coupled']['collides']}"
            ),
            (
                "  geometrie con bridge: "
                f"{item['construction']['geometries_with_bridges']}/"
                f"{item['size']}"
            ),
            (
                "  bridge totali: "
                f"{item['construction']['total_bridge_edges']}"
            ),
            (
                "  max weighted degree osservato: "
                f"{item['construction']['maximum_observed_weighted_degree']}"
            ),
            "",
        ])

    lines.extend([
        "===== AUDIT =====",
        (
            "Phase 1 encoder continuity: "
            f"{report['phase_1_encoder_continuity']['matches']}/"
            f"{report['phase_1_encoder_continuity']['total']}"
        ),
        (
            "D1 source boundary: "
            f"{report['d1_source_boundary_audit']['passed']}"
        ),
        (
            "Reflection causality audit: "
            f"{report['reflection_causality_audit']['passed']}"
        ),
        (
            "Causal classification: "
            f"{report['reflection_causality_audit']['classification']}"
        ),
        (
            "Translation control: "
            f"{report['translation_control']}"
        ),
        (
            "Weighted-degree bound: "
            f"{report['weighted_degree_bound']}"
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
            "Run PETRA VISION Gate 2 D1 "
            "global geometric coupling evidence."
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
        report["frozen_b0_replay"][
            "matches_frozen_expectation"
        ]
        and report[
            "phase_1_encoder_continuity"
        ]["exact"]
        and report[
            "d1_source_boundary_audit"
        ]["passed"]
        and report[
            "reflection_causality_audit"
        ]["passed"]
        and report["deterministic_replay"]
        and report["translation_control"]
        and report["weighted_degree_bound"]
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
