# PET Roadmap

This roadmap describes the next development directions after `v0.1.0`.

It is intentionally conservative: PET distinguishes stable implementation work,
bounded empirical work, and exploratory research.

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

Candidate work:

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

3. Improve `pet rewrite explain`

   Candidate additions:

   - support summary before/after
   - removed primes
   - introduced primes
   - strengthened branches
   - weakened branches

   Goal:

   - make rewrite explanations more useful as a structural debugger
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
