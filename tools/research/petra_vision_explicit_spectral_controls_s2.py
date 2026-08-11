"""Exact PETRA VISION Gate 3 G3-S2 local spectral controls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

import sympy as sp

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

S01_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_explicit_spectral_controls.py"
)

FGS_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "research"
    / "petra_vision_structural_geometric_factorization.py"
)


PROTOCOL_ID = (
    "petra-vision-explicit-spectral-controls-s2-v0"
)

APPLICABLE_SUBSTRATES = (
    "B0",
    "D1",
    "F1",
)

NOT_APPLICABLE = "not_applicable"

PolynomialSignature: TypeAlias = tuple[
    tuple[int, int],
    ...,
]

LocalSpectrumMultiset: TypeAlias = tuple[
    PolynomialSignature,
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
            f"unable to load frozen research module: {path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


s01 = _load_module(
    S01_TOOL_PATH,
    "_petra_vision_gate3_s2_s01",
)

fgs = _load_module(
    FGS_TOOL_PATH,
    "_petra_vision_gate3_s2_fgs",
)


if (
    s01.PROTOCOL_ID
    != "petra-vision-explicit-spectral-controls-s0-s1-v0"
):
    raise RuntimeError(
        "G3-S2 requires frozen G3-S0/S1"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G3-S2 expects an exact OrthogonalGeometry"
        )

    return geometry


def local_spectral_multiset(
    matrices: tuple[sp.MatrixBase, ...],
) -> LocalSpectrumMultiset:
    """Discard unit order while preserving every local spectral occurrence."""

    signatures = tuple(
        s01.characteristic_polynomial_signature(
            matrix
        )
        for matrix in matrices
    )

    return tuple(sorted(signatures))


def _induced_unweighted_laplacian(
    *,
    vertices: tuple[int, ...],
    adjacency: tuple[
        tuple[int, ...],
        ...,
    ],
) -> sp.Matrix:
    local_index = {
        vertex: position
        for position, vertex in enumerate(
            vertices
        )
    }

    matrix = sp.zeros(
        len(vertices),
        len(vertices),
    )

    for vertex in vertices:
        local_vertex = local_index[
            vertex
        ]

        local_neighbors = tuple(
            neighbor
            for neighbor in adjacency[
                vertex
            ]
            if neighbor in local_index
        )

        matrix[
            local_vertex,
            local_vertex,
        ] = len(local_neighbors)

        for neighbor in local_neighbors:
            matrix[
                local_vertex,
                local_index[neighbor],
            ] = -1

    return matrix


def b0_component_matrices(
    geometry: OrthogonalGeometry,
) -> tuple[sp.Matrix, ...]:
    """Return exact native occupied-component B0 Laplacians."""

    current = _require_geometry(
        geometry
    )

    graph = s01.v1.build_geometry_graph(
        current
    )

    return tuple(
        _induced_unweighted_laplacian(
            vertices=component,
            adjacency=graph.adjacency,
        )
        for component in graph.components
    )


def b0_component_spectrum_signature(
    geometry: OrthogonalGeometry,
) -> LocalSpectrumMultiset:
    return local_spectral_multiset(
        b0_component_matrices(
            geometry
        )
    )


def d1_original_component_matrices(
    geometry: OrthogonalGeometry,
) -> tuple[sp.Matrix, ...]:
    """Return local weight-2 D1 Laplacians before clearance bridges."""

    current = _require_geometry(
        geometry
    )

    graph = s01.d1.build_distance2_graph(
        current
    )

    local_edges = tuple(
        edge
        for edge in graph.edges
        if edge.kind == "local"
    )

    if any(
        edge.weight != s01.d1.LOCAL_WEIGHT
        for edge in local_edges
    ):
        raise RuntimeError(
            "frozen D1 local edge has unexpected weight"
        )

    if any(
        edge.kind == "bridge"
        for edge in local_edges
    ):
        raise RuntimeError(
            "D1 bridge entered local-edge set"
        )

    matrices: list[sp.Matrix] = []

    for component in graph.original_components:
        local_index = {
            vertex: position
            for position, vertex in enumerate(
                component
            )
        }

        matrix = sp.zeros(
            len(component),
            len(component),
        )

        for edge in local_edges:
            if (
                edge.left not in local_index
                or edge.right not in local_index
            ):
                continue

            left = local_index[
                edge.left
            ]

            right = local_index[
                edge.right
            ]

            weight = sp.Integer(
                edge.weight
            )

            matrix[left, left] += weight
            matrix[right, right] += weight

            matrix[left, right] -= weight
            matrix[right, left] -= weight

        matrices.append(
            matrix
        )

    return tuple(matrices)


def d1_original_component_spectrum_signature(
    geometry: OrthogonalGeometry,
) -> LocalSpectrumMultiset:
    return local_spectral_multiset(
        d1_original_component_matrices(
            geometry
        )
    )


def f1_immediate_factors(
    geometry: OrthogonalGeometry,
) -> tuple[OrthogonalGeometry, ...]:
    """Return the exact immediate native FGS factors used as G3-S2 units."""

    current = _require_geometry(
        geometry
    )

    factors = fgs.native_fgs(
        current
    )

    if fgs.recompose_fgs(
        factors
    ) != current:
        raise RuntimeError(
            "native immediate FGS factors do not recompose source geometry"
        )

    return factors


def f1_factor_matrices(
    geometry: OrthogonalGeometry,
) -> tuple[sp.Matrix, ...]:
    """Return one exact B0 Laplacian per immediate native FGS factor."""

    factors = f1_immediate_factors(
        geometry
    )

    return tuple(
        s01.b0_operator_matrix(
            factor
        )
        for factor in factors
    )


def f1_factor_spectrum_signature(
    geometry: OrthogonalGeometry,
) -> LocalSpectrumMultiset:
    return local_spectral_multiset(
        f1_factor_matrices(
            geometry
        )
    )


def local_unit_count(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> int | None:
    current = _require_geometry(
        geometry
    )

    if substrate == "B0":
        return len(
            b0_component_matrices(
                current
            )
        )

    if substrate == "D1":
        return len(
            d1_original_component_matrices(
                current
            )
        )

    if substrate == "F1":
        return len(
            f1_immediate_factors(
                current
            )
        )

    if substrate == "L1":
        return None

    raise ValueError(
        f"unsupported Gate 3 S2 substrate: {substrate}"
    )


def local_spectrum_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> LocalSpectrumMultiset | str:
    current = _require_geometry(
        geometry
    )

    if substrate == "B0":
        return b0_component_spectrum_signature(
            current
        )

    if substrate == "D1":
        return d1_original_component_spectrum_signature(
            current
        )

    if substrate == "F1":
        return f1_factor_spectrum_signature(
            current
        )

    if substrate == "L1":
        return NOT_APPLICABLE

    raise ValueError(
        f"unsupported Gate 3 S2 substrate: {substrate}"
    )


def multiply_polynomial_signatures(
    signatures: LocalSpectrumMultiset,
) -> PolynomialSignature:
    """Multiply exact monic polynomial signatures for structural controls."""

    variable = sp.Symbol("x")
    product = sp.Poly(
        1,
        variable,
        domain=sp.QQ,
    )

    for signature in signatures:
        degree = len(signature) - 1

        expression = sp.Add(*(
            sp.Rational(
                numerator,
                denominator,
            )
            * variable ** (
                degree - index
            )
            for index, (
                numerator,
                denominator,
            ) in enumerate(
                signature
            )
        ))

        product *= sp.Poly(
            expression,
            variable,
            domain=sp.QQ,
        )

    product = product.monic()

    return tuple(
        s01.canonical_rational(
            coefficient
        )
        for coefficient in product.all_coeffs()
    )


def signature_bytes(
    signature: object,
) -> bytes:
    return s01.signature_bytes(
        signature
    )


__all__ = [
    "APPLICABLE_SUBSTRATES",
    "NOT_APPLICABLE",
    "PROTOCOL_ID",
    "b0_component_matrices",
    "b0_component_spectrum_signature",
    "d1_original_component_matrices",
    "d1_original_component_spectrum_signature",
    "f1_factor_matrices",
    "f1_factor_spectrum_signature",
    "f1_immediate_factors",
    "local_spectral_multiset",
    "local_spectrum_signature",
    "local_unit_count",
    "multiply_polynomial_signatures",
    "signature_bytes",
]
