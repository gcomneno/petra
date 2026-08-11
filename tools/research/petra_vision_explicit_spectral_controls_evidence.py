#!/usr/bin/env python3
"""Deterministic evidence runner for PETRA VISION Gate 3 G3-S0/S1."""

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

import sympy as sp


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


S01_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls.py"
)

WIDTH4_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian_width4.py"
)

V1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)

D1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling.py"
)

F1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_f1.py"
)

L1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_global_geometric_coupling_l1.py"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-s0-s1-evidence-v0"
)

EXPECTED_S01_PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-s0-s1-v0"
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

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


s01 = _load_module(
    S01_TOOL_PATH,
    "_petra_vision_gate3_s01_evidence_tool",
)

width4 = _load_module(
    WIDTH4_TOOL_PATH,
    "_petra_vision_gate3_s01_evidence_width4",
)


if s01.PROTOCOL_ID != EXPECTED_S01_PROTOCOL_ID:
    raise RuntimeError(
        "evidence runner requires frozen G3-S0/S1 protocol"
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
        _canonical_json_bytes(signature)
    ).hexdigest()


def _collision_groups(
    codes: tuple[str, ...],
    signatures: tuple[object, ...],
) -> tuple[tuple[str, ...], ...]:
    if len(codes) != len(signatures):
        raise ValueError(
            "codes and signatures must have equal length"
        )

    groups: dict[object, list[str]] = defaultdict(list)

    for code, signature in zip(
        codes,
        signatures,
    ):
        groups[signature].append(code)

    return tuple(sorted(
        tuple(sorted(group))
        for group in groups.values()
        if len(group) > 1
    ))


def _collision_pairs_from_groups(
    groups: Iterable[tuple[str, ...]],
) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    for group in groups:
        for left, right in combinations(
            group,
            2,
        ):
            pairs.add(
                tuple(sorted((left, right)))
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
        "distinct_signatures": (
            len(set(signatures))
        ),
        "collision_group_count": len(groups),
        "colliding_shape_count": sum(
            len(group)
            for group in groups
        ),
        "collision_pair_count": len(pairs),
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

    control_pairs = _collision_pairs_from_groups(
        control_groups
    )

    candidate_pairs = _collision_pairs_from_groups(
        candidate_groups
    )

    split = sorted(
        control_pairs - candidate_pairs
    )

    introduced = sorted(
        candidate_pairs - control_pairs
    )

    return {
        "distinct_signature_gain": (
            int(candidate_summary[
                "distinct_signatures"
            ])
            - int(control_summary[
                "distinct_signatures"
            ])
        ),
        "control_collision_pair_count": (
            len(control_pairs)
        ),
        "candidate_collision_pair_count": (
            len(candidate_pairs)
        ),
        "split_pair_count": len(split),
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
            _signature_digest(signature)
            for signature in signatures
        ],
    }


def analyze_corpus(
    corpus_name: str,
) -> dict[str, object]:
    corpus = tuple(
        _select_corpus(corpus_name)
    )

    codes = tuple(
        width4.shape_code(shape)
        for shape in corpus
    )

    geometries = tuple(
        width4.encode_experimental_geometry(
            shape
        )
        for shape in corpus
    )

    substrate_results: dict[
        str,
        object,
    ] = {}

    for substrate in s01.SUBSTRATES:
        print(
            f"[{corpus_name}] {substrate}: "
            f"computing {len(geometries)} forms",
            file=sys.stderr,
            flush=True,
        )

        operator_signatures = []
        intrinsic_signatures = []
        spectrum_signatures = []

        has_intrinsic = (
            substrate in {
                "F1",
                "L1",
            }
        )

        for index, geometry in enumerate(
            geometries,
            start=1,
        ):
            operator_signatures.append(
                s01.operator_elementary_signature(
                    substrate,
                    geometry,
                )
            )

            if has_intrinsic:
                intrinsic_signatures.append(
                    s01.intrinsic_state_signature(
                        substrate,
                        geometry,
                    )
                )

            spectrum_signatures.append(
                s01.exact_operator_spectrum_signature(
                    substrate,
                    geometry,
                )
            )

            if (
                index % 10 == 0
                or index == len(geometries)
            ):
                print(
                    f"[{corpus_name}] {substrate}: "
                    f"{index}/{len(geometries)}",
                    file=sys.stderr,
                    flush=True,
                )

        operator_tuple = tuple(
            operator_signatures
        )

        spectrum_tuple = tuple(
            spectrum_signatures
        )

        operator_result = _analyze_channel(
            codes=codes,
            signatures=operator_tuple,
        )

        spectrum_result = _analyze_channel(
            codes=codes,
            signatures=spectrum_tuple,
        )

        result: dict[str, object] = {
            "s0_operator_elementary": (
                operator_result
            ),
            "s1_exact_operator_spectrum": (
                spectrum_result
            ),
            "s0_to_s1": compare_partitions(
                operator_result["summary"],
                spectrum_result["summary"],
            ),
        }

        if has_intrinsic:
            intrinsic_tuple = tuple(
                intrinsic_signatures
            )

            result[
                "s0_intrinsic_state"
            ] = _analyze_channel(
                codes=codes,
                signatures=intrinsic_tuple,
            )
        else:
            result[
                "s0_intrinsic_state"
            ] = None

        substrate_results[
            substrate
        ] = result

    return {
        "corpus": corpus_name,
        "form_count": len(corpus),
        "substrates": substrate_results,
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
        "s0_s1_protocol_id": (
            s01.PROTOCOL_ID
        ),
        "sympy_version": sp.__version__,
        "substrate_protocol_ids": {
            "B0": s01.v1.PROTOCOL_ID,
            "D1": s01.d1.PROTOCOL_ID,
            "F1": s01.f1.PROTOCOL_ID,
            "L1": s01.l1.PROTOCOL_ID,
        },
        "source_sha256": {
            "s0_s1_tool": (
                _sha256_file(
                    S01_TOOL_PATH
                )
            ),
            "evidence_runner": (
                _sha256_file(
                    Path(__file__)
                )
            ),
            "width4_corpus_tool": (
                _sha256_file(
                    WIDTH4_TOOL_PATH
                )
            ),
            "b0_source": (
                _sha256_file(
                    V1_TOOL_PATH
                )
            ),
            "d1_source": (
                _sha256_file(
                    D1_TOOL_PATH
                )
            ),
            "f1_source": (
                _sha256_file(
                    F1_TOOL_PATH
                )
            ),
            "l1_source": (
                _sha256_file(
                    L1_TOOL_PATH
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate exact Gate 3 G3-S0/S1 evidence "
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

    return parser.parse_args()


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
    raise SystemExit(main())
