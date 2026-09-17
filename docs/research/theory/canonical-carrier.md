# Canonical PETRA carrier

Status: **research formalization** for issue #277 under the complete-theory programme #276.

This note formalizes the abstract PETRA carrier independently of arithmetic interpretation, runtime representation, positional ranks, serialization, and the historical four-operator API. It is not yet a normative SPEC change.

## 1. Mathematical setting

### Definition 1 — Finite multiset

For a set or class `X`, let `M_f(X)` denote the finite multisets over `X`. A finite multiset records the multiplicity of each member but has no intrinsic order.

For `M in M_f(X)` and `x in X`, write `mult_M(x)` for the multiplicity of `x` in `M`.

### Definition 2 — Concrete realization

A **concrete realization** is a finite rooted non-plane tree

```text
R = (V, r, ->)
```

such that:

- `V` is a finite non-empty set of occurrence-local vertices;
- `r in V` is the distinguished root;
- `->` is the direct parent-child incidence relation;
- `r` has no immediate parent;
- every `v != r` has exactly one immediate parent;
- every vertex is reachable from `r` by a finite `->`-path.

These conditions are intended as the explicit structural characterization used below; acyclicity is derived rather than added as an independent axiom.

Vertex labels, names, addresses, or persistent identities are not part of the structure. Vertices merely distinguish simultaneous occurrences inside one realization.

### Definition 3 — Realization isomorphism

Two concrete realizations

```text
R = (V, r, ->)
S = (W, s, =>)
```

are **root-preserving isomorphic**, written

```text
R ≅ S,
```

when there exists a bijection `f : V -> W` such that

```text
f(r) = s
```

and, for all `u,v in V`,

```text
u -> v    iff    f(u) => f(v).
```

### Definition 4 — PETRA form

A **PETRA form** is an isomorphism class of concrete realizations under `≅`.

The PETRA carrier `P` is the set/class of all such isomorphism classes.

Thus equality in `P` is structural equality by definition:

```text
[R] = [S]    iff    R ≅ S.
```

No second equality relation is required at the carrier level.

### Remark 1 — Recursive presentation

The same carrier admits the recursive presentation

```text
P ::= Node(M_f(P)).
```

A representative `Node(M)` consists of one root occurrence plus one outgoing direct incidence for each copy in the finite multiset `M`, recursively realizing each child form.

This constructor notation is a compact presentation of the relational structure. It does not replace or eliminate direct incidence.

### Definition 5 — Zero-child form

Define

```text
Z := Node(empty multiset).
```

Equivalently, `Z` is the unique PETRA form represented by a one-vertex rooted realization.

### Remark 2 — One ontological species

`Z` is not a second ontological constructor. It is the arity-zero case of `Node`.

## 2. Primitive relation and derived notions

### Definition 6 — Node occurrence

A **node occurrence** is a vertex of a chosen concrete realization of a PETRA form.

Occurrence distinction is realization-local bookkeeping. Two occurrences may support structurally equal subforms, and no persistent occurrence identity participates in PETRA equality.

### Definition 7 — Direct incidence

For occurrences `u` and `v` in one concrete realization, write

```text
u -> v
```

when `v` is an immediate child occurrence of `u`.

Direct parent-child incidence is the primitive structural relation of the relational presentation.

Multiplicity is represented by multiple child occurrences and therefore by multiple outgoing incidences, including when their rooted subrealizations are mutually isomorphic.

### Remark 3 — Constructor and relational presentations

The constructor and relational descriptions are equivalent presentations of the same carrier:

```text
constructor presentation:
Node(M) records one root together with a finite multiset of child forms

relational presentation:
u -> v records each direct parent-child incidence between occurrences
```

The constructor determines the incidences of a realization; the incidence relation exposes the same structure directly. Neither presentation adds extra ontology.

### Remark 4 — Representation independence

Nested constructor notation, rooted-tree drawings, edge lists, adjacency/incidence matrices, and positional paths may represent the same PETRA form. None of those encodings is itself the ontology.

### Definition 8 — Root

The **root occurrence** of a concrete realization is its distinguished root vertex.

### Definition 9 — Parent and child

If `u -> v`, then `u` is the immediate parent of `v`, and `v` is an immediate child of `u`.

### Definition 10 — Descendant and ancestor

`v` is a proper descendant of `u` when there exists a non-empty finite chain

```text
u = x_0 -> x_1 -> ... -> x_k = v.
```

Ancestor is the converse relation.

### Definition 11 — Subtree form at an occurrence

For an occurrence `u`, the **subtree form rooted at `u`** is the PETRA form represented by the induced rooted descendant realization containing `u` and all descendants of `u`.

### Definition 12 — Size

The size of a PETRA form is the number of occurrences in any concrete realization representing it.

Equivalently, under the recursive presentation,

