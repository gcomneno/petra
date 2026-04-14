# PET contributor and operator guide

## Who this is for

This guide is for contributors or operators who want to reproduce bounded PET
reports or add a new one without reverse-engineering repo habits.

## Start here

Read these documents in this order:

1. `README.md`
2. `docs/reports/canonical-workflow.md`
3. `docs/reports/README.md`
4. `docs/reports/artifact-policy.md`
5. `docs/reports/tooling-classification.md`
6. `docs/reports/observation-pipeline.md`

## Current canonical lab path

The current canonical PET lab path is:

1. generate a bounded scan dataset
2. generate an atlas-style summary if the report needs it
3. publish a bounded report tied to explicit inputs
4. classify statements correctly before promoting them

Canonical examples already in use:
- metrics baseline: `docs/reports/metrics-2-10000.md`
- atlas reports: `docs/reports/atlas-2-100000.md`, `docs/reports/atlas-2-1000000.md`
- family benchmark: `docs/reports/families-benchmark-disjoint.md`

## Core commands

Generate a bounded scan dataset:

    python3 -m src.pet.cli scan <start> <end> --jsonl docs/reports/data/scan-<start>-<end>.jsonl

Generate an atlas-style summary from a scan dataset:

    python3 tools/atlas_summary.py docs/reports/data/scan-<start>-<end>.jsonl > docs/reports/data/atlas-summary-<start>-<end>.txt

Run the current canonical family benchmark:

    pet families benchmark-disjoint

## Minimal smoke run

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

Treat these as stable research tooling:
- `tools/atlas_summary.py`
- `pet families benchmark-disjoint`
- `tools/cluster_families_disjoint.py` (compatibility wrapper)

Treat `tools/cluster_families.py` as secondary/non-canonical.

Do not assume the rest of `tools/` is part of the canonical lab workflow.

## Artifact rule

Under the current repository policy:
- report markdown files under `docs/reports/` may be committed
- `docs/reports/data/` is local and Git-ignored
- local datasets and atlas summaries are reproducibility inputs, not committed repo state

Do not write docs that pretend ignored local data files are present in a fresh clone.

## Claim classification rule

Use `docs/reports/observation-pipeline.md`.

In practice:
- bounded facts stay bounded
- repeated bounded regularities are still not proofs
- beyond-range claims must be marked as conjectures
- definitional or proved facts belong to established status

## How to add a new bounded report

1. decide the bounded scope explicitly
2. generate the required local dataset or benchmark output
3. write the report as descriptive, comparative, benchmark, catalog, or workflow note
4. state the exact regeneration command(s)
5. state the local inputs the report depends on
6. classify statements conservatively
7. update `docs/reports/README.md` if the report becomes part of the stable lab record

## What not to do

- do not promote bounded findings into general theory silently
- do not treat exploratory scripts as stable lab interfaces by default
- do not assume local ignored data artifacts are committed
- do not add a new parallel workflow without documenting it

