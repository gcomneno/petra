# PET/PEG 2.0 Object-Native Operators

## Status and scope

This document is the normative PET/PEG 2.0 contract for the canonical
object-native operators:

- `SPROUT`
- `SHED`
- `GRAFT`
- `PRUNE`

It specifies a future structural layer.  It does **not** change the stable
`pet` CLI or implement these operations.  `NEW`, `DROP`, `INC`, and `DEC`,
including the prime-label addresses and value-level application recorded in
the earlier PET/PEG 2.0 notes, are superseded as *canonical PET operator
semantics*.  They remain useful historical and research material.

The contract is shape-first: an operator first determines an object shape.
A numeric projection, if a later layer needs one, is derived only from that
completed shape.  No rule in this document selects a next integer or prime,
performs arithmetic increment/decrement, multiplies/divides a represented
value, refactors an after-value, or chooses a numerically convenient
representative.

## 1. Object model

### 1.1 Grammar and roles

The normative grammar is:

```text
PET       ::= Leaf | Container
Leaf      ::= 1
Container ::= Product(Term+)
Term      ::= Root ^ PET
```

`Container` owns an ordered, non-empty sequence of visible `Term` values.
`Term` owns exactly one root identity and exactly one exponent relation to a
complete `PET` object.  `Leaf` is the terminal PET object.  It is not a
container, a term, a root, or an empty product.

When a term's exponent is `Leaf`, its canonical exponent-one relation is
implicit in compact notation.  The relation nevertheless owns a latent slot,
written `^`, at which that `Leaf` can be materialized into depth.  Thus `^`
is a relation target, not a node and not the numeric value one.

An empty container is never a PET value.  Any rewrite that removes the last
term from a container replaces that container with `Leaf`; this is the
canonical leaf restoration rule.

### 1.2 Root identities and canonical order

`Root` is an opaque, nonnumeric **positional identity**.  It is neither a
prime label nor an integer.  Within one container in one shape state, its
canonical spellings are the ordinal ranks `r0`, `r1`, ..., in visible-term
order.  They are scoped to that container and are recomputed after every
successful rewrite.  Thus `r0` is not a persistent instance identity: a term
that was `r1` before a sibling deletion can be `r0` afterwards, and a newly
appended term receives its rank only after canonicalization.

Here, “opaque identity” means that the rank is not interpreted as a number,
prime label, allocation token, or history-bearing object identifier.  It does
not mean immutable identity across shape states.  A root rank identifies a
term position only together with its containing state and container.  This is
the same state-scoped positional basis as an address, so rank recomputation
can retarget an old textual address without contradicting root opacity.

The canonical child order is the sequence of those ranks.  A new term is
inserted after the last visible term of its selected container; all ranks are
then assigned from zero in sequence.  Deletion closes the sequence and
reassigns ranks.  This rule is deterministic and depends only on the input
shape and invocation.  It does not depend on object allocation order,
traversal order, insertion history external to the current state, prime
labels, or numeric magnitude.

Root identities are unique within their container.  Multiple leaf terms are
allowed: they are distinct terms because their root identities differ.  This
is the only duplicate constraint needed by these operators.  In particular,
"canonical leaf" means `r^1` with its exponent relation to `Leaf`; it does
not mean a chosen prime.

### 1.3 Shape notation and illustrative numeric notation

This document writes a container as `C(r0^P0, r1^P1, ...)`.  For example,
the anonymous shape illustrated by the familiar `2^2` is:

```text
A = C(r0^C(r0^1))
```

The familiar expression is only a post-rewrite illustration obtained by a
separate canonical display/projection layer.  It is never an operator input
or target-selection mechanism.  Under that illustrative mapping, the shapes
used below display as follows:

```text
C(r0^C(r0^1), r1^1)          -> 2^2 * 3
C(r0^C(r0^1, r1^1))          -> 2^(2 * 3)
C(r0^C(r0^C(r0^1)))          -> 2^(2^2)
```

The examples do not assert that these numbers are chosen before the shape
rewrite, nor that the root identities are prime labels.

## 2. Positional structural addresses

