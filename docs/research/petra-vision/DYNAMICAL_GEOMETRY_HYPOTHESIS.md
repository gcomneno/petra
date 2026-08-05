# Dynamical geometry hypothesis

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status and scope

Status: **research hypothesis with bounded exploratory computational support**.

One declared Galton-like propagation law has produced deterministic and
sampled evidence over the complete 110-shape Phase 1 bounded corpus. That
evidence is recorded in `DYNAMICAL_MESSAGE_EVIDENCE.md`.

The result does not demonstrate a universal PETRA dynamic law, physical
propagation, robustness, security, novelty, or production readiness. It is not
a Phase 1 completion requirement. Literature and prior-art review remain
pending through the private RADAR.

This document extends the static PETRA VISION research model only. It does
not change the Phase 1 geometry contract, its acceptance criteria, or the
static decoding claim.

## Central formulation

The general research hypothesis is:

> Network form can alter the dynamics of what propagates through it.

The PETRA formulation is:

> Geometry is the structural message; propagation may be its temporal
> readout.

Conservatively stated, a PETRA geometry might be readable not only from its
static occupied-cell structure, but also from the characteristic dynamics
induced by that structure under a declared propagation law and standardized
probe.

## Formal research model

Let:

- `V` be the supported structural shapes;
- `C` be the canonical geometries;
- `X` be the admissible dynamic states on a geometry;
- `U` be the controlled input or probe space;
- `P_C` be a propagation operator determined by canonical geometry `C`;
- `Y(C, x0, u, t)` be the observed trajectory or response at time `t`, from
  initial state `x0` and input `u`;
- `Sigma(C, p)` be a dynamic signature produced by a standardized probe `p`.

The existing static maps remain unchanged:

```text
encode_geometry: V -> C
decode_geometry: C -> V
```

The dynamic layer is a research extension only:

```text
(C, x0, u) -> Y
Y -> candidate structural invariants or identity
```

For a declared law and observation procedure, `P_C` governs the evolution of
an admissible state in `X`; `Y` records all or part of that evolution; and
`Sigma` is a specified, reproducible reduction of `Y`. A signature may be a
full trajectory, a sampled response, or stable derived measurements. It is
not presumed injective: distinct canonical geometries may have the same
signature under a particular law, probe, boundary condition, and sampling
procedure. Such dynamic collisions define possible equivalence classes and
must be retained rather than discarded.

Geometry may influence admissible paths, neighborhood coupling, delays,
attenuation, boundary conditions, interference or concentration, and
synchronization and diffusion modes. This is not a claim that every physical
or computational medium exhibits every listed effect, nor that an effect
observed in one declared model transfers to another medium.

## Falsifiable hypotheses

The following hypotheses are proposed for declared models, probes, and
observation rules. A failed test is evidence against the applicable
hypothesis, not a result to be hidden or reclassified.

1. **Deterministic replay.** Identical `C`, probe `u`, initial state `x0`,
   propagation rules, boundary conditions, and sampling rules produce
   identical `Y` and `Sigma`.
2. **Authorized translation invariance.** For the current Phase 1 authorized
   normalization, translating an otherwise identical occupied-cell geometry
   before normalization does not alter the resulting `Sigma`.
3. **Order sensitivity.** Exchanging structurally distinct bays in a
   geometry produces an observable difference in `Y` or `Sigma` under at
   least one declared canonical probe, if the canonical geometries are
   structurally distinct after the exchange.
4. **Recursive correspondence.** A declared subgeometry has a reproducible
   correspondence with a local response region or derived local signature in
   its containing geometry.
5. **Bounded local-mutation response.** A bounded local structural mutation
   causes a measurable change in the response under a declared probe, or is
   retained as a measured counterexample/collision if it does not.
6. **Geometry-only computation.** Dynamic computation receives only occupied
   geometry cells and declared model parameters; it receives no serialized
   PETRA, address, label, metadata, object identity, or adapter-side channel.
7. **Possible bounded-shape distinguishability.** Different bounded shapes
   can, but are not assumed to, be dynamically distinguishable under one or
   more declared probes and laws.
8. **Dynamic equivalence is allowed.** Dynamic collisions and equivalence
   classes between non-identical geometries are explicit expected outcomes;
   injectivity of dynamic signatures is not required unless experiments later
   establish it for a precisely stated domain and protocol.

