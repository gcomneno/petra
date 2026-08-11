"""Exact PETRA VISION Gate 3 G3-S0/S1 spectral controls."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import TypeAlias

import sympy as sp

from petra.vision.geometry import OrthogonalGeometry


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

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
    "petra-vision-explicit-spectral-controls-s0-s1-v0"
)

SUBSTRATES = (
    "B0",
    "D1",
    "F1",
    "L1",
)

RationalPair: TypeAlias = tuple[int, int]
PolynomialSignature: TypeAlias = tuple[RationalPair, ...]
OperatorProfile: TypeAlias = tuple[
    int,
    int,
    int,
    tuple[RationalPair, ...],
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


v1 = _load_module(
    V1_TOOL_PATH,
    "_petra_vision_gate3_s01_v1",
)

d1 = _load_module(
    D1_TOOL_PATH,
    "_petra_vision_gate3_s01_d1",
)

f1 = _load_module(
    F1_TOOL_PATH,
    "_petra_vision_gate3_s01_f1",
)

l1 = _load_module(
    L1_TOOL_PATH,
    "_petra_vision_gate3_s01_l1",
)


if v1.PROTOCOL_ID != "petra-vision-graph-laplacian-v1":
    raise RuntimeError(
        "G3-S0/S1 requires frozen graph-Laplacian v1"
    )

if (
    d1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-distance2-v0"
):
    raise RuntimeError(
        "G3-S0/S1 requires frozen Gate 2 D1"
    )

if (
    f1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-fgs-proximity-v0"
):
    raise RuntimeError(
        "G3-S0/S1 requires frozen Gate 2 F1"
    )

if (
    l1.PROTOCOL_ID
    != "petra-vision-global-geometric-coupling-full-lattice-v0"
):
    raise RuntimeError(
        "G3-S0/S1 requires frozen Gate 2 L1"
    )


def _require_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    if type(geometry) is not OrthogonalGeometry:
        raise TypeError(
            "G3-S0/S1 expects an exact OrthogonalGeometry"
        )

    return geometry


def _require_substrate(
    substrate: str,
) -> str:
    if substrate not in SUBSTRATES:
        raise ValueError(
            f"unsupported Gate 3 substrate: {substrate}"
        )

    return substrate


def canonical_rational(
    value: object,
) -> RationalPair:
    """Serialize one exact scalar as a reduced rational pair."""

    if isinstance(value, float):
        raise TypeError(
            "floating-point values are forbidden in G3-S0/S1"
        )

    if isinstance(value, Fraction):
        return (
            value.numerator,
            value.denominator,
        )

    try:
        rational = sp.Rational(value)
    except (TypeError, ValueError) as error:
        raise TypeError(
            f"value is not an exact rational scalar: {value!r}"
        ) from error

    return (
        int(rational.p),
        int(rational.q),
    )


def _fraction_from_pair(
    pair: RationalPair,
) -> Fraction:
    return Fraction(
        pair[0],
        pair[1],
    )


def _sorted_rationals(
    values: tuple[object, ...],
) -> tuple[RationalPair, ...]:
    serialized = tuple(
        canonical_rational(value)
        for value in values
    )

    return tuple(sorted(
        serialized,
        key=_fraction_from_pair,
    ))


def signature_bytes(
    signature: object,
) -> bytes:
    """Return deterministic canonical JSON bytes for a signature."""

    return json.dumps(
        signature,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def characteristic_polynomial_signature(
    matrix: sp.MatrixBase,
) -> PolynomialSignature:
    """Return the exact monic characteristic-polynomial coefficient tuple."""

    if matrix.rows != matrix.cols:
        raise ValueError(
            "operator matrix must be square"
        )

    if matrix.rows == 0:
        return ((1, 1),)

    polynomial = matrix.charpoly()

    if polynomial.degree() != matrix.rows:
        raise RuntimeError(
            "characteristic-polynomial degree mismatch"
        )

    coefficients = tuple(
        canonical_rational(coefficient)
        for coefficient in polynomial.all_coeffs()
    )

    if coefficients[0] != (1, 1):
        raise RuntimeError(
            "characteristic polynomial must be monic"
        )

    return coefficients


def _positive_support_components(
    weighted_adjacency: tuple[
        tuple[tuple[int, object], ...],
        ...
    ],
) -> int:
    order = len(weighted_adjacency)

    if order == 0:
        return 0

    unseen = set(range(order))
    component_count = 0

    while unseen:
        component_count += 1
        start = min(unseen)
        unseen.remove(start)

        stack = [start]

        while stack:
            current = stack.pop()

            for neighbor, weight in weighted_adjacency[current]:
                if sp.Rational(weight) == 0:
                    continue

                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)

    return component_count


def _operator_profile_from_adjacency(
    weighted_adjacency: tuple[
        tuple[tuple[int, object], ...],
        ...
    ],
) -> OperatorProfile:
    order = len(weighted_adjacency)

    interaction_count = sum(
        1
        for left, row in enumerate(weighted_adjacency)
        for right, weight in row
        if (
            left < right
            and sp.Rational(weight) != 0
        )
    )

    weighted_degrees = tuple(
        sum(
            (
                sp.Rational(weight)
                for _neighbor, weight in row
                if sp.Rational(weight) != 0
            ),
            sp.Rational(0),
        )
        for row in weighted_adjacency
    )

    component_count = _positive_support_components(
        weighted_adjacency
    )

    return (
        order,
        interaction_count,
        component_count,
        _sorted_rationals(weighted_degrees),
    )


def b0_operator_matrix(
    geometry: OrthogonalGeometry,
) -> sp.Matrix:
    current = _require_geometry(geometry)
    graph = v1.build_geometry_graph(current)

    matrix = sp.zeros(
        len(graph.cells),
        len(graph.cells),
    )

    for vertex, neighbors in enumerate(
        graph.adjacency
    ):
        matrix[vertex, vertex] = len(neighbors)

        for neighbor in neighbors:
            matrix[vertex, neighbor] = -1

    return matrix


def b0_operator_profile(
    geometry: OrthogonalGeometry,
) -> OperatorProfile:
    current = _require_geometry(geometry)
    graph = v1.build_geometry_graph(current)

    adjacency = tuple(
        tuple(
            (neighbor, 1)
            for neighbor in neighbors
        )
        for neighbors in graph.adjacency
    )

    return _operator_profile_from_adjacency(
        adjacency
    )


def d1_operator_matrix(
    geometry: OrthogonalGeometry,
) -> sp.Matrix:
    current = _require_geometry(geometry)
    graph = d1.build_distance2_graph(current)

    matrix = sp.zeros(
        len(graph.cells),
        len(graph.cells),
    )

    for vertex, neighbors in enumerate(
        graph.adjacency
    ):
        weighted_degree = sum(
            weight
            for _neighbor, weight in neighbors
        )

        matrix[vertex, vertex] = weighted_degree

        for neighbor, weight in neighbors:
            matrix[vertex, neighbor] = -weight

    return matrix


def d1_operator_profile(
    geometry: OrthogonalGeometry,
) -> OperatorProfile:
    current = _require_geometry(geometry)
    graph = d1.build_distance2_graph(current)

    return _operator_profile_from_adjacency(
        graph.adjacency
    )


def f1_propagation_matrix_from_weights(
    weights: tuple[
        tuple[object, ...],
        ...
    ],
) -> sp.Matrix:
    """Construct the exact frozen F1 propagation operator from symmetric w_ij."""

    order = len(weights)

    if any(
        len(row) != order
        for row in weights
    ):
        raise ValueError(
            "F1 weight matrix must be square"
        )

    rational_weights = tuple(
        tuple(
            sp.Rational(value)
            for value in row
        )
        for row in weights
    )

    for row in range(order):
        if rational_weights[row][row] != 0:
            raise ValueError(
                "F1 weight diagonal must be zero"
            )

        for column in range(order):
            if rational_weights[row][column] < 0:
                raise ValueError(
                    "F1 proximity weights must be non-negative"
                )

            if (
                rational_weights[row][column]
                != rational_weights[column][row]
            ):
                raise ValueError(
                    "F1 proximity weights must be symmetric"
                )

    matrix = sp.zeros(
        order,
        order,
    )

    for row in range(order):
        normalization = (
            sp.Rational(1)
            + sum(
                rational_weights[row],
                sp.Rational(0),
            )
        )

        matrix[row, row] = (
            sp.Rational(1)
            / normalization
        )

        for column in range(order):
            if row == column:
                continue

            matrix[row, column] = (
                rational_weights[row][column]
                / normalization
            )

    return matrix


def f1_operator_matrix(
    geometry: OrthogonalGeometry,
) -> sp.Matrix:
    current = _require_geometry(geometry)
    graph = f1.build_factor_proximity_graph(current)

    return f1_propagation_matrix_from_weights(
        graph.weights
    )


def f1_operator_profile(
    geometry: OrthogonalGeometry,
) -> OperatorProfile:
    current = _require_geometry(geometry)
    graph = f1.build_factor_proximity_graph(current)

    adjacency = tuple(
        tuple(
            (
                neighbor,
                weight,
            )
            for neighbor, weight in enumerate(row)
            if (
                neighbor != vertex
                and weight != 0
            )
        )
        for vertex, row in enumerate(graph.weights)
    )

    return _operator_profile_from_adjacency(
        adjacency
    )


def f1_intrinsic_state_signature(
    geometry: OrthogonalGeometry,
) -> tuple[
    tuple[RationalPair, ...],
    ...,
]:
    current = _require_geometry(geometry)
    graph = f1.build_factor_proximity_graph(current)

    serialized = tuple(
        tuple(
            canonical_rational(value)
            for value in factor_state
        )
        for factor_state in graph.initial_state
    )

    return tuple(sorted(serialized))


def l1_operator_matrix(
    geometry: OrthogonalGeometry,
) -> sp.Matrix:
    """Direct exact L1 matrix, retained for small verification controls."""

    current = _require_geometry(geometry)

    graph = l1.build_full_lattice_graph(
        current,
        coupled=True,
    )

    matrix = sp.zeros(
        len(graph.cells),
        len(graph.cells),
    )

    for vertex, neighbors in enumerate(
        graph.adjacency
    ):
        weighted_degree = sum(
            weight
            for _neighbor, weight in neighbors
        )

        matrix[vertex, vertex] = weighted_degree

        for neighbor, weight in neighbors:
            matrix[vertex, neighbor] = -weight

    return matrix


def l1_operator_profile(
    geometry: OrthogonalGeometry,
) -> OperatorProfile:
    current = _require_geometry(geometry)

    graph = l1.build_full_lattice_graph(
        current,
        coupled=True,
    )

    return _operator_profile_from_adjacency(
        graph.adjacency
    )


def l1_intrinsic_state_signature(
    geometry: OrthogonalGeometry,
) -> tuple[RationalPair, ...]:
    current = _require_geometry(geometry)

    graph = l1.build_full_lattice_graph(
        current,
        coupled=True,
    )

    return _sorted_rationals(
        tuple(graph.initial_state)
    )


def _path_laplacian_matrix(
    order: int,
) -> sp.Matrix:
    if (
        type(order) is not int
        or order <= 0
    ):
        raise ValueError(
            "path order must be a positive integer"
        )

    matrix = sp.zeros(
        order,
        order,
    )

    for vertex in range(order):
        degree = 0

        if vertex > 0:
            matrix[vertex, vertex - 1] = -1
            degree += 1

        if vertex + 1 < order:
            matrix[vertex, vertex + 1] = -1
            degree += 1

        matrix[vertex, vertex] = degree

    return matrix


@lru_cache(maxsize=None)
def _path_charpoly_coefficients(
    order: int,
) -> tuple[int, ...]:
    matrix = _path_laplacian_matrix(order)

    coefficients = matrix.charpoly().all_coeffs()

    return tuple(
        int(coefficient)
        for coefficient in coefficients
    )


def _polynomial_expression(
    coefficients: tuple[int, ...],
    variable: sp.Symbol,
) -> sp.Expr:
    degree = len(coefficients) - 1

    return sp.Add(*(
        sp.Integer(coefficient)
        * variable ** (degree - index)
        for index, coefficient in enumerate(
            coefficients
        )
    ))


def rectangular_laplacian_matrix(
    width: int,
    height: int,
) -> sp.Matrix:
    """Construct a direct exact rectangular-grid Laplacian for controls."""

    if (
        type(width) is not int
        or type(height) is not int
        or width <= 0
        or height <= 0
    ):
        raise ValueError(
            "rectangle dimensions must be positive integers"
        )

    order = width * height

    matrix = sp.zeros(
        order,
        order,
    )

    def index(x: int, y: int) -> int:
        return x * height + y

    for x in range(width):
        for y in range(height):
            vertex = index(x, y)
            degree = 0

            for nx, ny in (
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
            ):
                if not (
                    0 <= nx < width
                    and 0 <= ny < height
                ):
                    continue

                neighbor = index(nx, ny)
                matrix[vertex, neighbor] = -1
                degree += 1

            matrix[vertex, vertex] = degree

    return matrix


@lru_cache(maxsize=None)
def _l1_resultant_signature_cached(
    width: int,
    height: int,
) -> PolynomialSignature:
    x = sp.Symbol("x")
    y = sp.Symbol("y")

    width_coefficients = (
        _path_charpoly_coefficients(width)
    )

    height_coefficients = (
        _path_charpoly_coefficients(height)
    )

    width_polynomial = _polynomial_expression(
        width_coefficients,
        y,
    )

    height_degree = (
        len(height_coefficients) - 1
    )

    shifted_height_polynomial = sp.Add(*(
        sp.Integer(coefficient)
        * (x - y) ** (
            height_degree - index
        )
        for index, coefficient in enumerate(
            height_coefficients
        )
    ))

    resultant = sp.resultant(
        width_polynomial,
        shifted_height_polynomial,
        y,
    )

    polynomial = sp.Poly(
        resultant,
        x,
        domain=sp.QQ,
    ).monic()

    expected_degree = width * height

    if polynomial.degree() != expected_degree:
        raise RuntimeError(
            "L1 resultant degree does not equal rectangle order"
        )

    coefficients = tuple(
        canonical_rational(coefficient)
        for coefficient in polynomial.all_coeffs()
    )

    if coefficients[0] != (1, 1):
        raise RuntimeError(
            "L1 resultant characteristic polynomial must be monic"
        )

    return coefficients


def l1_resultant_spectrum_signature(
    width: int,
    height: int,
) -> PolynomialSignature:
    """Return the exact rectangular-grid spectrum via path resultant."""

    if (
        type(width) is not int
        or type(height) is not int
        or width <= 0
        or height <= 0
    ):
        raise ValueError(
            "rectangle dimensions must be positive integers"
        )

    first, second = sorted(
        (width, height)
    )

    return _l1_resultant_signature_cached(
        first,
        second,
    )


def l1_rectangle_dimensions(
    geometry: OrthogonalGeometry,
) -> tuple[int, int]:
    current = _require_geometry(geometry)

    graph = l1.build_full_lattice_graph(
        current,
        coupled=True,
    )

    if not graph.cells:
        raise RuntimeError(
            "frozen L1 lattice must not be empty"
        )

    xs = {
        x
        for x, _y in graph.cells
    }

    ys = {
        y
        for _x, y in graph.cells
    }

    width = len(xs)
    height = len(ys)

    if width * height != len(graph.cells):
        raise RuntimeError(
            "frozen L1 domain is not a complete rectangle"
        )

    return width, height


def operator_elementary_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> OperatorProfile:
    current_substrate = _require_substrate(
        substrate
    )

    if current_substrate == "B0":
        return b0_operator_profile(geometry)

    if current_substrate == "D1":
        return d1_operator_profile(geometry)

    if current_substrate == "F1":
        return f1_operator_profile(geometry)

    return l1_operator_profile(geometry)


def intrinsic_state_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> object | None:
    current_substrate = _require_substrate(
        substrate
    )

    if current_substrate in {
        "B0",
        "D1",
    }:
        return None

    if current_substrate == "F1":
        return f1_intrinsic_state_signature(
            geometry
        )

    return l1_intrinsic_state_signature(
        geometry
    )


def exact_operator_spectrum_signature(
    substrate: str,
    geometry: OrthogonalGeometry,
) -> PolynomialSignature:
    current_substrate = _require_substrate(
        substrate
    )

    if current_substrate == "B0":
        return characteristic_polynomial_signature(
            b0_operator_matrix(geometry)
        )

    if current_substrate == "D1":
        return characteristic_polynomial_signature(
            d1_operator_matrix(geometry)
        )

    if current_substrate == "F1":
        return characteristic_polynomial_signature(
            f1_operator_matrix(geometry)
        )

    width, height = l1_rectangle_dimensions(
        geometry
    )

    return l1_resultant_spectrum_signature(
        width,
        height,
    )


__all__ = [
    "PROTOCOL_ID",
    "SUBSTRATES",
    "b0_operator_matrix",
    "b0_operator_profile",
    "canonical_rational",
    "characteristic_polynomial_signature",
    "d1_operator_matrix",
    "d1_operator_profile",
    "exact_operator_spectrum_signature",
    "f1_intrinsic_state_signature",
    "f1_operator_matrix",
    "f1_operator_profile",
    "f1_propagation_matrix_from_weights",
    "intrinsic_state_signature",
    "l1_intrinsic_state_signature",
    "l1_operator_matrix",
    "l1_operator_profile",
    "l1_rectangle_dimensions",
    "l1_resultant_spectrum_signature",
    "operator_elementary_signature",
    "rectangular_laplacian_matrix",
    "signature_bytes",
]
