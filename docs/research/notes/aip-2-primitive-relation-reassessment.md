# AIP-2 primitive relation reassessment

## Status

Research note under issues #256 and #268.

This note is non-normative. It does not change SPEC, runtime semantics, APIs, CLI behavior, serialization, addressing, operators, or Resolver behavior.

## Why AIP-2 needs reassessment

Previous AIP-2 work successfully showed, on a bounded executable corpus, that the current `Root`, positional rank, `Term` wrapper, `^`/exponent vocabulary, and sibling order can be erased while preserving the tested structural behavior.

That evidence was useful but one interpretation was too strong:

> wrapper erasure does not imply relation erasure.

Recursive containment is itself a relation. Writing a structure as nested syntax can make that relation look implicit, but implicit syntax is still a representation of a structural relation.

Therefore AIP-2 must distinguish:

```text
relation ontology
!=
relation representation
```

## Revised core question

The question is no longer whether PETRA has a relation at all.

The revised question is:

> What is the minimal primitive structural relation required by abstract PETRA, and which other relations or properties can be derived from it without information loss?

## Primitive candidate: direct containment / incidence

Let structural occurrences be denoted by `x`, `y`, ... and define:

```text
Contains(x, y)
```

meaning:

> occurrence `y` is directly contained in occurrence `x`.

This is a candidate primitive relation because removing it removes the information that makes recursive structure recursive.

The inverse view is not an independent primitive:

```text
ContainedBy(y, x) iff Contains(x, y)
```

## Derived relations

If direct containment is primitive, several other structural relations can be derived.

### Parent and children

```text
Parent(y) = x iff Contains(x, y)
Children(x) = { y | Contains(x, y) }
```

Subject to the candidate rooted-tree discipline, every non-root occurrence has exactly one direct parent.

### Sibling

```text
Sibling(y, z)
iff
exists x : Contains(x, y) and Contains(x, z) and y != z
```

Siblinghood therefore need not be primitive.

### Ancestor and descendant

`Ancestor(x, z)` is the transitive closure of direct containment.

```text
Contains(x, y)
Contains(y, z)
----------------
Ancestor(x, z)
```

`Descendant(z, x)` is the inverse view of `Ancestor(x, z)`.

### Level

For an occurrence `x`, `Level(x)` is the number of direct-containment edges from the root occurrence to `x`.

Thus level is derived from the relation.

Importantly, the converse does not hold: levels alone do not reconstruct the direct-containment relation.

For example, both structures below have one root at level 0, two occurrences at level 1, and one occurrence at level 2:

```text
A
|- B
|  `- D
`- C
```

and

```text
A
|- B
`- C
   `- D
```

The level assignment is the same, while `Parent(D)`, `Children(B)`, and `Children(C)` differ.

Therefore `Level` cannot replace the primitive relation.

### Depth

Global depth is derivable as the maximum root-relative level.

Node-relative subtree depth additionally requires descendant information, which is itself derived from direct containment.

## Relation versus representation

A relation can be represented in many equivalent-looking ways without changing its ontological role.

Examples include:

```text
nested boxes
adjacency matrix
edge list
rooted-tree drawing
recursive constructor syntax
```

An adjacency matrix is therefore a representation of the relation, not the relation itself.

For occurrences `x_i`, a matrix may encode:

```text
M[i,j] = 1 iff Contains(x_i, x_j)
```

Changing representation must not be confused with changing ontology.

## Multiplicity exposes an important distinction

A naive binary relation over shape values is not sufficient when duplicate equal child shapes occur.

Suppose two structurally equal empty forms occur under the same parent:

```text
A
|- B1 = []
`- B2 = []
```

If `B1` and `B2` are collapsed merely because their shapes are equal, then writing only

```text
Contains(A, [])
```

loses multiplicity.

AIP-1 executable evidence already showed that duplicate count is structurally significant on the tested corpus: set-valued composition collapsed 35 multiset classes to 4 classes and made multiplicity-sensitive SPROUT/SHED rewrites invisible.

Therefore AIP-2 must distinguish:

```text
shape equality
from
structural occurrence / incidence
```

This does not yet prove that persistent occurrence identity is CORE. It only shows that the relation model must preserve distinct incidences when equal shapes repeat.

A candidate formulation is therefore:

```text
primitive domain: structural occurrences
primitive relation: direct containment incidence
shape: recursively derived equivalence/classification of occurrences
```

Whether occurrence identity is primitive, ephemeral, quotientable, or merely representational remains open.

## What previous AIP-2 probes actually established

The bounded executable AIP-2 work supports the following narrower claims:

```text
Root / rank                    = erasable representation on tested corpus
Term wrapper                   = erasable wrapper on tested corpus
^ / exponent vocabulary        = not required by tested structural rewrites
sibling order                  = not required by tested abstract identity
recursive structure            = preserved
multiplicity                   = preserved
operator effects               = preserved under wrapper erasure
```

It did **not** establish:

```text
no intrinsic relation exists
```

The relation survived the probe implicitly as recursive parent-child structure.

## Provisional classification

```text
direct containment / incidence = CORE candidate
inverse containment             = DERIVED RELATION
parent / children               = DERIVED RELATION/PROPERTY
sibling                         = DERIVED RELATION
ancestor / descendant           = DERIVED RELATION
level                           = DERIVED PROPERTY
depth                           = DERIVED PROPERTY

^ / exponent relation wording  = INTERPRETATION / historical notation
Root / positional rank          = REPRESENTATION
Term wrapper                    = not established CORE
adjacency matrix                = REPRESENTATION
nested-box notation             = REPRESENTATION
```

## Minimality hypothesis

A strong current hypothesis is:

> One primitive direct-containment/incidence relation, together with structural occurrences and multiplicity-preserving recursive shape, is sufficient to derive the currently identified PETRA structural relations.

This is a hypothesis, not yet a theorem.

## Open questions

The reassessment leaves several questions for focused tests:

1. Must the primitive relation be formally directed, or is direction derivable from rootedness?
2. Is exactly one parent for every non-root occurrence intrinsic?
3. Is the carrier necessarily connected?
4. Are cycles intrinsically forbidden, or excluded only because current recursive construction cannot create them?
5. Does the root belong to ontology or can it be derived as the unique occurrence with no parent?
6. How should duplicate incidences be formalized without prematurely introducing persistent occurrence identifiers?
7. Is the resulting abstract carrier exactly an unlabeled rooted non-plane tree class, or does PETRA retain additional rewrite structure beyond that carrier?

## Current correction to AIP-2

The most important correction is concise:

```text
old overreach:
recursive containment only -> no distinct relation ontology

revised view:
recursive containment is itself the primitive relation candidate
```

AIP-2 should therefore remove arithmetic and representational relation machinery, not erase relation from the abstract core.
