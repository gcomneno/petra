# PETRA meta-theory — automorphisms and symmetry

Status: **research formalization** for issue #289 under Phase 5 of the complete-theory programme #276.

This note studies symmetry at three distinct levels:

1. automorphisms of one concrete realization of a PETRA form;
2. automorphism orbits of realization-local edit targets;
3. automorphisms of the global undirected PETRA edit graph.

These levels are related but are not identified.

No arithmetic interpretation is used.

## 1. Source data

Let `P` be the canonical PETRA carrier

```text
P ::= Node(M_f(P))
```

with zero-child form

```text
Z = Node(empty).
```

A concrete realization is a finite rooted non-plane tree. PETRA forms are root-preserving isomorphism classes of such realizations.

AIP-4 gives elementary ADD/REMOVE edits. The Phase-5 presentations layer also distinguishes:

```text
realization-level target occurrences
witnessed edit classes
unpointed successor forms.
```

That distinction is essential below.

## 2. Automorphism group of a realization

### Definition 1 — Realization automorphism group

For a concrete realization `T`, define

```text
Aut(T)
```

to be the group of root-preserving tree automorphisms of `T`, under composition.

Because `T` is finite, `Aut(T)` is finite.

### Theorem 1 — Realization-independence of automorphism-group isomorphism type

If `T` and `T'` realize the same PETRA form, then `Aut(T)` and `Aut(T')` are isomorphic groups.

More precisely, every root-preserving isomorphism

```text
f : T -> T'
```

induces a group isomorphism

```text
Phi_f : Aut(T) -> Aut(T')
Phi_f(g) = f g f^{-1}.
```

If `f' : T -> T'` is another realization isomorphism, then `Phi_f` and `Phi_f'` differ by an inner automorphism of `Aut(T')`.

#### Proof

Conjugation by `f` preserves identity, composition, and inverses, so `Phi_f` is a group isomorphism.

For another isomorphism `f'`, let

```text
h = f' f^{-1} in Aut(T').
```

Then

```text
Phi_f'(g)
= f' g f'^{-1}
= h (f g f^{-1}) h^{-1}.
```

Thus the two identifications differ by conjugation inside `Aut(T')`. QED.

### Definition 2 — Automorphism group of a PETRA form

For a PETRA form `P`, write

```text
Aut(P)
```

for the **group isomorphism type** of `Aut(T)` for any realization `T` of `P`.

This notation does not assert a choice-free literal identification of all realization automorphism groups.

## 3. Recursive decomposition

Let

```text
P = Node(M)
```

and suppose the root-child multiset has distinct child-form isomorphism types

```text
C_1, ..., C_k
```

with multiplicities

```text
m_1, ..., m_k >= 1.
```

Choose one concrete realization `U_i` of each `C_i` and realize the root children as `m_i` disjoint copies of `U_i` attached to a common root.

### Theorem 2 — Recursive automorphism-group decomposition

With the choices above,

```text
Aut(P)
~= product_{i=1}^k ( Aut(C_i)^{m_i} semidirect S_{m_i} ),
```

where `S_{m_i}` acts on `Aut(C_i)^{m_i}` by permuting coordinates.

Equivalently, each factor is the standard permutation wreath-product construction

```text
Aut(C_i) wr S_{m_i}
```

for that explicit coordinate-permutation action.

The displayed isomorphism depends on the chosen child-copy identifications; the resulting group isomorphism type does not.

#### Proof

Every root-preserving automorphism fixes the root. It therefore permutes the root-child subtrees while preserving their rooted isomorphism types. Hence children of type `C_i` may only be permuted among the `m_i` copies of that same type, giving a permutation in `S_{m_i}`.

After choosing where each copy is sent, the restriction of the automorphism from each source copy to its destination copy is a rooted isomorphism. Relative to the chosen identifications with `U_i`, this contributes one element of `Aut(U_i)` for each copy, hence an element of `Aut(C_i)^{m_i}`.

Conversely, any coordinatewise choice of child automorphisms together with any permutation among equal-type child copies extends uniquely to a root-preserving automorphism fixing the root and acting as prescribed below it.

Composition first permutes which coordinate is used and then composes the internal automorphisms. This is exactly the semidirect-product law for the coordinate-permutation action of `S_{m_i}` on `Aut(C_i)^{m_i}`. Different child types act independently, giving the direct product over `i`. QED.

### Corollary 1 — Automorphism-count recurrence

For

```text
P = Node(M)
```

with child types and multiplicities as above,

```text
|Aut(P)|
= product_{i=1}^k |Aut(C_i)|^{m_i} * m_i!.
```

