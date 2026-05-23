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


## Structural factorization and current PET triage workflow

The first-class public CLI entry point for structural factorization is:

```bash
pet structural-factorization N
```

The `tools/` triage scripts remain the canonical operator-side workflow for
deeper diagnostics, bounded classic handoff, and compatibility:

- `core/pet_triage_pipeline.sh` — canonical PET triage pipeline implementation.
- `pet_triage_pipeline.sh` — compatibility wrapper that delegates to `core/pet_triage_pipeline.sh`.
- `peelator.sh` — compatibility wrapper that delegates to `pet_triage_pipeline.sh`.

The triage pipeline follows this order:

1. PET race diagnostic
2. PET classic handoff policy
3. PET verified divisor summary
4. PET classic scan policy
5. legacy diagnostics, non-fatal

The core contract is:

> Structural factorization decomposes the PET-visible shape route. PET does
> not claim to factor opaque integers directly. PET selects a structural
> diagnostic and a bounded classic verification policy. Classic stages only
> accept divisors when explicitly verified.

## Core PET triage tools

These tools are part of the current PET-policy-first flow and live under
`tools/core/` unless otherwise noted:

- `core/pet_local_probe_proposal.py` — single-number PET race diagnostic report.
- `core/pet_backbone_race.py` — PET-only backbone race selection.
- `core/pet_backbone_race_matrix.py` — batch matrix for backbone race diagnostics.
- `core/pet_classic_handoff_route.py` — maps PET shape diagnostics to classic probe policies.
- `classic/pet_classic_scan_summary.py` — summarizes verified classic divisors from PET-guided scans.
- `classic/pet_classic_scan_policy.py` — classifies classic scan sources and policy status.
- `core/pet_triage_pipeline.sh` — canonical triage pipeline.

## Compatibility wrappers

- `pet_triage_pipeline.sh` — legacy root-level entry point kept for compatibility;
  delegates to `core/pet_triage_pipeline.sh`.
- `peelator.sh` — older command name kept for compatibility; delegates to
  `pet_triage_pipeline.sh`.

## Legacy diagnostics

Legacy diagnostics live under `tools/legacy/`.

Compatibility wrappers remain in `tools/` for existing scripts and tests, but
new callers should prefer the explicit legacy paths only when they intentionally
need historical lens diagnostics:

- `legacy/pet_lens_hint.py`
- `legacy/pet_lens_candidates.py`
- `legacy/pet_lens_transition.py`
- `legacy/pet_lens_mass_probe.py`
- `legacy/tune_peelator.sh`

Legacy diagnostics remain available for secondary diagnostics, historical
comparison, and test coverage, but they are no longer the main decision engine
of the triage flow.

Legacy diagnostics must not override PET race diagnostics or classic handoff
policy decisions.

## Classic scan support tools

Classic scan support tools live under `tools/classic/`.

Compatibility wrappers remain in `tools/` for existing scripts and tests:

- `classic/pet_classic_scan_summary.py`
- `classic/pet_classic_scan_policy.py`
- `classic/pet_crumb_classic_scan.py`
- `classic/pet_root_window_classic_scan.py`

These tools are still used by classic scan summary/policy tooling and should
not be removed without replacing their callers and tests.


## Stable tooling

Stable report tooling now lives under `tools/research/`.

Compatibility wrappers remain in `tools/` for existing scripts, tests, and
documentation examples:

- `research/atlas_summary.py` — atlas-style summary generation used by bounded reports
- `research/cluster_families_disjoint.py` — compatibility wrapper for the disjoint family
  benchmark tooling; canonical entry point: `pet families benchmark-disjoint`

## Dataset and report helpers

Dataset/report research helpers live under `tools/research/`.

Compatibility wrappers remain in `tools/` for existing scripts, tests, and
documentation examples:

- `research/cluster_families.py` — related family-clustering tooling
- `research/distinct_shapes.py` — distinct-shape extraction over bounded ranges
- `research/height_distribution.py` — PET height distribution over bounded ranges
- `research/shape_entropy.py` — entropy-style summaries over PET shape datasets
- `research/shape_count_fast.py` — fast shape counting utility
- `research/shape_first_occurrence.py` — first-occurrence reporting for PET shapes
- `research/scan_query.py` — filtering and grouped counts over PET scan JSONL artifacts
- `research/pet_table.py` — PET table generation from integer datasets
- `research/pet_profile_range.py` — PET profile exploration over numeric ranges
- `research/pet_family_combinations.py` — family-combination generation/counting in ranges
- `research/exponent_shape_trace.py` — exponent-shape trace reporting over known ranges

