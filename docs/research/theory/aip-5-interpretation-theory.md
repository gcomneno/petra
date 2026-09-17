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

AIP-4 supplies two intrinsic unpointed edit relations on `P`:

```text
P --ADD--> Q
P --REMOVE--> Q
```

induced by pointed elementary node addition and zero-child leaf removal, respectively.

This note treats carrier structure, information preservation, and edit preservation as logically distinct dimensions.

### Lemma 1 — The PETRA carrier is a set

The carrier `P` is a set, not a proper class.

#### Proof

For every natural number `n >= 1`, every concrete PETRA realization with `n` occurrences is isomorphic to one whose vertex set is

```text
{0, ..., n-1}.
```

Such a realization is determined by finite data: a distinguished root and a binary incidence relation on that finite set satisfying the PETRA rooted-tree conditions.

For fixed `n` there are only finitely many such finite structures. The union over all natural numbers `n` is therefore countable. Passing to root-preserving isomorphism classes is a quotient of that set, hence again a set.

Therefore `P` may be used as an object of `Set`. QED.

### Remark 1 — Why sethood matters here

Earlier carrier notes allowed the cautious phrase “set/class”. AIP-5 needs a genuine set-level statement because the finite-multiset construction is used as an endofunctor on `Set` and the initial-algebra claim quantifies over ordinary set-based target algebras.

No cardinality claim beyond sethood is required for the theory below.

## 2. Finite-multiset functor

### Definition 1 — Finite-multiset lifting

For a set `X`, let `M_f(X)` be the set of finite multisets over `X`.

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

### Lemma 2 — Functoriality

The finite-multiset lifting satisfies

```text
M_f(id_X) = id_{M_f(X)}
```

and

```text
M_f(g o f) = M_f(g) o M_f(f).
```

#### Proof

Both equalities hold copywise on every finite multiset and preserve multiplicity. QED.

Hence `M_f` is an endofunctor on `Set` for the purposes of this note.

## 3. Arbitrary interpretations

### Definition 2 — Arbitrary interpretation

Let `X` be any set. An **arbitrary interpretation** of PETRA in `X` is simply a function

```text
I : P -> X.
```

The pair `(X,I)` is an arbitrary PETRA interpretation.

This is the weakest possible notion. It asserts only that equal PETRA forms receive one well-defined target value because `I` is defined on the quotient carrier `P` itself.

### Proposition 1 — Arbitrary interpretation carries no preservation law

Every function `I : P -> X` is an arbitrary interpretation. From this fact alone one may not infer preservation of recursive construction, injectivity, ADD/REMOVE, size, depth, multiplicity, or any other PETRA property.

#### Proof

Immediate from Definition 2. QED.

## 4. Structural interpretations

### Definition 3 — Finite-multiset target algebra

A **finite-multiset target algebra** is a pair

```text
(X, alpha)
```

with

```text
alpha : M_f(X) -> X.
```

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

### Theorem 1 — Structural recursion theorem

For every finite-multiset target algebra `(X,alpha)`, there exists a unique structural interpretation

```text
fold_alpha : P -> X
```

such that

```text
fold_alpha(Node(M))
    = alpha(M_f(fold_alpha)(M))
```

for every finite multiset `M` of PETRA forms.

#### Proof — existence

Proceed by induction on PETRA size.

For the unique size-one form `Z = Node(empty)`, define

```text
fold_alpha(Z) = alpha(empty).
```

Assume the map is defined on all PETRA forms of size less than `n`. Let `p = Node(M)` have size `n`. Every child form in `M` has strictly smaller size, so each child image is already defined. Set

```text
fold_alpha(p) = alpha(M_f(fold_alpha)(M)).
```

PETRA equality identifies exactly the root-preserving isomorphism class of the finite rooted non-plane realization. The recursive multiset presentation is invariant under that equality, and `M_f` preserves multiplicity without introducing sibling order. Therefore the value depends only on the PETRA form and not on a representative or ordering.

Since every PETRA form has finite size, the definition reaches every element of `P`. QED.

#### Proof — uniqueness

