# PET canonical workflow

> [!IMPORTANT]
> **Phase 10 historical notice.** The `pet scan` and `pet query` commands
> described in this document no longer exist. The scan/query subsystem was
> removed in Phase 10 as part of the historical PET runtime deletion.
> Reproduction commands involving `pet scan` or `python3 -m src.pet.cli scan`
> are retained for provenance only and no longer work. Use the maintained
> Resolver at `resolver/` for shape and distance analysis over bounded
> integer ranges.

## Scope

This document defines the current canonical workflows for PET as a bounded,
reproducible structural laboratory for integers.

It does not define PET semantics, proof status, or future theory. Those belong
respectively to:

- `docs/reference/SPEC.md`
- `docs/reports/STATUS.md`
- research notes under `docs/research/`

## Purpose

The canonical workflow exists to ensure that PET results are produced,
summarized, and interpreted through stable, explicit pipelines rather than
through scattered ad-hoc exploration.

There are currently three canonical workflow families:

1. Structural factorization CLI workflow for stable single-number PET routes.
2. PET triage workflow for deeper operator-side structural diagnostics and
   bounded classic handoff.
3. Bounded report workflow for scan-backed reports, atlas summaries, and
   generated research artifacts.

## Canonical workflow A: structural factorization CLI

The public first-class CLI entry point is:

    pet structural-factorization N

This command emits a stable summary of the PET structural route:

- `status`
- `residual_reduction_chain`
- `terminal_residual`
- an explicit PET/classic boundary claim

Use `--pest-json PATH` to write an optional `pet.syntax_tree.v0`
explanatory artifact.

Structural factorization decomposes the PET-visible shape route; classic
verification confirms the arithmetic factors.

## Canonical workflow B: PET triage

The current operator-side triage flow is policy-first:

    PET race diagnostic
      -> PET classic handoff policy
      -> PET-approved classic probe route
      -> verified classic scan summary / policy
      -> non-fatal legacy diagnostics

### B1. Run the PET triage pipeline

Canonical implementation:

- `tools/core/pet_triage_pipeline.sh`

Compatibility entry points:

- `tools/pet_triage_pipeline.sh`
- `tools/peelator.sh`

Command pattern:

    tools/pet_triage_pipeline.sh N

The pipeline starts with the PET race diagnostic and classic handoff policy.
Legacy diagnostics are retained as non-fatal secondary output and must not
override the PET race diagnostic or handoff policy.

### B2. Run the PET race diagnostic directly

Canonical implementation:

- `tools/core/pet_local_probe_proposal.py`

Compatibility wrapper:

- `tools/pet_local_probe_proposal.py`

Command pattern:

    tools/pet_local_probe_proposal.py N --operator-depth auto --backbone-selection race

This report identifies:

- selected backbone order
- race selection quality
- PET shape diagnostic
- selected operator sequence
- final PET diagnostic summary

The proposal does not factor `N`.

### A3. Run PET classic handoff policy directly

Canonical implementation:

- `tools/core/pet_classic_handoff_route.py`

Compatibility wrapper:

- `tools/pet_classic_handoff_route.py`

Command pattern:

    tools/pet_classic_handoff_route.py N

This step maps PET shape diagnostics to bounded classic probe policies.

Current implemented policies:

- `atomic-exact` -> `primality-check-only`
- `narrow-deep` -> `power-like-local-check`
- `wide-exact` -> `backbone-wide-structural-check`
- `near-shape` -> `operator-neighborhood-check`

Current intentionally unavailable policy:

- `complex-border` -> `complex-border-route-needed`

A route is available only when the PET-approved policy is implemented. The old
NEW/DROP lens fallback is not the decision engine of the current handoff route.

### A4. Summarize verified classic divisors

Canonical implementations:

- `tools/classic/pet_classic_scan_summary.py`
- `tools/classic/pet_classic_scan_policy.py`

Compatibility wrappers:

- `tools/pet_classic_scan_summary.py`
- `tools/pet_classic_scan_policy.py`

Command pattern:

    tools/pet_classic_scan_summary.py N
    tools/pet_classic_scan_policy.py N

Classic stages may verify arithmetic divisors, but they must clearly distinguish
verified divisors from PET-only diagnostics.

## Canonical workflow B: bounded reports

This workflow is for reproducible bounded reports and generated artifacts.

### B1. Produce a bounded scan dataset

Primary artifact:

- `docs/reports/data/scan-<start>-<end>.jsonl`

Command pattern:

    python3 -m src.pet.cli scan <start> <end> --jsonl docs/reports/data/scan-<start>-<end>.jsonl

This dataset is the base empirical artifact for downstream reporting.

### B2. Produce an atlas-style summary from the scan dataset

Canonical implementation:

- `tools/research/atlas_summary.py`

Compatibility wrapper:

- `tools/atlas_summary.py`

Derived artifact:

- `docs/reports/data/atlas-summary-<start>-<end>.txt`