### 2.1 Syntax

The normative serialized address grammar is:

```text
anchor-address ::= "@/"
term-address   ::= "@/" index ("/" index)*
slot-address   ::= term-address "/^"
index          ::= "0" | nonzero-digit digit*
```

`@/` is a semantic anchor for the top-level PET object.  It is not a PET node,
container, term, leaf, root, or relation.  A numeric segment selects one
visible **term** in the current container's canonical child order.  To follow
another segment, the selected term's exponent target must be a `Container`;
the next segment selects a term in that exponent container.  A segment cannot
select a container, a leaf object, a root identity, or an exponent relation.

`^` identifies the exponent relation owned by the immediately preceding term.
Whether that relation is its latent exponent-one slot is an operator target
check, not address traversal: it is latent exactly when its current target is
`Leaf`. For `A` above, `@/0/0/^` identifies the latent slot of the inner
`r0^1` term. No prime label is involved.

The expected target type completes resolution:

| Operator target | Address form | Resolution result |
| --- | --- | --- |
| SPROUT root anchor | `@/` | semantic root anchor; its current PET may be a `Container` or `Leaf` |
| nested container | term address | selected term's exponent target, which must be a container |
| leaf term | term address | selected term itself, which must have exponent `Leaf` |
| exponent relation | slot address | selected term's exponent relation; its target is checked by the operator |

For `SPROUT`, `@/` is the semantic root anchor in both default and explicit
mode.  When the root PET is `Leaf`, either mode materializes it as
`C(r0^1)`.  No term address projects a `Leaf` into a container.

### 2.2 Resolution failures and shape-state scope

Addresses belong to exactly one pre-rewrite shape state.  They must be parsed
and resolved against that state before a rewrite starts.  The stable generic
resolution reasons are:

- `address-malformed`
- `address-out-of-range`
- `address-crosses-leaf`

The following ordered pipeline assigns exactly one stable failure reason to
every invocation; a later phase is never evaluated after an earlier failure.

1. Validate the invocation envelope: it must use the invocation schema,
   name one of the four operators, and contain exactly a valid `target` mode
   and the fields required by that mode. Any violation is
   `invocation-invalid`.
2. For `target.mode: "explicit"`, parse the address. A grammar failure is
   `address-malformed`.
3. Traverse its numeric term segments in the pre-rewrite shape. A missing
   selected term is `address-out-of-range`; an attempt to continue through a
   selected term whose exponent is `Leaf` is `address-crosses-leaf`. A final
   `^` identifies its owner relation whether that relation is latent or
   materialized.
4. Apply the selected operator's target-form and shape preconditions in the
   operator-specific order stated below. These checks, including whether a
   slot is latent, never emit a generic address reason.
5. For `target.mode: "default"`, skip address phases 2–3 and select from the
   operator's eligible pre-rewrite targets. If none exists, emit that
   operator's stated `*-no-eligible-*` reason.

Consequently, `address-kind-mismatch` and `slot-not-latent` are not reason
identifiers in this contract. An explicit target of the wrong syntactic form
or structural kind is reported by the applicable operator-specific reason;
an explicit GRAFT slot whose exponent is already a container is
`graft-slot-already-materialized`.

After a successful rewrite, clients must resolve any address again.  A rewrite
may create, destroy, invalidate, or retarget an address.  Canonical rank
renumbering alone can retarget a positional address. Since those ranks are
positional rather than persistent identities, a client must not infer that an
old textual address denotes the same term, container, or relation in the
result.

`address_effects` in a result is descriptive rather than an identity promise:
it records the target address used before the rewrite and any returned
post-rewrite witness address.  Implementations may additionally classify
tracked addresses as `stable`, `created`, `destroyed`, `retargeted`, or
`invalid`; no classification makes the old address reusable without resolving
it in the after-shape.

## 3. Invocation and result serialization

The normative machine-readable invocation is JSON with an explicit target
mode. Omission is invalid; it never silently means a default. Invocation and
result use distinct serialized schema values.

```json
{
  "schema": "pet.object-native-operator-invocation.v1",
  "operator": "SPROUT",
  "target": { "mode": "default" }
}
```

