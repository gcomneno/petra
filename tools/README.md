# tools

This directory contains operator-side PET utilities.

Presence in `tools/` does **not** imply that a script is part of the canonical
PET interface or that its interface is stable.

For the current tooling classification, see
[`../docs/reports/process/tooling-classification.md`](../docs/reports/process/tooling-classification.md).

## Scope rule

Tools kept in this directory must operate on already-known PET inputs, such as:

- known integers used for deterministic PET analysis
- known factorization or factor specifications
- PET artifacts
- scan JSONL artifacts
- known PET shapes or signatures

Tools should not implement structural discovery, opaque-integer reconstruction,
candidate search, byte-stream discovery, probe pipelines, or target-directed
search.

## Stable tooling

- `atlas_summary.py` — atlas-style summary generation used by bounded reports
- `cluster_families_disjoint.py` — compatibility wrapper for the disjoint family
  clustering benchmark tooling; canonical entry point: `pet families benchmark-disjoint`

## Secondary tooling

- `cluster_families.py` — related family-clustering tooling that is not part of
  the current canonical report-facing path
- `scan_query.py` — small operator-side helper for filtering and grouped counts
  over PET scan JSONL artifacts
- `pet_table.py` — CLI utility for generating PET tables from integer datasets
- `pet_profile_range.py` — CLI utility for exploring PET profiles over numeric
  ranges
- `pet_family_combinations.py` — CLI utility for generating or counting
  combinations across PET families in a range
- `pet_structural_diff.py` — research-facing structural diff helper for exact
  multiplicative and divisive PET updates

## Exploratory tooling policy

Exploratory tooling should not stay in this directory by default.

A script may remain only if it is:

- deterministic
- documented or tested
- based on known PET structures or generated scan artifacts
- not a discovery/search pipeline over opaque inputs

Otherwise it should be removed or moved to a separate research repository.

## Notes

- Do not infer interface stability from directory placement alone.
- Do not use this README as the source of truth for workflow or artifact policy;
  use the docs under `docs/reports/`.
