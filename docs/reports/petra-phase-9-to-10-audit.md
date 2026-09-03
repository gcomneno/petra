# PETRA Phase 9 → Phase 10 Audit

## Status

Issue: #224

Audit branch: `audit/issue-224-phase-9-to-10`

Foundation: `9422fddc7089776c6d71e2bce66ae1158890363a`

Foundation commit: `feat(petra): add minimal canonical CLI (#223)`

Audit mode: read-only repository audit before any Phase 9 implementation or Phase 10 removal.

Canonical authority:

- `AGENTS.md` — operational working contract;
- `docs/reference/SPEC.md` — sole normative PETRA semantic specification;
- `ROADMAP.md` — implementation-order authority.

## Boundary

The sparse-image research workstream was explicitly excluded from this audit.

The audit did not use as evidence:

- #205 — shape-first sparse image artifacts;
- #208 — Gate 2 sparse-artifact comparison;
- #213 — Gate 3 sparse-artifact adversarial pressure test;
- draft PR #206.

PETRA VISION and other noncanonical research were not promoted into PETRA requirements.

## Final verdict

`PHASE_10_READY`

Final transition statement:

`GO: PHASE 10 MAY BEGIN`

No Phase 9 candidate derived layer is required before Phase 10.

## Executive finding

The canonical PETRA runtime is already independent from the historical PET runtime and contains the required shape-first core, addresses, rewrite results and witnesses, four canonical operators, serialization, and minimal PETRA CLI.

The current specification does not require graphs, paths, traces/certificates, PETRA-native metrics, numeric prime-tower projection, or research probes before replacement.

The remaining historical PET surface is extensive, but its existence is migration work rather than evidence for a PETRA-derived-layer requirement.

Packaging, documentation, CI, stale-reference checks, and distribution metadata still expose mixed PET/PETRA state. These are Phase 10 retarget/removal concerns.

## Phase 9 matrix

| Candidate layer | Normative requirement found | Current implementation | Legacy/research pressure | Classification | Blocking reason |
| --- | --- | --- | --- | --- | --- |
| graphs / neighborhood traversal | No. Canonical PETRA does not require a graph layer before replacement. | Only historical PET graph functionality is present. | Legacy graph tests/tools and research usage. | `HISTORICAL_ONLY` | None |
| paths | No unresolved canonical path abstraction. Positional structural addresses already provide canonical targeting. | PETRA `Address`; historical PET graph-path abstractions remain legacy. | Historical graph routes/paths. | `OPTIONAL_DEFER` | None |
| traces / certificates | No. Canonical result/witness serialization already satisfies current operator outcome and audit needs. | PETRA `SuccessfulResult`, `FailedResult`, `AddressEffects`, serialized results; historical PET trace runtime remains separate. | Historical PET trace/certificate replay. | `HISTORICAL_ONLY` | None |
| PETRA-native metrics | No current specification or product requirement. | No canonical PETRA metrics layer. | PET-Metrics and historical metric tests/docs. | `HISTORICAL_ONLY` | None |
| prime-tower projection | No. Numeric projection is explicitly optional and future-derived. | No canonical PETRA numeric projection. | Historical encode/decode/factorization continuity pressure. | `OPTIONAL_DEFER` | None |
| research probes | No canonical runtime requirement. | Research tooling exists separately. | Active research workstreams. | `RESEARCH_ONLY` | None |

## Canonical PETRA completeness

The post-Phase-8 `src/petra` surface is autonomous and includes:

- immutable shape model: `Leaf`, `Root`, `Term`, `Container`;
- structural equality and hashing;
- canonical validation and normalization;
- positional structural addresses and deterministic resolution failures;
- immutable invocation/result/witness model;
- `SPROUT`;
- `SHED`;
- `GRAFT`;
- `PRUNE`;
- canonical shape serialization;
- invocation JSON parsing/serialization;
- result JSON serialization and stable failure reasons;
- minimal `petra` CLI;
- PETRA-only public package exports.

## PETRA → PET dependency audit

`NONE`

The canonical `src/petra` package imports only Python standard-library modules and sibling `petra` modules.

No canonical PETRA operator, serialization boundary, package export, or CLI requires `src/pet`.

## Phase 8 CLI verdict

`PASS`

The minimal CLI exposes PETRA shape + invocation JSON processing and canonical PETRA result JSON without depending on historical PET semantics.