An explicit target is:

```json
{
  "schema": "pet.object-native-operator-invocation.v1",
  "operator": "GRAFT",
  "target": { "mode": "explicit", "address": "@/0/0/^" }
}
```

The human-readable forms are `SPROUT`, `SHED`, `GRAFT`, and `PRUNE` for a
default, and `OPERATOR @/…` for an explicit target, for example
`GRAFT @/0/0/^`.  `@/`, positional segments, and `^` are rendered exactly as
above; implementations must not translate them into prime-label paths.

A successful result has at least the exact serialized schema field shown:

```text
schema: "pet.object-native-operator-result.v1", status: "ok", operator, invocation_target, resolved_target,
before_shape, after_shape, address_effects, reason: "<op>-applied"
```

A failed result has at least the exact serialized schema field shown:

```text
schema: "pet.object-native-operator-result.v1", status: "failed", operator, invocation_target, before_shape,
reason: "<stable-reason-id>"
```

It has no `after_shape`.  A numeric projection may be an optional,
non-normative derived field and must not participate in resolution or
success/failure.

## 4. Structural rewrites

All rewrite rules below take a PET shape and the normalized invocation, resolve
the stated target, perform exactly the stated structural replacement, and then
canonicalize the affected container ranks.  Defaults are ergonomic target
selection only; they are not a separate operator semantics.

### 4.1 SPROUT — add width

`SPROUT` inserts one canonical leaf term at the end of a selected container.

| Item | Contract |
| --- | --- |
| Invocation | `SPROUT` with `target.mode` `default` or explicit container address |
| Explicit target | `@/` selects the semantic root anchor; a term address projects to that term's materialized exponent container |
| Default | the top-level insertion through `@/` |
| Preconditions | a term-address target must project to a container; the root anchor accepts either a root container or root `Leaf` |
| Explicit check order | accept `@/`; otherwise accept a term address only if its selected term's exponent is a `Container`; otherwise `sprout-target-not-container` |
| Rewrite | append one canonical leaf term: `C(t0,...,tn) -> C(t0,...,tn,r(n+1)^1)`, then re-canonicalize ranks; root `Leaf -> C(r0^1)` for either root-anchor mode |
| Success reason | `sprout-applied` |
| Failure reasons | `invocation-invalid`, generic address reason, `sprout-target-not-container` |
| Address effect | the new leaf has a returned witness address; all old positional addresses must still be re-resolved |

The appended leaf receives the terminal rank after canonicalization, so no
container-scoped positional identity is duplicated. It is not a newly chosen
prime.

Default example from `A`:

```text
SPROUT
C(r0^C(r0^1)) -> C(r0^C(r0^1), r1^1)
```

Only after this rewrite may it be illustrated as `2^2 -> 2^2 * 3`.

Root-leaf anchor example (both invocations have the same result):

```text
SPROUT                 SPROUT @/
Leaf -> C(r0^1)        Leaf -> C(r0^1)
```

Explicit example:

```text
SPROUT @/0
C(r0^C(r0^1)) -> C(r0^C(r0^1, r1^1))
```

Here `@/0` selects the outer term and projects to its exponent container.  The
post-rewrite illustrative notation is `2^(2 * 3)`.

### 4.2 SHED — remove width

`SHED` deletes one selected canonical leaf **term** from its parent container.
The explicit target always denotes the leaf term, never its parent container.

| Item | Contract |
| --- | --- |
| Invocation | `SHED` with `target.mode` `default` or explicit leaf-term address |
| Explicit target | the term address must resolve to a direct leaf term (`Term(root, Leaf)`) |
| Default | the last eligible direct leaf term of the top-level container in canonical order |
| Preconditions | target is an eligible leaf term; its parent is a container |
| Explicit check order | accept a term address only if its selected term's exponent is `Leaf`; otherwise `shed-target-not-leaf` |
| Rewrite | remove that term from its parent; if no terms remain, replace the parent container with `Leaf` |
| Success reason | `shed-applied` |
| Failure reasons | `invocation-invalid`, generic address reason, `shed-target-not-leaf`, `shed-no-eligible-top-level-leaf` |
| Address effect | removed target is destroyed; siblings can be retargeted by rank closure; an emptied parent is replaced by `Leaf` |

