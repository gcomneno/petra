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

- [`RELATED-WORK.md`](RELATED-WORK.md) — maintained survey of PETRA's
  relationship to prior mathematics and computer-science literature, including
  explicit novelty boundaries. Canonical for research context; non-normative
  for PETRA semantics.
- [`SOURCE-REGISTER.md`](SOURCE-REGISTER.md) — maintained classification of
  external research material as direct related work, methodological
  inspiration, or unpromoted source material.
- [`notes/open-problems.md`](notes/open-problems.md) — active front.
  Each problem has a statement, a why-now, a first step, and a status.
  Updated as work progresses.
- [`notes/open-threads.md`](notes/open-threads.md) — historical archive
  of the T-series. All threads closed, moved to `open-problems.md`, or
  marked out of scope. Not maintained.

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

- [`notes/form-road-value-boundary.md`](notes/form-road-value-boundary.md)
  — T01/T16 boundary note. Form (`shape(n)`), strada (a sequence of
  canonical operators between two forms), and value (`n`) are three
  distinct levels. The signature of a transition is the pair
  `(shape(n), shape(n+1))`, not the strada, not the value.

- [`notes/recursive-reconstruction-t01.md`](notes/recursive-reconstruction-t01.md)
  — T01 third result. Every canonical shape can be built from the
  mother in a single chain of struct applications, using only two
  elementary pieces, in a height-first order. The chain is one strada,
  not a canonical invariant.

### Notes (continued)

- [`notes/collatz-like-reduction-dominance.md`](notes/collatz-like-reduction-dominance.md)
  — P2. Counterexample: every `3n+k` (k odd) is reduction-dominant, not
  only Collatz. The factor 3, not the value k=1, produces the reduction.

- [`notes/shape-context-not-bounded.md`](notes/shape-context-not-bounded.md)
  — P3. Negative. No bounded `k` determines the Collatz successor's
  shape from `(shape(n), n mod 2^k)`. Argument via Dirichlet.

- [`notes/shape-multiplicity.md`](notes/shape-multiplicity.md)
  — P4. Negative. The shape is a coarse descriptor: 64 distinct shapes
  for 10000 integers, top 10 covering 92.7%.

- [`notes/p5-symmetric-struct-destruct.md`](notes/p5-symmetric-struct-destruct.md)
  — P5. Positive. `struct` gains a fourth hook for inner containers;
  `destruct` is invertible with `inner=True`.

- [`notes/t01-struct-destruct-exponential.md`](notes/t01-struct-destruct-exponential.md)
  — T01 closed. `struct`/`destruct` on `shape(k^n)` work with one limit,
  resolved later by P5. Duplication lemma verified.

- [`notes/t02-functoriality-partial.md`](notes/t02-functoriality-partial.md)
  — P6 partial. `shift` and `double` admit `F_T` on a bounded sample.
  Six fingerprint classes at `N = 60`.

- [`notes/t03-multiset-invariant.md`](notes/t03-multiset-invariant.md)
  — P7. Positive. The fingerprint depends only on the multiset of
  exponents in the base, not on the prime values nor their order.

- [`notes/t04-overlap-too-coarse.md`](notes/t04-overlap-too-coarse.md)
  — P8. Negative. `node_count(meet) / node_count(join)` takes only 17
  distinct values on 124251 pairs.

- [`notes/recursive-metric-no-clusters.md`](notes/recursive-metric-no-clusters.md)
  — T07 partial. A recursive metric defined from shape structure
  overlaps with `structural_distance`; no natural clusters.

- [`notes/t07-finer-metrics-change-classification.md`](notes/t07-finer-metrics-change-classification.md)
  — P11. Positive. Replacing `node_count` with `depth` or `depth_mass`
  changes the fingerprint classification.

- [`notes/t08-3n-minus-1.md`](notes/t08-3n-minus-1.md)
  — P12. Positive. `3n-1` is reduction-dominant, same profile as
  `3n+k`. The sign of k does not matter.

- [`notes/t16-fingerprint-asymptotics.md`](notes/t16-fingerprint-asymptotics.md)
  — T16. Reduction of the fingerprint signal to the arithmetic function
  `g(n)` and its exact recurrence.

- [`notes/t19-stab-fifth-point.md`](notes/t19-stab-fifth-point.md)
  — T19 partial. Fifth data point at `N = 10^8` excludes the hypothesis
  `SumPk2 ~ c / sqrt(log log N)`.

- [`notes/t17-cache-id-bug.md`](notes/t17-cache-id-bug.md)
  — T17. Root cause of intermittent test failure: cache keyed by
  `id(shape)` could be poisoned by id reuse. Fixed.

- [`notes/t18-ruff-mypy-clean.md`](notes/t18-ruff-mypy-clean.md)
  — T18. Resolver now passes ruff and mypy clean.

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
replacement. It documents the PET, PET-Base, PET/PEG 2.0, and PET-Metrics
research lines. It is retained as evidence and provenance. It is not
maintained.

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
