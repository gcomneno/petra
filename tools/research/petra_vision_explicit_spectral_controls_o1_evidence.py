#!/usr/bin/env python3
"""Deterministic evidence runner for PETRA VISION Gate 3 G3-O1."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
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


O1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_o1.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)

O1_PROTOCOL_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "research"
    / "petra-vision"
    / "EXPLICIT_SPECTRAL_CONTROLS_O1_PROTOCOL.md"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-o1-evidence-v0"
)

EXPECTED_O1_PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-o1-v0"
)

EXPECTED_PROTOCOL_SHA256 = "80984e11e2764a435df0bf0857ff9a18c5528393d8c1033677ebc5b396ae2e91"
EXPECTED_TOOL_SHA256 = "4dbb3b27de69e04287427b477e54ea2046476a49919151263c53c3ea67fd0bf1"
EXPECTED_WIDTH4_SHA256 = "348d2dfaf6c26f71cd20af75ad7e298b58d26d0e2eab94279bd860492aa35707"

CORPORA = (
    "phase1",
    "heldout",
    "extended",
)

CHANNELS = (
    "B0",
    "D1-null",
    "D1-coupled",
    "F1-null",
    "F1-coupled",
    "L1-null",
    "L1-coupled",
)

OBSERVATIONS = (
    "coordinate-free-step0",
    "oriented-step0",
    "coordinate-free-dynamic",
    "oriented-dynamic",
)

COMPARISONS = (
    (
        "coordinate-free-step0_to_oriented-step0",
        "coordinate-free-step0",
        "oriented-step0",
    ),
    (
        "coordinate-free-dynamic_to_oriented-dynamic",
        "coordinate-free-dynamic",
        "oriented-dynamic",
    ),
    (
        "oriented-step0_to_oriented-dynamic",
        "oriented-step0",
        "oriented-dynamic",
    ),
    (
        "coordinate-free-step0_to_coordinate-free-dynamic",
        "coordinate-free-step0",
        "coordinate-free-dynamic",
    ),
)

COUPLING_FAMILIES = {
    "D1": (
        "D1-null",
        "D1-coupled",
    ),
    "F1": (
        "F1-null",
        "F1-coupled",
    ),
    "L1": (
        "L1-null",
        "L1-coupled",
    ),
}

EXPECTED_COLLISION = tuple(sorted((
    "G(G(G(T)),G(T,T))",
    "G(G(T,T),G(G(T)))",
)))


def _load_module(
    path: Path,
    name: str,
) -> ModuleType:
    existing = sys.modules.get(name)

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
    spec.loader.exec_module(module)

    return module


def _sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


if _sha256_file(
    O1_PROTOCOL_PATH
) != EXPECTED_PROTOCOL_SHA256:
    raise RuntimeError(
        "G3-O1 protocol digest changed after runner freeze"
    )

if _sha256_file(
    O1_TOOL_PATH
) != EXPECTED_TOOL_SHA256:
    raise RuntimeError(
        "G3-O1 implementation digest changed after runner freeze"
    )

if _sha256_file(
    WIDTH4_TOOL_PATH
) != EXPECTED_WIDTH4_SHA256:
    raise RuntimeError(
        "frozen width-4 corpus source digest changed"
    )


o1 = _load_module(
    O1_TOOL_PATH,
    "_petra_vision_gate3_o1_evidence_tool",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate3_o1_evidence_width4",
)


if o1.PROTOCOL_ID != EXPECTED_O1_PROTOCOL_ID:
    raise RuntimeError(
        "evidence runner requires frozen G3-O1 protocol"
    )

if o1.CHANNELS != CHANNELS:
    raise RuntimeError(
        "evidence runner requires frozen O1 channels"
    )

if o1.OBSERVATIONS != OBSERVATIONS:
    raise RuntimeError(
        "evidence runner requires frozen O1 observations"
    )

if o1.SAMPLE_STEPS != (
    1,
    2,
    4,
    8,
    16,
    32,
):
    raise RuntimeError(
        "evidence runner requires frozen O1 sample schedule"
    )

if o1.TRANSLATION_VECTOR != (
    17,
    11,
):
    raise RuntimeError(
        "evidence runner requires frozen O1 translation vector"
    )


def _jsonable(
    value: object,
) -> object:
    if isinstance(value, Fraction):
        return {
            "fraction": [
                value.numerator,
                value.denominator,
            ]
        }

    if isinstance(value, tuple):
        return [
            _jsonable(item)
            for item in value
        ]

    if isinstance(value, list):
        return [
            _jsonable(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _jsonable(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            str,
            int,
            bool,
        ),
    ) or value is None:
        return value

    raise TypeError(
        "unsupported canonical JSON value: "
        f"{type(value)!r}"
    )


def _canonical_json_bytes(
    value: object,
) -> bytes:
    return json.dumps(
        _jsonable(value),
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

    pairs = _collision_pairs_from_groups(
        groups
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
            signatures[index[left]]
            == signatures[index[right]]
        ),
    }


def analyze_observation(
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


def _raw_normalized_audit(
    *,
    codes: tuple[str, ...],
    geometries: tuple[object, ...],
    channel: str,
    raw_observations: dict[
        str,
        dict[str, object],
    ],
) -> dict[str, object] | None:
    family = (
        channel
        if channel == "B0"
        else channel.split("-", 1)[0]
    )

    if family == "F1":
        return None

    normalized_oriented = tuple(
        o1.normalized_dynamic_signature(
            geometry,
            channel,
            oriented=True,
        )
        for geometry in geometries
    )

    normalized_coordinate_free = tuple(
        o1.normalized_dynamic_signature(
            geometry,
            channel,
            oriented=False,
        )
        for geometry in geometries
    )

    normalized = {
        "coordinate-free-dynamic": (
            analyze_observation(
                codes=codes,
                signatures=(
                    normalized_coordinate_free
                ),
            )
        ),
        "oriented-dynamic": (
            analyze_observation(
                codes=codes,
                signatures=(
                    normalized_oriented
                ),
            )
        ),
    }

    comparisons = {}

    for observation in (
        "coordinate-free-dynamic",
        "oriented-dynamic",
    ):
        raw_summary = raw_observations[
            observation
        ][
            "summary"
        ]

        normalized_summary = normalized[
            observation
        ][
            "summary"
        ]

        forward = compare_partitions(
            raw_summary,
            normalized_summary,
        )

        backward = compare_partitions(
            normalized_summary,
            raw_summary,
        )

        if any((
            forward[
                "split_pair_count"
            ],
            forward[
                "introduced_pair_count"
            ],
            backward[
                "split_pair_count"
            ],
            backward[
                "introduced_pair_count"
            ],
        )):
            raise RuntimeError(
                "raw/normalized O1 dynamic partitions differ"
            )

        comparisons[
            observation
        ] = {
            "partition_equal": True,
            "raw_distinct_signatures": (
                raw_summary[
                    "distinct_signatures"
                ]
            ),
            "normalized_distinct_signatures": (
                normalized_summary[
                    "distinct_signatures"
                ]
            ),
        }

    return {
        "normalized": normalized,
        "comparisons": comparisons,
    }


def _reflection_diagnostic_summary(
    *,
    codes: tuple[str, ...],
    geometries: tuple[object, ...],
    channel: str,
) -> dict[str, object]:
    equal_codes = {
        observation: []
        for observation in OBSERVATIONS
    }

    changed_codes = {
        observation: []
        for observation in OBSERVATIONS
    }

    for code, geometry in zip(
        codes,
        geometries,
    ):
        diagnostic = (
            o1.canonical_reflection_diagnostic(
                geometry,
                channel,
            )
        )

        if tuple(
            diagnostic
        ) != OBSERVATIONS:
            raise RuntimeError(
                "canonical reflection diagnostic "
                "changed observation order"
            )

        for observation in OBSERVATIONS:
            target = (
                equal_codes
                if diagnostic[
                    observation
                ]
                else changed_codes
            )

            target[
                observation
            ].append(
                code
            )

    return {
        observation: {
            "equal_count": len(
                equal_codes[
                    observation
                ]
            ),
            "changed_count": len(
                changed_codes[
                    observation
                ]
            ),
            "equal_shape_codes": (
                equal_codes[
                    observation
                ]
            ),
            "changed_shape_codes": (
                changed_codes[
                    observation
                ]
            ),
        }
        for observation in OBSERVATIONS
    }


def _analyze_channel(
    *,
    channel: str,
    codes: tuple[str, ...],
    geometries: tuple[object, ...],
    progress: bool,
) -> dict[str, object]:
    signatures = {
        observation: []
        for observation in OBSERVATIONS
    }

    translation_ok = True
    reflection_transport_ok = True

    for index, geometry in enumerate(
        geometries,
        start=1,
    ):
        current = (
            o1.observation_signatures(
                geometry,
                channel,
            )
        )

        if tuple(
            current
        ) != OBSERVATIONS:
            raise RuntimeError(
                "O1 observation contract changed"
            )

        for observation in OBSERVATIONS:
            signatures[
                observation
            ].append(
                current[
                    observation
                ]
            )

        translated = o1.translate_geometry(
            geometry
        )

        translation_ok = (
            translation_ok
            and o1.observation_signatures(
                translated,
                channel,
            )
            == current
        )

        reflection_transport_ok = (
            reflection_transport_ok
            and o1.reflection_transport_audit(
                geometry,
                channel,
            )
        )

        if progress and (
            index % 10 == 0
            or index == len(
                geometries
            )
        ):
            print(
                f"[{channel}] "
                f"{index}/{len(geometries)}",
                file=sys.stderr,
            )

    if not translation_ok:
        raise RuntimeError(
            f"{channel}: translation audit failed"
        )

    if not reflection_transport_ok:
        raise RuntimeError(
            f"{channel}: reflection transport audit failed"
        )

    frozen_signatures = {
        observation: tuple(values)
        for observation, values
        in signatures.items()
    }

    observations = {
        observation: analyze_observation(
            codes=codes,
            signatures=frozen_signatures[
                observation
            ],
        )
        for observation in OBSERVATIONS
    }

    comparisons = {
        name: compare_partitions(
            observations[
                control
            ][
                "summary"
            ],
            observations[
                candidate
            ][
                "summary"
            ],
        )
        for (
            name,
            control,
            candidate,
        ) in COMPARISONS
    }

    raw_normalized = (
        _raw_normalized_audit(
            codes=codes,
            geometries=geometries,
            channel=channel,
            raw_observations=observations,
        )
    )

    reflection_diagnostic = (
        _reflection_diagnostic_summary(
            codes=codes,
            geometries=geometries,
            channel=channel,
        )
    )

    return {
        "observations": observations,
        "comparisons": comparisons,
        "translation_audit_passed": True,
        "reflection_transport_audit_passed": True,
        "canonical_reflection_diagnostic": (
            reflection_diagnostic
        ),
        "raw_normalized_audit": (
            raw_normalized
        ),
    }


def _coupling_comparisons(
    channels: dict[
        str,
        dict[str, object],
    ],
) -> dict[str, object]:
    result = {}

    for (
        family,
        (
            null_channel,
            coupled_channel,
        ),
    ) in COUPLING_FAMILIES.items():
        observations = {}

        for observation in OBSERVATIONS:
            null_summary = channels[
                null_channel
            ][
                "observations"
            ][
                observation
            ][
                "summary"
            ]

            coupled_summary = channels[
                coupled_channel
            ][
                "observations"
            ][
                observation
            ][
                "summary"
            ]

            observations[
                observation
            ] = compare_partitions(
                null_summary,
                coupled_summary,
            )

        result[
            family
        ] = observations

    return result


def analyze_corpus(
    *,
    name: str,
    shapes: tuple[object, ...],
    progress: bool = True,
) -> dict[str, object]:
    codes = tuple(
        width4.shape_code(
            shape
        )
        for shape in shapes
    )

    if len(
        set(codes)
    ) != len(codes):
        raise RuntimeError(
            "corpus contains duplicate shape codes"
        )

    geometries = tuple(
        width4.encode_experimental_geometry(
            shape
        )
        for shape in shapes
    )

    channels = {}

    for channel in CHANNELS:
        if progress:
            print(
                f"[{name}] O1 {channel}: "
                f"computing {len(shapes)} forms",
                file=sys.stderr,
            )

        channels[
            channel
        ] = _analyze_channel(
            channel=channel,
            codes=codes,
            geometries=geometries,
            progress=progress,
        )

    return {
        "o1_protocol_id": o1.PROTOCOL_ID,
        "corpus": name,
        "form_count": len(
            shapes
        ),
        "sample_steps": list(
            o1.SAMPLE_STEPS
        ),
        "channels": channels,
        "coupling_comparisons": (
            _coupling_comparisons(
                channels
            )
        ),
        "source_boundary": {
            "shape_code_is_metadata_only": True,
            "width4_geometry_encoder_is_input_only": True,
            "s1_input": False,
            "s2_input": False,
            "h1_input": False,
            "p1_input": False,
            "i1_input": False,
            "t1_input": False,
            "gate4_input": False,
        },
    }


def build_report(
    *,
    corpus: str,
    progress: bool = True,
) -> dict[str, object]:
    shapes = tuple(
        _select_corpus(
            corpus
        )
    )

    analysis = analyze_corpus(
        name=corpus,
        shapes=shapes,
        progress=progress,
    )

    return {
        "evidence_protocol_id": PROTOCOL_ID,
        "source_digests": {
            "o1_protocol_sha256": (
                _sha256_file(
                    O1_PROTOCOL_PATH
                )
            ),
            "o1_tool_sha256": (
                _sha256_file(
                    O1_TOOL_PATH
                )
            ),
            "width4_source_sha256": (
                _sha256_file(
                    WIDTH4_TOOL_PATH
                )
            ),
            "evidence_runner_sha256": (
                _sha256_file(
                    Path(__file__)
                )
            ),
        },
        "analysis": analysis,
    }


def write_report(
    report: dict[str, object],
    output: Path,
) -> str:
    payload = (
        json.dumps(
            _jsonable(report),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode(
        "utf-8"
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


def parse_args(
    argv: list[str] | None = None,
):
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic PETRA VISION "
            "Gate 3 O1 evidence."
        )
    )

    parser.add_argument(
        "--corpus",
        required=True,
        choices=CORPORA,
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
    args = parse_args(
        argv
    )

    report = build_report(
        corpus=args.corpus,
        progress=True,
    )

    digest = write_report(
        report,
        args.output,
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
