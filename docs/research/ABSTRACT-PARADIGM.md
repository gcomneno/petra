# PETRA Abstract Paradigm

## Status

This document defines the current **research paradigm** for abstracting PETRA
away from its arithmetic origin.

It is intentionally **non-normative**. Canonical PETRA semantics remain in
[`../reference/SPEC.md`](../reference/SPEC.md). Nothing in this document changes
runtime behavior, canonical grammar, operators, serialization, or validation.

Its purpose is to determine what PETRA must become before any future semantic
promotion is attempted.

## 1. Foundational statement

PETRA is intended to be a formal system for the definition, composition,
identification, and transformation of recursive canonical forms.

**Form is primary.**

Any meaning assigned to a PETRA form — arithmetic, numeric, combinatorial,
symbolic, linguistic, geometric, or otherwise — belongs to an external
interpretation and must not determine whether the form itself is valid,
identical to another form, canonical, addressable, or transformable.

The central independence principle is:

> **Interpretation may depend on PETRA; PETRA must not depend on any
> interpretation.**

## 2. Historical motivation

PETRA emerged from an arithmetic line of development in which recursive
prime-exponent structures were the original concrete objects. The subsequent
shape-first architecture deliberately removed concrete prime identities,
represented integer values, and arithmetic mutation from canonical semantics.

That transition is not assumed complete.

Terms such as `Product`, `Term`, exponent relation `^`, and other structural
choices may still encode assumptions inherited from the original arithmetic
view. Their presence in the current specification is therefore evidence of
history, not proof that they are intrinsic to form itself.

The research task is to separate:

```text
what the form requires
from
what the first interpretation happened to require
```

## 3. Core admission question

Every concept in the current PETRA model must answer this question:

> **Is this concept necessary to define form and its intrinsic transformations
> independently of every external interpretation?**

If the answer is yes, it is a candidate for the abstract core.

If the answer is no, the concept must be classified elsewhere rather than being
retained in core semantics by historical inertia.

## 4. Four-way classification

Every present or proposed PETRA concept should be classified into exactly one
of the following research categories until evidence justifies promotion.

### 4.1 CORE

A concept is `CORE` when it is necessary to define the abstract shape-space or
its intrinsic transformations independently of external meaning.

Typical questions:

- can a valid form be defined without it?
- can equality be defined without it?
- can structural transformation be defined without it?
- does removing it collapse distinctions that are intrinsic to form itself?

### 4.2 REPRESENTATION

A concept is `REPRESENTATION` when it is necessary or useful for canonical
encoding, addressing, normalization, transport, or display, but is not itself
part of the ontology of form.

A representation concept may change while the represented abstract form stays
the same.

Candidate examples to investigate include positional root ranks, textual
addresses, and canonical serialization syntax.

### 4.3 INTERPRETATION

A concept is `INTERPRETATION` when it assigns external domain meaning to an
otherwise valid PETRA form.

Examples may include:

- mapping structural components to prime numbers;
- reading structural relations as exponentiation;
- reading composition as multiplication;
- projecting a form to an integer;
- assigning symbolic, combinatorial, or domain-specific meaning.

Interpretations are consumers of PETRA structure. They do not define PETRA
validity.

### 4.4 HISTORICAL RESIDUE

A concept is `HISTORICAL RESIDUE` when it survives from an earlier model but is
not required by the abstract core, canonical representation, or a deliberately
maintained interpretation boundary.

Historical residue should be removed or archived once demonstrated to be
unnecessary.

## 5. Arithmetic Erasure Test

The main abstraction gate is the **Arithmetic Erasure Test**.

### 5.1 Test statement

If all references to the following are removed from the core description:

- prime numbers;
- integers;
- products;
- exponents;
- factorization;
- numeric values;
- numeric examples;

then PETRA's abstract core should remain completely definable and coherent.

### 5.2 Required survival properties

After arithmetic erasure, the candidate core must still define:

1. **Ontology** — what forms exist.
2. **Validity** — which structures are valid PETRA forms.
3. **Identity** — when two forms are the same form.
4. **Composition** — how complex forms are built from simpler forms, if
   composition is intrinsic.
5. **Canonicality** — what, if anything, makes one representation canonical.
6. **Addressability** — how a structural location can be selected, if
   addressability is intrinsic or representationally required.
7. **Transformation** — which form-to-form changes are intrinsically legal.
8. **Closure** — whether those transformations remain inside the valid
   shape-space.

Failure of the test does not automatically mean a concept must be deleted. It
means the concept must be examined to determine whether:

- an intrinsic property is still expressed with arithmetic language;
- the concept belongs to representation rather than core;
- the concept belongs to an interpretation;
- the concept is historical residue.

## 6. No privileged interpretation

The arithmetic prime-exponent reading is historically important but must not be
ontologically privileged.

The intended dependency direction is:

```text
PETRA abstract form
    |
    +-- arithmetic interpretation
    +-- combinatorial interpretation
    +-- symbolic interpretation
    +-- other future interpretations
```

and not:

```text
arithmetic structure
    |
    +-- PETRA as a derived encoding
```

A valid PETRA form may therefore be meaningful under zero, one, or several
interpretations.

In particular, the absence of a natural arithmetic projection must not by
itself invalidate a form if that form satisfies intrinsic PETRA rules.

## 7. Semantic independence requirements

A future abstract PETRA core should satisfy the following conditions.

### 7.1 Validity independence

A form is valid because it satisfies PETRA's intrinsic structural rules, not
because it denotes a number or any other external object.

