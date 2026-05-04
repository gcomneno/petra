# PET contributor and operator guide

## Who this is for

This guide is for contributors or operators who want to reproduce bounded PET
reports, run the current PET triage workflow, or add a new report without
reverse-engineering repo habits.

## Start here

Read these documents in this order:

1. `README.md`
2. `docs/reports/process/canonical-workflow.md`
3. `docs/reports/process/tooling-classification.md`
4. `docs/reports/README.md`
5. `docs/reports/process/artifact-policy.md`
6. `docs/reports/process/observation-pipeline.md`

## Current canonical workflows

PET currently has two canonical workflow families.

### Operator-side triage workflow

Use this for single-number PET structural diagnostics and bounded classic
handoff.

Canonical implementation:

- `tools/core/pet_triage_pipeline.sh`

Compatibility entry points:

- `tools/pet_triage_pipeline.sh`
- `tools/peelator.sh`

Command:

    tools/pet_triage_pipeline.sh N

The triage workflow runs:

1. PET race diagnostic
2. PET classic handoff policy
3. PET-approved classic probe route when implemented
4. verified classic scan summary / policy
5. legacy diagnostics as non-fatal secondary output

For direct inspection, use:

    tools/pet_local_probe_proposal.py N --operator-depth auto --backbone-selection race
    tools/pet_classic_handoff_route.py N

### Bounded report workflow

Use this for scan-backed reports and generated research artifacts.

The bounded report path is:

1. generate a bounded scan dataset
2. generate an atlas-style summary if the report needs it
3. publish a bounded report tied to explicit inputs
4. classify statements correctly before promoting them

Canonical examples already in use:

- metrics baseline: `docs/reports/generated/metrics-2-10000.md`
- atlas reports: `docs/reports/generated/atlas-2-100000.md`, `docs/reports/generated/atlas-2-1000000.md`
- family benchmark: `docs/reports/generated/families-benchmark-disjoint.md`

## Core commands

Run PET triage for a single number:

    tools/pet_triage_pipeline.sh N

Run the PET race diagnostic directly:

    tools/pet_local_probe_proposal.py N --operator-depth auto --backbone-selection race

Run the PET classic handoff policy directly:

    tools/pet_classic_handoff_route.py N

Generate a bounded scan dataset:

    python3 -m src.pet.cli scan <start> <end> --jsonl docs/reports/data/scan-<start>-<end>.jsonl

Generate an atlas-style summary from a scan dataset:

    python3 tools/atlas_summary.py docs/reports/data/scan-<start>-<end>.jsonl > docs/reports/data/atlas-summary-<start>-<end>.txt

Run the current canonical family benchmark:

    pet families benchmark-disjoint

## Minimal smoke runs

### Triage smoke run

Use a small number with an implemented PET classic handoff route:

    tools/pet_triage_pipeline.sh 10007 --no-fork --no-fork-follow --no-recursive

Expected high-level signals:

- `PET TRIAGE PIPELINE`
- `0. PET race diagnostic`
- `1. PET classic handoff policy`
- `classic_probe_policy = primality-check-only`
- `route_status = available`

This smoke run checks the current PET-policy-first operator path.

### Bounded report smoke run

A small bounded run can be used as a quick operator-side smoke check for the
current scan + summary path.

Example:

    python3 -m src.pet.cli scan 2 5000 --jsonl docs/reports/data/scan-2-5000.jsonl
    python3 tools/atlas_summary.py docs/reports/data/scan-2-5000.jsonl > docs/reports/data/atlas-summary-2-5000.txt

Quick checks:

    ls -lh docs/reports/data/scan-2-5000.jsonl
    tail -n 3 docs/reports/data/scan-2-5000.jsonl
    ls -lh docs/reports/data/atlas-summary-2-5000.txt
    sed -n '1,120p' docs/reports/data/atlas-summary-2-5000.txt

Notes:

- these files are local operator-side artifacts under the current artifact policy
- this is a smoke run for the bounded scan + summary workflow, not a committed report artifact by itself

## Tooling boundary

Current tool implementations are namespaced:

- `tools/core/` — PET triage core and policy-first handoff
- `tools/classic/` — bounded classic verification support
- `tools/legacy/` — historical lens diagnostics
- `tools/research/` — dataset/report and PET-METICA research helpers

Root-level `tools/*.py` and `tools/*.sh` entries are compatibility wrappers unless
the tooling classification document says otherwise.

Treat these as stable operator-side triage tooling:

- `tools/core/pet_triage_pipeline.sh`
- `tools/core/pet_local_probe_proposal.py`
- `tools/core/pet_classic_handoff_route.py`

Treat these as stable report-facing tooling:

- `tools/research/atlas_summary.py`
- `pet families benchmark-disjoint`
- `tools/research/cluster_families_disjoint.py`

Compatibility wrappers remain available at:

- `tools/pet_triage_pipeline.sh`
- `tools/peelator.sh`
- `tools/atlas_summary.py`
- `tools/cluster_families_disjoint.py`

Do not assume the rest of `tools/` is part of the canonical lab workflow.

## Artifact rule

Under the current repository policy:

- report markdown files under `docs/reports/` may be committed
- `docs/reports/data/` is local and Git-ignored
- `.pet-cache/` is local and Git-ignored
- local datasets, atlas summaries, cache files, and resume states are reproducibility inputs, not committed repo state

Do not write docs that pretend ignored local data or cache files are present in a fresh clone.

## Claim classification rule

Use `docs/reports/process/observation-pipeline.md`.

In practice:

- bounded facts stay bounded
- repeated bounded regularities are still not proofs
- beyond-range claims must be marked as conjectures
- definitional or proved facts belong to established status
- PET diagnostics are not arithmetic factors unless a classic stage explicitly verifies a divisor

## How to add a new bounded report

1. decide the bounded scope explicitly
2. generate the required local dataset or benchmark output
3. write the report as descriptive, comparative, benchmark, catalog, or workflow note
4. state the exact regeneration command(s)
5. state the local inputs the report depends on
6. classify statements conservatively
7. update `docs/reports/README.md` if the report becomes part of the stable lab record

## How to add a new operator workflow

1. decide whether it extends PET triage, classic verification, legacy diagnostics, or research tooling
2. place the implementation under the appropriate namespace
3. keep compatibility wrappers only when existing callers need them
4. document whether the workflow is canonical, legacy, or research-facing
5. clearly state whether it factors, verifies divisors, or only emits PET diagnostics

## What not to do

- do not promote bounded findings into general theory silently
- do not treat exploratory scripts as stable lab interfaces by default
- do not assume local ignored data/cache artifacts are committed
- do not add a new parallel workflow without documenting it
- do not present PET-only diagnostics as verified arithmetic factorization
