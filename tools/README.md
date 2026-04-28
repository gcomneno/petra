# tools

This directory contains operator-side PET utilities.

Presence in `tools/` does **not** imply that a script is part of the canonical
PET CLI interface or that its interface is stable.

For the current tooling classification, see
[`../docs/reports/process/tooling-classification.md`](../docs/reports/process/tooling-classification.md).

## Scope rule

Tools kept in this directory must operate on already-known PET inputs, such as:

- known integers used for deterministic PET analysis
- known factorization or factor specifications
- PET artifacts
- scan JSONL artifacts
- known PET shapes or signatures

Tools must not implement structural discovery over opaque integers, ISS/IRSR
pipelines, byte-stream discovery, preimage search, probe pipelines, or
target-directed candidate search.

## Stable tooling

- `atlas_summary.py` — atlas-style summary generation used by bounded reports
- `cluster_families_disjoint.py` — compatibility wrapper for the disjoint family
  benchmark tooling; canonical entry point: `pet families benchmark-disjoint`

## Dataset and report helpers

- `cluster_families.py` — related family-clustering tooling
- `distinct_shapes.py` — distinct-shape extraction over bounded ranges
- `height_distribution.py` — PET height distribution over bounded ranges
- `shape_entropy.py` — entropy-style summaries over PET shape datasets
- `shape_count_fast.py` — fast shape counting utility
- `shape_first_occurrence.py` — first-occurrence reporting for PET shapes
- `scan_query.py` — filtering and grouped counts over PET scan JSONL artifacts
- `pet_table.py` — PET table generation from integer datasets
- `pet_profile_range.py` — PET profile exploration over numeric ranges
- `pet_family_combinations.py` — family-combination generation/counting in ranges

## PET-METICA and shape research tooling

- `pet_rewrite_metric.py` — rewrite-metric helper
- `pet_shape_algebra.py` — shape algebra helper
- `pet_structural_diff.py` — structural diff helper for exact PET updates
- `shape_rewrite_arithmetic_v0.py` — tested v0 arithmetic rewrite helper
- `exponent_shape_trace.py` — exponent-shape trace reporting over known ranges

## Notes

- Do not infer interface stability from directory placement alone.
- Do not use this README as the source of truth for workflow or artifact policy;
  use the docs under `docs/reports/`.
