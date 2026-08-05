#!/usr/bin/env python3
"""Experimental width-4 extension of the PETRA VISION Laplacian study.

This research-only tool preserves the dynamic v1 protocol and imports its
geometry-only graph-Laplacian functions.  Its local encoder deliberately does
not call the Phase 1 validator: width four is outside that runtime contract.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import TypeAlias

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
V1_TOOL_PATH = (
    REPOSITORY_ROOT / "tools" / "research"
    / "petra_vision_graph_laplacian.py"
)

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from petra.vision import (  # noqa: E402
    OrderedGroup,
    OrthogonalGeometry,
    Terminal,
    VisionShape,
    geometry_extent,
)


def _load_v1_module():
    """Load the frozen v1 tool without requiring ``tools`` to be a package."""

    module_name = "petra_vision_graph_laplacian_v1"
    module = sys.modules.get(module_name)

    if module is not None:
        return module

    spec = importlib.util.spec_from_file_location(
        module_name,
        V1_TOOL_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load graph-Laplacian v1 tool")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


v1 = _load_v1_module()

PROTOCOL_ID = "petra-vision-graph-laplacian-width4-experimental-v1"
PHASE_1_MAX_WIDTH = 3
EXPERIMENTAL_MAX_WIDTH = 4
MAXIMUM_DEPTH = 3
MAXIMUM_NODES = 7
PHASE_1_CORPUS_SIZE = 110
EXTENDED_CORPUS_SIZE = 137
HELD_OUT_CORPUS_SIZE = 27
GEOMETRY_CELL_BUDGET = 181
GEOMETRY_WIDTH_BUDGET = 25
GEOMETRY_HEIGHT_BUDGET = 13

Signature: TypeAlias = tuple[object, ...]


def _positive_compositions(
    total: int,
    length: int,
) -> tuple[tuple[int, ...], ...]:
    if length == 1:
        return ((total,),) if total >= 1 else ()

    return tuple(
        (first, *tail)
        for first in range(1, total - length + 2)
        for tail in _positive_compositions(total - first, length - 1)
    )


@lru_cache(maxsize=None)
def _shapes_with_exact_nodes(
    node_count: int,
    maximum_width: int,
    maximum_depth: int,
) -> tuple[VisionShape, ...]:
    shapes: set[VisionShape] = set()

    if node_count == 1:
        shapes.add(Terminal())

    if maximum_depth <= 0 or node_count <= 1:
        return tuple(sorted(shapes, key=repr))

    for width in range(1, maximum_width + 1):
        for partition in _positive_compositions(node_count - 1, width):
            child_domains = tuple(
                _shapes_with_exact_nodes(
                    child_nodes,
                    maximum_width,
                    maximum_depth - 1,
                )
                for child_nodes in partition
            )

            if any(not domain for domain in child_domains):
                continue

            shapes.update(
                OrderedGroup(children=children)
                for children in product(*child_domains)
            )

    return tuple(sorted(shapes, key=repr))


@lru_cache(maxsize=None)
def bounded_corpus(
    maximum_width: int,
) -> tuple[VisionShape, ...]:
    """Enumerate this tool's bounded structural domain deterministically."""

    shapes: set[VisionShape] = set()

    for node_count in range(1, MAXIMUM_NODES + 1):
        shapes.update(
            _shapes_with_exact_nodes(
                node_count,
                maximum_width,
                MAXIMUM_DEPTH,
            )
        )

    return tuple(sorted(shapes, key=repr))


@lru_cache(maxsize=1)
def phase_1_corpus() -> tuple[VisionShape, ...]:
    corpus = bounded_corpus(PHASE_1_MAX_WIDTH)

    if len(corpus) != PHASE_1_CORPUS_SIZE:
        raise RuntimeError(
            f"expected {PHASE_1_CORPUS_SIZE} Phase 1 shapes, "
            f"received {len(corpus)}"
        )

    return corpus


@lru_cache(maxsize=1)
def extended_corpus() -> tuple[VisionShape, ...]:
    corpus = bounded_corpus(EXPERIMENTAL_MAX_WIDTH)

    if len(corpus) != EXTENDED_CORPUS_SIZE:
        raise RuntimeError(
            f"expected {EXTENDED_CORPUS_SIZE} extended shapes, "
            f"received {len(corpus)}"
        )

    return corpus


