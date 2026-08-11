#!/usr/bin/env python3
"""Deterministic evidence runner for PETRA VISION Gate 3 G3-I1."""

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


I1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_i1.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)

I1_PROTOCOL_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "research"
    / "petra-vision"
    / "EXPLICIT_SPECTRAL_CONTROLS_I1_PROTOCOL.md"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-i1-evidence-v0"
)

EXPECTED_I1_PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-i1-v0"
)

EXPECTED_COLLISION = tuple(sorted((
    "G(G(G(T)),G(T,T))",
    "G(G(T,T),G(G(T)))",
)))

CORPORA = (
    "phase1",
    "heldout",
    "extended",
)

SELECTED_MODES = (
    "minimum",
    "reflected-minimum",
)

TRANSPORTED_MODES = {
    "minimum": "reflected-minimum",
    "reflected-minimum": "minimum",
}


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


i1 = _load_module(
    I1_TOOL_PATH,
    "_petra_vision_gate3_i1_evidence_tool",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate3_i1_evidence_width4",
)


if i1.PROTOCOL_ID != EXPECTED_I1_PROTOCOL_ID:
    raise RuntimeError(
        "evidence runner requires frozen G3-I1 protocol"
    )

if i1.SUBSTRATES != (
    "B0",
    "D1",
):
    raise RuntimeError(
        "evidence runner requires frozen B0/D1 I1 scope"
    )

if i1.OBSERVATION_MODES != (
    "minimum",
    "reflected-minimum",
    "all-vertices",
):
    raise RuntimeError(
        "evidence runner requires frozen I1 observation family"
    )