#### Proof

Take cardinalities in Theorem 2. A finite semidirect product `G semidirect H` has cardinality `|G||H|`, and `|S_m|=m!`. QED.

### Corollary 2 — Recursive rigidity criterion

A PETRA form `P=Node(M)` is rigid iff both conditions hold:

1. every child form appearing in `M` is rigid;
2. every child-form isomorphism type occurs with multiplicity one.

Equivalently, all root children are pairwise non-isomorphic and recursively rigid.

#### Proof

By Corollary 1,

```text
|Aut(P)|=1
```

iff every factor `|Aut(C_i)|^{m_i}` equals one and every `m_i!` equals one. The first condition is equivalent to each `C_i` being rigid; the second is equivalent to `m_i=1` for every `i`. QED.

### Examples

`Z` is rigid.

A unary chain is rigid by repeated application of Corollary 2.

By contrast,

```text
Node({Z,Z})
```

has automorphism group isomorphic to `S_2`, generated by swapping its two leaf children.

## 4. Target orbits

Let `T` be a concrete realization of `P`. The group `Aut(T)` acts on the occurrence set of `T` by evaluation:

```text
g . u = g(u).
```

Because automorphisms preserve root, incidence, and child count, they preserve the subset of non-root leaf occurrences as well.

### Definition 3 — ADD-target orbit

An **ADD-target orbit** is an orbit of `Aut(T)` on all node occurrences of `T`.

### Definition 4 — REMOVE-target orbit

A **REMOVE-target orbit** is an orbit of `Aut(T)` on the non-root leaf occurrences of `T`.

The orbit partitions are independent of the chosen realization up to the natural transport supplied by any realization isomorphism.

## 5. Orbits and witnessed edit classes

### Theorem 3 — ADD-target orbits classify witnessed ADD classes

Fix a realization `T` of `P`. Two ADD target occurrences `u,v` determine the same witnessed ADD edge class out of `P` iff `u` and `v` lie in the same `Aut(T)`-orbit.

#### Proof

If `v=g(u)` for some `g in Aut(T)`, extend `g` after the edit by carrying the fresh leaf attached at `u` to the fresh leaf attached at `v`. This is exactly a witness-respecting isomorphism of the two ADD triples, so they define the same witnessed edge class.

Conversely, if the two ADD triples define the same witnessed edge class, Definition 1 of witnessed edits in the presentations layer supplies a root-preserving isomorphism of their source realizations carrying the chosen target occurrence `u` to `v`. Since the source realization is `T` in both triples, that source isomorphism is an element of `Aut(T)`. Hence `u` and `v` lie in the same orbit. QED.

### Theorem 4 — REMOVE-target orbits classify witnessed REMOVE classes

Fix a realization `T` of `P`. Two removable leaf targets determine the same witnessed REMOVE edge class out of `P` iff they lie in the same `Aut(T)`-orbit.

#### Proof

The argument is the REMOVE analogue of Theorem 3. An automorphism carrying one removable leaf to another transports the deletion witness. Conversely, equality of witnessed REMOVE classes includes a source-realization automorphism carrying one chosen deleted leaf to the other. QED.

### Corollary 3 — Exact witnessed-degree formulas

For every PETRA form `P`,

```text
number of witnessed ADD classes out of P
= number of Aut(P)-orbits on node occurrences,
```

and

```text
number of witnessed REMOVE classes out of P
= number of Aut(P)-orbits on non-root leaf occurrences.
```

Here orbit counts are realization-independent even though a literal action requires a chosen realization.

## 6. From witnessed classes to unpointed successors

Forgetting witness data maps witnessed edit classes onto unpointed successor forms.

### Proposition 1 — Orbit-equivalent targets have equal unpointed successors

Targets in the same automorphism orbit yield the same unpointed successor form, for both ADD and REMOVE.

#### Proof

By Theorems 3 and 4 they determine the same witnessed edge class, and forgetting the witness preserves its endpoint form. QED.

### Corollary 4 — Degree bounds refined by orbit counts

Let

```text
orb_ADD(P)
```

be the number of node-occurrence orbits, and let

```text
orb_REMOVE(P)
```

be the number of non-root-leaf orbits.

Then

```text
#ADD_successors(P) <= orb_ADD(P) <= size(P)
```

and

```text
#REMOVE_successors(P) <= orb_REMOVE(P) <= leaves(P)-[root is a leaf].
```

The first inequalities may be strict only if distinct witnessed target-orbits collapse to the same unpointed endpoint.

