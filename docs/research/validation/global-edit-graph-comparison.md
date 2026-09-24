# PETRA Phase 6 — global edit-graph literature comparison

Status: **Phase 6 external-validation note** for issue #305 under programme #276.

This note compares PETRA's local target-orbit questions and the global infinite edit graph with classical tree similarity and reconstruction literature. It does not modify the normative PETRA SPEC.

## 1. Object under study

The unpointed PETRA edit graph `E_P` has one vertex for each finite rooted unlabeled non-plane tree form and an undirected edge exactly when one form is obtained from the other by adding/removing one non-root leaf.

It is graded by `size`, and internally `d(Z,P)=size(P)-1`.

Four notions must remain separate: automorphisms inside one rooted tree, orbit-equivalence of edit targets, reconstruction of one tree from deletion data, and automorphisms of the infinite graph `E_P`.

## 2. Local target collisions: classical pseudosimilarity is directly relevant

For an ordinary tree, vertices are *similar* when an automorphism maps one to the other and *removal-similar* when their vertex-deleted trees are isomorphic. Removal-similar but non-similar vertices are pseudosimilar.

Kirkpatrick–Klawe–Corneil characterize pseudosimilarity in trees. The classical endvertex result says that two removal-similar leaves cannot be pseudosimilar.

That theorem is operation-exact for PETRA REMOVE except for one convention: PETRA automorphisms must preserve the root.

## 3. ADD collision: Krasikov's branch-interchange theorem

Krasikov proves a stronger attachment theorem. If `A` and `B` are non-isomorphic rooted trees and interchanging their attachment at vertices `a,b` of a tree `T` yields isomorphic trees, then `a,b` are similar in `T`.

Taking `A` to be a one-edge rooted tree and `B` a single vertex says precisely:

```text
attach a new leaf at a
       isomorphic to
attach a new leaf at b
    => a and b are automorphism-similar.
```

This is the exact unrooted analogue of the PETRA ADD successor-collision question.

## 4. Root-preserving bridge

PETRA's distinguished root is handled by a finite marker reduction. Attach at the root a new centre with more fresh leaf neighbours than any original vertex can have. The centre is then uniquely recognized by degree and its unique non-marker neighbour is the old root.

Applying the classical unrooted theorem after this marking forces the resulting automorphism to fix the PETRA root. The marker is auxiliary proof machinery only; it is not added to the PETRA carrier.

Therefore both previously open one-step converse questions close:

```text
same ADD successor    iff same ADD-target orbit
same REMOVE predecessor iff same REMOVE-target orbit
```

and consequently the unpointed one-step degree equals the appropriate target-orbit count.

## 5. Why this does not repair the residual-system failure

The residual-system audit found loss of **joint** occurrence information. In `Node({Z,Z})`, two distinct symmetric leaf removals and self-removal collapse to the same ordered pair of individual witnessed edge classes.

The new theorem concerns one target at a time. It proves there are no additional one-step successor collisions beyond automorphism symmetry. It does not restore relative identity for pairs of symmetric occurrences.

## 6. Lower-neighbour reconstruction: false for PETRA sets

The exact rooted multiset analogue is known. Kostochka–Nahvi–West–Zirlin define an `rc1-card` exactly by deleting one non-root leaf while preserving the root, and prove rooted trees reconstructible from the resulting **multiset**.

PETRA's unpointed lower neighbourhood is weaker: it keeps only the **set of distinct predecessor forms**.

That loss of multiplicity is already fatal at size three.

Let

```text
C = Node({Node({Z})})
S = Node({Z,Z}).
```

These are non-isomorphic rooted trees: `C` is the rooted chain of length two below the root, while `S` is the rooted star with two leaf children.

Deleting the unique non-root leaf of `C` gives

```text
Node({Z}).
```

Deleting either leaf of `S` gives the same rooted predecessor

```text
Node({Z}).
```

Hence

```text
Lower(C) = { Node({Z}) } = Lower(S),
```

although `C != S`.

The multiset decks remain different: `C` has one such card, while `S` has two. This is exactly why the rooted reconstruction theorem does not imply PETRA set reconstruction.

Therefore:

```text
rooted lower-neighbour set reconstruction    FALSE
```

No larger search or probe is needed to refute the universal statement.

## 7. Rooted reconstruction literature is not automatically operation-exact

Recent rooted-tree reconstruction results exist. For example, Andriantiana–Wagner reconstruct rooted forests with at least three leaves from maximal leaf-induced proper subforests.

Their `leaf-induced` operation keeps unions of root-to-selected-leaf paths; omitting one leaf can therefore remove an entire exclusive tail, not merely one leaf vertex. It is not PETRA REMOVE.

This is useful context but not a proof about `E_P`.

## 8. Global graph automorphisms

PETRA internally proves that `Z` is the unique degree-one vertex. Hence every automorphism of `E_P` fixes `Z`. Since graph automorphisms preserve graph distance and `d(Z,P)=size(P)-1`, every global automorphism preserves every size layer.

The generic graph-theoretic part is standard; the rank formula is PETRA-specific. This result is best classified **SPECIALIZED**, not novel.

The proposed induction from lower-neighbour sets cannot work as stated, because the size-three chain and star have identical lower-neighbour sets.

This does **not** produce a nontrivial automorphism of the global graph: upper-neighbour structure may still distinguish the two vertices. It only kills this particular reconstruction route.

Therefore:

```text
global Aut(E_P) triviality    OPEN
```

## 9. Phase-6 classification

```text
individual rooted-tree automorphism decomposition     SPECIALIZED
one-step ADD successor-orbit converse                 SPECIALIZED
one-step REMOVE predecessor-orbit converse            SPECIALIZED
exact unpointed one-step degree = orbit count         SPECIALIZED
fix Z / preserve rank under global automorphisms      SPECIALIZED
rooted lower-neighbour set reconstruction             FALSE
global Aut(E_P) triviality                            OPEN
```

No absence of a global-rigidity theorem is treated as evidence of novelty.

## 10. Consequence for the global question

The lower-neighbour-set route is closed negatively by the smallest nontrivial collision.

The remaining global question is therefore still

```text
Aut(E_P) triviality    OPEN
```

but any future proof must use more graph-theoretic information than the set of lower neighbours alone — for example upper neighbours or a richer multi-layer signature.

No such stronger programme is started here. No Phase-7 promotion follows from this note.
