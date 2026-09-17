# PETRA meta-theory — grading and edit-graph geometry

Status: **research formalization** for issue #283 under Phase 5 of the complete-theory programme #276.

This note studies the geometry induced by the elementary AIP-4 edit algebra on the canonical PETRA carrier. It is interpretation-free: no arithmetic, serialization, runtime addressing, or historical operator semantics are used.

The source results assumed here are:

- `P` is the set of finite rooted non-plane PETRA forms;
- `size : P -> N_{>=1}` is well-defined;
- `Z = Node(empty)` is the unique size-one form;
- elementary `ADD` and `REMOVE` are converse unpointed relations;
- one ADD changes size by `+1`;
- one REMOVE changes size by `-1`;
- every form reduces to `Z` by REMOVE and is constructible from `Z` by ADD.

## 1. The undirected PETRA edit graph

### Definition 1 — Edit adjacency

For PETRA forms `P,Q`, write

```text
P ~ Q
```

iff either

```text
P --ADD--> Q
```

or

```text
Q --ADD--> P.
```

By the AIP-4 converse theorem this is equivalent to saying that one endpoint is obtained from the other by exactly one elementary leaf insertion/deletion.

### Definition 2 — PETRA edit graph

Let

```text
E_P = (P, ~)
```

be the undirected graph whose vertices are PETRA forms and whose edges are edit adjacencies.

### Definition 3 — Edit path and distance

An edit path from `P` to `Q` is a finite sequence

```text
P = P_0 ~ P_1 ~ ... ~ P_k = Q.
```

Its length is `k`.

Define

```text
d(P,Q)
```

to be the minimum edit-path length from `P` to `Q`.

Existence of a finite path is guaranteed by reduction through `Z`; since path lengths are natural numbers, a minimum exists.

### Theorem 1 — Connectedness

`E_P` is connected.

#### Proof

For every `P`, AIP-4 gives a REMOVE path from `P` to `Z`. Reversing a REMOVE path gives an ADD path. Hence for arbitrary `P,Q` there is a path

```text
P ->* Z ->* Q.
```

Therefore every pair of vertices lies in one connected component. QED.

## 2. Size as a grading

### Definition 4 — Rank

Define

```text
rho(P) = size(P) - 1.
```

Thus `rho(Z)=0`.

### Theorem 2 — Unit grading law

If `P ~ Q`, then

```text
|rho(P)-rho(Q)| = 1.
```

Equivalently,

```text
|size(P)-size(Q)| = 1.
```

#### Proof

Every undirected edge is an ADD step in one orientation and a REMOVE step in the other. AIP-4 proves that ADD changes size by `+1` and REMOVE by `-1`. QED.

### Corollary 1 — Bipartiteness

`E_P` is bipartite with color classes determined by the parity of `size` (equivalently the parity of `rho`).

#### Proof

Every edge changes size by exactly one and therefore flips parity. No edge joins two vertices of the same parity. QED.

### Corollary 2 — No odd cycle

`E_P` has no odd cycle.

#### Proof

Every bipartite graph has no odd cycle. Equivalently, each edit flips size parity, so a closed path must contain an even number of steps. QED.

### Corollary 3 — Path-length parity

Every edit path from `P` to `Q` has length congruent modulo two to

```text
size(Q) - size(P).
```

In particular,

```text
d(P,Q) ≡ size(Q)-size(P) (mod 2).
```

#### Proof

Each step changes size by `+1` or `-1`, both of which are odd modulo two. Summing along a path shows that path length and total size difference have the same parity. QED.

## 3. Basic distance bounds

### Theorem 3 — Size lower bound

For all PETRA forms `P,Q`,

```text
d(P,Q) >= |size(P)-size(Q)|.
```

#### Proof

Along any edit path, one step changes size by at most one in absolute value. A path of length `k` can therefore change size by at most `k`. Taking the minimum over all paths gives the claim. QED.

### Theorem 4 — Via-Z upper bound