@lru_cache(maxsize=1)
def held_out_corpus() -> tuple[VisionShape, ...]:
    phase_1 = set(phase_1_corpus())
    held_out = tuple(
        shape
        for shape in extended_corpus()
        if shape not in phase_1
    )

    if len(held_out) != HELD_OUT_CORPUS_SIZE:
        raise RuntimeError(
            f"expected {HELD_OUT_CORPUS_SIZE} held-out shapes, "
            f"received {len(held_out)}"
        )

    return held_out


def shape_code(shape: VisionShape) -> str:
    """Return a structural code for corpus and collision reporting only."""

    if isinstance(shape, Terminal):
        return "T"

    return "G(" + ",".join(
        shape_code(child)
        for child in shape.children
    ) + ")"


def encode_experimental_geometry(
    shape: VisionShape,
) -> OrthogonalGeometry:
    """Encode the Phase 1 frame grammar without Phase 1 bound validation.

    This is intentionally isolated from ``encode_geometry``.  Generated corpus
    members use the same Terminal/OrderedGroup grammar and placement recurrence
    as Phase 1, but may contain an ordered group of width four.
    """

    if isinstance(shape, Terminal):
        return OrthogonalGeometry(cells=((0, 0),))

    child_geometries = tuple(
        encode_experimental_geometry(child)
        for child in shape.children
    )
    child_extents = tuple(
        geometry_extent(child)
        for child in child_geometries
    )
    container_height = max(
        height for _width, height in child_extents
    ) + 4
    cells: set[tuple[int, int]] = set()
    left_boundary = 0

    cells.update(
        (left_boundary, y)
        for y in range(container_height)
    )

    for child, (child_width, child_height) in zip(
        child_geometries,
        child_extents,
    ):
        right_boundary = left_boundary + child_width + 3
        cells.update(
            (x, 0)
            for x in range(left_boundary, right_boundary + 1)
        )
        cells.update(
            (x, container_height - 1)
            for x in range(left_boundary, right_boundary + 1)
        )
        cells.update(
            (right_boundary, y)
            for y in range(container_height)
        )
        child_offset_x = left_boundary + 2
        child_offset_y = container_height - child_height - 2
        cells.update(
            (child_offset_x + x, child_offset_y + y)
            for x, y in child.cells
        )
        left_boundary = right_boundary

    return OrthogonalGeometry(cells=tuple(sorted(cells)))


def _summarize_signatures_by_shape_code(
    shape_codes: tuple[str, ...],
    signatures: tuple[Signature, ...],
) -> dict[str, object]:
    if len(shape_codes) != len(signatures):
        raise ValueError("shape codes and signatures must have equal length")

    groups: dict[Signature, list[str]] = defaultdict(list)

    for code, signature in zip(shape_codes, signatures):
        groups[signature].append(code)

    collision_shape_codes = sorted(
        sorted(codes)
        for codes in groups.values()
        if len(codes) > 1
    )
    collision_size_distribution = Counter(
        len(codes) for codes in collision_shape_codes
    )

    return {
        "distinct_signatures": len(groups),
        "collision_group_count": len(collision_shape_codes),
        "colliding_shape_count": sum(
            len(codes) for codes in collision_shape_codes
        ),
        "collision_shape_codes": collision_shape_codes,
        "collision_size_distribution": {
            str(size): count
            for size, count in sorted(
                collision_size_distribution.items()
            )
        },
    }


