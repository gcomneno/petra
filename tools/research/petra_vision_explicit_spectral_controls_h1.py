"""Exact PETRA VISION Gate 3 G3-H1 heat-trace controls."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

S01_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls.py"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-h1-v0"
)

TRUNCATIONS = (
    ("M1", 1),
    ("M2", 2),
    ("M4", 4),
    ("M8", 8),
)

MAX_MOMENT = 8

RationalPair: TypeAlias = tuple[int, int]
PolynomialSignature: TypeAlias = tuple[RationalPair, ...]
MomentSignature: TypeAlias = tuple[RationalPair, ...]


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
            f"unable to load frozen research module: {path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


s01 = _load_module(
    S01_TOOL_PATH,
    "_petra_vision_gate3_h1_s01",
)


if (
    s01.PROTOCOL_ID
    != "petra-vision-explicit-spectral-controls-s0-s1-v0"
):
    raise RuntimeError(
        "G3-H1 requires frozen Gate 3 S0/S1 controls"
    )


def _require_rational_pair(
    pair: object,
) -> RationalPair:
    if (
        type(pair) is not tuple
        or len(pair) != 2
        or type(pair[0]) is not int
        or type(pair[1]) is not int
        or pair[1] <= 0
    ):
        raise TypeError(
            "H1 polynomial coefficients must be canonical rational pairs"
        )

    fraction = Fraction(
        pair[0],
        pair[1],
    )

    canonical = (
        fraction.numerator,
        fraction.denominator,
    )

    if pair != canonical:
        raise ValueError(
            "H1 rational pair must already be canonical"
        )

    return pair


def _fraction_from_pair(
    pair: RationalPair,
) -> Fraction:
    current = _require_rational_pair(
        pair
    )

    return Fraction(
        current[0],
        current[1],
    )


def _require_polynomial_signature(
    signature: object,
) -> PolynomialSignature:
    if (
        type(signature) is not tuple
        or not signature
    ):
        raise TypeError(
            "H1 expects a non-empty polynomial signature"
        )

    coefficients = tuple(
        _require_rational_pair(
            coefficient
        )
        for coefficient in signature
    )

    if coefficients[0] != (1, 1):
        raise ValueError(
            "H1 characteristic polynomial must be monic"
        )

    return coefficients


def _require_max_moment(
    max_moment: int,
) -> int:
    if (
        type(max_moment) is not int
        or not 0 <= max_moment <= MAX_MOMENT
    ):
        raise ValueError(
            f"H1 max moment must be between 0 and {MAX_MOMENT}"
        )

    return max_moment


def _require_truncation(
    truncation: str,
) -> int:
    for name, max_moment in TRUNCATIONS:
        if truncation == name:
            return max_moment

    raise ValueError(
        f"unsupported H1 truncation: {truncation}"
    )


def operator_order_from_spectrum(
    signature: PolynomialSignature,
) -> int:
    coefficients = (
        _require_polynomial_signature(
            signature
        )
    )

    return len(coefficients) - 1


def power_sums_from_charpoly(
    signature: PolynomialSignature,
    max_moment: int = MAX_MOMENT,
) -> MomentSignature:
    """Return exact p_0..p_k from one monic characteristic polynomial."""

    coefficients = tuple(
        _fraction_from_pair(
            coefficient
        )
        for coefficient in (
            _require_polynomial_signature(
                signature
            )
        )
    )

    current_max = _require_max_moment(
        max_moment
    )

    degree = len(coefficients) - 1

    moments: list[Fraction] = [
        Fraction(
            degree,
            1,
        )
    ]

    for order in range(
        1,
        current_max + 1,
    ):
        total = Fraction(
            0,
            1,
        )

        previous_coefficient_count = min(
            order - 1,
            degree,
        )

        for coefficient_index in range(
            1,
            previous_coefficient_count + 1,
        ):
            total += (
                coefficients[
                    coefficient_index
                ]
                * moments[
                    order - coefficient_index
                ]
            )

        if order <= degree:
            total += (
                order
                * coefficients[order]
            )

        moment = -total

        moments.append(
            moment
        )

    return tuple(
        s01.canonical_rational(
            moment
        )
        for moment in moments
    )


def heat_trace_moment_signature_from_spectrum(
    signature: PolynomialSignature,
    truncation: str,
) -> MomentSignature:
    max_moment = _require_truncation(
        truncation
    )

    return power_sums_from_charpoly(
        signature,
        max_moment=max_moment,
    )


def all_heat_trace_moment_signatures_from_spectrum(
    signature: PolynomialSignature,
) -> tuple[
    tuple[str, MomentSignature],
    ...,
]:
    full = power_sums_from_charpoly(
        signature,
        max_moment=MAX_MOMENT,
    )

    return tuple(
        (
            name,
            full[
                : max_moment + 1
            ],
        )
        for name, max_moment in TRUNCATIONS
    )


def heat_trace_moment_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
    truncation: str,
) -> MomentSignature:
    spectrum = (
        s01.exact_operator_spectrum_signature(
            substrate,
            geometry,
        )
    )

    return (
        heat_trace_moment_signature_from_spectrum(
            spectrum,
            truncation,
        )
    )


def all_heat_trace_moment_signatures(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> tuple[
    tuple[str, MomentSignature],
    ...,
]:
    spectrum = (
        s01.exact_operator_spectrum_signature(
            substrate,
            geometry,
        )
    )

    return (
        all_heat_trace_moment_signatures_from_spectrum(
            spectrum
        )
    )


def signature_bytes(
    signature: object,
) -> bytes:
    return json.dumps(
        signature,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


__all__ = [
    "MAX_MOMENT",
    "PROTOCOL_ID",
    "TRUNCATIONS",
    "all_heat_trace_moment_signatures",
    "all_heat_trace_moment_signatures_from_spectrum",
    "heat_trace_moment_signature",
    "heat_trace_moment_signature_from_spectrum",
    "operator_order_from_spectrum",
    "power_sums_from_charpoly",
    "signature_bytes",
]
