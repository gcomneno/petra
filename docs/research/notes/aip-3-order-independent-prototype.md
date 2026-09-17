# AIP-3 order-independent prototype

## Status

Research note for issue #254, under the parent AIP-3 question in #248.

This note is non-normative. It does not change `docs/reference/SPEC.md`, the
runtime model, public APIs, CLI behavior, serialization, addressing, operator
semantics, or Resolver behavior.

## Question

Can sibling order be removed from PETRA abstract identity while preserving the
candidate properties that appear intrinsic to form?

The concrete hypothesis is:

```text
abstract sibling structure = multiset of recursive components
canonical sibling order    = representation
semantic/domain order       = interpretation
```

Equivalently, define a recursive equivalence relation `~perm` that identifies
canonical PETRA states differing only by sibling permutations at any depth,
and study the quotient:

```text
P_unordered = P_current / ~perm
```

## Prototype

The research probe is:

`tools/research/aip3_order_independent_probe.py`

It defines an order-independent recursive key:

```text
Q(Leaf) = Leaf
Q(Container(children)) = Container(multiset(Q(child) for child in children))
```

The implementation materializes the multiset as a deterministically sorted
tuple only so that Python can compare and print it. The sorting rule is not
part of the candidate ontology.

Multiplicity is preserved. This is a multiset quotient, not a set quotient.
Therefore one terminal child, two terminal children, and three terminal
children remain three distinct abstract forms.

## Explicit permutation witness

Consider two current canonical shapes whose root children are structurally:

```text
[Leaf, Container(Leaf)]
[Container(Leaf), Leaf]
```

Under current PETRA equality these are different because corresponding ordered
term positions differ.

Under the candidate quotient they have the same recursive multiset key.

The probe also checks that the following candidate core observables are equal:

- total model-node count;
- recursive container depth;
- direct recursive-component multiplicity.

The same test is repeated for a permutation occurring below the root, showing
that the candidate equivalence is recursive rather than only top-level.

## What the prototype deliberately forgets

The quotient forgets:

- sibling ordinal position;
- `r0`, `r1`, ... rank assignment as semantic identity;
- textual address segments that depend on sibling position;
- canonical serialization order;
- insertion position;
- default target-selection tie-breaking that refers to first/last/preorder.

These are all currently observable in PETRA v2.0.0. The prototype does not
claim they are unimportant operationally. It tests whether they belong to
abstract form ontology.

## What the prototype preserves

The quotient preserves:

- terminal versus composite distinction;
- recursive containment/composition shape;
- sibling multiplicity;
- recursive depth;
- total Leaf/Container/Term accounting induced by the current model;
- the distinction between different multisets of recursive component shapes.

This is the minimum preservation set tested by the first prototype. It is not
yet a complete characterization of every possible future core invariant.

## Bounded counterexample search

The probe constructs one representative per candidate unordered form up to:

```text
max_depth = 2
max_width = 3
```

For each representative it materializes all unique root-level sibling
permutations available inside that bounded representative and groups them by
the order-independent key.

The search checks two things:

1. every permutation variant returns to the expected quotient class;
2. variants in one quotient class agree on node count, depth, and direct
   component multiplicity.

It also verifies that the number of quotient classes equals the number of
constructed unordered representatives, so no accidental collision is observed
inside the bounded corpus.

This is evidence, not proof for the unbounded shape-space.

## Why this matters for AIP-3

The current runtime stores a container as an ordered tuple, compares containers
position-by-position, assigns root ranks from those positions, and uses those
positions in addresses. Therefore sibling order is unquestionably normative in
PETRA v2.0.0.

That fact alone does not establish order as ontology.

The prototype demonstrates a coherent alternative abstraction in which current
ordered states can map to order-free classes without losing the tested
structural observables.

This strengthens the hypothesis that current sibling order mixes at least two
non-core concerns:

### Representation order

A deterministic implementation may need one stable ordering to serialize,
address, display, cache, or compare representatives. Such an order can be
chosen *after* abstract identity is known.

### Interpretation order

A domain may itself supply an order. The arithmetic interpretation is one such
case: the existing integer projection associates sorted prime factors with
positional ranks. A symbolic interpretation may have no corresponding domain
order at all, while another interpretation could define a completely different
one.

Therefore an order supplied by one interpretation cannot by itself justify an
order relation in the abstract PETRA ontology.

## Operator consequences

This prototype does not redefine operators, but it clarifies the distinction
that a future operator analysis must maintain.

At an abstract level, operations can be described without sibling ordinals:

```text
SPROUT: add one terminal component occurrence
SHED:   remove one eligible terminal component occurrence
GRAFT:  replace one eligible terminal relation target by a one-component composite
PRUNE:  perform the corresponding eligible collapse
```

What remains order-dependent in the current contract is principally target
coordination and default selection:

- numeric address segments select ordinal positions;
- root ranks mirror those positions;
- SPROUT appends at the end;
- SHED defaults to the last eligible top-level leaf;
- GRAFT/PRUNE use deterministic traversal/tie-breaking rules.

If the core becomes order-free, explicit operator application would need to
target structural occurrences without treating their presentation order as
identity. Deterministic defaults could still be defined by a representation
layer, but changing representation order must not change the abstract result
class.

Duplicate structurally identical occurrences are the important case: an
order-free multiset retains their multiplicity even though individual duplicate
occurrences have no persistent intrinsic identity. Selecting one of two
indistinguishable occurrences should therefore produce the same abstract class
when the local rewrite is identical.

## Resolver consequences

Resolver currently searches the graph of canonical ordered PETRA states. Under
the candidate abstraction, the research object would instead be a quotient
graph whose vertices are permutation classes.

Potential consequences include:

- fewer distinct vertices;
- paths differing only by sibling reorder artifacts collapse;
- positional witnesses become representation-level evidence;
- distance should be reconsidered on quotient classes rather than assumed to be
  identical to current ordered-state distance.

No claim about metric preservation is made here. That requires a separate
experiment because shortest paths may depend on current target-address and
canonical-order policy.

## Provisional result

The bounded prototype finds no structural counterexample to the hypothesis:

> sibling order is not required for the tested abstract shape properties.

More precisely:

> Current ordered PETRA states admit a non-trivial recursive multiset quotient
> that preserves terminal/composite structure, multiplicity, node count, depth,
> and the recursively composed child-shape inventory in the bounded corpus.

This does **not** yet prove that every future intrinsic PETRA property is
permutation-invariant.

## AIP-3 decision criterion

AIP-3 can be promoted from hypothesis toward a formal result if subsequent work
shows that every property admitted to the abstract core factors through the
quotient map:

```text
q : P_current -> P_unordered
```

That is, for each candidate core observable `F`, there should exist an
order-independent `F_bar` such that:

```text
F = F_bar . q
```

Any property that fails this factorization test must answer a harder question:
why is sibling position intrinsic to form rather than merely representation or
interpretation?

## Next step

Run the probe locally, record the concrete bounded counts, and then extend the
counterexample search only if the result justifies it. Do not modify the
normative model before that evidence is captured.