```text
size(Node(M)) = 1 + sum_{X in M, with multiplicity} size(X).
```

### Definition 13 — Level

The level of an occurrence `u` is the length of the unique direct-incidence path from the root to `u`.

Existence and uniqueness are established below.

### Definition 14 — Depth

The depth of a PETRA form is

```text
depth(P) = max level(u)
```

over the occurrences of any realization of `P`.

Equivalently,

```text
depth(Node(empty)) = 0,
depth(Node(M)) = 1 + max_{X in M} depth(X)    when M is non-empty.
```

## 3. Recursive characterization of structural identity

### Definition 15 — Recursive multiset characterization

For recursively presented forms, define the predicate `Eq_rec` by

```text
Eq_rec(Node(M), Node(N))
```

iff there exists a bijection between the copies of `M` and the copies of `N` such that every matched pair of child forms again satisfies `Eq_rec`.

This definition is multiplicity-preserving and does not refer to sibling order.

### Lemma 1 — Recursive characterization agrees with realization isomorphism

For recursively presented forms `p` and `q`,

```text
Eq_rec(p, q)
```

holds iff concrete realizations of `p` and `q` are root-preserving isomorphic.

#### Proof

Proceed by induction on `size(p) + size(q)`.

If both roots have no children, both realizations consist of one vertex, and the claim is immediate.

Otherwise, a root-preserving isomorphism maps immediate children of the first root bijectively to immediate children of the second root and restricts to an isomorphism between every matched pair of rooted child subrealizations. By the induction hypothesis, the corresponding child forms satisfy `Eq_rec`, giving the required multiplicity-preserving matching.

Conversely, suppose such a matching of child copies exists. By the induction hypothesis, each matched pair of child forms has root-preserving isomorphic realizations. Take the disjoint union of those child isomorphisms and extend it by mapping the outer root to the outer root. The result is a root-preserving isomorphism of the complete realizations. QED.

### Corollary 1 — Recursive identity is an equivalence relation

`Eq_rec` is reflexive, symmetric, and transitive.

#### Proof

By Lemma 1, `Eq_rec` coincides with root-preserving isomorphism, which is an equivalence relation. QED.

### Corollary 2 — Carrier equality has the recursive multiset form

For PETRA forms represented recursively,

```text
Node(M) = Node(N)
```

in `P` iff their child copies can be matched multiplicity-preservingly so that matched child forms are recursively equal.

Thus sibling order is absent from structural identity, while child multiplicity is intrinsic.

## 4. First structural theorems

### Theorem 1 — Unique root

Every concrete realization of a PETRA form has exactly one root occurrence.

#### Proof

The distinguished root `r` has no immediate parent by Definition 2. Any other occurrence `v != r` has exactly one immediate parent, again by Definition 2. Therefore `r` is the unique parentless occurrence and hence the unique root. QED.

### Theorem 2 — Unique immediate parent

Every non-root occurrence has exactly one immediate parent occurrence.

#### Proof

This is one of the defining conditions of concrete realizations in Definition 2. QED.

### Theorem 3 — Connectedness and unique root path

Every occurrence is reachable from the root by a unique finite direct-incidence path.

#### Proof

Existence is required by Definition 2.

For uniqueness, suppose an occurrence `v` had two distinct root-to-`v` paths. Let `w` be the first occurrence after their last common vertex at which the paths differ and later reconverge. At the first reconvergence point, that non-root occurrence would have two distinct immediate parents, contradicting Theorem 2. Hence the root path is unique. QED.

### Theorem 4 — Finiteness

Every PETRA form has finitely many node occurrences.

#### Proof

Every PETRA form is, by Definition 4, an isomorphism class of finite concrete realizations. Therefore every representative has finitely many occurrences. Isomorphism preserves cardinality, so size is well-defined and finite. QED.

### Theorem 5 — Acyclicity and well-foundedness

No occurrence is a proper descendant of itself, and every descending direct-incidence chain is finite.

#### Proof

Assume for contradiction that a directed cycle exists.

If the distinguished root `r` lies on that cycle, then `r` has an immediate predecessor on the cycle, contradicting Definition 2, which states that `r` has no immediate parent.

Otherwise, choose any occurrence `v` on the cycle. By Theorem 3, there is a unique finite path from `r` to `v`. Let `w` be the first occurrence on that root-to-`v` path that lies on the cycle. Since `w != r`, it has one predecessor on the root path. It also has a predecessor on the directed cycle. These predecessors are distinct because `w` was the first cycle occurrence encountered from the root. Thus `w` has two immediate parents, contradicting Theorem 2. Hence no directed cycle exists.

By Theorem 4 there are finitely many occurrences. An infinite descending chain would repeat an occurrence and therefore contain a directed cycle. Thus every descending chain is finite. QED.

