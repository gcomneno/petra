"""PETRA VISION Gate 2 G2-F0 factor-boundary null control.

G2-F0 composes the frozen native FGS operation with the frozen
graph-Laplacian v1 coordinate-free reader. Immediate factors are observed
independently and their signatures are returned as an unordered multiset.

No inter-factor coupling is implemented here.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

FGS_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_structural_geometric_factorization.py"
)

V1_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_graph_laplacian.py"
)


PROTOCOL_ID = (
    "petra-vision-global-geometric-coupling-fgs-null-v0"
)

EXPECTED_DYNAMIC_PROTOCOL_ID = (
    "petra-vision-graph-laplacian-v1"
)

READER_ID = "unordered-factor-global-multiset"


FactorSignature: TypeAlias = tuple[object, ...]
FactorMultisetSignature: TypeAlias = tuple[
    FactorSignature,
    ...,
]


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


fgs = _load_module(
    FGS_TOOL_PATH,
    "_petra_vision_gate2_f0_native_fgs",
)

v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate2_f0_graph_laplacian_v1",
)


DYNAMIC_PROTOCOL_ID = v1.PROTOCOL_ID

if DYNAMIC_PROTOCOL_ID != EXPECTED_DYNAMIC_PROTOCOL_ID:
    raise RuntimeError(
        "G2-F0 requires frozen graph-Laplacian v1; "
        f"received {DYNAMIC_PROTOCOL_ID!r}"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G2-F0 expects an exact OrthogonalGeometry"
        )

    return geometry


def immediate_factors(
    geometry: OrthogonalGeometry,
) -> tuple[OrthogonalGeometry, ...]:
    """Return the frozen native FGS immediate root factors."""

    current = _require_geometry(geometry)

    factors = fgs.native_fgs(current)

    if type(factors) is not tuple:
        raise RuntimeError(
            "native FGS did not return an exact tuple"
        )

    if not all(
        type(factor) is OrthogonalGeometry
        for factor in factors
    ):
        raise RuntimeError(
            "native FGS returned a non-geometry factor"
        )

    return factors


def factor_dynamic_signature(
    factor: OrthogonalGeometry,
) -> FactorSignature:
    """Observe one factor independently through frozen v1."""

    current = _require_geometry(factor)

    signatures = v1.geometry_dynamic_signatures(
        current
    )

    return signatures["global_multiset"]


def ordered_factor_signatures(
    geometry: OrthogonalGeometry,
) -> tuple[FactorSignature, ...]:
    """Return per-factor observations before removing factor order.

    This helper exists only to make the construction boundary auditable.
    It is not the final G2-F0 reader.
    """

    return tuple(
        factor_dynamic_signature(factor)
        for factor in immediate_factors(
            geometry
        )
    )


def factor_multiset_signature(
    geometry: OrthogonalGeometry,
) -> FactorMultisetSignature:
    """Return the unordered multiplicity-preserving F0 signature."""

    return tuple(sorted(
        ordered_factor_signatures(
            geometry
        )
    ))


__all__ = [
    "DYNAMIC_PROTOCOL_ID",
    "EXPECTED_DYNAMIC_PROTOCOL_ID",
    "FGS_TOOL_PATH",
    "PROTOCOL_ID",
    "READER_ID",
    "V1_TOOL_PATH",
    "factor_dynamic_signature",
    "factor_multiset_signature",
    "immediate_factors",
    "ordered_factor_signatures",
]
