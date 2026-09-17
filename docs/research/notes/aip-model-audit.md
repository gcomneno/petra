# AIP model audit — first pass

## Status

This note is a **non-normative research audit** of the current PETRA model
against [`../ABSTRACT-PARADIGM.md`](../ABSTRACT-PARADIGM.md).

The normative source remains [`../../reference/SPEC.md`](../../reference/SPEC.md).
Nothing here changes current PETRA grammar, validation, serialization, addressing,
or operator semantics.

The purpose is narrower: identify which current concepts appear intrinsic to
form, which appear representational, which belong to an external arithmetic
interpretation, and which remain unresolved.

## Audit method

Each concept is tested against the core admission question:

> Is this concept necessary to define form and its intrinsic transformations
> independently of every external interpretation?

and against the Arithmetic Erasure Test:

> After removing prime/integer/product/exponent/factorization/value language and
> numeric examples, does the concept still have a necessary structural role?

Provisional classes are:

- `CORE` — evidence currently supports an intrinsic structural role;
- `REPRESENTATION` — needed for canonical encoding, addressing, or display, not
  for form ontology itself;
- `INTERPRETATION` — assigns external meaning to form;
- `HISTORICAL RESIDUE` — inherited and apparently unnecessary at every maintained
  boundary;
- `UNRESOLVED` — current evidence is insufficient to decide.

A concept may contain separable sub-concepts with different classifications.
Where that happens, the audit explicitly splits them instead of forcing one
label onto an overloaded term.

## Summary matrix

| Current concept | First-pass classification | Main finding |
| --- | --- | --- |
| `Leaf` | `CORE` with representational/arithmetic spelling | A terminal form appears structurally necessary; spelling it as `1` is not |
| `Container` | `CORE` candidate / `UNRESOLVED` details | Recursive aggregation appears necessary; non-empty ordered container semantics need proof |
| `Product` | `INTERPRETATION` candidate | Multiplication is not used to establish current structural validity or rewrites |
| `Term` | `UNRESOLVED` | Some component/edge carrier appears necessary, but the current package may be arithmetic-shaped |
| `Root` | `REPRESENTATION` candidate | Current roots are explicitly state-scoped positional coordinates, not persistent ontology |
| `^` relation | `CORE` relation / `INTERPRETATION` name | A recursive edge appears intrinsic; exponentiation does not |
| ordering | `UNRESOLVED` | Current equality and defaults depend on order, but intrinsic necessity is unproved |
| addresses | `REPRESENTATION` | Addresses select locations in one state and carry no persistent identity |
| `SPROUT` | `UNRESOLVED` | Width growth is structurally meaningful if ordered aggregation is intrinsic |
| `SHED` | `UNRESOLVED` | Width reduction is structurally meaningful if leaf components/aggregation are intrinsic |
| `GRAFT` | `UNRESOLVED` | Depth growth is structurally meaningful if the recursive relation is intrinsic |
| `PRUNE` | `UNRESOLVED` | Depth reduction is structurally meaningful if the recursive relation is intrinsic |

No current concept is classified as `HISTORICAL RESIDUE` in this first pass.
Historical origin alone is not enough: residue requires evidence that the
concept is unnecessary to core, representation, and every deliberately retained
interpretation boundary.

## 1. `Leaf`

### Current normative role

The specification defines `Leaf ::= 1`, calls `Leaf` the terminal PETRA object,
forbids an empty container, and restores `Leaf` when a rewrite removes the last
term from a container.

### Arithmetic erasure

The structural role survives if the token `1` and all multiplicative-identity
language are erased. PETRA still needs a base case if the present finite
recursive construction is retained.

A neutral formulation could be conceptually equivalent to:

```text
Form ::= Terminal | Composite
```

without assigning a numeric meaning to `Terminal`.

### First-pass classification

- terminal/base-case concept: **`CORE` candidate with strong evidence**;
- textual token `1`: **`REPRESENTATION` today**, with obvious arithmetic
  genealogy;
- interpretation `Terminal -> 1`: **`INTERPRETATION`**.

### Open obligation

Determine whether PETRA intrinsically requires exactly one terminal form or
whether a more general abstract system could admit multiple terminal atoms.
The present model supports exactly one.

## 2. `Container`

### Current normative role

A container owns an ordered, non-empty sequence of visible terms. Recursion is
realized because each term points to a complete PETRA object.

### Arithmetic erasure

The need for some way to compose more than one recursively nested component
survives arithmetic erasure if PETRA is to retain width as well as depth.
However, three current properties do not yet follow merely from "form":

1. aggregation is non-empty;
2. aggregation is ordered;
3. aggregation consists specifically of current `Term` objects.

### First-pass classification

**`CORE` candidate for recursive aggregation; `UNRESOLVED` for its current exact
semantics.**

The word `Container` itself is sufficiently neutral. What remains to prove is
which of its constraints are intrinsic.

### Open obligation

Construct alternative candidate models with unordered or multiset aggregation
and compare equality, canonicalization, and operator behavior.

## 3. `Product`

### Current normative role

The grammar says:

```text
Container ::= Product(Term+)
```