Let `f,g : P -> X` satisfy the structural equation. Proceed by induction on size.

For `Z`,

```text
f(Z) = alpha(empty) = g(Z).
```

Assume `f(q)=g(q)` for every form of size less than `n`, and let `p=Node(M)` have size `n`. Every child in `M` has smaller size, hence

```text
M_f(f)(M) = M_f(g)(M).
```

Therefore

```text
f(p)
= alpha(M_f(f)(M))
= alpha(M_f(g)(M))
= g(p).
```

Thus `f=g`. QED.

### Corollary 1 — Initial-algebra property

The algebra

```text
(P, Node)
```

with

```text
Node : M_f(P) -> P
```

is initial among `M_f`-algebras in `Set`: for every algebra `(X,alpha)` there exists exactly one algebra homomorphism

```text
(P,Node) -> (X,alpha).
```

#### Proof

An `M_f`-algebra homomorphism is exactly a map satisfying the structural equation of Definition 4. Existence and uniqueness are Theorem 1. QED.

### Remark 2 — Terminology discipline

The universal property is proved internally. The words “initial algebra”, “structural recursion”, and related categorical terminology are standard-mathematics claims about the formulation, not PETRA novelty claims. Their relation to established literature must be documented separately before canonical publication claims.

## 5. Faithfulness

### Definition 5 — Faithful interpretation

An interpretation

```text
I : P -> X
```

is **faithful on forms** when it is injective:

```text
I(P) = I(Q)  =>  P = Q.
```

Faithfulness means that target values retain enough information to recover source-form identity.

It does not imply that recursive construction or edit relations are preserved.

### Proposition 2 — Structural does not imply faithful

There exists a structural interpretation that collapses all PETRA forms.

#### Proof

Let

```text
X = {*}
```

and define

```text
alpha(M) = *
```

for every finite multiset over `X`.

Theorem 1 gives a unique structural interpretation `fold_alpha : P -> X`, necessarily constant. Since PETRA has distinct forms such as

```text
Z != Node({Z}),
```

the interpretation is not injective. QED.

### Proposition 3 — Faithful does not imply structural

There exists a faithful arbitrary interpretation that is not structural for a chosen target algebra.

#### Proof

Let

```text
X = P
```

and let `I = id_P`, which is injective. Define a target algebra

```text
alpha : M_f(P) -> P
```

by the constant rule

```text
alpha(M) = Z
```

for every `M`.

For `p = Node({Z})`,

```text
I(p) = p != Z = alpha(M_f(I)({Z})).
```

Hence the structural equation fails although `I` is faithful. QED.

Therefore faithfulness and structural preservation are independent properties.

## 6. Edit interpretations

### Definition 6 — Target edit structure

A **target edit structure** is a triple

```text
(X, A_X, R_X)
```

where `A_X` and `R_X` are binary relations on `X` intended to receive PETRA ADD and REMOVE steps.

No assumption is made that these relations are functions, inverses, deterministic, or generated by concrete target operations.

### Definition 7 — Edit-preserving interpretation

An interpretation

```text
I : P -> X
```

is **edit-preserving** into `(X,A_X,R_X)` when

```text
P --ADD--> Q     =>     I(P) A_X I(Q),
P --REMOVE--> Q  =>     I(P) R_X I(Q).
```

### Definition 8 — Edit-reflecting interpretation

An interpretation

```text
I : P -> X
```

is **edit-reflecting** into `(X,A_X,R_X)` when

```text
I(P) A_X I(Q)    =>    P --ADD--> Q,
I(P) R_X I(Q)    =>    P --REMOVE--> Q
```

for all PETRA forms `P,Q`.

Reflection is logically distinct from preservation; neither is built into the definition of the other.

### Definition 9 — Strong edit interpretation

A **strong edit interpretation** is both edit-preserving and edit-reflecting.

### Remark 3 — Pointed versus unpointed semantics

AIP-4 pointed operations live on targeted realizations such as `(R,u)`, while carrier-level AIP-4 operations are the induced relations on `P`.

