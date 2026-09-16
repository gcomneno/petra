# Recursive reconstruction of a form from the mother (T01)

Status: research note (bounded empirical)
Scope: construct any canonical PETRA shape from the mother using struct only
Stability: one algorithm, verified on small cases; not a theorem
Thread: T01

## Context

T01 asks for a pair `(inner_sequence, structural_class(base))` extracted
from an exponential sequence. During the T01/T16 work, a related
question emerged: given any canonical PETRA shape, can it be rebuilt
step by step from the bare leaf, using only `struct`?

This note records a positive answer, with a specific strategy.

## Setup

The tools used:

- **Mother notation** (`notation.py`): the mother is the bare leaf;
  `(...)` is a container; `x` separates sibling fathers; `A`, `B`, `C`
  are local labels.
- **struct** (`struct_destruct.py`): attaches a shape to a form at any
  of its hooks. Three hooks exist: replace a leaf, append a new father,
  prepend a new father.
- **Elementary pieces**: only two, the bare leaf and the one-father
  container with a leaf father.

## Result

Every canonical PETRA shape can be constructed from the bare leaf using
only those two pieces, in a single chain of `struct` applications,
without intermediate restarts.

The strategy is **height-first**:

1. At a container, process fathers from left to right.
2. For each father:
   - append a new leaf father;
   - if the target father has a container exponent, fill it completely
     (recursively) before moving to the next father.

Each step of the chain is a real `struct` application to the current
shape. The final shape is structurally equal to the target.

## Examples

For `shape(360)`, the chain has 6 steps: from the bare leaf, the first
father is extended to its full depth, then the second, then the third.

For `shape(720)`, the first father is completed to its full depth (a
chain of three nested fathers), then the second, then the third.

For `shape(30030)`, all fathers are leaf, so the chain is a simple
sequence of append operations, one per father.

## The chain is unique only under the chosen order

The chain produced by this algorithm is unique because the traversal
order (left to right, height first) is fixed. A different order (right
to left, or width first) would produce a different chain for the same
target.

So the chain is **not** a canonical invariant of the shape. It is one
of several possible descriptions.

## Relation to the form-strada-value boundary

This note fits the boundary distinction recorded in
`form-road-value-boundary.md`:

- the **form** is the object (the target shape);
- the **strada** is the chain of `struct` applications;
- the **value** does not appear.

The chain is a strada. The form is the target. The construction shows
that every form has at least one strada from the bare leaf.

## Boundary

This note does not claim:

- that the algorithm is optimal (it is not shortest);
- that the chain is unique across all possible orders;
- that `struct` alone is a complete algebra (it is not: it needs the
  two elementary pieces);
- any theorem about all shapes beyond what is verified here.

## Reproducibility

`tools/research/rebuild_recursive.py N` for any positive integer N:
prints the recursion tree and the flat step list, and verifies that
`built == target`.

## Status

Third result of the T01 line. To be extended, refuted, or merged into
T01.