For all PETRA forms `P,Q`,

```text
d(P,Q) <= size(P) + size(Q) - 2.
```

#### Proof

AIP-4 reduces `P` to `Z` in exactly `size(P)-1` REMOVE steps and constructs `Q` from `Z` in exactly `size(Q)-1` ADD steps. Concatenating gives a path of the stated length. QED.

### Proposition 1 — The via-Z bound need not be geodesic

There exist `P,Q` for which the path through `Z` is not shortest.

#### Proof

Take

```text
P = Node({Z}),
Q = Node({Z,Z}).
```

Then `Q` is obtained from `P` by one ADD at the root, so

```text
d(P,Q)=1.
```

But the path through `Z` has length

```text
(size(P)-1) + (size(Q)-1)
= 1 + 2
= 3.
```

Hence the via-`Z` path is not geodesic. QED.

## 4. REMOVE order and common reducts

### Definition 5 — REMOVE reachability

Write

```text
S <=_R P
```

iff `P` can be transformed into `S` by zero or more REMOVE steps.

Call `S` a **reduct** of `P`.

### Theorem 5 — REMOVE reachability is a partial order

`<=_R` is a partial order on PETRA forms.

#### Proof

Reflexivity holds by the empty REMOVE sequence. Transitivity holds by concatenating REMOVE sequences.

For antisymmetry, suppose

```text
S <=_R P
```

and

```text
P <=_R S.
```

Every non-empty REMOVE sequence strictly decreases size. Therefore both relations can hold only if both witnessing sequences are empty, equivalently `size(P)=size(S)` and `P=S`. QED.

### Definition 6 — Common reduct

A PETRA form `S` is a **common reduct** of `P,Q` when

```text
S <=_R P
```

and

```text
S <=_R Q.
```

Define

```text
c(P,Q)
```

to be the maximum size of a common reduct of `P,Q`.

### Lemma 1 — Maximum common-reduct size exists

For every `P,Q`, `c(P,Q)` is well-defined.

#### Proof

`Z` is a reduct of every PETRA form, so the set of common reducts is non-empty.

A reduct of `P` has size between `1` and `size(P)`. Moreover, `P` has only finitely many realization-local occurrence subsets and therefore only finitely many forms obtainable by repeated leaf deletion. Hence the common reduct set is finite. Its set of sizes therefore has a maximum. QED.

### Lemma 2 — Realization lifting of an unpointed edit path

Every unpointed edit path

```text
P_0 ~ P_1 ~ ... ~ P_k
```

can be represented by a sequence of concrete realizations in which each consecutive step is an actual elementary leaf insertion or deletion and surviving occurrences are tracked consistently across the sequence.

#### Proof

Choose any realization of `P_0`. For the edge from `P_i` to `P_{i+1}`, the unpointed relation is witnessed by some realization of `P_i` and one elementary pointed edit. Any two realizations of `P_i` are root-preserving isomorphic. Transport the witnessing target occurrence/incidence through such an isomorphism to the currently chosen realization, perform the corresponding elementary edit there, and choose the resulting realization for `P_{i+1}`. Repeat inductively. QED.

### Lemma 3 — Survivors of an edit path form a common reduct

Consider a concrete lifted edit path from `P` to `Q`. Let `S` be the rooted structure induced by those occurrences that were already present in the initial realization of `P` and are never removed along the path.

Then `S` represents a common reduct of both `P` and `Q`.

#### Proof

The root is never removed, so the survivor set is non-empty and contains the root.

If an initial occurrence survives, every initial ancestor of that occurrence also survives: an ancestor cannot be removed as a leaf while a surviving descendant remains below it. Therefore survivors are ancestor-closed and induce a rooted connected subrealization of the initial tree.

Deleting all non-surviving initial occurrences can be performed by repeated leaf removals in descendant-first order, so the survivor form is a reduct of `P`.

