# PET canonical workflow

## Scope

This document defines the current canonical workflow for PET as a bounded,
reproducible structural laboratory for integers.

It does not define PET semantics, proof status, or future theory.
Those belong respectively to `docs/SPEC.md`, `docs/STATUS.md`, and research notes.

## Purpose

The canonical workflow exists to ensure that PET results are produced,
summarized, and interpreted through a stable, explicit pipeline rather than
through scattered ad-hoc exploration.

## Canonical pipeline

### 1. Produce a bounded scan dataset

Primary artifact:
- `docs/reports/data/scan-<start>-<end>.jsonl`

Command pattern:

    python3 -m src.pet.cli scan <start> <end> --jsonl docs/reports/data/scan-<start>-<end>.jsonl

This dataset is the base empirical artifact for downstream reporting.

### 2. Produce an atlas-style summary from the scan dataset

Primary helper:
- `tools/atlas_summary.py`

Derived artifact:
- `docs/reports/data/atlas-summary-<start>-<end>.txt`

Command pattern:

    python3 tools/atlas_summary.py docs/reports/data/scan-<start>-<end>.jsonl > docs/reports/data/atlas-summary-<start>-<end>.txt

This step converts the raw bounded scan into a compact structural summary.

### 3. Publish a bounded report tied to explicit inputs

Primary artifacts:
- `docs/reports/atlas-<start>-<end>.md`
- other bounded report documents under `docs/reports/`

A report is canonical only if it states:
- its bounded range
- the input dataset it depends on
- the command path used to reproduce it
- whether it is descriptive, comparative, or classificatory

### 4. Derive higher-level bounded artifacts from explicit datasets

Current bounded artifact families include:
- atlas reports
- signature catalogs
- family benchmarks
- metrics baselines

These artifacts must stay tied to explicit bounded inputs and must not be
presented as general theory by default.

### 4a. Metrics baseline workflow

Canonical path:
- generate a bounded scan dataset
- publish a descriptive metrics report tied to that dataset

Current example:
- dataset: `docs/reports/data/scan-2-10000.jsonl`
- report: `docs/reports/metrics-2-10000.md`

Command:

    python3 -m src.pet.cli scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl

The metrics baseline is currently scan-backed rather than driven by a separate
stable summary script.

### 4b. Family benchmark workflow

Primary helper:
- `pet families benchmark-disjoint`

Current example:
- report: `docs/reports/families-benchmark-disjoint.md`

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
- committed report at `docs/reports/atlas-<start>-<end>.md`

Stable filename pattern:
- `atlas-<start>-<end>.md`

### Metrics baseline step

Current canonical example:
- dataset: `docs/reports/data/scan-2-10000.jsonl`
- report: `docs/reports/metrics-2-10000.md`

Expected output:
- committed bounded metrics report

Current stable filename:
- `metrics-2-10000.md`

### Family benchmark step

Command pattern:

    pet families benchmark-disjoint

Expected output:
- stdout from the family benchmark command, to be used when preparing
  `docs/reports/families-benchmark-disjoint.md`

Current stable report filename:
- `families-benchmark-disjoint.md`

### 5. Classify statements before promoting them

Interpretation must follow `docs/reports/observation-pipeline.md`.

In practice:
- raw bounded facts belong in reports
- repeated bounded regularities may be called bounded empirical patterns
- beyond-range claims must be marked as conjectures
- proved or definitional statements belong to established status

## Current canonical artifacts

Stable entry points currently recognized by the repository:

- `docs/SPEC.md`
- `docs/STATUS.md`
- `docs/reports/metrics-2-10000.md`
- `docs/reports/atlas-2-100000.md`
- `docs/reports/atlas-2-1000000.md`
- `docs/reports/signatures-catalog-2-1000000.md`
- `docs/reports/families-benchmark-disjoint.md`
- `docs/reports/observation-pipeline.md`

## Current stable vs non-canonical boundary

Canonical workflow does **not** mean every script in `tools/` is stable.

At the current stage, the canonical lab path is centered on:
- bounded scan generation
- atlas-style summarization
- bounded report publication
- explicit statement classification

Exploratory scripts may still be useful, but they are not automatically part of
the canonical workflow unless a report or stable document explicitly relies on them.

## Usage rule

When adding a new PET report, prefer extending the existing bounded pipeline
instead of inventing a parallel undocumented flow.

If a result cannot be reproduced from explicit bounded inputs with a clear command
path, it should not be treated as a canonical PET lab artifact.
