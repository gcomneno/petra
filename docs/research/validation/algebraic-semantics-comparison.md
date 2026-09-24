# PETRA Phase 6 — algebraic semantics comparison

Status: **Phase 6 external-validation note** for issue #297 under programme #276.

This note validates PETRA's initial-algebra, fold, congruence, quotient, kernel, and first-isomorphism claims against external references. It does not promote research results into the normative SPEC.

## 1. Finite multiset = bag functor

Let `B : Set -> Set` be the bag functor. For a set `X`, `B(X)` is the set of finite multisets over `X`.

For a function `f : X -> Y`, multiplicities are pushed forward by summing along fibres:

```text
(B f)(m)(y) = sum_{x : f(x)=y} m(x).
```

This is the standard functorial action matching PETRA's use of finite child multisets.

## 2. Initial algebra

Adámek, Milius and Moss explicitly identify the initial algebra of the bag functor with all finite unordered trees.

Its algebra structure takes a finite bag of trees and attaches those trees, with their multiplicities, below a fresh common root.

That is structurally the same constructor as:

```text
Node : M_f(P) -> P.
```

The empty bag produces the one-node tree, matching PETRA's `Z = Node(empty)`.

### Phase-6 classification

```text
(P, Node) initial algebra for M_f on Set     KNOWN
```

PETRA's proof is therefore a rederivation / project-local formulation of established mathematics, not a novelty candidate.

## 3. Structural interpretations are folds

By the universal property of an initial algebra, for every `B`-algebra

```text
alpha : B(X) -> X
```

there exists a unique homomorphism

```text
fold_alpha : P -> X
```

such that

```text
fold_alpha(Node(M))
=
alpha(B(fold_alpha)(M)).
```

This is exactly the structure used by PETRA's structural interpretations.

### Phase-6 classification

```text
structural interpretation as recursive fold     SPECIALIZED
```

The generic theorem is standard; PETRA supplies its own terminology and interpretation architecture.

## 4. Bridge to ordinary universal algebra

The bag-algebra view is an endofunctor-algebra presentation. Standard universal-algebra congruence theorems are usually stated for a finitary operation signature.

A concrete bridge is:

```text
node_0
node_1(x1)
node_2(x1,x2)
...
node_n(x1,...,xn)
...
```

with equations imposing permutation invariance:

```text
node_n(x1,...,xn)
=
node_n(x_sigma(1),...,x_sigma(n))
```

for every permutation `sigma in S_n`.

This presents the same finite-bag constructor behaviour while making compatibility with operations an ordinary universal-algebra congruence condition.

The bridge matters: PETRA must not cite universal-algebra theorems as though the bag constructor had one fixed arity.

## 5. Congruence and quotient

Under the symmetric finitary presentation, an equivalence relation `~` is a structural congruence exactly when replacing equivalent arguments by equivalent arguments preserves every `node_n`.

The standard quotient construction then defines:

```text
node_n([x1],...,[xn])
=
[node_n(x1,...,xn)].
```

This is well-defined precisely because of congruence compatibility.

Therefore PETRA's quotient-algebra theorem is a specialization of standard universal algebra.

### Phase-6 classification

```text
quotient algebra from structural congruence       SPECIALIZED
```

## 6. Kernels

For a structural homomorphism `h : A -> B`, define:

```text
a ~ b  iff  h(a)=h(b).
```

Standard universal algebra proves that this kernel equivalence is a congruence.

Therefore:

```text
kernel of structural interpretation is congruence     SPECIALIZED
```

The adjective “structural” remains important: an arbitrary set map need not be a homomorphism and its kernel need not respect the constructor.

## 7. First isomorphism / image factorization

The standard Homomorphism Theorem gives, for a surjective homomorphism:

```text
A / ker(h) ~= B.
```

Applying it to the codomain restricted to the image yields:

```text
A / ker(h) ~= im(h).
```

Hence PETRA's first-isomorphism-style factorization is standard algebra specialized to its structural homomorphisms.

### Phase-6 classification

```text
P / ker(I) ~= im(I)      SPECIALIZED
```

## 8. What the generic algebra does not give PETRA

The external algebraic theorems do not imply:

- ADD/REMOVE transition compatibility;
- preservation or reflection of the PETRA edit relation;
- geodesic or metric properties;
- that an arbitrary semantic map has a structural kernel;
- that structural congruence implies edit compatibility.

Those remain separate PETRA theorems/counterexamples.

## 9. Phase-6 result

This slice resolves a substantial cluster of previous `TO-VERIFY` rows:

```text
bag-functor initial algebra                KNOWN
structural interpretation as fold         SPECIALIZED
kernel congruence                          SPECIALIZED
quotient by congruence                     SPECIALIZED
A/ker(h) ~= im(h)                          SPECIALIZED
```

The PETRA-specific boundary between structural congruence and edit compatibility remains internal and is not weakened by this classification.

No Phase-7 promotion follows automatically from these results.
