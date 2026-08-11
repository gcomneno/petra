# PETRA VISION — Temporal Dynamics Hypothesis

Status: pre-result research hypothesis.

Protocol identifier:

`petra-vision-temporal-dynamics-hypothesis-v0`

This document records a temporal research direction before any dedicated
temporal or spectral corpus result is evaluated.

It does not modify the frozen Gate 2 constructions.

## Motivation

Gate 2 already uses discrete dynamic evolution.

The graph-Laplacian and lattice constructions produce states at successive
integer steps, and the frozen readers sample selected steps such as:

1, 2, 4, 8, 16, 32.

So PETRA VISION already contains an algorithmic time coordinate.

Until now, however, time has primarily been treated as part of the measurement
protocol: several states are sampled and concatenated into a signature.

The temporal hypothesis asks a stronger question:

> Can the characteristic timing and ordering of geometry-only information
> propagation itself be treated as an intrinsic observable of a shape?

The distinction is important.

Gate 2 asks whether global geometric information becomes observable through
dynamics.

The temporal program asks how quickly, in what order, and on which characteristic
timescales that information becomes observable.

## Temporal hypothesis

For a fixed geometry-only dynamic law and a fixed global clock, a geometry may
possess a reproducible temporal response that contains information not captured
by a single static state or by an unordered collection of independently chosen
measurements.

A provisional bounded formulation is:

> A PETRA geometry may be characterized not only by spatial occupancy and a
> propagation law, but by the coordinate-free temporal trajectory induced when
> that law acts on the geometry.

This is a mathematical research hypothesis.

It is not a claim that PETRA models physical spacetime, relativity, cosmology,
or any physical field theory.

## Space and time are coupled operationally

In the current constructions, geometry determines:

- which sites exist in the dynamic domain;
- which sites communicate;
- which paths connect distant regions;
- the number and lengths of available propagation routes;
- local and global bottlenecks.

Those spatial properties determine how the state can evolve over discrete time.

Therefore space and time are not independent metadata in the proposed temporal
analysis.

The geometry constrains the dynamics, and the dynamics determines the temporal
response.

This motivates the working interpretation:

> Geometry determines not only where information can propagate, but the
> characteristic times at which global geometric relations become observable.

## Global clock

All primary temporal experiments must use a single frozen global discrete clock.

The time index is:

k = 0, 1, 2, ...

A geometry must not receive its own adaptive clock, rescaling, stopping rule, or
time normalization chosen from its identity or from corpus discrimination
results.

Matched comparisons must use the same propagation law parameters and the same
clock unless the parameter itself is the declared experimental variable.

## Normalized dynamic state

Where an Euler numerator recurrence uses denominator q, the exact integer
numerator state x(k) grows by powers of q.

For temporal relaxation analysis, the natural normalized state is:

y(k) = x(k) / q^k

using exact rational arithmetic wherever practical.

This separates physical-style state evolution from the integer representation
used to preserve exact computation.

The existing integer numerator trajectory remains valid for exact equality and
collision analysis.

## Candidate temporal observables

The following observables are predeclared as candidates for later Gate 3
evaluation.

They are not yet positive results.

### 1. Full temporal multiset trajectory

At every frozen time k, construct the same coordinate-free state multiset used
by the corresponding geometry-only reader.

The ordered sequence over time is retained.

Time order is meaningful.

Spatial vertex order remains unavailable.

This is the most direct temporal extension of the existing Gate 2 signatures.

### 2. First-divergence time

For two geometries that collide at k = 0, record the first frozen time at which
their coordinate-free dynamic readers differ.

If they never differ inside the frozen horizon, record that fact explicitly.

First-divergence time is a pairwise diagnostic.

It is not by itself a single-shape identity feature.

### 3. Distinction-growth curve

For a fixed corpus and fixed reader, record the number of equivalence classes
remaining after observations through time k.

This yields a corpus-level curve describing when discrimination becomes
available.

The curve must be reported over a predeclared time horizon.

No time step may be added because it happens to separate a desired collision.

### 4. Persistence of distinctions

If two geometries become distinguishable at some time, record whether the
distinction:

- persists at all later sampled times;
- disappears later;
- disappears and reappears.

This distinguishes transient temporal information from persistent information.

### 5. Relaxation trajectory

Using normalized exact state y(k), record coordinate-free measures of departure
from the equilibrium mean.

Candidate measures include exact variance-like second moments and state range.

Any threshold-derived relaxation time must have its threshold frozen before
corpus evaluation.

Adaptive thresholds are forbidden.

### 6. Spectral decay factors

For linear Laplacian dynamics, spectral modes provide an independent description
of characteristic temporal decay.

Gate 3 may compare temporal observations against explicit Laplacian spectral
controls.

The purpose is attribution:

- determine whether observed temporal scales are already explained by the
  spectrum;
- identify whether temporal discrimination adds anything beyond static spectral
  invariants.