The collapse of an emptied container to `Leaf` is canonical leaf restoration,
not a numeric deletion or division.

`shed-target-not-direct-child` is not a reason identifier in this contract.
Every term selected by a valid term address is a direct child of the container
traversed immediately before that segment, including nested leaf terms; SHED's
only explicit target-type check is therefore `shed-target-not-leaf`.

Default example:

```text
SHED
C(r0^C(r0^1), r1^1) -> C(r0^C(r0^1))
```

It may then be displayed as `2^2 * 3 -> 2^2`.

Explicit example:

```text
SHED @/0/1
C(r0^C(r0^1, r1^1)) -> C(r0^C(r0^1))
```

`@/0/1` is the selected inner leaf term; it is not an address for its parent
exponent container.

### 4.3 GRAFT — add depth

`GRAFT` materializes a selected latent exponent-one slot by replacing its
`Leaf` target with a one-term container containing a canonical leaf.

| Item | Contract |
| --- | --- |
| Invocation | `GRAFT` with `target.mode` `default` or explicit slot address |
| Explicit target | `term-address/^`; the selected relation must be latent (its current exponent target is `Leaf`) |
| Default | deepest eligible latent slot; ties select the last slot in canonical preorder order |
| Preconditions | the slot is latent; an already materialized exponent is ineligible |
| Explicit check order | if the address is not a slot address, `graft-target-not-slot`; otherwise accept a relation targeting `Leaf`, or emit `graft-slot-already-materialized` |
| Rewrite | `r^1 -> r^C(r0^1)` at the selected relation |
| Success reason | `graft-applied` |
| Failure reasons | `invocation-invalid`, generic address reason, `graft-target-not-slot`, `graft-slot-already-materialized`, `graft-no-eligible-latent-slot` |
| Address effect | the old `^` slot is consumed; its new terminal child is returned as a witness; deeper addresses are created |

Depth is the number of term segments from `@/` to the relation's owner term.
Canonical preorder compares sibling indices left to right; "last" means the
greatest eligible owner-term path at equal depth.  This is structural
tie-breaking, not numeric ordering.

Default example (the only eligible slot in `A`):

```text
GRAFT
C(r0^C(r0^1)) -> C(r0^C(r0^C(r0^1)))
```

The post-rewrite illustrative notation is `2^2 -> 2^(2^2)`.

Explicit example:

```text
GRAFT @/0/0/^
C(r0^C(r0^1)) -> C(r0^C(r0^C(r0^1)))
```

For a tie, the eligible slots of
`C(r0^C(r0^1), r1^C(r0^1))` are `@/0/0/^` and `@/1/0/^`; the default selects
`@/1/0/^` because it is last in canonical order.

### 4.4 PRUNE — remove depth

`PRUNE` deletes an eligible terminal leaf term from a singleton exponent
container and restores its parent term's implicit exponent-one slot.

| Item | Contract |
| --- | --- |
| Invocation | `PRUNE` with `target.mode` `default` or explicit terminal-leaf term address |
| Explicit target | the address selects the leaf term itself |
| Default | deepest eligible terminal leaf; ties select the last eligible leaf in canonical preorder order |
| Preconditions | selected term has exponent `Leaf`; it is the sole term of a container; that container is the exponent target of a parent term (never the root container) |
| Explicit check order | if the address is not a term address or its term's exponent is not `Leaf`, `prune-target-not-terminal-leaf`; otherwise if its parent is the root container, `prune-target-has-no-parent-relation`; otherwise if that parent is not singleton, `prune-parent-not-singleton-exponent`; otherwise accept |
| Rewrite | let `p` be the selected leaf term, `E = C(p)` its singleton parent exponent container, and `q` the parent term whose exponent relation targets `E`. Destroy `p`, `E`, and the relation `q -> E`; create the replacement relation `q -> Leaf`, which is `q`'s restored latent `^` slot. `q` and its containing/ancestor relations remain. |
| Success reason | `prune-applied` |
| Failure reasons | `invocation-invalid`, generic address reason, `prune-target-not-terminal-leaf`, `prune-parent-not-singleton-exponent`, `prune-target-has-no-parent-relation`, `prune-no-eligible-terminal-leaf` |
| Address effect | the selected terminal term and its singleton exponent container are destroyed; the restored parent `^` slot is returned as a witness; ancestor paths must be re-resolved |

