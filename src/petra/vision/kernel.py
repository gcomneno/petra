"""Minimal immutable structural kernel for PETRA VISION Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


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
        if not self.children:
            raise ValueError("ordered group children must be non-empty")
        if not all(_is_vision_shape(child) for child in self.children):
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
    """Validate one finite immutable VISION kernel shape iteratively."""

    root = _require_vision_shape(shape)

    pending: list[tuple[VisionShape, bool]] = [
        (root, False)
    ]
    active: set[int] = set()
    validated: set[int] = set()

    while pending:
        current, expanded = pending.pop()
        current_id = id(current)

        if current_id in validated:
            continue

        if expanded:
            active.remove(current_id)
            validated.add(current_id)
            continue

        if current_id in active:
            raise ValueError("VISION shape must be acyclic")

        active.add(current_id)
        pending.append((current, True))

        if isinstance(current, Terminal):
            continue

        if not isinstance(current.children, tuple):
            raise TypeError(
                "ordered group children must be a tuple"
            )

        if not current.children:
            raise ValueError(
                "ordered group children must be non-empty"
            )

        for child in reversed(current.children):
            required_child = _require_vision_shape(child)
            child_id = id(required_child)

            if child_id in active:
                raise ValueError("VISION shape must be acyclic")

            if child_id not in validated:
                pending.append((required_child, False))


__all__ = [
    "OrderedGroup",
    "Terminal",
    "VisionShape",
    "validate_vision_shape",
]
