# PETRA VISION experiment plan

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Phase 0 — Foundation

- Freeze the confidential invention disclosure.
- Define supported PETRA shape boundaries.
- Define terminology without committing to visual aesthetics.
- Establish negative examples and forbidden shortcuts.

Exit criterion:

The technical contract is precise enough that independent prototype
implementations could be compared objectively.

## Phase 1 — Minimal geometric grammar

Support only:

- `Leaf`;
- one ordered container node;
- bounded child counts;
- shallow depth.

Phase 1 defines and implements a bounded canonical nested-frame layout for
this proof domain: its coordinate system, orientation, placement, spacing,
and normalization rules preserve type, order, containment, and recursive
identity.

Exit criterion:

Exact roundtrip for an exhaustive bounded shape corpus.

## Phase 2 — Canonical layout

Generalize, formalize, or extend layout rules beyond the bounded Phase 1 proof
grammar, including:

- coordinate system;
- orientation;
- scale rules;
- spacing rules;
- canonical child placement;
- symmetry-breaking rules;
- geometric normalisation.

Exit criterion:

Structurally equal shapes produce identical canonical geometry and
distinct shapes remain distinguishable.

## Phase 3 — Native decoder

Formally harden, provide independent evidence for, or extend the canonical
geometry-only decoder already included in the bounded Phase 1 feasibility
prototype.

The decoder must not receive hidden PETRA serialisation, integer
values, node IDs, or external ordering metadata.

Exit criterion:

Exhaustive bounded encode/decode proof plus adversarial malformed
geometry tests.

## Phase 4 — Recursive scaling

Extend the grammar to deep and wide structures.

Measure:

- geometric growth;
- coordinate precision;
- collision risk;
- locality of change;
- repeated-subshape handling;
- rendering complexity.

Exit criterion:

Defined complexity bounds and successful roundtrip beyond ordinary
Python recursive equality limits.

## Phase 5 — Observation pipeline

Introduce vector rendering first, followed by controlled rasterisation.

Test:

- translation;
- uniform scaling;
- rotation where authorised;
- antialiasing;
- quantisation;
- limited noise;
- partial occlusion.

Exit criterion:

Explicit separation between canonical decoding and observational
recovery.

## Phase 6 — Multiscale semantics

Define which structural facts are visible at each scale.

Exit criterion:

Every scale transition corresponds to a documented PETRA structural
boundary and remains deterministic.

## Phase 7 — Authenticated completion

Explore intentionally incomplete geometries whose missing region is
completed from an authenticated external share.

Use established cryptographic components only.

Exit criterion:

A threat model, explicit trust boundary, and proof that geometric
incompleteness alone is not being misrepresented as encryption.

## Measurements

Every prototype must record:

- source shape;
- canonical geometry;
- decoded shape;
- exact roundtrip result;
- primitive count;
- bounding dimensions;
- maximum coordinate precision;
- local mutation distance;
- rendering and decoding time;
- rejection behaviour for malformed inputs.

## Stop conditions

Reconsider the design if:

- inverse decoding requires hidden serialized data;
- distinct shapes collide after canonical normalisation;
- geometry grows without a usable bound;
- canonicality depends on arbitrary renderer behaviour;
- multiscale levels do not correspond to native structure;
- the proposed method reduces to an ordinary labelled tree diagram.
