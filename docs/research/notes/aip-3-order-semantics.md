# AIP-3 — Order Semantics

## Status

Research note for the Arithmetic Independence Program.

This document is **non-normative**. Canonical PETRA semantics remain in
[`../../reference/SPEC.md`](../../reference/SPEC.md). Nothing here changes the
runtime, grammar, operators, serialization, addressing, or validation rules.

The purpose of AIP-3 is to determine whether sibling order is intrinsic to the
abstract form itself or whether the current ordering belongs to representation
and/or to the historical arithmetic interpretation.

## 1. Question

The current PETRA model treats every container as an ordered non-empty sequence
of terms. Root ranks, canonical equality, structural addresses, serialization,
default target selection, and several witnesses are all defined relative to
that order.

The research question is:

> If two sibling components contain the same recursive subforms with the same
> multiplicities but in a different sequence, are they two different abstract
> PETRA forms, or two representations of the same form?

AIP-3 must distinguish four hypotheses:

1. **Intrinsic-order hypothesis** — order is part of PETRA ontology.
2. **Canonical-order hypothesis** — order is not ontological, but one
   deterministic order is required for representation.
3. **Interpretation-order hypothesis** — order is supplied by an external
   interpretation.
4. **Unordered-core hypothesis** — sibling composition is fundamentally
   unordered/multiset-like and the present sequence order is historical or
   representational residue.

## 2. Current normative dependencies

The present specification makes order observable in several independent ways.
These observations describe the current contract; they do not prove that order
is intrinsically necessary.

### 2.1 Grammar and container state

A container owns an **ordered** non-empty sequence of visible terms.

Therefore the current typed model stores sequence order directly.

### 2.2 Root ranks

Visible terms receive ranks `r0`, `r1`, ... from their current sequence
positions. Ranks are recomputed after successful rewrites.

This already shows that root identity is not persistent ontology: rank depends
on order and state.

### 2.3 Canonical equality

Current equality compares corresponding terms in sequence order. Thus two
containers with structurally equal children in different positions compare as
different whenever the corresponding recursive subforms differ.

### 2.4 Addresses

Numeric address segments select a term by its position in the current canonical
child order. An address is therefore a coordinate over the ordered
representation, not an order-independent identity.

### 2.5 Serialization

Canonical textual serialization emits terms in current sequence order and
writes the associated positional ranks. A sibling permutation therefore changes
serialized text under the current contract.

### 2.6 Normalization

Canonical normalization does not derive a new order from intrinsic structure;
it preserves visible order and only reassigns ranks from zero upward.

This distinction is important: current canonicalization **numbers an existing
order**. It does not justify that order.

### 2.7 Default target selection

Current default behavior depends on canonical sequence/traversal order.
Examples include:

- `SPROUT` appends a new leaf term after the last visible term;
- `SHED` chooses the last eligible top-level leaf term;
- `GRAFT` uses canonical preorder and resolves ties by selecting the last
  eligible slot;
- `PRUNE` likewise depends on traversal/eligibility order defined over the
  current representation.

These dependencies make order operationally observable today, but deterministic
selection policy is not by itself evidence that order belongs to ontology.

## 3. Arithmetic erasure

Erase the arithmetic vocabulary and retain only recursive form.

A current container can then be viewed abstractly as something like:

```text
Composite(S0, S1, ..., Sn)
```

where each `Si` is a recursively nested PETRA form associated with one visible
component.

Nothing in that statement alone explains why:

```text
Composite(A, B)
```

must be intrinsically different from:

```text
Composite(B, A)
```

The distinction currently comes from sequence position, not from a demonstrated
shape invariant independent of representation.

Therefore sibling order does **not** pass the Arithmetic Erasure Test merely by
being present in the current grammar.

## 4. Permutation witness

Let `A` and `B` be two distinct recursively valid subforms.

Current ordered forms:

```text
X = C(r0^A, r1^B)
Y = C(r0^B, r1^A)
```

Under current semantics:

```text
X != Y
```

because equality is positional.

Now erase ranks and arithmetic interpretation and record only:

```text
children(X) = {A, B}
children(Y) = {B, A}
```

As multisets these are identical:

```text
{{A, B}} = {{A, B}}
```

No intrinsic distinction remains unless PETRA independently postulates a
left/right, first/second, temporal, geometric, causal, or other ordering
relation.

The current abstract paradigm contains no such independently justified
relation.

This is evidence **against treating order as already established CORE**.

It is not yet a proof that order must be removed; it shows that the burden of
proof lies with any intrinsic-order claim.

## 5. Hidden arithmetic channel

The strongest evidence that current sibling order may be inherited from the
arithmetic interpretation appears in the Resolver numeric projection.

`int_to_shape(n)`:

1. factors the integer;
2. sorts the prime factors;
3. enumerates them in ascending-prime order;
4. assigns ranks `r0`, `r1`, ...;
5. places each prime's recursively encoded exponent at that position.

