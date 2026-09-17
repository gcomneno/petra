# AIP-1 — Terminal versus empty composition

Status: research-only

Refs: #263, #270, #268, #269

## Question

Is `Terminal` an ontologically distinct PETRA constructor, or is it exactly the zero-child case of one uniform recursive constructor?

The question arises after two prior results:

1. AIP-3 strongly supports erasing sibling order from intrinsic identity while preserving multiplicity.
2. The AIP-2 reassessment restores direct containment/incidence as an intrinsic structural relation while keeping `^`, arithmetic relation language, positional rank, and representation choices outside the abstract core.

The present analysis therefore asks whether PETRA still needs two ontological species:

```text
Form ::= Terminal | Composite(Multiset(Form+))
```

or whether the same carrier can be expressed uniformly as:

```text
Form ::= Node(Multiset(Form*))
```

where the zero-child case is the base form.

Didactically:

```text
[]          zero-child PETRA
[[]]        one-child PETRA
[[][]]      two-child PETRA with two equal child forms
```

There is no separate naked terminal object in the one-constructor presentation.

## Relation ontology must remain explicit

The compact constructor notation must not be mistaken for a relation-free ontology.

For a form such as:

```text
[[] []]
```

the abstract structure contains one parent occurrence and two child occurrences with two direct containment/incidence facts.

The nested brackets are merely one representation of those incidences. Equivalent representations may include a rooted-tree drawing, an edge list, or an adjacency/incidence matrix. None of those representations is itself the relation.

Thus the candidate one-constructor model is not:

```text
"just nested syntax"
```

but rather:

```text
finite PETRA occurrences
+
direct parent-child incidence
+
recursive closure
+
multiplicity of child incidences
```

with sibling order absent from intrinsic identity.

## Candidate recursive equivalence

Let the current abstract two-constructor candidate be:

```text
T ::= Terminal | Composite(Multiset(T+))
```

and the uniform one-constructor candidate be:

```text
N ::= Node(Multiset(N*))
```

Define the recursive encoding `E : T -> N` by:

```text
E(Terminal) = Node(∅)
E(Composite(M)) = Node(multiset(E(x) for x in M))
```

Because a `Composite` in `T` is non-empty, every non-terminal `T` maps to a node with at least one child. Therefore the zero-child node has exactly one possible preimage candidate: `Terminal`.

Define the recursive decoding `D : N -> T` by:

```text
D(Node(∅)) = Terminal
D(Node(M)) = Composite(multiset(D(x) for x in M))    when M != ∅
```

At the grammar level these definitions suggest a recursive bijection:

```text
D(E(t)) = t
E(D(n)) = n
```

subject to equality being interpreted in the AIP-3 order-erased, multiplicity-preserving sense.

This is stronger than saying that an empty composite is merely "similar" to a terminal. It says that the separate `Terminal` constructor may be eliminable as syntax while preserving the same abstract carrier.

This note treats that as a hypothesis to validate, not yet as a normative conclusion.

## What information changes?

Under the proposed equivalence:

```text
Terminal                        <-> Node(∅)
Composite({Terminal})           <-> Node({Node(∅)})
Composite({Terminal,Terminal})  <-> Node({Node(∅),Node(∅)})
```

No accepted structural distinction is intentionally erased:

- zero children versus one child remains distinct;
- one child versus two equal children remains distinct;
- recursive depth remains distinct;
- child multiplicity remains distinct;
- sibling order remains erased as already supported by AIP-3.

In particular:

```text
Node(∅) != Node({Node(∅)})
```

The present question must not be confused with a unary-collapse hypothesis.

## Direct incidence and multiplicity

A naive set-valued relation over shape values is insufficient.

For:

```text
[[] []]
```

both child forms are structurally equal, but there are two child incidences. A model recording only:

```text
Contains(parent_shape, empty_shape)
```

would collapse multiplicity.

The abstract structure must therefore preserve incidence multiplicity. This can be expressed through occurrence-level incidences, multiedges, or an equivalent multiplicity-aware representation without requiring persistent externally visible occurrence identifiers.

This distinction is essential:

```text
persistent occurrence identity      not established CORE
incidence multiplicity              strongly supported CORE candidate
```

## Derived relations remain derived

If direct containment/incidence is primitive, then the usual structural relations remain derivable:

```text
ContainedBy
Parent
Children
Sibling
Ancestor
Descendant
Level
Depth
```

The one-constructor presentation does not alter that dependency structure.

In particular, `Level` does not reconstruct parent/child incidence: different trees can assign the same levels to corresponding occurrences while connecting them differently.

## Operator translation

The one-constructor model gives natural translations of the four current abstract operators.

Let:

```text
Z = Node(∅)
```

be the zero-child form.

### SPROUT

Abstractly add one zero-child child incidence:

```text
Node(M) -> Node(M ⊎ {Z})
```

This preserves the multiplicity-sensitive behavior already observed under AIP-1.

### SHED

Remove one eligible zero-child child incidence:

```text
Node(M ⊎ {Z}) -> Node(M)
```

When the removed child was the last child:

```text
Node({Z}) -> Node(∅)
```

No special ontological conversion from `Composite` to `Terminal` is required; the result is simply the same constructor at arity zero.

### GRAFT

The previous terminal-to-unary-composite transition becomes:

```text
Node(∅) -> Node({Node(∅)})
```

### PRUNE

The corresponding reverse case becomes:

```text
Node({Node(∅)}) -> Node(∅)
```

This translation is conceptually simpler than switching between two constructor species, but conceptual simplicity alone is not evidence of correctness. Operator conjugacy should be checked explicitly.

## Structural observables

Under the recursive correspondence, several observables should be preserved when defined on abstract PETRA forms rather than runtime wrappers:

- number of PETRA form occurrences;
- direct-incidence count;
- multiplicity at each parent;
- level of each occurrence;
- overall depth;
- recursive child-shape inventory.

Current runtime node-count conventions may include or exclude implementation wrappers differently. Those conventions must not be promoted to ontology without audit.

## What the hypothesis would imply

If the recursive bijection and operator conjugacy hold, then the abstract carrier can be written with one constructor:

```text
PETRA ::= Node(Multiset(PETRA*))
```

with:

```text
zero children   = base case
one child       = unary recursive form
many children   = wider recursive form
```

and intrinsic direct-incidence relations between parent and child occurrences.

The important conceptual consequence would be:

> `Terminal` is not a second kind of PETRA object; it is the zero-child case of the same recursive kind.

That conclusion remains provisional until the executable/counterexample checks are completed.

## What this does not establish

This analysis does not yet establish:

- that the one-constructor carrier is the final PETRA ontology;
- that occurrence identity is unnecessary in every future extension;
- that all current runtime/API behavior can be replaced without compatibility consequences;
- that unary nodes should collapse;
- that arbitrary graph-like relations belong to PETRA;
- that the abstract carrier itself is novel.

No SPEC/runtime/API/CLI/serialization/Resolver change follows from this note.

## Next validation target

A bounded executable probe should compare the two presentations and report:

1. round-trip `T -> N -> T` and `N -> T -> N`;
2. uniqueness of zero-child mapping;
3. preservation of multiplicity and AIP-3 permutation erasure;
4. preservation of direct-incidence counts;
5. node-count/level/depth correspondence;
6. conjugacy of SPROUT/SHED/GRAFT/PRUNE;
7. bounded collision search;
8. explicit witness cases for zero, unary, duplicate-child, and nested forms.

A passing bounded probe would strengthen the hypothesis but would not replace a mathematical proof of the recursive bijection.