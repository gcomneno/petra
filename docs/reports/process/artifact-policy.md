# PET artifact tracking policy

## Scope

This document defines the current artifact policy for PET report-generation
artifacts and local research outputs.

Its purpose is to make explicit what is expected to be committed, what is
expected to remain local, and what should not be treated as canonical repo
state.

## Artifact classes

### 1. Committed source artifacts

These are source-controlled files that define the PET lab workflow or publish
stable bounded results.

Examples:
- `README.md`
- `docs/SPEC.md`
- `docs/STATUS.md`
- `docs/reports/canonical-workflow.md`
- `docs/reports/README.md`
- bounded report documents under `docs/reports/*.md`

### 2. Local generated datasets

These are generated data artifacts used to reproduce or extend bounded reports,
but they are currently treated as local working artifacts rather than committed
repository state.

Current examples:
- `docs/reports/data/scan-2-10000.jsonl`
- `docs/reports/data/scan-2-100000.jsonl`
- `docs/reports/data/scan-2-1000000.jsonl`

Policy:
- generate locally when needed
- do not assume they are present in a fresh clone
- do not describe them as committed repo artifacts
- use them as reproducibility inputs, but treat them as operator-side artifacts

### 3. Local derived summaries

These are generated from local datasets and currently remain local as well.

Current examples:
- `docs/reports/data/atlas-summary-2-100000.txt`
- `docs/reports/data/atlas-summary-2-1000000.txt`

Policy:
- generate locally when needed
- treat as disposable/regenerable unless future policy says otherwise
- do not rely on them as committed repository state

### 4. Exploratory local artifacts

Transient charts, dumps, compressed files, binary outputs, and other one-off
research artifacts are local unless explicitly promoted into a documented report
workflow.

Examples:
- files under `artifacts/`
- temporary files
- local binary or compressed experiment outputs

## Current repository rule

At the current stage, `docs/reports/data/` is ignored by Git.

This means:
- report markdown files may be committed
- datasets and summary text files under `docs/reports/data/` are local by default
- reproducibility is command-based, not clone-completeness-based

## Contributor rule

When adding a new bounded report:
- commit the report document if it is intended as part of the stable lab record
- document the regeneration command
- document the expected local inputs if they are not committed
- do not silently rely on ignored local files without saying so

## Future policy note

This policy reflects the current repository state, not a final immutable choice.

A later consolidation step may decide to version some bounded datasets or some
derived summaries explicitly, but that must happen together with a deliberate
`.gitignore` update and SSOT index alignment.
