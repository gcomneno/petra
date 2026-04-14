# PET Reports

This directory contains report-oriented material produced around PET analysis, observation workflows, and dataset-based summaries.

## Structure

- `process/` — operational and process documentation used to produce, classify, or manage reports
- `generated/` — generated or report-style markdown outputs
- `data/` — datasets, summaries, JSONL scans, and other report input/output artifacts

## How to read this area

### If you want process or operational guidance
Start in:

- `process/`

Typical contents include:
- workflow notes
- artifact policies
- contributor/operator guidance
- observation pipeline notes
- tooling classification material

### If you want report outputs
Start in:

- `generated/`

Typical contents include:
- atlas-style reports
- benchmark summaries
- metrics summaries
- catalog-style outputs

### If you want raw report data
Look in:

- `data/`

Typical contents include:
- JSONL scans
- atlas summaries
- report-side intermediate or final data artifacts

## Important note

Files in `reports/` are not all equal.

- `process/` contains human-facing operational documentation
- `generated/` contains report documents derived from analysis
- `data/` contains artifacts consumed or produced by those reports

For project-wide source of truth, see:

- `../VISION.md`
- `../STATUS.md`
- `../PET-METICA.md`
- `../reference/SPEC.md`
