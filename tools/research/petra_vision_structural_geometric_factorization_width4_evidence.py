"""Held-out width-4 evidence for PETRA VISION Gate 1B — FGS."""

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
)

import petra_vision_graph_laplacian_width4 as width4

from petra_vision_structural_geometric_factorization import (
    native_fgs,
    recompose_fgs,
)


PROTOCOL_ID = (
    "petra-vision-structural-geometric-factorization-width4-v0"
)
EXPECTED_HELD_OUT_SIZE = 27

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
            "native held-out replay failed exact recomposition"
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
    recursive_tree, recursive_occurrences = (
        _native_tree(geometry)
    )

    return {
        "factor_count": len(factors),
        "factor_digests": _factor_digests(factors),
        "exact_recomposition": (
            recompose_fgs(factors) == geometry
        ),
        "recursive_tree": recursive_tree,
        "recursive_occurrences": recursive_occurrences,
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

    if len(phase_1) != 110:
        raise RuntimeError(
            "unexpected Phase 1 corpus size"
        )

    if len(held_out) != EXPECTED_HELD_OUT_SIZE:
        raise RuntimeError(
            "unexpected held-out corpus size"
        )

    if len(extended) != 137:
        raise RuntimeError(
            "unexpected extended corpus size"
        )

    if set(phase_1) & set(held_out):
        raise RuntimeError(
            "held-out corpus is not disjoint from Phase 1"
        )

    if set(phase_1) | set(held_out) != set(extended):
        raise RuntimeError(
            "Phase 1 plus held-out does not equal extended corpus"
        )

    rows: list[dict[str, Any]] = []

    immediate_matches = 0
    recursive_matches = 0
    recomposition_matches = 0
    deterministic_matches = 0
    expected_occurrences_total = 0
    native_occurrences_total = 0

    for position, shape in enumerate(
        held_out,
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

        native_matches = (
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
            native_matches
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
                    native_matches
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

    identity = _identity_audit()

    report: dict[str, Any] = {
        "protocol": PROTOCOL_ID,
        "claim_scope": (
            "held-out width-4 native geometry-only "
            "structural factorization"
        ),
        "native_factorizer": {
            "source_sha256": _native_module_digest(),
            "input_boundary": "OrthogonalGeometry only",
        },
        "corpora": {
            "phase_1_size": len(phase_1),
            "held_out_size": len(held_out),
            "extended_size": len(extended),
            "held_out_definition": (
                "extended width-4 corpus minus Phase 1 corpus"
            ),
            "held_out_disjoint_from_phase_1": True,
        },
        "geometry": {
            "encoder": (
                "isolated experimental width-4 geometry encoder"
            ),
            "production_geometry_contract_modified": False,
        },
        "decoder_control": {
            "evaluated": False,
            "reason": (
                "the frozen production decoder belongs to the "
                "Phase 1 width<=3 contract and is not extended "
                "for this held-out claim"
            ),
        },
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
        "identity_audit": identity,
        "rows": rows,
        "limitations": [
            (
                "Held-out width-4 bounded corpus only."
            ),
            (
                "The width-4 encoder and structural oracle "
                "exist only in the evidence layer."
            ),
            (
                "The production Phase 1 decoder is not "
                "extended or used as a width-4 baseline."
            ),
            (
                "The native factorizer is unchanged from "
                "the Phase 1 experiment."
            ),
            (
                "A positive result is not a theorem of "
                "general unique factorization."
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


def validate_report(
    report: dict[str, Any],
) -> None:
    summary = report["summary"]

    for key in (
        "immediate_native_matches",
        "recursive_native_matches",
        "exact_recomposition_matches",
        "deterministic_replay_matches",
    ):
        if summary[key] != EXPECTED_HELD_OUT_SIZE:
            raise RuntimeError(
                f"{key} is not "
                f"{EXPECTED_HELD_OUT_SIZE}/"
                f"{EXPECTED_HELD_OUT_SIZE}"
            )

    if (
        summary["native_recursive_occurrences"]
        != summary["expected_recursive_occurrences"]
    ):
        raise RuntimeError(
            "native recursive occurrence count "
            "does not match the structural oracle"
        )

    if not report["identity_audit"]["passed"]:
        raise RuntimeError(
            "native FGS identity audit failed"
        )


def render_text(
    report: dict[str, Any],
) -> str:
    summary = report["summary"]
    corpora = report["corpora"]

    return "\n".join(
        [
            (
                "===== PETRA VISION FGS GATE 1B "
                "— HELD-OUT WIDTH 4 ====="
            ),
            f"Protocol: {report['protocol']}",
            (
                "Held-out corpus: "
                f"{corpora['held_out_size']} forms"
            ),
            (
                "Disjoint from Phase 1: "
                f"{corpora['held_out_disjoint_from_phase_1']}"
            ),
            "",
            (
                "Immediate native/oracle: "
                f"{summary['immediate_native_matches']}/27"
            ),
            (
                "Recursive native/oracle: "
                f"{summary['recursive_native_matches']}/27"
            ),
            (
                "Exact recomposition: "
                f"{summary['exact_recomposition_matches']}/27"
            ),
            (
                "Deterministic replay: "
                f"{summary['deterministic_replay_matches']}/27"
            ),
            (
                "Recursive occurrences native/oracle: "
                f"{summary['native_recursive_occurrences']}/"
                f"{summary['expected_recursive_occurrences']}"
            ),
            (
                "Identity audit passed: "
                f"{report['identity_audit']['passed']}"
            ),
            (
                "Production decoder width-4 baseline: "
                "not evaluated by design"
            ),
            "",
            f"Report digest: {report['report_digest']}",
            "",
            (
                "Claim: held-out bounded width-4 FGS "
                "generalization only."
            ),
        ]
    )


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