### Theorem 6 — Zero-child uniqueness

A PETRA form has zero immediate children iff it equals `Z`.

#### Proof

A zero-child realization has exactly one vertex: the root. All one-vertex rooted realizations are root-preserving isomorphic, hence represent the same PETRA form `Z`. Conversely, `Z` is represented by a one-vertex realization and therefore has no immediate children. QED.

### Corollary 3 — Unary and zero-child forms remain distinct

```text
Node(empty) != Node({Node(empty)}).
```

#### Proof

Any realization of `Node(empty)` has one occurrence, while any realization of `Node({Node(empty)})` has two. Root-preserving isomorphism preserves cardinality, so the two forms are unequal. QED.

## 5. Equivalence with the two-constructor presentation

### Definition 16 — Two-constructor carrier

Let `T` be generated by

```text
T ::= Terminal | Composite(M_f^+(T)),
```

where `M_f^+(T)` denotes non-empty finite multisets.

The constructor labels carry no extra interpretation.

### Definition 17 — Encoding into PETRA

Define `E : T -> P` recursively by

```text
E(Terminal) = Node(empty),
E(Composite(M)) = Node(multiset(E(x) for x in M)).
```

### Definition 18 — Decoding from PETRA

Define `D : P -> T` recursively by

```text
D(Node(empty)) = Terminal,
D(Node(M)) = Composite(multiset(D(x) for x in M))    when M is non-empty.
```

By Corollary 2, this definition depends only on the structural form, not on sibling order or realization-local labels.

### Lemma 2 — Encoding preserves multiplicity

For every `t in T`, `E` preserves child multiplicities at every recursive level.

#### Proof

By structural induction. `Terminal` has no children. For `Composite(M)`, every multiset copy is mapped independently by `E`, and the resulting copies are collected in a multiset without deduplication. Apply the induction hypothesis recursively. QED.

### Theorem 7 — Two-constructor / one-constructor bijection

`E` and `D` are mutually inverse:

```text
D(E(t)) = t    for every t in T,
E(D(p)) = p    for every p in P.
```

Hence `T` and `P` are in bijection as structural carriers.

#### Proof

For `D(E(t)) = t`, use structural induction on `t`.

- Base: `t = Terminal`. Then

  ```text
  D(E(Terminal)) = D(Node(empty)) = Terminal.
  ```

- Step: `t = Composite(M)` with non-empty `M`. Then

  ```text
  D(E(Composite(M)))
  = D(Node(E[M]))
  = Composite(D[E[M]]).
  ```

  By the induction hypothesis, every copied child `x` satisfies `D(E(x)) = x`, and Lemma 2 preserves multiplicity. Hence the resulting multiset is exactly `M`.

For `E(D(p)) = p`, use structural induction on the recursive presentation of `p = Node(M)`.

- If `M` is empty,

  ```text
  E(D(Node(empty))) = E(Terminal) = Node(empty).
  ```

- If `M` is non-empty,

  ```text
  E(D(Node(M)))
  = E(Composite(D[M]))
  = Node(E[D[M]]).
  ```

  By induction, every copied child returns the same PETRA form in `P`, and multiplicities are preserved. Corollary 2 therefore gives equality of the resulting outer forms.

Thus `E` and `D` are mutually inverse. QED.

### Corollary 4 — Terminal is not required as a separate ontological species

The distinction between `Terminal` and `Composite` in Definition 16 is presentation-level rather than structurally necessary. The same carrier is represented with one constructor by treating the terminal case as `Node(empty)`.

## 6. Primitive versus derived structure

### Definition 19 — Primitive carrier content

At this stage the canonical carrier contains only:

1. one recursive node species;
2. finite child multiplicity;
3. primitive direct parent-child incidence.

### Corollary 5 — Derived relations

Immediate parent/child terminology, ancestor/descendant, siblinghood, level, depth, subtree containment, and root paths are derived from direct incidence together with the rooted finite-tree conditions.

### Remark 5 — No persistent occurrence identity

Proofs quantify over occurrences inside concrete realizations, but carrier equality does not depend on persistent labels for those occurrences. Any root-preserving renaming of realization-local vertices yields the same PETRA form.

## 7. Boundary of this note

This note does **not** establish:

- that `ADD` and `REMOVE` generate the complete PETRA algebra;
- the exact canonical algebraic signature;
- admissible interpretation/model classes;
- novelty relative to established rooted-tree mathematics;
- normative runtime or SPEC changes.

Those belong to later phases of #276.

## 8. Evidence status

The results above are intended as general mathematical statements. Existing bounded executable probes remain corroborating engineering evidence only; they are not used as proofs here.

Before canonical promotion, further review should still check terminology against established rooted-tree literature and verify that no theorem is being claimed as PETRA-specific when it is standard mathematics.
