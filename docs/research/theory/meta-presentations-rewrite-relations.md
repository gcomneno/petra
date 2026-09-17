# PETRA meta-theory — presentations and rewrite relations

Status: **research formalization** for issue #287 under Phase 5 of the complete-theory programme #276.

This note studies edit paths built from the elementary AIP-4 ADD/REMOVE relations. It does not change the canonical carrier, runtime, SPEC, or interpretation theory.

The central distinction is between:

1. PETRA forms;
2. individual elementary edit witnesses;
3. finite paths of such witnesses;
4. equations between paths.

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

AIP-4 gives converse unpointed relations

```text
P --ADD--> Q
P --REMOVE--> Q.
```

At realization level, an ADD chooses an occurrence and attaches one fresh zero-child occurrence below it. A REMOVE chooses a non-root zero-child occurrence and deletes that occurrence together with its incoming incidence.

The quotient from realizations to PETRA forms forgets persistent occurrence identity. Therefore an unpointed edge records existence of an elementary edit, but not necessarily a unique target witness.

## 2. Witnessed elementary edits

### Definition 1 — Witnessed edit

A **witnessed ADD** from a PETRA form `P` to a PETRA form `Q` is an isomorphism class of triples

```text
(T, u, T')
```

where:

- `T` is a concrete finite rooted non-plane realization of `P`;
- `u` is an occurrence of `T`;
- `T'` is obtained from `T` by attaching one fresh zero-child occurrence as a child of `u`;
- `T'` realizes `Q`.

Two such triples are identified when there is a root-preserving isomorphism of source realizations carrying the chosen target occurrence to the chosen target occurrence and extending to an isomorphism of the edited realizations that carries the fresh leaf to the fresh leaf.

A **witnessed REMOVE** is defined dually by a triple

```text
(T, e, T')
```

where `e` is a non-root zero-child occurrence of `T` and `T'` is obtained by deleting `e` and its incoming incidence.

### Remark 1 — Why witnesses are retained

At the form level, several realization-local targets may collapse to the same unpointed successor. Path equations involving cancellation or commutation need to know which elementary edit is being reversed or transported. Witnessed edits retain exactly that local information without introducing persistent global occurrence identity into the PETRA carrier.

### Definition 2 — Witnessed edit graph

Let `W_P` be the directed multigraph whose vertices are PETRA forms and whose directed edges are witnessed elementary ADD and REMOVE edits.

Multiple witnessed edges may have the same source and target forms.

Forgetting witnesses gives the AIP-4 unpointed relations.

## 3. Free path category

### Definition 3 — Edit path

A witnessed edit path is a finite composable sequence

```text
e_1 ; e_2 ; ... ; e_k
```

of edges of `W_P`.

The empty path at `P` is written `id_P`.

### Theorem 1 — Witnessed paths form the free category on `W_P`

PETRA forms as objects and finite witnessed edit paths as arrows form a category under path concatenation. This category is the free category on the directed multigraph `W_P`.

#### Proof

Concatenation of composable finite edge sequences is associative. The empty path at each vertex is a left and right identity. By construction there are no equations between non-identical paths beyond those forced by associativity and identities. This is precisely the free category on a directed multigraph. QED.

### Remark 2 — Not yet a groupoid

The free path category itself is not a groupoid: an ADD edge and its reversing REMOVE edge are distinct generators, and their composites are length-two paths rather than identities until cancellation relations are imposed.

## 4. Elementary inverse witnesses

### Definition 4 — Reverse witness

For every witnessed ADD edge

```text
e : P -> Q
```

let

```text
e^{-1} : Q -> P
```

be the witnessed REMOVE that deletes the particular fresh leaf introduced by `e`.

For every witnessed REMOVE edge, define its reverse witnessed ADD by reattaching one fresh zero-child occurrence at the same parent location in the surviving realization.

The reverse is defined at witness level, modulo the isomorphism relation of Definition 1.

### Lemma 1 — Reverse witness is well-defined and involutive

For every witnessed elementary edit `e`, the reverse witness `e^{-1}` is well-defined and

```text
(e^{-1})^{-1} = e.
```

#### Proof

Changing representatives of a witnessed edit by a root-preserving witness-respecting isomorphism transports the edited parent, deleted or inserted leaf, and incoming incidence accordingly. Reversing before or after this transport yields isomorphic witnessed edits. Hence reversal is independent of representatives.