A direct smoke observation confirmed canonical `SPROUT` execution and rejection of historical `NEW` as `invocation-invalid`.

The audit environment did not provide `pytest`; this did not create a transition blocker because Phase 8 had already been merged through its own implementation/review gate. No feature was reopened by this audit.

## Legacy dependency inventory

Static audit observations:

- `src/pet`: 20 files — Phase 10 removal surface;
- `src/petra`: 7 files — canonical PETRA runtime;
- tests: 114 files total;
- PETRA-focused tests: 10;
- 83 test files mention/import/invoke historical PET surfaces;
- 23 tests directly import PET runtime modules;
- 46 tests exercise PET CLI-oriented behavior;
- 35 `test_tools_pet*.py` files are predominantly historical/research tooling coverage;
- tools: 127 files total;
- `tools/research`: 64;
- `tools/core`: 10;
- `tools/classic`: 4;
- `tools/legacy`: 5;
- remaining root wrappers/helpers: 44.

These counts describe migration volume. They do not create Phase 9 requirements.

## Phase 10 work inventory

### DELETE

- `src/pet/**` after dependent active surfaces are retired/retargeted;
- historical PET runtime tests;
- PET graph/path/trace/metrics/projection tests that no longer represent current behavior;
- obsolete `pet` command surface;
- compatibility wrappers retained solely for the historical architecture.

### RETARGET

- `pyproject.toml` distribution identity and description;
- console-script exposure so the maintained command is only `petra`;
- package discovery assumptions;
- CI test selection after historical PET removal;
- stale-source/docs checks currently centered on `src/pet`;
- README current-state presentation;
- `docs/reports/STATUS.md`;
- active CLI/package documentation.

### KEEP_GENERIC

- build backend;
- license/classifiers/Python-version metadata where semantically neutral;
- generic GitHub Actions skeleton;
- generic documentation navigation already pointing at canonical PETRA sources;
- `src/petra/**`;
- PETRA tests.

### DECISION_REQUIRED DURING PHASE 10

- whether historical/research tools remain in-tree as clearly separated research/archive material or move elsewhere;
- whether `docs/reference/CLI.md` is retained as explicitly historical material or replaced by a maintained PETRA CLI reference.

These decisions do not block the start of Phase 10.

## Pre-Phase-10 blockers

`NONE`

## Specification / roadmap consistency

Audit classification:

`FAIL` for the complete repository presentation, but not for canonical authority.

`docs/reference/SPEC.md` and `ROADMAP.md` are mutually consistent.

The inconsistency is in stale active surfaces such as packaging, README/status material, and CLI documentation that still expose historical PET or mixed PET/PETRA state.

Those inconsistencies are Phase 10 cleanup work, not evidence that a Phase 9 derived layer is required.

## Research boundary conclusion

- sparse-image research was not analyzed;
- PETRA VISION was not promoted;
- research evidence was not used to manufacture a Phase 9 requirement;
- active research may continue independently of canonical replacement work unless separately promoted by an explicit decision.

## Transition decision

Phase 10 may begin because:

1. no Phase 9 derived layer is required by the canonical specification or current PETRA product/runtime surface;
2. `src/petra` has no dependency on `src/pet`;
3. the minimal PETRA CLI is present;
4. the remaining mixed repository state is primarily deletion, retargeting, packaging, documentation, CI and release work expressly belonging to Phase 10.

## Recommended first Phase 10 slice

Start with a narrow distribution-boundary transition rather than deleting all of `src/pet` at once:

1. remove the legacy `pet` console-script exposure;
2. make package/distribution metadata PETRA-primary;
3. retarget active CLI/package documentation and stale-reference checks;
4. retarget CI sufficiently to validate the PETRA distribution boundary;
5. preserve physical `src/pet/**` deletion for a subsequent Phase 10 slice after the distribution boundary is clean.

This first slice should prove that PETRA can be installed and invoked as the sole maintained product interface before performing the broader historical runtime deletion.

## Non-claims

This audit does not claim that:

- Phase 9 derived layers will never be useful;
- historical PET functionality must be recreated in PETRA;
- research workstreams are complete or obsolete;
- all Phase 10 work can safely be done in one change;
- physical deletion of `src/pet/**` has already been authorized beyond the ordered Phase 10 process.
