#!/usr/bin/env python3
"""Bounded collision semantics for the frozen PETRA VISION readers.

This is a research reporting layer.  It imports the frozen graph construction
and propagation code rather than copying or changing it.  In particular, the
only input to ``coordinate_free_signatures`` is an OrthogonalGeometry.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import sys
import textwrap
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from math import factorial
from itertools import permutations
from pathlib import Path
from typing import TypeAlias

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
V1_TOOL_PATH = REPOSITORY_ROOT / "tools" / "research" / "petra_vision_graph_laplacian.py"
WIDTH4_TOOL_PATH = REPOSITORY_ROOT / "tools" / "research" / "petra_vision_graph_laplacian_width4.py"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from petra.vision import OrthogonalGeometry, encode_geometry  # noqa: E402

PROTOCOL_ID = "petra-vision-coordinate-free-collision-semantics-v1"
FIXED_TRANSLATIONS = ((17, 23), (-11, 7))
COMPONENT_GAP = 2
READERS = ("global_multiset", "component_multiset")
CONTROLS = ("oriented", "null_oriented")
Signature: TypeAlias = tuple[object, ...]
ComponentShape: TypeAlias = tuple[tuple[int, int], ...]


def _load_module(name: str, path: Path):
    module = sys.modules.get(name)
    if module is not None:
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load research tool: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v1 = _load_module("petra_vision_graph_laplacian_v1", V1_TOOL_PATH)
width4 = _load_module("petra_vision_graph_laplacian_width4", WIDTH4_TOOL_PATH)


@dataclass(frozen=True)
class ReportingAnnotation:
    """Corpus-only metadata deliberately excluded from dynamic computation."""

    corpus_index: int
    shape_code: str
    phase_1_index: int | None = None


def _require_geometry(geometry: OrthogonalGeometry) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError("geometry must be an OrthogonalGeometry")
    return geometry


def _require_displacement(value: object) -> tuple[int, int]:
    if type(value) is not tuple or len(value) != 2:
        raise TypeError("displacement must be an exact (x, y) tuple")
    x, y = value
    if type(x) is not int or type(y) is not int:
        raise TypeError("displacement coordinates must be exact integers")
    return x, y


def translate_geometry(
    geometry: OrthogonalGeometry,
    displacement: tuple[int, int],
) -> OrthogonalGeometry:
    """Return a checked fixed translation without normalizing it away."""

    current = _require_geometry(geometry)
    dx, dy = _require_displacement(displacement)
    return OrthogonalGeometry(cells=tuple(sorted(
        (x + dx, y + dy)
        for x, y in current.cells
    )))


def horizontal_reflection(geometry: OrthogonalGeometry) -> OrthogonalGeometry:
    """Reflect in the geometry bounding box, retaining a deterministic order."""

    current = _require_geometry(geometry)
    minimum_x = min(x for x, _y in current.cells)
    maximum_x = max(x for x, _y in current.cells)
    return OrthogonalGeometry(cells=tuple(sorted(
        (minimum_x + maximum_x - x, y)
        for x, y in current.cells
    )))


def normalized_component_shapes(
    geometry: OrthogonalGeometry,
) -> tuple[ComponentShape, ...]:
    """Extract sorted, translation-normalized disconnected component shapes."""

    graph = v1.build_geometry_graph(_require_geometry(geometry))
    shapes: list[ComponentShape] = []
    for component in graph.components:
        cells = tuple(graph.cells[index] for index in component)
        min_x = min(x for x, _y in cells)
        min_y = min(y for _x, y in cells)
        shapes.append(tuple(sorted((x - min_x, y - min_y) for x, y in cells)))
    return tuple(shapes)


def _validate_component_shape(shape: ComponentShape) -> ComponentShape:
    if type(shape) is not tuple or not shape:
        raise ValueError("component shapes must be non-empty exact tuples")
    component = OrthogonalGeometry(cells=shape)
    if min(x for x, _y in component.cells) != 0 or min(
        y for _x, y in component.cells
    ) != 0:
        raise ValueError("component shapes must be normalized")
    if len(v1.build_geometry_graph(component).components) != 1:
        raise ValueError("each reconstructed component shape must be connected")
    return component.cells


def _validate_permutation(permutation: tuple[int, ...], size: int) -> tuple[int, ...]:
    if type(permutation) is not tuple:
        raise TypeError("permutation must be an exact tuple")
    if any(type(index) is not int for index in permutation):
        raise TypeError("permutation indices must be exact integers")
    if tuple(sorted(permutation)) != tuple(range(size)):
        raise ValueError("permutation must contain each component index exactly once")
    return permutation


def packed_displacements(
    ordered_shapes: tuple[ComponentShape, ...],
) -> tuple[tuple[int, int], ...]:
    """Choose the declared bounded, non-adjacent left-to-right placement."""

    cursor = 0
    displacements: list[tuple[int, int]] = []
    for shape in ordered_shapes:
        normalized = _validate_component_shape(shape)
        width = max(x for x, _y in normalized) + 1
        displacements.append((cursor, 0))
        cursor += width + COMPONENT_GAP
    return tuple(displacements)


def reconstruct_component_geometry(
    components: tuple[ComponentShape, ...],
    permutation: tuple[int, ...],
    displacements: tuple[tuple[int, int], ...] | None = None,
) -> OrthogonalGeometry:
    """Rebuild components, rejecting overlap, touching, and malformed inputs."""

    if type(components) is not tuple or not components:
        raise ValueError("components must be a non-empty exact tuple")
    normalized = tuple(_validate_component_shape(shape) for shape in components)
    order = _validate_permutation(permutation, len(normalized))
    ordered = tuple(normalized[index] for index in order)
    placements = (
        packed_displacements(ordered)
        if displacements is None
        else displacements
    )
    if type(placements) is not tuple or len(placements) != len(ordered):
        raise ValueError("one displacement is required for every output component")
    checked_placements = tuple(_require_displacement(item) for item in placements)
    cells = tuple(sorted(
        (x + dx, y + dy)
        for shape, (dx, dy) in zip(ordered, checked_placements)
        for x, y in shape
    ))
    if len(set(cells)) != len(cells):
        raise ValueError("reconstructed components overlap")
    reconstructed = OrthogonalGeometry(cells=cells)
    reconstructed_shapes = normalized_component_shapes(reconstructed)
    if len(reconstructed_shapes) != len(components):
        raise ValueError("reconstructed components overlap or touch")
    if tuple(sorted(reconstructed_shapes)) != tuple(sorted(normalized)):
        raise ValueError("reconstructed geometry does not preserve component shapes")
    return reconstructed


def _component_permutation_cases(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[OrthogonalGeometry, ...], dict[str, object]]:
    """Generate and validate every distinct packed component ordering.

    A labelled permutation of equal normalized component shapes does not
    describe a distinct generated geometry.  Those redundant specifications
    are counted separately before the distinct bounded family is replayed.
    """

    components = normalized_component_shapes(_require_geometry(geometry))
    seen_orders: set[tuple[ComponentShape, ...]] = set()
    seen_geometries: set[OrthogonalGeometry] = set()
    variants: list[OrthogonalGeometry] = []
    rejected = Counter()
    raw_specifications = 0
    duplicate_specifications = 0
    duplicate_geometries = 0

    for order in permutations(range(len(components))):
        raw_specifications += 1
        fingerprint = tuple(components[index] for index in order)
        if fingerprint in seen_orders:
            duplicate_specifications += 1
            continue
        seen_orders.add(fingerprint)
        try:
            candidate = reconstruct_component_geometry(components, order)
        except (TypeError, ValueError) as error:
            rejected[type(error).__name__ + ": " + str(error)] += 1
            continue
        if candidate in seen_geometries:
            duplicate_geometries += 1
            continue
        seen_geometries.add(candidate)
        variants.append(candidate)

    return tuple(variants), {
        "raw_labelled_permutation_specifications": raw_specifications,
        "duplicate_labelled_permutation_specifications": duplicate_specifications,
        "candidate_cases": len(seen_orders),
        "valid_reconstructed_geometries": len(variants),
        "invalid_or_rejected_cases": sum(rejected.values()),
        "rejection_reasons": dict(sorted(rejected.items())),
        "duplicate_generated_geometries": duplicate_geometries,
        "unique_valid_generated_geometries": len(variants),
    }


def component_permutation_geometries(
    geometry: OrthogonalGeometry,
) -> tuple[OrthogonalGeometry, ...]:
    """Return every distinct, validated packed component ordering."""

    variants, _manifest = _component_permutation_cases(geometry)
    return variants


def component_permutation_count(geometry: OrthogonalGeometry) -> int:
    """Return the exact number of distinct valid packed component orderings."""

    components = normalized_component_shapes(_require_geometry(geometry))
    count = factorial(len(components))
    for multiplicity in Counter(components).values():
        count //= factorial(multiplicity)
    return count


def coordinate_free_signatures(
    geometry: OrthogonalGeometry,
) -> dict[str, Signature]:
    """Frozen signatures; this dynamic boundary accepts geometry only."""

    return v1.geometry_dynamic_signatures(_require_geometry(geometry))


def _derived_case_signatures(
    geometry: OrthogonalGeometry,
) -> dict[str, Signature]:
    """Evaluate one generated geometry through the same geometry-only core."""

    return coordinate_free_signatures(geometry)


def _signature_digest(signature: Signature) -> str:
    return hashlib.sha256(json.dumps(
        signature,
        separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def _dynamic_records(
    geometries: tuple[OrthogonalGeometry, ...],
) -> tuple[dict[str, Signature], ...]:
    """Compute dynamics before any corpus annotation is joined."""

    return tuple(coordinate_free_signatures(geometry) for geometry in geometries)


def _equivalence_groups(
    records: tuple[dict[str, Signature], ...],
    reader: str,
) -> tuple[tuple[int, ...], ...]:
    groups: dict[Signature, list[int]] = defaultdict(list)
    for position, record in enumerate(records):
        groups[record[reader]].append(position)
    return tuple(sorted(
        (tuple(group) for group in groups.values()),
        key=lambda group: group,
    ))


DYNAMIC_AUDIT_FUNCTIONS = (
    coordinate_free_signatures, _derived_case_signatures,
    v1.build_geometry_graph, v1.canonical_component_probe, v1.probe_state,
    v1.evolve_euler_numerator, v1.dynamic_signatures_from_probe,
    v1.geometry_dynamic_signatures, _dynamic_records, _equivalence_groups,
)


def _reader_report(
    records: tuple[dict[str, Signature], ...],
    annotations: tuple[ReportingAnnotation, ...],
    reader: str,
) -> dict[str, object]:
    groups = _equivalence_groups(records, reader)
    collisions = tuple(group for group in groups if len(group) > 1)
    return {
        "equivalence_definition": (
            "C ~ D exactly when the frozen " + reader +
            " signatures are equal under the declared protocol"
        ),
        "distinct_signatures": len(groups),
        "equivalence_memberships": [list(group) for group in groups],
        "equivalence_classes": [
            [annotations[position].shape_code for position in group]
            for group in groups
        ],
        "collisions": [
            {
                "positions": list(group),
                "corpus_indices": [
                    annotations[position].corpus_index
                    for position in group
                ],
                "phase_1_indices": [
                    annotations[position].phase_1_index
                    for position in group
                ],
                "shape_codes": [annotations[position].shape_code for position in group],
                "signature_sha256": _signature_digest(records[group[0]][reader]),
            }
            for group in collisions
        ],
    }


def _corpus_entries(name: str) -> tuple[tuple[OrthogonalGeometry, ...], tuple[ReportingAnnotation, ...]]:
    if name == "phase_1":
        shapes = v1.bounded_phase_1_corpus()
        return (
            tuple(encode_geometry(shape) for shape in shapes),
            tuple(ReportingAnnotation(index, v1.shape_code(shape), index) for index, shape in enumerate(shapes)),
        )
    if name == "held_out":
        shapes = width4.held_out_corpus()
        return (
            tuple(width4.encode_experimental_geometry(shape) for shape in shapes),
            tuple(ReportingAnnotation(index, width4.shape_code(shape)) for index, shape in enumerate(shapes)),
        )
    if name == "extended":
        shapes = width4.extended_corpus()
        phase_index = {shape: index for index, shape in enumerate(v1.bounded_phase_1_corpus())}
        return (
            tuple(width4.encode_experimental_geometry(shape) for shape in shapes),
            tuple(ReportingAnnotation(index, width4.shape_code(shape), phase_index.get(shape)) for index, shape in enumerate(shapes)),
        )
    raise ValueError(f"unsupported corpus: {name}")


def _analyze_geometry_records(
    geometries: tuple[OrthogonalGeometry, ...],
    annotations: tuple[ReportingAnnotation, ...],
) -> dict[str, object]:
    """Perform one complete geometry-only replay before reporting is joined."""

    if len(geometries) != len(annotations):
        raise ValueError("geometries and reporting annotations must align")
    records = _dynamic_records(geometries)
    return {
        "size": len(geometries),
        "readers": {reader: _reader_report(records, annotations, reader) for reader in READERS},
        "controls": {
            reader: {
                "role": "control only; not coordinate-free success evidence",
                "distinct_signatures": len(_equivalence_groups(records, reader)),
            }
            for reader in CONTROLS
        },
        "signature_replay_digest": hashlib.sha256(json.dumps(
            [[_signature_digest(record[reader]) for reader in (*READERS, *CONTROLS)] for record in records],
            separators=(",", ":"),
        ).encode("utf-8")).hexdigest(),
    }


def _analyze_corpus(name: str) -> dict[str, object]:
    geometries, annotations = _corpus_entries(name)
    return _analyze_geometry_records(geometries, annotations)


def _transform_report(geometries: tuple[OrthogonalGeometry, ...]) -> dict[str, object]:
    translation_matches = {reader: 0 for reader in (*READERS, *CONTROLS)}
    reflection_matches = {reader: 0 for reader in (*READERS, *CONTROLS)}
    total_translation_cases = 0
    reflection_examples: list[int] = []
    permutation_counts = Counter()
    permutation_rejections = Counter()
    permutation_matches = {reader: 0 for reader in READERS}
    per_source: list[dict[str, object]] = []
    source_manifests: list[dict[str, object]] = []
    originals: list[dict[str, Signature]] = []
    cases: list[tuple[int, OrthogonalGeometry]] = []
    replay_digest = hashlib.sha256()
    for position, geometry in enumerate(geometries):
        original = coordinate_free_signatures(geometry)
        originals.append(original)
        for displacement in FIXED_TRANSLATIONS:
            candidate = coordinate_free_signatures(translate_geometry(geometry, displacement))
            total_translation_cases += 1
            for reader in translation_matches:
                translation_matches[reader] += candidate[reader] == original[reader]
        reflected = coordinate_free_signatures(horizontal_reflection(geometry))
        for reader in reflection_matches:
            reflection_matches[reader] += reflected[reader] == original[reader]
        if reflected["global_multiset"] == original["global_multiset"]:
            reflection_examples.append(position)
        variants, manifest = _component_permutation_cases(geometry)
        for field in (
            "raw_labelled_permutation_specifications",
            "duplicate_labelled_permutation_specifications",
            "candidate_cases",
            "valid_reconstructed_geometries",
            "invalid_or_rejected_cases",
            "duplicate_generated_geometries",
            "unique_valid_generated_geometries",
        ):
            permutation_counts[field] += int(manifest[field])
        permutation_rejections.update(manifest["rejection_reasons"])
        source_manifests.append(manifest)
        cases.extend((position, candidate_geometry) for candidate_geometry in variants)

    source_matches_by_position = [
        {reader: 0 for reader in READERS}
        for _geometry in geometries
    ]
    # Input order is retained.  Workers only make the bounded exhaustive
    # replay practical; every generated geometry still reaches the frozen
    # geometry-only dynamic entry point.
    with ProcessPoolExecutor(max_workers=4) as executor:
        signatures = executor.map(
            _derived_case_signatures,
            (geometry for _position, geometry in cases),
            chunksize=32,
        )
        for (position, candidate_geometry), candidate in zip(cases, signatures):
            replay_digest.update(json.dumps(
                {
                    "source_position": position,
                    "cells": candidate_geometry.cells,
                    "signature_sha256": {
                        reader: _signature_digest(candidate[reader])
                        for reader in READERS
                    },
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8"))
            for reader in permutation_matches:
                matched = candidate[reader] == originals[position][reader]
                permutation_matches[reader] += matched
                source_matches_by_position[position][reader] += matched
    for position, manifest in enumerate(source_manifests):
        per_source.append({
            "source_position": position,
            "candidate_cases": manifest["candidate_cases"],
            "valid_reconstructed_geometries": manifest[
                "valid_reconstructed_geometries"
            ],
            "per_reader_signature_matches": source_matches_by_position[position],
        })

    dynamically_evaluated_cases = permutation_counts[
        "unique_valid_generated_geometries"
    ]
    return {
        "protocol": {
            "fixed_translations": [list(value) for value in FIXED_TRANSLATIONS],
            "horizontal_reflection": "reflection in each geometry bounding box",
            "component_permutations": "all distinct permutations of normalized disconnected component shapes",
            "spatial_reorderings": "each permutation is rebuilt left-to-right with two empty columns between bounding boxes",
            "validity": "reconstruction rejects malformed shapes, invalid permutations, overlap, and touching components",
        },
        "counts": {
            "source_geometries": len(geometries),
            "translation_cases": total_translation_cases,
            "reflection_cases": len(geometries),
            "raw_labelled_permutation_specifications": permutation_counts[
                "raw_labelled_permutation_specifications"
            ],
            "duplicate_labelled_permutation_specifications": permutation_counts[
                "duplicate_labelled_permutation_specifications"
            ],
            "candidate_cases": permutation_counts["candidate_cases"],
            "valid_reconstructed_geometries": permutation_counts[
                "valid_reconstructed_geometries"
            ],
            "invalid_or_rejected_cases": permutation_counts[
                "invalid_or_rejected_cases"
            ],
            "duplicate_generated_geometries": permutation_counts[
                "duplicate_generated_geometries"
            ],
            "unique_valid_generated_geometries": permutation_counts[
                "unique_valid_generated_geometries"
            ],
            "dynamically_evaluated_cases": dynamically_evaluated_cases,
        },
        "translation_matches": translation_matches,
        "reflection_matches": reflection_matches,
        "rejection_reasons": dict(sorted(permutation_rejections.items())),
        "per_reader_signature_matches": permutation_matches,
        "derived_signature_replay_digest": replay_digest.hexdigest(),
        "per_source": per_source,
        "global_reflection_match_positions": reflection_examples,
    }


DYNAMIC_PARAMETER_ALLOW_LIST = {
    "coordinate_free_signatures": ("geometry",),
    "_derived_case_signatures": ("geometry",),
    "build_geometry_graph": ("geometry",),
    "canonical_component_probe": ("graph",),
    "probe_state": ("graph", "mode"),
    "evolve_euler_numerator": ("state", "graph", "denominator"),
    "dynamic_signatures_from_probe": ("graph", "probe", "denominator", "sample_steps"),
    "geometry_dynamic_signatures": ("geometry", "denominator", "sample_steps"),
    "_dynamic_records": ("geometries",),
    "_equivalence_groups": ("records", "reader"),
}
FORBIDDEN_IDENTITY_TOKENS = {
    "VisionShape", "Terminal", "OrderedGroup", "shape_code", "corpus_index",
    "phase_1_index", "serialize", "serialization", "address", "structural",
    "identity", "filename", "metadata", "annotation", "adapter", "encode_geometry",
    "decode_geometry", "id",
}


def _function_parameters(function: object) -> tuple[str, ...]:
    return tuple(inspect.signature(function).parameters)


def _identity_tokens(node: ast.AST) -> set[str]:
    tokens: set[str] = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Name):
            tokens.add(item.id)
        elif isinstance(item, ast.Attribute):
            tokens.add(item.attr)
        elif isinstance(item, ast.Constant) and isinstance(item.value, str):
            tokens.add(item.value)
    return tokens


def _called_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def identity_channel_audit(
    geometries: tuple[OrthogonalGeometry, ...],
    annotations: tuple[ReportingAnnotation, ...],
) -> dict[str, object]:
    """Audit the explicit geometry-only boundary and independent relabelling."""

    violations: dict[str, list[str]] = {}
    sensitive_calls = set(DYNAMIC_PARAMETER_ALLOW_LIST)
    for function in DYNAMIC_AUDIT_FUNCTIONS:
        name = function.__name__
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
        function_violations: list[str] = []
        parameters = _function_parameters(function)
        if parameters != DYNAMIC_PARAMETER_ALLOW_LIST[name]:
            function_violations.append("parameters=" + repr(parameters))
        forbidden_references = sorted(_identity_tokens(tree) & FORBIDDEN_IDENTITY_TOKENS)
        if forbidden_references:
            function_violations.append("forbidden_references=" + repr(forbidden_references))
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            if _called_name(call) not in sensitive_calls:
                continue
            forbidden_arguments = sorted(_identity_tokens(call) & FORBIDDEN_IDENTITY_TOKENS)
            if forbidden_arguments:
                function_violations.append("forbidden_call_argument=" + repr(forbidden_arguments))
        if function_violations:
            violations[name] = function_violations

    reporting_tree = ast.parse(textwrap.dedent(inspect.getsource(_reader_report)))
    reporting_calls = {
        _called_name(call) for call in ast.walk(reporting_tree)
        if isinstance(call, ast.Call)
    }
    annotation_lines = [node.lineno for node in ast.walk(reporting_tree)
                        if isinstance(node, ast.Name) and node.id == "annotations"
                        and isinstance(node.ctx, ast.Load)]
    equivalence_lines = [call.lineno for call in ast.walk(reporting_tree)
                         if isinstance(call, ast.Call) and _called_name(call) == "_equivalence_groups"]
    reporting_join_after_dynamic = (
        not (reporting_calls & {
            "coordinate_free_signatures", "_dynamic_records", "build_geometry_graph",
            "probe_state", "dynamic_signatures_from_probe", "geometry_dynamic_signatures",
        })
        and bool(equivalence_lines) and bool(annotation_lines)
        and min(equivalence_lines) < min(annotation_lines)
    )

    changed_annotations = tuple(
        ReportingAnnotation(10_000 + position, "relabeled-shape-" + str(position), 20_000 + position)
        for position in range(len(annotations))
    )
    # These are two separate complete replays; neither result is re-used for
    # the other computation or for equivalence grouping.
    baseline = _analyze_geometry_records(geometries, annotations)
    relabeled = _analyze_geometry_records(geometries, changed_annotations)
    baseline_memberships = tuple(
        baseline["readers"][reader]["equivalence_memberships"] for reader in READERS
    )
    relabeled_memberships = tuple(
        relabeled["readers"][reader]["equivalence_memberships"] for reader in READERS
    )
    return {
        "ast_passed": not violations and reporting_join_after_dynamic,
        "ast_violations": violations,
        "parameter_allow_list": {name: list(parameters) for name, parameters in DYNAMIC_PARAMETER_ALLOW_LIST.items()},
        "reporting_join_after_dynamic_records": reporting_join_after_dynamic,
        "coordinate_free_claim_readers": list(READERS),
        "control_readers_excluded_from_coordinate_free_claim": list(CONTROLS),
        "negative_annotation_control": {
            "annotations_changed": annotations != changed_annotations,
            "independent_complete_dynamic_recomputations": 2,
            "signatures_unchanged": baseline["signature_replay_digest"] == relabeled["signature_replay_digest"],
            "class_membership_unchanged": baseline_memberships == relabeled_memberships,
            "reporting_output_changed": baseline["readers"] != relabeled["readers"],
        },
        "limitations": [
            "The AST inspection checks declared Python sources and direct call expressions only.",
            "It cannot prove runtime behavior of dependencies, reflective code, monkeypatching, or all transitive information flows.",
        ],
    }


def _classify_collisions(
    corpus_name: str,
    corpus: dict[str, object],
    geometries: tuple[OrthogonalGeometry, ...],
    transforms: dict[str, object],
) -> list[dict[str, object]]:
    """Classify every computed non-singleton class without filtering it out."""

    classified: list[dict[str, object]] = []
    transform_sources = {
        item["source_position"]: item
        for item in transforms["per_source"]
    }
    for reader in READERS:
        for collision in corpus["readers"][reader]["collisions"]:
            positions = collision["positions"]
            pair = len(positions) == 2
            same_components = pair and (
                tuple(sorted(normalized_component_shapes(geometries[positions[0]])))
                == tuple(sorted(normalized_component_shapes(geometries[positions[1]])))
            )
            reflected = pair and horizontal_reflection(geometries[positions[0]]) == geometries[positions[1]]
            phase_1_indices = collision["phase_1_indices"]
            transformation_sources = (
                phase_1_indices
                if pair and all(type(index) is int for index in phase_1_indices)
                else []
            )
            all_reorderings_match = (
                len(transformation_sources) == 2
                and all(
                    index in transform_sources
                    and transform_sources[index]["per_reader_signature_matches"][reader]
                    == transform_sources[index]["valid_reconstructed_geometries"]
                    for index in transformation_sources
                )
            )
            structural = same_components and reflected and all_reorderings_match
            # This stable annotation is consulted only after collision classes
            # and structural evidence have already been computed.
            is_known_class = collision["phase_1_indices"] == [23, 41]
            classified.append({
                "corpus": corpus_name,
                "reader": reader,
                "positions": positions,
                "corpus_indices": collision["corpus_indices"],
                "phase_1_indices": collision["phase_1_indices"],
                "shape_codes": collision["shape_codes"],
                "classification": "structural" if structural else "unclassified",
                "is_known_phase_1_23_41_class": is_known_class,
                "transformation_source_phase_1_indices": list(transformation_sources),
                "justification": (
                    "Both geometries are reflected, have the same normalized disconnected-component multiset, and every generated valid component reordering of each source matches this reader."
                    if structural else "The bounded evidence does not establish an intentional quotient explanation; no accidental attribution is inferred."
                ),
                "explicit_invariants": [
                    "equal frozen reader signatures",
                    "same multiset of normalized disconnected component shapes",
                    "translation-invariant geometry-only graph construction and reader",
                ] if structural else [],
            })
    return classified


def _derive_additional_collisions(classifications: list[dict[str, object]]) -> list[dict[str, object]]:
    """Retain every collision other than the post-computation known class."""

    return [item for item in classifications if not item["is_known_phase_1_23_41_class"]]


@lru_cache(maxsize=1)
def analyze_experiment() -> dict[str, object]:
    phase_1 = _analyze_corpus("phase_1")
    held_out = _analyze_corpus("held_out")
    extended = _analyze_corpus("extended")
    phase_geometries, phase_annotations = _corpus_entries("phase_1")
    held_out_geometries, _held_out_annotations = _corpus_entries("held_out")
    extended_geometries, _extended_annotations = _corpus_entries("extended")
    transforms = _transform_report(phase_geometries)
    audit = identity_channel_audit(phase_geometries, phase_annotations)
    replay = _analyze_corpus("phase_1") == phase_1
    classifications = {
        "phase_1": _classify_collisions(
            "phase_1", phase_1, phase_geometries, transforms,
        ),
        "held_out": _classify_collisions(
            "held_out", held_out, held_out_geometries, transforms,
        ),
        "extended": _classify_collisions(
            "extended", extended, extended_geometries, transforms,
        ),
    }
    additional = {
        name: _derive_additional_collisions(items)
        for name, items in classifications.items()
    }
    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "dynamic_protocol": v1.PROTOCOL_ID,
            "euler_denominator": v1.EULER_DENOMINATOR,
            "sample_steps": list(v1.SAMPLE_STEPS),
            "reader_equivalence": {
                "global_multiset": "C ~ D iff their frozen global multiset signatures are equal",
                "component_multiset": "C ~ D iff their frozen component multiset signatures are equal",
            },
        },
        "corpora": {"phase_1": phase_1, "held_out": held_out, "extended": extended},
        "derived_transformations": transforms,
        "collision_classification": classifications,
        "phase_1_collision_classification": classifications["phase_1"],
        "additional_collisions": {
            **additional,
            "policy": "Derived after enumerating every non-singleton coordinate-free equivalence class; only the post-computation #23/#41 annotation is subtracted.",
        },
        "identity_channel_audit": audit,
        "deterministic_replay": replay,
        "bounded_claims": [
            "The two frozen coordinate-free readers induce the reported equality relations on these three bounded corpora.",
            "The Phase 1 reflected #23/#41 pair is structural for the declared component-order quotient evidence.",
        ],
        "limitations_and_non_claims": [
            "No theorem is claimed for unbounded shapes or arbitrary placements.",
            "Oriented and null_oriented results are controls, not coordinate-free success.",
            "This does not implement a decoder, FGS, factor graph, alternate graph, or production API.",
            "Accidental collisions are not inferred merely from a collision; absent evidence they remain unclassified.",
        ],
    }


def render_text_report(report: dict[str, object]) -> str:
    lines = [
        "===== PETRA VISION COORDINATE-FREE COLLISIONS =====",
        f"Protocol: {report['protocol']['dynamic_protocol']}",
        f"Euler denominator / samples: {report['protocol']['euler_denominator']} / {tuple(report['protocol']['sample_steps'])}",
        "",
    ]
    for name, label in (("phase_1", "Phase 1"), ("held_out", "Held-out width 4"), ("extended", "Extended")):
        corpus = report["corpora"][name]
        lines.append(f"{label}: {corpus['size']} geometries")
        for reader in READERS:
            result = corpus["readers"][reader]
            lines.append(f"  {reader}: {result['distinct_signatures']}/{corpus['size']}; collisions={len(result['collisions'])}")
        lines.append("")
    lines.extend([
        "Phase 1 classifications:",
        *[f"  {item['reader']}: {item['classification']} {item['corpus_indices']} {item['shape_codes']}" for item in report["phase_1_collision_classification"]],
        f"Derived permutation/reordering cases replayed: {report['derived_transformations']['counts']['dynamically_evaluated_cases']}",
        f"Identity audit passed: {report['identity_channel_audit']['ast_passed']}",
        f"Deterministic replay: {report['deterministic_replay']}",
        "Oriented and null_oriented observations are controls only.",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Characterize frozen PETRA VISION coordinate-free collisions.")
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON")
    parser.add_argument("--write-json", type=Path, metavar="PATH", help="write deterministic JSON")
    return parser


def _scientific_invariants_hold(report: dict[str, object]) -> bool:
    phase = report["corpora"]["phase_1"]
    held_out = report["corpora"]["held_out"]
    extended = report["corpora"]["extended"]
    expected_codes = ["G(G(G(T)),G(T,T))", "G(G(T,T),G(G(T)))"]
    return (
        report["protocol"]["euler_denominator"] == 8
        and report["protocol"]["sample_steps"] == [1, 2, 4, 8, 16, 32]
        and all(phase["readers"][reader]["distinct_signatures"] == 109 for reader in READERS)
        and all(held_out["readers"][reader]["distinct_signatures"] == 27 for reader in READERS)
        and all(extended["readers"][reader]["distinct_signatures"] == 136 for reader in READERS)
        and all(phase["readers"][reader]["collisions"][0]["corpus_indices"] == [23, 41] for reader in READERS)
        and all(phase["readers"][reader]["collisions"][0]["shape_codes"] == expected_codes for reader in READERS)
        and all(item["classification"] == "structural" for item in report["phase_1_collision_classification"])
        and report["identity_channel_audit"]["ast_passed"]
        and report["identity_channel_audit"]["negative_annotation_control"]["signatures_unchanged"]
        and report["identity_channel_audit"]["negative_annotation_control"]["class_membership_unchanged"]
        and report["identity_channel_audit"]["negative_annotation_control"]["reporting_output_changed"]
        and report["derived_transformations"]["counts"]["candidate_cases"]
        == report["derived_transformations"]["counts"]["dynamically_evaluated_cases"]
        and all(
            report["derived_transformations"]["per_reader_signature_matches"][reader]
            == report["derived_transformations"]["counts"]["dynamically_evaluated_cases"]
            for reader in READERS
        )
        and report["deterministic_replay"]
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_experiment()
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.write_json is not None:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(payload + "\n", encoding="utf-8")
    print(payload if args.json else render_text_report(report))
    return 0 if _scientific_invariants_hold(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
