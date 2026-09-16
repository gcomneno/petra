# struct/destruct on shape(k^n) (T01)

Status: research note (bounded empirical)
Scope: use struct/destruct to explore shape(k^n)
Stability: one limit of struct, one verification of the duplication
           lemma; no new theorem
Thread: T01

## Context

The exact identity `shape(k^n) = C(r0^shape(e1*n), ...)` is proven
(`exponential-base-structural-class.md`). T01 asks whether
`struct`/`destruct` can be used to explore the exponential case.

## Method

For small `k` and `n`, `destruct(shape(k^n))` is computed, and each
result `(piece, rest, kind)` is tested by checking whether
`shape(k^n) in struct(rest, piece)`.

## Result 1 — struct/destruct work on shape(k^n) with one known exception

For `12^3`, `30^2`, `30^3`, `6^4`, almost every destruct case is
recomposed by struct. The exceptions occur when the detached piece is
a father of an **inner** container, not of the root.

Example for `12^3 = 1728`, `shape = ○^(A^(A × B) × B^(A))`:

- `[father] piece = ○, rest = ○^(A^(A) × B^(A))` is not recomposed by
  `struct(rest, ○)`.

The reason is that `struct` adds fathers only at the root (via append
or prepend), or replaces a leaf with a container. It does not add a
father to an inner container. This is a limit of `struct`, not of
`destruct`.

## Result 2 — verification of the duplication lemma

`30^2` and `30^3` have the same shape, `○^(A^(A) × B^(A) × C^(A))`.
The reason is that `shape(2) = shape(3) = ○^(A)`, and by the exact
identity:

    shape(30^n) = C(r0^shape(n), r1^shape(n), r2^shape(n)).

Both `n = 2` and `n = 3` give the same result. This is a concrete
instance of the duplication lemma (`{a, a, ...} ≡ {a}`), not a new
result.

## Boundary

This note does not claim:

- that `struct` covers all inverses of `destruct` (it does not);
- that the limit generalizes to all shapes (tested on four pairs);
- that the exponent case gives new structural results beyond the
  duplication lemma.

## Reproducibility

`tools/research/t01_exponential_struct_destruct.py` with defaults
reproduces the four pairs.

## Status

T01 closed. The exponential case is explored; the tools work with one
known limit, and the duplication lemma is verified.
