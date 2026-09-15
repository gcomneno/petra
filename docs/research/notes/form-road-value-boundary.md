# Form, strada, value: a boundary note from T01/T16

Status: research note (conceptual distinction)
Scope: three levels that repeatedly collided during T01 and T16
Stability: a distinction, not a theory
Thread: T01, T16

## Context

During the T01 and T16 sessions, three different notions kept being
mistaken for one another:

1. **Form** — `shape(n)`, the canonical PETRA shape of a number `n`.
2. **Strada** — a sequence of canonical operators (`SPROUT`, `SHED`,
   `GRAFT`, `PRUNE`) transforming one form into another. Italian for
   "road", kept in Italian because English lacks a clean word.
3. **Value** — `n` itself, the integer.

This note records the distinction and its consequences for the T01/T16
work. It is a boundary note, not a claim about mathematics.

## The three levels, precisely

### Form

`shape(n)` is canonical, ordered, and unique. Two integers with the same
factorization structure have the same form: `shape(2) = shape(3) =
shape(5) = ○^A`. The form contains no prime labels and no integer values.

The canonical operators (SPROUT, SHED, GRAFT, PRUNE) act on forms, but
only through specific invocations (a target address, a mode). A form
alone does not determine "what happens next".

### Strada

Given two forms `A` and `B`, there may be **many** `strade` transforming
`A` into `B`. Example: from `shape(4)` to `shape(5)`, both `SHED @/0/0`
and `PRUNE @/0/0` work and produce the same result.

A `strada` is a **description** of one way to go from `A` to `B`. It is
not unique. A search algorithm (`resolve`) picks one `strada` by
minimality and tie-breaking, but the pick is arbitrary.

### Value

The integer `n` is external to the form. It is what makes `shape(2)` and
`shape(3)` "different" even though their forms are identical. Any
distinction that requires the value (e.g. "`2` comes before `3`") is not
visible in the form.

## The consequence

The **signature of a transition** `n → n+1` at the form level is the
**pair** `(shape(n), shape(n+1))`. Not the `strada`, not the value.

- The `strada` is a description among many. Choosing one arbitrarily
  loses information.
- The value introduces distinctions that the form does not contain.

## Application to T16

The fingerprint `(red, exp, stab)` introduced in
`sequence-structural-fingerprint-classifier.md` is a statistic **over
transitions of node counts**, not over forms. It sits between the form
level and the `strada` level: it summarizes the sequence of changes
without committing to a specific `strada`.

Consequence: it inherits the fragility of the `strada` level. Different
windows, different results. Convergence is not guaranteed. The
falsification recorded in `exponential-base-structural-class.md`
follows from this.

## Application to T01

The pair `(inner_sequence, structural_class(base))` from T01 is a
**form-level** object: `inner_sequence = n ↦ shape(n)` and
`structural_class = multiset of exponents of base`. The exponential
identity `shape(k^n) = C(r0^shape(e1·n), ...)` is exact and does not
depend on `strada` or value.

## Tools introduced by the distinction

- **Mother notation** (`resolver/notation.py`): reads forms, not
  `strade`. `○` is the mother; `^` and `×` compose the tree.
- **struct / destruct** (`resolver/struct_destruct.py`): operate on
  forms at one level, without search, without `strada`.

Both are form-level tools. Neither speaks about values or about `strade`.

## Boundary

This note does not claim:

- that `strade` are useless — they are useful descriptions;
- that value is forbidden — it is legitimate when made explicit;
- that the fingerprint is wrong — it is a specific statistic with a
  specific domain;
- any mathematical theorem.

It records a distinction and where it bit during T01/T16.

## Status

First conceptual note of the T01/T16 line. To be extended if further
levels emerge.
