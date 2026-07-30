# PET/PEG 2.0 Core Pillars

PET/PEG 2.0 must be grounded on structural concepts that are useful for the
next implementation layer.

This document separates core concepts from research-only diagnostics.

> **Legacy implementation boundary.** The `NEW`, `DROP`, `INC`, and `DEC`
> examples below identify retained executable research behavior. The sole
> normative future operator contract is
> [`pet-peg-2.0-object-native-operators.md`](pet-peg-2.0-object-native-operators.md).

## Boundary

This document does not claim:

- improved factorization performance
- complete PEG algebra
- default routing changes
- anchor-selection changes
- verification changes
- stable CLI behavior changes

Operator-semantics reports, pattern classes, and matrix scans remain
experimental diagnostics unless explicitly promoted.

## Pillar 1 — Recursive PET objects

A PET object is not only a flat product of atomic factors.

PET/PEG 2.0 treats objects as recursive structures:

    object
    ├── child object
    │   └── child object
    └── child object

The important question is not only:

    what are the factors?

but also:

    what is the recursive structure of the object?

Required outcome:

- define the PET object model
- define atomic vs composite objects
- define root objects
- define recursive child objects
- define when two recursive PET objects are structurally equivalent

## Pillar 2 — Root-base recursion

PET/PEG 2.0 must support objects that behave as powers of other PET objects.

This is the root-base recursion idea:

    N = R^k

where `R` may itself be a PET object, not just an atomic integer.

Required outcome:

- define root-base object semantics
- define exponent semantics over PET objects
- distinguish numeric power from structural recursive power
- expose when a root base is exact, partial, or inferred

## Pillar 3 — Structural addresses and identity

PET/PEG 2.0 needs stable ways to refer to parts of an object.

An address identifies a structural location inside a PET object:

    []
    [2]
    [2, 3]
    [2, 3, 5]

The key question is what happens to an address after an operator is applied.

Possible outcomes:

- stable
- created
- destroyed
- retargeted
- blocked at leaf

Required outcome:

- define address syntax
- define address validity
- define selected object at an address
- define address stability under operators
- define failure modes

## Pillar 4 — Operator semantics

PET/PEG 2.0 operators must have explicit semantics.

Examples:

- NEW
- DROP
- INC
- DEC
- retarget
- rewrite
- expand
- contract

For each operator, PET/PEG 2.0 must define:

- input object
- output object
- affected address
- created structure
- destroyed structure
- preserved structure
- blocked cases

Required outcome:

- operator semantic table
- executable probes for each operator
- regression tests for operator behavior
- clear boundary between operator semantics and routing policy

## Pillar 5 — Paths and graph traversal

PET/PEG 2.0 is not only about individual transformations.

It must model possible paths through a graph of PET objects:

    object A --operator--> object B --operator--> object C

The graph layer records alternative paths, not just one selected route.

Required outcome:

- define graph node semantics
- define graph edge semantics
- define path representation
- define path equivalence
- define path truncation
- define deterministic traversal constraints

## Pillar 6 — Traces, certificates, and exploration policy

PET/PEG 2.0 must separate two things:

1. what happened
2. why that route was selected

The trace/certificate layer records what happened:

    input
    operators
    intermediate objects
    final object
    verification data

The exploration-policy layer decides which path to try first.

Required outcome:

- define trace format
- define certificate format
- define replay/check procedure
- separate trace validity from route quality
- keep routing heuristics outside core semantics until explicitly promoted

## Role of pattern classes

Pattern classes are not PET/PEG 2.0 core semantics.

They are experimental diagnostics for observing repeated behavior in the
operator-semantics probes.

They may be useful for:

- detecting regressions
- describing observed structural families
- testing operator-semantics invariants
- guiding future research questions

They must not be treated as:

- routing policy
- factorization proof
- PEG completeness proof
- core PET object semantics
- stable CLI contract

## Implementation order

The implementation should proceed in this order:

1. recursive PET object model
2. root-base recursion
3. structural addresses
4. operator semantics
5. graph/path model
6. trace/certificate layer
7. exploration policy

Exploration policy comes last because it depends on all previous layers.
