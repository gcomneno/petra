# PET Research

This directory contains research material at two distinct levels:

1. **Current PETRA research** — active research directions on the PETRA
   runtime, the Resolver satellite, and the shape-space framework.
   Non-normative for PETRA semantics, but actively maintained.
2. **Historical PET research** — research material produced before the
   PETRA replacement, retained as evidence and provenance. Not
   normative and not maintained.

For PETRA semantics, the sole normative source is
[`../reference/SPEC.md`](../reference/SPEC.md).

## Current PETRA research

The current PETRA research line explores shape-space as a setting for
analyzing integer sequences and dynamics. The work uses the Resolver
satellite (`../../resolver/`) and the PETRA canonical runtime
(`../../src/petra/`) without extending either.

### Living registry

- [`notes/open-threads.md`](notes/open-threads.md) — index of active and
  dormant research directions. Each thread has a statement, a minimal
  example, a status, and dependencies. Updated as work progresses.

### Notes

- [`notes/collatz-structural-signature.md`](notes/collatz-structural-signature.md)
  — the Collatz trajectory in shape space: 13 shapes over 112 values,
  reduction-dominant transitions, and a comparison with a random control.

- [`notes/arithmetic-maps-structural-fingerprint.md`](notes/arithmetic-maps-structural-fingerprint.md)
  — cross-map comparison of reduction/expansion/stability profiles.
  Collatz is reduction-dominant (56.7–59.4%); phi, n+1, n+2, n+3 and
  2n+1 are balanced or expansion-dominant.

- [`notes/collatz-ranking-obstruction.md`](notes/collatz-ranking-obstruction.md)
  — a negative structural result: no ranking function over pure PETRA
  shapes can establish termination of the Collatz map. Proof by
  counterexample plus experimental confirmation.

- [`notes/sequence-structural-fingerprint-classifier.md`](notes/sequence-structural-fingerprint-classifier.md)
  — the (red, exp, stab) profile as a classifier of integer sequence
  families. Convergent across N, multi-scale via threshold clustering,
  with structural-class collisions for exponential bases.

- [`notes/exponential-base-structural-class.md`](notes/exponential-base-structural-class.md)
  — T01 first result. Exact identity `shape(k^n) = C(r0^shape(e₁n), …)`,
  a duplication lemma, two falsified conjectures, and a methodological
  warning: the fingerprint is window-dependent, not a class invariant.

### Code

The current research line has produced a derived layer in the Resolver:

- `../../resolver/src/resolver/structural_algebra.py` — contains, meet,
  join, overlap as analytic operators on PETRA shapes.

### Boundary

Current PETRA research:

- does not extend canonical PETRA semantics;
- does not modify `src/petra/`;
- is not part of the maintained PETRA distribution surface;
- is bounded and empirical, not a source of theorems unless explicitly
  proved.

## Historical PET research

<!-- PETRA-HISTORICAL-RESEARCH -->
> [!IMPORTANT]
> **Historical or exploratory research.** Nothing in this section is
> normative for PETRA unless incorporated explicitly into
> [`../reference/SPEC.md`](../reference/SPEC.md).

This section contains research material produced before the PETRA
replacement. It documents the PET, PET-Base, PET/PEG 2.0, PET-Metrics,
and PET-METICA research lines. It is retained as evidence and
provenance. It is not maintained.

## Structure

- `notes/` — conceptual notes, theory fragments, and structural observations
- `experiments/` — experiment writeups and scorecards
- `partial/` — partial shape material
- `datasets/` — conventional location for raw datasets generated locally; these artifacts are not maintained in the repository
- `archive/` — historical or superseded research documents kept for reference

## How to read this area

### If you want conceptual notes
Start in:

- `notes/`

### If you want concrete experiment writeups
Start in:

- `experiments/`

Recent closure record:

- `experiments/pet-metica-seven-family-ladder-pass.md` — seven-family tier ladder (300–1200), tier-drift correction, closed in commit f95a437

Recent archive record:

- `archive/pet-activation-trace-prototype.md` — historical structural-frontier traversal and activation-profile experiment, not promoted

### If you want partial shape material
Start in:

- `partial/`

### If you want raw data

Raw datasets are generated locally and are not maintained in the repository.

The historical million-entry datasets removed from the maintained tree remain
recoverable from Git commit `71b1eab`.

### If you want older material that is no longer the main line
Look in:

- `archive/`

## Operational PET route pipeline

The PET-to-classic routing pipeline is documented in:

- `pet_route_pipeline.md`

It describes the completed text-output pipeline: structural diagnosis, grip diagnostic, route escalation policy, route execution, factor promotion, final status, and canonical examples.

## PET/PEG 2.0 operator probes

The probes below describe historical PET/PEG 2.0 behavior, not
canonical PETRA semantics. The sole normative operator contract is
[`../reference/SPEC.md`](../reference/SPEC.md).

The retained foundation probes use X/Y/Z operator axes:

- X — support topology
- Y — recursive refinement
- Z — connectivity dynamics

The historical research probes were:

- `tools/research/pet_operator_axis_invariant_probe.py`
- `tools/research/pet_operator_address_probe.py`
- `tools/research/pet_operator_x_address_probe.py`
- `tools/research/pet_operator_y_address_probe.py`
- `tools/research/pet_operator_y_mutation_probe.py`
- `tools/research/pet_operator_z_route_probe.py`

These probes were removed during Phase 10 together with the historical
PET runtime. They remain recoverable through Git history.

## PET-METICA reading map

PET-METICA material is intentionally split by role. Its `NEW`, `DROP`,
`INC`, and `DEC` references describe historical behavior or retained
research evidence, never canonical PETRA semantics.

### Historical PET-METICA behavior

These compatibility references describe the historical rewrite-geometric
CLI and research line:

- `notes/PET-METICA.md`
- `notes/pet_metica_minimal_definitions.md`
- `notes/pet_metica_operational_semantics.md`
- `notes/pet_metica_claims_snapshot.md`

### Supporting notes

These notes support the historical line with bounded observations,
generator structure, local rewrite laws, or empirical vocabulary:

- `notes/pet-grammar-note.md`
- `notes/pet-local-generator-algebra-note.md`
- `notes/pet-generator-structural-encoding-note.md`
- `notes/pet-shape-families-note.md`
- `notes/pet_metica_seven_family_tier_drift.md`
- `notes/pet-multiplicative-grammar.md`
- `notes/pet-problem-statement.md`
- `notes/pet-completion-aware-residual-descent.md`
- `notes/pet-operator-semantics-pattern-distribution.md`
- `notes/pet-object-native-relocation-permutation.md`

### Experimental / not core

These files explore PET-METICA `⊕` candidates, comparisons, examples, or
negative results:

- `notes/pet_metica_plus_design.md`
- `notes/pet_metica_plus_semantics_v0.md`
- `notes/pet_metica_plus_av0_counterexamples.md`
- `notes/pet_metica_plus_av1_semantics.md`
- `notes/pet_metica_plus_av1_vs_cv0.md`
- `notes/pet_metica_plus_candidate_examples.md`
- `notes/pet_metica_plus_case_2_6_30.md`
- `notes/pet_metica_plus_decision.md`

## Important note on historical material

Files in the historical section are research material.

They may contain:

- partial ideas
- exploratory formulations
- outdated hypotheses
- local procedures
- experimental directions not promoted to project-wide source of truth

For current project-wide source of truth, see:

- `../VISION.md`
- `../reports/STATUS.md`
- `../reference/SPEC.md`

## Historical PET/PEG 2.0 operator semantics reports

Promotion policy (historical):

- `../foundations/pet-peg-2.0-operator-semantics-promotion-policy.md`

The PET/PEG 2.0 foundation layer had experimental documented reports that
aggregated the executable X/Y/Z operator probes.

These reports and their tools were removed during Phase 10. They remain
recoverable through Git history.

## Historical guarded redirect research

- `notes/pet-guarded-redirect-factor-chain-certificates.md` — factor-chain product certificates for guarded redirect structural factorization research.
- `notes/pet-guarded-redirect-structural-wall-families.md` — structural-prefix wall families observed in guarded redirect factor-chain research.