No spectral uniqueness claim is predeclared.

## Temporal signature versus sampled signature

The existing Gate 2 dynamic signatures already contain several time samples.

That does not by itself establish the temporal hypothesis.

A Gate 3 temporal result must explicitly study the temporal structure of the
trajectory, for example:

- when distinctions first arise;
- how discrimination accumulates with time;
- whether distinctions persist;
- how relaxation rates differ;
- how those times relate to spectral modes.

Thus the research object changes from:

geometry -> several sampled states

to:

geometry -> ordered temporal response.

## Primary invariance boundary

A valid temporal observable may use:

- the global discrete time index;
- exact dynamic state values;
- geometry-derived dynamic connectivity;
- frozen propagation parameters.

It must not use:

- absolute spatial coordinates in the final reader;
- vertex identity or ordering;
- shape code;
- AST or decoder identity;
- FGS ordinal unless explicitly declared as a labelled control;
- corpus index;
- geometry-specific adaptive clocks;
- post-result time selection.

## Translation control

Rigid integer translation of the source geometry must not change its temporal
signature or characteristic temporal observables.

## Reflection control

For a reflection-equivariant construction, exact reflected geometries must have
the same coordinate-free temporal response.

The retained Gate 1A pair remains the canonical control:

`G(G(G(T)),G(T,T))`

and

`G(G(T,T),G(G(T)))`

A temporal method that separates this pair under a reflection-equivariant
dynamic law requires causal audit before any positive interpretation.

## Matched temporal nulls

Every dedicated temporal experiment must define its causal null before corpus
evaluation.

Depending on the question, useful matched nulls may include:

- identical initial state with propagation disabled;
- identical uniform medium versus a declared modified medium;
- identical dynamic trajectory with time order deliberately discarded;
- identical sampled states with only temporal summary information removed.

The null must isolate the temporal property actually being claimed.

## Temporal-order null

A particularly important future control is predeclared:

> Keep the same collection of sampled coordinate-free states but remove their
> time labels and temporal order.

If the ordered temporal trajectory distinguishes geometries that the unordered
collection does not, then temporal ordering itself contributes information.

This control must be implemented without exposing spatial ordering.

## No geometry-specific time warping

The following are forbidden for primary evidence:

- rescaling time separately for each geometry;
- aligning trajectories by a geometry-specific landmark;
- choosing a geometry-specific starting point;
- choosing a geometry-specific stopping point;
- dynamic time warping optimized using shape identity;
- selecting sample times after observing collisions.

Such methods may be studied later as labelled diagnostics only if explicitly
motivated.

## Relationship to Gate 2

Gate 2 remains a study of global geometric coupling.

Its current findings must not be reinterpreted retroactively as dedicated
temporal evidence.

In particular:

- D1 concerns weak geometric coupling and probe attribution;
- F1 concerns proximity coupling among geometry-derived factors;
- L1 concerns propagation through a uniform full lattice;
- E1 concerns an occupancy-aware material modification of that lattice.

The temporal hypothesis is motivated by those results but is not required to
classify them.

## Relationship to Gate 3

Gate 3 is the natural location for the first dedicated temporal study because it
already reserves explicit spectral controls.

A proposed Gate 3 sequence is:

1. freeze a reference geometry-only dynamic construction;
2. measure full discrete temporal trajectories under a fixed global clock;
3. construct temporal-order and no-propagation controls;
4. measure first-divergence and distinction-growth behavior;
5. measure normalized relaxation behavior;
6. compare those observations with explicit spectral invariants and decay
   factors;
7. classify what temporal information is independent, redundant, or
   symmetry-forbidden.

The reference construction should be selected from already frozen Gate 2
constructions rather than invented after inspecting temporal results.

## Success criterion

The temporal hypothesis receives positive bounded support if a predeclared
temporal observable adds reproducible discrimination or explanatory structure
beyond its matched non-temporal control while:

- preserving the geometry-only source boundary;
- preserving declared symmetries;
- using a single frozen global clock;
- avoiding adaptive time selection;
- replaying deterministically.

Perfect injectivity is not required.

## Valid negative result

A negative result is scientifically valid if temporal ordering or characteristic
timescales add no information beyond matched spatial/dynamic or spectral
controls.

Parameters, horizons, thresholds, and sample times must not be changed merely
to obtain a positive result.

## Interpretation boundary

The useful conceptual analogy is:

> Space supplies the permitted routes; dynamics turns those routes into a
> temporal response.

This may resemble ideas encountered in spacetime or field theories, but PETRA
VISION currently provides only a discrete mathematical information-propagation
model.

No physical or cosmological equivalence is claimed.

## Deferred status

This hypothesis is frozen for future Gate 3 work.

No dedicated temporal corpus result has yet been evaluated.

Gate 2 must be completed on its existing matrix before temporal experiments are
activated.
