# AIP-5 — PETRA interpretation theory

Status: **research formalization** for issue #281 under the complete-theory programme #276.

This note defines what it means to assign external meaning to PETRA after the carrier and elementary edit algebra have already been fixed. It is deliberately independent of arithmetic, historical runtime representation, positional ranks, serialization, and application-specific values.

The governing dependency invariant is:

```text
interpretation depends on PETRA
PETRA does not depend on interpretation
```

Nothing in an interpretation may retroactively change PETRA structural equality, carrier membership, or intrinsic ADD/REMOVE legality.

## 1. Source structure

Let `P` denote the canonical PETRA carrier established under #277/#278 and corrected under #279/#280.

A PETRA form is a root-preserving isomorphism class of finite rooted non-plane tree realizations. Under the recursive presentation,

```text
P ::= Node(M_f(P)),
```

where `M_f(P)` is the set of finite multisets of PETRA forms.

Let

```text
Z = Node(empty).
```

AIP-4 also supplies two intrinsic unpointed edit relations on `P`:

```text
P --ADD--> Q
P --REMOVE--> Q
```

induced by pointed elementary node addition and zero-child leaf removal, respectively.

This note treats the carrier structure and the edit structure separately before considering interpretations that preserve both.

## 2. Multiset lifting

### Definition 1 — Multiset lifting of a map

For a map

```text
f : X -> Y,
```

define

```text
M_f(f) : M_f(X) -> M_f(Y)
```

by applying `f` independently to every multiset copy, preserving multiplicity.

Thus if

```text
M = {x_1, ..., x_n}
```

with repetitions counted, then

```text
M_f(f)(M) = {f(x_1), ..., f(x_n)}.
```

No sibling order is introduced by this lifting.

## 3. Arbitrary interpretations

### Definition 2 — Arbitrary interpretation

Let `X` be any set. An **arbitrary interpretation** of PETRA in `X` is simply a function

```text
I : P -> X.
```

The pair `(X,I)` is an arbitrary PETRA interpretation.

This is the weakest possible notion. It asserts only that equal PETRA forms receive one well-defined target value because `I` is defined on the quotient carrier `P` itself.

### Remark 1 — What arbitrary interpretation does not mean

An arbitrary interpretation need not preserve:

- recursive `Node` construction;
- size, depth, multiplicity, or any other structural invariant;
- ADD/REMOVE steps;
- distinctness of PETRA forms;
- any target operation or relation.

Therefore the word **interpretation** alone carries no preservation theorem.

### Proposition 1 — Every carrier map is an arbitrary interpretation

Every function `I : P -> X` is an arbitrary PETRA interpretation, and no additional PETRA property follows from this fact alone.

#### Proof

This is Definition 2. The absence of additional conclusions follows because Definition 2 imposes no equations or relation-preservation conditions beyond being a function on `P`. QED.

## 4. Structural interpretations

### Definition 3 — Finite-multiset target algebra

A **finite-multiset target algebra** is a pair

```text
(X, alpha)
```

with a structure map

```text
alpha : M_f(X) -> X.
```

The map `alpha` specifies how a finite unordered multiset of already-interpreted child values is combined into one target value.

No injectivity, surjectivity, associativity, arithmetic meaning, or edit semantics are assumed.

### Definition 4 — Structural interpretation

A map

```text
I : P -> X
```

is a **structural interpretation** into `(X,alpha)` when, for every finite multiset `M` of PETRA forms,

```text
I(Node(M)) = alpha(M_f(I)(M)).
```

Equivalently, the diagram

```text
M_f(P)  --Node-->   P
  |                 |
M_f(I)             I
  |                 |
  v                 v
M_f(X) --alpha-->   X
```

commutes.

This is the exact sense in which the recursive PETRA constructor is preserved.

### Theorem 1 — Structural recursion theorem

For every finite-multiset target algebra `(X,alpha)`, there exists a unique structural interpretation

```text
fold_alpha : P -> X
```

satisfying

```text
fold_alpha(Node(M))
    = alpha(M_f(fold_alpha)(M))
```

for every finite multiset `M` of PETRA forms.

#### Proof — existence

Define `fold_alpha` by induction on PETRA size.

For the unique size-one form `Z = Node(empty)`, set

