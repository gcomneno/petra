# Roadmap

This roadmap keeps PET focused on becoming a clearer, more usable, and more credible project.

It is intentionally short.

## Current position

PET currently works best as:

- a small Python CLI
- a reproducible PET artifact and report tooling project
- a PET triage workflow for single-number structural diagnostics
- a policy-first bridge from PET diagnostics to bounded classic verification
- a project for exploring recursive prime-exponent-tree representations of integers
- an emerging rewrite-geometric framework through PET-METICA

It is not yet a polished end-user product.

## Near-term priorities

### 1. Keep the project map clear

Improve first-contact clarity for new visitors and contributors.

Focus areas:

- keep `README.md` as a clean landing page
- keep `docs/` navigable and role-based
- preserve a clear distinction between source-of-truth docs, research notes, reports, and paper material
- keep document paths and cross-links aligned with the actual repository structure

### 2. Keep PET-Base stable and legible

Preserve the credibility of the core representation.

Focus areas:

- keep the formal PET-Base contract stable
- avoid accidental drift between implementation and `docs/reference/SPEC.md`
- keep validation, serialization, and roundtrip behavior easy to inspect
- document user-facing behavior changes precisely

### 3. Improve CLI usability and consistency

Make the command-line experience easier to understand and more stable.

Focus areas:

- keep command behavior predictable
- reduce ambiguity in output and docs
- strengthen help text and examples
- preserve consistency across commands and report tooling

### 4. Keep PET triage and empirical workflows reproducible

Single-number triage, classic handoff policy, scans, summaries, reports, and
datasets should remain easy to regenerate.

Focus areas:

- preserve reproducible commands
- keep PET triage entry points easy to find
- keep report entry points easy to find
- improve the path from raw scan to summary/report
- keep the PET diagnostic vs verified classic divisor boundary explicit
- avoid stale claims in top-level documentation

## Mid-term priorities

### 5. Sharpen the PET-Metrics layer

Continue clarifying which structural observations are merely available and which ones are actually informative.

Focus areas:

- stabilize the most useful metrics
- compare families more systematically
- separate robust recurring patterns from suggestive one-off observations
- keep empirical claims clearly labeled as empirical

### 6. Develop PET-METICA carefully

PET-METICA is now the most promising live research direction beyond PET-Base.

Focus areas:

- keep local rewrite moves well defined
- improve shortest-path / canonical-path tooling
- study asymmetry and rewrite friction more systematically
- identify robust hubs and family-level behavior
- avoid overstating computational observations as proved mathematics

### 7. Consolidate PET/PEG 2.0 operator semantics

PET/PEG 2.0 now has a research-only executable operator semantics layer for
recursive addresses and X/Y/Z operator roles.

Current milestone:

- recursive operator addresses are documented and probeable
- X-axis support topology uses `NEW(parent_address, q)` and `DROP(parent_address, p)`
- Y-axis recursive refinement uses `INC(address)` and `DEC(address)`
- Y-axis hypothetical mutation probes model value-level exponent changes as `k -> k + 1` and `k -> k - 1`
- X/Y commutativity probing compares `X then Y` vs `Y then X` orderings
- Z-axis route dynamics use history-prefix references for `REDIRECT(...)` and `SHADOW_SELECT(...)`
- the foundation snapshot is recorded in `docs/foundations/operator-semantics-snapshot.md`
- full regression after the operator semantics tranche: `620 passed, 1 skipped`

Next questions:

- expand X/Y commutativity and non-commutativity observations
- study address stability across NEW, DROP, INC, and DEC
- connect operator invocations to path-history identity
- evolve synthetic Z-axis route labels into structured PEG edge payloads

### 8. Keep stable vs exploratory boundaries sharp

Continue making it obvious which parts are:

- stable definitions and contracts
- empirical observations
- exploratory hypotheses
- open questions

This helps the project stay credible as it grows.

## Later possibilities

These are possible future directions, not commitments:

- broader PET-METICA experiments at larger ranges
- richer structural visualization
- clearer family atlases and catalogs
- shape algebra and partial-shape extensions
- packaging improvements for easier external use

## What this roadmap is not

This roadmap is not a promise of rapid feature expansion.

The current priority is to improve:

- clarity
- consistency
- reproducibility
- epistemic discipline

before broadening scope.

## Guiding principle

PET should grow by becoming easier to understand, easier to validate, harder to misread, and more explicit about which claims belong to PET-Base, PET-Metrics, PET-METICA, or the broader experimental frontier.