An interpretation `I : P -> X` naturally interprets the unpointed relations. Interpreting pointed operations requires additional target-pointing structure and a map on pointed realizations; that is a separate extension.

## 7. Independence results for edit semantics

### Proposition 4 — Faithful does not imply edit-preserving

There exists a faithful interpretation into a target edit structure that preserves no non-trivial PETRA edits.

#### Proof

Take

```text
X = P,
I = id_P,
A_X = empty relation,
R_X = empty relation.
```

`I` is injective, but PETRA has non-trivial ADD/REMOVE edges and the target has none. Therefore `I` is faithful and not edit-preserving. QED.

### Proposition 5 — Edit-preserving does not imply edit-reflecting

There exists an edit-preserving interpretation that reflects neither relation.

#### Proof

Let

```text
X = {*},
I(P) = *,
A_X = {(*,*)},
R_X = {(*,*)}.
```

Every PETRA edit maps to the unique target loop, so preservation holds.

Reflection fails because `* A_X *` holds while

```text
P --ADD--> P
```

is impossible for every `P` by the AIP-4 size `+1` theorem. Likewise `* R_X *` holds while `P --REMOVE--> P` is impossible. QED.

### Proposition 6 — Structural does not imply edit-preserving

There exists a structural interpretation that is not edit-preserving.

#### Proof

Use the singleton structural interpretation from Proposition 2 and choose empty target edit relations. PETRA has ADD/REMOVE edges, so preservation fails. QED.

### Proposition 7 — Edit-preserving does not imply structural

There exists an edit-preserving interpretation that is not structural for a chosen target algebra.

#### Proof

Take

```text
X = P,
I = id_P,
A_X = ADD,
R_X = REMOVE.
```

Then edit preservation holds exactly.

Now equip the same set `X=P` with the constant target algebra

```text
alpha(M) = Z.
```

As in Proposition 3, the identity map fails the structural equation at `Node({Z})`. Therefore edit preservation does not imply structural preservation. QED.

### Remark 4 — Independent qualifiers

The following are independent predicates on an interpretation once the relevant target structures have been supplied:

```text
STRUCTURAL
FAITHFUL
EDIT-PRESERVING
EDIT-REFLECTING
```

They are not levels of one hierarchy and must not be drawn as a single inheritance tree.

## 8. PETRA edit-graph embeddings

### Definition 10 — PETRA labeled edit graph

Define

```text
G_P = (P, ADD, REMOVE)
```

with vertices `P` and the two AIP-4 edge labels.

### Theorem 2 — Faithful strong edit interpretations are graph embeddings

Let

```text
I : P -> X
```

be faithful, edit-preserving, and edit-reflecting into `(X,A_X,R_X)`.

Then `I` identifies `G_P` with the labeled subgraph of the target relation structure induced on `I(P)`:

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

Preservation supplies both forward implications; reflection supplies both reverse implications. Injectivity prevents distinct PETRA forms from being identified. Hence the source labeled graph is isomorphic to its image. QED.

### Corollary 2 — Source reconstruction inside the image

Within the image of a faithful strong edit interpretation, PETRA form identity and one-step AIP-4 adjacency are recoverable.

This does not recover realization-local occurrence targets, because those are not part of the unpointed carrier.

## 9. Combined model notions

### Definition 11 — Structural model

A **PETRA structural model** is a triple

```text
(X, alpha, I)
```

where `(X,alpha)` is an `M_f`-algebra and `I` is the unique structural interpretation supplied by Theorem 1.

### Definition 12 — Edit model

A **PETRA edit model** is a quadruple

```text
(X, A_X, R_X, I)
```

where `I : P -> X` is edit-preserving.

### Definition 13 — Full PETRA model

A **full PETRA model** is

```text
(X, alpha, A_X, R_X, I)
```

such that:

1. `I` is structural with respect to `alpha`;
2. `I` is edit-preserving with respect to `A_X,R_X`.

Additional qualifiers are stated independently:

```text
faithful    iff I is injective
strong-edit iff I is preserving + reflecting
embedded    iff I is structural + faithful + preserving + reflecting
```

### Remark 5 — “Full” is a PETRA-local convenience term

