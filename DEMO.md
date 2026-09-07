# PETRA hands-on demo

This document is a practical introduction to the maintained PETRA runtime and
CLI.

It records two hands-on demonstrations executed against PETRA 0.1.4 during
Phase 10:

1. a complete structural road test using all four canonical operators;
2. a non-trivial experiment using only default target selection.

This document is explanatory and didactic. It does **not** define PETRA
semantics.

The sole normative source is
[`docs/reference/SPEC.md`](docs/reference/SPEC.md). The maintained command-line
contract is documented in
[`docs/reference/CLI.md`](docs/reference/CLI.md).

## What PETRA is doing

PETRA works directly with recursive canonical shapes.

A leaf is written:

```text
1
```

A one-term container is written:

```text
C(r0^1)
```

A deeper shape can look like:

```text
C(r0^C(r0^1),r1^1)
```

The important point is that PETRA operates on this structure directly.

The maintained runtime does not need to start from an integer, factor it,
choose concrete primes, or reconstruct a tree from a numeric value.

The four canonical structural operators are:

| Operator | Practical intuition in these demos |
| --- | --- |
| `SPROUT` | add structural width |
| `SHED` | remove eligible structural width |
| `GRAFT` | materialize structural depth |
| `PRUNE` | collapse eligible structural depth |

These descriptions are only learning aids. The exact operator contracts remain
those in the specification.

## Local setup

From the repository root, a clean local environment can be prepared with:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

The maintained console command is then:

```text
.venv/bin/petra
```

Its interface is:

```text
petra SHAPE_TEXT INVOCATION_JSON
```

For example:

```bash
.venv/bin/petra \
    '1' \
    '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}'
```

A successful invocation emits one canonical JSON result.

Among the useful fields are:

- `before_shape`;
- `after_shape`;
- `resolved_target`;
- `address_effects.target_address`;
- `address_effects.witness_address`;
- `status`;
- `reason`.

## Reading the addresses used below

The demonstrations use canonical positional addresses.

Examples:

| Address | Practical reading in these examples |
| --- | --- |
| `@/` | root anchor |
| `@/0` | first visible term at the root |
| `@/1` | second visible term at the root |
| `@/0/^` | exponent relation slot owned by the first term |
| `@/0/0` | first term inside the first term's materialized exponent |
| `@/0/0/^` | that nested term's exponent relation slot |

Addresses are state-scoped and positional. They are not persistent object IDs
or prime labels.

For the complete address grammar and resolution rules, see the specification.

## Demo 1 — complete structural road test

### Question

Can the maintained PETRA CLI:

- construct non-trivial recursive structure;
- exercise all four canonical operators;
- use both explicit and default targets;
- expose deterministic witnesses;
- return exactly to the initial shape;
- reject an invalid rewrite without mutating its input?

### Observed round trip

The demonstration started from the canonical leaf:

```text
1
```

The observed sequence was:

```text
1
→ C(r0^1)
→ C(r0^1,r1^1)
→ C(r0^C(r0^1),r1^1)
→ C(r0^C(r0^C(r0^1)),r1^1)
→ C(r0^C(r0^1),r1^1)
→ C(r0^C(r0^1))
→ C(r0^1)
→ 1
```

### Step 1 — SPROUT

```text
before  = 1
target  = @/
after   = C(r0^1)
witness = @/0
```

A new canonical leaf term appeared at the root.

### Step 2 — SPROUT

```text
before  = C(r0^1)
target  = @/
after   = C(r0^1,r1^1)
witness = @/1
```

The shape grew in width again.

### Step 3 — explicit GRAFT

Invocation target:

```text
@/0/^
```

Observed result:

```text
before  = C(r0^1,r1^1)
target  = @/0/^
after   = C(r0^C(r0^1),r1^1)
witness = @/0/0
```

The latent exponent relation became a materialized nested container.

### Step 4 — another explicit GRAFT

```text
before  = C(r0^C(r0^1),r1^1)
target  = @/0/0/^
after   = C(r0^C(r0^C(r0^1)),r1^1)
witness = @/0/0/0
```

The same branch gained another level of depth.

### Step 5 — default PRUNE

```text
target  = @/0/0/0
witness = @/0/0/^
```

The deepest materialized singleton depth was collapsed.

### Step 6 — default SHED

```text
target  = @/1
after   = C(r0^C(r0^1))
witness = @/
```

The eligible top-level leaf term was removed.

### Step 7 — default PRUNE

```text
target  = @/0/0
after   = C(r0^1)
witness = @/0/^
```

The remaining nested depth was collapsed.

### Step 8 — default SHED

```text
target  = @/0
after   = 1
witness = @/
```

Removing the final eligible term restored the canonical leaf.

The complete structural round trip therefore ended at exactly the same shape
from which it started:

```text
1
```

## Failure behavior

The road test also deliberately requested:

```text
shape   = C(r0^1)
request = GRAFT @/
```

The root anchor is not a valid `GRAFT` slot.

Observed result:

```text
exit   = 1
status = failed
reason = graft-target-not-slot
before = C(r0^1)
```

The important practical observation is that PETRA returned a structured
failure and preserved the original `before_shape`.

No speculative repair or mutation occurred.

## Demo 2 — default-target selection on a non-trivial shape

The second demonstration removed explicit target choice from the experiment.

Every invocation used:

```json
{"mode":"default"}
```

### Question