## 7. Converse orbit theorem

Phase-6 external validation resolves the converse:

```text
same unpointed successor
=> same target orbit.
```

The external ingredients are classical tree-similarity results:

- Krasikov's branch-interchange theorem implies that if attaching one pendant leaf at `u` or `v` gives isomorphic **unrooted** trees, then `u` and `v` are automorphism-similar in the original tree;
- Harary–Palmer and Kirkpatrick–Klawe–Corneil show that removal-similar endvertices of a tree are automorphism-similar.

PETRA requires the automorphism to preserve the distinguished root. The following finite marker reduction supplies that bridge.

### Lemma 2 — Root-marker reduction

Let `T` be a finite rooted tree with root `r`. Attach to `r` a new marker centre `m`, and attach `D` fresh leaves to `m`, where

```text
D > |V(T)| + 2.
```

Call the resulting unrooted tree `T^*`.

Then every automorphism of `T^*` fixes `m` and `r`.

#### Proof

The marker centre `m` has degree `D+1`, strictly larger than the degree of every original vertex even after one PETRA ADD operation. Hence `m` is uniquely characterized by degree and is fixed by every automorphism.

Among the neighbours of `m`, exactly one — `r` — is not one of the `D` new marker leaves. Therefore every automorphism fixing `m` also fixes `r`. QED.

### Theorem 5 — ADD successor equality iff target-orbit equality

Let `u,v` be occurrences of a rooted realization `T`. Attaching one fresh leaf at `u` and at `v` yields the same PETRA successor form iff `u` and `v` lie in the same root-preserving `Aut(T)`-orbit.

#### Proof

The forward direction is the only new one.

Assume the two rooted ADD results are isomorphic. Attach the same marker of Lemma 2 at the root of both results. The rooted isomorphism extends over the identical marker, so the two marked trees are isomorphic as unrooted trees.

Apply Krasikov's theorem to the marked base tree `T^*`, taking one attached rooted tree to be a single edge and the other to be a single vertex. It follows that `u` and `v` are similar in `T^*`.

By Lemma 2 every automorphism of `T^*` fixes the original root `r`. Restricting the automorphism to the original vertices gives a root-preserving automorphism of `T` carrying `u` to `v`.

The reverse direction is Proposition 1. QED.

### Theorem 6 — REMOVE successor equality iff target-orbit equality

Let `u,v` be removable leaves of a rooted realization `T`. Deleting `u` and `v` yields the same PETRA predecessor form iff `u` and `v` lie in the same root-preserving `Aut(T)`-orbit.

#### Proof

Assume the two rooted deletion results are isomorphic. Attach the same marker of Lemma 2 to the root. Then in the marked unrooted tree `T^*`, the endvertices `u` and `v` are removal-similar.

The classical endvertex pseudosimilarity theorem implies that `u` and `v` are similar in `T^*`. Lemma 2 forces the witnessing automorphism to fix the original root, and restriction to `T` gives a root-preserving automorphism carrying `u` to `v`.

The reverse direction is Proposition 1. QED.

### Corollary 5 — Exact unpointed degree formulas

For every PETRA form `P`,

```text
#ADD_successors(P) = orb_ADD(P)
#REMOVE_successors(P) = orb_REMOVE(P).
```

Thus forgetting witnesses loses exactly automorphism symmetry for a **single** elementary ADD or REMOVE target. It does not introduce any additional one-step target collisions.

This does not contradict the residual-system obstruction from Phase 6: pairwise relative occurrence information can still be lost when two individually quotient-equivalent witnessed edges are considered together.

## 8. Marked-tree characterization of target orbits

The orbit problem itself has an exact representation-independent test.

### Definition 5 — Once-marked realization

For a realization `T` and occurrence `u`, let

```text
(T,u)
```

denote the rooted tree `T` with exactly `u` distinguished by a mark.

Isomorphisms of marked realizations must preserve both the root and the mark.

### Lemma 1 — Orbit iff marked realizations are isomorphic

For occurrences `u,v` of the same realization `T`,

```text
u and v lie in the same Aut(T)-orbit
iff
(T,u) ~= (T,v)
```

as rooted once-marked trees.

#### Proof

An automorphism carrying `u` to `v` is exactly a root-preserving isomorphism from `(T,u)` to `(T,v)` preserving the distinguished mark. QED.

This gives a direct canonical-combinatorial method for computing target orbits in bounded experiments without enumerating the full automorphism group.

## 9. Global edit-graph automorphisms

Let

```text
E_P
```

be the undirected unpointed PETRA edit graph from the grading/edit-geometry layer.

