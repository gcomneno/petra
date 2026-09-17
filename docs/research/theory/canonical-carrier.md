# Canonical PETRA carrier

Status: **research formalization** for issue #277 under the complete-theory programme #276.

This note formalizes the abstract PETRA carrier independently of arithmetic interpretation, runtime representation, positional ranks, serialization, and the historical four-operator API. It is not yet a normative SPEC change.

## 1. Mathematical setting

### Definition 1 — Finite multiset

For a set or class `X`, let `M_f(X)` denote the finite multisets over `X`. A finite multiset records the multiplicity of each member but has no intrinsic order.

For `M in M_f(X)` and `x in X`, write `mult_M(x)` for the multiplicity of `x` in `M`.

### Definition 2 — PETRA carrier

The PETRA carrier `P` is the least class closed under the constructor

```text
Node : M_f(P) -> P.
```

Equivalently, `P` is the least fixed point of

```text
P ~= M_f(P)
```

with the constructor written explicitly as

```text
P ::= Node(M_f(P)).
```

Every PETRA form is therefore a node whose children form a finite multiset of PETRA forms.

### Definition 3 — Zero-child form

Define

```text
Z := Node(empty multiset).
```

`Z` is the zero-child PETRA form.

### Remark 1 — One ontological species

`Z` is not a second ontological constructor. It is the arity-zero case of `Node`.

### Definition 4 — Realization and node occurrence

A **realization** of a PETRA form `P` is any finite rooted tree obtained by recursively realizing the child multiset of each `Node` occurrence, using one distinct child occurrence for each multiset copy.

A **node occurrence** is a vertex of such a realization.

Occurrence distinction is local structural bookkeeping: two occurrences may carry structurally equal subforms, and no persistent identity is part of PETRA structural equality.

### Definition 5 — Direct incidence

For node occurrences `u` and `v` in a realization, write

```text
u -> v
```

when `v` is one of the immediate child occurrences contributed by the child multiset at `u`.

This direct parent-child incidence is primitive. Multiplicity is represented by multiple child incidences, including when the corresponding child subforms are structurally equal.

### Remark 2 — Representation independence

Nested constructor notation, rooted-tree drawings, edge lists, adjacency/incidence matrices, and positional paths may represent the same direct-incidence structure. None of those encodings is itself the ontology.

## 2. Derived structural notions

### Definition 6 — Root

The root occurrence of a realization is the outer occurrence introduced by the outermost `Node` constructor.

### Definition 7 — Parent and child

If `u -> v`, then `u` is the immediate parent of `v`, and `v` is an immediate child of `u`.

### Definition 8 — Descendant and ancestor

`v` is a proper descendant of `u` when there exists a non-empty finite chain

```text
u = x_0 -> x_1 -> ... -> x_k = v.
```

Ancestor is the converse relation.

### Definition 9 — Subtree form at an occurrence

The subtree form rooted at occurrence `u` is the PETRA form recursively determined by `u` and all descendants of `u`.

### Definition 10 — Size

Define size recursively by

```text
size(Node(M)) = 1 + sum_{X in M, with multiplicity} size(X).
```

Thus size counts node occurrences.

### Definition 11 — Level

The level of an occurrence `u` is the length of the unique direct-incidence path from the root to `u`.

The existence and uniqueness used here are justified by Theorems 1–3 below.

### Definition 12 — Depth

Define

```text
depth(P) = max level(u)
```

over all occurrences `u` of `P`.

Equivalently,

```text
depth(Node(empty)) = 0,
depth(Node(M)) = 1 + max_{X in M} depth(X)    when M is non-empty.
```

## 3. Structural equality

### Definition 13 — Recursive structural equality

Define `~=`, structural equality, recursively by

```text
Node(M) ~= Node(N)
```

iff there exists a multiplicity-preserving matching between the members of `M` and `N` such that matched child forms are recursively structurally equal.