Can PETRA navigate a shape containing several possible structural locations
using only its canonical default-target rules, behave deterministically at
structural boundaries, and restore the exact initial shape?

### Initial shape

```text
C(r0^C(r0^1,r1^C(r0^1)),r1^C(r0^C(r0^1),r1^1),r2^1)
```

This shape deliberately contains:

- multiple top-level terms;
- several nested containers;
- several latent exponent slots;
- different depths;
- more than one plausible place a human might initially look at.

That makes default target selection visible rather than trivial.

## Phase A — repeated default GRAFT

The first three invocations were all simply:

```text
GRAFT [default]
```

PETRA selected:

```text
01 target = @/1/0/0/^
02 target = @/1/0/0/0/^
03 target = @/1/0/0/0/0/^
```

The corresponding witnesses were:

```text
01 witness = @/1/0/0/0
02 witness = @/1/0/0/0/0
03 witness = @/1/0/0/0/0/0
```

The deepest observed shape became:

```text
C(r0^C(r0^1,r1^C(r0^1)),r1^C(r0^C(r0^C(r0^C(r0^C(r0^1)))),r1^1),r2^1)
```

### What we learned

Repeated default `GRAFT` did not jump among unrelated branches.

Under the current canonical rule, it repeatedly extended one deterministic
deepest branch.

This is deterministic target selection, not a claim of autonomous
decision-making.

## Phase B — repeated default PRUNE

Three default `PRUNE` operations then selected:

```text
04 target = @/1/0/0/0/0/0
05 target = @/1/0/0/0/0
06 target = @/1/0/0/0
```

Their witnesses moved back to the corresponding latent relation slots:

```text
04 witness = @/1/0/0/0/0/^
05 witness = @/1/0/0/0/^
06 witness = @/1/0/0/^
```

After those three operations, PETRA had restored the exact initial shape.

### What we learned

For the depth created by the preceding `GRAFT` sequence, default `PRUNE`
retraced the newly materialized chain in reverse.

The experiment therefore exposed a clear local inverse pattern:

```text
GRAFT
GRAFT
GRAFT
↓
PRUNE
PRUNE
PRUNE
```

This observation applies to the demonstrated legal states. The specification,
not this document, defines the general operator laws.

## Phase C — root width round trip

Default `SPROUT` selected:

```text
target  = @/
witness = @/3
```

and changed the root from three terms to four.

The following default `SHED` selected:

```text
target  = @/3
witness = @/
```

and restored the original three-term shape exactly.

In this state, the added rightmost leaf term was therefore the next eligible
default `SHED` target.

## Phase D — reaching a structural boundary

A further default `SHED` selected:

```text
target = @/2
```

This removed the last top-level leaf term, leaving:

```text
C(r0^C(r0^1,r1^C(r0^1)),r1^C(r0^C(r0^1),r1^1))
```

At that point both remaining top-level terms had materialized exponent
containers.

Another default `SHED` produced:

```text
exit   = 1
status = failed
reason = shed-no-eligible-top-level-leaf
```

The shape remained unchanged.

### What we learned

Default target selection does not mean "always find something to do."

When the operator has no eligible target under its canonical rule, PETRA stops
with a stable failed result instead of inventing a rewrite.

## Phase E — exact restoration

One final default `SPROUT` selected the root:

```text
target  = @/
witness = @/2
```

and reconstructed:

```text
C(r0^C(r0^1,r1^C(r0^1)),r1^C(r0^C(r0^1),r1^1),r2^1)
```

This is byte-for-byte the canonical textual shape with which the second
demonstration started.

## The practical mental model

The two demonstrations suggest a useful way to think about PETRA while
learning it:

```text
canonical shape
    ↓
positional target
    ↓
structural rewrite
    ↓
canonical after-shape
    +
resolved target
    +
witness
```

The shape is primary.

Addresses tell us where a rewrite applies in the current structural state.

The result tells us both what the structure became and which structural
location witnesses the effect.

A failed rewrite remains a first-class result rather than an exceptional
mutation path.

## What these demonstrations establish

They directly observed that the maintained implementation can:

- parse and operate on canonical recursive shapes;
- execute `SPROUT`, `SHED`, `GRAFT`, and `PRUNE`;
- resolve explicit positional targets;
- select canonical default targets;
- expose resolved-target and witness addresses;
- construct and collapse nested structure;
- perform exact demonstrated structural round trips;
- reject ineligible operations with stable failure reasons;
- preserve `before_shape` when those demonstrated rewrites fail.

## What these demonstrations do not establish

They do **not** establish:

- numeric or prime projection semantics;
- integer factorization behavior;
- historical PET compatibility;
- general algebraic inverse theorems beyond the demonstrated cases;
- performance or scalability characteristics;
- graph, path, metric, trace, or certificate semantics;
- any semantics not already defined by the canonical specification.

## Where to go next

For exact semantics:

- [`docs/reference/SPEC.md`](docs/reference/SPEC.md)

For the maintained CLI contract:

- [`docs/reference/CLI.md`](docs/reference/CLI.md)

For project status:

- [`docs/reports/STATUS.md`](docs/reports/STATUS.md)

For the implementation roadmap:

- [`ROADMAP.md`](ROADMAP.md)

The shortest useful first experiment remains:

```bash
.venv/bin/petra \
    '1' \
    '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}'
```

From there, the useful question is no longer "what integer does this
represent?"

It is:

> What structural state do I have, where can this operator legally act, and
> what canonical shape does that rewrite produce?