Applying reversal twice restores the original local edit witness up to the same witness-isomorphism relation. QED.

### Definition 5 — Elementary cancellation congruence on paths

Let `≡_inv` be the least path congruence containing

```text
e ; e^{-1} ≡_inv id_source(e)
```

and

```text
e^{-1} ; e ≡_inv id_target(e)
```

for every witnessed elementary edit `e`.

A path congruence means an equivalence relation on parallel paths that is stable under concatenation on either side.

### Theorem 2 — Quotient by inverse cancellation is a groupoid

The quotient of the free path category by `≡_inv` is a groupoid.

#### Proof

For a path

```text
p = e_1 ; ... ; e_k
```

define the reversed path

```text
p^{-1} = e_k^{-1} ; ... ; e_1^{-1}.
```

Repeated elementary cancellations give

```text
p ; p^{-1} ≡_inv id
```

and

```text
p^{-1} ; p ≡_inv id.
```

Thus every arrow class has an inverse. QED.

### Remark 3 — This is a formal path quotient

The groupoid of Theorem 2 is a path-level construction. It does not assert that two arbitrary paths with equal endpoints are equivalent. Additional path relations are needed for that stronger statement.

## 5. Independent edits and commutation

We next isolate a relation that is genuinely induced by tree structure rather than imposed formally.

### Definition 6 — Independent elementary edits in a realization

Let two elementary edits be specified on the same concrete realization `T`.

They are **independent** when their chosen existing target occurrences are distinct.

Concretely:

- ADD/ADD: the two chosen target occurrences are distinct;
- REMOVE/REMOVE: the two chosen leaf occurrences are distinct;
- ADD/REMOVE: the ADD target occurrence is not the leaf occurrence deleted by REMOVE.

For REMOVE/ADD use the symmetric condition.

Because a removable occurrence is a leaf, distinctness is enough: deleting one leaf cannot delete or retarget another existing occurrence, and adding a fresh leaf at another occurrence cannot invalidate the removable leaf.

### Theorem 3 — Independent elementary edits commute up to realization isomorphism

Let `a` and `b` be independent elementary edits on a realization `T`. Performing `a` and then the transported residual of `b` yields a realization isomorphic, by an isomorphism fixing all occurrences that existed in `T`, to the realization obtained by performing `b` and then the transported residual of `a`.

Therefore the two length-two witnessed paths have the same PETRA endpoint.

#### Proof

Consider the possible pairs.

**ADD/ADD.** Each edit adds one fresh leaf at a distinct existing occurrence. Neither operation changes any existing incidence. Performing the additions in either order produces the same original realization plus one new leaf at each chosen target. The two results differ at most by the names assigned to the two fresh occurrences and are therefore root-preserving isomorphic while fixing every original occurrence.

**REMOVE/REMOVE.** The two targets are distinct leaves of the original realization. Distinct leaves cannot be ancestors of one another. Removing either leaf does not affect the other leaf or its parent incidence. Deleting both leaves in either order therefore yields the same surviving rooted incidence structure.

**ADD/REMOVE.** Let the ADD target be `u` and let the removed leaf be `e`, with `u != e`. Adding a fresh child below `u` does not change `e` or its incoming incidence, so `e` remains removable. Removing `e` does not delete `u`, because `e` is a leaf distinct from `u`. Hence both orders are valid and result in the same old occurrences except for deletion of `e`, together with one fresh leaf below `u`. The two results are isomorphic fixing every surviving old occurrence.

The REMOVE/ADD case is symmetric. QED.

### Corollary 1 — Independent-edit square

Independent edits determine a commuting square of PETRA forms

```text
        a
   P ------> P_a
   |           |
 b |           | b/a
   v           v
  P_b -----> P_ab
        a/b
```

where `b/a` and `a/b` are the residual edits transported after the other edit.

The two length-two paths have the same endpoint form.

### Remark 4 — Same target is not covered

Two ADDs at the same occurrence may also produce the same endpoint independent of order, but they are not called independent here. Likewise an ADD at a leaf followed by removal of that same original leaf is not an independent pair: after the ADD, the original leaf is no longer removable, while removing it first destroys the ADD target.

The theorem states a sufficient condition, not a complete characterization of all commuting edit pairs.

## 6. Commutation path relation

### Definition 7 — Independent-commutation congruence

Let `≡_comm` be the least path congruence containing, for every independent-edit square,

```text
a ; (b/a) ≡_comm b ; (a/b).
```

