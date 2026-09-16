# PET tooling classification

## Scope

This document classifies the current `tools/` layout after the PET triage
reorganization. The first-class structural factorization CLI lives in the
main `pet` command, not under `tools/`.

The purpose of this classification is to keep PET focused on already-known
inputs, PET artifacts, structural diagnostics, and bounded classic verification.
Tools may analyze, build, validate, summarize, or explain known PET structures.
They must not reintroduce broad structural discovery over opaque integers.

## Boundary rule

Tools kept in this repository may operate on:

- known integers used for deterministic PET analysis
- known factorizations or factor specifications
- PET artifacts
- scan JSONL artifacts
- known PET shapes or signatures
- PET-selected bounded classic verification windows

Tools should not implement:

- ISS / IRSR structural search
- byte-stream-to-structure discovery
- preimage search
- target-directed opaque reconstruction
- unbounded factor search presented as PET discovery
- opaque-integer reconstruction without known structure

## First-class structural factorization CLI

The public structural factorization entry point is:

    pet structural-factorization N

This command emits a stable PET structural route summary and may optionally
write a `pet.syntax_tree.v0` explanatory artifact with `--pest-json PATH`.

`tools/` triage scripts remain operator-side diagnostics and compatibility
entry points; they are not the public name of the structural factorization
feature.

## Current tools layout

The `tools/` root contains compatibility wrappers and documentation. Real tool
implementations are grouped by role:

- `tools/core/` — PET triage core and policy-first handoff.
- `tools/classic/` — bounded classic verification support.
- `tools/legacy/` — historical lens diagnostics kept for comparison and tests.
- `tools/research/` — dataset/report helpers and shape research tools.

Root-level wrappers remain available for existing scripts, tests, and
documentation examples. Directory placement, not wrapper presence, defines the
current role of a tool.

## Core PET triage tooling

These tools define the current PET-policy-first workflow.

### `tools/core/pet_triage_pipeline.sh`

Status:
- canonical operator-side triage pipeline

Reason:
- runs PET race diagnostic first
- routes through PET classic handoff policy
- keeps legacy diagnostics non-fatal
- replaces the old peelator-first workflow

Compatibility:
- `tools/pet_triage_pipeline.sh`
- `tools/peelator.sh`

### `tools/core/pet_local_probe_proposal.py`

Status:
- core PET triage diagnostic

Reason:
- produces the single-number PET race diagnostic report
- supports `--operator-depth auto`
- supports `--backbone-selection race`
- reports `race_shape_diagnostic`
- emits a human-readable PET diagnostic summary

### `tools/core/pet_backbone_race.py`

Status:
- core PET backbone selection helper

Reason:
- evaluates candidate backbone orders using PET-only shape probes
- exposes shared race quality and shape diagnostic helpers
- does not factor `N`

### `tools/core/pet_backbone_race_matrix.py`

Status:
- core diagnostic matrix helper

Reason:
- produces batch PET backbone race diagnostics
- validates diagnostic behavior across primes, powers, mixed shapes, diagonals,
  and border cases

### `tools/core/pet_classic_handoff_route.py`

Status:
- core PET-to-classic policy bridge

Reason:
- maps PET shape diagnostics to classic probe policies
- does not use the old NEW/DROP fallback as the decision engine
- only exposes implemented PET-approved classic routes
- leaves `complex-border` unavailable until a dedicated route exists

## Classic verification support

These tools support bounded classic verification. They may verify arithmetic
divisors, but they must clearly distinguish verified divisors from PET-only
diagnostics.

### `tools/classic/pet_classic_scan_summary.py`

Status:
- classic verification summary helper

Reason:
- summarizes verified divisors from PET-guided classic scans
- accepts divisors only when arithmetic verification succeeds

Compatibility:
- `tools/pet_classic_scan_summary.py`

### `tools/classic/pet_classic_scan_policy.py`

Status:
- classic scan policy classifier

