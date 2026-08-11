#!/usr/bin/env python3
"""Deterministic evidence runner for PETRA VISION Gate 3 G3-P1."""

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


P1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls_p1.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)

P1_PROTOCOL_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "research"
    / "petra-vision"
    / "EXPLICIT_SPECTRAL_CONTROLS_P1_PROTOCOL.md"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-p1-evidence-v0"
)

EXPECTED_P1_PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-p1-v0"
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

INTRINSIC_PROBE_MODES = (
    "local-degree",
    "constant",
    "zero",
)

TRANSPORTED_PROBE_PAIRS = {
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


p1 = _load_module(
    P1_TOOL_PATH,
    "_petra_vision_gate3_p1_evidence_tool",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate3_p1_evidence_width4",
)


if p1.PROTOCOL_ID != EXPECTED_P1_PROTOCOL_ID:
    raise RuntimeError(
        "evidence runner requires frozen G3-P1 protocol"
    )

if p1.SUBSTRATES != (
    "B0",
    "D1",
):
    raise RuntimeError(
        "evidence runner requires frozen B0/D1 P1 scope"
    )

if p1.PROBE_MODES != (
    "minimum",
    "reflected-minimum",
    "local-degree",
    "constant",
    "zero",
):
    raise RuntimeError(
        "evidence runner requires frozen P1 probe family"
    )

if p1.TRANSLATION_VECTOR != (
    17,
    11,
):
    raise RuntimeError(
        "evidence runner requires frozen P1 translation vector"
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
    ).encode("utf-8")


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
) -> tuple[tuple[str, ...], ...]:
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
        groups[signature].append(
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
            signatures[index[left]]
            == signatures[index[right]]
        ),
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


def _mass_distribution(
    masses: tuple[int, ...],
) -> dict[str, int]:
    return {
        str(mass): count
        for mass, count in sorted(
            Counter(
                masses
            ).items()
        )
    }