"Terminal" here is deliberately stronger than "leaf": it requires both a
leaf exponent and the singleton exponent-container parent relation.  Therefore
`PRUNE` cannot remove one sibling from a wider exponent container; that is
width removal and belongs to `SHED`.

A terminal leaf term has no materialized descendants: its exponent is `Leaf`.
PRUNE therefore does not destroy descendants of `p`; it destroys exactly `p`,
its singleton container `E`, and their parent exponent relation, then creates
the `q -> Leaf` relation described above.

Default example:

```text
PRUNE
C(r0^C(r0^C(r0^1))) -> C(r0^C(r0^1))
```

The result may be illustrated as `2^(2^2) -> 2^2`.

Explicit example:

```text
PRUNE @/0/0/0
C(r0^C(r0^C(r0^1))) -> C(r0^C(r0^1))
```

## 5. Partial inverse laws

These are local, witness-aware rewrite laws.  They are not total algebraic
inverses and neither operator name nor a default invocation carries enough
history to make them total.

### 5.1 SPROUT and SHED

If `SPROUT` succeeds on a container `C`, let `w` be the returned address of
the appended leaf in the after-shape.  Re-resolve `w` in that after-shape and
apply explicit `SHED w`.  The result is structurally equal to the before-shape
provided no intervening rewrite changed that selected container.  A rewrite
witness is sufficient; invocation history is not otherwise required.

Conversely, if `SHED` removes the final visible term of its parent container
and that parent remains a container, a re-resolved explicit `SPROUT` at that
parent reconstructs the before-shape.  If the deleted term was not final,
`SPROUT` has no position argument and appends instead, so it cannot restore
the original order.  If SHED collapsed the root container to `Leaf`, only the
default anchor can restore a one-leaf root shape.

Defaults make this partial.  A nested `SPROUT @/0` is not undone by default
`SHED`, which searches only the top-level container.  In
`C(r0^1, r1^C(r0^1), r2^1)`, shedding `@/0` and then sprouting at the root
produces `C(r0^C(r0^1), r1^1, r2^1)`, not the original ordering.  Positional
addresses also change as ranks close: an old `@/1` can select a different term
after deleting `@/0`.  Even without a default, a container with several
eligible leaf terms requires the returned SPROUT witness (or an explicit
after-shape target): shedding a different eligible leaf is a valid rewrite,
not the stated inverse.

### 5.2 GRAFT and PRUNE

If `GRAFT` succeeds at latent slot `s`, let `w` be its returned singleton
terminal-leaf witness.  Re-resolve `w` in the after-shape and apply explicit
`PRUNE w`; it restores the original latent slot and before-shape, provided no
intervening rewrite altered the parent relation.  The witness is sufficient;
an invocation history is not required.

Conversely, a successful explicit `PRUNE` returns the restored slot witness.
Re-resolve it in the after-shape and apply explicit `GRAFT`; it restores the
pruned singleton depth.  The law fails outside PRUNE's singleton-parent
precondition because a non-singleton deletion is not a depth inverse.

Defaults are not an inverse guarantee.  If two eligible terminal leaves have
the same maximum depth, default `PRUNE` chooses the last one, which may not be
the leaf just grafted.  Likewise, default `GRAFT` can choose a deeper or later
newly available slot rather than the slot restored by a prior prune.  The
slot address consumed by GRAFT is invalid in its after-shape, and a terminal
leaf address consumed by PRUNE is invalid in its after-shape; each inverse
must use the returned after-shape witness rather than reuse the old address.

## 6. Compatibility and supersession inventory

