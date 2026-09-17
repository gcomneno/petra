# AIP-1 multiplicity ontology

## Status

Research note under issues #263 and #264.

This note is non-normative. It does not change SPEC, runtime semantics, APIs, CLI behavior, serialization, addressing, operators, or Resolver behavior.

AIP-1 asks which composition properties are intrinsic to the fully abstract PETRA carrier. This note isolates one question:

> If a composite contains two recursively equal child forms instead of one, is that multiplicity itself part of abstract PETRA structure?

## Competing models

Multiset candidate:

```text
Form ::= Terminal | Composite(Multiset(Form+))
```

Set candidate:

```text
Form ::= Terminal | Composite(Set(Form+))
```

They differ exactly when equal child shapes repeat. For any form `A`:

```text
M1 = Composite({A})
M2 = Composite({A, A})
```

Under multiset semantics `M1 != M2`; under set semantics they collapse.

## Current executable contract

The current runtime stores `Container.terms` as a non-empty tuple. Structural equality compares term counts before descending recursively, so different widths are unequal even before arithmetic interpretation is considered.

Thus current v2.0.0 behavior distinguishes one occurrence of a child from two equal occurrences. This establishes operational normativity, not yet abstract intrinsicness.

## Arithmetic Erasure Test

Erase integers, primes, product/exponent language, factorization, roots, order, addresses and numeric examples.

The distinction still remains expressible purely structurally:

```text
one occurrence of A
versus
two occurrences of A
```

Multiplicity therefore survives arithmetic erasure as a CORE candidate.

## Set-collapse test

If duplicate equal children are collapsed,

```text
Composite({A, A}) -> Composite({A})
```

then the erased count cannot be reconstructed from the remaining recursive structure.

This differs from properties already demoted or derived:

- sibling order can be quotiented while retaining the multiset of children;
- level can be reconstructed from recursive path length;
- duplicate count cannot be recovered after set collapse.

Set semantics is therefore a stronger information loss than the AIP-3 permutation quotient.

## Multiplicity versus occurrence identity

Preserving multiplicity does not require persistent identity for equal occurrences.

The abstract carrier may retain only:

```text
A occurs twice
```

without distinguishing a first and second `A`.

Provisional separation:

```text
multiplicity count        = CORE candidate
persistent occurrence id  = not established CORE
sibling order / position  = REPRESENTATION
```

This is exactly the structural role naturally captured by a multiset.

## Operator-survival test

### SPROUT

Abstractly, SPROUT adds one terminal child occurrence:

```text
Composite(M) -> Composite(M + {Terminal})
```

If `Terminal` is already present, multiset semantics changes the state by increasing its count.

Under set semantics, adding the same shape again is invisible. A successful width-increasing rewrite may therefore collapse to no abstract state change.

### SHED

From two terminal occurrences:

```text
Composite({Terminal, Terminal})
    -> Composite({Terminal})
```

multiset semantics preserves a visible before/after distinction.

Under set semantics, both sides collapse to the same state. SHED can therefore become observationally invisible.

### GRAFT / PRUNE

Their local depth-changing effect

```text
Terminal <-> Composite({Terminal})
```

does not itself require sibling multiplicity. But if several equal eligible occurrences coexist, their count still contributes to the surrounding composite state.

The strongest multiplicity pressure therefore comes from SPROUT/SHED.

## Equality consequence

If multiplicity is CORE, abstract equality must compare recursively equal child forms together with their counts, while still ignoring sibling permutation.

```text
Composite(M) == Composite(N)
iff
M and N contain the same recursive child shapes
with the same multiplicities
```

## Representation consequence

Ranks, current numeric addresses and serialization punctuation are not needed merely to preserve multiplicity. A canonical representation may sort equal-shape classes or otherwise choose deterministic coordinates while keeping duplicate counts intact.

Serialization must remain injective with respect to multiplicity: `Composite({A})` and `Composite({A,A})` must not encode as the same abstract state if this classification is retained.

## Resolver consequence

State identity and occurrence targeting must be separated.

A state with two equal child occurrences may have multiple concrete rewrite targets that lead to the same quotient successor once order and persistent occurrence identity are ignored. That does not require persistent occurrence identity in CORE, but it does require the state to remember that two occurrences exist.

## Counterexample against set semantics

Take:

```text
S = Composite({Terminal})
```

After one SPROUT at that composite, the structural intent is:

```text
S' = Composite({Terminal, Terminal})
```

Multiset semantics gives `S' != S`.
Set semantics gives `S' == S`.

Likewise, SHED from two equal terminals to one becomes invisible under set semantics.

If SPROUT/SHED are retained as intrinsic width-changing structural transformations, this is a direct argument that set semantics is too weak.

## Provisional classification

```text
child collection                = CORE candidate
child multiplicity              = CORE candidate, strongly supported
persistent occurrence identity  = not established CORE
sibling order                   = not CORE
positional rank                 = REPRESENTATION
```

The key non-arithmetic argument is:

> Erasing duplicate counts makes some accepted width-changing structural rewrites observationally disappear.

## Limits

This note does not settle all of AIP-1. Still open:

- non-emptiness versus an empty composite;
- whether `Terminal` could be identified with an empty composite;
- grouping/associativity and flattening;
- whether `Composite({A})` is intrinsically distinct from `A`;
- whether composition needs an algebraic operator beyond recursive constructor syntax.

## Recommended next test

A focused research-only executable probe should compare multiset and set erasure on a bounded corpus and verify:

1. sibling permutations still collapse;
2. multiset erasure preserves duplicate counts;
3. set erasure creates explicit width collisions;
4. SPROUT becomes invisible under set erasure when adding an already-present child shape;
5. SHED from multiplicity two to one becomes invisible under set erasure;
6. no production semantics are changed.

A passing probe would strengthen this AIP-1 multiplicity classification without constituting an absolute proof of final ontology.