def _assert_intrinsic_pair_control(
    result: dict[str, object],
    *,
    substrate: str,
    operator: str,
    mode: str,
) -> None:
    if mode not in INTRINSIC_PROBE_MODES:
        return

    expected = result[
        "expected_collision"
    ]

    if (
        expected["present"]
        and not expected["collides"]
    ):
        raise RuntimeError(
            "intrinsic P1 probe separated "
            "#23/#41: "
            f"{substrate} {operator} {mode}"
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

    raw_probe_data: dict[
        str,
        dict[str, object],
    ] = {}

    raw_b0_data: dict[
        str,
        dict[str, object],
    ] = {}

    raw_d1_data: dict[
        str,
        dict[str, object],
    ] = {}

    for mode in p1.PROBE_MODES:
        print(
            f"[{corpus_name}] P1 {mode}: "
            f"computing {len(geometries)} forms",
            file=sys.stderr,
            flush=True,
        )

        probes = []
        masses = []
        step_zero = []

        b0_dynamic = []
        d1_null_dynamic = []
        d1_coupled_dynamic = []

        b0_translation_passed = True
        d1_null_translation_passed = True
        d1_coupled_translation_passed = True

        b0_reflection_passed = True
        d1_null_reflection_passed = True
        d1_coupled_reflection_passed = True

        for index, geometry in enumerate(
            geometries,
            start=1,
        ):
            b0_probe = p1.probe_state(
                "B0",
                geometry,
                mode,
            )

            d1_probe = p1.probe_state(
                "D1",
                geometry,
                mode,
            )

            _assert_equal(
                b0_probe,
                d1_probe,
                message=(
                    "B0 and D1 probe tuples differ "
                    f"for {mode}"
                ),
            )

            probe = b0_probe

            probes.append(
                probe
            )

            masses.append(
                p1.probe_mass(
                    probe
                )
            )

            step_zero_signature = (
                p1.step_zero_signature(
                    probe
                )
            )

            step_zero.append(
                step_zero_signature
            )

            current_b0 = (
                p1.b0_dynamic_signature_from_probe(
                    geometry,
                    probe,
                )
            )

            current_d1_null = (
                p1.d1_dynamic_signature_from_probe(
                    geometry,
                    probe,
                    coupled=False,
                )
            )

            current_d1_coupled = (
                p1.d1_dynamic_signature_from_probe(
                    geometry,
                    probe,
                    coupled=True,
                )
            )

            b0_dynamic.append(
                current_b0
            )

            d1_null_dynamic.append(
                current_d1_null
            )

            d1_coupled_dynamic.append(
                current_d1_coupled
            )

            translated = p1.translate_geometry(
                geometry
            )

            translated_b0_probe = (
                p1.probe_state(
                    "B0",
                    translated,
                    mode,
                )
            )

            translated_d1_probe = (
                p1.probe_state(
                    "D1",
                    translated,
                    mode,
                )
            )

            _assert_equal(
                probe,
                translated_b0_probe,
                message=(
                    "B0 probe changed under translation: "
                    f"{mode}"
                ),
            )

            _assert_equal(
                probe,
                translated_d1_probe,
                message=(
                    "D1 probe changed under translation: "
                    f"{mode}"
                ),
            )

            translated_b0 = (
                p1.b0_dynamic_signature_from_probe(
                    translated,
                    translated_b0_probe,
                )
            )

            translated_d1_null = (
                p1.d1_dynamic_signature_from_probe(
                    translated,
                    translated_d1_probe,
                    coupled=False,
                )
            )

            translated_d1_coupled = (
                p1.d1_dynamic_signature_from_probe(
                    translated,
                    translated_d1_probe,
                    coupled=True,
                )
            )

            b0_translation_passed = (
                b0_translation_passed
                and translated_b0 == current_b0
            )

            d1_null_translation_passed = (
                d1_null_translation_passed
                and translated_d1_null
                == current_d1_null
            )

            d1_coupled_translation_passed = (
                d1_coupled_translation_passed
                and translated_d1_coupled
                == current_d1_coupled
            )

            reflected = p1.horizontal_reflection(
                geometry
            )

            if mode in INTRINSIC_PROBE_MODES:
                reflected_mode = mode
            else:
                reflected_mode = (
                    TRANSPORTED_PROBE_PAIRS[
                        mode
                    ]
                )

            reflected_b0_probe = (
                p1.probe_state(
                    "B0",
                    reflected,
                    reflected_mode,
                )
            )

            reflected_d1_probe = (
                p1.probe_state(
                    "D1",
                    reflected,
                    reflected_mode,
                )
            )

            reflected_b0 = (
                p1.b0_dynamic_signature_from_probe(
                    reflected,
                    reflected_b0_probe,
                )
            )

            reflected_d1_null = (
                p1.d1_dynamic_signature_from_probe(
                    reflected,
                    reflected_d1_probe,
                    coupled=False,
                )
            )

            reflected_d1_coupled = (
                p1.d1_dynamic_signature_from_probe(
                    reflected,
                    reflected_d1_probe,
                    coupled=True,
                )
            )

            b0_reflection_passed = (
                b0_reflection_passed
                and reflected_b0
                == current_b0
            )

            d1_null_reflection_passed = (
                d1_null_reflection_passed
                and reflected_d1_null
                == current_d1_null
            )

            d1_coupled_reflection_passed = (
                d1_coupled_reflection_passed
                and reflected_d1_coupled
                == current_d1_coupled
            )

            if mode in INTRINSIC_PROBE_MODES:
                _assert_equal(
                    step_zero_signature,
                    p1.step_zero_signature(
                        reflected_b0_probe
                    ),
                    message=(
                        "intrinsic step-zero probe "
                        "changed under reflection: "
                        f"{mode}"
                    ),
                )

            if (
                index % 10 == 0
                or index == len(geometries)
            ):
                print(
                    f"[{corpus_name}] P1 {mode}: "
                    f"{index}/{len(geometries)}",
                    file=sys.stderr,
                    flush=True,
                )

        if not b0_translation_passed:
            raise RuntimeError(
                f"B0 translation audit failed: {mode}"
            )

        if not d1_null_translation_passed:
            raise RuntimeError(
                "D1 null translation audit failed: "
                f"{mode}"
            )

        if not d1_coupled_translation_passed:
            raise RuntimeError(
                "D1 coupled translation audit failed: "
                f"{mode}"
            )

        if not b0_reflection_passed:
            raise RuntimeError(
                f"B0 reflection audit failed: {mode}"
            )

        if not d1_null_reflection_passed:
            raise RuntimeError(
                "D1 null reflection audit failed: "
                f"{mode}"
            )

        if not d1_coupled_reflection_passed:
            raise RuntimeError(
                "D1 coupled reflection audit failed: "
                f"{mode}"
            )

        step_zero_result = _analyze_channel(
            codes=codes,
            signatures=tuple(
                step_zero
            ),
        )

        b0_result = _analyze_channel(
            codes=codes,
            signatures=tuple(
                b0_dynamic
            ),
        )

        d1_null_result = _analyze_channel(
            codes=codes,
            signatures=tuple(
                d1_null_dynamic
            ),
        )

        d1_coupled_result = _analyze_channel(
            codes=codes,
            signatures=tuple(
                d1_coupled_dynamic
            ),
        )

        _assert_intrinsic_pair_control(
            b0_result,
            substrate="B0",
            operator="frozen",
            mode=mode,
        )

        _assert_intrinsic_pair_control(
            d1_null_result,
            substrate="D1",
            operator="null",
            mode=mode,
        )

        _assert_intrinsic_pair_control(
            d1_coupled_result,
            substrate="D1",
            operator="coupled",
            mode=mode,
        )

        raw_probe_data[mode] = {
            "mass_distribution": (
                _mass_distribution(
                    tuple(masses)
                )
            ),
            "masses": masses,
            "step_zero": (
                step_zero_result
            ),
            "probe_digests": [
                _signature_digest(
                    probe
                )
                for probe in probes
            ],
        }

        raw_b0_data[mode] = {
            "dynamic": b0_result,
            "translation_audit_passed": (
                b0_translation_passed
            ),
            "reflection_audit_passed": (
                b0_reflection_passed
            ),
        }

        raw_d1_data[mode] = {
            "matched_probe_identity": True,
            "null": {
                "dynamic": (
                    d1_null_result
                ),
                "translation_audit_passed": (
                    d1_null_translation_passed
                ),
                "reflection_audit_passed": (
                    d1_null_reflection_passed
                ),
            },
            "coupled": {
                "dynamic": (
                    d1_coupled_result
                ),
                "translation_audit_passed": (
                    d1_coupled_translation_passed
                ),
                "reflection_audit_passed": (
                    d1_coupled_reflection_passed
                ),
            },
            "null_to_coupled": (
                compare_partitions(
                    d1_null_result[
                        "summary"
                    ],
                    d1_coupled_result[
                        "summary"
                    ],
                )
            ),
        }

    minimum_step_zero = (
        raw_probe_data[
            "minimum"
        ][
            "step_zero"
        ][
            "summary"
        ]
    )

    minimum_b0 = (
        raw_b0_data[
            "minimum"
        ][
            "dynamic"
        ][
            "summary"
        ]
    )

    minimum_d1_null = (
        raw_d1_data[
            "minimum"
        ][
            "null"
        ][
            "dynamic"
        ][
            "summary"
        ]
    )

    minimum_d1_coupled = (
        raw_d1_data[
            "minimum"
        ][
            "coupled"
        ][
            "dynamic"
        ][
            "summary"
        ]
    )

    for mode in p1.PROBE_MODES:
        raw_probe_data[
            mode
        ][
            "minimum_to_probe"
        ] = compare_partitions(
            minimum_step_zero,
            raw_probe_data[
                mode
            ][
                "step_zero"
            ][
                "summary"
            ],
        )

        raw_b0_data[
            mode
        ][
            "minimum_to_mode"
        ] = compare_partitions(
            minimum_b0,
            raw_b0_data[
                mode
            ][
                "dynamic"
            ][
                "summary"
            ],
        )

        raw_d1_data[
            mode
        ][
            "minimum_to_mode"
        ] = {
            "null": (
                compare_partitions(
                    minimum_d1_null,
                    raw_d1_data[
                        mode
                    ][
                        "null"
                    ][
                        "dynamic"
                    ][
                        "summary"
                    ],
                )
            ),
            "coupled": (
                compare_partitions(
                    minimum_d1_coupled,
                    raw_d1_data[
                        mode
                    ][
                        "coupled"
                    ][
                        "dynamic"
                    ][
                        "summary"
                    ],
                )
            ),
        }

    return {
        "corpus": corpus_name,
        "form_count": len(
            corpus
        ),
        "probes": raw_probe_data,
        "substrates": {
            "B0": {
                "modes": raw_b0_data,
            },
            "D1": {
                "modes": raw_d1_data,
            },
        },
    }


def build_evidence(
    corpus_name: str,
) -> dict[str, object]:
    if corpus_name not in CORPORA:
        raise ValueError(
            f"unsupported corpus: {corpus_name}"
        )

    return {
        "protocol_id": PROTOCOL_ID,
        "p1_protocol_id": (
            p1.PROTOCOL_ID
        ),
        "probe_modes": list(
            p1.PROBE_MODES
        ),
        "intrinsic_probe_modes": list(
            INTRINSIC_PROBE_MODES
        ),
        "translation_vector": list(
            p1.TRANSLATION_VECTOR
        ),
        "source_sha256": {
            "p1_protocol": (
                _sha256_file(
                    P1_PROTOCOL_PATH
                )
            ),
            "p1_tool": (
                _sha256_file(
                    P1_TOOL_PATH
                )
            ),
            "b0_tool": (
                _sha256_file(
                    p1.V1_TOOL_PATH
                )
            ),
            "d1_tool": (
                _sha256_file(
                    p1.D1_TOOL_PATH
                )
            ),
            "width4_corpus_tool": (
                _sha256_file(
                    WIDTH4_TOOL_PATH
                )
            ),
            "evidence_runner": (
                _sha256_file(
                    Path(__file__)
                )
            ),
        },
        "analysis": analyze_corpus(
            corpus_name
        ),
    }


def write_evidence(
    evidence: dict[str, object],
    output: Path,
) -> None:
    payload = json.dumps(
        evidence,
        indent=2,
        sort_keys=True,
    ) + "\n"

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        payload,
        encoding="utf-8",
    )


def _parse_args(
    argv: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Gate 3 G3-P1 evidence "
            "for one frozen corpus partition."
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

    return parser.parse_args(
        argv
    )


def main() -> int:
    args = _parse_args()

    evidence = build_evidence(
        args.corpus
    )

    write_evidence(
        evidence,
        args.output,
    )

    digest = hashlib.sha256(
        args.output.read_bytes()
    ).hexdigest()

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