def _signature_digest(signature: Signature) -> str:
    return hashlib.sha256(json.dumps(
        signature,
        separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def experimental_geometry_dynamic_signatures(
    geometry: OrthogonalGeometry,
) -> dict[str, Signature]:
    """Delegate the frozen v1 dynamic core using occupied geometry only."""

    return v1.geometry_dynamic_signatures(geometry)


def _analyze_corpus(
    corpus: tuple[VisionShape, ...],
) -> dict[str, object]:
    signatures_by_reader: dict[str, list[Signature]] = {
        "null_oriented": [],
        "global_multiset": [],
        "component_multiset": [],
        "oriented": [],
    }
    shape_records = []
    replay_exact = True
    budget_ok = True

    for shape in corpus:
        geometry = encode_experimental_geometry(shape)
        width, height = geometry_extent(geometry)
        within_budget = (
            len(geometry.cells) <= GEOMETRY_CELL_BUDGET
            and width <= GEOMETRY_WIDTH_BUDGET
            and height <= GEOMETRY_HEIGHT_BUDGET
        )
        budget_ok = budget_ok and within_budget
        dynamic = experimental_geometry_dynamic_signatures(geometry)
        replay_exact = (
            replay_exact
            and experimental_geometry_dynamic_signatures(geometry) == dynamic
        )

        digests = {}
        for reader, signature in dynamic.items():
            signatures_by_reader[reader].append(signature)
            digests[reader] = _signature_digest(signature)

        shape_records.append({
            "shape": shape_code(shape),
            "extent": [width, height],
            "occupied_cells": len(geometry.cells),
            "within_geometry_budget": within_budget,
            "signature_sha256": digests,
        })

    codes = tuple(record["shape"] for record in shape_records)
    reader_results = {
        reader: _summarize_signatures_by_shape_code(
            codes,
            tuple(signatures),
        )
        for reader, signatures in signatures_by_reader.items()
    }

    return {
        "size": len(corpus),
        "geometry_budget_satisfied": budget_ok,
        "deterministic_replay": replay_exact,
        "readers": reader_results,
        "shapes": shape_records,
    }


EXPECTED_COLLISION = sorted([
    "G(G(G(T)),G(T,T))",
    "G(G(T,T),G(G(T)))",
])


@lru_cache(maxsize=1)
def analyze_experiment() -> dict[str, object]:
    phase_1 = phase_1_corpus()
    extended = extended_corpus()
    held_out = held_out_corpus()

    phase_1_report = _analyze_corpus(phase_1)
    extended_report = _analyze_corpus(extended)
    held_out_report = _analyze_corpus(held_out)
    extended_collisions = {
        reader: extended_report["readers"][reader][
            "collision_shape_codes"
        ]
        for reader in ("global_multiset", "component_multiset")
    }
    phase_1_collisions = {
        reader: phase_1_report["readers"][reader][
            "collision_shape_codes"
        ]
        for reader in ("global_multiset", "component_multiset")
    }

    if set(phase_1) & set(held_out):
        raise RuntimeError("held-out corpus overlaps the Phase 1 corpus")
    if not all(
        report["geometry_budget_satisfied"]
        for report in (phase_1_report, extended_report, held_out_report)
    ):
        raise RuntimeError("an experimental geometry exceeds the stated budget")

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "status": "experimental research; not a Phase 1 runtime contract",
            "dynamic_protocol_imported_from": v1.PROTOCOL_ID,
            "euler_denominator": v1.EULER_DENOMINATOR,
            "sample_steps": list(v1.SAMPLE_STEPS),
            "probe": (
                "unit impulse at the lexicographically minimum "
                "vertex of every connected component"
            ),
            "identity_channels": "excluded from the dynamic core",
        },
        "corpora": {
            "phase_1": {
                "size": len(phase_1),
                "maximum_width": PHASE_1_MAX_WIDTH,
                "maximum_depth": MAXIMUM_DEPTH,
                "maximum_nodes": MAXIMUM_NODES,
            },
            "extended": {
                "size": len(extended),
                "maximum_width": EXPERIMENTAL_MAX_WIDTH,
                "maximum_depth": MAXIMUM_DEPTH,
                "maximum_nodes": MAXIMUM_NODES,
            },
            "held_out": {
                "size": len(held_out),
                "definition": "extended corpus minus Phase 1 corpus",
                "disjoint_from_phase_1": True,
            },
        },
        "geometry_budget": {
            "maximum_occupied_cells": GEOMETRY_CELL_BUDGET,
            "maximum_width": GEOMETRY_WIDTH_BUDGET,
            "maximum_height": GEOMETRY_HEIGHT_BUDGET,
            "extended_corpus_satisfied": extended_report[
                "geometry_budget_satisfied"
            ],
        },
        "phase_1": phase_1_report,
        "held_out": held_out_report,
        "extended": extended_report,
        "collision_audit": {
            "expected_preexisting_collision_shape_codes": EXPECTED_COLLISION,
            "extended_global_multiset": extended_collisions[
                "global_multiset"
            ],
            "extended_component_multiset": extended_collisions[
                "component_multiset"
            ],
            "no_new_collision_shape_codes": (
                extended_collisions == phase_1_collisions
            ),
        },
        "deterministic_replay": (
            phase_1_report["deterministic_replay"]
            and held_out_report["deterministic_replay"]
            and extended_report["deterministic_replay"]
        ),
    }


