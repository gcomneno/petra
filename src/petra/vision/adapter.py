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
    PHASE_1_MAX_ORDERED_GROUP_WIDTH,
    PHASE_1_MAX_STRUCTURAL_DEPTH,
    PHASE_1_MAX_TOTAL_NODES,
    Terminal,
    VisionShape,
    VISION_SHAPE_OUT_OF_BOUNDS,
    validate_vision_shape,
)


def adapt_petra_shape(shape: PetraShape) -> VisionShape:
    """Project one canonical native PETRA shape into the VISION kernel."""

    _strict_native_preflight(shape)

    # Native validation remains a compatibility check, but it is only safe
    # after the VISION boundary has established exact runtime types, acyclic
    # structure, and the shallow bounded domain.
    validate_shape(shape)

    converted: dict[int, VisionShape] = {}
    pending: list[tuple[PetraShape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        current_id = id(current)

        if current_id in converted:
            continue

        if type(current) is Leaf:
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

    projected = converted[id(shape)]
    validate_vision_shape(projected)
    return projected


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

        if type(current) is Terminal:
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


def _strict_native_preflight(shape: object) -> None:
    """Check the exact, bounded native subset before native recursion.

    This deliberately validates only facts required by the VISION adapter:
    native record types, container/term/root formation, positional ranks,
    acyclicity, and the documented Phase 1 structural domain. It does not
    widen into a second implementation of native PETRA semantics.
    """

    _require_exact_native_shape(shape)

    pending: list[tuple[PetraShape, int, bool]] = [
        (shape, 0, False)
    ]
    active: set[int] = set()
    node_count = 0

    while pending:
        current, depth, leaving = pending.pop()
        current_id = id(current)

        if leaving:
            active.remove(current_id)
            continue

        _require_exact_native_shape(current)

        if current_id in active:
            raise ValueError("PETRA shape must be acyclic")

        if depth > PHASE_1_MAX_STRUCTURAL_DEPTH:
            _raise_out_of_bounds()

        node_count += 1
        if node_count > PHASE_1_MAX_TOTAL_NODES:
            _raise_out_of_bounds()

        if type(current) is Leaf:
            continue

        if type(current.terms) is not tuple:
            raise TypeError("container terms must be an exact tuple")

        if not current.terms:
            raise ValueError("container terms must be non-empty")

        if len(current.terms) > PHASE_1_MAX_ORDERED_GROUP_WIDTH:
            _raise_out_of_bounds()

        active.add(current_id)
        pending.append((current, depth, True))

        for expected_rank, term in reversed(
            tuple(enumerate(current.terms))
        ):
            if type(term) is not Term:
                raise TypeError("container terms must contain exact Term values")

            if type(term.root) is not Root:
                raise TypeError("term root must be an exact Root")

            if type(term.root.rank) is not int:
                raise TypeError("root rank must be an exact int")

            if term.root.rank < 0:
                raise ValueError("root rank must be >= 0")

            if term.root.rank != expected_rank:
                raise ValueError(
                    "non-canonical root rank: "
                    f"expected r{expected_rank}, got r{term.root.rank}"
                )

            exponent = term.exponent
            _require_exact_native_shape(exponent)
            pending.append((exponent, depth + 1, False))


def _require_exact_native_shape(value: object) -> PetraShape:
    if type(value) not in (Leaf, Container):
        raise TypeError("expected an exact PETRA Leaf or Container")
    return value


def _raise_out_of_bounds() -> None:
    raise ValueError(VISION_SHAPE_OUT_OF_BOUNDS)


__all__ = [
    "adapt_petra_shape",
    "restore_petra_shape",
]
