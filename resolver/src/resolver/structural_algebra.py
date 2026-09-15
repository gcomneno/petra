"""Structural algebra on PETRA shapes: meet, join, contains.

This module is a derived layer on top of the canonical PETRA runtime.
It defines three binary operations that do not appear in the canonical
specification:

- contains(a, b): a is positionally contained in b;
- meet(a, b): the largest shape contained in both a and b;
- join(a, b): the smallest shape containing both a and b;
- structural_overlap(a, b): a similarity measure in [0, 1].

"Contained" is defined positionally: a shape s is contained in a shape
t if s can be obtained from t by recursively truncating the term
sequences. This is a structural relation, not an arithmetic one:
meet of two integer shapes is not the shape of their gcd.

The operators are analytic: they consume two shapes and produce a third.
They do not modify an existing shape and do not participate in the
canonical operator vocabulary (SPROUT, SHED, GRAFT, PRUNE).
"""

from __future__ import annotations

from petra import Container, Leaf, PetraShape, Root, Term, node_count


def contains(a: PetraShape, b: PetraShape) -> bool:
    """Return True if a is positionally contained in b."""

    if isinstance(a, Leaf):
        return True
    if isinstance(b, Leaf):
        return False

    assert isinstance(a, Container) and isinstance(b, Container)
    if len(a.terms) > len(b.terms):
        return False
    for ta, tb in zip(a.terms, b.terms):
        if not contains(ta.exponent, tb.exponent):
            return False
    return True


def meet(a: PetraShape, b: PetraShape) -> PetraShape:
    """Return the largest shape positionally contained in both a and b."""

    if isinstance(a, Leaf) or isinstance(b, Leaf):
        return Leaf()

    assert isinstance(a, Container) and isinstance(b, Container)
    k = min(len(a.terms), len(b.terms))
    new_terms = []
    for i in range(k):
        ea = a.terms[i].exponent
        eb = b.terms[i].exponent
        new_terms.append(Term(root=Root(i), exponent=meet(ea, eb)))
    return Container(terms=tuple(new_terms))


def join(a: PetraShape, b: PetraShape) -> PetraShape:
    """Return the smallest shape positionally containing both a and b."""

    if isinstance(a, Leaf):
        return b
    if isinstance(b, Leaf):
        return a

    assert isinstance(a, Container) and isinstance(b, Container)
    k = max(len(a.terms), len(b.terms))
    new_terms = []
    for i in range(k):
        if i >= len(a.terms):
            exp = b.terms[i].exponent
        elif i >= len(b.terms):
            exp = a.terms[i].exponent
        else:
            exp = join(a.terms[i].exponent, b.terms[i].exponent)
        new_terms.append(Term(root=Root(i), exponent=exp))
    return Container(terms=tuple(new_terms))


def structural_overlap(a: PetraShape, b: PetraShape) -> float:
    """Return a similarity in [0, 1] from node_count(meet) / node_count(join)."""

    m = meet(a, b)
    j = join(a, b)
    return node_count(m) / node_count(j)