## PET-METICA and shape research tooling

PET-METICA and structural research helpers live under `tools/research/`.

Compatibility wrappers remain in `tools/` for existing scripts, tests, imports,
and documentation examples:

- `research/pet_rewrite_metric.py` — rewrite-metric helper
- `research/pet_shape_algebra.py` — shape algebra helper
- `research/pet_structural_diff.py` — structural diff helper for exact PET updates
- `research/shape_rewrite_arithmetic_v0.py` — tested v0 arithmetic rewrite helper
- `research/shape_overlap.py` — shape overlap helper
- `research/stencil_lens_probe.py` — stencil lens probe helper
- `research/surface_signature.py` — surface signature helper
- `research/exponent_shape_trace.py` — exponent-shape trace reporting over known ranges

PET-shadow / backbone-closure research helpers:

- `research/pet_shape_scale_compare_study.py` — compares PET-shadow local projection summaries across scale rules.
- `research/pet_shape_overlap_projection_study.py` — studies positional overlap of PET-shadow visible segment projections.
- `research/pet_shadow_route_correlation_study.py` — correlates PET-shadow summaries with decimal rigidity and full signature cost.
- `research/pet_backbone_closure_basis_study.py` — generates PET-native target bases from shallow flat-backbone closures.
- `research/pet_backbone_closure_shadow_matrix.py` — compares PET-shadow summaries across backbone-closure target bases.

## Notes

- Do not infer interface stability from directory placement alone.
- Do not use this README as the source of truth for workflow or artifact policy;
  use the docs under `docs/reports/`.


- `tools/research/pet_recursive_shape_chunk_study.py`
  - Diagnostic study for small digit-mixed numbers with computable real PET.
  - Recursively searches PET-guided decimal splits.
  - Compares local PET generators using product/gcd/lcm-style merge candidates.
  - Classifies local preservation versus `emergent-global-generator` failures.


## PET shadow monster router

`tools/research/pet_shadow_monster_router.py` combines the global `Σ_backbone`
signal with optional local `Λ_chunk` diagnostics and routes each input into a
diagnostic monster class.

It does not factor `N` and does not reconstruct `PET(N)`.

Current route classes include:

- `saturated-shadow-coherent`
- `sigma-coherent-large-field`
- `weak-or-unstable-shadow-field`
- `fragile-shadow-field`
- `local-preserved-shadow-coherent`
- `local-preserved-sigma-floor-risk`
- `deceptive-stable-sigma`
- `diffuse-field`

Large inputs skip recursive chunk diagnosis by default through
`--max-chunk-digits 8`, avoiding expensive local segmentation on opaque numbers.

Use `--progress` to print per-number progress messages to stderr.

## PET/PEG 2.0 operator semantics research reports

PET/PEG 2.0 operator semantics research tooling lives under `tools/research/`.

The aggregated report tools are experimental documented tooling; primitive
operator probes remain research-only. Promotion policy is documented in
`../docs/foundations/pet-peg-2.0-operator-semantics-promotion-policy.md`.

These tools do not define stable CLI behavior and do not change PET core
factorization, routing, anchor selection, verification, or default operator
semantics.

Single-number report:

- `research/pet_operator_semantics_report.py` — aggregates PET/PEG 2.0
  operator-semantics probes for one integer, including recursive address
  samples, X/Y samples, X/Y composition classifications, address-stability
  classifications, and axis-invariant summary.

Multi-number matrix report:

- `research/pet_operator_semantics_report_matrix.py` — runs the single-number
  report across explicit numbers and/or `--range START END`, derives
  operator-semantics pattern signatures, groups numbers by shared patterns, and
  summarizes pattern anatomy.

Example experimental report commands:

    python tools/research/pet_operator_semantics_report.py 60
    python tools/research/pet_operator_semantics_report_matrix.py --range 12 18
    python tools/research/pet_operator_semantics_report_matrix.py 60 --range 12 14 --json

For large ranges, the matrix report can emit filtered pattern-group views without
per-number rows:

    python tools/research/pet_operator_semantics_report_matrix.py --range 2 100 --top-patterns 3 --no-rows
    python tools/research/pet_operator_semantics_report_matrix.py --range 12 18 --min-count 2 --pattern leaf-blocked --no-rows --json
