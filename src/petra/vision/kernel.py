"""Minimal immutable structural kernel for PETRA VISION Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


PHASE_1_MAX_ORDERED_GROUP_WIDTH = 3
PHASE_1_MAX_STRUCTURAL_DEPTH = 3
PHASE_1_MAX_TOTAL_NODES = 7
VISION_SHAPE_OUT_OF_BOUNDS = (
    "VISION shape exceeds the Phase 1 structural bounds"
)


@dataclass(frozen=True)
class Terminal:
    """The unique terminal VISION kernel value."""


@dataclass(frozen=True)
class OrderedGroup:
    """A non-empty ordered sequence of complete VISION child shapes."""

    children: tuple["VisionShape", ...]

    def __post_init__(self) -> None:
        if not isinstance(self.children, tuple):
            raise TypeError("ordered group children must be a tuple")

        # A tuple subclass can override iteration or indexing after this
        # immutable record has been constructed. Snapshot it once at the
        # kernel boundary so later validation has a trusted exact tuple.
        children = (
            self.children
            if type(self.children) is tuple
            else tuple(self.children)
        )
        object.__setattr__(self, "children", children)

        if not children:
            raise ValueError("ordered group children must be non-empty")
        if not all(_is_vision_shape(child) for child in children):
            raise TypeError(
                "ordered group children must contain only "
                "Terminal or OrderedGroup values"
            )


VisionShape: TypeAlias = Terminal | OrderedGroup


def _is_vision_shape(value: object) -> bool:
    return type(value) in (Terminal, OrderedGroup)


def _require_vision_shape(value: object) -> VisionShape:
    if not _is_vision_shape(value):
        raise TypeError(
            "expected a VISION Terminal or OrderedGroup"
        )
    return value


def validate_vision_shape(shape: VisionShape) -> None:
    """Validate one bounded finite VISION kernel shape iteratively.

    The stable Phase 1 bounds failure is ``ValueError`` with
    ``VISION_SHAPE_OUT_OF_BOUNDS``. Node counting is by structural
    occurrence, so shared acyclic child objects count at every position.
    """

    root = _require_vision_shape(shape)

    pending: list[tuple[VisionShape, int, bool]] = [
        (root, 0, False)
    ]
    active: set[int] = set()
    node_count = 0

    while pending:
        current, depth, leaving = pending.pop()
        current_id = id(current)

        if leaving:
            active.remove(current_id)
            continue

        if current_id in active:
            raise ValueError("VISION shape must be acyclic")

        _require_vision_shape(current)

        if depth > PHASE_1_MAX_STRUCTURAL_DEPTH:
            _raise_out_of_bounds()

        node_count += 1
        if node_count > PHASE_1_MAX_TOTAL_NODES:
            _raise_out_of_bounds()

        if type(current) is Terminal:
            continue

        if type(current.children) is not tuple:
            raise TypeError(
                "ordered group children must be a tuple"
            )

        if not current.children:
            raise ValueError(
                "ordered group children must be non-empty"
            )

        if len(current.children) > PHASE_1_MAX_ORDERED_GROUP_WIDTH:
            _raise_out_of_bounds()

        active.add(current_id)
        pending.append((current, depth, True))

        for child in reversed(current.children):
            required_child = _require_vision_shape(child)
            pending.append((required_child, depth + 1, False))


def _raise_out_of_bounds() -> None:
    raise ValueError(VISION_SHAPE_OUT_OF_BOUNDS)


__all__ = [
    "OrderedGroup",
    "PHASE_1_MAX_ORDERED_GROUP_WIDTH",
    "PHASE_1_MAX_STRUCTURAL_DEPTH",
    "PHASE_1_MAX_TOTAL_NODES",
    "Terminal",
    "VisionShape",
    "VISION_SHAPE_OUT_OF_BOUNDS",
    "validate_vision_shape",
]