### Definition 6 — Global edit-graph automorphism group

Define

```text
Aut(E_P)
```

to be the group of graph automorphisms of `E_P`.

This is a different object from `Aut(P)`: the former permutes PETRA forms globally; the latter permutes occurrences inside one realization while fixing its form.

### Theorem 7 — `Z` is graph-theoretically distinguished

`Z` is the unique vertex of degree one in `E_P`.

#### Proof

`Z` has no REMOVE successor and exactly one ADD successor, obtained by adding a leaf at its unique occurrence. Hence its degree is one.

Now let `P != Z`. Since `size(P)>=2`, `P` has at least one non-root leaf, hence at least one REMOVE neighbor of size `size(P)-1`.

Every form also has at least one ADD neighbor of size `size(P)+1`, obtained by adding a leaf at any occurrence. A REMOVE neighbor and an ADD neighbor cannot coincide because their sizes differ. Hence every `P != Z` has degree at least two.

Therefore `Z` is the unique degree-one vertex. QED.

### Corollary 6 — Every global edit-graph automorphism fixes `Z`

Every element of `Aut(E_P)` fixes `Z`.

#### Proof

Graph automorphisms preserve vertex degree, and `Z` is uniquely characterized by degree one. QED.

### Theorem 8 — Distance from `Z` equals rank

For every PETRA form `P`,

```text
d(Z,P) = size(P)-1.
```

#### Proof

The size lower bound gives

```text
d(Z,P) >= size(P)-size(Z) = size(P)-1.
```

AIP-4 constructibility gives an ADD-only path from `Z` to `P` of exactly `size(P)-1` steps. Hence equality holds. QED.

### Corollary 7 — Global graph automorphisms preserve size exactly

For every

```text
F in Aut(E_P)
```

and every PETRA form `P`,

```text
size(F(P)) = size(P).
```

#### Proof

By Corollary 6, `F(Z)=Z`. Graph automorphisms preserve distance, so

```text
d(Z,F(P))
= d(F(Z),F(P))
= d(Z,P).
```

Apply Theorem 8 to both sides. QED.

### Corollary 8 — Global graph automorphisms preserve each rank layer and the canonical bipartition

Every global edit-graph automorphism preserves every set

```text
{P : size(P)=n}
```

setwise. In particular it preserves, rather than exchanges, the even/odd size bipartition.

### Remark 1 — Global rigidity is not yet proved

The previous results severely constrain `Aut(E_P)`, but they do not prove that every global graph automorphism is the identity.

To prove global rigidity one would need to show, for example, that every form is determined graph-theoretically by already-fixed lower layers or by some other intrinsic neighborhood signature. No such reconstruction theorem is assumed here.

## 10. What is established

This note proves internally:

- automorphism-group isomorphism type is independent of realization;
- the recursive semidirect/wreath-product decomposition of `Aut(P)`;
- the automorphism-count recurrence;
- the recursive rigidity criterion;
- ADD-target automorphism orbits classify witnessed ADD edge classes exactly;
- REMOVE-target automorphism orbits classify witnessed REMOVE edge classes exactly;
- same-orbit targets necessarily have the same unpointed successor;
- conversely, equal unpointed ADD successors imply equal ADD-target orbits;
- conversely, equal unpointed REMOVE predecessors imply equal REMOVE-target orbits;
- unpointed ADD/REMOVE degree equals the corresponding target-orbit count exactly;
- target orbits are characterized by once-marked rooted-tree isomorphism;
- `Z` is the unique degree-one vertex of the global edit graph;
- every global edit-graph automorphism fixes `Z`;
- distance from `Z` equals `size-1`;
- every global edit-graph automorphism preserves size/rank layers exactly.

## 11. What remains open

This note does **not** establish:

- triviality or a complete classification of `Aut(E_P)`;
- rooted reconstruction of a PETRA form from the **set** of its lower neighbours in every rank;
- reconstruction of a PETRA form from its lower-neighbor data;
- novelty relative to established rooted-tree automorphism, wreath-product, reconstruction, or graph-automorphism theory;
- any normative runtime or SPEC consequence.

These belong to later Phase-5 work or Phase-6 external validation.

## 12. Evidence discipline

The group decomposition, orbit classification of witnessed edits, rigidity criterion, and global graph constraints above are mathematical statements proved from the canonical carrier and established Phase-5 edit theory.

The accompanying bounded probe is permitted to search for target-orbit collisions and to corroborate the recursive automorphism counts. Such bounded results remain computational evidence unless converted into explicit general proofs or counterexamples.