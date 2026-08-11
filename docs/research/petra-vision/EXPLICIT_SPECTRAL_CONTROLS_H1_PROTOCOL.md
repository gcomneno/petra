# PETRA VISION Gate 3 — G3-H1 heat-trace control protocol

## Status

Frozen before corpus observation.

Protocol identifier:

`petra-vision-explicit-spectral-controls-h1-v0`

G3-H1 follows the completed S0/S1 and S2 controls.

This protocol defines only H1.

P1, I1, T1, and O1 remain inactive.

## Purpose

G3-H1 tests how much of the discrimination present in the full frozen S1
operator spectrum survives under a predeclared compressed, coordinate-free
spectral observable.

H1 is not a new classifier search.

No H1 parameter may be selected or removed after corpus results are observed
in order to improve discrimination.

## Frozen substrates

Evaluate the same global frozen operators used by G3-S1:

- G3-B0;
- G3-D1;
- G3-F1;
- G3-L1.

S2 component/factor spectra are not inputs to H1.

H1 therefore remains a global operator-spectrum control.

## Exact heat-trace representation

For a frozen operator A with eigenvalue multiset lambda_1, ..., lambda_n,
define the spectral power sums

`p_k = sum_i lambda_i^k = trace(A^k)`.

Define

`p_0 = n`.

The formal heat trace is

`H(t) = trace(exp(-t A))`.

Its Taylor expansion at zero is

`H(t) = sum_{k >= 0} ((-t)^k / k!) p_k`.

Therefore a finite tuple of exact power sums is an exact finite Taylor jet of
the heat trace at t = 0.

G3-H1 uses these exact spectral moments rather than floating-point eigenvalues,
matrix exponentials, or sampled transcendental values.

## Frozen compression ladder

Evaluate all four predeclared truncations:

- H1-M1: `(p_0, p_1)`;
- H1-M2: `(p_0, p_1, p_2)`;
- H1-M4: `(p_0, p_1, p_2, p_3, p_4)`;
- H1-M8: `(p_0, p_1, ..., p_8)`.

All four are primary reported controls.

No truncation is selected as the preferred result after observing the corpus.

The ladder is intended to measure how discrimination changes as progressively
more exact heat-trace Taylor information is retained.

## Exact arithmetic

Moments must be derived deterministically from the exact S1 characteristic
polynomial representation or an exactly equivalent rational/integer operator
calculation.

Allowed arithmetic:

- integers;
- exact rationals;
- exact Newton-identity reconstruction from the monic characteristic
  polynomial.

Forbidden for the primary reader:

- floating-point eigensolvers;
- numerical root finding;
- approximate matrix exponentials;
- tolerance-based eigenvalue clustering;
- coordinate-dependent rounding;
- corpus-dependent thresholds.

Canonical rational values must use the same exact `(numerator, denominator)`
style already frozen for S1 where applicable.

## Reader boundary

The H1 reader may observe only:

- the frozen substrate identifier;
- the exact global S1 operator characteristic polynomial or an exactly
  equivalent exact operator representation;
- the resulting exact moment tuple for the declared truncation.

The reader must not observe:

- vertex identity;
- eigenvector identity or orientation;
- coordinates;
- bounding-box placement;
- factor order;
- component order;
- recovered AST/tree identity;
- shape serialization;
- corpus index;
- probe or initial condition;
- dynamic trajectory;
- S2 local factor/component spectra.

## Relationship to S1

Every H1 signature is a deterministic function of the full S1 spectrum.

Therefore the following are protocol invariants:

1. H1 may merge distinct S1 spectra.
2. H1 must never split an S1 collision.
3. H1-M2 must refine or equal H1-M1.
4. H1-M4 must refine or equal H1-M2.
5. H1-M8 must refine or equal H1-M4.

Any violation is an implementation or source-boundary failure, not a positive
scientific result.

For any operator of order at most four, the exact power sums through p_4,
together with the order, determine the monic characteristic polynomial through
Newton identities.

Therefore, where the frozen F1 operator order is at most four, H1-M4 is
expected to reproduce the S1 spectral partition exactly.

This is a mathematical sanity check, not a corpus discovery.

## Historical #23/#41 control

Where the retained reflected/reordered #23/#41 pair collides under S1, it must
also collide under every H1 truncation.

H1 is derived only from S1 eigenvalue information and cannot introduce
orientation information absent from S1.

If H1 separates this pair while S1 does not, stop and audit the implementation
before any further corpus observation.

## Corpus order

Observe corpora separately and strictly in this order:

1. Phase 1 — 110 forms;
2. held-out width-4 — 27 forms;
3. extended frozen domain — 137 forms.

Phase 1 must be interpreted before held-out is executed.

Held-out must be interpreted before extended is executed.

No headline score may hide the separate held-out behavior.

## Required measurements

For every substrate and every H1 truncation record:

- operator order distribution;
- distinct H1 signatures;
- exact collision groups;
- collision-pair count;
- distinct-signature delta relative to S1;
- S1 collision pairs split by H1;
- collision pairs introduced by H1 relative to S1;
- refinement relation to the preceding H1 truncation;
- behavior of #23/#41 where applicable;
- deterministic replay;
- source SHA256;
- evidence SHA256.

The evidence must also report the complete compression curve:

`S1 -> H1-M8 -> H1-M4 -> H1-M2 -> H1-M1`

without selecting a post-hoc winner.

## Interpretation

A useful positive H1 result is bounded evidence that a compressed exact
heat-trace/spectral-moment observable retains explicitly measured distinctions
of the full S1 spectrum.

A negative H1 result is also valid: substantial spectral discrimination may
require more information than the frozen finite moment tuple retains.

H1 cannot establish information beyond S1 because it is a deterministic
compression of S1.

In particular, H1 cannot explain any Gate 2 dynamic distinction that is absent
from S1.

## Rabbit-watch conditions

The following are scientifically interesting but must be interpreted within the
H1 boundary:

- unexpectedly high retention of S1 distinctions at H1-M1 or H1-M2;
- the same low-order moment compression retaining strongly across Phase 1 and
  held-out;
- a sharp substrate-specific difference in the amount of spectral information
  retained by low-order moments.

The following are not rabbits and require an immediate audit:

- H1 splits an S1 collision;
- a lower-order truncation refines a higher-order truncation;
- #23/#41 separates when it collides under S1;
- H1 uses information outside the frozen global operator spectrum.

## Non-claims

G3-H1 does not establish:

- universal injectivity;
- spectral uniqueness;
- recovery of PETRA syntax or AST identity;
- orientation recovery;
- dynamic or temporal information beyond the operator spectrum;
- probe independence;
- impulse-response attribution;
- physical heat diffusion or physical time;
- robustness outside the frozen corpora.

The term heat trace here denotes the formal spectral exponential trace and its
exact Taylor moments. It is not a claim about physical thermodynamics.

## Gate boundary

Freeze this protocol before implementing or observing H1 corpus results.

After protocol freeze:

1. implement exact moment extraction;
2. add focused tests and source-boundary audits;
3. freeze the evidence runner before corpus observation;
4. observe Phase 1 only;
5. interpret before held-out;
6. continue in the declared corpus order.

P1, I1, T1, and O1 remain inactive throughout G3-H1.