```text
fold_alpha(Z) = alpha(empty).
```

Assume `fold_alpha` has been defined for all PETRA forms of size strictly less than `n`. Let `P = Node(M)` have size `n`. Every child form occurring in `M` has size strictly less than `n`, so its image is already defined. Set

```text
fold_alpha(P) = alpha(M_f(fold_alpha)(M)).
```

Carrier equality is recursive multiset equality modulo structural isomorphism, while `M_f` is insensitive to sibling order and preserves multiplicity. Hence this value depends only on the PETRA form, not on a chosen realization or ordering. Thus the definition is well-defined for every finite size. QED.

#### Proof — uniqueness

Let `f,g : P -> X` both satisfy the structural equation. Proceed by induction on PETRA size.

For `Z`,

```text
f(Z) = alpha(empty) = g(Z).
```

Suppose `f(Q)=g(Q)` for every form `Q` of size smaller than `n`, and let `P=Node(M)` have size `n`. Every child in `M` has smaller size, hence

```text
M_f(f)(M) = M_f(g)(M).
```

Applying `alpha` gives

```text
f(P) = alpha(M_f(f)(M))
     = alpha(M_f(g)(M))
     = g(P).
```

Therefore `f=g`. QED.

### Corollary 1 — Initial-algebra property, internally established

The recursive PETRA carrier has the universal property that for every finite-multiset algebra `(X,alpha)` there is exactly one homomorphism from `(P,Node)` to `(X,alpha)`.

This is the usual form of an initial-algebra property. The theorem above establishes the property internally; terminology and relation to established literature still require external validation before novelty or canonical-literature claims.

### Definition 5 — Carrier homomorphism

A structural interpretation is equivalently a homomorphism of the finite-multiset algebras

```text
(P,Node) -> (X,alpha).
```

The word **homomorphism** is used here only because the source and target signatures have been stated explicitly.

## 5. Faithfulness

### Definition 6 — Faithful interpretation

An interpretation

```text
I : P -> X
```

is **faithful on forms** when it is injective:

```text
I(P) = I(Q)  =>  P = Q.
```

Faithfulness means that the target value retains enough information to reconstruct which PETRA form was interpreted.

It does not, by itself, say that PETRA operations or recursive construction are preserved.

### Proposition 2 — Structural preservation does not imply faithfulness

There exists a structural interpretation that maps every PETRA form to the same target value.

#### Proof

Take the singleton set

```text
X = {*}
```

and define

```text
alpha(M) = *
```

for every finite multiset `M` over `X`.

By Theorem 1 there is a unique structural interpretation `fold_alpha : P -> X`; necessarily it sends every PETRA form to `*`. Since PETRA has distinct forms, for example

```text
Z != Node({Z}),
```

this interpretation is not injective. QED.

### Corollary 2 — Structure preservation and information preservation are independent notions

A structural homomorphism may intentionally collapse structural distinctions. Faithfulness must therefore be stated separately.

## 6. Edit interpretations

### Definition 7 — Target edit structure

A **target edit structure** is a triple

```text
(X, A_X, R_X)
```

where `A_X` and `R_X` are binary relations on `X` intended to receive PETRA ADD and REMOVE steps.

No assumption is made that these target relations are functions, inverses, deterministic, or generated by concrete target operations.

### Definition 8 — AIP-4 algebra-preserving interpretation

An interpretation

```text
I : P -> X
```

is **edit-preserving** into `(X,A_X,R_X)` when

```text
P --ADD--> Q     =>     I(P) A_X I(Q),
P --REMOVE--> Q  =>     I(P) R_X I(Q).
```

This is preservation of the unpointed AIP-4 relation algebra.

### Definition 9 — Edit-reflecting interpretation

An edit-preserving interpretation is **edit-reflecting** when the converses also hold:

```text
I(P) A_X I(Q)    =>    P --ADD--> Q,
I(P) R_X I(Q)    =>    P --REMOVE--> Q.
```

Reflection is strictly stronger than preservation.

### Definition 10 — Strong edit interpretation

A **strong edit interpretation** is both edit-preserving and edit-reflecting.

### Remark 2 — Pointed versus unpointed semantics

AIP-4 pointed operations live on targeted realizations such as `(R,u)`, while the intrinsic carrier-level operations are the induced relations on `P`.

