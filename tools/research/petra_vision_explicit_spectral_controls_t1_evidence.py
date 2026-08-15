#!/usr/bin/env python3
"""Deterministic evidence runner for PETRA VISION Gate 3 G3-T1."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(SOURCE_ROOT),
    )


T1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_t1.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)

T1_PROTOCOL_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "research"
    / "petra-vision"
    / "EXPLICIT_SPECTRAL_CONTROLS_T1_PROTOCOL.md"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-t1-evidence-v0"
)

EXPECTED_T1_PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-t1-v0"
)

CORPORA = (
    "phase1",
    "heldout",
    "extended",
)

CHANNELS = (
    "B0",
    "D1-null",
    "D1-coupled",
    "F1",
    "L1",
)

EXPECTED_COLLISION = tuple(sorted((
    "G(G(G(T)),G(T,T))",
    "G(G(T,T),G(G(T)))",
)))


def _load_module(
    path: Path,
    name: str,
) -> ModuleType:
    existing = sys.modules.get(
        name
    )

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

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module
    spec.loader.exec_module(
        module
    )

    return module


t1 = _load_module(
    T1_TOOL_PATH,
    "_petra_vision_gate3_t1_evidence_tool",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate3_t1_evidence_width4",
)


if t1.PROTOCOL_ID != EXPECTED_T1_PROTOCOL_ID:
    raise RuntimeError(
        "evidence runner requires frozen G3-T1 protocol"
    )

if t1.SUBSTRATES != (
    "B0",
    "D1",
    "F1",
    "L1",
):
    raise RuntimeError(
        "evidence runner requires frozen T1 substrate scope"
    )

if t1.REDUCTIONS != (
    "ordered",
    "unordered",
    "endpoints",
    "terminal",
):
    raise RuntimeError(
        "evidence runner requires frozen T1 reductions"
    )

if t1.SAMPLE_STEPS != (
    1,
    2,
    4,
    8,
    16,
    32,
):
    raise RuntimeError(
        "evidence runner requires frozen T1 sample schedule"
    )

if t1.TRANSLATION_VECTOR != (
    17,
    11,
):
    raise RuntimeError(
        "evidence runner requires frozen T1 translation vector"
    )


def _sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _canonical_json_bytes(
    value: object,
) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )


def _signature_digest(
    signature: object,
) -> str:
    return hashlib.sha256(
        _canonical_json_bytes(
            signature
        )
    ).hexdigest()


def _collision_groups(
    codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> tuple[
    tuple[str, ...],
    ...,
]:
    if len(codes) != len(signatures):
        raise ValueError(
            "codes and signatures must have equal length"
        )

    groups: dict[
        object,
        list[str],
    ] = defaultdict(list)

    for code, signature in zip(
        codes,
        signatures,
    ):
        groups[
            signature
        ].append(
            code
        )

    return tuple(sorted(
        tuple(sorted(group))
        for group in groups.values()
        if len(group) > 1
    ))


def _collision_pairs_from_groups(
    groups: Iterable[
        tuple[str, ...]
    ],
) -> set[
    tuple[str, str]
]:
    pairs: set[
        tuple[str, str]
    ] = set()

    for group in groups:
        for left, right in combinations(
            group,
            2,
        ):
            pairs.add(
                tuple(sorted((
                    left,
                    right,
                )))
            )

    return pairs


def summarize_signatures(
    codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> dict[str, object]:
    groups = _collision_groups(
        codes,
        signatures,
    )

    pairs = (
        _collision_pairs_from_groups(
            groups
        )
    )

    size_distribution = Counter(
        len(group)
        for group in groups
    )

    return {
        "distinct_signatures": len(
            set(signatures)
        ),
        "collision_group_count": len(
            groups
        ),
        "colliding_shape_count": sum(
            len(group)
            for group in groups
        ),
        "collision_pair_count": len(
            pairs
        ),
        "maximum_collision_group_size": max(
            (
                len(group)
                for group in groups
            ),
            default=1,
        ),
        "collision_size_distribution": {
            str(size): count
            for size, count in sorted(
                size_distribution.items()
            )
        },
        "collision_shape_codes": [
            list(group)
            for group in groups
        ],
    }


def compare_partitions(
    control_summary: dict[str, object],
    candidate_summary: dict[str, object],
) -> dict[str, object]:
    control_groups = tuple(
        tuple(group)
        for group in control_summary[
            "collision_shape_codes"
        ]
    )

    candidate_groups = tuple(
        tuple(group)
        for group in candidate_summary[
            "collision_shape_codes"
        ]
    )

    control_pairs = (
        _collision_pairs_from_groups(
            control_groups
        )
    )

    candidate_pairs = (
        _collision_pairs_from_groups(
            candidate_groups
        )
    )

    split = sorted(
        control_pairs
        - candidate_pairs
    )

    introduced = sorted(
        candidate_pairs
        - control_pairs
    )

    return {
        "distinct_signature_delta": (
            int(candidate_summary[
                "distinct_signatures"
            ])
            - int(control_summary[
                "distinct_signatures"
            ])
        ),
        "control_collision_pair_count": len(
            control_pairs
        ),
        "candidate_collision_pair_count": len(
            candidate_pairs
        ),
        "split_pair_count": len(
            split
        ),
        "introduced_pair_count": len(
            introduced
        ),
        "split_pairs": [
            list(pair)
            for pair in split
        ],
        "introduced_pairs": [
            list(pair)
            for pair in introduced
        ],
    }


def expected_pair_status(
    codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> dict[str, object]:
    index = {
        code: position
        for position, code in enumerate(
            codes
        )
    }

    present = all(
        code in index
        for code in EXPECTED_COLLISION
    )

    if not present:
        return {
            "present": False,
            "collides": None,
        }

    left, right = EXPECTED_COLLISION

    return {
        "present": True,
        "collides": (
            signatures[
                index[left]
            ]
            == signatures[
                index[right]
            ]
        ),
    }


def analyze_channel(
    *,
    codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> dict[str, object]:
    return {
        "summary": summarize_signatures(
            codes,
            signatures,
        ),
        "expected_collision": (
            expected_pair_status(
                codes,
                signatures,
            )
        ),
        "signature_digests": [
            _signature_digest(
                signature
            )
            for signature in signatures
        ],
    }


def _select_corpus(
    name: str,
):
    if name == "phase1":
        return width4.phase_1_corpus()

    if name == "heldout":
        return width4.held_out_corpus()

    if name == "extended":
        return width4.extended_corpus()

    raise ValueError(
        f"unsupported corpus: {name}"
    )


def _channel_parameters(
    channel: str,
) -> tuple[
    str,
    bool | None,
]:
    if channel == "B0":
        return (
            "B0",
            None,
        )

    if channel == "D1-null":
        return (
            "D1",
            False,
        )

    if channel == "D1-coupled":
        return (
            "D1",
            True,
        )

    if channel == "F1":
        return (
            "F1",
            None,
        )

    if channel == "L1":
        return (
            "L1",
            None,
        )

    raise ValueError(
        f"unsupported T1 evidence channel: {channel}"
    )


def _assert_equal(
    left: object,
    right: object,
    *,
    message: str,
) -> None:
    if left != right:
        raise RuntimeError(
            message
        )


def _reduction_signatures(
    trajectories: tuple[
        tuple[object, ...],
        ...,
    ],
    reduction: str,
) -> tuple[object, ...]:
    return tuple(
        t1.temporal_reduction(
            trajectory,
            reduction,
        )
        for trajectory in trajectories
    )


def _prefix_signatures(
    trajectories: tuple[
        tuple[object, ...],
        ...,
    ],
    *,
    unordered: bool,
    length: int,
) -> tuple[object, ...]:
    if length < 1 or length > len(
        t1.SAMPLE_STEPS
    ):
        raise ValueError(
            "prefix length outside frozen schedule"
        )

    signatures = []

    for trajectory in trajectories:
        prefixes = (
            t1.unordered_prefixes(
                trajectory
            )
            if unordered
            else t1.ordered_prefixes(
                trajectory
            )
        )

        signatures.append(
            prefixes[
                length - 1
            ]
        )

    return tuple(
        signatures
    )


def _pair_diagnostics(
    codes: tuple[str, ...],
    step_zero: tuple[object, ...],
    trajectories: tuple[
        tuple[object, ...],
        ...,
    ],
) -> dict[str, object]:
    if not (
        len(codes)
        == len(step_zero)
        == len(trajectories)
    ):
        raise ValueError(
            "pair diagnostic collections must align"
        )

    first_divergence_groups: dict[
        str,
        list[list[str]],
    ] = defaultdict(list)

    persistence_groups: dict[
        str,
        list[list[str]],
    ] = defaultdict(list)

    step_zero_collision_pair_count = 0

    for left_index, right_index in combinations(
        range(
            len(codes)
        ),
        2,
    ):
        left_code = codes[
            left_index
        ]

        right_code = codes[
            right_index
        ]

        pair = list(sorted((
            left_code,
            right_code,
        )))

        if (
            step_zero[left_index]
            == step_zero[right_index]
        ):
            step_zero_collision_pair_count += 1

            first = t1.first_divergence_time(
                trajectories[
                    left_index
                ],
                trajectories[
                    right_index
                ],
            )

            key = (
                "none-within-frozen-horizon"
                if first is None
                else str(first)
            )

            first_divergence_groups[
                key
            ].append(
                pair
            )

        label, pattern = t1.persistence_pattern(
            trajectories[
                left_index
            ],
            trajectories[
                right_index
            ],
        )

        pattern_key = (
            label
            + ":"
            + "".join(
                "1" if value else "0"
                for value in pattern
            )
        )

        persistence_groups[
            pattern_key
        ].append(
            pair
        )

    return {
        "first_divergence": {
            "step_zero_collision_pair_count": (
                step_zero_collision_pair_count
            ),
            "distribution": {
                key: len(value)
                for key, value in sorted(
                    first_divergence_groups.items()
                )
            },
            "pairs": {
                key: value
                for key, value in sorted(
                    first_divergence_groups.items()
                )
            },
        },
        "persistence": {
            "distribution": {
                key: len(value)
                for key, value in sorted(
                    persistence_groups.items()
                )
            },
            "pairs": {
                key: value
                for key, value in sorted(
                    persistence_groups.items()
                )
            },
        },
    }


def _transport_state(
    original_cells: tuple[
        tuple[int, int],
        ...,
    ],
    reflected_cells: tuple[
        tuple[int, int],
        ...,
    ],
    state: tuple[int, ...],
) -> tuple[int, ...]:
    if len(original_cells) != len(state):
        raise ValueError(
            "state/cell length mismatch"
        )

    xmin = min(
        x
        for x, _y in original_cells
    )

    xmax = max(
        x
        for x, _y in original_cells
    )

    index = {
        cell: position
        for position, cell in enumerate(
            reflected_cells
        )
    }

    transported = [
        0
        for _cell in reflected_cells
    ]

    for position, (x, y) in enumerate(
        original_cells
    ):
        reflected_cell = (
            xmin + xmax - x,
            y,
        )

        transported[
            index[
                reflected_cell
            ]
        ] = state[
            position
        ]

    return tuple(
        transported
    )


def _transported_b0_trajectory(
    geometry,
) -> object:
    reflected = t1.horizontal_reflection(
        geometry
    )

    original_graph = t1.b0.build_geometry_graph(
        geometry
    )

    reflected_graph = t1.b0.build_geometry_graph(
        reflected
    )

    original_probe = (
        t1.b0.canonical_component_probe(
            original_graph
        )
    )

    transported_probe = _transport_state(
        original_graph.cells,
        reflected_graph.cells,
        original_probe,
    )

    raw = t1._euler_raw_trajectory(
        transported_probe,
        lambda state: t1.b0.evolve_euler_numerator(
            state,
            reflected_graph,
            denominator=t1.b0.EULER_DENOMINATOR,
        ),
        sample_steps=t1.SAMPLE_STEPS,
    )

    return t1._normalize_raw_trajectory(
        raw,
        denominator=t1.b0.EULER_DENOMINATOR,
        sample_steps=t1.SAMPLE_STEPS,
    )


def _transported_d1_trajectory(
    geometry,
    *,
    coupled: bool,
) -> object:
    reflected = t1.horizontal_reflection(
        geometry
    )

    bridge_weight = (
        t1.d1.BRIDGE_WEIGHT
        if coupled
        else 0
    )

    original_graph = (
        t1.d1.build_distance2_graph(
            geometry,
            bridge_weight=bridge_weight,
        )
    )

    reflected_graph = (
        t1.d1.build_distance2_graph(
            reflected,
            bridge_weight=bridge_weight,
        )
    )

    original_probe = (
        t1.d1.original_component_probe(
            original_graph
        )
    )

    transported_probe = _transport_state(
        original_graph.cells,
        reflected_graph.cells,
        original_probe,
    )

    raw = t1._euler_raw_trajectory(
        transported_probe,
        lambda state: t1.d1.evolve_weighted_euler_numerator(
            state,
            reflected_graph,
            denominator=t1.d1.EULER_DENOMINATOR,
        ),
        sample_steps=t1.SAMPLE_STEPS,
    )

    return t1._normalize_raw_trajectory(
        raw,
        denominator=t1.d1.EULER_DENOMINATOR,
        sample_steps=t1.SAMPLE_STEPS,
    )


def _reflection_audit(
    channel: str,
    geometry,
    original_trajectory: object,
) -> bool:
    if channel == "B0":
        return (
            _transported_b0_trajectory(
                geometry
            )
            == original_trajectory
        )

    if channel == "D1-null":
        return (
            _transported_d1_trajectory(
                geometry,
                coupled=False,
            )
            == original_trajectory
        )

    if channel == "D1-coupled":
        return (
            _transported_d1_trajectory(
                geometry,
                coupled=True,
            )
            == original_trajectory
        )

    substrate, coupled = (
        _channel_parameters(
            channel
        )
    )

    reflected = t1.horizontal_reflection(
        geometry
    )

    return (
        t1.normalized_trajectory(
            substrate,
            reflected,
            coupled=coupled,
        )
        == original_trajectory
    )


def _raw_audit(
    *,
    codes: tuple[str, ...],
    substrate: str,
    coupled: bool | None,
    geometries: tuple[object, ...],
    normalized_reductions: dict[
        str,
        dict[str, object],
    ],
) -> dict[str, object] | None:
    if substrate == "F1":
        return None

    raw_trajectories = tuple(
        t1.raw_numerator_trajectory(
            substrate,
            geometry,
            coupled=coupled,
        )
        for geometry in geometries
    )

    raw_reductions: dict[
        str,
        dict[str, object],
    ] = {}

    for reduction in t1.REDUCTIONS:
        signatures = _reduction_signatures(
            raw_trajectories,
            reduction,
        )

        raw_reductions[
            reduction
        ] = analyze_channel(
            codes=codes,
            signatures=signatures,
        )

    raw_ordered_pairs = (
        _collision_pairs_from_groups(
            tuple(
                tuple(group)
                for group in raw_reductions[
                    "ordered"
                ][
                    "summary"
                ][
                    "collision_shape_codes"
                ]
            )
        )
    )

    normalized_ordered_pairs = (
        _collision_pairs_from_groups(
            tuple(
                tuple(group)
                for group in normalized_reductions[
                    "ordered"
                ][
                    "summary"
                ][
                    "collision_shape_codes"
                ]
            )
        )
    )

    if (
        raw_ordered_pairs
        != normalized_ordered_pairs
    ):
        raise RuntimeError(
            "raw/normalized ordered partitions differ"
        )

    return {
        "reductions": raw_reductions,
        "ordered_partition_matches_normalized": True,
        "raw_unordered_vs_normalized_unordered": (
            compare_partitions(
                normalized_reductions[
                    "unordered"
                ][
                    "summary"
                ],
                raw_reductions[
                    "unordered"
                ][
                    "summary"
                ],
            )
        ),
    }


def _analyze_temporal_channel(
    *,
    channel: str,
    codes: tuple[str, ...],
    geometries: tuple[object, ...],
) -> dict[str, object]:
    substrate, coupled = (
        _channel_parameters(
            channel
        )
    )

    trajectories = []
    step_zero = []

    translation_ok = True
    reflection_ok = True

    for index, geometry in enumerate(
        geometries,
        start=1,
    ):
        trajectory = (
            t1.normalized_trajectory(
                substrate,
                geometry,
                coupled=coupled,
            )
        )

        trajectories.append(
            trajectory
        )

        step_zero.append(
            t1.step_zero_snapshot(
                substrate,
                geometry,
                coupled=coupled,
                normalized=True,
            )
        )

        translated = t1.translate_geometry(
            geometry
        )

        translation_ok = (
            translation_ok
            and t1.normalized_trajectory(
                substrate,
                translated,
                coupled=coupled,
            )
            == trajectory
        )

        reflection_ok = (
            reflection_ok
            and _reflection_audit(
                channel,
                geometry,
                trajectory,
            )
        )

        if (
            index % 10 == 0
            or index == len(geometries)
        ):
            print(
                f"[{channel}] "
                f"{index}/{len(geometries)}",
                file=sys.stderr,
                flush=True,
            )

    frozen_trajectories = tuple(
        trajectories
    )

    frozen_step_zero = tuple(
        step_zero
    )

    reductions: dict[
        str,
        dict[str, object],
    ] = {}

    for reduction in t1.REDUCTIONS:
        signatures = _reduction_signatures(
            frozen_trajectories,
            reduction,
        )

        reductions[
            reduction
        ] = analyze_channel(
            codes=codes,
            signatures=signatures,
        )

    comparisons = {
        "unordered_to_ordered": (
            compare_partitions(
                reductions[
                    "unordered"
                ][
                    "summary"
                ],
                reductions[
                    "ordered"
                ][
                    "summary"
                ],
            )
        ),
        "endpoints_to_ordered": (
            compare_partitions(
                reductions[
                    "endpoints"
                ][
                    "summary"
                ],
                reductions[
                    "ordered"
                ][
                    "summary"
                ],
            )
        ),
        "terminal_to_endpoints": (
            compare_partitions(
                reductions[
                    "terminal"
                ][
                    "summary"
                ],
                reductions[
                    "endpoints"
                ][
                    "summary"
                ],
            )
        ),
        "terminal_to_ordered": (
            compare_partitions(
                reductions[
                    "terminal"
                ][
                    "summary"
                ],
                reductions[
                    "ordered"
                ][
                    "summary"
                ],
            )
        ),
    }

    for label, comparison in (
        comparisons.items()
    ):
        if int(
            comparison[
                "introduced_pair_count"
            ]
        ) != 0:
            raise RuntimeError(
                "deterministic temporal projection "
                f"introduced collisions: {label}"
            )

    prefixes = []

    for length, step in enumerate(
        t1.SAMPLE_STEPS,
        start=1,
    ):
        ordered_signatures = (
            _prefix_signatures(
                frozen_trajectories,
                unordered=False,
                length=length,
            )
        )

        unordered_signatures = (
            _prefix_signatures(
                frozen_trajectories,
                unordered=True,
                length=length,
            )
        )

        ordered_analysis = analyze_channel(
            codes=codes,
            signatures=ordered_signatures,
        )

        unordered_analysis = analyze_channel(
            codes=codes,
            signatures=unordered_signatures,
        )

        comparison = compare_partitions(
            unordered_analysis[
                "summary"
            ],
            ordered_analysis[
                "summary"
            ],
        )

        if int(
            comparison[
                "introduced_pair_count"
            ]
        ) != 0:
            raise RuntimeError(
                "ordered prefix introduced collisions"
            )

        prefixes.append({
            "length": length,
            "through_step": step,
            "ordered": ordered_analysis,
            "unordered": unordered_analysis,
            "unordered_to_ordered": comparison,
        })

    raw_audit = _raw_audit(
        codes=codes,
        substrate=substrate,
        coupled=coupled,
        geometries=geometries,
        normalized_reductions=reductions,
    )

    return {
        "step_zero": analyze_channel(
            codes=codes,
            signatures=frozen_step_zero,
        ),
        "reductions": reductions,
        "comparisons": comparisons,
        "prefixes": prefixes,
        "diagnostics": _pair_diagnostics(
            codes,
            frozen_step_zero,
            frozen_trajectories,
        ),
        "translation_audit_passed": (
            translation_ok
        ),
        "reflection_or_transport_audit_passed": (
            reflection_ok
        ),
        "reflection_semantics": (
            "transported-frozen-probe"
            if channel in (
                "B0",
                "D1-null",
                "D1-coupled",
            )
            else "intrinsic-equivariant"
        ),
        "raw_numerator_audit": (
            raw_audit
        ),
    }


def _d1_matched_audit(
    geometries: tuple[object, ...],
) -> bool:
    for geometry in geometries:
        null_graph = (
            t1.d1.build_distance2_graph(
                geometry,
                bridge_weight=0,
            )
        )

        coupled_graph = (
            t1.d1.build_distance2_graph(
                geometry,
                bridge_weight=t1.d1.BRIDGE_WEIGHT,
            )
        )

        if (
            null_graph.cells
            != coupled_graph.cells
        ):
            return False

        if (
            t1.d1.original_component_probe(
                null_graph
            )
            != t1.d1.original_component_probe(
                coupled_graph
            )
        ):
            return False

    return True


def _d1_comparisons(
    null_analysis: dict[str, object],
    coupled_analysis: dict[str, object],
) -> dict[str, object]:
    reductions = {}

    for reduction in t1.REDUCTIONS:
        reductions[
            reduction
        ] = compare_partitions(
            null_analysis[
                "reductions"
            ][
                reduction
            ][
                "summary"
            ],
            coupled_analysis[
                "reductions"
            ][
                reduction
            ][
                "summary"
            ],
        )

    prefixes = []

    for null_prefix, coupled_prefix in zip(
        null_analysis[
            "prefixes"
        ],
        coupled_analysis[
            "prefixes"
        ],
    ):
        _assert_equal(
            null_prefix[
                "length"
            ],
            coupled_prefix[
                "length"
            ],
            message="D1 prefix lengths differ",
        )

        prefixes.append({
            "length": null_prefix[
                "length"
            ],
            "through_step": null_prefix[
                "through_step"
            ],
            "ordered_null_to_coupled": (
                compare_partitions(
                    null_prefix[
                        "ordered"
                    ][
                        "summary"
                    ],
                    coupled_prefix[
                        "ordered"
                    ][
                        "summary"
                    ],
                )
            ),
            "unordered_null_to_coupled": (
                compare_partitions(
                    null_prefix[
                        "unordered"
                    ][
                        "summary"
                    ],
                    coupled_prefix[
                        "unordered"
                    ][
                        "summary"
                    ],
                )
            ),
        })

    return {
        "reductions": reductions,
        "prefixes": prefixes,
    }


def analyze_corpus(
    corpus_name: str,
) -> dict[str, object]:
    corpus = tuple(
        _select_corpus(
            corpus_name
        )
    )

    codes = tuple(
        width4.shape_code(
            shape
        )
        for shape in corpus
    )

    geometries = tuple(
        width4.encode_experimental_geometry(
            shape
        )
        for shape in corpus
    )

    channel_results: dict[
        str,
        dict[str, object],
    ] = {}

    for channel in CHANNELS:
        print(
            f"[{corpus_name}] T1 {channel}: "
            f"computing {len(geometries)} forms",
            file=sys.stderr,
            flush=True,
        )

        channel_results[
            channel
        ] = _analyze_temporal_channel(
            channel=channel,
            codes=codes,
            geometries=geometries,
        )

        current = channel_results[
            channel
        ]

        if not current[
            "translation_audit_passed"
        ]:
            raise RuntimeError(
                f"translation audit failed: {channel}"
            )

        if not current[
            "reflection_or_transport_audit_passed"
        ]:
            raise RuntimeError(
                f"reflection/transport audit failed: {channel}"
            )

    matched_d1 = _d1_matched_audit(
        geometries
    )

    if not matched_d1:
        raise RuntimeError(
            "D1 null/coupled matched-state audit failed"
        )

    d1_comparison = _d1_comparisons(
        channel_results[
            "D1-null"
        ],
        channel_results[
            "D1-coupled"
        ],
    )

    return {
        "protocol_id": PROTOCOL_ID,
        "t1_protocol_id": t1.PROTOCOL_ID,
        "corpus": corpus_name,
        "form_count": len(
            corpus
        ),
        "sample_steps": list(
            t1.SAMPLE_STEPS
        ),
        "translation_vector": list(
            t1.TRANSLATION_VECTOR
        ),
        "normalization": {
            "B0": {
                "kind": "exact-euler",
                "denominator": (
                    t1.b0.EULER_DENOMINATOR
                ),
            },
            "D1": {
                "kind": "exact-euler",
                "denominator": (
                    t1.d1.EULER_DENOMINATOR
                ),
            },
            "F1": {
                "kind": "exact-rational-frozen-state",
                "denominator": None,
            },
            "L1": {
                "kind": "exact-euler",
                "denominator": (
                    t1.l1.EULER_DENOMINATOR
                ),
            },
        },
        "source_boundary": {
            "shape_code_is_metadata_only": True,
            "p1_input": False,
            "i1_input": False,
            "s1_input": False,
            "s2_input": False,
            "h1_input": False,
            "o1_input": False,
            "gate4_input": False,
        },
        "d1_matched_initial_state_audit_passed": (
            matched_d1
        ),
        "channels": channel_results,
        "d1_null_to_coupled": (
            d1_comparison
        ),
        "sources": {
            "t1_protocol_sha256": (
                _sha256_file(
                    T1_PROTOCOL_PATH
                )
            ),
            "t1_implementation_sha256": (
                _sha256_file(
                    T1_TOOL_PATH
                )
            ),
            "width4_source_sha256": (
                _sha256_file(
                    WIDTH4_TOOL_PATH
                )
            ),
        },
    }


def build_evidence(
    corpus_name: str,
) -> dict[str, object]:
    return {
        "evidence_protocol_id": (
            PROTOCOL_ID
        ),
        "analysis": analyze_corpus(
            corpus_name
        ),
    }


def write_evidence(
    output: Path,
    evidence: dict[str, object],
) -> str:
    payload = (
        _canonical_json_bytes(
            evidence
        )
        + b"\n"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_bytes(
        payload
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic PETRA VISION "
            "Gate 3 T1 evidence."
        )
    )

    parser.add_argument(
        "--corpus",
        required=True,
        choices=CORPORA,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
    )

    return parser


def main() -> int:
    args = _parser().parse_args()

    evidence = build_evidence(
        args.corpus
    )

    digest = write_evidence(
        args.output,
        evidence,
    )

    print(
        f"Evidence: {args.output}"
    )

    print(
        f"SHA256:   {digest}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