Equivalently, after quotienting child forms by `~=`, the multisets of equivalence classes are equal.

Sibling order is therefore absent from structural identity; child multiplicity is retained.

### Remark 3 — Isomorphism view

Definition 13 is equivalent to root-preserving isomorphism of finite rooted non-plane tree realizations, where repeated isomorphic child subtrees remain distinct occurrences through multiplicity.

## 4. First structural theorems

### Theorem 1 — Unique root

Every PETRA form has exactly one root occurrence.

#### Proof

By Definition 2, every PETRA form is constructed by one outer application `Node(M)`. That application contributes one outer occurrence. Every other occurrence appears recursively inside one member of `M`; hence no other occurrence is outermost. Therefore exactly one root occurrence exists. QED.

### Theorem 2 — Unique immediate parent

Every non-root occurrence has exactly one immediate parent occurrence.

#### Proof

Consider a realization of `Node(M)`. Each non-root occurrence is introduced as one specific multiset copy inside the child multiset of exactly one containing occurrence. By construction, that containing occurrence contributes exactly one direct incidence to that child occurrence. Recursive realization repeats the same rule independently inside each child. Therefore every non-root occurrence has one and only one immediate parent. QED.

### Theorem 3 — Connectedness and unique root path

Every occurrence is reachable from the root by a unique finite direct-incidence path.

#### Proof

Existence follows by structural induction. The root has the empty path. Any non-root occurrence lies in a recursively realized child form; prepend the direct incidence from its immediate parent to the induction-hypothesis path inside that child.

Uniqueness follows from Theorem 2: if two distinct root-to-occurrence paths existed, their final divergence would give some non-root occurrence two distinct immediate parents. Contradiction. QED.

### Theorem 4 — Finiteness

Every PETRA form has finitely many node occurrences.

#### Proof

By structural induction on the least construction of `P`. For `Node(M)`, the multiset `M` is finite by Definition 1. Every child form in `M` has finitely many occurrences by the induction hypothesis. A finite sum of finite cardinalities, plus the root occurrence, is finite. Equivalently, `size(Node(M))` is a finite natural number. QED.

### Theorem 5 — Acyclicity and well-foundedness

No node occurrence is a proper descendant of itself, and every descending direct-incidence chain is finite.

#### Proof

Along every direct incidence from parent to child, the child belongs to a proper recursively contained subrealization. If a cycle existed, some occurrence would have to be a proper recursive descendant of itself, contradicting the finite construction tree generated by Definition 2.

More concretely, by Theorem 4 there are finitely many occurrences, and by Theorem 2 every non-root occurrence has one parent. A directed cycle would be disconnected from the unique root or would force an occurrence on the cycle to have two incoming parent incidences when entered from the root path, contradicting Theorem 3. Hence there are no directed cycles. Since the occurrence set is finite, every descending chain is finite. QED.

### Theorem 6 — Structural equality is an equivalence relation

The relation `~=` of Definition 13 is reflexive, symmetric, and transitive.

#### Proof

Proceed by structural induction on size.

**Reflexivity.** For `Node(M)`, match every child occurrence copy with itself. By induction each child form is structurally equal to itself, so `Node(M) ~= Node(M)`.

**Symmetry.** If `Node(M) ~= Node(N)`, Definition 13 supplies a multiplicity-preserving matching from `M` to `N`. Reverse that matching. By induction, child equality is symmetric, so `Node(N) ~= Node(M)`.

**Transitivity.** Suppose `Node(M) ~= Node(N)` and `Node(N) ~= Node(K)`. Compose the two multiplicity-preserving matchings through the copies of `N`. By induction, matched child forms satisfy transitivity. The composite is therefore a multiplicity-preserving matching from `M` to `K`, giving `Node(M) ~= Node(K)`. QED.

### Theorem 7 — Uniqueness of the zero-child form

A PETRA form has zero immediate children iff it is structurally equal to `Z = Node(empty)`.

#### Proof