Thus after concrete prime labels are discarded, **their relative ascending
order survives indirectly through position**.

For example, arithmetic structures conceptually of the form:

```text
p0^A * p1^B
```

and

```text
p0^B * p1^A
```

become the two ordered PETRA shapes:

```text
C(r0^A, r1^B)
C(r0^B, r1^A)
```

Although `r0` and `r1` are explicitly nonnumeric and are not prime labels, the
sequence still preserves the association "exponent belonging to the first
ordered prime" versus "exponent belonging to the second ordered prime".

Therefore current order acts as a **residual carrier of arithmetic base
association**.

This does not make ordering invalid. It does mean that its historical origin is
not neutral and that it cannot be promoted as intrinsic merely because prime
labels themselves have been removed.

## 6. Provisional classification

AIP-3 therefore gives the following provisional result:

| Aspect | Classification |
| --- | --- |
| existence of multiple sibling components | `CORE` candidate |
| sibling multiplicity | `CORE` candidate |
| arbitrary sequence position as ontology | `UNRESOLVED`, with evidence against necessity |
| deterministic canonical ordering | `REPRESENTATION` candidate |
| positional ranks `r0`, `r1`, ... | `REPRESENTATION` candidate |
| prime-associated ordering used by numeric projection | `INTERPRETATION` |
| current preservation of insertion/visible sequence | possible `HISTORICAL RESIDUE`, not yet proved |

The key distinction is:

> multiplicity may be intrinsic even when order is not.

An unordered core therefore should be modeled as a **multiset**, not as a set.
Equal sibling subforms may occur more than once and that multiplicity can be
structurally meaningful.

## 7. Candidate unordered core

A minimal alternative model is:

```text
Form ::= Terminal | Composite(Multiset(Form+))
```

This is intentionally schematic. AIP-2 and AIP-1 still need to determine the
true relation and composition ontology.

For AIP-3 only, the relevant claim is that sibling membership and multiplicity
can be separated from sequence position.

Two composites would then be equal when there exists a multiplicity-preserving
bijection between their recursively equal children.

Equivalently, equality is recursive multiset equality rather than recursive
sequence equality.

## 8. Deterministic representation without ontological order

An unordered core does **not** imply nondeterministic serialization.

Representation can impose a deterministic order after the abstract form is
known.

A representation-level canonicalization could conceptually:

1. compute an interpretation-independent structural key for each child;
2. sort children by that structural key;
3. preserve duplicate multiplicities;
4. assign ephemeral positional coordinates `r0`, `r1`, ...;
5. serialize and address the resulting canonical presentation.

The structural key must itself depend only on abstract PETRA structure. It must
not depend on:

- prime values;
- represented integers;
- allocation identity;
- insertion history;
- external interpretation;
- pre-existing positional ranks.

One possible research construction is a recursive canonical code:

```text
code(Terminal) = T
code(Composite(children)) = C(sort(code(child) for child in children))
```

This is a research sketch, not a proposed syntax.

Its purpose is to demonstrate that deterministic representation does not require
ordered ontology.

## 9. Duplicate siblings and occurrence identity

An unordered multiset raises an important concern: if two siblings are equal,
how can one occurrence be targeted?

The answer may remain purely representational.

Suppose the abstract multiset is:

```text
{{A, A, B}}
```

Canonical representation may expose three state-scoped occurrences:

```text
r0:A, r1:A, r2:B
```

The two `A` occurrences need not possess persistent ontological identity. They
are interchangeable occurrences of the same structural member with
multiplicity two.

If a structural operation transforms exactly one `A` into `A'`, either choice
produces the same abstract multiset:

```text
{{A, A', B}}
```

provided the operation depends only on the selected occurrence's structure and
not on hidden identity or history.

This symmetry is strong evidence that positional occurrence identity can remain
at the representation layer.

A counterexample would be any canonical operator whose result depends on *which
indistinguishable equal occurrence* was chosen after all representation data is
erased. No such counterexample has yet been established.

## 10. Operator consequences

### 10.1 SPROUT

Abstractly, `SPROUT` adds one terminal member to a selected composite.

Current "append last" behavior appears representational. In an unordered core:

```text
M -> M ⊎ {Terminal}
```

where `⊎` is multiset addition.

No intrinsic insertion position is required.

### 10.2 SHED

Abstractly, `SHED` removes one selected terminal occurrence from a composite.

For equal terminal occurrences, removing any one yields the same multiset.

Current "last eligible" default therefore looks like deterministic target
selection over representation rather than core semantics.

### 10.3 GRAFT

`GRAFT` transforms one selected latent recursive relation into a materialized
nested form.

Its structural effect does not inherently require sibling order. Address and
default selection currently do.

### 10.4 PRUNE

`PRUNE` performs the inverse structural collapse under its current
preconditions. Again, the local rewrite appears order-independent while target
selection is order-dependent.

### 10.5 Preliminary operator result