if i1.TRANSLATION_VECTOR != (
    17,
    11,
):
    raise RuntimeError(
        "evidence runner requires frozen I1 translation vector"
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

    left, right = (
        EXPECTED_COLLISION
    )

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


def _analyze_channel(
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


def _source_index_under_reflection(
    substrate: str,
    geometry,
    source_index: int,
) -> tuple[
    object,
    int,
]:
    reflected = i1.horizontal_reflection(
        geometry
    )

    original_cells = i1._substrate_cells(
        substrate,
        geometry,
    )

    reflected_cells = i1._substrate_cells(
        substrate,
        reflected,
    )

    if (
        source_index < 0
        or source_index >= len(
            original_cells
        )
    ):
        raise ValueError(
            "source index outside geometry"
        )

    reflected_index = {
        cell: index
        for index, cell in enumerate(
            reflected_cells
        )
    }

    reflected_cell = i1._reflection_cell(
        geometry,
        original_cells[
            source_index
        ],
    )

    return (
        reflected,
        reflected_index[
            reflected_cell
        ],
    )


def _elementary_response_bijection_audit(
    substrate: str,
    geometry,
    *,
    coupled: bool | None,
    expected_aggregate: object,
) -> bool:
    cells = i1._substrate_cells(
        substrate,
        geometry,
    )

    original_responses = []
    reflected_responses = []

    for source_index in range(
        len(cells)
    ):
        impulse = i1.unit_impulse(
            len(cells),
            source_index,
        )

        reflected, target_index = (
            _source_index_under_reflection(
                substrate,
                geometry,
                source_index,
            )
        )

        reflected_cells = (
            i1._substrate_cells(
                substrate,
                reflected,
            )
        )

        reflected_impulse = (
            i1.unit_impulse(
                len(reflected_cells),
                target_index,
            )
        )

        kwargs = {}

        if substrate == "D1":
            if type(coupled) is not bool:
                raise TypeError(
                    "D1 bijection audit requires coupled bool"
                )

            kwargs[
                "coupled"
            ] = coupled

        original = i1.elementary_response(
            substrate,
            geometry,
            impulse,
            **kwargs,
        )

        reflected_response = (
            i1.elementary_response(
                substrate,
                reflected,
                reflected_impulse,
                **kwargs,
            )
        )

        if original != reflected_response:
            return False

        original_responses.append(
            original
        )

        reflected_responses.append(
            reflected_response
        )

    original_aggregate = tuple(sorted(
        original_responses
    ))

    reflected_aggregate = tuple(sorted(
        reflected_responses
    ))

    return (
        original_aggregate
        == reflected_aggregate
        == expected_aggregate
    )


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

    raw_step_zero: dict[
        str,
        list[object],
    ] = {
        mode: []
        for mode in i1.OBSERVATION_MODES
    }

    raw_b0: dict[
        str,
        list[object],
    ] = {
        mode: []
        for mode in i1.OBSERVATION_MODES
    }

    raw_d1_null: dict[
        str,
        list[object],
    ] = {
        mode: []
        for mode in i1.OBSERVATION_MODES
    }

    raw_d1_coupled: dict[
        str,
        list[object],
    ] = {
        mode: []
        for mode in i1.OBSERVATION_MODES
    }

    audit_data: dict[
        str,
        dict[str, object],
    ] = {}

    for mode in i1.OBSERVATION_MODES:
        print(
            f"[{corpus_name}] I1 {mode}: "
            f"computing {len(geometries)} forms",
            file=sys.stderr,
            flush=True,
        )

        b0_translation = True
        b0_reflection = True

        d1_null_translation = True
        d1_null_reflection = True

        d1_coupled_translation = True
        d1_coupled_reflection = True

        matched_impulse_identity = True
        mass_one_invariant = True

        b0_aggregation = True
        d1_null_aggregation = True
        d1_coupled_aggregation = True

        family_sizes = []

        for index, geometry in enumerate(
            geometries,
            start=1,
        ):
            b0_cells = i1._substrate_cells(
                "B0",
                geometry,
            )

            d1_cells = i1._substrate_cells(
                "D1",
                geometry,
            )

            _assert_equal(
                b0_cells,
                d1_cells,
                message=(
                    "B0/D1 occupied vertex domains differ"
                ),
            )

            family_sizes.append(
                len(b0_cells)
            )

            step_zero = (
                i1.observation_step_zero_signature(
                    "B0",
                    geometry,
                    mode,
                )
            )

            d1_step_zero = (
                i1.observation_step_zero_signature(
                    "D1",
                    geometry,
                    mode,
                )
            )

            _assert_equal(
                step_zero,
                d1_step_zero,
                message=(
                    "B0/D1 step-zero signatures differ"
                ),
            )

            raw_step_zero[
                mode
            ].append(
                step_zero
            )

            if mode in SELECTED_MODES:
                b0_impulse = i1.selected_impulse(
                    "B0",
                    geometry,
                    mode,
                )

                d1_impulse = i1.selected_impulse(
                    "D1",
                    geometry,
                    mode,
                )

                matched_impulse_identity = (
                    matched_impulse_identity
                    and b0_impulse == d1_impulse
                )

                mass_one_invariant = (
                    mass_one_invariant
                    and i1.impulse_mass(
                        b0_impulse
                    ) == 1
                    and i1.impulse_mass(
                        d1_impulse
                    ) == 1
                )
            else:
                family = (
                    i1.elementary_impulse_family(
                        len(b0_cells)
                    )
                )

                mass_one_invariant = (
                    mass_one_invariant
                    and all(
                        i1.impulse_mass(
                            impulse
                        ) == 1
                        for impulse in family
                    )
                )

                matched_impulse_identity = (
                    matched_impulse_identity
                    and family
                    == i1.elementary_impulse_family(
                        len(d1_cells)
                    )
                )

            current_b0 = (
                i1.observation_signature(
                    "B0",
                    geometry,
                    mode,
                )
            )

            current_null = (
                i1.observation_signature(
                    "D1",
                    geometry,
                    mode,
                    coupled=False,
                )
            )

            current_coupled = (
                i1.observation_signature(
                    "D1",
                    geometry,
                    mode,
                    coupled=True,
                )
            )

            raw_b0[
                mode
            ].append(
                current_b0
            )

            raw_d1_null[
                mode
            ].append(
                current_null
            )

            raw_d1_coupled[
                mode
            ].append(
                current_coupled
            )

            translated = i1.translate_geometry(
                geometry
            )

            translated_zero_b0 = (
                i1.observation_step_zero_signature(
                    "B0",
                    translated,
                    mode,
                )
            )

            translated_zero_d1 = (
                i1.observation_step_zero_signature(
                    "D1",
                    translated,
                    mode,
                )
            )

            _assert_equal(
                step_zero,
                translated_zero_b0,
                message=(
                    f"B0 step-zero changed under translation: {mode}"
                ),
            )

            _assert_equal(
                step_zero,
                translated_zero_d1,
                message=(
                    f"D1 step-zero changed under translation: {mode}"
                ),
            )

            translated_b0 = (
                i1.observation_signature(
                    "B0",
                    translated,
                    mode,
                )
            )

            translated_null = (
                i1.observation_signature(
                    "D1",
                    translated,
                    mode,
                    coupled=False,
                )
            )

            translated_coupled = (
                i1.observation_signature(
                    "D1",
                    translated,
                    mode,
                    coupled=True,
                )
            )

            b0_translation = (
                b0_translation
                and translated_b0
                == current_b0
            )

            d1_null_translation = (
                d1_null_translation
                and translated_null
                == current_null
            )

            d1_coupled_translation = (
                d1_coupled_translation
                and translated_coupled
                == current_coupled
            )

            reflected = i1.horizontal_reflection(
                geometry
            )

            if mode in SELECTED_MODES:
                reflected_mode = (
                    TRANSPORTED_MODES[
                        mode
                    ]
                )

                reflected_b0 = (
                    i1.observation_signature(
                        "B0",
                        reflected,
                        reflected_mode,
                    )
                )

                reflected_null = (
                    i1.observation_signature(
                        "D1",
                        reflected,
                        reflected_mode,
                        coupled=False,
                    )
                )

                reflected_coupled = (
                    i1.observation_signature(
                        "D1",
                        reflected,
                        reflected_mode,
                        coupled=True,
                    )
                )

                b0_reflection = (
                    b0_reflection
                    and reflected_b0
                    == current_b0
                )

                d1_null_reflection = (
                    d1_null_reflection
                    and reflected_null
                    == current_null
                )

                d1_coupled_reflection = (
                    d1_coupled_reflection
                    and reflected_coupled
                    == current_coupled
                )
            else:
                reflected_b0 = (
                    i1.observation_signature(
                        "B0",
                        reflected,
                        "all-vertices",
                    )
                )

                reflected_null = (
                    i1.observation_signature(
                        "D1",
                        reflected,
                        "all-vertices",
                        coupled=False,
                    )
                )

                reflected_coupled = (
                    i1.observation_signature(
                        "D1",
                        reflected,
                        "all-vertices",
                        coupled=True,
                    )
                )

                b0_reflection = (
                    b0_reflection
                    and reflected_b0
                    == current_b0
                )

                d1_null_reflection = (
                    d1_null_reflection
                    and reflected_null
                    == current_null
                )

                d1_coupled_reflection = (
                    d1_coupled_reflection
                    and reflected_coupled
                    == current_coupled
                )

                b0_aggregation = (
                    b0_aggregation
                    and _elementary_response_bijection_audit(
                        "B0",
                        geometry,
                        coupled=None,
                        expected_aggregate=current_b0,
                    )
                )

                d1_null_aggregation = (
                    d1_null_aggregation
                    and _elementary_response_bijection_audit(
                        "D1",
                        geometry,
                        coupled=False,
                        expected_aggregate=current_null,
                    )
                )

                d1_coupled_aggregation = (
                    d1_coupled_aggregation
                    and _elementary_response_bijection_audit(
                        "D1",
                        geometry,
                        coupled=True,
                        expected_aggregate=current_coupled,
                    )
                )

            if (
                index % 10 == 0
                or index == len(
                    geometries
                )
            ):
                print(
                    f"[{corpus_name}] I1 {mode}: "
                    f"{index}/{len(geometries)}",
                    file=sys.stderr,
                    flush=True,
                )

        if not mass_one_invariant:
            raise RuntimeError(
                f"I1 mass-one invariant failed: {mode}"
            )

        if not matched_impulse_identity:
            raise RuntimeError(
                f"I1 matched B0/D1 impulse identity failed: {mode}"
            )

        if not b0_translation:
            raise RuntimeError(
                f"I1 B0 translation audit failed: {mode}"
            )

        if not d1_null_translation:
            raise RuntimeError(
                f"I1 D1-null translation audit failed: {mode}"
            )

        if not d1_coupled_translation:
            raise RuntimeError(
                f"I1 D1-coupled translation audit failed: {mode}"
            )

        if not b0_reflection:
            raise RuntimeError(
                f"I1 B0 reflection audit failed: {mode}"
            )

        if not d1_null_reflection:
            raise RuntimeError(
                f"I1 D1-null reflection audit failed: {mode}"
            )

        if not d1_coupled_reflection:
            raise RuntimeError(
                f"I1 D1-coupled reflection audit failed: {mode}"
            )

        if mode == "all-vertices":
            if not b0_aggregation:
                raise RuntimeError(
                    "I1 B0 elementary aggregation/bijection audit failed"
                )

            if not d1_null_aggregation:
                raise RuntimeError(
                    "I1 D1-null elementary aggregation/bijection audit failed"
                )

            if not d1_coupled_aggregation:
                raise RuntimeError(
                    "I1 D1-coupled elementary aggregation/bijection audit failed"
                )

        audit_data[
            mode
        ] = {
            "mass_one_invariant": (
                mass_one_invariant
            ),
            "matched_impulse_identity": (
                matched_impulse_identity
            ),
            "family_size_distribution": {
                str(size): count
                for size, count in sorted(
                    Counter(
                        family_sizes
                    ).items()
                )
            },
            "b0": {
                "translation_audit_passed": (
                    b0_translation
                ),
                "reflection_audit_passed": (
                    b0_reflection
                ),
                "elementary_aggregation_bijection_audit_passed": (
                    b0_aggregation
                    if mode == "all-vertices"
                    else None
                ),
            },
            "d1_null": {
                "translation_audit_passed": (
                    d1_null_translation
                ),
                "reflection_audit_passed": (
                    d1_null_reflection
                ),
                "elementary_aggregation_bijection_audit_passed": (
                    d1_null_aggregation
                    if mode == "all-vertices"
                    else None
                ),
            },
            "d1_coupled": {
                "translation_audit_passed": (
                    d1_coupled_translation
                ),
                "reflection_audit_passed": (
                    d1_coupled_reflection
                ),
                "elementary_aggregation_bijection_audit_passed": (
                    d1_coupled_aggregation
                    if mode == "all-vertices"
                    else None
                ),
            },
        }

    step_zero = {}
    b0_modes = {}
    d1_modes = {}

    for mode in i1.OBSERVATION_MODES:
        step_zero_signatures = tuple(
            raw_step_zero[
                mode
            ]
        )

        b0_signatures = tuple(
            raw_b0[
                mode
            ]
        )

        null_signatures = tuple(
            raw_d1_null[
                mode
            ]
        )

        coupled_signatures = tuple(
            raw_d1_coupled[
                mode
            ]
        )

        step_zero_channel = (
            _analyze_channel(
                codes=codes,
                signatures=step_zero_signatures,
            )
        )

        b0_channel = (
            _analyze_channel(
                codes=codes,
                signatures=b0_signatures,
            )
        )

        null_channel = (
            _analyze_channel(
                codes=codes,
                signatures=null_signatures,
            )
        )

        coupled_channel = (
            _analyze_channel(
                codes=codes,
                signatures=coupled_signatures,
            )
        )

        step_zero[
            mode
        ] = step_zero_channel

        b0_modes[
            mode
        ] = {
            "dynamic": b0_channel,
            "translation_audit_passed": (
                audit_data[
                    mode
                ][
                    "b0"
                ][
                    "translation_audit_passed"
                ]
            ),
            "reflection_audit_passed": (
                audit_data[
                    mode
                ][
                    "b0"
                ][
                    "reflection_audit_passed"
                ]
            ),
            "elementary_aggregation_bijection_audit_passed": (
                audit_data[
                    mode
                ][
                    "b0"
                ][
                    "elementary_aggregation_bijection_audit_passed"
                ]
            ),
        }

        d1_modes[
            mode
        ] = {
            "mass_one_invariant": (
                audit_data[
                    mode
                ][
                    "mass_one_invariant"
                ]
            ),
            "matched_impulse_identity": (
                audit_data[
                    mode
                ][
                    "matched_impulse_identity"
                ]
            ),
            "family_size_distribution": (
                audit_data[
                    mode
                ][
                    "family_size_distribution"
                ]
            ),
            "null": {
                "dynamic": null_channel,
                "translation_audit_passed": (
                    audit_data[
                        mode
                    ][
                        "d1_null"
                    ][
                        "translation_audit_passed"
                    ]
                ),
                "reflection_audit_passed": (
                    audit_data[
                        mode
                    ][
                        "d1_null"
                    ][
                        "reflection_audit_passed"
                    ]
                ),
                "elementary_aggregation_bijection_audit_passed": (
                    audit_data[
                        mode
                    ][
                        "d1_null"
                    ][
                        "elementary_aggregation_bijection_audit_passed"
                    ]
                ),
            },
            "coupled": {
                "dynamic": coupled_channel,
                "translation_audit_passed": (
                    audit_data[
                        mode
                    ][
                        "d1_coupled"
                    ][
                        "translation_audit_passed"
                    ]
                ),
                "reflection_audit_passed": (
                    audit_data[
                        mode
                    ][
                        "d1_coupled"
                    ][
                        "reflection_audit_passed"
                    ]
                ),
                "elementary_aggregation_bijection_audit_passed": (
                    audit_data[
                        mode
                    ][
                        "d1_coupled"
                    ][
                        "elementary_aggregation_bijection_audit_passed"
                    ]
                ),
            },
            "null_to_coupled": (
                compare_partitions(
                    null_channel[
                        "summary"
                    ],
                    coupled_channel[
                        "summary"
                    ],
                )
            ),
        }

    all_vertices_b0 = (
        b0_modes[
            "all-vertices"
        ][
            "dynamic"
        ][
            "expected_collision"
        ]
    )

    all_vertices_null = (
        d1_modes[
            "all-vertices"
        ][
            "null"
        ][
            "dynamic"
        ][
            "expected_collision"
        ]
    )

    all_vertices_coupled = (
        d1_modes[
            "all-vertices"
        ][
            "coupled"
        ][
            "dynamic"
        ][
            "expected_collision"
        ]
    )

    for label, status in (
        (
            "B0",
            all_vertices_b0,
        ),
        (
            "D1 null",
            all_vertices_null,
        ),
        (
            "D1 coupled",
            all_vertices_coupled,
        ),
    ):
        if (
            status[
                "present"
            ]
            and not status[
                "collides"
            ]
        ):
            raise RuntimeError(
                "intrinsic I1-all-vertices separated "
                f"#23/#41 under {label}"
            )

    comparisons = {
        "B0": {},
        "D1_null": {},
        "D1_coupled": {},
    }

    for selected_mode in SELECTED_MODES:
        comparisons[
            "B0"
        ][
            f"{selected_mode}_to_all_vertices"
        ] = compare_partitions(
            b0_modes[
                selected_mode
            ][
                "dynamic"
            ][
                "summary"
            ],
            b0_modes[
                "all-vertices"
            ][
                "dynamic"
            ][
                "summary"
            ],
        )

        comparisons[
            "D1_null"
        ][
            f"{selected_mode}_to_all_vertices"
        ] = compare_partitions(
            d1_modes[
                selected_mode
            ][
                "null"
            ][
                "dynamic"
            ][
                "summary"
            ],
            d1_modes[
                "all-vertices"
            ][
                "null"
            ][
                "dynamic"
            ][
                "summary"
            ],
        )

        comparisons[
            "D1_coupled"
        ][
            f"{selected_mode}_to_all_vertices"
        ] = compare_partitions(
            d1_modes[
                selected_mode
            ][
                "coupled"
            ][
                "dynamic"
            ][
                "summary"
            ],
            d1_modes[
                "all-vertices"
            ][
                "coupled"
            ][
                "dynamic"
            ][
                "summary"
            ],
        )

    return {
        "corpus": corpus_name,
        "form_count": len(
            corpus
        ),
        "step_zero": step_zero,
        "substrates": {
            "B0": {
                "modes": b0_modes,
            },
            "D1": {
                "modes": d1_modes,
            },
        },
        "selected_to_intrinsic_comparisons": (
            comparisons
        ),
    }


def evidence_document(
    corpus_name: str,
) -> dict[str, object]:
    if corpus_name not in CORPORA:
        raise ValueError(
            f"unsupported corpus: {corpus_name}"
        )

    analysis = analyze_corpus(
        corpus_name
    )

    return {
        "protocol_id": PROTOCOL_ID,
        "i1_protocol_id": i1.PROTOCOL_ID,
        "corpus": corpus_name,
        "form_count": analysis[
            "form_count"
        ],
        "frozen_parameters": {
            "substrates": list(
                i1.SUBSTRATES
            ),
            "observation_modes": list(
                i1.OBSERVATION_MODES
            ),
            "translation_vector": list(
                i1.TRANSLATION_VECTOR
            ),
            "b0_denominator": (
                i1.b0.EULER_DENOMINATOR
            ),
            "d1_denominator": (
                i1.d1.EULER_DENOMINATOR
            ),
            "sample_steps": list(
                i1.b0.SAMPLE_STEPS
            ),
            "elementary_impulse_mass": 1,
            "all_vertices_aggregation": (
                "unordered-multiplicity-preserving-"
                "multiset-of-elementary-response-signatures"
            ),
        },
        "source_sha256": {
            "i1_protocol": _sha256_file(
                I1_PROTOCOL_PATH
            ),
            "i1_tool": _sha256_file(
                I1_TOOL_PATH
            ),
            "b0_tool": _sha256_file(
                i1.B0_TOOL_PATH
            ),
            "d1_tool": _sha256_file(
                i1.D1_TOOL_PATH
            ),
            "width4_corpus_tool": _sha256_file(
                WIDTH4_TOOL_PATH
            ),
            "evidence_runner": _sha256_file(
                Path(__file__).resolve()
            ),
        },
        "analysis": analysis,
    }


def write_evidence(
    path: Path,
    document: dict[str, object],
) -> None:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        payload + "\n",
        encoding="utf-8",
    )


def _parse_args(
    argv: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate one frozen G3-I1 corpus evidence artifact"
        )
    )

    parser.add_argument(
        "--corpus",
        choices=CORPORA,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    return parser.parse_args(
        argv
    )


def main(
    argv: list[str] | None = None,
) -> int:
    args = _parse_args(
        argv
    )

    document = evidence_document(
        args.corpus
    )

    write_evidence(
        args.output,
        document,
    )

    digest = _sha256_file(
        args.output
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
