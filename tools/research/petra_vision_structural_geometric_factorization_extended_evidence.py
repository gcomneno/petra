"""Extended 137-form evidence for PETRA VISION Gate 1B — FGS."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

from petra.vision import (
    OrthogonalGeometry,
    Terminal,
    VisionShape,
    encode_geometry,
)

import petra_vision_graph_laplacian_width4 as width4

from petra_vision_structural_geometric_factorization import (
    native_fgs,
    recompose_fgs,
)


PROTOCOL_ID = (
    "petra-vision-structural-geometric-factorization-extended-v0"
)

EXPECTED_PHASE_1_SIZE = 110
EXPECTED_HELD_OUT_SIZE = 27
EXPECTED_EXTENDED_SIZE = 137

EXPECTED_PHASE_1_OCCURRENCES = 574
EXPECTED_HELD_OUT_OCCURRENCES = 155
EXPECTED_EXTENDED_OCCURRENCES = 729

_THIS_FILE = Path(__file__).resolve()
_NATIVE_MODULE_PATH = (
    _THIS_FILE.parent
    / "petra_vision_structural_geometric_factorization.py"
)


def _geometry_digest(
    geometry: OrthogonalGeometry,
) -> str:
    return hashlib.sha256(
        repr(geometry.cells).encode("utf-8")
    ).hexdigest()



def _native_module_digest() -> str:
    return hashlib.sha256(
        _NATIVE_MODULE_PATH.read_bytes()
    ).hexdigest()


def _factor_digests(
    factors: tuple[OrthogonalGeometry, ...],
) -> list[str]:
    return [
        _geometry_digest(factor)
        for factor in factors
    ]


def _structural_factors(
    shape: VisionShape,
) -> tuple[OrthogonalGeometry, ...]:
    if isinstance(shape, Terminal):
        return ()

    return tuple(
        width4.encode_experimental_geometry(child)
        for child in shape.children
    )


def _structural_tree(
    shape: VisionShape,
) -> tuple[Any, ...]:
    if isinstance(shape, Terminal):
        return ()

    return tuple(
        _structural_tree(child)
        for child in shape.children
    )


def _structural_occurrences(
    shape: VisionShape,
) -> int:
    if isinstance(shape, Terminal):
        return 0

    return sum(
        1 + _structural_occurrences(child)
        for child in shape.children
    )


def _native_tree(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[Any, ...], int]:
    factors = native_fgs(geometry)

    if recompose_fgs(factors) != geometry:
        raise RuntimeError(
            "native recursive replay failed exact recomposition"
        )

    children: list[tuple[Any, ...]] = []
    occurrences = 0

    for factor in factors:
        subtree, descendants = _native_tree(factor)
        children.append(subtree)
        occurrences += 1 + descendants

    return tuple(children), occurrences


def _native_observation(
    geometry: OrthogonalGeometry,
) -> dict[str, Any]:
    factors = native_fgs(geometry)
    tree, occurrences = _native_tree(geometry)

    return {
        "factor_digests": _factor_digests(factors),
        "recursive_tree": tree,
        "recursive_occurrences": occurrences,
        "exact_recomposition": (
            recompose_fgs(factors) == geometry
        ),
    }


def _analyze_corpus(
    name: str,
    corpus: tuple[VisionShape, ...],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    immediate_matches = 0
    recursive_matches = 0
    recomposition_matches = 0
    deterministic_matches = 0
    expected_occurrences_total = 0
    native_occurrences_total = 0

    for position, shape in enumerate(
        corpus,
        start=1,
    ):
        geometry = width4.encode_experimental_geometry(
            shape
        )

        expected_factors = _structural_factors(
            shape
        )
        expected_tree = _structural_tree(
            shape
        )
        expected_occurrences = (
            _structural_occurrences(shape)
        )

        native = _native_observation(
            geometry
        )
        replay = _native_observation(
            geometry
        )

        expected_factor_digests = (
            _factor_digests(expected_factors)
        )

        immediate_match = (
            native["factor_digests"]
            == expected_factor_digests
        )

        recursive_match = (
            native["recursive_tree"]
            == expected_tree
            and native["recursive_occurrences"]
            == expected_occurrences
        )

        deterministic = native == replay

        immediate_matches += int(
            immediate_match
        )
        recursive_matches += int(
            recursive_match
        )
        recomposition_matches += int(
            native["exact_recomposition"]
        )
        deterministic_matches += int(
            deterministic
        )
        expected_occurrences_total += (
            expected_occurrences
        )
        native_occurrences_total += int(
            native["recursive_occurrences"]
        )

        rows.append(
            {
                "position": position,
                "shape": width4.shape_code(shape),
                "source_digest": (
                    _geometry_digest(geometry)
                ),
                "expected_factor_digests": (
                    expected_factor_digests
                ),
                "native_factor_digests": (
                    native["factor_digests"]
                ),
                "native_matches_oracle": (
                    immediate_match
                ),
                "recursive_matches_oracle": (
                    recursive_match
                ),
                "exact_recomposition": (
                    native["exact_recomposition"]
                ),
                "deterministic_replay": (
                    deterministic
                ),
                "expected_recursive_occurrences": (
                    expected_occurrences
                ),
                "native_recursive_occurrences": (
                    native["recursive_occurrences"]
                ),
            }
        )

    return {
        "name": name,
        "size": len(corpus),
        "summary": {
            "immediate_native_matches": (
                immediate_matches
            ),
            "recursive_native_matches": (
                recursive_matches
            ),
            "exact_recomposition_matches": (
                recomposition_matches
            ),
            "deterministic_replay_matches": (
                deterministic_matches
            ),
            "expected_recursive_occurrences": (
                expected_occurrences_total
            ),
            "native_recursive_occurrences": (
                native_occurrences_total
            ),
        },
        "rows": rows,
    }


def _identity_audit() -> dict[str, Any]:
    source = _NATIVE_MODULE_PATH.read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)

    imported_modules = sorted(
        {
            (node.level, node.module)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        },
        key=repr,
    )

    geometry_imports = sorted(
        {
            alias.asname or alias.name
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module == "petra.vision.geometry"
            )
            for alias in node.names
        }
    )

    forbidden = {
        "VisionShape",
        "Terminal",
        "OrderedGroup",
        "decode_geometry",
        "encode_geometry",
        "adapt_petra_shape",
        "restore_petra_shape",
        "shape_code",
        "resolve_address",
        "serialize_shape",
    }

    referenced = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    violations = sorted(
        forbidden & referenced
    )

    expected_imports = sorted(
        {
            (0, "__future__"),
            (0, "collections.abc"),
            (0, "petra.vision.geometry"),
        },
        key=repr,
    )

    passed = (
        imported_modules == expected_imports
        and geometry_imports
        == [
            "OrthogonalGeometry",
            "geometry_extent",
        ]
        and not any(
            isinstance(node, ast.Import)
            for node in ast.walk(tree)
        )
        and not violations
    )

    return {
        "passed": passed,
        "forbidden_name_violations": violations,
        "scope": (
            "AST/source-boundary audit only; "
            "not a formal transitive information-flow proof"
        ),
    }


def build_report() -> dict[str, Any]:
    phase_1 = width4.phase_1_corpus()
    held_out = width4.held_out_corpus()
    extended = width4.extended_corpus()

    if len(phase_1) != EXPECTED_PHASE_1_SIZE:
        raise RuntimeError(
            "unexpected Phase 1 corpus size"
        )

    if len(held_out) != EXPECTED_HELD_OUT_SIZE:
        raise RuntimeError(
            "unexpected held-out corpus size"
        )

    if len(extended) != EXPECTED_EXTENDED_SIZE:
        raise RuntimeError(
            "unexpected extended corpus size"
        )

    phase_1_set = set(phase_1)
    held_out_set = set(held_out)
    extended_set = set(extended)

    if phase_1_set & held_out_set:
        raise RuntimeError(
            "held-out corpus overlaps Phase 1"
        )

    if phase_1_set | held_out_set != extended_set:
        raise RuntimeError(
            "Phase 1 and held-out do not partition extended"
        )

    encoder_continuity_matches = sum(
        width4.encode_experimental_geometry(shape)
        == encode_geometry(shape)
        for shape in phase_1
    )

    phase_1_report = _analyze_corpus(
        "phase_1",
        phase_1,
    )
    held_out_report = _analyze_corpus(
        "held_out_width_4",
        held_out,
    )
    extended_report = _analyze_corpus(
        "extended",
        extended,
    )

    report: dict[str, Any] = {
        "protocol": PROTOCOL_ID,
        "claim_scope": (
            "bounded 137-form native geometry-only "
            "structural factorization"
        ),
        "corpora": {
            "phase_1_size": len(phase_1),
            "held_out_size": len(held_out),
            "extended_size": len(extended),
            "held_out_disjoint_from_phase_1": True,
            "partition_exact": True,
        },
        "geometry": {
            "extended_encoder": (
                "isolated experimental width-4 geometry encoder"
            ),
            "phase_1_encoder_continuity_matches": (
                encoder_continuity_matches
            ),
            "production_geometry_contract_modified": False,
        },
        "native_factorizer": {
            "source_sha256": _native_module_digest(),
            "input_boundary": "OrthogonalGeometry only",
        },
        "phase_1": phase_1_report,
        "held_out": held_out_report,
        "extended": extended_report,
        "identity_audit": _identity_audit(),
        "limitations": [
            (
                "The result covers the declared bounded "
                "137-form domain only."
            ),
            (
                "The width-4 encoder and structural oracle "
                "exist only in the evidence layer."
            ),
            (
                "The native factorizer is unchanged from "
                "the Phase 1 experiment."
            ),
            (
                "The source-boundary audit is not a formal "
                "transitive information-flow proof."
            ),
            (
                "No general or arithmetic unique "
                "factorization theorem is claimed."
            ),
        ],
    }

    canonical = json.dumps(
        report,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    report["report_digest"] = (
        hashlib.sha256(canonical).hexdigest()
    )

    return report


def _validate_corpus(
    report: dict[str, Any],
    *,
    expected_size: int,
    expected_occurrences: int,
) -> None:
    if report["size"] != expected_size:
        raise RuntimeError(
            f"{report['name']} has unexpected size"
        )

    summary = report["summary"]

    for key in (
        "immediate_native_matches",
        "recursive_native_matches",
        "exact_recomposition_matches",
        "deterministic_replay_matches",
    ):
        if summary[key] != expected_size:
            raise RuntimeError(
                f"{report['name']} {key} is not "
                f"{expected_size}/{expected_size}"
            )

    if (
        summary["expected_recursive_occurrences"]
        != expected_occurrences
    ):
        raise RuntimeError(
            f"{report['name']} oracle occurrence count changed"
        )

    if (
        summary["native_recursive_occurrences"]
        != expected_occurrences
    ):
        raise RuntimeError(
            f"{report['name']} native occurrence count mismatch"
        )


def validate_report(
    report: dict[str, Any],
) -> None:
    if (
        report["geometry"][
            "phase_1_encoder_continuity_matches"
        ]
        != EXPECTED_PHASE_1_SIZE
    ):
        raise RuntimeError(
            "experimental encoder does not reproduce "
            "all Phase 1 geometries"
        )

    _validate_corpus(
        report["phase_1"],
        expected_size=EXPECTED_PHASE_1_SIZE,
        expected_occurrences=EXPECTED_PHASE_1_OCCURRENCES,
    )

    _validate_corpus(
        report["held_out"],
        expected_size=EXPECTED_HELD_OUT_SIZE,
        expected_occurrences=EXPECTED_HELD_OUT_OCCURRENCES,
    )

    _validate_corpus(
        report["extended"],
        expected_size=EXPECTED_EXTENDED_SIZE,
        expected_occurrences=EXPECTED_EXTENDED_OCCURRENCES,
    )

    if not report["identity_audit"]["passed"]:
        raise RuntimeError(
            "native FGS identity audit failed"
        )


def _summary_line(
    label: str,
    corpus: dict[str, Any],
) -> list[str]:
    summary = corpus["summary"]
    size = corpus["size"]

    return [
        (
            f"{label} immediate native/oracle: "
            f"{summary['immediate_native_matches']}/{size}"
        ),
        (
            f"{label} recursive native/oracle: "
            f"{summary['recursive_native_matches']}/{size}"
        ),
        (
            f"{label} exact recomposition: "
            f"{summary['exact_recomposition_matches']}/{size}"
        ),
        (
            f"{label} deterministic replay: "
            f"{summary['deterministic_replay_matches']}/{size}"
        ),
        (
            f"{label} recursive occurrences: "
            f"{summary['native_recursive_occurrences']}/"
            f"{summary['expected_recursive_occurrences']}"
        ),
    ]


def render_text(
    report: dict[str, Any],
) -> str:
    lines = [
        (
            "===== PETRA VISION FGS GATE 1B "
            "— EXTENDED 137 ====="
        ),
        f"Protocol: {report['protocol']}",
        "",
        (
            "Corpus partition: "
            "110 Phase 1 + 27 held-out = 137 extended"
        ),
        (
            "Held-out disjoint from Phase 1: "
            f"{report['corpora']['held_out_disjoint_from_phase_1']}"
        ),
        (
            "Phase 1 encoder continuity: "
            f"{report['geometry']['phase_1_encoder_continuity_matches']}/110"
        ),
        (
            "Native factorizer SHA256: "
            f"{report['native_factorizer']['source_sha256']}"
        ),
        "",
    ]

    lines.extend(
        _summary_line(
            "Phase 1",
            report["phase_1"],
        )
    )
    lines.append("")

    lines.extend(
        _summary_line(
            "Held-out",
            report["held_out"],
        )
    )
    lines.append("")

    lines.extend(
        _summary_line(
            "Extended",
            report["extended"],
        )
    )
    lines.extend(
        [
            "",
            (
                "Identity audit passed: "
                f"{report['identity_audit']['passed']}"
            ),
            "",
            (
                "Report digest: "
                f"{report['report_digest']}"
            ),
            "",
            (
                "Claim: bounded 137-form FGS feasibility "
                "under the declared geometric grammar only."
            ),
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
    )
    args = parser.parse_args()

    report = build_report()
    validate_report(report)

    if args.json is not None:
        args.json.write_text(
            json.dumps(
                report,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
