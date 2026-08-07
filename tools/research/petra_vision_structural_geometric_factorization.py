"""Native geometry-only Structural Geometric Factorization research tool.

Gate 1B keeps this module deliberately independent from VisionShape,
decode_geometry, PETRA addresses, serialization, and structural metadata.
"""

from __future__ import annotations

from collections.abc import Iterable

from petra.vision.geometry import (
    OrthogonalGeometry,
    geometry_extent,
)


Cell = tuple[int, int]


class FGSGeometryError(ValueError):
    """Raised when geometry violates the native FGS contract."""


def _make_geometry(cells: Iterable[Cell]) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(set(cells))),
    )


def _require_canonical_geometry(
    value: object,
) -> OrthogonalGeometry:
    if type(value) is not OrthogonalGeometry:
        raise TypeError(
            "native FGS expects an exact OrthogonalGeometry"
        )

    geometry = value
    cells = geometry.cells

    if min(x for x, _ in cells) != 0:
        raise FGSGeometryError(
            "native FGS requires canonical minimum x = 0"
        )

    if min(y for _, y in cells) != 0:
        raise FGSGeometryError(
            "native FGS requires canonical minimum y = 0"
        )

    return geometry


def _frame_cells(
    width: int,
    height: int,
    boundaries: tuple[int, ...],
) -> set[Cell]:
    cells = {
        (x, 0)
        for x in range(width)
    }
    cells.update(
        (x, height - 1)
        for x in range(width)
    )

    for x in boundaries:
        cells.update(
            (x, y)
            for y in range(height)
        )

    return cells


def _full_height_columns(
    geometry: OrthogonalGeometry,
) -> tuple[int, ...]:
    width, height = geometry_extent(geometry)
    occupied = set(geometry.cells)

    return tuple(
        x
        for x in range(width)
        if all(
            (x, y) in occupied
            for y in range(height)
        )
    )


def _extract_factor(
    *,
    occupied: set[Cell],
    parent_height: int,
    left_boundary: int,
    right_boundary: int,
) -> OrthogonalGeometry:
    if right_boundary - left_boundary < 4:
        raise FGSGeometryError("FGS bay is too narrow")

    payload = {
        (x, y)
        for x, y in occupied
        if (
            left_boundary < x < right_boundary
            and 0 < y < parent_height - 1
        )
    }

    if not payload:
        raise FGSGeometryError("FGS bay has no factor payload")

    if any(
        x in (
            left_boundary + 1,
            right_boundary - 1,
        )
        for x, _ in payload
    ):
        raise FGSGeometryError(
            "FGS factor violates horizontal clearance"
        )

    if any(
        y in (1, parent_height - 2)
        for _, y in payload
    ):
        raise FGSGeometryError(
            "FGS factor violates vertical clearance"
        )

    minimum_x = min(x for x, _ in payload)
    maximum_x = max(x for x, _ in payload)
    minimum_y = min(y for _, y in payload)
    maximum_y = max(y for _, y in payload)

    if minimum_x != left_boundary + 2:
        raise FGSGeometryError(
            "FGS factor has invalid left alignment"
        )

    if maximum_x != right_boundary - 2:
        raise FGSGeometryError(
            "FGS factor has invalid right alignment"
        )

    if maximum_y != parent_height - 3:
        raise FGSGeometryError(
            "FGS factor has invalid top alignment"
        )

    if minimum_y < 2:
        raise FGSGeometryError(
            "FGS factor has invalid bottom clearance"
        )

    return _make_geometry(
        (
            x - minimum_x,
            y - minimum_y,
        )
        for x, y in payload
    )


def native_fgs(
    geometry: OrthogonalGeometry,
) -> tuple[OrthogonalGeometry, ...]:
    """Extract immediate ordered factor geometries from geometry alone."""

    current = _require_canonical_geometry(geometry)

    if current.cells == ((0, 0),):
        return ()

    width, height = geometry_extent(current)

    if width < 5 or height < 5:
        raise FGSGeometryError(
            "non-terminal FGS geometry is smaller than one frame"
        )

    occupied = set(current.cells)

    perimeter = (
        {(x, 0) for x in range(width)}
        | {(x, height - 1) for x in range(width)}
        | {(0, y) for y in range(height)}
        | {(width - 1, y) for y in range(height)}
    )

    if not perimeter.issubset(occupied):
        raise FGSGeometryError(
            "FGS parent outer frame is incomplete"
        )

    boundaries = _full_height_columns(current)

    if (
        len(boundaries) < 2
        or boundaries[0] != 0
        or boundaries[-1] != width - 1
    ):
        raise FGSGeometryError(
            "FGS parent boundaries are not canonical"
        )

    factors = tuple(
        _extract_factor(
            occupied=occupied,
            parent_height=height,
            left_boundary=left,
            right_boundary=right,
        )
        for left, right in zip(
            boundaries,
            boundaries[1:],
        )
    )

    scaffold = _frame_cells(
        width,
        height,
        boundaries,
    )

    factor_placements: list[set[Cell]] = []
    left_boundary = 0

    for factor in factors:
        factor_width, factor_height = geometry_extent(factor)

        offset_x = left_boundary + 2
        offset_y = height - factor_height - 2

        placed = {
            (offset_x + x, offset_y + y)
            for x, y in factor.cells
        }

        factor_placements.append(placed)
        left_boundary = left_boundary + factor_width + 3

    owned = set(scaffold)

    for placed in factor_placements:
        if owned & placed:
            raise FGSGeometryError(
                "FGS scaffold and factor ownership overlap"
            )

        owned.update(placed)

    if owned != occupied:
        raise FGSGeometryError(
            "FGS ownership does not cover source geometry exactly"
        )

    if recompose_fgs(factors) != current:
        raise FGSGeometryError(
            "FGS factors do not exactly recompose source geometry"
        )

    return factors


def recompose_fgs(
    factors: tuple[OrthogonalGeometry, ...],
) -> OrthogonalGeometry:
    """Recompose one canonical geometry from ordered factor geometries."""

    if type(factors) is not tuple:
        raise TypeError(
            "FGS factors must be an exact tuple"
        )

    if not factors:
        return OrthogonalGeometry(
            cells=((0, 0),)
        )

    trusted: list[OrthogonalGeometry] = []

    for factor in factors:
        trusted.append(
            _require_canonical_geometry(factor)
        )

    extents = tuple(
        geometry_extent(factor)
        for factor in trusted
    )

    parent_height = (
        max(
            height
            for _, height in extents
        )
        + 4
    )

    cells: set[Cell] = set()
    left_boundary = 0

    cells.update(
        (left_boundary, y)
        for y in range(parent_height)
    )

    for factor, (factor_width, factor_height) in zip(
        trusted,
        extents,
    ):
        right_boundary = (
            left_boundary
            + factor_width
            + 3
        )

        cells.update(
            (x, 0)
            for x in range(
                left_boundary,
                right_boundary + 1,
            )
        )
        cells.update(
            (x, parent_height - 1)
            for x in range(
                left_boundary,
                right_boundary + 1,
            )
        )
        cells.update(
            (right_boundary, y)
            for y in range(parent_height)
        )

        offset_x = left_boundary + 2
        offset_y = (
            parent_height
            - factor_height
            - 2
        )

        cells.update(
            (
                offset_x + x,
                offset_y + y,
            )
            for x, y in factor.cells
        )

        left_boundary = right_boundary

    return _make_geometry(cells)


__all__ = [
    "FGSGeometryError",
    "native_fgs",
    "recompose_fgs",
]