ADD steps do not alter existing incidences, and REMOVE steps only delete a leaf and its incoming incidence. Thus the same surviving occurrences and incidences remain in the final realization of `Q`. Any added or other non-surviving occurrences can likewise be removed in descendant-first order, so the survivor form is also a reduct of `Q`. QED.

## 5. Exact distance formula

### Theorem 6 — Common-reduct distance theorem

For all PETRA forms `P,Q`,

```text
d(P,Q)
= size(P) + size(Q) - 2*c(P,Q).
```

#### Proof — upper bound

Let `S` be a common reduct of maximum size `c(P,Q)`.

Because `S <=_R P`, there is a REMOVE path from `P` to `S` of exactly

```text
size(P)-size(S)
```

steps. Because `S <=_R Q`, reversing a REMOVE path from `Q` to `S` gives an ADD path from `S` to `Q` of exactly

```text
size(Q)-size(S)
```

steps.

Concatenating yields

```text
d(P,Q)
<= size(P)+size(Q)-2*size(S)
= size(P)+size(Q)-2*c(P,Q).
```

#### Proof — lower bound

Take any edit path from `P` to `Q` of length `L`, and lift it to concrete realizations by Lemma 2.

Let the path contain `a` ADD steps and `r` REMOVE steps. Then

```text
L = a+r
```

and the net size change gives

```text
size(Q) = size(P) + a - r.
```

Hence

```text
r = (L + size(P) - size(Q))/2.
```

At most `r` occurrences that were present initially can have been removed, because there are only `r` REMOVE steps total. Therefore at least

```text
size(P)-r
= (size(P)+size(Q)-L)/2
```

initial occurrences survive to the end.

By Lemma 3 those survivors form a common reduct `S`. Therefore

```text
c(P,Q) >= size(S)
         >= (size(P)+size(Q)-L)/2.
```

Rearranging,

```text
L >= size(P)+size(Q)-2*c(P,Q).
```

This holds for every path, hence also for a shortest path. Combined with the upper bound, equality follows. QED.

### Corollary 4 — A geodesic may always be chosen REMOVE-then-ADD

For every `P,Q`, there exists a geodesic of the form

```text
P --REMOVE*--> S --ADD*--> Q
```

where `S` is any maximum-size common reduct.

#### Proof

The path constructed in the upper-bound part of Theorem 6 has length exactly equal to the distance. QED.

### Corollary 5 — Characterization of the size lower-bound equality case

Assume `size(P) <= size(Q)`. Then

```text
d(P,Q) = size(Q)-size(P)
```

iff

```text
P <=_R Q,
```

or equivalently iff `Q` can be obtained from `P` by ADD-only steps.

The symmetric statement holds when `size(Q) <= size(P)`.

#### Proof

By Theorem 6, equality with the size lower bound means

```text
size(P)+size(Q)-2*c(P,Q)
= size(Q)-size(P),
```

so `c(P,Q)=size(P)`.

A common reduct of `P` having size `size(P)` must equal `P`, since every non-empty REMOVE sequence decreases size. Thus `P` is a reduct of `Q`. The converse is immediate from an ADD-only path of length `size(Q)-size(P)`. QED.

### Corollary 6 — Characterization of via-Z geodesicity

The canonical path through `Z` is geodesic iff

```text
c(P,Q)=1.
```

#### Proof

The via-`Z` path has length

```text
size(P)+size(Q)-2.
```

By Theorem 6 this equals the distance exactly when `2*c(P,Q)=2`, hence when `c(P,Q)=1`. QED.

### Theorem 7 — Maximum-size common reducts need not be unique

There exist PETRA forms with two distinct maximum-size common reducts.

#### Proof

Let

```text
P = Node({ Node({ Z, Node({Z}) }) })
```

and

```text
Q = Node({ Node({Z,Z}), Node({Node({Z})}) }).
```

Then

```text
size(P)=5,
size(Q)=7.
```

Consider

```text
S_1 = Node({Node({Z,Z})})
```

and

```text
S_2 = Node({Node({Node({Z})})}).
```