## Bounded exploratory Galton-like evidence

A transient Galton-like computational thread has now supplied bounded evidence
for deterministic replay, order-sensitive response, direct terminal
probability propagation, finite-corpus dynamic distinguishability, inverse
decoding, reflection equivariance, reader-dependent equivalence classes, and
finite observation precision.

The exact protocol, measurements, margins, decoder results, methodological
risks, and non-claims are recorded in `DYNAMICAL_MESSAGE_EVIDENCE.md`.

The evidence is specific to its declared rule, initial condition, bounded
corpus, and observation convention. It does not replace the canonical
geometry-only graph-Laplacian experiment below, satisfy its controls, or
establish a physical mechanism.

## Minimal computational experiment

This first canonical reproducible experiment is a diagnostic over all 110
Phase 1 shapes.
shapes. It is a neutral computational propagation law, not a performance
benchmark or physical-media claim.

1. Start from each canonical occupied-cell geometry and derive a
   four-neighbor adjacency graph solely from occupied geometry cells.
2. Use deterministic graph-Laplacian diffusion as the first propagation law,
   with the graph Laplacian defining `P_C` and fixed, documented integration
   and sampling rules.
3. Define canonical impulse probes and canonical observation points from
   normalized occupied cells and graph structure only. Do not consult PETRA
   serialization, native addresses, labels, adapter objects, or other native
   identity data.
4. Record each full trajectory or a stable, fully specified derived signature
   `Sigma(C, p)`, together with declared model and probe parameters.
5. Test deterministic replay, authorized translation invariance, child-order
   sensitivity, and bounded local-mutation sensitivity.
6. Count signature collisions, retain every collision and negative result,
   and record their participating geometries rather than treating them as
   failures of the dataset.
7. Compare structurally different shapes having similar elementary statistics
   (for example occupied-cell count, graph order, edge count, or bounding-box
   dimensions) to distinguish simple size effects from candidate structural
   effects.

The experiment may produce evidence of distinguishability, collisions, or no
useful separation. It introduces no required threshold, no claim of a
physical propagation mechanism, and no extension to the Phase 1 completion
gate.

## Risks, controls, and audit requirements

Known risks include isospectral or otherwise dynamically equivalent
non-identical geometries; dependence on the selected probe or boundary
conditions; discretization artifacts; accidental leakage through canonical
ordering or labels; overfitting a propagation law to the 110-shape corpus;
confusion of computational adjacency with physical propagation; dependence on
sampling resolution; and false inference of structural causation from
correlation.

Controls must include at least:

- negative controls that preserve elementary graph or occupancy statistics
  where feasible while breaking the proposed structural relation;
- null or permuted probe/observation assignments, reported separately from
  canonical-probe results;
- repeated runs over declared changes to time step, duration, and sampling
  resolution, with sensitivity recorded;
- comparison of more than one declared boundary condition or a clear record
  when only one is used;
- held-out or newly generated bounded shapes before any propagation-law
  tuning is interpreted as general evidence; and
- retention of all negative outcomes, ambiguous results, and collisions.

A geometry-only audit is mandatory for every experiment implementation. The
audit must establish that graph construction, probe selection, propagation,
observation selection, signature derivation, and result grouping consume
only canonical occupied geometry plus explicitly declared experimental
parameters. It must specifically exclude serialized PETRA, addresses,
labels, metadata, object identity, and adapter-side channels. Any necessary
canonical ordering must be derived from the geometry itself, documented, and
tested for leakage with negative controls.

## Research consequences and boundaries

Static structural decoding recovers a supported PETRA shape from canonical
geometry under `decode_geometry`. Dynamic structural fingerprinting compares
responses or signatures induced by a declared law and probe; it may identify
a candidate class without uniquely decoding a shape. Dynamic inverse
reconstruction would attempt to infer geometry from `Y` or `Sigma`; it is a
separate, harder research problem and is not implied by fingerprinting.
Physical observation pipelines would add a material system, sensing,
calibration, noise, and model-validation questions; they are outside this
computational experiment.

Accordingly, dynamic observations may complement static geometry but do not
replace its exact decoder, establish causal physical behavior, or justify a
claim of security, robustness, novelty, or production readiness.
