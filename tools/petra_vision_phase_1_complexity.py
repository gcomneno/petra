"""Generate PETRA VISION Phase 1 complexity-measurement evidence."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import statistics
import time
from pathlib import Path
from typing import Any, Iterable

from petra.vision import (
    OrderedGroup,
    Terminal,
    VisionShape,
    decode_geometry,
    encode_geometry,
    geometry_extent,
)


CORPUS_MAX_WIDTH = 3
CORPUS_MAX_DEPTH = 3
CORPUS_MAX_NODES = 7
EXPECTED_CORPUS_COUNT = 110
SCHEMA_ID = "petra.vision.phase1.complexity.v1"
SCHEMA_VERSION = 1
EXPECTED_MAXIMA = {
    "structural_node_count": 7,
    "structural_depth": 3,
    "maximum_ordered_group_width": 3,
    "occupied_primitive_count": 181,
    "geometry_bounding_box_width": 25,
    "geometry_bounding_box_height": 13,
}
CONFIDENTIALITY_BANNER = "CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE"


def _compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    """Yield positive, ordered compositions in lexical numeric order."""
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total):
        for remainder in _compositions(total - first, parts - 1):
            yield (first,) + remainder


def _canonical_shape_encoding(shape: VisionShape) -> str:
    """Return the explicit, tagged recursive encoding for a kernel shape."""
    if isinstance(shape, Terminal):
        return "T"
    if isinstance(shape, OrderedGroup):
        return "G[" + ",".join(_canonical_shape_encoding(child) for child in shape.children) + "]"
    raise TypeError("unsupported VISION shape")


def generate_corpus() -> tuple[VisionShape, ...]:
    """Return every bounded Phase 1 tree, in canonical representation order."""
    cache: dict[tuple[int, int], tuple[VisionShape, ...]] = {}

    def shapes_within(depth: int, nodes: int) -> tuple[VisionShape, ...]:
        key = (depth, nodes)
        if key in cache:
            return cache[key]
        shapes: list[VisionShape] = [Terminal()] if nodes == 1 else []
        if depth:
            for child_count in range(1, CORPUS_MAX_WIDTH + 1):
                for counts in _compositions(nodes - 1, child_count):
                    pools = [shapes_within(depth - 1, count) for count in counts]
                    for children in itertools.product(*pools):
                        shapes.append(OrderedGroup(children))
        cache[key] = tuple(shapes)
        return cache[key]

    corpus = tuple(
        sorted(
            (
                shape
                for nodes in range(1, CORPUS_MAX_NODES + 1)
                for shape in shapes_within(CORPUS_MAX_DEPTH, nodes)
            ),
            key=_canonical_shape_encoding,
        )
    )
    if len(corpus) != EXPECTED_CORPUS_COUNT or len(set(corpus)) != len(corpus):
        raise RuntimeError("unexpected Phase 1 corpus")
    return corpus


def structural_metrics(shape: VisionShape) -> tuple[int, int, int]:
    """Return occurrence-counted nodes, maximum depth, and group width."""
    node_count = 0
    maximum_depth = 0
    maximum_width = 0
    pending: list[tuple[VisionShape, int]] = [(shape, 0)]
    while pending:
        current, depth = pending.pop()
        node_count += 1
        maximum_depth = max(maximum_depth, depth)
        if isinstance(current, OrderedGroup):
            maximum_width = max(maximum_width, len(current.children))
            pending.extend((child, depth + 1) for child in current.children)
    return node_count, maximum_depth, maximum_width


def deterministic_record(index: int, shape: VisionShape) -> tuple[dict[str, Any], Any]:
    """Build deterministic diagnostics and canonical geometry for one shape."""
    geometry = encode_geometry(shape)
    if decode_geometry(geometry) != shape:
        raise RuntimeError("VISION geometry roundtrip failed")
    node_count, depth, group_width = structural_metrics(shape)
    geometry_width, geometry_height = geometry_extent(geometry)
    cell_record = json.dumps(geometry.cells, separators=(",", ":"))
    return ({
        "index": index,
        "shape_id": hashlib.sha256(_canonical_shape_encoding(shape).encode("utf-8")).hexdigest(),
        "structural_node_count": node_count,
        "structural_depth": depth,
        "maximum_ordered_group_width": group_width,
        "occupied_primitive_count": len(geometry.cells),
        "geometry_bounding_box_width": geometry_width,
        "geometry_bounding_box_height": geometry_height,
        "geometry_cells_digest": hashlib.sha256(cell_record.encode("utf-8")).hexdigest(),
        "roundtrip_verified": True,
    }, geometry)


def corpus_diagnostics() -> list[tuple[VisionShape, dict[str, Any], Any]]:
    """Return the complete corpus together with its deterministic evidence."""
    return [
        (shape, record, geometry)
        for index, shape in enumerate(generate_corpus())
        for record, geometry in (deterministic_record(index, shape),)
    ]


def _median_batch_nanoseconds(operation: Any, samples: int, iterations: int) -> int:
    batch_values: list[int] = []
    for _ in range(samples):
        started = time.perf_counter_ns()
        for _ in range(iterations):
            operation()
        batch_values.append((time.perf_counter_ns() - started) // iterations)
    return int(statistics.median(batch_values))


def measure_records(samples: int, iterations: int) -> list[dict[str, Any]]:
    """Measure bounded corpus operations without including report serialization."""
    if samples <= 0 or iterations <= 0:
        raise ValueError("samples and iterations must be positive")
    records: list[dict[str, Any]] = []
    for shape, record, geometry in corpus_diagnostics():
        # One independently verified warm-up precedes each operation's batches.
        if decode_geometry(encode_geometry(shape)) != shape:
            raise RuntimeError("VISION geometry roundtrip failed")
        measured = dict(record)
        measured["encoding_median_nanoseconds_per_operation"] = _median_batch_nanoseconds(
            lambda: encode_geometry(shape), samples, iterations
        )
        measured["decoding_median_nanoseconds_per_operation"] = _median_batch_nanoseconds(
            lambda: decode_geometry(geometry), samples, iterations
        )
        records.append(measured)
    return records


def _range_summary(values: list[int]) -> dict[str, int]:
    return {"minimum": min(values), "median": int(statistics.median(values)), "maximum": max(values)}


def build_result(samples: int, iterations: int) -> dict[str, Any]:
    """Build the complete serializable evidence record."""
    shapes = measure_records(samples, iterations)
    maxima = {
        metric: max(shape[metric] for shape in shapes)
        for metric in EXPECTED_MAXIMA
    }
    if maxima != EXPECTED_MAXIMA:
        raise RuntimeError("Phase 1 deterministic envelope mismatch")
    encoding = [shape["encoding_median_nanoseconds_per_operation"] for shape in shapes]
    decoding = [shape["decoding_median_nanoseconds_per_operation"] for shape in shapes]
    return {
        "schema": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "timer": "time.perf_counter_ns",
        },
        "methodology": {
            "samples": samples,
            "iterations": iterations,
            "warmup": "one encode/decode roundtrip per shape before measurement",
            "timing": "median of the per-batch integer nanoseconds per operation; each raw batch duration is floor-divided by iterations, and loop overhead is not subtracted",
            "limitations": "Diagnostic timing only; it establishes no performance threshold, optimality, production-readiness, or cross-machine comparison.",
            "shape_identifier_derivation": "SHA-256 of the UTF-8 canonical tagged recursive shape encoding: Terminal is T and OrderedGroup children are G[child0,...,childn].",
            "geometry_digest_derivation": "SHA-256 of the UTF-8 canonical compact JSON record of geometry cells, serialized with separators ',' and ':'.",
        },
        "corpus": {
            "shape_count": len(shapes),
            "maximum_width": CORPUS_MAX_WIDTH,
            "maximum_depth": CORPUS_MAX_DEPTH,
            "maximum_structural_node_occurrences": CORPUS_MAX_NODES,
        },
        "summary": {
            "deterministic_maxima": maxima,
            "encoding_nanoseconds_per_operation": _range_summary(encoding),
            "decoding_nanoseconds_per_operation": _range_summary(decoding),
        },
        "shapes": shapes,
    }


def write_json_result(result: dict[str, Any], output: Path) -> None:
    """Write stable UTF-8 JSON, creating the requested parent directory."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_result(result: dict[str, Any]) -> str:
    """Render the confidential complete-record Markdown report."""
    summary = result["summary"]
    environment = result["environment"]
    methodology = result["methodology"]
    lines = [
        f"> **{CONFIDENTIALITY_BANNER}**",
        "",
        "# PETRA VISION Phase 1 complexity measurement evidence",
        "",
        f"Schema: `{result['schema']}` (version {result['schema_version']}).",
        "",
        "## Purpose and timing limitations",
        "",
        "This diagnostic records structural and geometry complexity for every bounded Phase 1 shape.",
        "",
        methodology["limitations"],
        "",
        "## Environment and methodology",
        "",
        f"- Python: {environment['python_implementation']} {environment['python_version']}",
        f"- Platform: {environment['platform']}",
        f"- Timer: {environment['timer']}",
        f"- Samples: {methodology['samples']}; iterations per batch: {methodology['iterations']}",
        f"- Method: {methodology['warmup']}; {methodology['timing']}",
        "",
        "## Corpus-wide deterministic maxima",
        "",
        "| Nodes | Depth | Group width | Occupied cells | Geometry width | Geometry height |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        "| {structural_node_count} | {structural_depth} | {maximum_ordered_group_width} | {occupied_primitive_count} | {geometry_bounding_box_width} | {geometry_bounding_box_height} |".format(**summary["deterministic_maxima"]),
        "",
        "## Timing aggregates (ns/op)",
        "",
        "| Operation | Minimum | Median | Maximum |",
        "| --- | ---: | ---: | ---: |",
        "| Encoding | {minimum} | {median} | {maximum} |".format(**summary["encoding_nanoseconds_per_operation"]),
        "| Decoding | {minimum} | {median} | {maximum} |".format(**summary["decoding_nanoseconds_per_operation"]),
        "",
        "## Per-shape metric and timing records",
        "",
        "| Index | Shape ID | Nodes | Depth | Group width | Occupied cells | Geometry width | Geometry height | Encode median ns/op | Decode median ns/op |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for shape in result["shapes"]:
        markdown_record = dict(shape)
        markdown_record["shape_id"] = shape["shape_id"][:12]
        lines.append(
            "| {index} | {shape_id} | {structural_node_count} | {structural_depth} | "
            "{maximum_ordered_group_width} | {occupied_primitive_count} | "
            "{geometry_bounding_box_width} | {geometry_bounding_box_height} | "
            "{encoding_median_nanoseconds_per_operation} | "
            "{decoding_median_nanoseconds_per_operation} |".format(
                **markdown_record
            )
        )
    return "\n".join(lines) + "\n"


def write_markdown_result(result: dict[str, Any], output: Path) -> None:
    """Write the confidential Markdown report."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown_result(result), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    positive_integer = lambda value: _positive_integer(parser, value)
    parser.add_argument("--samples", type=positive_integer, default=7)
    parser.add_argument("--iterations", type=positive_integer, default=100)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    return parser.parse_args(argv)


def _positive_integer(parser: argparse.ArgumentParser, value: str) -> int:
    try:
        integer = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if integer <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return integer


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = build_result(args.samples, args.iterations)
    write_json_result(result, args.json_output)
    write_markdown_result(result, args.markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