An interpretation `I : P -> X` has no occurrence target parameter and therefore naturally interprets the **unpointed relations**.

Interpreting pointed operations requires additional target-pointing structure and a separate map on pointed realizations. That is an extension of AIP-5, not something silently contained in a map on `P`.

## 7. Independence results between faithfulness and edit preservation

### Proposition 3 — Faithfulness alone does not imply edit preservation

There exists a faithful interpretation into a target edit structure that preserves no non-trivial PETRA edits.

#### Proof

Take

```text
X = P
```

and let

```text
I = identity_P.
```

This interpretation is injective. Define both target relations to be empty:

```text
A_X = empty relation,
R_X = empty relation.
```

PETRA has non-trivial ADD/REMOVE steps, but none can map to a target relation edge because there are no target edges. Therefore `I` is faithful but not edit-preserving. QED.

### Proposition 4 — Edit preservation does not imply reflection

There exists an edit-preserving interpretation that reflects neither ADD nor REMOVE.

#### Proof

Take again

```text
X = {*},
I(P) = *
```

for every PETRA form `P`, and define

```text
A_X = {(*,*)},
R_X = {(*,*)}.
```

Every PETRA ADD or REMOVE step maps to the unique target loop, so preservation holds.

Reflection fails. For any PETRA form `P`, the target relation `* A_X *` holds, but

```text
P --ADD--> P
```

is impossible because ADD increases size by exactly one. Similarly `P --REMOVE--> P` is impossible. QED.

### Proposition 5 — Structural preservation does not imply edit preservation

There exists a structural interpretation whose chosen target edit relations do not preserve AIP-4.

#### Proof

Use any structural interpretation, for example the singleton structural interpretation from Proposition 2, and choose empty target edit relations. Since PETRA has ADD/REMOVE edges, edit preservation fails. QED.

### Remark 3 — Distinct preservation axes

Carrier recursion, faithfulness, and edit preservation answer different questions:

```text
structural:  does recursive construction commute?
faithful:    are distinct PETRA forms kept distinct?
edit:        are ADD/REMOVE edges preserved?
```

No one of these properties should be inferred merely from another unless a theorem supplies additional hypotheses.

## 8. Embeddings of the PETRA edit graph

### Definition 11 — PETRA labeled edit graph

Define the labeled directed graph

```text
G_P = (P, ADD, REMOVE)
```

whose vertices are PETRA forms and whose two edge labels are the AIP-4 relations.

### Theorem 2 — Faithful strong edit interpretations are graph embeddings

Let

```text
I : P -> X
```

be injective, edit-preserving, and edit-reflecting into `(X,A_X,R_X)`.

Then `I` identifies `G_P` with the labeled subgraph of the target induced on the image `I(P)`: for every `P,Q`,

```text
P --ADD--> Q
iff
I(P) A_X I(Q),
```

and

```text
P --REMOVE--> Q
iff
I(P) R_X I(Q).
```

#### Proof

Preservation gives both forward implications and reflection gives both reverse implications. Injectivity identifies each source vertex with a unique image vertex, so no distinct PETRA forms are collapsed. Hence the labeled source graph is isomorphic to its image subgraph. QED.

### Corollary 3 — Reconstruction from a faithful strong edit image

Within the image of a faithful strong edit interpretation, both PETRA form identity and one-step AIP-4 adjacency are recoverable.

This does not imply recovery of realization-local occurrence targets, because those were never part of the unpointed carrier.

## 9. Combined PETRA models

### Definition 12 — Structural model

A **PETRA structural model** is a triple

```text
(X, alpha, I)
```

where `(X,alpha)` is a finite-multiset algebra and `I` is the unique structural interpretation supplied by Theorem 1.

### Definition 13 — Edit model

A **PETRA edit model** is a quadruple

```text
(X, A_X, R_X, I)
```

where `I : P -> X` is edit-preserving.

### Definition 14 — Full structure-and-edit model

A **full PETRA model** consists of

```text
(X, alpha, A_X, R_X, I)
```

such that:

1. `I` is the structural homomorphism from `(P,Node)` to `(X,alpha)`;
2. `I` preserves AIP-4 ADD and REMOVE relations.

Optional qualifiers are then stated separately:

