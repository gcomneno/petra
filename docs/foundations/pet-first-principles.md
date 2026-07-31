# PET from first principles

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


PET starts from a research question, not from a command-line feature.

What happens if positive integers are represented as recursive vertical
structures instead of being observed only as horizontal digit-width values?

The original PET bet is that height may expose structural information that is
not immediately visible in the final numeric projection.

This document re-derives PET from that seed idea.

## 1. The original bet

Classical notation usually makes large integers grow in width:

- more digits
- larger magnitude
- wider explicit representation

PET asks whether the same integer can also be observed through recursive
height:

- prime roots
- exponent objects
- exponent objects whose exponents are again PET objects
- structural depth
- reusable recursive shape

The hope is not assumed as true.

The hypothesis to test is:

A recursive vertical representation may expose structural properties,
manipulations, or shortcuts that are not obvious in the classical numeric
projection.

## 2. What PET is

PET stands for Prime Exponent Tree.

A PET object is a finite recursive structure built from prime roots.

At each level, a PET object contains prime roots of the form:

    p^E

where:

- p is a prime root at the current level
- E is itself a PET object

The minimal PET object is:

    1

This object is treated as the first constructible PET object and as a leaf.

Therefore, exponents are not merely integer annotations.

In PET, an exponent is an object of the same kind as the whole.

That single recursive step is the seed of the model.

## 3. Value vs structure

A PET object has at least two different readings.

The numeric value is what the structure evaluates to after collapse.

The structural form is how the object is recursively built before collapse.

Two PET objects may be numerically equal while still being interesting to
compare structurally.

PET is therefore not only interested in the question:

    what number is this?

It is also interested in the question:

    what recursive structure produced this number?

## 4. Why 1 is a leaf

PET needs a base object to stop recursion.

The object 1 acts as the leaf object because it is neutral, constructible, and
allows prime roots such as p^1 to exist without requiring another external
primitive.

This is a modeling choice.

It does not claim that 1 is prime.

It says that 1 is the minimal PET object from which recursive exponent
structure can terminate.

## 5. What PET is not

PET is not currently a proven faster factorization method.

PET is not a magic shortcut for large integers.

PET does not claim improved asymptotic performance.

PET does not claim that recursive height automatically makes hard arithmetic
problems easy.

PET is a structural lens.

Its value must be tested by asking whether the lens reveals reproducible
properties that are hard to see from the numeric projection alone.

## 6. Construction boundary

PET distinguishes observing a known structure from discovering that structure.

If an integer is given only as a classical numeric value, building its canonical
prime-exponent PET representation requires recovering its prime-exponent
structure.

Therefore PET must not hide factorization cost inside the representation step.

A PET object may be useful once a structure is known, generated, inferred, or
provided, but the act of constructing that structure from an opaque integer is
itself part of the research boundary.

## 7. What survives if the magic fails

Even if no computational shortcut is found, PET may still provide useful
concepts:

- recursive object identity
- structural equivalence
- depth and mass metrics
- structural addresses
- operator semantics
- path histories
- traces and certificates
- separation between numeric equality and structural equality

These ideas belong to the representation layer.

They should be judged separately from performance claims.

## 8. Relationship to PET/PEG 2.0

PET/PEG 2.0 extends the original PET idea with executable structure:

- recursive PET objects
- root-base recursion
- structural addresses
- explicit operators
- graph traversal
- traces and certificates

These are implementation and semantics layers built on top of the original
seed.

They should not obscure the seed itself.

Before adding more algorithms, PET should be able to explain its own first
principles clearly.

## 9. Current research stance

The current safe position is:

PET studies whether recursive prime-exponent structures expose meaningful
structural information about positive integers.

This includes, but is not limited to:

- compactness
- height
- recursive shape
- structural identity
- address stability
- transformation paths
- trace replayability

Any stronger claim must be demonstrated separately.

In particular, claims about faster factorization, routing superiority, or
algorithmic shortcuts remain out of scope unless supported by explicit
evidence.