def render_text_report(report: dict[str, object]) -> str:
    lines = [
        "===== PETRA VISION GRAPH-LAPLACIAN WIDTH=4 =====",
        "Stato: ricerca sperimentale; non amplia il contratto runtime Phase 1.",
        f"Protocollo dinamico: {report['protocol']['dynamic_protocol_imported_from']}",
        (
            "Denominatore/passaggi: "
            f"{report['protocol']['euler_denominator']} / "
            f"{tuple(report['protocol']['sample_steps'])}"
        ),
        "",
    ]

    for corpus_name, label in (
        ("held_out", "Held-out strutturale"),
        ("extended", "Corpus esteso"),
    ):
        result = report[corpus_name]
        lines.extend([
            f"{label}: {result['size']} forme",
        ])
        for reader in (
            "null_oriented",
            "global_multiset",
            "component_multiset",
            "oriented",
        ):
            summary = result["readers"][reader]
            lines.append(
                f"  {reader}: {summary['distinct_signatures']}/"
                f"{result['size']}; collisioni="
                f"{summary['collision_shape_codes']}"
            )
        lines.append("")

    collision = report["collision_audit"]
    lines.extend([
        "Audit collisioni:",
        f"  preesistente: {collision['expected_preexisting_collision_shape_codes']}",
        f"  nessuna collisione nuova: {collision['no_new_collision_shape_codes']}",
        (
            "Budget geometrico esteso: "
            f"{report['geometry_budget']['extended_corpus_satisfied']} "
            f"(celle<={GEOMETRY_CELL_BUDGET}, "
            f"width<={GEOMETRY_WIDTH_BUDGET}, "
            f"height<={GEOMETRY_HEIGHT_BUDGET})"
        ),
        f"Replay deterministico: {report['deterministic_replay']}",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the experimental PETRA VISION width-4 study."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the deterministic machine-readable report",
    )
    parser.add_argument(
        "--write-json",
        type=Path,
        metavar="PATH",
        help="write the deterministic machine-readable report to PATH",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_experiment()
    payload = json.dumps(report, indent=2, sort_keys=True)

    if args.write_json is not None:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(payload + "\n", encoding="utf-8")

    print(payload if args.json else render_text_report(report))

    held_out_readers = report["held_out"]["readers"]
    extended_readers = report["extended"]["readers"]
    collision_audit = report["collision_audit"]

    expected = (
        report["corpora"]["phase_1"]["size"] == PHASE_1_CORPUS_SIZE
        and report["corpora"]["extended"]["size"] == EXTENDED_CORPUS_SIZE
        and report["corpora"]["held_out"]["size"] == HELD_OUT_CORPUS_SIZE
        and all(
            held_out_readers[reader]["distinct_signatures"]
            == HELD_OUT_CORPUS_SIZE
            and held_out_readers[reader]["collision_shape_codes"] == []
            for reader in (
                "null_oriented",
                "global_multiset",
                "component_multiset",
                "oriented",
            )
        )
        and extended_readers["null_oriented"]["distinct_signatures"]
        == EXTENDED_CORPUS_SIZE
        and extended_readers["oriented"]["distinct_signatures"]
        == EXTENDED_CORPUS_SIZE
        and extended_readers["global_multiset"]["distinct_signatures"]
        == EXTENDED_CORPUS_SIZE - 1
        and extended_readers["component_multiset"]["distinct_signatures"]
        == EXTENDED_CORPUS_SIZE - 1
        and collision_audit[
            "extended_global_multiset"
        ] == [EXPECTED_COLLISION]
        and collision_audit[
            "extended_component_multiset"
        ] == [EXPECTED_COLLISION]
        and collision_audit["no_new_collision_shape_codes"] is True
        and report["geometry_budget"][
            "extended_corpus_satisfied"
        ] is True
        and report["deterministic_replay"] is True
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