Reason:
- classifies classic scan sources and policy status
- does not verify new divisors directly

Compatibility:
- `tools/pet_classic_scan_policy.py`

### `tools/classic/pet_crumb_classic_scan.py`

Status:
- classic scan support helper

Reason:
- preserves first-step crumb classic scan behavior
- used by scan summary tooling

Compatibility:
- `tools/pet_crumb_classic_scan.py`

### `tools/classic/pet_root_window_classic_scan.py`

Status:
- classic scan support helper

Reason:
- preserves bounded root-window classic scan behavior
- used by scan summary tooling

Compatibility:
- `tools/pet_root_window_classic_scan.py`

## Legacy diagnostics

These tools are retained for secondary diagnostics, historical comparison, and
test coverage. They are not the main decision engine of the current triage flow.

### `tools/legacy/pet_lens_hint.py`

Status:
- legacy lens diagnostic

Compatibility:
- `tools/pet_lens_hint.py`

### `tools/legacy/pet_lens_candidates.py`

Status:
- legacy lens diagnostic

Compatibility:
- `tools/pet_lens_candidates.py`

### `tools/legacy/pet_lens_transition.py`

Status:
- legacy lens diagnostic

Compatibility:
- `tools/pet_lens_transition.py`

### `tools/legacy/pet_lens_mass_probe.py`

Status:
- legacy lens diagnostic

Compatibility:
- `tools/pet_lens_mass_probe.py`

### `tools/legacy/tune_peelator.sh`

Status:
- legacy tuning diagnostic

Reason:
- retained for historical recursive-lens tuning experiments
- not part of the canonical triage path

Compatibility:
- `tools/tune_peelator.sh`

## Research and report helpers

These tools operate on known inputs, explicit bounded ranges, or existing scan
artifacts. They are useful for reports and research, but they are not the
canonical operator-side triage path.

### Stable report-facing helpers

- `tools/research/atlas_summary.py`
- `tools/research/cluster_families_disjoint.py`

Compatibility wrappers:
- `tools/atlas_summary.py`
- `tools/cluster_families_disjoint.py`

Canonical CLI alternative:
- `pet families benchmark-disjoint`

### Secondary dataset/report helpers

- `tools/research/cluster_families.py`
- `tools/research/distinct_shapes.py`
- `tools/research/height_distribution.py`
- `tools/research/shape_entropy.py`
- `tools/research/shape_count_fast.py`
- `tools/research/shape_first_occurrence.py`
- `tools/research/scan_query.py`
- `tools/research/pet_table.py`
- `tools/research/pet_profile_range.py`
- `tools/research/pet_family_combinations.py`
- `tools/research/exponent_shape_trace.py`
- `tools/research/mass_excitation_delta.sh`
- `tools/research/mass_excitation_sweep.sh`

Compatibility wrappers remain in `tools/` with the same filenames.

### Structural research helpers

- `tools/research/pet_shape_algebra.py`
- `tools/research/pet_rewrite_metric.py`
- `tools/research/pet_structural_diff.py`
- `tools/research/shape_rewrite_arithmetic_v0.py`
- `tools/research/shape_overlap.py`
- `tools/research/stencil_lens_probe.py`
- `tools/research/surface_signature.py`

Compatibility wrappers remain in `tools/` with the same filenames.

`tools/research/pet_shape_algebra.py` is still import-compatible through
`tools/pet_shape_algebra.py` for existing tests and callers.

## Usage rule

Workflow docs, contributor docs, and report regeneration notes should treat only
the current core triage tools and explicitly listed stable report-facing helpers
as interface-stable.

Compatibility wrappers are allowed for existing scripts, tests, and historical
documentation, but new operational documentation should prefer the namespaced
paths.

Legacy diagnostics must not override PET race diagnostics or PET classic handoff
policy decisions.

Research helpers may be useful, but they should not be presented as canonical
public interfaces by default.