Both have size four and they are not equal: in `S_1` the unique level-one node has two children, while in `S_2` the realization is a unary chain below the root.

From `P`, removing the leaf inside its unary child subtree yields `S_1`, while removing the sibling leaf instead yields `S_2`. Hence both are reducts of `P`.

From `Q`, delete the entire size-three child subtree complementary to the desired one, using descendant-first leaf removals. This yields `S_1` in one case and `S_2` in the other. Hence both are also reducts of `Q`.

It remains to prove maximality. A common reduct of size five would have to equal `P`, because every non-empty REMOVE sequence from `P` strictly decreases size. But reducing `Q` from size seven to size five permits exactly two REMOVE steps. To obtain a root-degree-one form from `Q`, one of its two root child subtrees must disappear completely. Each such subtree has size three, requiring three leaf removals. Therefore `P` is not a reduct of `Q`, and no common reduct can have size five.

Thus `c(P,Q)=4`, and both distinct forms `S_1,S_2` attain that maximum. QED.

### Corollary 7 — The REMOVE poset is not a meet-semilattice

The partial order `(P, <=_R)` is not a meet-semilattice.

#### Proof

For the pair `P,Q` from Theorem 7, `S_1` and `S_2` are distinct common lower bounds of maximum possible size four.

If one were strictly below the other under `<=_R`, a non-empty REMOVE sequence would connect them and strictly decrease size. Since they have equal size, neither can lie below the other unless they are equal, which they are not.

Therefore the pair has no greatest lower bound. Hence `(P, <=_R)` is not a meet-semilattice. QED.

### Remark 1 — Distance depends on maximum size, not on a meet

The distance theorem requires only the numerical quantity `c(P,Q)`, the maximum **size** of a common reduct. Theorem 7 shows that there need not be a unique maximum common reduct and Corollary 7 rules out a global meet operation for `<=_R`.

No lattice interpretation should therefore be inferred from the common-reduct distance formula.

## 6. Geodesic normalization

### Theorem 8 — Every geodesic determines a maximum common survivor reduct

Let a shortest path from `P` to `Q` be lifted to concrete realizations as in Lemma 2. The initial occurrences that survive the entire path form a common reduct of size exactly `c(P,Q)`.

#### Proof

Let the geodesic length be `L=d(P,Q)`. The survivor estimate in the lower-bound proof of Theorem 6 gives a common reduct of size at least

```text
(size(P)+size(Q)-L)/2.
```

By the exact distance formula this quantity is `c(P,Q)`. No common reduct can be larger by definition, so the survivor reduct has exactly that size. QED.

### Corollary 8 — No wasted add-then-delete steps on a geodesic

On a lifted geodesic, no occurrence created by an ADD step is later deleted by a REMOVE step.

#### Proof

If an added occurrence were later removed, then at least one REMOVE step would be spent on a non-initial occurrence. Fewer than `r` initial occurrences would be removed, so strictly more than `size(P)-r=c(P,Q)` initial occurrences would survive. Lemma 3 would then produce a common reduct larger than `c(P,Q)`, contradiction. QED.

### Corollary 9 — Geodesic normal form exists

Every pair `P,Q` admits a shortest path with all REMOVE steps before all ADD steps.

#### Proof

Choose a maximum common reduct and use Corollary 4. QED.

This is an existence statement about geodesic normal form. It does not claim uniqueness of geodesics or literal commutation of every concrete edit sequence step-by-step.

## 7. Local finiteness

### Theorem 9 — Finite degree

Every vertex of `E_P` has finite degree.

#### Proof

Choose a realization of `P` with `n=size(P)` occurrences.

An ADD step is determined at realization level by choosing one of the `n` target occurrences. Different targets may collapse to the same unpointed successor after quotienting by isomorphism, so there are at most `n` distinct ADD successors.

A REMOVE step is determined by choosing a non-root leaf occurrence. There are at most `n-1` such occurrences, and quotienting can only reduce the number of distinct successors.

