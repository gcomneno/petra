# PETRA Phase 7 — normative promotion boundary

Status: **Phase 7 boundary decision** for issue #313 under programme #276.

Phase 6 is complete. This note defines what is eligible for normative promotion before any change to `docs/reference/SPEC.md`.

It is intentionally narrow: no runtime, API, CLI, serialization, Resolver, or arithmetic-projection change is made here.

## 1. Governing rule

Phase 7 promotes only research statements that are both:

1. mathematically stable enough for normative use; and
2. necessary to define PETRA itself.

Research results may remain valid without becoming normative PETRA semantics.

The promotion boundary is therefore:

```text
canonical semantic core
    -> candidate for normative SPEC

meta-theory / provenance / open questions
    -> remain research
```

## 2. Current SPEC versus validated research core

| Topic | Current normative SPEC v2.0.0 | Validated research core | Phase-7 decision |
| --- | --- | --- | --- |
| carrier | `PETRA ::= Leaf | Container` | one recursive species `P ::= Node(M_f(P))` | **PROMOTE** research carrier |
| zero-child case | separate `Leaf ::= 1` | `Z = Node(empty)`, arity-zero case of `Node` | **PROMOTE** |
| child collection | ordered non-empty visible `Term+` sequence | finite multiset of child forms, multiplicity intrinsic, no sibling order | **PROMOTE** |
| primitive relation | exponent relation through `Term`/`Root` | direct parent-child incidence | **PROMOTE** |
| identity | state-scoped positional `Root` ranks | no persistent occurrence identity in carrier | **PROMOTE** carrier rule |
| equality | recursive ordered sequence equality | rooted non-plane tree isomorphism / multiset-recursive equality | **PROMOTE** |
| elementary edits | `SPROUT / SHED / GRAFT / PRUNE` | elementary leaf `ADD / REMOVE`; stronger subtree edits are not elementary | **PROMOTE** ADD/REMOVE semantic core |
| interpretation | prime/exponent reading embedded in product terminology | interpretations depend on PETRA; PETRA does not depend on an interpretation | **PROMOTE** boundary |
| serialization | `C(r0^...)` with positional ranks | representation is not ontology | **DEFER** redesign |
| resolver / addresses | positional, state-scoped addresses | targeting is operation-local representation, not carrier identity | **DEFER** redesign |
| runtime/API/CLI | v2.0.0 executable contract | not part of mathematical promotion itself | **DEFER** |

## 3. Direct semantic conflicts

The current normative SPEC and the validated research carrier cannot both remain canonical without qualification.

### Conflict A — one constructor versus two constructors

Current:

```text
PETRA ::= Leaf | Container
```

Research:

```text
P ::= Node(M_f(P))
Z = Node(empty)
```

The research result makes the zero-child form an arity-zero case of the same recursive species. Therefore `Leaf` cannot remain a second ontological constructor if the research carrier is promoted.

### Conflict B — ordered children versus unordered multiplicity

Current containers own an ordered sequence of terms and equality compares corresponding positions.

The validated carrier has no intrinsic sibling order. Equal child forms may occur with multiplicity, but permutation of siblings does not change the PETRA form.

This is a normative semantic conflict, not a notation cleanup.

### Conflict C — positional roots versus carrier identity

Current `Root` ranks are state-scoped positional identities.

The validated carrier has no persistent node identity and does not need root ranks to define equality. Occurrence identity exists only inside a chosen realization for local targeting/proofs.

Therefore positional ranks may survive later as an addressing/serialization mechanism, but they cannot define canonical PETRA identity.

### Conflict D — four public operators versus two elementary edits

The current SPEC canonically names `SPROUT`, `SHED`, `GRAFT`, and `PRUNE`.

AIP-4 establishes the intrinsic elementary edit system as leaf ADD/REMOVE. Subtree insertion/deletion is stronger than one elementary step.

Phase 7 should therefore promote ADD/REMOVE first. The fate of the four historical public operators is a later compatibility/API decision, not part of the carrier promotion.

## 4. Promotion set

The following are approved **promotion candidates** for the next normative slice:

```text
P ::= Node(M_f(P))

Z := Node(empty)

primitive structure:
    finite rooted non-plane realization
    direct parent-child incidence
    finite multiplicity
    no intrinsic sibling order
    no persistent occurrence identity

equality:
    root-preserving structural isomorphism
    equivalently recursive multiset equality

elementary intrinsic edit relations:
    ADD one fresh zero-child occurrence
    REMOVE one non-root zero-child occurrence

interpretation boundary:
    interpretation depends on PETRA
    PETRA does not depend on interpretation
```

These candidates are supported by the completed research/validation programme. Promotion does not imply novelty.

## 5. Keep research-only

The following remain research-level and are **not** normative requirements:

- global `Aut(E_P)` triviality;
- completeness of cancellation plus independent commutation;
- full residual-system / DRS / SDRS membership;
- witnessed-path presentation machinery;
- global edit-graph reconstruction questions;
- provenance classifications themselves;
- bounded probes;
- novelty claims.

No `OPEN` result is promoted.

## 6. Deferred compatibility surfaces

These require separate Phase-7 decisions after the semantic core changes:

- canonical textual serialization;
- positional addresses and Resolver behavior;
- `SPROUT / SHED / GRAFT / PRUNE` public compatibility;
- runtime object model;
- CLI/API schemas;
- trace/witness serialization;
- arithmetic or prime/exponent projection.

They must be derived from the promoted carrier, not used to constrain it retroactively.

## 7. Smallest safe next normative delta

The next Phase-7 issue should change **only the object-model/equality foundation of the normative SPEC**:

```text
SPEC section 1:
    Leaf | Container | Term | Root ontology
        ->
    Node(M_f(P)) carrier + direct incidence + Z

ordered sibling equality
        ->
    unordered multiplicity-preserving structural equality
```

That next slice should explicitly avoid:

```text
operators
serialization
addresses
Resolver
runtime
CLI/API
arithmetic projection
```

Those surfaces will necessarily need later reconciliation, but combining them into the first normative change would make the semantic promotion unnecessarily large.

## 8. Boundary result

```text
PHASE_7_PROMOTION_BOUNDARY = DEFINED

NEXT:
    normative carrier + equality delta only
```

No normative file has been modified by this issue.
