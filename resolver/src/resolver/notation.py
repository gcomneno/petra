"""Human-readable mother notation for canonical PETRA shapes.

The mother notation renders a canonical PETRA shape as a tree:

    ○^(A × B^(C^(D)) × E)

- `○` is the mother: the bare leaf, always the root placeholder.
- `(...)` is a container.
- Inside a container, `×` separates sibling fathers.
- Each father is labelled `A`, `B`, `C`, ... in order of appearance,
  locally within its container. Labels are not values and are not
  persistent identities.
- A father written as `A` has an implicit leaf as exponent.
- A father written as `A^(...)` has a container as exponent.

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


def _render_container(shape: Container) -> str:
    """Render the content of a container: fathers separated by ×."""

    parts: list[str] = []
    for i, term in enumerate(shape.terms):
        label = _label(i)
        exp = term.exponent
        if isinstance(exp, Leaf):
            parts.append(label)
        else:
            parts.append(f"{label}^({_render_container(exp)})")
    return " × ".join(parts)


def to_mother_notation(shape: PetraShape) -> str:
    """Return the mother notation of a canonical shape."""

    validate_shape(shape)
    if isinstance(shape, Leaf):
        return "○"
    return f"○^({_render_container(shape)})"
