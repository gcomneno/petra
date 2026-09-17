# PETRA meta-theory — congruences and quotient structures

Status: **research formalization** for issue #285 under Phase 5 of the complete-theory programme #276.

This note studies when PETRA forms may be identified without destroying the recursive algebra, and separately when identifications are compatible with the intrinsic ADD/REMOVE relations.

The two notions are deliberately not conflated.

## 1. Source structures

Let `P` be the canonical PETRA carrier with

```text
Node : M_f(P) -> P
```

and let

```text
P --ADD--> Q
P --REMOVE--> Q
```

be the intrinsic AIP-4 relations.

From AIP-5, `(P,Node)` is the initial `M_f`-algebra in `Set`.

Let `~` be an equivalence relation on `P`, and let

```text
q : P -> P/~
```

be the quotient map.

## 2. Structural congruence

### Definition 1 — Structural congruence

An equivalence relation `~` on `P` is a **structural congruence** when, for all finite child multisets `M,N` over `P`,

```text
M_f(q)(M) = M_f(q)(N)
```

implies

```text
Node(M) ~ Node(N).
```

Thus parent equivalence depends only on the multiset of child equivalence classes, with multiplicity retained and sibling order absent.

### Remark 1 — Why the quotient-map formulation is used

Informal pairwise matching of children is error-prone in a multiset setting. Equality after `M_f(q)` says exactly that `M` and `N` contain the same multiplicities of `~`-classes.

## 3. Quotient algebra theorem

### Theorem 1 — Structural congruence induces a quotient algebra

If `~` is a structural congruence, there exists a unique map

```text
bar_Node : M_f(P/~) -> P/~
```

such that

```text
q(Node(M)) = bar_Node(M_f(q)(M))
```

for every finite multiset `M` over `P`.

Equivalently, the diagram

```text
M_f(P)  --Node-->      P
  |                    |
M_f(q)                 q
  |                    |
  v                    v
M_f(P/~) --bar_Node--> P/~
```

commutes.

#### Proof

The quotient map `q` is surjective. Therefore `M_f(q)` is also surjective: for every finite multiset of quotient classes, choose one representative of each multiset occurrence.

For `C in M_f(P/~)`, choose `M in M_f(P)` with

```text
M_f(q)(M)=C
```

and define

```text
bar_Node(C)=q(Node(M)).
```

If `N` is another preimage of `C`, then

```text
M_f(q)(M)=M_f(q)(N),
```

so structural congruence gives `Node(M) ~ Node(N)`. Hence

```text
q(Node(M))=q(Node(N)),
```

and the definition is well-defined.

The commuting equation follows by construction.

For uniqueness, any map satisfying the commuting equation must take every `C=M_f(q)(M)` to `q(Node(M))`. Surjectivity of `M_f(q)` determines the map on all inputs. QED.

### Theorem 2 — Converse quotient criterion

Let `~` be an equivalence relation on `P`. Suppose there exists

```text
bar_Node : M_f(P/~) -> P/~
```

such that `q` is an `M_f`-algebra homomorphism:

```text
q(Node(M)) = bar_Node(M_f(q)(M)).
```

Then `~` is a structural congruence.

#### Proof

If

```text
M_f(q)(M)=M_f(q)(N),
```

then applying `bar_Node` gives

```text
q(Node(M))=q(Node(N)).
```

Therefore `Node(M) ~ Node(N)`. QED.

### Corollary 1 — Exact quotient criterion

An equivalence relation on `P` supports an `M_f`-algebra quotient making the canonical projection a homomorphism **iff** it is a structural congruence.

## 4. Kernels of structural interpretations

Let

```text
I : P -> X
```

be a structural interpretation into an `M_f`-algebra `(X,alpha)`.

### Definition 2 — Kernel equivalence

Define

```text
P ~_I Q
iff
I(P)=I(Q).
```

### Theorem 3 — Kernel congruence theorem

The kernel equivalence `~_I` of every structural interpretation is a structural congruence.

#### Proof

Let

```text
q_I : P -> P/~_I
```

be the kernel quotient, and suppose

```text
M_f(q_I)(M)=M_f(q_I)(N).
```

Then the two child multisets have equal multiplicities of kernel classes. Applying `I` copywise therefore gives

```text
M_f(I)(M)=M_f(I)(N).
```

Because `I` is structural,

```text
I(Node(M))
= alpha(M_f(I)(M))
= alpha(M_f(I)(N))
= I(Node(N)).
```

Hence `Node(M) ~_I Node(N)`. QED.

### Corollary 2 — Faithfulness is trivial structural kernel

For a structural interpretation `I`,

```text
I is faithful
iff
~_I is equality on P.
```

#### Proof

Faithfulness is injectivity, which is exactly the statement that equal target values occur only for equal source forms. QED.

## 5. Image factorization

Let `Y = im(I) subseteq X`.

### Lemma 1 — The homomorphic image is closed under the target structure

For every finite multiset `C` over `Y`,

```text
alpha(C) in Y.
```