The four operator *effects* survive the removal of sibling order more readily
than their current default-selection and address policies.

This suggests a useful decomposition:

```text
core rewrite relation
+
representation-level target coordinate
+
representation-level deterministic default policy
```

AIP-4 must later determine whether the resulting rewrite system is generatively
complete.

## 11. Equality consequences

Demoting order from ontology changes equality substantially.

Current:

```text
C(A, B) != C(B, A)
```

Candidate abstract equality:

```text
Composite({{A, B}}) == Composite({{B, A}})
```

This would quotient the current ordered shape-space by sibling permutations at
every recursive level.

Formally, if `~perm` is the equivalence relation generated by arbitrary sibling
permutations recursively, the candidate abstract space is:

```text
P_unordered = P_current / ~perm
```

This quotient perspective is important because it lets PETRA retain the current
ordered implementation as a representative system while researching whether
the quotient, rather than the representatives, is the true abstract ontology.

## 12. Resolver consequences

The current Resolver operates over canonical typed shapes whose equality and
hashing include ordered term tuples. Its graph therefore distinguishes sibling
permutations when those permutations yield distinct valid canonical shapes.

If AIP-3 ultimately demotes order:

- Resolver states should eventually be quotient states or canonical
  representatives of permutation classes;
- distance zero should hold between permutation-equivalent forms;
- visited-state hashing must use order-independent canonical form;
- atlases may shrink because permutation variants collapse;
- shortest-path results may shorten where current paths spend edits navigating
  distinctions that the abstract core no longer recognizes;
- verifier logic must compare abstract classes rather than raw ordered tuples;
- arithmetic projection must remain outside this quotient unless it explicitly
  supplies the ordering/decorations required to recover prime association.

No Resolver change is proposed in this issue.

## 13. Consequence for arithmetic interpretation

If the core becomes unordered, the existing arithmetic mapping cannot simply
assume that abstract sibling position identifies ascending primes.

The arithmetic interpretation would need to provide its own additional
structure, for example:

```text
abstract multiset form
+
arithmetic decoration / assignment
-> prime-exponent interpretation
```

or define a deterministic interpretation-specific assignment rule.

This is desirable from the abstract-paradigm perspective: information required
only to interpret the form numerically should belong to the arithmetic
interpretation, not to PETRA core ontology.

It also means that a single abstract PETRA form could correspond to multiple
arithmetically decorated forms if the interpretation chooses to expose those
assignments rather than canonicalize one.

That is not a defect in PETRA core. It is evidence that arithmetic meaning
contains information not intrinsic to bare form.

## 14. What would prove intrinsic order?

Order should be promoted to `CORE` only if at least one property can be shown
that:

1. is definable without external interpretation;
2. distinguishes sibling permutations;
3. is necessary for form identity or intrinsic transformation;
4. cannot be reconstructed as canonical representation metadata.

Examples of potentially sufficient evidence would be an independently justified
orientation, adjacency, left/right relation, causal ordering, or noncommutative
composition law intrinsic to PETRA.

No such property is present in the current abstract paradigm or established by
the current specification.

## 15. What would refute the unordered-core hypothesis?

The unordered-core hypothesis would be refuted by a representation-independent
counterexample where two permutation-equivalent current shapes:

- admit different sets of intrinsic local rewrites;
- have different intrinsic invariants;
- produce different abstract results under the same structurally specified
  operation;
- or cannot be canonically represented without importing external meaning.

Current positional addresses, root ranks, serialized text, and default-selection
policies do not qualify because they are themselves representation-dependent.

## 16. AIP-3 provisional conclusion

The current evidence supports the following research conclusion:

> **Sibling order is operationally normative in PETRA v2.0.0 but is not yet
> justified as intrinsic to abstract form.**

More strongly:

> **Current ordering carries residual information from the arithmetic
> interpretation because ascending prime association is preserved through
> positional rank even after prime labels are erased.**

Therefore the leading AIP-3 hypothesis is:

```text
abstract sibling structure = multiset of recursive components
canonical sibling order    = representation
prime/base assignment       = interpretation
```

This is still a research result, not a normative migration.

Before any `SPEC.md` change, the hypothesis should be tested by constructing an
order-independent prototype model and checking:

1. recursive equality modulo sibling permutation;
2. deterministic structural canonicalization;
3. duplicate-occurrence targeting;
4. all four operator effects;
5. Resolver quotient behavior on bounded atlases;
6. explicit separation of arithmetic decoration from abstract shape.

## 17. Decision

AIP-3 remains **OPEN**, but the burden of proof has shifted.

The question is no longer "can PETRA work without current order?" — a coherent
unordered candidate model exists.

The next question is:

> **Can any representation-independent invariant or rewrite behavior prove that
> sibling permutations must denote different abstract forms?**

Until such evidence appears, sibling order should be treated as a strong
`REPRESENTATION` candidate rather than assumed `CORE`.