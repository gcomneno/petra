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

## Scaling and limits

The reconstruction algorithm's cost is proportional to the
`node_count` of the target, which depends on the multiplicative
structure of `n`, not on the number of digits of `n`.

### Smooth numbers

Smooth numbers (`n = 2^k`, `n = 2^a * 3^b * ...`) build in constant
time regardless of size:

| n | time | node_count |
| --- | ---: | ---: |
| 2^100 | 0.00s | 7 |
| 2^1000 | 0.00s | 11 |
| 2^100000 | 0.25s | 11 |
| 2^1000000 | 0.25s | 15 |
| 2^10000000 | 0.33s | 11 |

`node_count` does not grow monotonically with the exponent. It
depends on `shape(k)` for `n = 2^k`, hence on the factorization of `k`
itself. `k = 10^6 = 2^6 * 5^6` gives a larger shape than
`k = 10^7 = 2^7 * 5^7`.

### Semiprimes

The practical limit is in `sympy.factorint`, not in the
reconstruction:

| prime size | total n | time | outcome |
| --- | ---: | ---: | --- |
| 20 digits | 39 | 2.9s | ok |
| 25 digits | 49 | 1.3s | ok |
| 30 digits | 59 | >15s | timeout |
| 35 digits | 69 | >15s | timeout |

Beyond ~25-30 digits per prime, factoring a semiprime is not feasible
with the current tooling. The reconstructed shape, however, is
trivially small (`○^(A × B)`) regardless of prime size: two large
primes are indistinguishable from two small ones in the shape.

### Products of distinct primes raised to powers

The most structurally rich cases are products of many distinct primes,
each raised to a power:

- `2^100 * 3^50 * 5^30`: 27 nodes, 0.25s
- `2^1000 * 3^500`: 21 nodes, 0.25s
- `(2*3*5*7*11*13)^50`: 49 nodes, 0.34s

All build in under a second. The limit is again factorization, not
reconstruction.

### Conclusion

The shape and its reconstruction scale with the multiplicative
structure of `n`, not with the magnitude of `n`. Smooth numbers of
millions of digits are reconstructed in constant time. Semiprimes of
moderate size hit the limits of `sympy.factorint`.

## Step count of the single-chain reconstruction

The height-first single-chain algorithm appends one leaf at a time.
Every append adds exactly two nodes: one `Term` and one `Leaf`. The
initial shape is the bare leaf, which counts as one node.

Therefore the number of append steps for a target with `node_count = N`
is:

    steps = (N - 1) / 2

Verified on `n = 1..200` via `rebuild_recursive.py`: no failures.

This count is a property of the algorithm, not of the shape. It is an
upper bound: other construction strategies could use fewer steps by
attaching larger pieces at once.

## Comparison with BFS reconstruction

Two reconstruction tools are available:

- `rebuild_recursive.py` — height-first, single chain, only leaf
  appends. Step count: `(N-1)/2` for `node_count = N`.
- `rebuild_shape.py` — BFS with a piece set. `--pieces minimal` uses
  only the bare leaf and the one-father container. `--pieces all` uses
  every shape with `node_count < target`.

Empirical step counts:

| n | recursive (leaf appends) | BFS minimal | BFS all |
| ---: | ---: | ---: | ---: |
| 12 | 4 | 3 | 3 |
| 30 | 4 | 4 | 3 |
| 720 | 7 | (none) | 3 |
| 3600 | 8 | (none) | 3 |

Notes:

- BFS `minimal` fails on larger targets (`720`, `3600`): with only the
  bare leaf and the one-father container, some targets are not
  reachable at all.
- BFS `all` stays at 3 steps regardless of target size, but it uses
  pieces whose `node_count` is close to the target's. It presupposes
  that such pieces are available. If only the bare leaf is given, those
  pieces must first be built, and the cost is hidden.
- The recursive algorithm grows as `(N-1)/2`, which is an upper bound
  when only the bare leaf is given.

The two counts are not directly comparable: they assume different
starting material.

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
