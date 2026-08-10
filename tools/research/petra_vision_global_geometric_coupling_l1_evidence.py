#!/usr/bin/env python3
"""Deterministic evidence for PETRA VISION Gate 2 G2-L1."""

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
    "petra-vision-global-geometric-coupling-full-lattice-evidence-v0"
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


l1 = _load_module(
    L1_TOOL_PATH,
    "_petra_vision_gate2_l1_evidence_l1",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate2_l1_evidence_width4",
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
    pairs: set[tuple[str, str]] = set()

    for raw_group in summary[
        "collision_shape_codes"
    ]:
        group = tuple(raw_group)

        for left, right in combinations(
            group,
            2,
        ):
            pairs.add(
                tuple(sorted((left, right)))
            )

    return pairs


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
        "split_by_coupling_count": (
            len(split)
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
        L1_TOOL_PATH.read_text(
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

    graph_a = l1.build_full_lattice_graph(
        geometry_a,
        coupled=True,
    )
    graph_b = l1.build_full_lattice_graph(
        geometry_b,
        coupled=True,
    )

    width_a = (
        max(x for x, _y in graph_a.cells)
        - min(x for x, _y in graph_a.cells)
        + 1
    )
    height_a = (
        max(y for _x, y in graph_a.cells)
        - min(y for _x, y in graph_a.cells)
        + 1
    )

    width_b = (
        max(x for x, _y in graph_b.cells)
        - min(x for x, _y in graph_b.cells)
        + 1
    )
    height_b = (
        max(y for _x, y in graph_b.cells)
        - min(y for _x, y in graph_b.cells)
        + 1
    )

    null_match = (
        l1.full_lattice_signature(
            geometry_a,
            coupled=False,
        )
        == l1.full_lattice_signature(
            geometry_b,
            coupled=False,
        )
    )

    coupled_match = (
        l1.full_lattice_signature(
            geometry_a,
            coupled=True,
        )
        == l1.full_lattice_signature(
            geometry_b,
            coupled=True,
        )
    )

    passed = all((
        width_a == width_b,
        height_a == height_b,
        len(graph_a.cells) == len(
            graph_b.cells
        ),
        null_match,
        coupled_match,
    ))

    return {
        "passed": passed,
        "pair": list(EXPECTED_COLLISION),
        "same_bounding_width": (
            width_a == width_b
        ),
        "same_bounding_height": (
            height_a == height_b
        ),
        "same_lattice_vertex_count": (
            len(graph_a.cells)
            == len(graph_b.cells)
        ),
        "null_match": null_match,
        "coupled_match": coupled_match,
    }


def _translation_audit() -> dict[str, object]:
    shapes = width4.phase_1_corpus()

    matched_null = 0
    matched_coupled = 0

    for shape in shapes:
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
            l1.full_lattice_signature(
                geometry,
                coupled=False,
            )
            == l1.full_lattice_signature(
                translated,
                coupled=False,
            )
        ):
            matched_null += 1

        if (
            l1.full_lattice_signature(
                geometry,
                coupled=True,
            )
            == l1.full_lattice_signature(
                translated,
                coupled=True,
            )
        ):
            matched_coupled += 1

    return {
        "passed": (
            matched_null == len(shapes)
            and matched_coupled == len(
                shapes
            )
        ),
        "offset": [11, 7],
        "null_matches": matched_null,
        "coupled_matches": matched_coupled,
        "total": len(shapes),
    }


def _analyze_corpus(
    corpus: tuple[object, ...],
) -> dict[str, object]:
    codes: list[str] = []

    lattice_size_signatures: list[object] = []
    static_signatures: list[object] = []
    null_signatures: list[object] = []
    coupled_signatures: list[object] = []

    records: list[dict[str, object]] = []

    lattice_vertex_distribution: Counter[int] = Counter()
    occupied_distribution: Counter[int] = Counter()
    empty_distribution: Counter[int] = Counter()

    maximum_observed_degree = 0
    total_lattice_vertices = 0
    total_lattice_edges = 0
    geometries_with_empty_sites = 0
    deterministic_matches = 0

    for shape in corpus:
        code = width4.shape_code(shape)

        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        coupled_graph = (
            l1.build_full_lattice_graph(
                geometry,
                coupled=True,
            )
        )

        null_graph = (
            l1.build_full_lattice_graph(
                geometry,
                coupled=False,
            )
        )

        if (
            coupled_graph.cells
            != null_graph.cells
            or coupled_graph.initial_state
            != null_graph.initial_state
        ):
            raise RuntimeError(
                "L1 matched null changed domain or initial field"
            )

        lattice_vertices = len(
            coupled_graph.cells
        )
        occupied = sum(
            coupled_graph.initial_state
        )
        empty = lattice_vertices - occupied

        lattice_vertex_distribution[
            lattice_vertices
        ] += 1
        occupied_distribution[
            occupied
        ] += 1
        empty_distribution[
            empty
        ] += 1

        total_lattice_vertices += (
            lattice_vertices
        )
        total_lattice_edges += len(
            coupled_graph.edges
        )

        if empty > 0:
            geometries_with_empty_sites += 1

        observed_degree = l1.maximum_degree(
            coupled_graph
        )

        maximum_observed_degree = max(
            maximum_observed_degree,
            observed_degree,
        )

        lattice_size_signature = (
            lattice_vertices
        )

        static_signature = tuple(sorted(
            coupled_graph.initial_state
        ))

        null_signature = (
            l1.full_lattice_signature(
                geometry,
                coupled=False,
            )
        )

        coupled_signature = (
            l1.full_lattice_signature(
                geometry,
                coupled=True,
            )
        )

        replay = (
            l1.full_lattice_signature(
                geometry,
                coupled=True,
            )
        )

        if replay == coupled_signature:
            deterministic_matches += 1

        codes.append(code)
        lattice_size_signatures.append(
            lattice_size_signature
        )
        static_signatures.append(
            static_signature
        )
        null_signatures.append(
            null_signature
        )
        coupled_signatures.append(
            coupled_signature
        )

        records.append({
            "shape": code,
            "lattice_vertices": (
                lattice_vertices
            ),
            "occupied_sites": occupied,
            "empty_sites": empty,
            "lattice_edges": len(
                coupled_graph.edges
            ),
            "maximum_degree": (
                observed_degree
            ),
            "static_sha256": (
                _signature_sha256(
                    static_signature
                )
            ),
            "null_sha256": (
                _signature_sha256(
                    null_signature
                )
            ),
            "coupled_sha256": (
                _signature_sha256(
                    coupled_signature
                )
            ),
        })

    frozen_codes = tuple(codes)

    lattice_size_summary = _summarize(
        frozen_codes,
        tuple(lattice_size_signatures),
    )

    static_summary = _summarize(
        frozen_codes,
        tuple(static_signatures),
    )

    null_summary = _summarize(
        frozen_codes,
        tuple(null_signatures),
    )

    coupled_summary = _summarize(
        frozen_codes,
        tuple(coupled_signatures),
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
            "maximum_observed_degree": (
                maximum_observed_degree
            ),
            "maximum_degree_bound": (
                l1.MAXIMUM_DEGREE_BOUND
            ),
            "euler_denominator": (
                l1.EULER_DENOMINATOR
            ),
            "degree_bound_passed": (
                maximum_observed_degree
                <= l1.MAXIMUM_DEGREE_BOUND
                < l1.EULER_DENOMINATOR
            ),
            "lattice_vertex_distribution": {
                str(value): count
                for value, count in sorted(
                    lattice_vertex_distribution.items()
                )
            },
            "occupied_site_distribution": {
                str(value): count
                for value, count in sorted(
                    occupied_distribution.items()
                )
            },
            "empty_site_distribution": {
                str(value): count
                for value, count in sorted(
                    empty_distribution.items()
                )
            },
        },
        "readers": {
            "lattice_size_only": (
                lattice_size_summary
            ),
            "step0_static_multiset": (
                static_summary
            ),
            "l1_matched_null": (
                null_summary
            ),
            "l1_coupled": (
                coupled_summary
            ),
        },
        "incremental_vs_null": (
            _delta(
                null_summary,
                coupled_summary,
            )
        ),
        "known_gate1a_collision": {
            "step0_static_multiset": (
                _known_collision_status(
                    static_summary
                )
            ),
            "l1_matched_null": (
                _known_collision_status(
                    null_summary
                )
            ),
            "l1_coupled": (
                _known_collision_status(
                    coupled_summary
                )
            ),
        },
        "null_equals_static_partition": (
            _collision_pairs(
                null_summary
            )
            == _collision_pairs(
                static_summary
            )
            and null_summary[
                "distinct_signatures"
            ]
            == static_summary[
                "distinct_signatures"
            ]
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
            "L1 source boundary audit failed"
        )

    reflection = _reflection_audit()

    if not reflection["passed"]:
        raise RuntimeError(
            "L1 reflection control failed"
        )

    translation = _translation_audit()

    if not translation["passed"]:
        raise RuntimeError(
            "L1 translation control failed"
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

        if not (
            known[
                "l1_matched_null"
            ]["collides"]
            and known[
                "l1_coupled"
            ]["collides"]
        ):
            raise RuntimeError(
                "L1 violated frozen reflected-pair control"
            )

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "l1_protocol": l1.PROTOCOL_ID,
            "euler_denominator": (
                l1.EULER_DENOMINATOR
            ),
            "maximum_degree_bound": (
                l1.MAXIMUM_DEGREE_BOUND
            ),
            "sample_steps": list(
                l1.SAMPLE_STEPS
            ),
            "domain": (
                "exact minimal axis-aligned bounding rectangle"
            ),
            "medium": (
                "uniform four-neighbor lattice"
            ),
            "initial_field": (
                "binary occupancy indicator"
            ),
            "primary_reader": (
                "global multiset of complete scalar lattice state"
            ),
        },
        "source_provenance": {
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
        "null_equals_static_partition": all(
            report[
                "null_equals_static_partition"
            ]
            for report in reports
        ),
        "deterministic_replay": all(
            report["deterministic_replay"]
            for report in reports
        ),
        "known_reflected_pair_preserved": (
            reflection["null_match"]
            and reflection["coupled_match"]
        ),
        "claim_boundary": (
            "bounded Gate 2 L1 uniform-lattice evidence only; "
            "occupancy is initial state only; no FGS, structural "
            "identity, intrinsic reflection breaking, spectral, "
            "robustness, physical, decoding, or theorem-level claim"
        ),
    }


def render_text_report(
    report: dict[str, object],
) -> str:
    lines = [
        "===== PETRA VISION GATE 2 — L1 EVIDENCE =====",
        f"Protocol: {report['protocol']['id']}",
        (
            "L1 source SHA256: "
            f"{report['source_provenance']['l1_source_sha256']}"
        ),
        "",
        "===== G2-L1 =====",
    ]

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = report[name]

        size_only = item["readers"][
            "lattice_size_only"
        ]
        static = item["readers"][
            "step0_static_multiset"
        ]
        null = item["readers"][
            "l1_matched_null"
        ]
        coupled = item["readers"][
            "l1_coupled"
        ]
        delta = item[
            "incremental_vs_null"
        ]
        known = item[
            "known_gate1a_collision"
        ]

        lines.extend([
            f"{label}: {item['size']} forme",
            (
                "  lattice size: "
                f"{size_only['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  step0 static: "
                f"{static['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  matched null: "
                f"{null['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  L1 coupled:   "
                f"{coupled['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  gain:         "
                f"{delta['distinct_signature_gain']}"
            ),
            (
                "  split collision-pairs: "
                f"{delta['split_by_coupling_count']}"
            ),
            (
                "  new collision-pairs:   "
                f"{delta['introduced_by_coupling_count']}"
            ),
            (
                "  #23/#41 null/coupled: "
                f"{known['l1_matched_null']['collides']} / "
                f"{known['l1_coupled']['collides']}"
            ),
            (
                "  geometrie con empty sites: "
                f"{item['construction']['geometries_with_empty_sites']}/"
                f"{item['size']}"
            ),
            (
                "  lattice vertices totali: "
                f"{item['construction']['total_lattice_vertices']}"
            ),
            (
                "  lattice edges totali: "
                f"{item['construction']['total_lattice_edges']}"
            ),
            (
                "  max degree osservato: "
                f"{item['construction']['maximum_observed_degree']}"
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
            "Degree bound 4 < 8: "
            f"{report['degree_bound_passed']}"
        ),
        (
            "Matched null partition == static partition: "
            f"{report['null_equals_static_partition']}"
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
            "Run PETRA VISION Gate 2 G2-L1 evidence."
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
        and report[
            "null_equals_static_partition"
        ]
        and report["deterministic_replay"]
        and report[
            "known_reflected_pair_preserved"
        ]
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
