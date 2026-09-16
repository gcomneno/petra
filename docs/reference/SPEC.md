# PETRA Specification

## Status and authority

This document is the **single canonical specification** for:

**PETRA — Prime Exponent Tower Recursive Algebra**

It supersedes the active PET-Base, PET/PEG 2.0, and executable
PET-Metrics product architecture. Earlier documents remain historical,
research, or design evidence only. They do not define current PETRA behavior.

PETRA is shape-first. Its primary objects are recursive canonical structures,
not integers reconstructed through factorization.

The initial runtime does not require:

- concrete prime labels;
- primality testing;
- prime generation;
- integer factorization;
- numeric `encode` or `decode`;
- preservation of historical PET APIs, formats, commands, traces, or readers.

The word **Prime** names the intended mathematical interpretation of recursive
exponent towers. Any numeric projection is optional, derived after a complete
shape exists, and governed by a separate future contract.

The canonical structural operators are:

- `SPROUT`;
- `SHED`;
- `GRAFT`;
- `PRUNE`.

No value-first or prime-selection operation is part of canonical PETRA
semantics.

## Design principles

PETRA follows these rules:

1. one specification and one executable model;
2. recursive shape before numeric interpretation;
3. canonical positional identity rather than persistent labels;
4. direct structural rewrites rather than arithmetic mutation and refactoring;
5. deterministic validation, resolution, outcomes, and witnesses;
6. reuse of previous artifacts only when a concrete PETRA requirement needs
   them;
7. Git history, tags, and releases preserve PET history instead of active
   compatibility code.

## 1. Object model

### 1.1 Grammar and roles

The normative grammar is:

```text
PETRA     ::= Leaf | Container
Leaf      ::= 1
Container ::= Product(Term+)
Term      ::= Root ^ PETRA
```

`Container` owns an ordered, non-empty sequence of visible `Term` objects.
`Term` owns exactly one root identity and exactly one exponent relation to a
complete `PETRA` object.  `Leaf` is the terminal PETRA object.  It is not a
container, a term, a root, or an empty product.

When a term's exponent is `Leaf`, its canonical exponent-one relation is
implicit in compact notation.  The relation nevertheless owns a latent slot,
written `^`, at which that `Leaf` can be materialized into depth.  Thus `^`
is a relation target, not a node and not the numeric value one.

An empty container is never a valid PETRA shape.  Any rewrite that removes
the last term from a container replaces that container with `Leaf`; this is the
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

### 1.4 Canonical validation, normalization, and equality

A PETRA shape is canonical when:

- every object conforms to the grammar in section 1.1;
- every container is non-empty;
- every visible term occupies exactly one position in its container;
- root ranks are exactly `r0`, `r1`, ..., in visible order;
- every exponent relation targets one complete PETRA object;
- no prime label, represented integer, allocation identity, or rewrite history
  participates in structural identity.

Canonical normalization assigns root ranks from visible order recursively. It
does not choose primes, calculate values, reorder terms according to numeric
magnitude, or reconstruct a shape from an integer.

Canonical equality is recursive shape equality:

- `Leaf` equals only `Leaf`;
- two containers are equal when their ordered term sequences have equal length
  and corresponding exponent targets are canonically equal;
- root ranks follow from those positions and do not provide persistent identity
  across shape states.

Every public operator invocation receives an already valid canonical shape.
Validation occurs before address parsing or resolution. Implementations must not
silently normalize a malformed or non-canonical input before resolving its
target.

After a successful rewrite, the affected shape is normalized before witnesses
and address effects are finalized. A failed rewrite preserves the exact
`before_shape`.

### 1.5 Canonical textual serialization

The canonical textual serialization is the public, deterministic shape
representation used for display, transport between typed PETRA boundaries,
fixtures, and future CLI input and output.

Its grammar is:

```text
SerializedPETRA     ::= SerializedLeaf | SerializedContainer
SerializedLeaf      ::= "1"
SerializedContainer ::= "C(" SerializedTerm ("," SerializedTerm)* ")"
SerializedTerm      ::= SerializedRoot "^" SerializedPETRA
SerializedRoot      ::= "r" CanonicalIndex
CanonicalIndex      ::= "0" | NonZeroDigit Digit*
Digit               ::= "0" | NonZeroDigit
NonZeroDigit        ::= "1" | "2" | "3" | "4" | "5"
                      | "6" | "7" | "8" | "9"
```

For example:

```text
1
C(r0^1)
C(r0^C(r0^1),r1^1)
C(r0^C(r0^C(r0^1)))
```

The serializer emits exactly:

- ASCII characters;
- lowercase `r`;
- uppercase `C`;
- decimal positional ranks without leading zeroes;
- `^` between each root and its complete exponent target;
- `,` between sibling terms;
- parentheses around every container;
- no whitespace;
- no trailing newline.

The parser may accept ASCII whitespace before, after, or between lexical
tokens. Whitespace is not part of canonical output. Therefore accepted input
such as `C( r0 ^ 1 , r1 ^ 1 )` serializes canonically as
`C(r0^1,r1^1)`.

Only ASCII space, horizontal tab, line feed, carriage return, form feed, and
vertical tab are whitespace. In particular, whitespace is never allowed
inside the single `r`-plus-decimal-digits root token.

#### 1.5.1 Normative resource limits

Canonical text processing uses these fixed limits:

| Resource | Limit |
| --- | ---: |
| Input text length (including permitted whitespace) | 65,536 ASCII characters |
| Nested container depth | 2,048 |
| Total model nodes | 10,001 |
| Terms in one container | 1,024 |
| Decimal digits in one root-rank token | 4 |

A total model node is one `Leaf`, `Container`, or `Term`; `Root` is owned by a
term and is not counted separately. The corresponding runtime primitive is
`petra.node_count(shape)`, admitted under the metrics policy in section 8.
The odd total leaves room for the largest
possible complete PETRA tree under that accounting. The limits are deliberately
fixed and modest: they comfortably cover normal PETRA shapes, permit deep
machine-generated shapes without relying on a Python call stack, and bound
textual allocation and traversal work. The four-digit rank limit matches the
largest canonical rank (`r1023`) allowed by the container-width limit.

The parser checks the input-length limit before scanning and checks every other
limit while scanning, before growing an unbounded container or nesting stack.
Any malformed, truncated, hostile, or over-limit textual input raises
`ShapeSyntaxError("shape-text-malformed")`.

The serializer validates its typed input iteratively and applies the same
depth, total-node, container-width, root-rank-digit, and rendered-text-length
budgets. A typed shape that exceeds one of those budgets raises
`ValueError("shape-serialization-limit-exceeded")`. Other invalid typed
shapes retain the existing validation exception behavior (for example, a
non-canonical rank raises `ValueError`).

The parser constructs the typed PETRA model directly. It must not introduce a
second public shape model or depend on the historical PET runtime.

Parsed root ranks are preserved exactly long enough for canonical validation.
The parser must not repair, normalize, reorder, or renumber them. Thus
`C(r1^1)` is syntactically well formed but fails canonical shape validation;
it is not silently converted to `C(r0^1)`.

Parsing distinguishes textual grammar failure from canonical model validation:

- malformed or incomplete text raises the dedicated PETRA shape syntax error
  with stable reason `shape-text-malformed`;
- a syntactically complete shape that violates canonical model invariants
  raises the existing validation error;
- non-text input is a textual grammar failure.

Serialization first requires a valid canonical typed shape through the existing
validation contract. It must not silently normalize invalid typed input.

The public round-trip laws are:

```text
parse_shape(serialize_shape(shape)) == shape
serialize_shape(parse_shape(text)) == canonical textual form of text
```

The second law normalizes only accepted textual presentation differences such
as whitespace. It does not normalize semantically invalid root ranks or repair
invalid PETRA structures.

This shape serialization is distinct from:

- structural-address serialization;
- operator invocation and result envelopes;
- JSON representation;
- numeric projection;
- persistence schema evolution;
- historical PET formats.

## 2. Positional structural addresses

### 2.1 Syntax

The normative serialized address grammar is:

```text
anchor-address ::= "@/"
term-address   ::= "@/" index ("/" index)*
slot-address   ::= term-address "/^"
index          ::= "0" | nonzero-digit digit*
```

`@/` is a semantic anchor for the top-level PETRA shape.  It is not a node,
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
| SPROUT root anchor | `@/` | semantic root anchor; the current root shape may be a `Container` or `Leaf` |
| nested container | term address | selected term's exponent target, which must be a container |
| leaf term | term address | selected term itself, which must have exponent `Leaf` |
| exponent relation | slot address | selected term's exponent relation; its target is checked by the operator |

For `SPROUT`, `@/` is the semantic root anchor in both default and explicit
mode.  When the root shape is `Leaf`, either mode materializes it as
`C(r0^1)`.  No term address projects a `Leaf` into a container.

### 2.2 Resolution failures and shape-state scope

Every invocation receives a valid canonical PETRA shape. Shape validation
precedes address parsing and resolution. An invalid or non-canonical shape is
outside this operator contract and must not be normalized implicitly: doing so
before resolution could change which object a positional address selects.
Canonical rank normalization occurs only after a successful rewrite. A failed
invocation preserves the exact before-shape.

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
  "schema": "petra.operator-invocation.v1",
  "operator": "SPROUT",
  "target": { "mode": "default" }
}
```

An explicit target is:

```json
{
  "schema": "petra.operator-invocation.v1",
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
schema: "petra.operator-result.v1", status: "ok", operator, invocation_target, resolved_target,
before_shape, after_shape, address_effects, reason: "<op>-applied"
```

For a successful result:

- `operator` is the normalized operator name;
- `invocation_target` is the normalized default or explicit target from the
  invocation, before target selection or resolution;
- `resolved_target` identifies the selected pre-rewrite structural object,
  relation, or semantic root anchor, including its structural kind and
  pre-rewrite address when it has one;
- `address_effects` records the resolved pre-rewrite target and exactly one
  post-rewrite witness address. The witness identifies the appended leaf for
  SPROUT, the surviving parent container or restored collapsed relation for
  SHED, the created terminal leaf for GRAFT, or the restored latent slot for
  PRUNE. It is resolved in the after-shape and is not an assertion that any old
  positional address retained its identity.

The SHED witness distinguishes whether the selected leaf term's parent
container survives or collapses:

- a surviving root parent uses `@/`;
- a surviving nested exponent container uses the address of the owning term
  whose exponent relation targets that container;
- a root parent that collapses to root `Leaf` uses `@/`, through which SPROUT
  can materialize `C(r0^1)`;
- a nested exponent container that collapses to `Leaf` uses the owning term's
  latent slot address (`owner-term-address/^`), through which GRAFT can
  materialize `C(r0^1)`.

A plain owning term address is not a restoration witness after nested collapse:
its exponent target is then `Leaf`, so SPROUT must continue to reject it with
`sprout-target-not-container`.

A failed result has at least the exact serialized schema field shown:

```text
schema: "petra.operator-result.v1", status: "failed", operator, invocation_target, before_shape,
reason: "<stable-reason-id>"
```

It has no `after_shape`, `resolved_target`, or `address_effects`. `operator` is
the normalized operator name, or `null` when envelope validation cannot
normalize one. `invocation_target` is the normalized target object, or `null`
when envelope validation cannot normalize one. An implementation may retain
the raw invocation in an additional diagnostic field, but it must not affect
the stable reason.

The concrete JSON representation is canonical and contains no persistent
identity. A `resolved_target` is exactly an object with `kind` and `address`.
`kind` is one of `anchor`, `term`, or `slot`, and `address` is the canonical
state-scoped PETRA address of that resolved pre-rewrite target.

`address_effects` is exactly an object with `target_address` and
`witness_address`. `target_address` is the canonical address resolved in the
before-shape; `witness_address` is the single canonical post-rewrite witness
address resolved in the after-shape. Neither address is a persistent identity.

Canonical invocation and result serialization uses JSON with object keys sorted
lexicographically, compact separators, no insignificant whitespace, and no
trailing newline. Accepted invocation JSON may contain ordinary JSON
whitespace, but duplicate object keys and non-standard JSON constants are
invalid. These serialization rules do not change the failure precedence,
operator semantics, or state-scoped address rules above.

The following matrix fixes the operator-specific reason after address parsing
and traversal have succeeded:

| Operator | Resolved explicit form or state | Stable reason |
| --- | --- | --- |
| SPROUT | `@/` | accepted |
| SPROUT | term whose exponent target is `Container` | accepted |
| SPROUT | term whose exponent target is `Leaf`, or slot address | `sprout-target-not-container` |
| SHED | term whose exponent target is `Leaf` | accepted |
| SHED | `@/`, slot address, or term whose exponent target is `Container` | `shed-target-not-leaf` |
| GRAFT | slot whose relation targets `Leaf` | accepted |
| GRAFT | `@/` or term address | `graft-target-not-slot` |
| GRAFT | slot whose relation targets `Container` | `graft-slot-already-materialized` |
| PRUNE | eligible terminal-leaf term | accepted |
| PRUNE | `@/`, slot address, or term whose exponent target is `Container` | `prune-target-not-terminal-leaf` |
| PRUNE | leaf term directly in the root container | `prune-target-has-no-parent-relation` |
| PRUNE | nested leaf term in a non-singleton exponent container | `prune-parent-not-singleton-exponent` |

A numeric projection may be an optional, non-normative derived field and must
not participate in resolution or success/failure.

## 4. Structural rewrites

All rewrite rules below take a PETRA shape and the normalized invocation, resolve
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
| Address effect | removed target is destroyed; siblings can be retargeted by rank closure; witness is `@/` for a root parent, the owning term address for a surviving nested parent, or the owning slot address for a collapsed nested parent |

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
tie-breaking, not numeric ordering. PRUNE uses the same definition: the depth
of a terminal leaf is the number of segments in that leaf's term address.

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
| Rewrite | let `leaf_term` be the selected leaf term, `exponent_container = C(leaf_term)` its singleton parent exponent container, and `parent_term` the term whose exponent relation targets `exponent_container`. Destroy `leaf_term`, `exponent_container`, and the relation `parent_term -> exponent_container`; create the replacement relation `parent_term -> Leaf`, which is `parent_term`'s restored latent `^` slot. `parent_term` and its containing and ancestor relations remain. |
| Success reason | `prune-applied` |
| Failure reasons | `invocation-invalid`, generic address reason, `prune-target-not-terminal-leaf`, `prune-parent-not-singleton-exponent`, `prune-target-has-no-parent-relation`, `prune-no-eligible-terminal-leaf` |
| Address effect | the selected terminal term and its singleton exponent container are destroyed; the restored parent `^` slot is returned as a witness; ancestor paths must be re-resolved |

"Terminal" here is deliberately stronger than "leaf": it requires both a
leaf exponent and the singleton exponent-container parent relation.  Therefore
`PRUNE` cannot remove one sibling from a wider exponent container; that is
width removal and belongs to `SHED`.

A terminal leaf term has no materialized descendants: its exponent is `Leaf`.
PRUNE therefore does not destroy descendants of the selected leaf term. It
destroys exactly that term, its singleton exponent container, and their parent
exponent relation, then creates the `parent_term -> Leaf` relation described
above.

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
parent reconstructs the before-shape. The target is `@/` for the root
container, or the address of the owning term for a nested exponent container.
If the deleted term was not final, `SPROUT` has no position argument and
appends instead, so it cannot restore the original order. If SHED collapsed
the root container to `Leaf`, only the root anchor, selected either by default
or explicitly as `@/`, can restore a one-leaf root shape.

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

## 6. Replacement architecture

PETRA replaces the active PET runtime rather than extending it.

The following concepts are obsolete as current runtime foundations:

- the prime-labelled `PET` list-of-tuples representation;
- `PETObject` as a value-derived object model;
- `pet_object_from_int`;
- `prime_label`;
- prime-labelled structural addresses;
- `after_value`;
- `apply_operator_by_value`;
- `NEW`, `DROP`, `INC`, and `DEC`;
- graph, trace, and certificate replay by represented value;
- the existing `pet` CLI and PET-Base JSON contract.

No compatibility bridge, reader, command, test suite, or duplicate runtime is a
PETRA requirement merely because it existed previously.

Temporary coexistence during implementation is permitted only as an internal
migration mechanism. The replacement is complete only when the obsolete
runtime is removed and the active package and CLI are named `petra`.

Historically useful PET behavior remains available through Git history, tag
`v0.3.0`, and published releases.

## 7. Prime-tower projection boundary

A projection may eventually interpret canonical term positions through a
deterministic prime sequence and derive a numeric prime-exponent tower.

Such a projection is not part of the initial PETRA core.

A future projection contract must independently define:

- its domain and codomain;
- whether all PETRA shapes are projectable;
- prime assignment rules;
- handling of values too large to materialize;
- reverse projection, if any;
- error and partiality semantics.

Projection must never:

- determine structural identity;
- influence address resolution;
- choose operator targets;
- alter canonical order;
- make factorization a prerequisite for structural rewrites.

Primality checks, prime generation, and factorization may be introduced only
when that projection contract demonstrates a concrete need.

## 8. Metrics admission policy

No historical PET metric becomes a PETRA metric automatically.

A metric may enter the PETRA runtime only when it:

- is defined directly on canonical PETRA shapes;
- has an explicit domain and result type;
- is independent of represented integers unless declared as a projection
  metric;
- remains well-defined across canonical normalization;
- states whether it observes objects, terms, relations, addresses, rewrites, or
  paths;
- has examples and tests derived from this specification.

Historical PET-Metrics results remain research evidence. They
must not be promoted as PETRA laws or invariants without a new derivation and
admission decision.

### Admitted metrics

`petra.node_count(shape) -> int`

- Defined directly on canonical PETRA shapes.
- Domain: `PetraShape`. Result type: `int`.
- Independent of represented integers.
- Well-defined across canonical normalization.
- Observes objects: one `Leaf`, one `Container`, or one `Term` each
  contributes 1; `Root` is owned by a `Term` and is not counted separately.
- Tests: `tests/test_petra_metrics.py`.

This is the first metric admitted to PETRA under this policy. It supersedes
no historical PET metric.

## 9. Graph, path, trace, and certificate boundary

Graph, path, trace, and certificate facilities are derived layers, not
prerequisites of the structural core.

If introduced, they must operate on:

- canonical PETRA shapes;
- versioned structural invocations;
- positional addresses resolved in each `before_shape`;
- successful result witnesses;
- explicit schema versions.

They must not replay operations by integer value, prime-labelled identity, or
legacy operator labels.

No derived layer is required until a concrete PETRA use case justifies it.

## 10. Implementation dependency order

The canonical implementation order is:

1. immutable PETRA shape model;
2. canonical normalization and equality;
3. positional structural-address parser and resolver;
4. atomic rewrite result and witness model;
5. `SPROUT` and `SHED`;
6. `GRAFT` and `PRUNE`;
7. canonical PETRA serialization;
8. minimal PETRA CLI;
9. optional derived layers justified by concrete requirements;
10. removal of the PET runtime and completion of the package, CLI, and
    repository rename.

Graph, path, trace, certificate, metric, and numeric-projection work is not
automatically mandatory.

## 11. Conformance checklist

A conforming PETRA implementation must:

- implement the grammar and roles in section 1;
- reject empty containers and malformed relations;
- derive root ranks only from current visible position;
- implement canonical validation, normalization, and equality;
- resolve state-scoped positional addresses as specified in section 2;
- preserve the invocation and result semantics in section 3;
- implement all four operators, defaults, failures, and examples in section 4;
- preserve only the partial inverse laws and counterexamples in section 5;
- produce exactly one post-rewrite witness for every successful operator;
- preserve the exact before-shape on failure;
- avoid value-first, factorization-first, and prime-selection rewrite rules;
- avoid permanent compatibility dependencies on the historical PET runtime;
- treat projection and derived analytical layers as separate admissions.

An implementation is not conforming merely because it reproduces historical
PET numeric behavior.