#### Proof

Choose, for every occurrence of a value in `C`, a source preimage under `I`. These preimages form a finite multiset `M` over `P` with

```text
M_f(I)(M)=C.
```

Then

```text
alpha(C)
= alpha(M_f(I)(M))
= I(Node(M)),
```

which lies in `Y`. QED.

Therefore the restriction

```text
alpha_Y : M_f(Y) -> Y
```

is well-defined.

### Theorem 4 — Kernel quotient / image factorization

There is a unique bijection

```text
j : P/~_I -> Y
```

such that

```text
j([P])=I(P)
```

and

```text
I = inclusion o j o q_I.
```

Moreover `j` is an isomorphism of `M_f`-algebras between the quotient algebra from Theorem 1 and `(Y,alpha_Y)`.

#### Proof

Well-definedness follows from the definition of `~_I`. Surjectivity follows from `Y=im(I)`. Injectivity follows because two quotient classes with the same image value are the same kernel class.

For homomorphicity, for every multiset `M` over `P`,

```text
j(bar_Node(M_f(q_I)(M)))
= j(q_I(Node(M)))
= I(Node(M))
= alpha(M_f(I)(M))
= alpha_Y(M_f(j)(M_f(q_I)(M))).
```

Since `M_f(q_I)` is surjective, this establishes the homomorphism law on every quotient multiset. Bijectivity then gives an algebra isomorphism. QED.

### Theorem 5 — Quotient universal factorization

Let `~` be a structural congruence and let

```text
h : P -> X
```

be a structural interpretation such that

```text
P ~ Q => h(P)=h(Q).
```

Then there exists a unique structural map

```text
bar_h : P/~ -> X
```

with

```text
h = bar_h o q.
```

#### Proof

Define `bar_h([P])=h(P)`. The hypothesis makes this well-defined. Uniqueness follows from surjectivity of `q`. The homomorphism law follows by combining the quotient structure equation with the structural equation for `h`. QED.

This is the universal factorization property of the structural quotient used in this note.

## 6. Arbitrary semantic kernels need not be congruences

### Proposition 1 — Kernel of an arbitrary interpretation may fail structural compatibility

There exists an arbitrary interpretation whose kernel equivalence is not a structural congruence.

#### Proof

Let

```text
A = Node({Z})
```

and define

```text
I : P -> {0,1}
```

by

```text
I(P)=1 iff P=A,
I(P)=0 otherwise.
```

Let `~_I` be its kernel.

Set

```text
B = Node({Z,Z}).
```

Then `Z` and `B` both map to `0`, so

```text
q_I(Z)=q_I(B).
```

Hence

```text
M_f(q_I)({Z}) = M_f(q_I)({B}).
```

But

```text
Node({Z}) = A
```

maps to `1`, while

```text
Node({B})
```

is not `A` and maps to `0`.

Therefore

```text
Node({Z}) not ~_I Node({B}),
```

so the structural congruence law fails. QED.

Thus arbitrary semantic collapse and algebraically admissible quotient collapse are distinct notions.

## 7. Quotients of ADD/REMOVE relations

Carrier congruence alone does not specify how edit relations should descend.

Let `R` be any binary relation on `P`.

### Definition 3 — Existential quotient relation

For any equivalence relation `~`, define a relation on quotient classes by

```text
[P] bar_R_exists [Q]
```

iff there exist representatives `P' in [P]` and `Q' in [Q]` with

```text
P' R Q'.
```

This relation is always well-defined because the definition quantifies over whole equivalence classes rather than choosing distinguished representatives.

### Definition 4 — Representative-invariant relation quotient

Call `~` **representative-invariant for `R`** when

```text
P ~ P' and Q ~ Q'
=>
(P R Q iff P' R Q').
```

Under this stronger condition one may equivalently define

```text
[P] bar_R [Q] iff P R Q
```

using any representatives.

### Definition 5 — Transition-compatible equivalence

Call `~` **transition-compatible for `R`** when

```text
P ~ P' and P R Q
=>
exists Q' such that P' R Q' and Q ~ Q'.
```

Because `~` is symmetric, the same condition also transports transitions from `P'` back to `P`.

This is weaker than representative-invariance: it requires matching target classes, not the same representative-level edge relation for every pair.

For PETRA edit semantics, ADD-compatibility and REMOVE-compatibility must be stated separately unless a theorem connects them.

### Proposition 2 — Representative-invariance implies transition compatibility

If `~` is representative-invariant for `R`, then it is transition-compatible for `R`.

#### Proof

Given `P ~ P'` and `P R Q`, choose `Q'=Q`. Since `Q~Q`, representative-invariance yields `P' R Q`. QED.

The converse need not be assumed.

## 8. Structural congruence does not imply edit compatibility

### Proposition 3 — Structural congruence alone does not preserve REMOVE behavior

There exists a structural congruence that is not transition-compatible for REMOVE.

#### Proof

Take the universal equivalence relation

```text
P ~ Q
```

for all PETRA forms `P,Q`.