Let

```text
≡_loc
```

be the least path congruence generated jointly by inverse cancellation and independent commutation.

Thus `≡_loc` contains exactly the equations forced by the selected local generators before any completeness theorem is asserted.

## 7. Reduced paths

### Definition 8 — Immediately reducible and reduced paths

A path is **immediately reducible** when it contains an adjacent pair

```text
e ; e^{-1}
```

or

```text
e^{-1} ; e.
```

A path is **reduced** when it contains no such adjacent inverse pair.

### Theorem 4 — Every finite path reduces by cancellation to a reduced path

Every witnessed edit path is `≡_inv`-equivalent to at least one reduced path.

#### Proof

If the path contains an adjacent inverse pair, delete that pair using an elementary cancellation relation. Each deletion reduces path length by two. Since path length is a natural number, the process terminates after finitely many deletions. The resulting path contains no adjacent inverse pair and is therefore reduced. QED.

### Remark 5 — No uniqueness claim

Theorem 4 proves termination of elementary cancellation, not uniqueness of a reduced representative and not confluence of cancellation combined with commutation.

## 8. Reduced does not imply geodesic

### Proposition 1 — A reduced edit path can be non-geodesic

There exists a reduced witnessed edit path whose endpoints are adjacent in the unpointed edit graph.

#### Proof

Let

```text
S = Node({Z}).
```

Choose its root `r` and its unique child leaf `c` in a realization.

Let `a` be ADD at the root and `b` be ADD at the leaf `c`.

Then:

```text
A = a(S) = Node({Z,Z}),
B = b(S) = Node({Node({Z})}),
C = a(b(S)) = b(a(S)) = Node({Z,Node({Z})}).
```

By Theorem 3, `a` and `b` commute because their targets `r` and `c` are distinct original occurrences.

Consider the path

```text
S --b--> B --a/b--> C --(b/a)^{-1}--> A.
```

It has length three. No two consecutive edges are an edit immediately followed by its reverse: the first two are ADDs, while the final REMOVE reverses the first ADD only after the independent ADD `a` has intervened. Therefore the path is reduced.

But `S` and `A` are adjacent by the single ADD `a`, so

```text
d(S,A)=1.
```

Hence the reduced length-three path is not geodesic. QED.

### Corollary 2 — Immediate cancellation is not a complete shortest-path reduction system

Deleting adjacent inverse pairs alone cannot characterize geodesics in the PETRA edit graph.

## 9. Local shortening through a commuting square

The previous counterexample also identifies the additional local mechanism responsible for that non-geodesicity.

### Proposition 2 — Cancellation after commutation shortens the square detour

In the setting of Proposition 1,

```text
b ; (a/b) ; (b/a)^{-1}
```

is `≡_loc`-equivalent to the one-edge path `a`.

#### Proof

Independent commutation gives

```text
b ; (a/b)
≡_loc
a ; (b/a).
```

Therefore

```text
b ; (a/b) ; (b/a)^{-1}
≡_loc
a ; (b/a) ; (b/a)^{-1}
≡_loc
a.
```

QED.

This shows why both cancellation and commutation belong in a plausible local presentation.

## 10. Relation to geodesic normal form

Phase-5 edit geometry already proves that for every pair `P,Q` there exists a geodesic

```text
P --REMOVE*--> S --ADD*--> Q
```

through a maximum-size common reduct `S`.

### Theorem 5 — Every endpoint pair has a geodesic monotone normal-form representative

For every `P,Q`, at least one shortest unpointed edit path has all REMOVE steps before all ADD steps.

#### Proof

This is the geodesic-normal-form theorem established in the grading/edit-geometry layer. QED.

### Remark 6 — Path-equivalence statement is stronger and remains open

Theorem 5 is existential: it says that a geodesic of REMOVE*ADD* shape exists.

It does **not** prove that every geodesic witnessed path is `≡_loc`-equivalent to such a path, nor that every arbitrary path can be transformed to a geodesic using only inverse cancellation and independent commutation.

Those are presentation-completeness questions.

## 11. Candidate PETRA edit presentation

The natural current candidate is:

```text
generators:
  witnessed elementary ADD edges
  witnessed elementary REMOVE edges

relations:
  e ; e^{-1} = id
  e^{-1} ; e = id
  a ; (b/a) = b ; (a/b)     for independent edits
  witness transport under realization isomorphism
```