“Full PETRA model” is proposed here as project terminology for a target carrying both recursive carrier semantics and AIP-4 edit semantics. It is not asserted to be standard terminology in category theory, universal algebra, graph theory, or model theory.

## 10. Interpretation independence

### Theorem 3 — Interpretation cannot feed back into PETRA

Let `I : P -> X` be any arbitrary interpretation, with or without structural, faithful, preserving, reflecting, or full-model qualifiers.

For PETRA forms `P,Q`, whether

```text
P = Q,
P --ADD--> Q,
P --REMOVE--> Q
```

holds is determined entirely in the PETRA source theory and is independent of `I(P)` and `I(Q)`.

#### Proof

Carrier equality is defined by root-preserving structural isomorphism in the source. ADD/REMOVE are defined by source elementary edit witnesses modulo that equality. None of these source definitions quantifies over a target set, target algebra, target relation, or interpretation map. QED.

### Corollary 3 — External values are downstream

Numbers, names, weights, labels, logical meanings, physical meanings, application states, or any other target values may be assigned by interpretations, but they cannot become PETRA structural identity or edit legality merely because an interpretation uses them.

### Corollary 4 — Non-faithful models are legitimate

A model may intentionally identify distinct PETRA forms. The collapse occurs in the model, not in PETRA itself.

## 11. Classification summary

The basic object is always a map

```text
I : P -> X.
```

Possible independent qualifiers are:

```text
STRUCTURAL       preserves Node / finite-multiset recursion
FAITHFUL         injective on PETRA forms
EDIT-PRESERVING  source edit => target edit
EDIT-REFLECTING  target edit between images => source edit
```

Combined notions used in this note are:

```text
STRONG-EDIT
= EDIT-PRESERVING + EDIT-REFLECTING

FULL PETRA MODEL
= STRUCTURAL + EDIT-PRESERVING

EMBEDDED FULL MODEL
= STRUCTURAL + FAITHFUL + EDIT-PRESERVING + EDIT-REFLECTING
```

There is no single total hierarchy among the four qualifiers.

## 12. Historical arithmetic reading

The historical arithmetic motivation is not used in any definition or proof above.

If an arithmetic interpretation is retained, it must be presented as one concrete target and separately checked against the predicates in this note:

```text
arbitrary?
structural?
faithful?
edit-preserving?
edit-reflecting?
full?
embedded?
```

No status is granted merely because arithmetic historically motivated PETRA.

## 13. Results established here

This note establishes internally:

- `P` is a set and can be used in `Set`;
- `M_f` acts functorially on sets and maps;
- every finite-multiset algebra admits a unique PETRA structural interpretation;
- `(P,Node)` therefore has the corresponding initial-algebra universal property;
- structural preservation and faithfulness are independent;
- faithfulness and edit preservation are independent;
- structural preservation and edit preservation are independent;
- edit preservation does not imply edit reflection;
- faithful strong edit interpretations embed the labeled PETRA edit graph into their target relation structure;
- interpretation values cannot feed back into PETRA equality or intrinsic edit legality.

## 14. What remains external or open

This note does **not** establish:

- novelty of any universal-property statement;
- canonical terminology relative to category theory, universal algebra, term algebra, graph homomorphism, or model theory;
- a classification of all finite-multiset target algebras;
- conditions on `alpha` that guarantee faithfulness of `fold_alpha`;
- conditions that derive target edit relations canonically from `alpha`;
- a theory of pointed-operation interpretations;
- composition/category structure among PETRA models;
- whether the historical arithmetic reading is structural, faithful, or edit-preserving;
- normative SPEC/runtime/API changes.

Those questions belong to later meta-theory, related-work validation, or model-specific follow-up.

## 15. Evidence discipline

The principal AIP-5 results are universal mathematical statements and are supported here by definitions, induction, and explicit counterexamples.

A bounded executable probe may corroborate examples but cannot prove Theorem 1, Theorem 2, or Theorem 3.

Before canonical promotion, terminology and universal-property claims must be compared explicitly with established mathematics. No originality claim is made here.