| Current behavior/material | Conflict with this contract | Status and migration treatment |
| --- | --- | --- |
| `PETObject.children`, `value`, `prime_label`, `role`, and `kind` | representation is value-derived and stores prime-labelled child paths rather than object-native terms, containers, and relations | replace in a dedicated representation migration; retain bridge compatibility meanwhile |
| `pet_object_from_int`, legacy-tree bridge, and reconstruction after rewrite | determines shape from integer factorization and rebuilds an after-value | incompatible with structural rewrite; preserve only as legacy/projection bridge |
| prime-label paths such as `(2, 2)` | labels, rather than positions, select current objects | superseded by `@/…` positional addresses and `^` slots |
| `NEW` / `DROP` | selects or removes prime support and chooses fresh primes | superseded canonical vocabulary; historical/research semantics remain documented |
| `INC` / `DEC` | arithmetic exponent mutation by `+1` / `-1` | superseded canonical vocabulary; historical/research semantics remain documented |
| `apply_operator_by_value` | computes an `after_value` then calls `pet_object_from_int(after_value)` | incompatible; future rewrite engine must operate on shapes directly |
| experimental CLI operator-semantics commands and rewrite CLI labels | syntax and output expose `NEW/DROP/INC/DEC`, primes, and value targets | do not rename mechanically; add new opt-in syntax in a later CLI issue |
| graph edges and traversal | labels, neighbors, and deterministic ordering use old operators and fresh-prime enumeration | build separate object-native graph labels and traversal |
| traces and certificates | serialize values, prime-label addresses, old labels, and replay by value | version a shape-native trace/certificate schema; retain readers for historical traces |
| research probes and report matrices | probe old target rules, arithmetic mutation, and prime-labelled address stability | keep as legacy research probes; add separately named object-native probes |
| existing tests | assert construction from values and old labels/results | preserve as legacy coverage, then add a separate object-native suite |
| foundations and historical reports | some notes describe exploratory X/Y or current executable `NEW/DROP/INC/DEC` | add targeted supersession links; do not rewrite every historical report |

The current `NEW`, `DROP`, `INC`, and `DEC` contracts are therefore
superseded *only as canonical PET semantics*.  This does not erase their
research observations, stable PET-Base references, report provenance, or
historical trace interpretation.

## 7. Follow-up implementation issue split

The boundaries below intentionally separate representation, resolution,
rewriting, integration, and migration.  No GitHub issues are created by this
document.

### 1. Object-native PET shape representation

- Objective: introduce immutable `Leaf`, `Container`, `Term`, root-rank, and
  relation concepts without deriving identity from an integer.
- In scope: constructors, invariants, canonical rank normalization, shape
  equality, and fixture serialization of shapes.
- Non-goals: addresses, operators, numeric projection, CLI migration.
- Dependencies: none.
- Acceptance criteria: represents all grammar cases; forbids empty containers
  and duplicate local identities; deterministic canonical serialization has no
  prime labels or represented values.

### 2. Positional structural-address resolver

- Objective: parse and resolve `@/`, positional term paths, typed projections,
  and `^` slots against a shape.
- In scope: syntax, stable resolution reasons, target-kind resolution, and
  address-effect comparison helpers.
- Non-goals: rewrites or default target selection.
- Dependencies: issue 1.
- Acceptance criteria: resolves `@/0/0/^`; distinguishes containers, terms,
  leaves, and relations; rejects all generic failure cases deterministically.

### 3. Structural rewrite engine and result schema

- Objective: provide atomic shape rewrites and the versioned success/failure
  result contract.
- In scope: before/after shapes, witnesses, canonicalization, stable reasons,
  and no-op prevention.
- Non-goals: any one operator's policy, projection to integers, graph search.
- Dependencies: issues 1–2.
- Acceptance criteria: successful rewrites never reconstruct from an
  `after_value`; results distinguish `ok` and `failed`; witnesses are resolved
  in the after-shape.

### 4. SPROUT and SHED

- Objective: implement the width pair on the rewrite engine.
- In scope: explicit/default resolution, empty-container leaf restoration,
  inverse-witness behavior, and operator-specific reasons.