The final line is already built into Definition 1 by taking witnessed edits modulo witness-respecting realization isomorphism.

### Definition 9 — Local presentation quotient

Call the path quotient by `≡_loc` the **local presentation quotient**.

This name is intentionally descriptive rather than canonical. No completeness claim is built into the definition.

## 12. Completeness question

### Open Problem 1 — Are local relations complete for endpoint equality?

Let `p` and `q` be witnessed edit paths with the same source and the same target PETRA forms.

Must

```text
p ≡_loc q
```

hold?

Equivalently: do inverse cancellations and independent-edit commutations generate all path equalities induced by PETRA endpoint structure?

This note does not prove the statement and does not assume it.

There are at least three reasons for caution:

1. unpointed endpoint equality can arise from nontrivial automorphisms;
2. edits at the same or structurally symmetric targets may yield equal endpoint forms without satisfying the chosen independence criterion;
3. dependency-changing edit sequences may create endpoint coincidences not decomposable into obvious commuting squares.

A bounded cycle search can provide evidence or counterexamples, but not a general proof of completeness.

## 13. Cycle structure

### Proposition 3 — Every unpointed edit cycle has even length

Every cycle in the PETRA edit graph has even length.

#### Proof

The edit graph is bipartite by size parity. Every cycle in a bipartite graph has even length. QED.

### Proposition 4 — Independent pairs generate length-four squares

Whenever two independent edits from the same realization produce distinct intermediate PETRA forms and a distinct final form, Corollary 1 gives a length-four cycle in the unpointed edit graph.

#### Proof

The commuting square provides four edit edges. Under the stated distinctness assumptions its four vertices are distinct, so its boundary is a length-four cycle. QED.

### Remark 7 — Degenerate squares

Automorphisms or quotienting to forms may identify one or both intermediate vertices, so a realization-level commuting square need not always appear as a four-vertex square in the unpointed graph.

### Open Problem 2 — Cycle generation

It remains open here whether every edit-graph cycle is generated, in an appropriate path-homotopy sense, by:

- immediate backtracks; and
- independent-edit commuting squares.

No median-graph, cubical, CAT(0), or simply connected square-complex conclusion is drawn.

## 14. Automorphism-sensitive targeting

A PETRA form is an isomorphism class, while witnessed edits remember a realization-local target modulo witness-respecting automorphism.

Consequently three multiplicities must remain distinct:

```text
number of realization-level target occurrences
number of witnessed edit classes
number of distinct unpointed successor forms
```

The first can exceed the second because automorphic targets collapse. The second can exceed the third because non-automorphic targets are not yet proved always to yield distinct successor forms.

This note therefore never identifies form-level paths with unique sequences of occurrence targets.

## 15. What is established

This note proves internally:

- witnessed elementary edits form a directed multigraph over PETRA forms;
- finite witnessed edit paths form the free category on that multigraph;
- every witnessed elementary edit has a well-defined reverse witness;
- quotienting paths by elementary inverse cancellation yields a groupoid;
- elementary edits at distinct existing target occurrences commute up to realization isomorphism under the explicit independence criterion;
- independent edits determine commuting squares;
- every finite path can be reduced by deleting adjacent inverse pairs;
- reduced does not imply geodesic;
- cancellation plus independent commutation can shorten the canonical square detour;
- every endpoint pair has an existential REMOVE*ADD* geodesic from the previous geometry theorem;
- every edit-graph cycle has even length;
- independent edits provide a canonical source of length-four squares.

## 16. What remains open

This note does **not** establish:

- uniqueness of reduced paths;
- confluence of cancellation and commutation;
- that every geodesic is locally equivalent to every other geodesic;
- completeness of the candidate presentation;
- that every cycle is generated by commuting squares and backtracks;
- a presentation of the unpointed edit graph with no witness data;
- an exact classification of automorphism-induced path collapse;
- any median, cubical, CAT(0), modular, or related global geometry;
- novelty relative to established rewriting, trace, event-structure, or rooted-tree edit theory;
- any normative runtime or SPEC consequence.

These belong to later Phase-5 work or Phase-6 external validation.

## 17. Evidence discipline

All theorems above are internal consequences of the canonical PETRA carrier and elementary edit definitions.

A bounded executable probe may later search short cycles and test whether every small equal-endpoint path pair is generated by the selected local relations. Such results would remain computational evidence unless converted into explicit mathematical proofs or counterexamples.