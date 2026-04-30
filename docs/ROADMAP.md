# PET Roadmap

This roadmap describes the next development directions after `v0.1.0`.

It is intentionally conservative: PET distinguishes stable implementation work,
bounded empirical work, and exploratory research.

## PET-METICA v0.2.0 focus

PET-METICA v0.2.0 should complete the toolkit as a bounded,
research-facing layer for analyzing structural change.

The main conceptual distinction for this milestone is between
quantitative delta and structural delta.

- Quantitative delta measures how much a numeric value changes.
- Structural delta measures how the recursive PET anatomy changes across
  prime-exponent branches.

This distinction keeps PET-METICA focused on what it can safely observe:
not only how much a value changes, but where and how its structure changes.

Two values may be numerically close while being structurally distant,
because nearby integers can have very different prime-exponent anatomies.
Conversely, a larger numeric change may still be structurally simple when
it corresponds to a small number of PET-core branch operations.

PET-METICA does not directly model business domains. It models recursive
structures of measures. When those structures are projected onto a domain
model, PET-METICA can describe systems where observed values are not only
numeric quantities, but recursively analyzable structural states.

This supports future bounded experiments such as event-system or IoT-style
analysis, where stable event dimensions may be encoded as prime axes and
observed counts or severities may be represented as exponent vectors.

This is a non-core projection layer: it must not claim that PET-METICA
solves factorization, primality, or domain modeling by itself.

## Current release

### `v0.1.0`

Status: released.

Included:

- PET-Base canonical representation and CLI contracts
- PET-Metrics canonical and extended metric layers
- PET-METICA operational rewrite toolkit
- bounded PET-METICA reports and canonical demo
- claim hygiene separating stable, bounded, exploratory, and non-core material

## Next milestone: `v0.2.0`

Theme: make PET-METICA more useful as an operational research-facing toolkit.

Status: PET-METICA is now complete as a bounded operational/research-facing
layer. The remaining items below are v0.2.x enhancements, not blockers for
operational completeness.

Completed operational layer:

- rewrite distance
- rewrite path explanation
- `structural_delta` summary in `pet rewrite explain`
- rewrite friction reports
- bounded rewrite scans
- bounded rewrite matrices
- canonical bounded demo report
- claim-safe ROADMAP, CLI, STATUS, and report documentation

Enhancement candidates:

1. Add dedicated PET-METICA hub reporting

   Possible command:

       pet rewrite hubs --n-max 30 --overscan 90 --limit 10

   Goal:

   - expose hub scores without requiring a full scan dump
   - support bounded hub reports
   - keep all claims tied to explicit scan parameters

2. Add dedicated PET-METICA asymmetry reporting

   Possible command:

       pet rewrite asymmetry --n-max 30 --overscan 90 --limit 10

   Goal:

   - expose directional rewrite cost differences
   - highlight pairs where `cost(a,b) != cost(b,a)`
   - support bounded asymmetry reports

3. Continue improving `pet rewrite explain`

   Completed:

   - `structural_delta` summary
   - removed primes
   - introduced primes
   - strengthened branches
   - weakened branches
   - human and JSON output

   Future optional additions:

   - support summary before/after

   Goal:

   - keep rewrite explanations useful as a structural debugger
   - keep the output readable and deterministic

4. Improve PET-METICA reports

   Candidate reports:

   - larger bounded rewrite report
   - hub-focused report
   - asymmetry-focused report
   - friction-focused report

   All reports must include:

   - exact command
   - bounded scope
   - non-claims
   - reproducible input assumptions

5. Keep claim hygiene strict

   Rules:

   - bounded observations remain bounded
   - repeated empirical patterns are not theorems
   - non-core compositional/operator ideas stay explicitly non-core
   - PET-Base must remain stable and untouched by PET-METICA experiments

## Later milestone: `v0.3.0`

Theme: shape-level consolidation.

Candidate work:

- clarify shape-level PET-METICA APIs
- separate number-level and shape-level reports
- decide which shape-algebra helpers deserve stable CLI exposure
- archive or demote stale experiments
- expand bounded scan/report infrastructure

## Explicit non-goals for now

The following are not immediate goals:

- proving global asymptotic claims
- promoting non-core compositional operators
- changing PET-Base semantics
- treating bounded PET-METICA findings as general theorems
- mixing cleanup/refactor work with new research claims