It is a structural congruence because every two parent forms are equivalent.

Let

```text
A = Node({Z}).
```

Then

```text
A --REMOVE--> Z.
```

But `A ~ Z`, while `Z` has no REMOVE successor because the root cannot be removed.

Therefore the REMOVE transition from `A` cannot be matched from the equivalent representative `Z`. Transition compatibility fails. QED.

So structural quotient validity does not by itself guarantee edit-semantic quotient validity.

### Remark 2 — Converse independence remains open here

This note does not yet claim that every edit-compatible equivalence can fail structural congruence, nor that edit compatibility implies structural congruence. That direction requires a separate proof or counterexample and remains open in this first quotient formalization.

## 9. Geometry under quotienting

Use the existential quotient of the undirected edit adjacency `~_E` unless stated otherwise.

### Theorem 6 — Connectedness survives every quotient

For any equivalence relation `~` on `P`, the existential quotient edit graph is connected.

#### Proof

Take quotient classes `[P]` and `[Q]`. The source edit graph is connected, so there exists a source path

```text
P=P_0 ~_E P_1 ~_E ... ~_E P_k=Q.
```

Applying the quotient map gives a quotient walk

```text
[P_0], [P_1], ..., [P_k].
```

Whenever consecutive classes differ, the corresponding source edge witnesses a quotient edge. Removing repeated consecutive classes yields a quotient path from `[P]` to `[Q]`. QED.

### Corollary 3 — Quotient distance is non-expansive

Whenever quotient distance is measured in the existential quotient graph,

```text
d_quot([P],[Q]) <= d(P,Q).
```

#### Proof

The image of any source path gives a quotient walk of no greater length. Apply this to a geodesic. QED.

Distance can decrease strictly when distinct source vertices collapse.

### Theorem 7 — Size grading descends exactly when equivalence preserves size

A function

```text
bar_size : P/~ -> N_{>=1}
```

with

```text
bar_size([P])=size(P)
```

is well-defined iff

```text
P ~ Q => size(P)=size(Q).
```

#### Proof

This is exactly the criterion for a function to be constant on equivalence classes. QED.

If size descends, every quotient edge between distinct classes changes `bar_size` by exactly one, so the loop-free quotient graph retains the size bipartition.

### Proposition 4 — Structural congruence alone does not preserve grading or bipartiteness

The universal structural congruence collapses all forms into one quotient class.

Therefore size does not descend. Under the existential quotient relation, the single class has a loop because PETRA has source edit edges whose endpoints lie in that class.

Hence structural congruence alone does not preserve the source grading, and the looped quotient is not bipartite in the usual loop-free graph sense. QED.

### Proposition 5 — Finite equivalence classes preserve local finiteness

If every equivalence class is finite, then the existential quotient of the locally finite PETRA edit graph is locally finite.

#### Proof

Fix a quotient class `C`. Its source representatives form a finite set. Each representative has finitely many source neighbors. The union of these finite neighbor sets is finite, so only finitely many quotient classes can be adjacent to `C`. QED.

### Remark 3 — Arbitrary infinite-class quotients

Local finiteness for arbitrary infinite equivalence classes is not established here. A single quotient class may collect infinitely many representatives whose outgoing neighbor classes are not uniformly bounded.

## 10. What is established

This note proves internally:

- the exact structural congruence criterion;
- existence and uniqueness of the quotient `M_f`-algebra;
- the converse quotient criterion;
- kernel congruence for every structural interpretation;
- faithful iff trivial structural kernel;
- quotient/image factorization for structural interpretations;
- a universal factorization property for structural quotients;
- an explicit arbitrary interpretation whose kernel is not a structural congruence;
- precise distinctions among existential, representative-invariant, and transition-compatible relational quotients;
- structural congruence does not imply REMOVE transition compatibility;
- connectedness survives arbitrary existential quotienting;
- quotient distance is non-expansive;
- size grading descends exactly through size-preserving equivalences;
- structural congruence alone need not preserve grading or bipartiteness;
- finite equivalence classes preserve local finiteness.

## 11. What remains open

This note does **not** yet establish:

- whether edit-transition compatibility implies any structural congruence law in PETRA;
- a complete classification of equivalences compatible with both ADD and REMOVE;
- whether the strongest useful edit quotient notion should be representative-invariance, transition compatibility, or another relation-theoretic condition;
- preservation of exact distance under non-trivial quotients;
- local finiteness for arbitrary infinite-class quotients;
- congruence lattices of `(P,Node)`;
- classification of all homomorphic images of PETRA;
- external novelty or standard terminology;
- any normative SPEC/runtime consequence.

Those belong to later Phase-5 work or Phase-6 validation.

## 12. Evidence discipline

The results in this note are algebraic and relational statements proved directly from the canonical PETRA carrier, AIP-4 relations, and AIP-5 homomorphism theory.

A bounded executable probe is not required for the core quotient theorems. If later used to search for edit-compatible counterexamples or classify small congruences, it will provide computational evidence only and will not replace proof.