Command pattern:

    python3 tools/atlas_summary.py docs/reports/data/scan-<start>-<end>.jsonl > docs/reports/data/atlas-summary-<start>-<end>.txt

This step converts the raw bounded scan into a compact structural summary.

### B3. Publish a bounded report tied to explicit inputs

Primary artifacts:

- `docs/reports/generated/atlas-<start>-<end>.md`
- other bounded report documents under `docs/reports/generated/`

A report is canonical only if it states:

- its bounded range
- the input dataset it depends on
- the command path used to reproduce it
- whether it is descriptive, comparative, or classificatory

### B4. Derive higher-level bounded artifacts from explicit datasets

Current bounded artifact families include:

- atlas reports
- signature catalogs
- family benchmarks
- metrics baselines

These artifacts must stay tied to explicit bounded inputs and must not be
presented as general theory by default.

### B4a. Metrics baseline workflow

Canonical path:

- generate a bounded scan dataset
- publish a descriptive metrics report tied to that dataset

Current example:

- dataset: `docs/reports/data/scan-2-10000.jsonl`
- report: `docs/reports/generated/metrics-2-10000.md`

Command:

    python3 -m src.pet.cli scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl

The metrics baseline is currently scan-backed rather than driven by a separate
stable summary script.

### B4b. Family benchmark workflow

Primary helper:

- `pet families benchmark-disjoint`

Current example:

- report: `docs/reports/generated/families-benchmark-disjoint.md`

Command:

    pet families benchmark-disjoint

This workflow is currently CLI-output-backed: the report is derived from the
family benchmark command output rather than from a committed scan dataset.

## Stable filenames and expected outputs

### Scan step

Command pattern:

    python3 -m src.pet.cli scan <start> <end> --jsonl docs/reports/data/scan-<start>-<end>.jsonl

Expected output:

- local generated JSONL dataset at `docs/reports/data/scan-<start>-<end>.jsonl`

Artifact status:

- operator-side artifact
- not expected to be present in a fresh clone
- regenerated via the documented command pattern

Stable filename pattern:

- `scan-<start>-<end>.jsonl`

### Atlas summary step

Command pattern:

    python3 tools/atlas_summary.py docs/reports/data/scan-<start>-<end>.jsonl > docs/reports/data/atlas-summary-<start>-<end>.txt

Expected output:

- local derived summary text at `docs/reports/data/atlas-summary-<start>-<end>.txt`

Artifact status:

- operator-side derived artifact
- not expected to be present in a fresh clone
- regenerated from the corresponding scan dataset

Stable filename pattern:

- `atlas-summary-<start>-<end>.txt`

### Atlas report step

Expected output:

- committed report at `docs/reports/generated/atlas-<start>-<end>.md`

Stable filename pattern:

- `atlas-<start>-<end>.md`

### Metrics baseline step

Current canonical example:

- dataset: `docs/reports/data/scan-2-10000.jsonl`
- report: `docs/reports/generated/metrics-2-10000.md`

Expected output:

- committed bounded metrics report

Current stable filename:

- `metrics-2-10000.md`

### Family benchmark step

Command pattern:

    pet families benchmark-disjoint

Expected output:

- stdout from the family benchmark command, to be used when preparing
  `docs/reports/generated/families-benchmark-disjoint.md`

Current stable report filename:

- `families-benchmark-disjoint.md`

## Statement classification

Interpretation must follow `docs/reports/process/observation-pipeline.md`.

In practice:

- raw bounded facts belong in reports
- repeated bounded regularities may be called bounded empirical patterns
- beyond-range claims must be marked as conjectures
- proved or definitional statements belong to established status

## Current canonical artifacts

Stable entry points currently recognized by the repository:

- `docs/reference/SPEC.md`
- `docs/reports/STATUS.md`
- `docs/reports/generated/metrics-2-10000.md`
- `docs/reports/generated/atlas-2-100000.md`
- `docs/reports/generated/atlas-2-1000000.md`
- `docs/reports/generated/signatures-catalog-2-1000000.md`
- `docs/reports/generated/families-benchmark-disjoint.md`
- `docs/reports/process/observation-pipeline.md`
- `docs/reports/process/tooling-classification.md`

## Current stable vs non-canonical boundary

Canonical workflow does **not** mean every script in `tools/` is stable.

At the current stage, the canonical operator-side path is centered on:

- PET race diagnostic
- PET classic handoff policy
- bounded classic verification only when explicitly authorized
- non-fatal legacy diagnostics

The canonical report path is centered on:

- bounded scan generation
- atlas-style summarization
- bounded report publication
- explicit statement classification

Exploratory scripts may still be useful, but they are not automatically part of
the canonical workflow unless a report or stable document explicitly relies on
them.

## Usage rule

When adding a new PET report or operator workflow, prefer extending one of the
existing canonical workflows instead of inventing a parallel undocumented flow.

If a result cannot be reproduced from explicit bounded inputs with a clear
command path, it should not be treated as a canonical PET lab artifact.