- Non-goals: depth operators, old `NEW/DROP` replacement, CLI exposure.
- Dependencies: issues 1–3.
- Acceptance criteria: all examples and partial-inverse preconditions in this
  contract pass, including nested explicit targets and rank retargeting.

### 5. GRAFT and PRUNE

- Objective: implement the depth pair on the rewrite engine.
- In scope: latent-slot materialization, singleton terminality, depth/tie
  defaults, inverse witnesses, and reasons.
- Non-goals: width operators or arithmetic exponent changes.
- Dependencies: issues 1–3.
- Acceptance criteria: `@/0/0/^` and `@/0/0/0` examples pass; non-singleton
  leaf deletion is rejected by PRUNE; default ties are deterministic.

### 6. Object-native CLI and serialization

- Objective: expose opt-in invocation parsing and versioned structural
  serialization without changing legacy command meanings.
- In scope: JSON invocation/result format, human rendering, address text, and
  backwards-compatible command boundary.
- Non-goals: removing legacy CLI syntax or changing stable PET-Base output.
- Dependencies: issues 1–5.
- Acceptance criteria: defaults require explicit `mode: default`; explicit
  paths render identically across CLI and JSON; legacy commands remain intact.

### 7. Shape-native traces, certificates, and graph labels

- Objective: record/replay structural operations and graph edges by shape and
  versioned invocation, not by value reconstruction.
- In scope: labels, path identity, witnesses, certificate replay, and bounded
  graph integration.
- Non-goals: route preference policy or conversion of legacy trace archives.
- Dependencies: issues 1–5; issue 6 for public serialization.
- Acceptance criteria: replay resolves every target in each before-shape;
  labels contain positional addresses; old trace schema remains readable as
  legacy data or reports an explicit version mismatch.

### 8. Object-native probes and tests

- Objective: add focused tests and research probes for shape rewrites and
  address effects.
- In scope: unit/property fixtures, 2^2 examples, defaults, failures,
  counterexamples, inverse partiality, and probe/report schema.
- Non-goals: deleting legacy probe/tests or treating old arithmetic findings as
  new semantics.
- Dependencies: issues 1–7 as applicable.
- Acceptance criteria: every normative example and stable reason is covered;
  tests demonstrate address invalidation and default non-inverse cases.

### 9. Documentation migration and legacy compatibility

- Objective: make active docs point to this contract while preserving research
  provenance and bridge guidance.
- In scope: references, supersession notices, compatibility table updates, and
  migration notes for implementation/API docs.
- Non-goals: broad historical-report rewrites or a mechanical global rename.
- Dependencies: this specification; coordinate with issues 1–8 as they land.
- Acceptance criteria: active canonical vocabulary is unambiguous; legacy
  documents identify their status; no documentation claims arithmetic
  `INC/DEC` is canonical object-native semantics.

### 10. Research specification: object-native symmetric relocation

- Objective: investigate a possible distinct `R` — structural relocation
  family containing `SWAP(address_a, address_b)`.
- In scope: a separate future specification for atomically exchanging two
  compatible structural subobjects without numeric reconstruction.
- Non-goals: adding `SWAP` to this contract or inferring any of its semantics
  from `SPROUT`, `SHED`, `GRAFT`, or `PRUNE`.
- Dependencies: issues 1–3; the future specification may additionally depend
  on the address and witness conventions established by issues 6–7.
- Acceptance criteria: deliberately deferred. That issue must independently
  define target compatibility, overlapping-address rules, canonical
  reordering, address witnesses, partiality, and any involution law before an
  implementation is proposed.

## 8. Conformance checklist

A conforming implementation of this contract must:

- represent the grammar and role boundaries in section 1;
- resolve positional, state-scoped addresses as specified in section 2;
- use the explicit invocation and stable outcome fields in section 3;
- implement all four rewrites, defaults, failures, and examples in section 4;
- preserve only the partial inverse laws and counterexamples in section 5;
- avoid every value-first or prime-selection rule prohibited by this document;
- treat the compatibility inventory and follow-up boundaries in sections 6–7
  as migration constraints.