### 7.2 Identity independence

Two forms are equal or distinct because of intrinsic structural criteria.
External interpreted values must not participate in core equality.

### 7.3 Canonicalization independence

Canonicalization must not require prime selection, numeric magnitude,
factorization, or another interpretation-specific ordering principle.

### 7.4 Transformation independence

Core transformations must operate directly on forms. They must not require
first interpreting a form into an external domain, mutating that value, and
reconstructing a form.

### 7.5 Interpretation independence

Adding, removing, or changing an interpretation must not change the set of
valid core forms unless the core itself has been deliberately revised through
the normative promotion process.

## 8. Current grammar under examination

The current normative grammar is:

```text
PETRA     ::= Leaf | Container
Leaf      ::= 1
Container ::= Product(Term+)
Term      ::= Root ^ PETRA
```

This document does **not** replace that grammar.

Instead, every symbol in it becomes a research subject.

### `Leaf`

Question: does the core require a terminal form?

Possible intrinsic concept: `Terminal` or `Atom`.

The spelling `1` may be arithmetic interpretation rather than ontology.

### `Container`

Question: does the core require a recursive aggregate/container construct, or
is the current container shape itself inherited from the arithmetic model?

### `Product`

Question: is there an intrinsic composition operation, or is multiplication
only one interpretation of a more general aggregation relation?

### `Term`

Question: is a term an intrinsic structural entity, a representation artifact,
or merely arithmetic terminology for a more general component or relation?

### `Root`

Question: does a root identity exist intrinsically, or are current `r0`, `r1`,
... ranks only canonical coordinates used to address components in one state?

### `^` relation

Question: is there intrinsically an exponent relation, or only a structural
relation from one component to a recursively nested form?

## 9. Foundational research questions

The abstraction program begins with five mandatory questions.

### AIP-1 — Composition ontology

Why must a `Container` be a `Product(Term+)`?

Determine whether `Product` expresses an intrinsic structural composition or a
residue of arithmetic multiplication.

### AIP-2 — Relation ontology

Why must every `Term` have exactly one exponent relation?

Determine whether the relation currently written `^` is intrinsically part of
PETRA or an arithmetic interpretation of a more general recursive relation.

### AIP-3 — Order semantics

Why does the visible term sequence have its current ordering structure?

Determine whether order is:

- intrinsic to form;
- necessary only for canonical representation;
- replaceable by unordered or multiset structure;
- inherited from the original arithmetic encoding.

### AIP-4 — Generative completeness

Do `SPROUT`, `SHED`, `GRAFT`, and `PRUNE` generate all grammatically valid PETRA
forms from an appropriate minimal starting form?

This must be proved or refuted rather than assumed from implementation
coverage.

### AIP-5 — Non-arithmetic forms

Do valid PETRA forms exist that have no natural arithmetic projection?

A positive answer would strongly separate PETRA ontology from arithmetic
interpretation. A negative answer would show that the present shape-space still
coincides structurally with an arithmetic-generated universe even if labels are
removed.

Neither result is presupposed.

## 10. Candidate abstract vocabulary

The following substitutions are research hypotheses only:

```text
Leaf      -> Terminal / Atom
Container -> Aggregate / Composite
Product   -> Composition
Term      -> Component / Relation
Exponent  -> Recursive relation
Root      -> Coordinate / position
```

Renaming alone is not abstraction.

A concept should only be renamed or removed after its structural role has been
classified. Replacing arithmetic vocabulary with generic vocabulary while
preserving hidden arithmetic assumptions would fail the purpose of this
program.

## 11. Interpretation boundary

A future arithmetic interpretation may look conceptually like:

```text
PETRA form
    |
    v
ArithmeticInterpretation
    |
    +-- component position -> selected prime/base
    +-- recursive relation -> exponentiation
    +-- composition        -> multiplication
    +-- terminal           -> multiplicative identity
    +-- complete form      -> integer/value
```

This is an example of dependency direction, not a proposed normative API.

The same abstract form should in principle be available to other independent
interpretations without changing PETRA core semantics.

## 12. Abstraction success criterion

A successful abstract PETRA specification should be understandable by a reader
who knows nothing about PETRA's arithmetic origin.

That reader should be able to determine:

- what a PETRA form is;
- which forms are valid;
- how forms compose or relate;
- when two forms are identical;
- how a structural location is identified;
- which transformations are legal;
- what invariants those transformations preserve or change.

Only after understanding those rules should the reader need to learn that
prime-exponent arithmetic is one possible interpretation.

## 13. Promotion discipline

This document is a research foundation, not a semantic migration plan.

The required sequence is:

```text
inventory current concept
-> classify CORE / REPRESENTATION / INTERPRETATION / HISTORICAL RESIDUE
-> apply Arithmetic Erasure Test
-> construct counterexamples and alternative models
-> prove or refute necessity
-> define abstract replacement if earned
-> verify operator consequences
-> only then consider SPEC.md promotion
```

No current runtime concept should be deleted, renamed, or generalized merely
because it appears arithmetic in origin.

## 14. Working definition

The current research definition is:

> **PETRA studies recursively composable canonical forms and the intrinsic
> transformations between them. PETRA core assigns no domain meaning to its
> forms. Numeric, arithmetic, symbolic, combinatorial, or other meanings are
> supplied by independent interpretations. No interpretation participates in
> core validity, identity, canonicalization, or transformation semantics unless
> the corresponding property is independently justified as intrinsic to form
> itself.**

This definition is the hypothesis that the Arithmetic Independence Program must
now test.