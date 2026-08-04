"""Canonical orthogonal geometry for PETRA VISION Phase 1."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import NoReturn, TypeAlias

from .kernel import (
    OrderedGroup,
    Terminal,
    VisionShape,
    validate_vision_shape,
)


Cell: TypeAlias = tuple[int, int]

GEOMETRY_MALFORMED = (
    "geometry does not match the Phase 1 canonical grammar"
)
PHASE_1_MAX_GEOMETRY_CELLS = 181
PHASE_1_MAX_GEOMETRY_WIDTH = 25
PHASE_1_MAX_GEOMETRY_HEIGHT = 13
PHASE_1_MAX_COORDINATE_MAGNITUDE = (1 << 63) - 1


class GeometrySyntaxError(ValueError):
    """Raised when geometry cannot be decoded unambiguously."""


@dataclass(frozen=True)
class OrthogonalGeometry:
    """One deterministic record of occupied integer-lattice cells."""

    cells: tuple[Cell, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.cells, tuple):
            raise TypeError("geometry cells must be a tuple")

        # Snapshot tuple subclasses at the public representation boundary.
        # They can otherwise make later iteration depend on external mutable
        # state despite this frozen dataclass.
        source_cells = (
            self.cells
            if type(self.cells) is tuple
            else tuple(self.cells)
        )
        trusted_cells: list[Cell] = []

        for cell in source_cells:
            if not isinstance(cell, tuple):
                raise TypeError(
                    "every geometry cell must be an (x, y) tuple"
                )

            trusted_cell = (
                cell
                if type(cell) is tuple
                else tuple(cell)
            )

            if len(trusted_cell) != 2:
                raise TypeError(
                    "every geometry cell must be an (x, y) tuple"
                )

            x, y = trusted_cell
            if type(x) is not int or type(y) is not int:
                raise TypeError(
                    "geometry coordinates must be exact integers"
                )

            trusted_cells.append((x, y))

        cells = tuple(trusted_cells)
        object.__setattr__(self, "cells", cells)

        if not cells:
            raise ValueError("geometry cells must be non-empty")

        if tuple(sorted(cells)) != cells:
            raise ValueError(
                "geometry cells must use canonical coordinate order"
            )

        if len(set(cells)) != len(cells):
            raise ValueError("geometry cells must not contain duplicates")


def _require_geometry(value: object) -> OrthogonalGeometry:
    if type(value) is not OrthogonalGeometry:
        raise TypeError("expected an OrthogonalGeometry")

    return value


def _make_geometry(cells: Iterable[Cell]) -> OrthogonalGeometry:
    return OrthogonalGeometry(
        cells=tuple(sorted(set(cells))),
    )


def normalize_geometry(
    geometry: OrthogonalGeometry,
) -> OrthogonalGeometry:
    """Translate geometry so that both minimum coordinates are zero."""

    current = _require_geometry(geometry)
    cells = _trusted_geometry_cells(current)

    minimum_x = min(x for x, _ in cells)
    minimum_y = min(y for _, y in cells)

    if minimum_x == 0 and minimum_y == 0:
        return current

    return _make_geometry(
        (x - minimum_x, y - minimum_y)
        for x, y in cells
    )


def geometry_extent(
    geometry: OrthogonalGeometry,
) -> tuple[int, int]:
    """Return the width and height of one geometry bounding box."""

    current = _require_geometry(geometry)
    cells = _trusted_geometry_cells(current)

    minimum_x = min(x for x, _ in cells)
    maximum_x = max(x for x, _ in cells)
    minimum_y = min(y for _, y in cells)
    maximum_y = max(y for _, y in cells)

    return (
        maximum_x - minimum_x + 1,
        maximum_y - minimum_y + 1,
    )


def encode_geometry(shape: VisionShape) -> OrthogonalGeometry:
    """Encode one valid VISION kernel shape as canonical geometry."""

    validate_vision_shape(shape)
    return _encode_valid_shape(shape)


def _encode_valid_shape(shape: VisionShape) -> OrthogonalGeometry:
    if isinstance(shape, Terminal):
        return _make_geometry(((0, 0),))

    child_geometries = tuple(
        _encode_valid_shape(child)
        for child in shape.children
    )

    child_extents = tuple(
        geometry_extent(child)
        for child in child_geometries
    )

    maximum_child_height = max(
        height
        for _, height in child_extents
    )

    container_height = maximum_child_height + 4

    cells: set[Cell] = set()
    left_boundary = 0

    cells.update(
        (left_boundary, y)
        for y in range(container_height)
    )

    for child, (child_width, child_height) in zip(
        child_geometries,
        child_extents,
    ):
        right_boundary = left_boundary + child_width + 3

        cells.update(
            (x, 0)
            for x in range(
                left_boundary,
                right_boundary + 1,
            )
        )

        cells.update(
            (x, container_height - 1)
            for x in range(
                left_boundary,
                right_boundary + 1,
            )
        )

        cells.update(
            (right_boundary, y)
            for y in range(container_height)
        )

        child_offset_x = left_boundary + 2
        child_offset_y = (
            container_height
            - child_height
            - 2
        )

        cells.update(
            (
                child_offset_x + x,
                child_offset_y + y,
            )
            for x, y in child.cells
        )

        left_boundary = right_boundary

    return _make_geometry(cells)


def decode_geometry(
    geometry: OrthogonalGeometry,
) -> VisionShape:
    """Decode geometry after canonical translation normalisation."""

    current = _require_geometry(geometry)

    try:
        cells = _trusted_geometry_cells(
            current,
            enforce_decoder_budgets=True,
        )
    except (TypeError, ValueError) as error:
        _reject(str(error))

    minimum_x = min(x for x, _ in cells)
    minimum_y = min(y for _, y in cells)
    normalized = (
        current
        if minimum_x == 0 and minimum_y == 0
        else _make_geometry(
            (x - minimum_x, y - minimum_y)
            for x, y in cells
        )
    )

    return _decode_normalized_geometry(normalized)


def _trusted_geometry_cells(
    geometry: OrthogonalGeometry,
    *,
    enforce_decoder_budgets: bool = False,
) -> tuple[Cell, ...]:
    """Recheck a record after construction or hostile attribute mutation."""

    cells = geometry.cells

    if type(cells) is not tuple:
        raise TypeError("geometry cells must be an exact tuple")

    if not cells:
        raise ValueError("geometry cells must be non-empty")

    if enforce_decoder_budgets and len(cells) > PHASE_1_MAX_GEOMETRY_CELLS:
        raise ValueError("geometry exceeds the Phase 1 cell budget")

    for cell in cells:
        if type(cell) is not tuple or len(cell) != 2:
            raise TypeError(
                "every geometry cell must be an exact (x, y) tuple"
            )

        x, y = cell
        if type(x) is not int or type(y) is not int:
            raise TypeError("geometry coordinates must be exact integers")

        if enforce_decoder_budgets and (
            x > PHASE_1_MAX_COORDINATE_MAGNITUDE
            or x < -PHASE_1_MAX_COORDINATE_MAGNITUDE
            or y > PHASE_1_MAX_COORDINATE_MAGNITUDE
            or y < -PHASE_1_MAX_COORDINATE_MAGNITUDE
        ):
            raise ValueError(
                "geometry coordinates exceed the Phase 1 resource limit"
            )

    if tuple(sorted(cells)) != cells:
        raise ValueError("geometry cells must use canonical coordinate order")

    if len(set(cells)) != len(cells):
        raise ValueError("geometry cells must not contain duplicates")

    if enforce_decoder_budgets:
        minimum_x = min(x for x, _ in cells)
        maximum_x = max(x for x, _ in cells)
        minimum_y = min(y for _, y in cells)
        maximum_y = max(y for _, y in cells)
        width = maximum_x - minimum_x + 1
        height = maximum_y - minimum_y + 1

        if width > PHASE_1_MAX_GEOMETRY_WIDTH:
            raise ValueError("geometry exceeds the Phase 1 width budget")

        if height > PHASE_1_MAX_GEOMETRY_HEIGHT:
            raise ValueError("geometry exceeds the Phase 1 height budget")

    return cells


def _decode_normalized_geometry(
    geometry: OrthogonalGeometry,
) -> VisionShape:
    cells = set(geometry.cells)

    if cells == {(0, 0)}:
        return Terminal()

    width, height = geometry_extent(geometry)

    if width < 5 or height < 5:
        _reject("non-terminal geometry is smaller than one frame")

    perimeter = (
        {(x, 0) for x in range(width)}
        | {(x, height - 1) for x in range(width)}
        | {(0, y) for y in range(height)}
        | {(width - 1, y) for y in range(height)}
    )

    if not perimeter.issubset(cells):
        _reject("outer frame is incomplete")

    full_height_columns = tuple(
        x
        for x in range(width)
        if all(
            (x, y) in cells
            for y in range(height)
        )
    )

    if (
        len(full_height_columns) < 2
        or full_height_columns[0] != 0
        or full_height_columns[-1] != width - 1
    ):
        _reject("frame boundaries are not canonical")

    decoded_children: list[VisionShape] = []

    for left_boundary, right_boundary in zip(
        full_height_columns,
        full_height_columns[1:],
    ):
        if right_boundary - left_boundary < 4:
            _reject("bay is too narrow")

        interior_cells = {
            (x, y)
            for x, y in cells
            if (
                left_boundary < x < right_boundary
                and 0 < y < height - 1
            )
        }

        if not interior_cells:
            _reject("bay contains no child geometry")

        if any(
            x in (
                left_boundary + 1,
                right_boundary - 1,
            )
            for x, _ in interior_cells
        ):
            _reject("horizontal child clearance is not canonical")

        if any(
            y in (1, height - 2)
            for _, y in interior_cells
        ):
            _reject("vertical child clearance is not canonical")

        minimum_x = min(x for x, _ in interior_cells)
        maximum_x = max(x for x, _ in interior_cells)
        minimum_y = min(y for _, y in interior_cells)
        maximum_y = max(y for _, y in interior_cells)

        if (
            minimum_x != left_boundary + 2
            or maximum_x != right_boundary - 2
        ):
            _reject("child width or horizontal alignment is invalid")

        if maximum_y != height - 3:
            _reject("child top alignment is invalid")

        if minimum_y < 2:
            _reject("child bottom clearance is invalid")

        child_geometry = _make_geometry(
            (
                x - minimum_x,
                y - minimum_y,
            )
            for x, y in interior_cells
        )

        decoded_children.append(
            _decode_normalized_geometry(child_geometry)
        )

    decoded = OrderedGroup(
        children=tuple(decoded_children),
    )

    try:
        validate_vision_shape(decoded)
    except (TypeError, ValueError) as error:
        _reject(str(error))

    if _encode_valid_shape(decoded) != geometry:
        _reject("geometry is not the canonical encoding of its shape")

    return decoded


def _reject(detail: str) -> NoReturn:
    raise GeometrySyntaxError(
        f"{GEOMETRY_MALFORMED}: {detail}"
    )


__all__ = [
    "Cell",
    "GEOMETRY_MALFORMED",
    "GeometrySyntaxError",
    "OrthogonalGeometry",
    "PHASE_1_MAX_COORDINATE_MAGNITUDE",
    "PHASE_1_MAX_GEOMETRY_CELLS",
    "PHASE_1_MAX_GEOMETRY_HEIGHT",
    "PHASE_1_MAX_GEOMETRY_WIDTH",
    "decode_geometry",
    "encode_geometry",
    "geometry_extent",
    "normalize_geometry",
]