but current structural validity, equality, addressing, and rewrites operate on
the contained sequence rather than performing multiplication.

### Arithmetic erasure

Removing the word `Product` does not obviously remove any structural mechanism.
A neutral `Composite(Component+)` or equivalent could express the observed
structural role.

### First-pass classification

**`INTERPRETATION` candidate.**

The arithmetic interpretation may read composition as multiplication, but the
current structural algorithms do not require multiplication to operate.

It is **not yet `HISTORICAL RESIDUE`**, because the arithmetic interpretation is
a deliberately retained external interpretation and may legitimately use this
word at that boundary.

### Open obligation

Prove that no current core invariant depends on product laws such as
commutativity, associativity, identity, or factor semantics. Current evidence
suggests that it does not, but this must be checked systematically.

## 4. `Term`

### Current normative role

A term owns one root identity and exactly one relation to a complete PETRA
object. Terms are the visible children selected by numeric address segments.
Leaf terms are also direct targets of `SHED` and `PRUNE`.

### Arithmetic erasure

Some structural carrier is likely necessary if a composite owns distinguishable
components that each lead recursively to another form. What is not established
is whether this carrier must have the exact current decomposition:

```text
Term = Root + one exponent relation
```

A more abstract model might treat a component simply as an edge to a subform,
with position supplied by representation rather than by an owned root object.

### First-pass classification

**`UNRESOLVED`.**

A component-like concept appears necessary, but the current `Term` object may
mix core relation, positional representation, and arithmetic terminology.

### Open obligation

Try a minimal model in which a composite is merely a collection/sequence of
recursive child forms. Determine which current semantics cannot be recovered
without an explicit `Term` object.

## 5. `Root`

### Current normative role

The specification explicitly defines `Root` as opaque, nonnumeric, positional,
container-scoped, and recomputed after every successful rewrite. `r0`, `r1`, ...
are not persistent identities and do not carry prime labels or numeric value.

### Arithmetic erasure

The current `Root` survives arithmetic erasure only as a way to name a
component position in one canonical state. Structural equality already derives
root ranks from corresponding positions rather than using them as persistent
identity.

### First-pass classification

**`REPRESENTATION` candidate with strong evidence.**

The current evidence suggests:

```text
core component position
        -> canonical representation rank rN
```

rather than:

```text
core object Root(rN)
```

### Open obligation

Build an equivalent in-memory abstract model without explicit root identities
and test whether canonical equality and all four rewrites can be expressed
without loss. If yes, `Root` should remain only at the representation boundary.

## 6. `^` relation

### Current normative role

Every term has one relation to a complete PETRA object. The relation can target
`Leaf` or a materialized `Container`; `GRAFT` and `PRUNE` operate directly on
this relation state. The specification already says `^` is a relation target,
not a node and not the numeric value one.

### Arithmetic erasure

The **recursive relation** survives. The interpretation "exponentiation" does
not need to survive.

Without some relation from a component to a nested form, current depth semantics
would disappear. But nothing in the structural rewrite mechanics requires that
relation to mean exponentiation.

### First-pass classification

- existence of one recursive child relation per component: **`CORE` candidate**;
- name "exponent", symbol `^`, and arithmetic exponentiation meaning:
  **`INTERPRETATION` / `REPRESENTATION`**.

### Open obligation

AIP-2 must determine whether "exactly one" recursive relation is intrinsic or
only inherited from prime-exponent syntax. A more general form algebra might
allow zero, one, or several typed relations per component.

## 7. Ordering

### Current normative role

The specification currently makes order semantically visible:

- containers own ordered sequences;
- canonical equality compares corresponding sequence positions;
- ranks derive from visible order;
- `SPROUT` appends at the end;
- `SHED` default selects the last eligible top-level leaf;
- `GRAFT` and other defaults use canonical traversal/tie-breaking order.

### Arithmetic erasure

Order still exists after removing arithmetic vocabulary because the current
specification explicitly includes it. That shows **operational dependence**, not
**intrinsic necessity**.

The central unresolved question is whether two composites differing only by
sibling permutation are genuinely different forms or merely different
representations of one abstract form.

### First-pass classification

**`UNRESOLVED`.**

This is one of the highest-impact audit results because changing the answer
would affect equality, canonicalization, addresses, default target selection,
serialization, and possibly the operator graph.

### Open obligation

AIP-3 should compare at least:

1. ordered-tree semantics;
2. unordered-tree semantics;
3. multiset-of-children semantics with deterministic canonical rendering.

No migration should occur until the effect on equality and operators is known.

## 8. Addresses

### Current normative role

Addresses are explicitly state-scoped selectors. Numeric segments select visible
terms in current canonical order; `^` selects the owned relation. Rewrites can
create, destroy, invalidate, or retarget addresses. The specification explicitly
forbids treating them as persistent identity.

### Arithmetic erasure

Addressing remains useful even in a completely non-arithmetic PETRA, but a
specific textual address is not part of the ontology of the addressed form.

### First-pass classification

**`REPRESENTATION`.**

This classification is comparatively strong: the specification itself treats
addresses as state-relative selection machinery rather than enduring identity.

### Open obligation

