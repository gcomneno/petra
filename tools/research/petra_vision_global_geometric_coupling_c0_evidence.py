#!/usr/bin/env python3
"""Deterministic evidence for PETRA VISION Gate 2 G2-C0."""

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


C0_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_c0.py"
)

V1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-component-null-evidence-v0"
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


c0 = _load_module(
    C0_TOOL_PATH,
    "_petra_vision_gate2_c0_evidence_c0",
)

v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate2_c0_evidence_v1",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate2_c0_evidence_width4",
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
    baseline: dict[str, object],
    candidate: dict[str, object],
) -> dict[str, object]:
    baseline_pairs = _collision_pairs(
        baseline
    )
    candidate_pairs = _collision_pairs(
        candidate
    )

    split = sorted(
        baseline_pairs - candidate_pairs
    )
    introduced = sorted(
        candidate_pairs - baseline_pairs
    )

    return {
        "distinct_signature_gain": (
            int(candidate[
                "distinct_signatures"
            ])
            - int(baseline[
                "distinct_signatures"
            ])
        ),
        "baseline_collision_pair_count": (
            len(baseline_pairs)
        ),
        "candidate_collision_pair_count": (
            len(candidate_pairs)
        ),
        "split_by_representation_count": (
            len(split)
        ),
        "split_by_representation": [
            list(pair)
            for pair in split
        ],
        "introduced_by_representation_count": (
            len(introduced)
        ),
        "introduced_by_representation": [
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
        C0_TOOL_PATH.read_text(
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

    source = C0_TOOL_PATH.read_text(
        encoding="utf-8"
    )

    return {
        "passed": (
            petra_imports
            == ["petra.vision.geometry"]
            and not (
                referenced_names
                & forbidden_names
            )
            and "v1.geometry_dynamic_signatures("
            in source
            and '"global_multiset"' in source
        ),
        "petra_imports": petra_imports,
        "forbidden_references": sorted(
            referenced_names
            & forbidden_names
        ),
        "inner_protocol": (
            c0.INNER_PROTOCOL_ID
        ),
        "inner_reader": (
            "frozen v1 global_multiset"
        ),
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


def _redisplace_components(
    geometry: object,
):
    geometry_type = type(geometry)

    components = list(
        reversed(
            c0.connected_component_geometries(
                geometry
            )
        )
    )

    cells = []
    cursor_x = 0

    for component in components:
        width = (
            max(
                x
                for x, _y in component.cells
            )
            + 1
        )

        cells.extend(
            (
                cursor_x + x,
                y,
            )
            for x, y in component.cells
        )

        cursor_x += width + 7

    return geometry_type(
        cells=tuple(sorted(cells))
    )


def _translation_displacement_audit() -> dict[str, object]:
    corpus = width4.phase_1_corpus()

    translation_matches = 0
    displacement_matches = 0

    for shape in corpus:
        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        translated = _translate_geometry(
            geometry,
            dx=17,
            dy=11,
        )

        displaced = _redisplace_components(
            geometry
        )

        signature = (
            c0.component_null_signature(
                geometry
            )
        )

        if (
            signature
            == c0.component_null_signature(
                translated
            )
        ):
            translation_matches += 1

        if (
            signature
            == c0.component_null_signature(
                displaced
            )
        ):
            displacement_matches += 1

    total = len(corpus)

    return {
        "passed": (
            translation_matches == total
            and displacement_matches == total
        ),
        "translation_matches": (
            translation_matches
        ),
        "displacement_and_order_matches": (
            displacement_matches
        ),
        "total": total,
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

    c0_match = (
        c0.component_null_signature(
            geometry_a
        )
        == c0.component_null_signature(
            geometry_b
        )
    )

    component_shapes_match = (
        v1.normalized_component_shapes(
            geometry_a
        )
        == v1.normalized_component_shapes(
            geometry_b
        )
    )

    return {
        "passed": (
            c0_match
            and component_shapes_match
        ),
        "pair": list(EXPECTED_COLLISION),
        "normalized_component_shapes_match": (
            component_shapes_match
        ),
        "c0_match": c0_match,
    }


def _analyze_corpus(
    corpus: tuple[object, ...],
) -> dict[str, object]:
    codes: list[str] = []

    component_count_signatures: list[object] = []
    static_profile_signatures: list[object] = []
    b0_signatures: list[object] = []
    c0_signatures: list[object] = []

    component_count_distribution: Counter[int] = Counter()

    total_components = 0
    maximum_components = 0
    exact_partition_count = 0
    multiplicity_matches = 0
    deterministic_matches = 0

    records: list[dict[str, object]] = []

    for shape in corpus:
        code = width4.shape_code(shape)

        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        components = (
            c0.connected_component_geometries(
                geometry
            )
        )

        component_count = len(
            components
        )

        total_components += component_count
        maximum_components = max(
            maximum_components,
            component_count,
        )
        component_count_distribution[
            component_count
        ] += 1

        graph = v1.build_geometry_graph(
            geometry
        )

        if (
            len(graph.components)
            == component_count
            and sum(
                len(component.cells)
                for component in components
            )
            == len(geometry.cells)
        ):
            exact_partition_count += 1

        normalized_from_c0 = tuple(sorted(
            component.cells
            for component in components
        ))

        normalized_from_v1 = (
            v1.normalized_component_shapes(
                geometry
            )
        )

        if (
            normalized_from_c0
            == normalized_from_v1
        ):
            multiplicity_matches += 1

        component_count_signature = (
            component_count
        )

        static_profile = (
            c0.static_component_profile_signature(
                geometry
            )
        )

        b0_signature = (
            v1.geometry_dynamic_signatures(
                geometry
            )["global_multiset"]
        )

        c0_signature = (
            c0.component_null_signature(
                geometry
            )
        )

        if (
            c0.component_null_signature(
                geometry
            )
            == c0_signature
        ):
            deterministic_matches += 1

        codes.append(code)

        component_count_signatures.append(
            component_count_signature
        )
        static_profile_signatures.append(
            static_profile
        )
        b0_signatures.append(
            b0_signature
        )
        c0_signatures.append(
            c0_signature
        )

        records.append({
            "shape": code,
            "component_count": (
                component_count
            ),
            "component_count_sha256": (
                _signature_sha256(
                    component_count_signature
                )
            ),
            "static_profile_sha256": (
                _signature_sha256(
                    static_profile
                )
            ),
            "b0_sha256": (
                _signature_sha256(
                    b0_signature
                )
            ),
            "c0_sha256": (
                _signature_sha256(
                    c0_signature
                )
            ),
        })

    frozen_codes = tuple(codes)

    count_summary = _summarize(
        frozen_codes,
        tuple(
            component_count_signatures
        ),
    )

    static_summary = _summarize(
        frozen_codes,
        tuple(
            static_profile_signatures
        ),
    )

    b0_summary = _summarize(
        frozen_codes,
        tuple(b0_signatures),
    )

    c0_summary = _summarize(
        frozen_codes,
        tuple(c0_signatures),
    )

    return {
        "size": len(corpus),
        "construction": {
            "total_component_occurrences": (
                total_components
            ),
            "maximum_component_count": (
                maximum_components
            ),
            "component_count_distribution": {
                str(count): occurrences
                for count, occurrences in sorted(
                    component_count_distribution.items()
                )
            },
        },
        "readers": {
            "component_count_only": (
                count_summary
            ),
            "static_component_profile": (
                static_summary
            ),
            "frozen_b0_global_multiset": (
                b0_summary
            ),
            "c0_component_multiset": (
                c0_summary
            ),
        },
        "incremental_c0_vs_b0": (
            _delta(
                b0_summary,
                c0_summary,
            )
        ),
        "known_gate1a_collision": {
            "frozen_b0_global_multiset": (
                _known_collision_status(
                    b0_summary
                )
            ),
            "c0_component_multiset": (
                _known_collision_status(
                    c0_summary
                )
            ),
        },
        "exact_component_partition": (
            exact_partition_count
            == len(corpus)
        ),
        "component_multiplicity_preserved": (
            multiplicity_matches
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
            "C0 source boundary audit failed"
        )

    displacement = (
        _translation_displacement_audit()
    )

    if not displacement["passed"]:
        raise RuntimeError(
            "C0 translation/displacement audit failed"
        )

    reflection = _reflection_audit()

    if not reflection["passed"]:
        raise RuntimeError(
            "C0 reflected-pair audit failed"
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

        if not known[
            "c0_component_multiset"
        ]["collides"]:
            raise RuntimeError(
                "C0 violated frozen component-order collision"
            )

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "c0_protocol": c0.PROTOCOL_ID,
            "inner_protocol": (
                c0.INNER_PROTOCOL_ID
            ),
            "component_adjacency": (
                c0.COMPONENT_ADJACENCY
            ),
            "sample_steps": list(
                c0.SAMPLE_STEPS
            ),
            "inner_reader": (
                "frozen v1 global_multiset"
            ),
            "final_reader": (
                "unordered multiplicity-preserving "
                "multiset of per-component signatures"
            ),
        },
        "source_provenance": {
            "c0_source_sha256": (
                _source_sha256(
                    C0_TOOL_PATH
                )
            ),
            "v1_source_sha256": (
                _source_sha256(
                    V1_TOOL_PATH
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
        "translation_displacement_audit": (
            displacement
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
        "exact_component_partition": all(
            report[
                "exact_component_partition"
            ]
            for report in reports
        ),
        "component_multiplicity_preserved": all(
            report[
                "component_multiplicity_preserved"
            ]
            for report in reports
        ),
        "deterministic_replay": all(
            report[
                "deterministic_replay"
            ]
            for report in reports
        ),
        "known_reflected_pair_preserved": (
            reflection["c0_match"]
        ),
        "claim_boundary": (
            "bounded Gate 2 C0 representation-control evidence only; "
            "any gain over B0 is attributed to preserving disconnected "
            "component boundaries, not to global geometric coupling"
        ),
    }


def render_text_report(
    report: dict[str, object],
) -> str:
    lines = [
        "===== PETRA VISION GATE 2 — C0 EVIDENCE =====",
        f"Protocol: {report['protocol']['id']}",
        (
            "C0 source SHA256: "
            f"{report['source_provenance']['c0_source_sha256']}"
        ),
        "",
        "===== G2-C0 =====",
    ]

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = report[name]
        readers = item["readers"]

        count = readers[
            "component_count_only"
        ]
        static = readers[
            "static_component_profile"
        ]
        b0 = readers[
            "frozen_b0_global_multiset"
        ]
        c0_reader = readers[
            "c0_component_multiset"
        ]

        delta = item[
            "incremental_c0_vs_b0"
        ]

        known = item[
            "known_gate1a_collision"
        ]

        lines.extend([
            f"{label}: {item['size']} forme",
            (
                "  component count: "
                f"{count['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  static component profile: "
                f"{static['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  frozen B0: "
                f"{b0['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  C0 dynamic: "
                f"{c0_reader['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  C0 gain vs B0: "
                f"{delta['distinct_signature_gain']}"
            ),
            (
                "  B0 collision-pairs split: "
                f"{delta['split_by_representation_count']}"
            ),
            (
                "  new collision-pairs: "
                f"{delta['introduced_by_representation_count']}"
            ),
            (
                "  #23/#41 B0/C0: "
                f"{known['frozen_b0_global_multiset']['collides']} / "
                f"{known['c0_component_multiset']['collides']}"
            ),
            (
                "  component occurrences: "
                f"{item['construction']['total_component_occurrences']}"
            ),
            (
                "  max components: "
                f"{item['construction']['maximum_component_count']}"
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
            "Translation/displacement/order control: "
            f"{report['translation_displacement_audit']['passed']}"
        ),
        (
            "Reflection/reordered control: "
            f"{report['reflection_audit']['passed']}"
        ),
        (
            "Exact component partition: "
            f"{report['exact_component_partition']}"
        ),
        (
            "Multiplicity preserved: "
            f"{report['component_multiplicity_preserved']}"
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
            "Run PETRA VISION Gate 2 G2-C0 evidence."
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
        and report[
            "translation_displacement_audit"
        ]["passed"]
        and report["reflection_audit"][
            "passed"
        ]
        and report[
            "exact_component_partition"
        ]
        and report[
            "component_multiplicity_preserved"
        ]
        and report[
            "deterministic_replay"
        ]
        and report[
            "known_reflected_pair_preserved"
        ]
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