If a form has zero immediate children, its child multiset is empty, so by Definition 2 it is `Node(empty)`. Conversely, `Node(empty)` has no child copies by construction. Since there is only one empty finite multiset, all zero-child forms are structurally equal under Definition 13. QED.

## 5. Equivalence with the two-constructor candidate

### Definition 14 — Historical abstract two-constructor carrier

Let `T` be generated by

```text
T ::= Terminal | Composite(M_f^+(T)),
```

where `M_f^+(T)` denotes non-empty finite multisets.

This definition is abstract: the names `Terminal` and `Composite` here are only constructor labels.

### Definition 15 — Encoding into the one-constructor carrier

Define `E : T -> P` recursively by

```text
E(Terminal) = Node(empty),
E(Composite(M)) = Node(multiset(E(x) for x in M)).
```

### Definition 16 — Decoding into the two-constructor carrier

Define `D : P -> T` recursively by

```text
D(Node(empty)) = Terminal,
D(Node(M)) = Composite(multiset(D(x) for x in M))    when M is non-empty.
```

### Lemma 1 — Encoding preserves multiplicity and erases no structural distinction

For every `t in T`, child multiplicities at every recursive level are preserved by `E`.

#### Proof

Immediate by structural induction: `E` maps each multiset copy independently and uses the resulting multiset without deduplication or ordering. QED.

### Theorem 8 — Two-constructor / one-constructor bijection

`E` and `D` are mutually inverse up to structural equality:

```text
D(E(t)) = t              for every t in T,
E(D(p)) ~= p             for every p in P.
```

Hence the two-constructor carrier and the one-constructor carrier are structurally isomorphic presentations.

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

  By the induction hypothesis, every copied child `x` satisfies `D(E(x)) = x`, with multiplicity preserved by Lemma 1. Hence the resulting multiset is exactly `M`.

For `E(D(p)) ~= p`, use structural induction on `p = Node(M)`.

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

  By induction, each child returns a structurally equal form, and multiplicities are unchanged. Definition 13 therefore gives `E(D(p)) ~= p`.

Thus `E` and `D` are mutually inverse at the structural level. QED.

### Corollary 1 — Terminal is not required as a separate ontological species

The distinction between `Terminal` and `Composite` in Definition 14 is presentation-level rather than structurally necessary: the same carrier is represented with one constructor by treating the terminal case as `Node(empty)`.

### Corollary 2 — Unary and zero-child forms remain distinct

```text
Node(empty) !~= Node({Node(empty)}).
```

#### Proof

Their root child multisets have cardinalities zero and one, respectively, so no multiplicity-preserving matching exists. QED.

## 6. What is primitive and what is derived

### Definition 17 — Primitive carrier content

At this stage the canonical carrier candidate contains only:

1. one recursive node species;
2. finite child multiplicity;
3. primitive direct parent-child incidence.

### Corollary 3 — Derived relations

Immediate parent/child, ancestor/descendant, siblinghood, level, depth, and subtree containment are derived from direct incidence and the rooted recursive construction.

### Remark 4 — No persistent occurrence identity

Proofs quantify over occurrences inside a realization, but structural equality does not depend on persistent labels for those occurrences. Renaming realization-local occurrence labels leaves the PETRA form unchanged.

## 7. Boundary of this note

This note does **not** establish:

- that `ADD` and `REMOVE` generate the complete PETRA algebra;
- the exact canonical algebraic signature;
- admissible interpretation/model classes;
- novelty relative to established rooted-tree mathematics;
- normative runtime or SPEC changes.

Those belong to later phases of #276.

## 8. Evidence status

The theorems above are intended as general mathematical statements derived from the recursive carrier definition. Existing bounded executable probes remain corroborating engineering evidence only; they are not used as proofs here.

The next required review should check the definitions and proofs for hidden dependence on sibling order, positional identity, historical wrappers, or interpretation-specific vocabulary before canonical promotion.
