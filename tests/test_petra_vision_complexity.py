"""Contract tests for PETRA VISION Phase 1 complexity evidence."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_JSON = ROOT / "docs/research/petra-vision/PHASE_1_COMPLEXITY_DATA.json"
ARTIFACT_MARKDOWN = ROOT / "docs/research/petra-vision/PHASE_1_COMPLEXITY_RESULTS.md"
SHA256 = re.compile(r"[0-9a-f]{64}")

TOP_LEVEL_KEYS = {
    "schema", "schema_version", "environment", "methodology", "corpus", "summary", "shapes"
}
ENVIRONMENT_KEYS = {"python_implementation", "python_version", "platform", "timer"}
METHODOLOGY_KEYS = {
    "samples", "iterations", "warmup", "timing", "limitations",
    "shape_identifier_derivation", "geometry_digest_derivation",
}
CORPUS_KEYS = {
    "shape_count", "maximum_width", "maximum_depth", "maximum_structural_node_occurrences"
}
SUMMARY_KEYS = {
    "deterministic_maxima", "encoding_nanoseconds_per_operation",
    "decoding_nanoseconds_per_operation",
}
SHAPE_KEYS = {
    "index", "shape_id", "structural_node_count", "structural_depth",
    "maximum_ordered_group_width", "occupied_primitive_count",
    "geometry_bounding_box_width", "geometry_bounding_box_height",
    "geometry_cells_digest", "roundtrip_verified",
    "encoding_median_nanoseconds_per_operation",
    "decoding_median_nanoseconds_per_operation",
}


def _load_tool():
    path = ROOT / "tools/petra_vision_phase_1_complexity.py"
    spec = importlib.util.spec_from_file_location("petra_vision_phase_1_complexity", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# This independent tagged grammar deliberately has no dependency on the tool.
_TERMINAL = ("T",)


def _independent_compositions(total: int, parts: int):
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total):
        for suffix in _independent_compositions(total - first, parts - 1):
            yield (first,) + suffix


@lru_cache(maxsize=None)
def _independent_shapes_within(depth: int, nodes: int):
    shapes = [_TERMINAL] if nodes == 1 else []
    if depth:
        for child_count in range(1, 4):
            for counts in _independent_compositions(nodes - 1, child_count):
                pools = [_independent_shapes_within(depth - 1, count) for count in counts]
                for children in __import__("itertools").product(*pools):
                    shapes.append(("G", children))
    return tuple(shapes)


def _independent_encoding(shape) -> str:
    if shape == _TERMINAL:
        return "T"
    return "G[" + ",".join(_independent_encoding(child) for child in shape[1]) + "]"


def _independent_corpus():
    return tuple(sorted(
        (shape for nodes in range(1, 8) for shape in _independent_shapes_within(3, nodes)),
        key=_independent_encoding,
    ))


def _independent_metrics(shape):
    nodes = depth = width = 0
    pending = [(shape, 0)]
    while pending:
        current, current_depth = pending.pop()
        nodes += 1
        depth = max(depth, current_depth)
        if current != _TERMINAL:
            width = max(width, len(current[1]))
            pending.extend((child, current_depth + 1) for child in current[1])
    return nodes, depth, width


def _project_tool_shape(tool, shape):
    if isinstance(shape, tool.Terminal):
        return _TERMINAL
    assert isinstance(shape, tool.OrderedGroup)
    return ("G", tuple(_project_tool_shape(tool, child) for child in shape.children))


def _cell_digest(cells) -> str:
    compact_json = json.dumps(cells, separators=(",", ":"))
    return hashlib.sha256(compact_json.encode("utf-8")).hexdigest()


def _shape_id(shape) -> str:
    return hashlib.sha256(_independent_encoding(shape).encode("utf-8")).hexdigest()


def _range(values):
    return {"minimum": min(values), "median": int(statistics.median(values)), "maximum": max(values)}


def test_independent_corpus_proves_complete_unique_bounded_grammar_and_order():
    tool = _load_tool()
    independent = _independent_corpus()
    counts = {
        nodes: len(_independent_shapes_within(3, nodes))
        for nodes in range(1, 8)
    }

    assert counts == {1: 1, 2: 1, 3: 2, 4: 5, 5: 12, 6: 28, 7: 61}
    assert len(independent) == 110
    assert len(set(independent)) == 110
    assert tuple(_independent_encoding(shape) for shape in independent) == tuple(sorted(
        _independent_encoding(shape) for shape in independent
    ))

    projected = tuple(_project_tool_shape(tool, shape) for shape in tool.generate_corpus())
    assert set(projected) == set(independent)
    assert len(set(projected)) == 110
    assert projected == independent


def test_identifiers_and_deterministic_records_are_independently_recomputed():
    tool = _load_tool()
    diagnostics = tool.corpus_diagnostics()
    independent = _independent_corpus()
    assert len(diagnostics) == len(independent) == 110

    shape_ids = []
    geometry_digests = []
    geometries = []
    for index, ((shape, record, geometry), abstract) in enumerate(zip(diagnostics, independent)):
        assert record["index"] == index
        assert _project_tool_shape(tool, shape) == abstract
        assert record["shape_id"] == _shape_id(abstract)
        assert record["geometry_cells_digest"] == _cell_digest(geometry.cells)
        assert record["roundtrip_verified"] is True
        assert tool.decode_geometry(geometry) == shape
        assert tuple(record[name] for name in (
            "structural_node_count", "structural_depth", "maximum_ordered_group_width"
        )) == _independent_metrics(abstract)
        assert record["occupied_primitive_count"] == len(geometry.cells)
        assert tuple(record[name] for name in (
            "geometry_bounding_box_width", "geometry_bounding_box_height"
        )) == tool.geometry_extent(geometry)
        shape_ids.append(record["shape_id"])
        geometry_digests.append(record["geometry_cells_digest"])
        geometries.append(geometry.cells)

    assert len(set(shape_ids)) == len(shape_ids)
    assert len(set(geometry_digests)) == len(geometry_digests)
    assert len(set(geometries)) == len(geometries)
    assert len({shape_id[:12] for shape_id in shape_ids}) == len(shape_ids)


def _validate_json_payload(tool, payload):
    assert set(payload) == TOP_LEVEL_KEYS
    assert payload["schema"] == tool.SCHEMA_ID
    assert payload["schema_version"] == tool.SCHEMA_VERSION
    assert set(payload["environment"]) == ENVIRONMENT_KEYS
    assert set(payload["methodology"]) == METHODOLOGY_KEYS
    assert set(payload["corpus"]) == CORPUS_KEYS
    assert set(payload["summary"]) == SUMMARY_KEYS
    assert all(isinstance(payload["environment"][key], str) for key in ENVIRONMENT_KEYS)
    assert isinstance(payload["methodology"]["samples"], int)
    assert isinstance(payload["methodology"]["iterations"], int)
    assert all(isinstance(payload["methodology"][key], str) for key in METHODOLOGY_KEYS - {"samples", "iterations"})
    assert payload["corpus"] == {
        "shape_count": 110, "maximum_width": 3, "maximum_depth": 3,
        "maximum_structural_node_occurrences": 7,
    }
    assert payload["environment"]["python_version"].count(" ") == 0
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    assert all(blocked not in serialized.lower() for blocked in (
        "timestamp", "build date", "repository", "username", "hostname", "git branch", "commit", "network"
    ))

    records = payload["shapes"]
    assert isinstance(records, list) and [record["index"] for record in records] == list(range(110))
    expected_diagnostics = {
        record["shape_id"]: (record, geometry)
        for _, record, geometry in tool.corpus_diagnostics()
    }
    for record in records:
        assert set(record) == SHAPE_KEYS
        assert isinstance(record["roundtrip_verified"], bool)
        assert all(isinstance(record[key], int) for key in SHAPE_KEYS - {
            "shape_id", "geometry_cells_digest", "roundtrip_verified",
        })
        assert SHA256.fullmatch(record["shape_id"])
        assert SHA256.fullmatch(record["geometry_cells_digest"])
        expected, geometry = expected_diagnostics[record["shape_id"]]
        assert record["geometry_cells_digest"] == _cell_digest(geometry.cells)
        assert {
            key: record[key] for key in SHAPE_KEYS - {
                "index", "encoding_median_nanoseconds_per_operation",
                "decoding_median_nanoseconds_per_operation",
            }
        } == {
            key: expected[key] for key in SHAPE_KEYS - {
                "index", "encoding_median_nanoseconds_per_operation",
                "decoding_median_nanoseconds_per_operation",
            }
        }
    assert payload["summary"]["deterministic_maxima"] == {
        metric: max(record[metric] for record in records) for metric in tool.EXPECTED_MAXIMA
    }
    assert payload["summary"]["encoding_nanoseconds_per_operation"] == _range(
        [record["encoding_median_nanoseconds_per_operation"] for record in records]
    )
    assert payload["summary"]["decoding_nanoseconds_per_operation"] == _range(
        [record["decoding_median_nanoseconds_per_operation"] for record in records]
    )


def _validate_markdown(tool, payload, report):
    assert tool.CONFIDENTIALITY_BANNER in report
    assert tool.SCHEMA_ID in report
    assert payload["environment"]["python_version"] in report
    assert "(" not in next(line for line in report.splitlines() if line.startswith("- Python:"))
    assert payload["methodology"]["timing"] in report
    assert payload["methodology"]["limitations"] in report
    assert "## Per-shape metric and timing records" in report
    assert "Complete shape records" not in report
    lowered = report.lower()
    assert all(claim not in lowered for claim in (
        "novel", "robust", "cryptographic-security", "performance-success", "production-ready"
    ))

    maxima = payload["summary"]["deterministic_maxima"]
    assert "| {structural_node_count} | {structural_depth} | {maximum_ordered_group_width} | {occupied_primitive_count} | {geometry_bounding_box_width} | {geometry_bounding_box_height} |".format(**maxima) in report
    for aggregate in ("encoding_nanoseconds_per_operation", "decoding_nanoseconds_per_operation"):
        values = payload["summary"][aggregate]
        assert "| {minimum} | {median} | {maximum} |".format(**values) in report

    rows = [line for line in report.splitlines() if re.match(r"^\| \d+ \| [0-9a-f]{12} \|", line)]
    assert len(rows) == 110
    identifiers = {record["shape_id"] for record in payload["shapes"]}
    for expected, row in zip(payload["shapes"], rows):
        fields = [field.strip() for field in row.strip("|").split("|")]
        assert [int(value) for value in (fields[0], *fields[2:])] == [
            expected["index"], expected["structural_node_count"], expected["structural_depth"],
            expected["maximum_ordered_group_width"], expected["occupied_primitive_count"],
            expected["geometry_bounding_box_width"], expected["geometry_bounding_box_height"],
            expected["encoding_median_nanoseconds_per_operation"],
            expected["decoding_median_nanoseconds_per_operation"],
        ]
        assert sum(identifier.startswith(fields[1]) for identifier in identifiers) == 1
    assert [int(row.split("|")[1]) for row in rows] == list(range(110))


def test_generated_and_repository_artifacts_conform_to_the_full_contract(tmp_path):
    tool = _load_tool()
    result = tool.build_result(samples=1, iterations=1)
    json_output = tmp_path / "missing" / "parent" / "result.json"
    markdown_output = tmp_path / "another" / "missing" / "result.md"
    assert not json_output.parent.exists() and not markdown_output.parent.exists()
    tool.write_json_result(result, json_output)
    tool.write_markdown_result(result, markdown_output)
    assert json_output.parent.exists() and markdown_output.parent.exists()

    for json_path, markdown_path in ((json_output, markdown_output), (ARTIFACT_JSON, ARTIFACT_MARKDOWN)):
        raw = json_path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        assert raw == json.dumps(payload, indent=2, sort_keys=True) + "\n"
        _validate_json_payload(tool, payload)
        _validate_markdown(tool, payload, markdown_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("argument", ["--samples", "--iterations"])
@pytest.mark.parametrize("value", ["0", "-1", "not-an-integer"])
def test_cli_rejects_invalid_timing_parameters(argument, value, tmp_path):
    tool = _load_tool()
    with pytest.raises(SystemExit):
        tool.parse_args([
            argument, value, "--json-output", str(tmp_path / "result.json"),
            "--markdown-output", str(tmp_path / "result.md"),
        ])