If ordering changes under AIP-3, the address scheme may need redesign even if
the abstract ability to select a structural location remains.

## 9. `SPROUT`

### Current normative role

`SPROUT` adds width by appending one canonical leaf term to a selected
container, or materializes a root leaf into a one-term container.

### Arithmetic erasure

The operation can be restated without arithmetic:

> add one terminal component to a selected composite.

Thus its structural idea survives arithmetic erasure. However, its exact
semantics depend on currently unresolved assumptions:

- composites are ordered;
- a component/term is intrinsic;
- appending "at the end" matters;
- there is exactly one terminal form.

### First-pass classification

**`UNRESOLVED`, with a plausible future `CORE` role.**

### Open obligation

Re-evaluate after AIP-1 and AIP-3. In an unordered model, `SPROUT` may remain a
well-defined width-growth generator while "append at end" disappears into
canonical representation.

## 10. `SHED`

### Current normative role

`SHED` removes one selected leaf term from its parent composite and restores
`Leaf` when that removal empties the parent.

### Arithmetic erasure

The operation can be restated structurally:

> remove one terminal component; if the composite becomes empty, restore the
> terminal form according to the current closure rule.

No division or numeric mutation is necessary.

### First-pass classification

**`UNRESOLVED`, with a plausible future `CORE` role.**

Its exact meaning depends on whether terminal components, non-empty composites,
and the empty-to-terminal collapse are intrinsic.

### Open obligation

Determine whether `SHED` is a genuine partial inverse of abstract width growth
under each candidate composition ontology.

## 11. `GRAFT`

### Current normative role

`GRAFT` replaces a terminal relation target with a one-component composite,
thereby adding depth.

### Arithmetic erasure

The operation survives cleanly as a structural depth-growth rewrite if the
recursive relation itself is intrinsic. The labels "exponent", "exponent-one",
and symbol `^` are unnecessary to state the transformation.

### First-pass classification

**`UNRESOLVED`, with a strong plausible future `CORE` role.**

The unresolved dependency is AIP-2: whether the exact one-relation component
model is intrinsic.

### Open obligation

Restate and test `GRAFT` on a neutral relation model before any semantic
promotion.

## 12. `PRUNE`

### Current normative role

`PRUNE` removes a narrowly defined nested terminal component and restores its
owning relation to the terminal state. It acts as the structural counterpart to
`GRAFT` under current preconditions.

### Arithmetic erasure

Like `GRAFT`, its structural meaning survives without arithmetic vocabulary if
one recursive relation and terminal restoration are intrinsic.

### First-pass classification

**`UNRESOLVED`, with a strong plausible future `CORE` role.**

### Open obligation

Determine whether the current singleton-parent precondition is intrinsic to
safe inverse depth reduction or merely an artifact of the current
prime-exponent-shaped grammar.

## 13. What the first pass already tells us

The current PETRA specification has already removed more arithmetic semantics
than its vocabulary suggests. In particular:

- root ranks are explicitly nonnumeric positional coordinates;
- numeric projection is already optional and external;
- operators mutate structure directly rather than arithmetic values;
- addresses are structural and state-scoped;
- the `^` slot is already specified as a relation target rather than a numeric
  exponent value.

The strongest remaining arithmetic traces appear to be **semantic names and
shape constraints**, not active numeric computation.

The audit therefore suggests a likely decomposition:

```text
candidate abstract core
    terminal form
    recursive composite
    recursive component/relation
    intrinsic structural rewrites (to be proved)

canonical representation
    positional ranks
    addresses
    serialization
    deterministic rendering/order if order proves non-intrinsic

arithmetic interpretation
    terminal -> 1
    composition -> multiplication
    recursive relation -> exponentiation
    positional components -> prime/base assignment
    whole form -> integer/value
```

This is a hypothesis, not a promoted architecture.

## 14. Highest-priority unresolved questions

The first pass identifies three dependencies that should be investigated before
operator completeness or non-arithmetic examples:

1. **AIP-3 order semantics** — because order currently affects equality,
   representation, addressing, and all default operator selection.
2. **AIP-2 relation ontology** — because it determines whether `Term`, `^`,
   `GRAFT`, and `PRUNE` reflect an intrinsic recursive edge or inherited
   exponent syntax.
3. **AIP-1 composition ontology** — because it determines whether `Container`,
   `Product`, width, `SPROUT`, and `SHED` have the right abstract basis.

Only after these three are better constrained should AIP-4 generative
completeness be stated over a candidate abstract grammar. AIP-5 then tests
whether that grammar genuinely extends beyond the arithmetic interpretation.

## 15. First-pass conclusion

The Arithmetic Erasure Test does **not** collapse PETRA. A recognizable
structural system remains after arithmetic meaning is removed.

But the test also shows that the current specification cannot yet be declared a
fully interpretation-independent algebra of forms, because order, exact
component structure, and the one-relation model are still embedded as normative
shape constraints without an independent necessity argument.

The next research step should therefore not be a rename. It should be an
alternative-model comparison for AIP-3, AIP-2, and AIP-1, in that order, with
counterexamples demonstrating exactly which distinctions each candidate model
preserves or erases.