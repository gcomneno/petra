"""Structural metrics on canonical PETRA shapes.

This module exposes structural measurements defined directly on the
canonical PETRA model. Metrics here observe objects, not values.

The only metric currently admitted is `node_count`, defined in SPEC
section 1.5.1 as the number of `Leaf`, `Container`, and `Term` objects
in a shape. `Root` is owned by a `Term` and is not counted separately.

The function is iterative to avoid Python call-stack limits on deep
shapes; it mirrors the depth and node-count budgets enforced by the
serializer.
"""

from __future__ import annotations

from .model import Container, Leaf, PetraShape, validate_shape

__all__ = ["node_count"]


def node_count(shape: PetraShape) -> int:
    """Return the total number of model nodes in a canonical shape.

    A model node is one `Leaf`, one `Container`, or one `Term`. The
    `Root` owned by a term is not counted separately.

    The input is validated as a canonical shape before counting.
    """

    validate_shape(shape)

    total = 0
    stack: list[PetraShape] = [shape]
    while stack:
        current = stack.pop()
        if isinstance(current, Leaf):
            total += 1
            continue
        assert isinstance(current, Container)
        total += 1  # the container itself
        for term in current.terms:
            total += 1  # the term
            stack.append(term.exponent)
    return total