```text
faithful       iff I is injective
strong-edit    iff I also reflects ADD/REMOVE
embedded       iff faithful + strong-edit
```

This note proposes **full PETRA model** as the useful default when both the recursive carrier and the intrinsic edit algebra matter. An arbitrary interpretation remains valid terminology but carries no structural guarantee.

## 10. Interpretation cannot feed back into PETRA

### Theorem 3 — Interpretation independence

Let `I : P -> X` be any arbitrary, structural, faithful, edit-preserving, strong, or full interpretation/model.

For PETRA forms `P,Q`, whether

```text
P = Q,
P --ADD--> Q,
P --REMOVE--> Q
```

holds is determined entirely in the PETRA source theory and is independent of the values `I(P)` and `I(Q)`.

#### Proof

Carrier equality is defined by source root-preserving structural isomorphism. ADD/REMOVE are defined by source elementary edit witnesses modulo that equality. None of these definitions quantifies over a target set, target algebra, target relation, or interpretation map. Therefore target meaning cannot alter any of the three source judgments. QED.

### Corollary 4 — External values are semantically downstream

Numbers, names, weights, labels, physical meanings, logical meanings, application states, or any other target values may be assigned by interpretations, but they cannot become PETRA structural identity merely because an interpretation uses them.

### Corollary 5 — Non-faithful models are legitimate

A model may intentionally identify distinct PETRA forms without changing PETRA itself. The collapse occurs in the model, not in the source carrier.

## 11. Historical arithmetic reading

The historical arithmetic motivation is not used in any definition or proof above.

If an arithmetic interpretation is retained, it must be presented as a concrete target model and separately checked against the hierarchy in this note:

```text
arbitrary?
structural?
faithful?
edit-preserving?
edit-reflecting?
full?
```

No status is granted merely because arithmetic historically motivated the project.

In particular, if two different PETRA forms or two different PETRA edit steps receive the same arithmetic image, that is a property of the arithmetic model and does not alter source equality or source reachability.

## 12. Current AIP-5 classification

The interpretation hierarchy is therefore:

```text
arbitrary interpretation
        |
        +-- structural interpretation / carrier homomorphism
        |       |
        |       +-- faithful structural interpretation
        |
        +-- edit-preserving interpretation
                |
                +-- edit-reflecting / strong edit interpretation

full PETRA model
= structural + edit-preserving

embedded full model
= structural + edit-preserving + edit-reflecting + faithful
```

The branches are not a total ordering: structural preservation, faithfulness, and edit preservation are independent properties unless combined explicitly.

## 13. What is proved here

This note establishes internally:

- the distinction between arbitrary, structural, faithful, edit-preserving, edit-reflecting, and full interpretations;
- a structural recursion theorem for every finite-multiset target algebra;
- uniqueness of the structural interpretation for a fixed target algebra;
- the corresponding initial-algebra universal property of the PETRA recursive carrier;
- an explicit structural-but-non-faithful model;
- an explicit faithful-but-not-edit-preserving interpretation;
- an explicit edit-preserving-but-not-reflecting interpretation;
- the labeled edit-graph embedding theorem for faithful strong interpretations;
- the interpretation-independence theorem.

## 14. What remains external or open

This note does **not** yet establish:

- novelty of any universal-property statement;
- canonical terminology relative to category theory, universal algebra, coalgebra, term algebra, graph homomorphism, or model theory;
- a classification of all finite-multiset target algebras;
- conditions on `alpha` that guarantee faithfulness of `fold_alpha`;
- conditions that derive target edit relations canonically from `alpha`;
- a theory of pointed-operation interpretations;
- composition/category structure among PETRA models;
- whether the historical arithmetic reading is structural, faithful, or edit-preserving under this formalization;
- normative SPEC/runtime/API changes.

Those questions belong to later meta-theory, related-work validation, or model-specific follow-up.

## 15. Evidence discipline

The principal AIP-5 results are universal mathematical statements and are proved by definitions, structural induction, and explicit counterexamples. A bounded executable probe may corroborate examples but is neither necessary nor sufficient to establish Theorem 1, Theorem 2, or Theorem 3.

Before canonical promotion, terminology and universal-property claims should be compared explicitly with established mathematics. No originality claim is made here.