Therefore `P` has finitely many neighbors. QED.

### Remark 2 — Automorphism orbits

Targets in the same automorphism orbit necessarily yield isomorphic edit results, so automorphism orbits provide a natural compression of realization-level targets.

This note does not yet claim the converse: targets in distinct automorphism orbits need not automatically be assumed to produce distinct unpointed successors without proof.

## 8. First one-step statistics

The meta-theory must distinguish exact invariants from gradings and bounded-change statistics.

### Proposition 2 — Size is a grading, not an invariant

`size` changes by exactly one on every edit edge.

Therefore it is not invariant under ADD/REMOVE, but it is an exact rank/grading function.

### Proposition 3 — Size parity is a bipartite color, not an invariant

Parity flips on every elementary edit. It is therefore not invariant along edges, but it determines the canonical bipartition of `E_P`.

### Proposition 4 — Depth is 1-Lipschitz under one edit

If `P ~ Q`, then

```text
|depth(P)-depth(Q)| <= 1.
```

#### Proof

Adding one leaf at an occurrence of level `l` creates a new occurrence at level `l+1` and leaves all existing levels unchanged. Therefore depth either stays unchanged or increases by exactly one. REMOVE is the converse operation, so depth either stays unchanged or decreases by exactly one. QED.

### Proposition 5 — Leaf count has bounded one-step change

Let `leaves(P)` denote the number of zero-child occurrences in a realization of `P`. For one ADD step:

- if the target was already a leaf, that target ceases to be a leaf and the new child becomes a leaf, so leaf count is unchanged;
- if the target was not a leaf, the new child adds one leaf, so leaf count increases by one.

Thus an undirected edit changes leaf count by at most one in absolute value.

### Proposition 6 — Root degree has bounded one-step change

One elementary edit changes root degree by at most one in absolute value, with change occurring exactly when the edited incidence is at the root.

### Remark 3 — Degree multiset and other statistics

The complete vertex-degree multiset of a realization can change at the edited parent and at the inserted/removed leaf only, but quotient-level consequences require separate formulation. No stronger invariant claim is made here.

## 9. What is established

This note proves internally:

- `E_P` is connected;
- `size-1` is a rank function changing by exactly one per edge;
- `E_P` is bipartite and has no odd cycles;
- all path lengths have the parity forced by endpoint sizes;
- the basic lower and via-`Z` upper distance bounds;
- REMOVE reachability is a partial order;
- every pair has at least one maximum-size common reduct;
- the exact distance formula

  ```text
  d(P,Q)=size(P)+size(Q)-2*c(P,Q);
  ```

- every pair admits a REMOVE-then-ADD geodesic through a maximum common reduct;
- via-`Z` is geodesic exactly when the largest common reduct has size one;
- maximum-size common reducts need not be unique;
- the REMOVE poset is not a meet-semilattice;
- the edit graph is locally finite;
- depth, leaf count, and root degree have bounded one-step variation as specified above.

## 10. What remains open

This note does **not** yet establish:

- a classification of all pairs with non-unique maximum common reducts;
- join-semilattice or weaker order-theoretic properties beyond the negative meet result;
- lattice, median-graph, CAT(0), modular, or distributive properties;
- a closed formula for the number of geodesics;
- exact unpointed degree in terms of automorphism orbits;
- global automorphism group of `E_P`;
- a complete classification of all Lipschitz or invariant statistics;
- novelty relative to known rooted-tree insertion/deletion metrics;
- any normative SPEC/runtime consequence.

These belong to later Phase-5 work or Phase-6 external validation.

## 11. Evidence discipline

The results above are mathematical statements proved from the canonical carrier and AIP-4 edit rules.

The bounded executable probe corroborates the exact distance formula on small forms and was used to discover the explicit non-uniqueness witness promoted into Theorem 7. The proof of Theorem 7 is independent of the bounded enumeration.

Probe results remain computational evidence only and do not replace the general proofs.