# PET notation and collapse semantics

This document defines compact first-principles notation for PET objects.

> **Projection boundary.** Its prime-root notation and numeric collapse remain
> useful for canonical numeric display. They are not the normative structural
> identity, address, or operator contract for object-native PET/PEG 2.0
> rewrites; see
> [`pet-peg-2.0-object-native-operators.md`](pet-peg-2.0-object-native-operators.md).

It bridges the seed idea in `pet-first-principles.md` and the concrete examples
in `pet-first-principles-examples.md`.

The goal is conceptual precision, not new implementation behavior.

## Scope

This document defines:

- PET object notation
- the leaf object
- canonical `PET(n)` when prime-exponent structure is known
- numeric collapse
- current-level support
- height intuition
- numeric equality vs structural equality
- the construction boundary

It does not define:

- a new algorithm
- a CLI behavior
- a routing policy
- an anchor-selection policy
- a performance claim

## PET object syntax

A first-principles PET object is either:

    1

or a finite product of prime-root terms:

    p_1^E_1 * p_2^E_2 * ... * p_k^E_k

where:

- each `p_i` is a prime root
- each `E_i` is itself a PET object
- the current-level prime roots are distinct
- display order is canonical when roots are sorted increasingly

The expression is recursive because exponents are PET objects, not plain integer
labels.

## Leaf object

The minimal PET object is:

    1

This is the leaf object.

It terminates recursive exponent structure.

It is a modeling base object, not a claim that `1` is prime.

## Canonical PET(n)

`PET(n)` means the canonical PET object for the positive integer `n`, assuming
the prime-exponent structure of `n` is already known.

For `n = 1`:

    PET(1) = 1

For `n > 1`, if the classical factorization is:

    n = p_1^e_1 * p_2^e_2 * ... * p_k^e_k

then the canonical PET object is:

    PET(n) = p_1^PET(e_1) * p_2^PET(e_2) * ... * p_k^PET(e_k)

This definition is recursive because every exponent `e_i` is represented by
its own canonical PET object.

## Construction boundary

`PET(n)` is notation for a canonical object once the prime-exponent structure
of `n` is known.

If `n` is given as an opaque integer, constructing `PET(n)` requires knowing or
recovering that prime-exponent structure.

Therefore PET notation must not hide factorization cost inside the
representation step.

This boundary is part of the definition.

## Collapse

`collapse(P)` evaluates a PET object back to its ordinary numeric value.

For the leaf object:

    collapse(1) = 1

For a compound PET object:

    P = p_1^E_1 * p_2^E_2 * ... * p_k^E_k

the collapse is:

    collapse(P) =
        p_1^collapse(E_1) *
        p_2^collapse(E_2) *
        ... *
        p_k^collapse(E_k)

So collapse recursively evaluates exponent objects before evaluating the
current-level prime-root product.

## Collapse examples

For:

    PET(4) = 2^PET(2)
           = 2^(2^1)

collapse gives:

    collapse(PET(4))
      = collapse(2^PET(2))
      = 2^collapse(PET(2))
      = 2^2
      = 4

For:

    PET(360) = 2^PET(3) * 3^PET(2) * 5^PET(1)
             = 2^(3^1) * 3^(2^1) * 5^1

collapse gives:

    collapse(PET(360))
      = 2^3 * 3^2 * 5^1
      = 360

## Support

`support(P)` is the set of current-level prime roots of `P`.

For the leaf object:

    support(1) = {}

For:

    P = p_1^E_1 * p_2^E_2 * ... * p_k^E_k

the support is:

    support(P) = {p_1, p_2, ..., p_k}

Examples:

    support(PET(1)) = {}
    support(PET(2)) = {2}
    support(PET(12)) = {2, 3}
    support(PET(360)) = {2, 3, 5}

This is current-level support only.

It does not automatically include prime roots inside exponent objects.

## Height intuition

`height(P)` describes how far recursive exponent structure rises above the
leaf object.

A simple first-principles convention is:

    height(1) = 0

and for a compound object:

    height(P) = 1 + max(height(E_i))

where each `E_i` is an exponent object of `P`.

Examples:

    height(PET(1)) = 0
    height(PET(2)) = 1
    height(PET(4)) = 2
    height(PET(16)) = 3

The purpose of height is not to make arithmetic faster.

The purpose is to make recursive vertical structure explicit.

## Numeric equality

Two PET objects are numerically equal when their collapsed values are equal:

    collapse(P) = collapse(Q)

This compares only the final numeric projection.

It does not record how an object was built, traversed, annotated, or reached.

## Structural equality

Two first-principles PET objects are structurally equal when:

- both are the leaf object, or
- both have the same current-level prime-root support, and
- for every shared prime root, their exponent objects are structurally equal

For fully canonical prime-root PET objects, the structure is determined by the
integer's prime-exponent structure.

So, within this narrow canonical notation:

    PET(a) and PET(b) are structurally equal iff a = b

This relies on canonical construction and ordinary prime factorization
uniqueness.

## Why still separate value and structure?

Even when canonical `PET(n)` is uniquely determined, PET still separates two
readings:

    numeric value
    recursive structure before collapse

The numeric value answers:

    what integer does this evaluate to?

The recursive structure answers:

    what prime-root and exponent-object shape produced it?

This distinction becomes more important in wider PET/PEG layers where objects
may have:

- root-base forms
- partial or inferred structures
- addresses
- path histories
- traces
- certificates
- exploration metadata

In those wider layers, numeric equality may not be enough to express
structural, historical, or trace equality.

## Summary

The compact first-principles model is:

    PET(1) = 1

and for known factorization:

    n = product of p_i^e_i

the canonical object is:

    PET(n) = product of p_i^PET(e_i)

with numeric collapse:

    collapse(product of p_i^E_i) = product of p_i^collapse(E_i)

This gives PET its core loop:

    integer -> recursive prime-exponent object -> numeric collapse

The research question is whether the middle representation exposes useful
structure that the final collapsed value hides.
