"""Native PETRA adapter for the PETRA VISION structural kernel."""

from __future__ import annotations

from ..model import (
    Container,
    Leaf,
    PetraShape,
    Root,
    Term,
    validate_shape,
)
from .kernel import (
    OrderedGroup,
    Terminal,
    VisionShape,
    validate_vision_shape,
)


def adapt_petra_shape(shape: PetraShape) -> VisionShape:
    """Project one canonical native PETRA shape into the VISION kernel."""

    validate_shape(shape)

    converted: dict[int, VisionShape] = {}
    pending: list[tuple[PetraShape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        current_id = id(current)

        if current_id in converted:
            continue

        if isinstance(current, Leaf):
            converted[current_id] = Terminal()
            continue

        if not expanded:
            pending.append((current, True))

            for term in reversed(current.terms):
                child = term.exponent
                if id(child) not in converted:
                    pending.append((child, False))

            continue

        converted[current_id] = OrderedGroup(
            children=tuple(
                converted[id(term.exponent)]
                for term in current.terms
            )
        )

    return converted[id(shape)]


def restore_petra_shape(shape: VisionShape) -> PetraShape:
    """Reconstruct one canonical native PETRA shape from the kernel."""

    validate_vision_shape(shape)

    converted: dict[int, PetraShape] = {}
    pending: list[tuple[VisionShape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        current_id = id(current)

        if current_id in converted:
            continue

        if isinstance(current, Terminal):
            converted[current_id] = Leaf()
            continue

        if not expanded:
            pending.append((current, True))

            for child in reversed(current.children):
                if id(child) not in converted:
                    pending.append((child, False))

            continue

        converted[current_id] = Container(
            terms=tuple(
                Term(
                    root=Root(rank),
                    exponent=converted[id(child)],
                )
                for rank, child in enumerate(current.children)
            )
        )

    restored = converted[id(shape)]
    validate_shape(restored)
    return restored


__all__ = [
    "adapt_petra_shape",
    "restore_petra_shape",
]
