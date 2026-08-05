#!/usr/bin/env python3
"""Reproducible bounded graph-Laplacian experiment for PETRA VISION."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from typing import TypeAlias

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from petra.vision import (  # noqa: E402
    Cell,
    OrderedGroup,
    OrthogonalGeometry,
    Terminal,
    VisionShape,
    encode_geometry,
    geometry_extent,
    normalize_geometry,
)

PROTOCOL_ID = "petra-vision-graph-laplacian-v1"
EULER_DENOMINATOR = 8
SAMPLE_STEPS = (1, 2, 4, 8, 16, 32)
NEIGHBOR_OFFSETS = (
    (-1, 0),
    (0, -1),
    (0, 1),
    (1, 0),
)

State: TypeAlias = tuple[int, ...]
Signature: TypeAlias = tuple[object, ...]


@dataclass(frozen=True)
class GeometryGraph:
    """Four-neighbor graph derived exclusively from occupied geometry cells."""

    cells: tuple[Cell, ...]
    adjacency: tuple[tuple[int, ...], ...]
    components: tuple[tuple[int, ...], ...]


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
                shapes.add(OrderedGroup(children=children))

    return tuple(sorted(shapes, key=repr))


@lru_cache(maxsize=1)
def bounded_phase_1_corpus() -> tuple[VisionShape, ...]:
    """Enumerate the bounded Phase 1 corpus independently of test modules."""

    shapes: set[VisionShape] = set()

    for node_count in range(1, 8):
        shapes.update(
            _shapes_with_exact_nodes(
                node_count,
                maximum_depth=3,
            )
        )

    corpus = tuple(sorted(shapes, key=repr))

    if len(corpus) != 110:
        raise RuntimeError(
            f"expected 110 bounded shapes, received {len(corpus)}"
        )

    return corpus


def shape_code(shape: VisionShape) -> str:
    """Return a stable structural code used only as result metadata."""

    if isinstance(shape, Terminal):
        return "T"

    return "G(" + ",".join(
        shape_code(child)
        for child in shape.children
    ) + ")"


def structural_profile(
    shape: VisionShape,
) -> tuple[int, int, tuple[int, ...]]:
    """Return node count, terminal count, and sorted local arities."""

    if isinstance(shape, Terminal):
        return 1, 1, (0,)

    nodes = 1
    terminals = 0
    arities = [len(shape.children)]

    for child in shape.children:
        child_nodes, child_terminals, child_arities = (
            structural_profile(child)
        )
        nodes += child_nodes
        terminals += child_terminals
        arities.extend(child_arities)

    return nodes, terminals, tuple(sorted(arities))


def build_geometry_graph(
    geometry: OrthogonalGeometry,
) -> GeometryGraph:
    """Derive a deterministic four-neighbor graph from geometry cells only."""

    if not isinstance(geometry, OrthogonalGeometry):
        raise TypeError("geometry must be an OrthogonalGeometry")

    cells = tuple(sorted(geometry.cells))
    index_by_cell = {
        cell: index
        for index, cell in enumerate(cells)
    }

    adjacency: list[tuple[int, ...]] = []

    for x, y in cells:
        neighbors = []

        for dx, dy in NEIGHBOR_OFFSETS:
            candidate = (x + dx, y + dy)

            if candidate in index_by_cell:
                neighbors.append(index_by_cell[candidate])

        adjacency.append(tuple(sorted(neighbors)))

    unseen = set(range(len(cells)))
    components: list[tuple[int, ...]] = []

    while unseen:
        start = min(unseen)
        unseen.remove(start)

        stack = [start]
        component: list[int] = []

        while stack:
            current = stack.pop()
            component.append(current)

            for neighbor in adjacency[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)

        components.append(tuple(sorted(component)))

    components.sort(
        key=lambda component: cells[component[0]]
    )

    return GeometryGraph(
        cells=cells,
        adjacency=tuple(adjacency),
        components=tuple(components),
    )


def graph_profile(
    graph: GeometryGraph,
) -> dict[str, object]:
    edge_count = sum(
        len(neighbors)
        for neighbors in graph.adjacency
    ) // 2

    isolated_count = sum(
        len(neighbors) == 0
        for neighbors in graph.adjacency
    )

    component_cycle_ranks = []

    for component in graph.components:
        component_edges = sum(
            len(graph.adjacency[vertex])
            for vertex in component
        ) // 2

        component_cycle_ranks.append(
            component_edges - len(component) + 1
        )

    return {
        "vertices": len(graph.cells),
        "edges": edge_count,
        "components": len(graph.components),
        "isolated_vertices": isolated_count,
        "component_cycle_ranks": tuple(
            sorted(component_cycle_ranks)
        ),
        "maximum_degree": max(
            (
                len(neighbors)
                for neighbors in graph.adjacency
            ),
            default=0,
        ),
    }


def canonical_component_probe(
    graph: GeometryGraph,
) -> State:
    """Place one unit impulse at the minimum vertex of each component."""

    state = [0] * len(graph.cells)

    for component in graph.components:
        state[component[0]] = 1

    return tuple(state)


def evolve_euler_numerator(
    state: State,
    graph: GeometryGraph,
    *,
    denominator: int = EULER_DENOMINATOR,
) -> State:
    """Advance one Euler step using exact common-denominator numerators."""

    if denominator <= 0:
        raise ValueError("denominator must be positive")

    next_state = []

    for vertex, neighbors in enumerate(graph.adjacency):
        laplacian_value = (
            len(neighbors) * state[vertex]
            - sum(state[neighbor] for neighbor in neighbors)
        )

        next_state.append(
            denominator * state[vertex]
            - laplacian_value
        )

    return tuple(next_state)



def probe_state(
    graph: GeometryGraph,
    mode: str,
) -> State:
    """Build a declared geometry-only initial state."""

    if mode == "minimum":
        return canonical_component_probe(graph)

    if mode == "zero":
        return tuple(0 for _cell in graph.cells)

    if mode == "constant":
        return tuple(1 for _cell in graph.cells)

    state = [0] * len(graph.cells)

    if mode == "maximum":
        for component in graph.components:
            state[component[-1]] = 1

        return tuple(state)

    if mode == "endpoints":
        for component in graph.components:
            state[component[0]] = 1
            state[component[-1]] = 1

        return tuple(state)

    raise ValueError(f"unsupported probe mode: {mode}")


def dynamic_signatures_from_probe(
    graph: GeometryGraph,
    probe: State,
    *,
    denominator: int = EULER_DENOMINATOR,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> dict[str, Signature]:
    """Calculate exact graph signatures from a declared initial state."""

    if denominator <= 0:
        raise ValueError("denominator must be positive")

    if len(probe) != len(graph.cells):
        raise ValueError(
            "probe length must equal the graph vertex count"
        )

    if not sample_steps:
        raise ValueError("sample_steps must not be empty")

    if tuple(sorted(set(sample_steps))) != sample_steps:
        raise ValueError(
            "sample_steps must be strictly increasing positive integers"
        )

    if sample_steps[0] <= 0:
        raise ValueError("sample_steps must contain positive integers")

    state = probe
    sample_set = set(sample_steps)

    global_samples = []
    component_samples = []
    oriented_samples = []

    for step in range(1, sample_steps[-1] + 1):
        state = evolve_euler_numerator(
            state,
            graph,
            denominator=denominator,
        )

        if step not in sample_set:
            continue

        global_samples.append(tuple(sorted(state)))

        component_samples.append(
            tuple(sorted(
                tuple(sorted(
                    state[vertex]
                    for vertex in component
                ))
                for component in graph.components
            ))
        )

        oriented_samples.append(state)

    return {
        "null_oriented": tuple(
            probe
            for _step in sample_steps
        ),
        "global_multiset": tuple(global_samples),
        "component_multiset": tuple(component_samples),
        "oriented": tuple(oriented_samples),
    }


def geometry_dynamic_signatures(
    geometry: OrthogonalGeometry,
    *,
    denominator: int = EULER_DENOMINATOR,
    sample_steps: tuple[int, ...] = SAMPLE_STEPS,
) -> dict[str, Signature]:
    """Calculate canonical signatures using geometry-only input."""

    graph = build_geometry_graph(geometry)

    return dynamic_signatures_from_probe(
        graph,
        probe_state(graph, "minimum"),
        denominator=denominator,
        sample_steps=sample_steps,
    )

def horizontal_reflection(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    width, _height = geometry_extent(geometry)

    reflected_cells = tuple(sorted(
        (width - 1 - x, y)
        for x, y in geometry.cells
    ))

    return normalize_geometry(
        OrthogonalGeometry(cells=reflected_cells)
    )


def normalized_component_shapes(
    geometry: OrthogonalGeometry,
) -> tuple[tuple[Cell, ...], ...]:
    graph = build_geometry_graph(geometry)
    normalized_components = []

    for component in graph.components:
        cells = tuple(
            graph.cells[vertex]
            for vertex in component
        )
        min_x = min(x for x, _y in cells)
        min_y = min(y for _x, y in cells)

        normalized_components.append(tuple(sorted(
            (x - min_x, y - min_y)
            for x, y in cells
        )))

    return tuple(sorted(normalized_components))


def signature_digest(signature: Signature) -> str:
    payload = json.dumps(
        signature,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def summarize_signatures(
    signatures: list[Signature],
) -> dict[str, object]:
    groups: dict[Signature, list[int]] = defaultdict(list)

    for index, signature in enumerate(signatures):
        groups[signature].append(index)

    collision_groups = [
        indices
        for indices in groups.values()
        if len(indices) > 1
    ]

    return {
        "distinct_signatures": len(groups),
        "collision_group_count": len(collision_groups),
        "colliding_shape_count": sum(
            len(group)
            for group in collision_groups
        ),
        "collision_groups": collision_groups,
        "collision_size_distribution": {
            str(size): count
            for size, count in sorted(
                Counter(
                    len(group)
                    for group in collision_groups
                ).items()
            )
        },
    }




def unary_terminal_expansions(
    shape: VisionShape,
) -> tuple[VisionShape, ...]:
    """Expand exactly one terminal occurrence into a unary ordered group."""

    mutations: set[VisionShape] = set()

    if isinstance(shape, Terminal):
        mutations.add(
            OrderedGroup(children=(Terminal(),))
        )
        return tuple(mutations)

    for index, child in enumerate(shape.children):
        for mutated_child in unary_terminal_expansions(child):
            children = list(shape.children)
            children[index] = mutated_child

            mutations.add(
                OrderedGroup(children=tuple(children))
            )

    return tuple(sorted(mutations, key=repr))



def analyze_elementary_statistics_control(
    geometries: tuple[OrthogonalGeometry, ...],
    primary_signatures: tuple[Signature, ...],
) -> dict[str, object]:
    """Compare shapes sharing the same elementary graph statistics."""

    if len(geometries) != len(primary_signatures):
        raise ValueError(
            "geometry and signature collections must have equal length"
        )

    groups: dict[tuple[object, ...], list[int]] = defaultdict(list)

    for index, geometry in enumerate(geometries):
        graph = build_geometry_graph(geometry)
        profile = graph_profile(graph)

        elementary_key = (
            profile["vertices"],
            profile["edges"],
            profile["components"],
            profile["isolated_vertices"],
            geometry_extent(geometry),
        )

        groups[elementary_key].append(index)

    shared_groups = tuple(
        tuple(indices)
        for indices in groups.values()
        if len(indices) > 1
    )

    detected_pairs: list[list[int]] = []
    undetected_pairs: list[list[int]] = []

    for indices in shared_groups:
        for left, right in combinations(indices, 2):
            pair = [left, right]

            if primary_signatures[left] == primary_signatures[right]:
                undetected_pairs.append(pair)
            else:
                detected_pairs.append(pair)

    return {
        "elementary_statistics": (
            "vertices, edges, connected components, isolated vertices, "
            "and geometry extent"
        ),
        "shared_group_count": len(shared_groups),
        "involved_shape_count": sum(
            len(indices)
            for indices in shared_groups
        ),
        "comparable_pair_count": (
            len(detected_pairs) + len(undetected_pairs)
        ),
        "detected_pair_count": len(detected_pairs),
        "undetected_pair_count": len(undetected_pairs),
        "undetected_pairs": undetected_pairs,
        "first_detected_pairs": detected_pairs[:8],
    }


def analyze_local_mutation_sensitivity(
    corpus: tuple[VisionShape, ...],
    primary_signatures: tuple[Signature, ...],
) -> dict[str, object]:
    """Measure bounded sensitivity to one-node terminal expansion."""

    if len(corpus) != len(primary_signatures):
        raise ValueError(
            "corpus and signature collections must have equal length"
        )

    corpus_indices = {
        shape: index
        for index, shape in enumerate(corpus)
    }

    mutation_pairs: set[tuple[int, int]] = set()

    for source_index, source_shape in enumerate(corpus):
        for target_shape in unary_terminal_expansions(
            source_shape
        ):
            target_index = corpus_indices.get(target_shape)

            if target_index is not None:
                mutation_pairs.add(
                    (source_index, target_index)
                )

    ordered_pairs = tuple(sorted(mutation_pairs))
    detected_pairs = []
    undetected_pairs = []

    for source_index, target_index in ordered_pairs:
        pair = [source_index, target_index]

        if (
            primary_signatures[source_index]
            != primary_signatures[target_index]
        ):
            detected_pairs.append(pair)
        else:
            undetected_pairs.append(pair)

    source_indices = {
        source_index
        for source_index, _target_index in ordered_pairs
    }
    target_indices = {
        target_index
        for _source_index, target_index in ordered_pairs
    }

    return {
        "mutation": (
            "replace one Terminal occurrence with "
            "OrderedGroup((Terminal(),))"
        ),
        "valid_pair_count": len(ordered_pairs),
        "detected_pair_count": len(detected_pairs),
        "undetected_pair_count": len(undetected_pairs),
        "mutable_source_count": len(source_indices),
        "reached_target_count": len(target_indices),
        "detected_pairs": detected_pairs,
        "undetected_pairs": undetected_pairs,
    }


def analyze_probe_sensitivity(
    geometries: tuple[OrthogonalGeometry, ...],
) -> dict[str, object]:
    """Measure distinguishability under declared initial-state controls."""

    probe_modes = (
        "zero",
        "minimum",
        "maximum",
        "endpoints",
        "constant",
    )

    results: dict[str, object] = {}

    for mode in probe_modes:
        signatures_by_reader: dict[str, list[Signature]] = {
            "global_multiset": [],
            "component_multiset": [],
            "oriented": [],
        }

        for geometry in geometries:
            graph = build_geometry_graph(geometry)
            signatures = dynamic_signatures_from_probe(
                graph,
                probe_state(graph, mode),
            )

            for reader in signatures_by_reader:
                signatures_by_reader[reader].append(
                    signatures[reader]
                )

        results[mode] = {
            reader: summarize_signatures(signatures)
            for reader, signatures in signatures_by_reader.items()
        }

    return results


def analyze_temporal_sensitivity(
    geometries: tuple[OrthogonalGeometry, ...],
) -> dict[str, object]:
    """Measure sensitivity to integration step and sampling duration."""

    graphs = tuple(
        build_geometry_graph(geometry)
        for geometry in geometries
    )

    schedules = {
        "final_32": (32,),
        "early": (1, 2, 4, 8),
        "sparse": (1, 4, 16, 32),
        "primary": SAMPLE_STEPS,
        "extended": (1, 2, 4, 8, 16, 32, 64),
    }

    results: dict[str, object] = {}

    for probe_mode in ("minimum", "maximum"):
        denominator_results: dict[str, object] = {}

        for denominator in (4, 8, 16):
            schedule_results: dict[str, object] = {}

            for schedule_name, sample_steps in schedules.items():
                signatures = [
                    dynamic_signatures_from_probe(
                        graph,
                        probe_state(graph, probe_mode),
                        denominator=denominator,
                        sample_steps=sample_steps,
                    )["global_multiset"]
                    for graph in graphs
                ]

                schedule_results[schedule_name] = (
                    summarize_signatures(signatures)
                )

            denominator_results[str(denominator)] = (
                schedule_results
            )

        results[probe_mode] = denominator_results

    return results


@lru_cache(maxsize=1)
def analyze_experiment() -> dict[str, object]:
    corpus = bounded_phase_1_corpus()

    signatures_by_reader: dict[str, list[Signature]] = {
        "null_oriented": [],
        "global_multiset": [],
        "component_multiset": [],
        "oriented": [],
    }

    shape_records = []
    maximum_degree = 0
    component_counts = []
    component_node_matches = 0
    isolated_terminal_matches = 0
    cycle_arity_matches = 0
    replay_exact = True

    geometries: list[OrthogonalGeometry] = []

    for index, shape in enumerate(corpus):
        geometry = encode_geometry(shape)
        geometries.append(geometry)

        graph = build_geometry_graph(geometry)
        graph_data = graph_profile(graph)
        structural_nodes, terminals, arities = structural_profile(shape)

        component_node_matches += (
            graph_data["components"] == structural_nodes
        )
        isolated_terminal_matches += (
            graph_data["isolated_vertices"] == terminals
        )
        cycle_arity_matches += (
            graph_data["component_cycle_ranks"] == arities
        )

        maximum_degree = max(
            maximum_degree,
            int(graph_data["maximum_degree"]),
        )
        component_counts.append(
            int(graph_data["components"])
        )

        dynamic = geometry_dynamic_signatures(geometry)

        replay = geometry_dynamic_signatures(geometry)
        replay_exact = replay_exact and replay == dynamic

        digests = {}

        for reader, signature in dynamic.items():
            signatures_by_reader[reader].append(signature)
            digests[reader] = signature_digest(signature)

        shape_records.append({
            "index": index,
            "shape": shape_code(shape),
            "extent": list(geometry_extent(geometry)),
            "occupied_cells": len(geometry.cells),
            "components": graph_data["components"],
            "isolated_vertices": graph_data["isolated_vertices"],
            "signature_sha256": digests,
        })

    reader_results = {
        reader: summarize_signatures(signatures)
        for reader, signatures in signatures_by_reader.items()
    }

    geometry_tuple = tuple(geometries)
    probe_sensitivity = analyze_probe_sensitivity(
        geometry_tuple
    )
    temporal_sensitivity = analyze_temporal_sensitivity(
        geometry_tuple
    )
    primary_signature_tuple = tuple(
        signatures_by_reader["global_multiset"]
    )

    local_mutation_sensitivity = (
        analyze_local_mutation_sensitivity(
            corpus,
            primary_signature_tuple,
        )
    )
    elementary_statistics_control = (
        analyze_elementary_statistics_control(
            geometry_tuple,
            primary_signature_tuple,
        )
    )

    primary_collisions = reader_results[
        "global_multiset"
    ]["collision_groups"]

    collision_analysis: dict[str, object] | None = None

    if primary_collisions == [[23, 41]]:
        left = geometries[23]
        right = geometries[41]

        collision_analysis = {
            "indices": [23, 41],
            "geometries_identical": left == right,
            "horizontal_reflections": (
                horizontal_reflection(left) == right
            ),
            "same_normalized_component_multiset": (
                normalized_component_shapes(left)
                == normalized_component_shapes(right)
            ),
        }

    return {
        "protocol": {
            "id": PROTOCOL_ID,
            "graph": "occupied cells with four-neighbor orthogonal adjacency",
            "laplacian": "combinatorial L = D - A",
            "boundary_condition": "natural disconnected graph boundary",
            "integration": "explicit Euler with exact integer numerators",
            "euler_denominator": EULER_DENOMINATOR,
            "sample_steps": list(SAMPLE_STEPS),
            "probe": (
                "unit impulse at the lexicographically minimum "
                "vertex of every connected component"
            ),
        },
        "corpus": {
            "size": len(corpus),
            "maximum_degree": maximum_degree,
            "minimum_components": min(component_counts),
            "maximum_components": max(component_counts),
        },
        "structural_controls": {
            "components_equal_structural_nodes": (
                component_node_matches
            ),
            "isolated_vertices_equal_terminals": (
                isolated_terminal_matches
            ),
            "component_cycle_ranks_equal_local_arities": (
                cycle_arity_matches
            ),
        },
        "readers": reader_results,
        "deterministic_replay": replay_exact,
        "primary_collision": collision_analysis,
        "probe_sensitivity": probe_sensitivity,
        "temporal_sensitivity": temporal_sensitivity,
        "local_mutation_sensitivity": (
            local_mutation_sensitivity
        ),
        "elementary_statistics_control": (
            elementary_statistics_control
        ),
        "shapes": shape_records,
    }


def render_text_report(report: dict[str, object]) -> str:
    protocol = report["protocol"]
    corpus = report["corpus"]
    controls = report["structural_controls"]
    readers = report["readers"]

    lines = [
        "===== PETRA VISION GRAPH-LAPLACIAN =====",
        f"Protocollo:                    {protocol['id']}",
        f"Forme:                         {corpus['size']}",
        f"Denominatore Euler:            {protocol['euler_denominator']}",
        f"Passi campionati:              {tuple(protocol['sample_steps'])}",
        f"Grado massimo:                 {corpus['maximum_degree']}",
        (
            "Componenti min/max:            "
            f"{corpus['minimum_components']} / "
            f"{corpus['maximum_components']}"
        ),
        "",
        "Controlli strutturali:",
        (
            "  componenti = nodi:           "
            f"{controls['components_equal_structural_nodes']}/110"
        ),
        (
            "  isolati = terminali:          "
            f"{controls['isolated_vertices_equal_terminals']}/110"
        ),
        (
            "  cicli componente = arità:     "
            f"{controls['component_cycle_ranks_equal_local_arities']}/110"
        ),
        "",
    ]

    labels = {
        "null_oriented": "Controllo nullo orientato",
        "global_multiset": "Diffusione, multinsieme globale",
        "component_multiset": "Diffusione, componenti separate",
        "oriented": "Diffusione, lettore orientato",
    }

    for reader in (
        "null_oriented",
        "global_multiset",
        "component_multiset",
        "oriented",
    ):
        result = readers[reader]
        lines.extend([
            f"{labels[reader]}:",
            (
                "  firme distinte:              "
                f"{result['distinct_signatures']}/110"
            ),
            (
                "  collisioni:                  "
                f"{result['collision_groups']}"
            ),
            "",
        ])

    probe_sensitivity = report["probe_sensitivity"]
    temporal_sensitivity = report["temporal_sensitivity"]

    lines.append("Sensibilità al probe:")

    for probe_name in (
        "zero",
        "minimum",
        "maximum",
        "endpoints",
        "constant",
    ):
        result = probe_sensitivity[probe_name][
            "global_multiset"
        ]
        first_collisions = result["collision_groups"][:3]

        lines.append(
            f"  {probe_name:10s} "
            f"{result['distinct_signatures']}/110, "
            f"gruppi={result['collision_group_count']}, "
            f"forme={result['colliding_shape_count']}, "
            f"prime={first_collisions}"
        )

    lines.extend([
        "",
        "Sensibilità temporale, lettore globale:",
    ])

    for denominator in ("4", "8", "16"):
        primary = temporal_sensitivity["minimum"][
            denominator
        ]["primary"]
        early = temporal_sensitivity["minimum"][
            denominator
        ]["early"]

        lines.append(
            f"  denominatore {denominator}: "
            f"primario={primary['distinct_signatures']}/110, "
            f"precoce={early['distinct_signatures']}/110"
        )

    lines.append("")

    local_mutations = report[
        "local_mutation_sensitivity"
    ]

    lines.append("Sensibilità alle mutazioni locali:")
    lines.append(
        "  coppie valide/rilevate:        "
        f"{local_mutations['valid_pair_count']} / "
        f"{local_mutations['detected_pair_count']}"
    )
    lines.append(
        "  mutazioni non rilevate:        "
        f"{local_mutations['undetected_pair_count']}"
    )
    lines.append(
        "  sorgenti/destinazioni coperte: "
        f"{local_mutations['mutable_source_count']} / "
        f"{local_mutations['reached_target_count']}"
    )
    lines.append("")

    elementary = report[
        "elementary_statistics_control"
    ]

    lines.append("Controllo delle statistiche elementari:")
    lines.append(
        "  gruppi condivisi / forme:      "
        f"{elementary['shared_group_count']} / "
        f"{elementary['involved_shape_count']}"
    )
    lines.append(
        "  coppie confrontate/rilevate:   "
        f"{elementary['comparable_pair_count']} / "
        f"{elementary['detected_pair_count']}"
    )
    lines.append(
        "  coppie non distinte:           "
        f"{elementary['undetected_pairs']}"
    )
    lines.append("")

    collision = report["primary_collision"]

    lines.extend([
        "Collisione primaria:",
        f"  analisi:                     {collision}",
        "",
        (
            "Replay deterministico:          "
            f"{report['deterministic_replay']}"
        ),
    ])

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the bounded PETRA VISION graph-Laplacian "
            "research experiment."
        )
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable report",
    )
    parser.add_argument(
        "--write-json",
        type=Path,
        metavar="PATH",
        help="write the machine-readable report to PATH",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_experiment()

    if args.write_json is not None:
        args.write_json.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.write_json.write_text(
            json.dumps(
                report,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(
            report,
            indent=2,
            sort_keys=True,
        ))
    else:
        print(render_text_report(report))

    expected = (
        report["corpus"]["size"] == 110
        and report["deterministic_replay"] is True
    )

    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
