# Abstract PETRA carrier — foundational answers

Status: research-only.

This note consolidates four foundational answers supported by the current AIP-1, AIP-2, and AIP-3 evidence. It does not modify the normative SPEC, runtime, API, CLI, serialization, or Resolver.

## 1. Candidate carrier

The current abstract carrier candidate is:

```text
Form ::= Node(Multiset_finite(Form*))
```

There is one ontological node kind. `Node(∅)` is the zero-child case; no distinct `Terminal` species is required by the bounded evidence obtained so far.

The constructor notation above is compact syntax. It must not hide the structural relation described below.

## 2. Answer 1 — primitive relation domain

### Definition candidate

PETRA has a primitive direct parent-child incidence relation.

For an occurrence `p` of a node and an immediate child occurrence `c`, write:

```text
Incidence(p, c)
```

or equivalently, as directional vocabulary:

```text
Contains(p, c)
```

The relation is between structural occurrences/incidences, not merely between abstract shape values.

### Why shape-value relation alone is insufficient

Suppose a parent contains two structurally equal children. A binary relation over shape values could record only one pair `(parent-shape, child-shape)` and would therefore lose multiplicity.

PETRA must preserve the fact that two child incidences exist even when their child forms are recursively equal.

### What is not implied

Preserving distinct incidences does **not** establish persistent occurrence identity. An implementation may use temporary identifiers, paths, indices, edge objects, or another representation, but none is thereby promoted to ontology.

### Derived relations

From direct incidence one may derive, when defined:

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

These are not additional primitive relation kinds in the current minimal candidate.

## 3. Answer 2 — global structural properties

Under the recursive carrier:

```text
Form ::= Node(Multiset_finite(Form*))
```

PETRA has the following structural consequences.

### Root

Each PETRA form has one outer node. That node is the root occurrence of that form.

### Immediate parent

Every non-root occurrence is introduced as one child incidence of exactly one immediately containing node. Therefore each non-root occurrence has one immediate parent within that form.

### Connectedness

Every occurrence is reached recursively from the outer/root node by following zero or more direct child incidences. Therefore the represented structure is connected from its root.

### Acyclicity / well-foundedness

The grammar is inductive: a form is built from already-formed finite child forms. No form contains itself through a finite downward incidence chain. Thus the candidate carrier is well-founded and acyclic.

### Finiteness

Every node has a finite child multiset, and the candidate carrier considered here is inductively finite. Therefore every PETRA form contains finitely many node occurrences and incidences.

### Classification

These properties should not all be recorded as unrelated axioms. In the current presentation:

- the one outer node and finite child multiset are definitional;
- unique immediate parent, rooted connectedness, acyclicity, and finiteness of the whole form follow from the inductive construction.

## 4. Answer 3 — structural identity

### Definition candidate

Two PETRA forms are structurally equal exactly when their roots have recursively equal finite multisets of child forms.

Equivalently:

```text
Node(M1) = Node(M2)
```

iff there exists a multiplicity-preserving pairing between the members of `M1` and `M2` such that paired child forms are structurally equal recursively.

### Consequences

```text
sibling order       = not part of structural identity
child multiplicity  = part of structural identity
recursive shape     = part of structural identity
positional rank     = not part of structural identity
persistent ids      = not established as part of structural identity
```

Thus:

```text
Node({A, A}) != Node({A})
```

but any permutation of the same child multiset represents the same abstract form.

## 5. Answer 4 — carrier, algebra, interpretation

PETRA must distinguish three layers.

### Carrier

The carrier is the abstract structural domain:

```text
nodes
+ direct parent-child incidences
+ finite recursive multiset composition
```

The carrier exists independently of arithmetic or any other external interpretation.

### Algebra

The algebra is the family of transformations admitted on the carrier.

The current minimal AIP-4 hypothesis is deliberately small:

```text
ADD(parent-occurrence, child-form)
REMOVE(parent-occurrence, child-incidence)
```

Informally:

- `ADD` introduces one new direct child incidence under a selected parent occurrence;
- `REMOVE` removes one selected direct child incidence from a parent occurrence.

This is a **hypothesis**, not yet a conclusion. It remains to be tested whether these two generators are sufficient to express the full intrinsic rewrite algebra and whether the current named operations `SPROUT`, `SHED`, `GRAFT`, and `PRUNE` are specializations/macros, constrained cases, or contain additional irreducible semantics.

### Interpretation

An interpretation assigns external meaning to the already-existing PETRA carrier.

The dependency direction is:

```text
PETRA carrier  -> may admit interpretation
interpretation -> depends on PETRA carrier
```

not the reverse.

Arithmetic terminology, numeric projection, prime labels, exponent language, or any other external semantics belong here unless independently shown to be intrinsic to the carrier.

## 6. Relation versus representation

The primitive incidence relation is ontological. The following are possible representations of that relation:

```text
nested constructor syntax
rooted-tree drawing
edge list
adjacency matrix
positional paths
serialized child arrays
```

None of these representations is the relation itself.

In particular, an adjacency matrix can encode direct incidence, but PETRA does not thereby become a matrix ontology.

## 7. Current minimal abstract statement

The present research evidence supports the following compact statement:

> A PETRA form is a finite recursively defined rooted structure of nodes. Each node has a finite multiset of direct child incidences. Direct parent-child incidence is primitive; sibling order is not intrinsic; child multiplicity is intrinsic. Structural equality is recursive multiset equality. Other structural relations are derived from direct incidence. External interpretations depend on this carrier and do not define it.

A compact constructor presentation is:

```text
Form ::= Node(Multiset_finite(Form*))
```

with the explicit warning that this syntax abbreviates, rather than erases, the underlying direct-incidence relation.

## 8. Status of the four answers

```text
1. primitive relation domain       supported candidate
2. rooted finite global structure supported consequence of construction
3. recursive multiset identity    strongly supported candidate
4. layer separation               established research architecture
   ADD/REMOVE generators           open AIP-4 hypothesis
```

The next unresolved foundational question is therefore no longer the existence of the carrier relation or the `Terminal` case. It is whether the rewrite algebra is indeed generated by minimal `ADD` and `REMOVE` operations, and under which validity constraints.

## References within PETRA research

- #248 — AIP-3 order semantics
- #256 — AIP-2 relation ontology
- #257 — level/depth derivability
- #261 — executable recursive-containment probe
- #263 — AIP-1 composition ontology
- #264 — multiplicity ontology
- #266 — Set vs Multiset executable probe
- #268 — primitive relation reassessment
- #270 — Terminal vs empty composition
- #274 — this consolidation
