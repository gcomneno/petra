#!/usr/bin/env python3
"""Deterministic evidence for PETRA VISION Gate 2 G2-F0."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


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
    "petra-vision-global-geometric-coupling-fgs-null-evidence-v0"
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


f0 = _load_module(
    F0_TOOL_PATH,
    "_petra_vision_gate2_f0_evidence_f0",
)

fgs = _load_module(
    FGS_TOOL_PATH,
    "_petra_vision_gate2_f0_evidence_fgs",
)

v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate2_f0_evidence_v1",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate2_f0_evidence_width4",
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
        "containing_collision_group": containing_group,
    }


def _static_factor_profile(
    factor: object,
) -> tuple[object, ...]:
    graph = v1.build_geometry_graph(factor)
    profile = v1.graph_profile(graph)

    return (
        profile["vertices"],
        profile["edges"],
        profile["components"],
        profile["isolated_vertices"],
        tuple(profile["component_cycle_ranks"]),
        profile["maximum_degree"],
    )


def _static_factor_multiset(
    geometry: object,
) -> tuple[tuple[object, ...], ...]:
    return tuple(sorted(
        _static_factor_profile(factor)
        for factor in f0.immediate_factors(
            geometry
        )
    ))


def _source_boundary_audit() -> dict[str, object]:
    tree = ast.parse(
        F0_TOOL_PATH.read_text(
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

    source = F0_TOOL_PATH.read_text(
        encoding="utf-8"
    )

    forbidden_coupling_fragments = sorted(
        fragment
        for fragment in (
            "build_distance2_graph",
            "bridge_weight",
            "evolve_weighted_euler_numerator",
            "message_passing",
            "shared_state",
        )
        if fragment in source
    )

    return {
        "passed": (
            petra_imports
            == ["petra.vision.geometry"]
            and not forbidden_references
            and not forbidden_coupling_fragments
        ),
        "input_boundary": "OrthogonalGeometry only",
        "petra_imports": petra_imports,
        "forbidden_references": forbidden_references,
        "forbidden_coupling_fragments": (
            forbidden_coupling_fragments
        ),
    }


def _frozen_b0_summary() -> dict[str, object]:
    report = width4.analyze_experiment()

    result = {}

    for name in (
        "phase_1",
        "held_out",
        "extended",
    ):
        reader = report[name]["readers"][
            "global_multiset"
        ]

        result[name] = {
            "size": report[name]["size"],
            "distinct_signatures": (
                reader["distinct_signatures"]
            ),
            "collision_shape_codes": (
                reader["collision_shape_codes"]
            ),
        }

    result["matches_frozen_expectation"] = (
        result["phase_1"]["distinct_signatures"] == 109
        and result["held_out"]["distinct_signatures"] == 27
        and result["extended"]["distinct_signatures"] == 136
        and report["deterministic_replay"]
    )

    return result


def _analyze_corpus(
    corpus: tuple[object, ...],
) -> dict[str, object]:
    codes: list[str] = []

    factor_count_signatures: list[object] = []
    static_signatures: list[object] = []
    ordered_dynamic_signatures: list[object] = []
    f0_signatures: list[object] = []

    records: list[dict[str, object]] = []

    factor_count_distribution: Counter[int] = Counter()

    total_factor_occurrences = 0
    repeated_dynamic_signature_geometries = 0
    recomposition_matches = 0
    deterministic_matches = 0

    for shape in corpus:
        code = width4.shape_code(shape)
        geometry = (
            width4.encode_experimental_geometry(
                shape
            )
        )

        factors = f0.immediate_factors(
            geometry
        )

        factor_count = len(factors)
        factor_count_distribution[
            factor_count
        ] += 1
        total_factor_occurrences += factor_count

        if fgs.recompose_fgs(factors) == geometry:
            recomposition_matches += 1

        static_signature = (
            _static_factor_multiset(
                geometry
            )
        )

        ordered_dynamic = (
            f0.ordered_factor_signatures(
                geometry
            )
        )

        primary = (
            f0.factor_multiset_signature(
                geometry
            )
        )

        replay = (
            f0.factor_multiset_signature(
                geometry
            )
        )

        if replay == primary:
            deterministic_matches += 1

        if len(set(primary)) < len(primary):
            repeated_dynamic_signature_geometries += 1

        codes.append(code)
        factor_count_signatures.append(
            factor_count
        )
        static_signatures.append(
            static_signature
        )
        ordered_dynamic_signatures.append(
            ordered_dynamic
        )
        f0_signatures.append(
            primary
        )

        records.append({
            "shape": code,
            "immediate_factor_count": (
                factor_count
            ),
            "factor_multiplicity_preserved": (
                len(primary) == factor_count
            ),
            "static_factor_profile_sha256": (
                _signature_sha256(
                    static_signature
                )
            ),
            "ordered_dynamic_sha256": (
                _signature_sha256(
                    ordered_dynamic
                )
            ),
            "f0_unordered_dynamic_sha256": (
                _signature_sha256(
                    primary
                )
            ),
        })

    frozen_codes = tuple(codes)

    factor_count_summary = _summarize(
        frozen_codes,
        tuple(factor_count_signatures),
    )

    static_summary = _summarize(
        frozen_codes,
        tuple(static_signatures),
    )

    ordered_summary = _summarize(
        frozen_codes,
        tuple(ordered_dynamic_signatures),
    )

    f0_summary = _summarize(
        frozen_codes,
        tuple(f0_signatures),
    )

    return {
        "size": len(corpus),
        "factorization": {
            "total_immediate_factor_occurrences": (
                total_factor_occurrences
            ),
            "factor_count_distribution": {
                str(count): occurrences
                for count, occurrences in sorted(
                    factor_count_distribution.items()
                )
            },
            "recomposition_matches": (
                recomposition_matches
            ),
            "recomposition_total": len(corpus),
            "exact_recomposition": (
                recomposition_matches
                == len(corpus)
            ),
            "repeated_dynamic_signature_geometries": (
                repeated_dynamic_signature_geometries
            ),
        },
        "readers": {
            "factor_count_only": (
                factor_count_summary
            ),
            "static_factor_profile_multiset": (
                static_summary
            ),
            "ordered_factor_dynamic_control": (
                ordered_summary
            ),
            "f0_unordered_factor_dynamic": (
                f0_summary
            ),
        },
        "known_gate1a_collision": {
            "factor_count_only": (
                _known_collision_status(
                    factor_count_summary
                )
            ),
            "static_factor_profile_multiset": (
                _known_collision_status(
                    static_summary
                )
            ),
            "ordered_factor_dynamic_control": (
                _known_collision_status(
                    ordered_summary
                )
            ),
            "f0_unordered_factor_dynamic": (
                _known_collision_status(
                    f0_summary
                )
            ),
        },
        "deterministic_replay": (
            deterministic_matches
            == len(corpus)
        ),
        "multiplicity_preserved": all(
            record[
                "factor_multiplicity_preserved"
            ]
            for record in records
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
            "held-out corpus overlaps Phase 1"
        )

    if (
        set(phase_1) | set(held_out)
        != set(extended)
    ):
        raise RuntimeError(
            "Phase 1 + held-out does not equal extended corpus"
        )

    source_audit = _source_boundary_audit()

    if not source_audit["passed"]:
        raise RuntimeError(
            "F0 source boundary audit failed"
        )

    frozen_b0 = _frozen_b0_summary()

    if not frozen_b0[
        "matches_frozen_expectation"
    ]:
        raise RuntimeError(
            "frozen G2-B0 replay diverged"
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

    phase1_collision = phase_1_report[
        "known_gate1a_collision"
    ]["f0_unordered_factor_dynamic"][
        "collides"
    ]

    extended_collision = extended_report[
        "known_gate1a_collision"
    ]["f0_unordered_factor_dynamic"][
        "collides"
    ]

    if not (
        phase1_collision
        and extended_collision
    ):
        raise RuntimeError(
            "F0 violated frozen reflected-pair control"
        )

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "f0_protocol": f0.PROTOCOL_ID,
            "dynamic_protocol": (
                f0.DYNAMIC_PROTOCOL_ID
            ),
            "reader": f0.READER_ID,
            "scope": (
                "immediate native FGS factors only"
            ),
            "inter_factor_coupling": False,
            "factor_order_primary_reader": False,
            "factor_multiplicity_preserved": True,
        },
        "source_provenance": {
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
        "frozen_b0_replay": frozen_b0,
        "source_boundary_audit": (
            source_audit
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
            for report in reports
        ),
        "exact_recomposition": all(
            report["factorization"][
                "exact_recomposition"
            ]
            for report in reports
        ),
        "multiplicity_preserved": all(
            report["multiplicity_preserved"]
            for report in reports
        ),
        "known_reflected_pair_preserved": (
            phase1_collision
            and extended_collision
        ),
        "claim_boundary": (
            "bounded G2-F0 factor-boundary null evidence only; "
            "ordered factor observation is diagnostic only; "
            "no inter-factor coupling, decoding, spectral, "
            "robustness, or theorem-level claim"
        ),
    }


def render_text_report(
    report: dict[str, object],
) -> str:
    lines = [
        "===== PETRA VISION GATE 2 — F0 EVIDENCE =====",
        f"Protocol: {report['protocol']['id']}",
        (
            "F0 source SHA256: "
            f"{report['source_provenance']['f0_source_sha256']}"
        ),
        "",
        "===== FROZEN G2-B0 =====",
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
            f"{item['size']}"
        )

    lines.extend([
        (
            "B0 conforme al congelato: "
            f"{b0['matches_frozen_expectation']}"
        ),
        "",
        "===== G2-F0 =====",
    ])

    for name, label in (
        ("phase_1", "Phase 1"),
        ("held_out", "Held-out width 4"),
        ("extended", "Extended"),
    ):
        item = report[name]

        count_only = item["readers"][
            "factor_count_only"
        ]
        static = item["readers"][
            "static_factor_profile_multiset"
        ]
        ordered = item["readers"][
            "ordered_factor_dynamic_control"
        ]
        primary = item["readers"][
            "f0_unordered_factor_dynamic"
        ]

        known = item[
            "known_gate1a_collision"
        ]

        lines.extend([
            f"{label}: {item['size']} forme",
            (
                "  factor-count only: "
                f"{count_only['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  static factor profile: "
                f"{static['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  ordered dynamic CONTROL: "
                f"{ordered['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  F0 unordered dynamic: "
                f"{primary['distinct_signatures']}/"
                f"{item['size']}"
            ),
            (
                "  F0 collision groups: "
                f"{primary['collision_group_count']}; "
                "forme collidenti="
                f"{primary['colliding_shape_count']}; "
                "max group="
                f"{primary['maximum_collision_group_size']}"
            ),
            (
                "  #23/#41 ordered/F0: "
                f"{known['ordered_factor_dynamic_control']['collides']}"
                " / "
                f"{known['f0_unordered_factor_dynamic']['collides']}"
            ),
            (
                "  immediate factor occurrences: "
                f"{item['factorization']['total_immediate_factor_occurrences']}"
            ),
            (
                "  exact recomposition: "
                f"{item['factorization']['recomposition_matches']}/"
                f"{item['factorization']['recomposition_total']}"
            ),
            "",
        ])

    lines.extend([
        "===== AUDIT =====",
        (
            "F0 source boundary: "
            f"{report['source_boundary_audit']['passed']}"
        ),
        (
            "Exact FGS recomposition: "
            f"{report['exact_recomposition']}"
        ),
        (
            "Multiplicity preserved: "
            f"{report['multiplicity_preserved']}"
        ),
        (
            "Known reflected pair preserved: "
            f"{report['known_reflected_pair_preserved']}"
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
            "Run PETRA VISION Gate 2 G2-F0 evidence."
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
        and report["source_boundary_audit"][
            "passed"
        ]
        and report["exact_recomposition"]
        and report["multiplicity_preserved"]
        and report[
            "known_reflected_pair_preserved"
        ]
        and report["deterministic_replay"]
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
