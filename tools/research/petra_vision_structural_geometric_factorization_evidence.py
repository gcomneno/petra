"""Deterministic evidence for PETRA VISION Gate 1B — FGS Phase 1."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Any

from petra.vision import (
    OrderedGroup,
    OrthogonalGeometry,
    Terminal,
    VisionShape,
    decode_geometry,
    encode_geometry,
)

from petra_vision_structural_geometric_factorization import (
    FGSGeometryError,
    native_fgs,
    recompose_fgs,
)


PROTOCOL_ID = "petra-vision-structural-geometric-factorization-v0"
EXPECTED_PHASE_1_SIZE = 110
EXPECTED_RECURSIVE_OCCURRENCES = 574

_THIS_FILE = Path(__file__).resolve()
_NATIVE_MODULE_PATH = (
    _THIS_FILE.parent
    / "petra_vision_structural_geometric_factorization.py"
)


def _positive_compositions(
    total: int,
    length: int,
) -> tuple[tuple[int, ...], ...]:
    if length == 1:
        return ((total,),) if total >= 1 else ()

    compositions: list[tuple[int, ...]] = []

    for first in range(1, total - length + 2):
        for tail in _positive_compositions(
            total - first,
            length - 1,
        ):
            compositions.append((first, *tail))

    return tuple(compositions)


@lru_cache(maxsize=None)
def _shapes_with_exact_nodes(
    node_count: int,
    maximum_depth: int,
) -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()

    if node_count == 1:
        shapes.add(Terminal())

    if maximum_depth <= 0 or node_count <= 1:
        return tuple(sorted(shapes, key=repr))

    child_budget = node_count - 1

    for width in range(1, 4):
        for partition in _positive_compositions(
            child_budget,
            width,
        ):
            child_domains = tuple(
                _shapes_with_exact_nodes(
                    child_nodes,
                    maximum_depth - 1,
                )
                for child_nodes in partition
            )

            if any(not domain for domain in child_domains):
                continue

            for children in product(*child_domains):
                shapes.add(
                    OrderedGroup(children=children)
                )

    return tuple(sorted(shapes, key=repr))


def phase_1_corpus() -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()

    for node_count in range(1, 8):
        shapes.update(
            _shapes_with_exact_nodes(
                node_count,
                maximum_depth=3,
            )
        )

    return tuple(sorted(shapes, key=repr))


def shape_code(shape: VisionShape) -> str:
    if isinstance(shape, Terminal):
        return "T"

    return "G(" + ",".join(
        shape_code(child)
        for child in shape.children
    ) + ")"


def _geometry_digest(
    geometry: OrthogonalGeometry,
) -> str:
    payload = repr(geometry.cells).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()



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
        encode_geometry(child)
        for child in shape.children
    )


def _decoder_factors(
    geometry: OrthogonalGeometry,
) -> tuple[OrthogonalGeometry, ...]:
    decoded = decode_geometry(geometry)

    if isinstance(decoded, Terminal):
        return ()

    return tuple(
        encode_geometry(child)
        for child in decoded.children
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


def _native_tree(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[Any, ...], int]:
    factors = native_fgs(geometry)

    if recompose_fgs(factors) != geometry:
        raise RuntimeError(
            "native recursive replay failed exact recomposition"
        )

    children: list[tuple[Any, ...]] = []
    occurrence_count = 0

    for factor in factors:
        subtree, descendants = _native_tree(factor)
        children.append(subtree)
        occurrence_count += 1 + descendants

    return tuple(children), occurrence_count


def _native_observation(
    geometry: OrthogonalGeometry,
) -> dict[str, Any]:
    factors = native_fgs(geometry)
    tree, occurrences = _native_tree(geometry)

    return {
        "factor_count": len(factors),
        "factor_digests": _factor_digests(factors),
        "exact_recomposition": (
            recompose_fgs(factors) == geometry
        ),
        "recursive_tree": tree,
        "recursive_occurrences": occurrences,
    }


def _geometry_from_cells(
    cells: set[tuple[int, int]],
) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(cells)),
    )


def _malformed_controls() -> dict[str, Any]:
    unary_shape = OrderedGroup(
        children=(Terminal(),)
    )
    unary = set(
        encode_geometry(unary_shape).cells
    )

    incomplete_outer = set(unary)
    incomplete_outer.remove((2, 0))

    empty_bay = set(unary)
    empty_bay.remove((2, 2))

    horizontal_clearance = set(unary)
    horizontal_clearance.remove((2, 2))
    horizontal_clearance.add((1, 2))

    extra_separator = set(unary)
    extra_separator.update(
        (3, y)
        for y in range(1, 4)
    )

    controls: dict[str, bool] = {}

    translated = OrthogonalGeometry(
        cells=((17, -11),)
    )

    try:
        native_fgs(translated)
    except FGSGeometryError:
        controls["noncanonical_translation_rejected"] = True
    else:
        controls["noncanonical_translation_rejected"] = False

    root_cases = {
        "incomplete_outer_frame_rejected": incomplete_outer,
        "empty_bay_rejected": empty_bay,
        "horizontal_clearance_rejected": horizontal_clearance,
        "extra_separator_rejected": extra_separator,
    }

    for name, cells in root_cases.items():
        try:
            native_fgs(
                _geometry_from_cells(cells)
            )
        except FGSGeometryError:
            controls[name] = True
        else:
            controls[name] = False

    nested_source = encode_geometry(
        OrderedGroup(
            children=(
                OrderedGroup(
                    children=(Terminal(),)
                ),
            )
        )
    )
    nested_cells = set(nested_source.cells)
    nested_cells.remove((4, 2))
    malformed_parent = _geometry_from_cells(
        nested_cells
    )

    try:
        immediate = native_fgs(malformed_parent)
        root_accepted = len(immediate) == 1
    except FGSGeometryError:
        root_accepted = False
        immediate = ()

    nested_child_rejected = False

    if root_accepted:
        try:
            native_fgs(immediate[0])
        except FGSGeometryError:
            nested_child_rejected = True

    controls["nested_parent_root_accepted"] = root_accepted
    controls["nested_child_rejected_recursively"] = (
        nested_child_rejected
    )

    return {
        "controls": controls,
        "passed": sum(
            value is True
            for value in controls.values()
        ),
        "total": len(controls),
        "all_passed": all(controls.values()),
    }


def _identity_audit() -> dict[str, Any]:
    source = _NATIVE_MODULE_PATH.read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)

    imported_modules = sorted(
        {
            (
                node.level,
                node.module,
            )
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
        "imported_modules": [
            [level, module]
            for level, module in imported_modules
        ],
        "geometry_imports": geometry_imports,
        "forbidden_name_violations": violations,
        "scope": (
            "AST/source-boundary audit only; "
            "not a formal information-flow proof"
        ),
    }


def build_report() -> dict[str, Any]:
    corpus = phase_1_corpus()

    if len(corpus) != EXPECTED_PHASE_1_SIZE:
        raise RuntimeError(
            "unexpected Phase 1 corpus size"
        )

    rows: list[dict[str, Any]] = []

    immediate_native_matches = 0
    decoder_matches = 0
    recursive_matches = 0
    recomposition_matches = 0
    deterministic_matches = 0
    recursive_occurrences = 0

    for position, shape in enumerate(
        corpus,
        start=1,
    ):
        geometry = encode_geometry(shape)

        expected_factors = _structural_factors(
            shape
        )
        decoder_factors = _decoder_factors(
            geometry
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
        decoder_factor_digests = (
            _factor_digests(decoder_factors)
        )

        native_matches = (
            native["factor_digests"]
            == expected_factor_digests
        )
        decoder_matches_oracle = (
            decoder_factor_digests
            == expected_factor_digests
        )
        recursive_matches_oracle = (
            native["recursive_tree"]
            == _structural_tree(shape)
        )
        deterministic = native == replay

        immediate_native_matches += int(
            native_matches
        )
        decoder_matches += int(
            decoder_matches_oracle
        )
        recursive_matches += int(
            recursive_matches_oracle
        )
        recomposition_matches += int(
            native["exact_recomposition"]
        )
        deterministic_matches += int(
            deterministic
        )
        recursive_occurrences += int(
            native["recursive_occurrences"]
        )

        rows.append(
            {
                "position": position,
                "shape": shape_code(shape),
                "source_digest": (
                    _geometry_digest(geometry)
                ),
                "expected_factor_digests": (
                    expected_factor_digests
                ),
                "decoder_factor_digests": (
                    decoder_factor_digests
                ),
                "native_factor_digests": (
                    native["factor_digests"]
                ),
                "native_matches_oracle": (
                    native_matches
                ),
                "decoder_matches_oracle": (
                    decoder_matches_oracle
                ),
                "recursive_matches_oracle": (
                    recursive_matches_oracle
                ),
                "exact_recomposition": (
                    native["exact_recomposition"]
                ),
                "deterministic_replay": (
                    deterministic
                ),
                "recursive_occurrences": (
                    native[
                        "recursive_occurrences"
                    ]
                ),
            }
        )

    malformed = _malformed_controls()
    identity = _identity_audit()

    report: dict[str, Any] = {
        "protocol": PROTOCOL_ID,
        "claim_scope": (
            "bounded Phase 1 native geometry-only "
            "structural factorization"
        ),
        "native_factorizer": {
            "source_sha256": _native_module_digest(),
            "input_boundary": "OrthogonalGeometry only",
        },
        "corpus": {
            "name": "phase_1",
            "size": len(corpus),
            "maximum_nodes": 7,
            "maximum_depth": 3,
            "maximum_width": 3,
        },
        "summary": {
            "immediate_native_matches": (
                immediate_native_matches
            ),
            "decoder_matches": decoder_matches,
            "recursive_matches": (
                recursive_matches
            ),
            "exact_recomposition_matches": (
                recomposition_matches
            ),
            "deterministic_replay_matches": (
                deterministic_matches
            ),
            "recursive_occurrences": (
                recursive_occurrences
            ),
        },
        "malformed_controls": malformed,
        "identity_audit": identity,
        "rows": rows,
        "limitations": [
            (
                "Phase 1 bounded corpus only; "
                "held-out width 4 is not evaluated here"
            ),
            (
                "The structural oracle and shape codes "
                "exist only in the evidence/reporting layer"
            ),
            (
                "The native implementation boundary is "
                "audited from source/AST, not by formal "
                "transitive information-flow analysis"
            ),
            (
                "A positive result is not a theorem of "
                "general unique factorization"
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

    required_110 = (
        "immediate_native_matches",
        "decoder_matches",
        "recursive_matches",
        "exact_recomposition_matches",
        "deterministic_replay_matches",
    )

    for key in required_110:
        if summary[key] != EXPECTED_PHASE_1_SIZE:
            raise RuntimeError(
                f"{key} is not "
                f"{EXPECTED_PHASE_1_SIZE}/"
                f"{EXPECTED_PHASE_1_SIZE}"
            )

    if (
        summary["recursive_occurrences"]
        != EXPECTED_RECURSIVE_OCCURRENCES
    ):
        raise RuntimeError(
            "unexpected recursive occurrence count"
        )

    if not report[
        "malformed_controls"
    ]["all_passed"]:
        raise RuntimeError(
            "one or more malformed controls failed"
        )

    if not report["identity_audit"]["passed"]:
        raise RuntimeError(
            "native FGS identity audit failed"
        )


def render_text(
    report: dict[str, Any],
) -> str:
    summary = report["summary"]
    malformed = report["malformed_controls"]

    return "\n".join(
        [
            "===== PETRA VISION FGS GATE 1B — PHASE 1 =====",
            f"Protocol: {report['protocol']}",
            (
                "Corpus Phase 1: "
                f"{report['corpus']['size']} forms"
            ),
            "",
            (
                "Immediate native/oracle: "
                f"{summary['immediate_native_matches']}/110"
            ),
            (
                "Decoder baseline/oracle: "
                f"{summary['decoder_matches']}/110"
            ),
            (
                "Recursive native/oracle: "
                f"{summary['recursive_matches']}/110"
            ),
            (
                "Exact recomposition: "
                f"{summary['exact_recomposition_matches']}/110"
            ),
            (
                "Deterministic replay: "
                f"{summary['deterministic_replay_matches']}/110"
            ),
            (
                "Recursive non-root occurrences: "
                f"{summary['recursive_occurrences']}/574"
            ),
            (
                "Malformed controls: "
                f"{malformed['passed']}/"
                f"{malformed['total']}"
            ),
            (
                "Identity audit passed: "
                f"{report['identity_audit']['passed']}"
            ),
            "",
            f"Report digest: {report['report_digest']}",
            "",
            (
                "Claim: bounded Phase 1 FGS feasibility only; "
                "no general factorization theorem."
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
