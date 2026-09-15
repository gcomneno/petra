"""Human-readable mother notation for canonical PETRA shapes.

This module renders a canonical PETRA shape in the "mother notation":

    ○^A^A × B^B × C

- `○` is the mother (the root container). There is always exactly one.
- `^` relates a mother to its first father, or a father to its child.
- `×` separates sibling fathers inside the same container.
- `A`, `B`, `C`, ... are local labels assigned in order of appearance
  within each container. They are not values and not positions; they
  only distinguish siblings locally.

The notation is a presentation layer. It does not change canonical
PETRA semantics and does not participate in shape identity.
"""

from __future__ import annotations

from petra import Container, Leaf, PetraShape, validate_shape

__all__ = ["to_mother_notation"]

_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _label(index: int) -> str:
    """Return the i-th label (A, B, ..., Z, AA, AB, ...)."""

    n = index
    base = len(_LABELS)
    result = ""
    while True:
        result = _LABELS[n % base] + result
        n = n // base - 1
        if n < 0:
            break
    return result


def _render(shape: PetraShape) -> str:
    """Render a shape as the content of a container: siblings separated by ×.

    A leaf renders as the empty string (the neutral placeholder is
    implicit). A container renders as a chain of `^` between its first
    father and the rest.
    """

    if isinstance(shape, Leaf):
        return ""

    assert isinstance(shape, Container)
    parts: list[str] = []
    for i, term in enumerate(shape.terms):
        label = _label(i)
        inner = _render(term.exponent)
        if inner == "":
            parts.append(label)
        else:
            parts.append(f"{label}^{inner}")
    return " × ".join(parts)


def to_mother_notation(shape: PetraShape) -> str:
    """Return the mother notation of a canonical shape.

    The leaf renders as `○`. A non-trivial shape renders as `○^...` with
    its content rendered in the same notation, using local sibling
    labels.
    """

    validate_shape(shape)
    if isinstance(shape, Leaf):
        return "○"
    content = _render(shape)
    return f"○^{content}"
