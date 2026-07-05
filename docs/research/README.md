# PET Research

This directory contains active research material that is **not** part of the stable PET-Base specification.

## Structure

- `notes/` — conceptual notes, theory fragments, and structural observations
- `experiments/` — experiment writeups and scorecards
- `partial/` — partial shape material
- `datasets/` — raw datasets, streams, indexes, and large research artifacts
- `archive/` — historical or superseded research documents kept for reference

## How to read this area

### If you want conceptual notes
Start in:

- `notes/`

### If you want concrete experiment writeups
Start in:

- `experiments/`

### If you want partial shape material
Start in:

- `partial/`

### If you want raw data
Look in:

- `datasets/`

### If you want older material that is no longer the main line
Look in:

- `archive/`

## Operational PET route pipeline

The current PET-to-classic routing pipeline is documented in:

- `pet_route_pipeline.md`

It describes the completed text-output pipeline: structural diagnosis, grip diagnostic, route escalation policy, route execution, factor promotion, final status, and canonical examples.

## PET/PEG 2.0 operator probes

The PET/PEG 2.0 foundation layer introduces X/Y/Z operator axes:

- X — support topology
- Y — recursive refinement
- Z — connectivity dynamics

The current research-only probes are:

- `../../tools/research/pet_operator_axis_invariant_probe.py` — validates the first operator-axis invariants against the existing shape-level operator algebra.
- `../../tools/research/pet_operator_address_probe.py` — resolves documented PET/PEG 2.0 recursive operator addresses against PET objects produced by `pet.encode(N)`.
- `../../tools/research/pet_operator_x_address_probe.py` — classifies hypothetical address-aware X-axis operations using the uniform parent-support form `NEW(parent_address, q)` / `DROP(parent_address, p)`.
- `../../tools/research/pet_operator_y_address_probe.py` — classifies address-aware Y-axis targets for `INC(address)` / `DEC(address)` without mutating PET objects.
- `../../tools/research/pet_operator_y_mutation_probe.py` — emits research-only hypothetical Y-axis value-level exponent mutations for `INC(address)` / `DEC(address)`.
- `../../tools/research/pet_operator_z_route_probe.py` — validates research-only Z-axis history-prefix route references for `REDIRECT(...)` / `SHADOW_SELECT(...)`.

These probes are not part of stable PET-Base behavior. They do not change CLI defaults, core operator semantics, routing, anchor selection, or residual descent.

## PET-METICA reading map

PET-METICA material is intentionally split by stability level.

### Current PET-METICA core

These files describe the current rewrite-geometric line:

- `notes/PET-METICA.md`
- `notes/pet_metica_minimal_definitions.md`
- `notes/pet_metica_operational_semantics.md`
- `notes/pet_metica_claims_snapshot.md`

### Supporting notes

These notes support the current line with bounded observations, generator
structure, local rewrite laws, or empirical vocabulary:

- `notes/pet-grammar-note.md`
- `notes/pet-local-generator-algebra-note.md`
- `notes/pet-generator-structural-encoding-note.md`
- `notes/pet-exponent-shape-trace-observed-patterns.md`
- `notes/pet-shape-families-note.md`
- `notes/pet_metica_seven_family_tier_drift.md` — bounded ladder on `7×{2^k,3^k}` seed asymmetry and explicit tier-drift correction
- `notes/pet-multiplicative-grammar.md`
- `notes/pet-problem-statement.md`
- `notes/pet-completion-aware-residual-descent.md` — structural walls, lateral doors, trap-doors, and completion-aware residual descent observations
- `notes/pet-operator-semantics-pattern-distribution.md` — experimental PET/PEG operator-semantics matrix pattern distribution through 100,000

### Experimental / not core

These files explore PET-METICA `⊕` candidates, comparisons, examples, or
negative results. They are useful research material, but they are not part of
the current operational core:

- `notes/pet_metica_plus_design.md`
- `notes/pet_metica_plus_semantics_v0.md`
- `notes/pet_metica_plus_av0_counterexamples.md`
- `notes/pet_metica_plus_av1_semantics.md`
- `notes/pet_metica_plus_av1_vs_cv0.md`
- `notes/pet_metica_plus_candidate_examples.md`
- `notes/pet_metica_plus_case_2_6_30.md`
- `notes/pet_metica_plus_decision.md`

## Important note

Files in `research/` are research material.

They may contain:

- partial ideas
- exploratory formulations
- outdated hypotheses
- local procedures
- experimental directions not promoted to project-wide source of truth

For current project-wide source of truth, see:

- `../VISION.md`
- `../reports/STATUS.md`
- `notes/PET-METICA.md`
- `../reference/SPEC.md`

## PET/PEG 2.0 operator semantics reports

Promotion policy:

- `../foundations/pet-peg-2.0-operator-semantics-promotion-policy.md`

The PET/PEG 2.0 foundation layer now has experimental documented reports that
aggregate the executable X/Y/Z operator probes.

Single-number report:

- `../../tools/research/pet_operator_semantics_report.py` — aggregates PET/PEG
  2.0 operator-semantics probe output for one integer.

Multi-number matrix report:

- `../../tools/research/pet_operator_semantics_report_matrix.py` — scans
  explicit numbers and/or ranges, derives pattern signatures, groups numbers by
  shared observed patterns, and summarizes pattern anatomy.

Related probes:

- `../../tools/research/pet_operator_xy_commutativity_probe.py`
- `../../tools/research/pet_operator_address_stability_probe.py`
- `../../tools/research/pet_operator_axis_invariant_probe.py`

Example experimental report commands:

    python tools/research/pet_operator_semantics_report.py 60
    python tools/research/pet_operator_semantics_report_matrix.py --range 12 18
    python tools/research/pet_operator_semantics_report_matrix.py 60 --range 12 14 --json
    pet experimental operator-semantics report 60
    pet experimental operator-semantics matrix --range 12 18

For large ranges, the matrix report can emit filtered pattern-group views without
per-number rows:

    python tools/research/pet_operator_semantics_report_matrix.py --range 2 100 --top-patterns 3 --no-rows
    python tools/research/pet_operator_semantics_report_matrix.py --range 12 18 --min-count 2 --pattern leaf-blocked --no-rows --json

Matrix pattern groups also include experimental `pattern_class` labels, such as
`single-support-leaf`, `multi-support-removal`, and
`multi-support-recursive-leaf-blocked`, to make recurrent operator-semantics
patterns easier to compare across ranges.

Use `--anatomy` to include arithmetic anatomy summaries for each pattern
group, including `omega_dist`, `big_omega_dist`, `max_exp_dist`,
`first_nonflat_exp_dist`, `squarefree_ratio`, and `has_support_2_3_ratio`.

Use `--check-rules` to include experimental rule-check summaries in the
matrix payload, including the observed multi-support nonflat rule.

Use `--compact-text` to suppress large text-only number lists and print a
shorter summary, rule-check section, and compact pattern-group lines.

These probes and experimental reports are not part of stable PET-Base
behavior. They do not change CLI defaults, core operator semantics, routing,
anchor selection, or residual descent.
- `notes/pet-guarded-redirect-factor-chain-certificates.md` — factor-chain product certificates for guarded redirect structural factorization research.
- `notes/pet-guarded-redirect-structural-wall-families.md` — structural-prefix wall families observed in guarded redirect factor-chain research.
