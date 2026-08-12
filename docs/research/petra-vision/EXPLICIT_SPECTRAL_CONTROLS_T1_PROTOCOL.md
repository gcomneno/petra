# PETRA VISION Gate 3 — G3-T1 temporal-observation protocol

## Status

Frozen before any dedicated T1 corpus evaluation.

Parent issue:

`#200 — research: attribute PETRA VISION discrimination with explicit spectral controls`

Protocol identifier:

`petra-vision-explicit-spectral-controls-t1-v0`

Gate 3 foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

Immediately preceding completed Gate 3 family:

`263b665` — `research: record Gate 3 impulse response evidence`

Pre-result temporal hypothesis:

`petra-vision-temporal-dynamics-hypothesis-v0`

Temporal-hypothesis SHA256:

`2b84e56d392841389e3e30358213433f2c3833695016c4add118759fefe58df2`

No dedicated T1 result from Phase 1, held-out, or extended has been inspected
before this protocol freeze.

## Gate boundary

At T1 protocol freeze:

- S0/S1 is complete;
- S2 is complete;
- H1 is complete;
- P1 is complete;
- I1 is complete;
- T1 is active only at protocol level;
- O1 is inactive.

Gate 4 adversarial mutation work remains outside this gate.

T1 must not modify or reinterpret any completed Gate 3 result merely to improve
temporal discrimination.

## Purpose

G3-T1 asks a narrow attribution question:

> Given the same frozen dynamic trajectory and the same coordinate-free
> per-time spatial observations, does retaining temporal labels and temporal
> ordering provide discrimination that is lost when those same observations
> are treated as an unordered collection or reduced to selected endpoints?

T1 is an observation-layer ablation.

It does not create a new propagation law.

It does not choose a new probe.

It does not tune the sample schedule.

It does not modify a frozen operator.

It does not alter the per-time spatial reader.

The experimental variable is the temporal observation rule only.

## Core matched-control principle

For every T1 comparison, all of the following remain fixed:

- source geometry;
- frozen substrate construction;
- frozen initial state or frozen probe;
- propagation operator;
- propagation parameters;
- global discrete clock;
- sample times;
- exact evolved states;
- coordinate-free per-time spatial reader.

Only the temporal aggregation of those already computed per-time observations
may differ.

Therefore the primary causal contrast is:

`same sampled states + temporal order`

versus:

`same sampled states - temporal labels/order`

No temporal claim is valid if the two sides use different dynamics, different
initial conditions, different sample times, different spatial readers, or
different numerical approximations.

## Global clock and sample schedule

The global algorithmic time index is:

`k = 0, 1, 2, ...`

The primary T1 sample schedule is exactly the already frozen Gate 2 schedule:

`T = (1, 2, 4, 8, 16, 32)`

No additional sample time may be inserted after corpus inspection.

No sample time may be removed because it reduces discrimination.

No geometry receives:

- an adaptive clock;
- a geometry-specific time rescaling;
- a geometry-specific origin;
- a geometry-specific stopping rule;
- dynamic time warping;
- a collision-dependent sampling schedule.

Step zero may be recorded as a baseline diagnostic.

Step zero is not inserted into the primary six-snapshot T1 reduction because
the primary comparison is explicitly defined over the already frozen sampled
trajectory.

## Spatial snapshot abstraction

For a frozen substrate and frozen geometry, let:

`X_k`

be the exact dynamic state at time `k`.

Let:

`R(X_k)`

be the already declared coordinate-free spatial observation of that state.

T1 defines:

`S_k = R(X_k)`

after any substrate-required exact normalization described below.

T1 never exposes:

- vertex identity;
- vertex order;
- factor ordinal;
- component ordinal;
- absolute spatial coordinates;
- shape code;
- corpus index;
- AST identity;
- decoded tree identity;
- serialization identity.

T1 operates only on the sequence of coordinate-free snapshots:

`S_1, S_2, S_4, S_8, S_16, S_32`

and changes only how time is retained or discarded.

## Exact temporal-state normalization

### Motivation

The frozen Euler implementations preserve exact arithmetic by evolving integer
numerators.

If a recurrence uses denominator `q`, the raw numerator state carries a
representation factor proportional to `q^k`.

That factor must not become an accidental time label in the primary
temporal-order control.

Therefore T1 distinguishes:

1. a canonical normalized state used for primary temporal attribution;
2. the frozen integer-numerator representation retained only as an exact
   compatibility/audit channel where applicable.

### Euler-style substrates

Where the frozen state is represented by an Euler numerator recurrence with
fixed denominator `q`, define:

`Y_k = X_k / q^k`

using exact rational arithmetic.

Every scalar is serialized canonically as:

`(numerator, denominator)`

with:

- positive denominator;
- lowest terms;
- integers represented as `(n, 1)`.

The coordinate-free spatial snapshot is formed from the exact normalized state.

For B0:

`q = 8`

For D1:

`q = 16`

For L1:

use the exact denominator already frozen by the L1 implementation.

No new L1 denominator may be introduced by T1.

### F1

F1 is not an Euler-numerator Laplacian update.

Its frozen propagation operator is the exact rational operator `P`.

The F1 state is already represented in exact rational arithmetic.

No artificial `q^k` normalization is added.

### Raw-numerator audit

For Euler-style substrates, T1 may also record the same temporal reductions over
the exact frozen numerator snapshots.

This is an audit channel only.

For the ordered trajectory, numerator and normalized representations must induce
the same collision partition because time labels and the fixed substrate
denominator make the conversion exactly invertible.

A discrepancy is an implementation failure.

For unordered reductions, numerator and normalized partitions may differ
because the numerator scale can itself reveal the sample time.

Any discrimination that exists only in the raw unordered representation and
disappears under exact normalization is classified as representation-scale
information, not primary temporal-order evidence.

## Frozen substrates

T1 evaluates all four primary Gate 3 substrates separately.

### B0

Use the frozen occupied-cell graph-Laplacian v1 dynamics without modification.

Use its already frozen primary initial condition and per-time coordinate-free
state reader.

The existing B0 source-selection qualification remains in force.

T1 does not reinterpret the B0 probe as intrinsic.

### D1

Evaluate separately:

- matched D1 null;
- D1 coupled.

Use the exact frozen Gate 2 distance-2 construction.

The null and coupled trajectories must use:

- identical geometry;
- identical initial state;
- identical sample schedule;
- identical Euler denominator;
- identical temporal reductions;
- identical spatial reader.

Only the frozen bridge weight differs.

The existing D1 probe qualification remains in force.

T1 does not convert a coordinate-derived excitation into intrinsic evidence.

### F1

Use the frozen FGS factor-proximity propagation operator `P`.

Use the frozen intrinsic six-channel factor state.

The same `P` continues to act independently on the six frozen feature channels.

The per-time reader must remove factor order exactly as already required by the
frozen F1 representation.

T1 may not expose structural address, factor ordinal, recovered AST identity, or
left/right order.

### L1

Use the frozen uniform full-lattice propagation construction.

Use the frozen binary occupancy initial field.

Use the frozen full-lattice operator, propagation parameters, and
coordinate-free per-time state reader.

T1 may not replace the occupancy field with a point probe or otherwise alter the
encoded input semantics.

## Frozen T1 reductions

Exactly four primary per-form temporal reductions are declared.

No fifth reduction may be invented after corpus inspection without a separately
frozen follow-up protocol.

### T1-ordered

Primary full temporal trajectory:

`(S_1, S_2, S_4, S_8, S_16, S_32)`

Time labels and temporal order are retained.

Spatial vertex/factor ordering remains unavailable.

### T1-unordered

Primary temporal-order null.

Use exactly the same six snapshots as T1-ordered, but remove their time labels
and sequence position.

The signature is the canonical sorted multiplicity-preserving multiset:

`multiset({S_1, S_2, S_4, S_8, S_16, S_32})`

Multiplicity is retained.

No snapshot is discarded.

No snapshot is recomputed.

No spatial information is changed.

This is the primary matched control for the claim that temporal ordering itself
contributes discrimination.

### T1-endpoints

Retain only the ordered labelled endpoint pair:

`(S_1, S_32)`

All intermediate sampled observations are discarded.

This tests whether the full trajectory contains discrimination beyond its
declared beginning/end samples.

### T1-terminal

Retain only:

`S_32`

This tests whether the complete sampled trajectory contains discrimination
beyond the final frozen sampled state.

## Primary causal comparisons

### Temporal-order attribution

Primary contrast:

`T1-unordered -> T1-ordered`

Because T1-unordered is a deterministic reduction of T1-ordered:

- ordered may split unordered collision pairs;
- ordered must introduce zero collision pairs relative to unordered.

Any introduced pair indicates an implementation/comparison failure.

A positive temporal-order attribution requires at least one exact unordered
collision pair to split under ordered while all matched controls remain fixed.

### Intermediate-trajectory attribution

Secondary contrast:

`T1-endpoints -> T1-ordered`

Because endpoints are a deterministic reduction of the ordered trajectory:

- ordered may split endpoint collision pairs;
- ordered must introduce zero collision pairs.

A positive result means intermediate sampled states contribute information not
contained in the declared endpoint pair.

### Endpoint-pair attribution

Secondary contrast:

`T1-terminal -> T1-endpoints`

Because terminal is a deterministic reduction of endpoints:

- endpoints may split terminal collision pairs;
- endpoints must introduce zero collision pairs.

### Full trajectory versus terminal

Also report:

`T1-terminal -> T1-ordered`

This is descriptive attribution of all pre-terminal sampled information.

The nested controls above remain the preferred causal decomposition.

## Prefix distinction-growth curves

For each prefix length:

`m = 1, 2, 3, 4, 5, 6`

using the corresponding prefix of:

`(1, 2, 4, 8, 16, 32)`

record separately:

1. the ordered-prefix signature count;
2. the unordered-prefix signature count;
3. exact collision groups;
4. ordered-prefix splits relative to the matched unordered prefix;
5. introduced pairs, which must be zero.

This produces two corpus-level distinction-growth curves:

- ordered temporal accumulation;
- order-discarded temporal accumulation.

The horizon and all six prefix boundaries are frozen before corpus evaluation.

No additional intermediate time may be inserted.

## First-divergence diagnostic

Step zero is recorded separately for this diagnostic.

For every pair that collides under the coordinate-free step-zero observation,
record the first frozen sample time among:

`1, 2, 4, 8, 16, 32`

at which their per-time snapshots differ.

If no sampled divergence occurs, record:

`none-within-frozen-horizon`

First-divergence time is a pairwise diagnostic.

It is not concatenated into a stronger single-form identity signature.

It cannot be used to select new sample times.

## Persistence diagnostic

For every pair observed to diverge at one or more frozen sample times, record
its equality/difference pattern over:

`1, 2, 4, 8, 16, 32`

Classify the pattern descriptively as:

- never diverges;
- diverges and remains different;
- diverges then collides again;
- multiple difference/collision transitions.

This diagnostic measures persistence or transience of temporal distinctions.

It is not a new primary classifier.

## D1 matched causal reporting

For every T1 reduction and every prefix, report D1 null and D1 coupled
separately.

Record:

- null distinct signature count;
- coupled distinct signature count;
- exact null collision pairs;
- exact coupled collision pairs;
- null-to-coupled split pairs;
- newly introduced pairs.

The null/coupled comparison must not change:

- initial state;
- sample schedule;
- temporal aggregation;
- normalization;
- spatial reader.

Only the frozen bridge weight may differ.

The D1 result remains probe-qualified wherever the underlying frozen probe is
coordinate-derived.

T1 cannot erase that prior causal qualification.

## Relationship to completed P1 and I1

P1 and I1 are complete before T1 activation.

Their results may inform interpretation of T1 after a T1 corpus result exists.

They are not T1 signature inputs.

T1 must not:

- import a P1 signature into a temporal signature;
- import an I1 signature into a temporal signature;
- select a temporal reduction because it matches P1 or I1;
- change the B0/D1 initial condition to reproduce a prior partition.

If a T1 partition unexpectedly matches a completed P1 or I1 partition, exact
post-result partition comparison is permitted only as explicitly labelled
rabbit isolation.

Count equality alone is never sufficient.

## Relationship to S1 spectral controls

S1 is complete before T1 activation.

S1 coefficients, eigenvalues, or collision identities are not T1 inputs.

After a T1 result exists, T1 may be compared with S1 for attribution.

Such comparison must be post-result and explicitly labelled.

T1 does not predeclare a claim that ordered trajectories reconstruct spectra or
vice versa.

## Translation control

Rigid integer translation by the already used Gate 3 vector:

`(+17, +11)`

must preserve every primary T1 reduction.

This includes:

- ordered;
- unordered;
- endpoints;
- terminal;
- all ordered/unordered prefixes;
- first-divergence diagnostics;
- persistence diagnostics.

A translation failure invalidates the affected channel.

## Reflection/equivariance control

### Intrinsic/reflection-equivariant source channels

For a substrate whose frozen initial state and dynamics are
reflection-equivariant, horizontal reflection must preserve:

- every per-time coordinate-free snapshot;
- ordered trajectory;
- unordered trajectory;
- endpoint pair;
- terminal snapshot;
- prefix signatures;
- first-divergence behavior;
- persistence behavior.

### Coordinate-derived B0/D1 source channels

The frozen B0/D1 primary source construction retains its previously established
probe qualification.

For those channels, reflection correctness is tested by exact transport of the
source/initial state through the reflection bijection.

Independent coordinate-derived source reselection is not evidence of intrinsic
reflection behavior.

A temporal result obtained from such a channel remains probe-qualified even if
the temporal aggregation itself is coordinate-free.

T1 must not relabel it as intrinsic.

## Historical #23/#41 family

The retained Gate 1A reflected/reordered pair must be reported explicitly for
every applicable primary reduction.

For intrinsic/reflection-equivariant channels, an unexpected T1 separation of
the exact reflected pair is an audit failure until proven otherwise.

For coordinate-derived B0/D1 source channels, any separation must retain the
existing probe qualification and must not be interpreted as intrinsic temporal
reflection breaking.

T1 does not claim orientation.

Orientation belongs to G3-O1.

## Source-boundary audit

A T1 primary signature may use only:

- the frozen substrate state trajectory;
- the global frozen sample schedule;
- exact substrate-required normalization;
- the frozen coordinate-free per-time spatial reader;
- the declared temporal reduction.

It must not observe:

- coordinates in the final reader;
- source vertex identity;
- vertex order;
- factor order;
- component order;
- structural address;
- AST identity;
- decoded tree identity;
- shape code;
- corpus index;
- serialization identity;
- P1 output;
- I1 output;
- S1 output;
- S2 output;
- H1 output;
- O1 output;
- Gate 4 mutation identity.

Shape code may appear only as evidence metadata used to name collision pairs.

## Determinism requirements

Every T1 corpus result must replay byte-for-byte.

Canonical serialization is required for:

- exact rational values;
- per-time snapshots;
- unordered temporal multisets;
- collision groups;
- pair sets;
- diagnostics.

No iteration-order-dependent output is permitted.

## Corpus order

T1 must be evaluated in exactly this order:

1. Phase 1 — 110 frozen forms;
2. deterministic Phase 1 replay;
3. held-out width-4 — 27 frozen forms;
4. deterministic held-out replay;
5. extended — 137 total forms;
6. deterministic extended replay;
7. formal evidence record and T1 closure.

Scientific interpretation occurs before opening the next corpus.

The held-out result must remain separately visible.

The 137-form extended corpus is a composition control, not a third independent
replication.

## Required evidence

For every substrate/channel and temporal reduction record at minimum:

- protocol identifier;
- frozen substrate identifier;
- frozen parameters;
- normalization rule;
- sample schedule;
- signature count;
- exact collision groups;
- exact collision pairs;
- signature digests;
- matched reduction splits;
- newly introduced pairs;
- D1 null-to-coupled splits and introduced pairs;
- #23/#41 behavior where applicable;
- translation audit;
- reflection/transport audit;
- source-boundary audit;
- source SHA256 digests;
- evidence SHA256 digest.

Also record:

- ordered/unordered prefix growth curves;
- first-divergence distribution and exact relevant pairs;
- persistence-pattern distribution and exact relevant pairs.

## Primary T1 classification rules

### Positive temporal-order result

Temporal ordering receives bounded positive support for a declared channel if:

1. normalized T1-ordered strictly refines normalized T1-unordered;
2. the comparison uses exactly the same six sampled states;
3. introduced collision pairs are zero;
4. source-boundary audits pass;
5. translation/reflection requirements pass;
6. the result replays deterministically.

A Phase 1-only positive result is bounded and unreplicated.

Held-out reproduction is required for replicated status.

### Negative temporal-order result

If normalized ordered and unordered induce the same complete collision
partition, then temporal ordering adds no discrimination on that frozen corpus.

This is a valid negative result.

### Endpoint sufficiency

If normalized endpoints and ordered induce the same complete partition, then
the intermediate sampled states add no discrimination beyond the two declared
endpoints on that corpus.

### Terminal sufficiency

If normalized terminal and ordered induce the same complete partition, then the
full sampled trajectory adds no discrimination beyond the final sampled state
on that corpus.

### Representation-scale artifact

If raw numerator unordered observations distinguish forms that normalized
unordered observations do not, while normalized ordered analysis does not
support the same temporal claim, classify the extra discrimination as
representation-scale information.

Do not call it intrinsic temporal ordering.

## Rabbit watch

Stop normal execution and isolate before opening the next corpus if any of the
following occur:

1. normalized ordered strictly refines normalized unordered by a substantial
   exact partition change;
2. a temporal-order gain appears cleanly under an intrinsic F1 or L1 channel;
3. D1 coupled gains temporal-order distinctions absent from the matched null;
4. the same temporal-order gain appears independently on held-out;
5. a normalized T1 partition unexpectedly equals a previously frozen S1, P1,
   or I1 partition;
6. first-divergence times show a sharp, reproducible family structure not
   explained by the declared static/terminal controls;
7. intermediate states recover distinctions absent from both endpoints and
   terminal observations.

Any rabbit isolation must be read-only with respect to the frozen T1 protocol.

Counts alone never establish partition equivalence.

## False-rabbit conditions

The following are not positive temporal discoveries:

- discrimination caused only by `q^k` numerator scaling;
- different sample schedules across forms;
- post-result time selection;
- geometry-specific time warping;
- coordinate leakage;
- source identity leakage;
- factor/component ordinal leakage;
- orientation leakage;
- a B0/D1 reflected-pair separation already explained by source selection;
- deterministic replay failure;
- mismatch between the states used by ordered and unordered controls.

## Deferred temporal candidates

The pre-result temporal hypothesis also declares possible future studies of:

- relaxation moments/range;
- threshold-derived relaxation times;
- spectral decay factors.

These are not part of T1-v0.

No relaxation threshold is selected here.

No spectral-decay signature is introduced here.

If one of those questions is activated later, it requires a separately frozen
follow-up protocol before its corpus results are observed.

This keeps T1-v0 focused on temporal observation/order attribution.

## O1 boundary

T1 uses coordinate-free per-time spatial observations only.

No oriented state sequence is a T1 primary signature.

Oriented temporal observations, if ever examined, belong exclusively to G3-O1
and must be explicitly labelled diagnostic controls.

O1 remains inactive throughout T1-v0 protocol freeze.

## Gate 4 boundary

T1 does not:

- mutate geometries;
- search adversarial collisions;
- optimize examples;
- generate new corpus forms;
- search for minimal counterexamples in the PETRA corpus.

Those activities belong to later gates.

## Supported interpretation if positive

A valid positive T1 result may support a bounded statement such as:

> Under the frozen PETRA dynamics and frozen coordinate-free spatial reader,
> retaining the declared temporal ordering separates forms that remain
> indistinguishable when the exact same sampled states are exposed only as an
> unordered multiplicity-preserving collection.

The statement must retain any substrate/probe qualification.

## Supported interpretation if negative

A valid negative T1 result may support a bounded statement such as:

> On the frozen PETRA corpus and declared sample schedule, the unordered
> collection of coordinate-free sampled states retains the same discrimination
> partition as the ordered trajectory; temporal ordering therefore adds no
> measured discrimination under this protocol.

Negative results are scientifically valid and must not trigger parameter
changes.

## Non-claims

G3-T1-v0 does not establish:

- physical time;
- spacetime;
- relativity;
- cosmological dynamics;
- continuous-time behavior;
- optimal sample times;
- universal temporal uniqueness;
- graph reconstruction;
- spectral reconstruction;
- orientation recovery;
- robustness to noise;
- adversarial robustness;
- theorem-level temporal reconstruction.

## Completion condition

G3-T1-v0 is complete when:

1. the protocol, implementation, and evidence runner are frozen before corpus
   observation;
2. Phase 1, held-out, and extended are evaluated separately in frozen order;
3. all three corpus artifacts replay byte-for-byte;
4. ordered, unordered, endpoints, and terminal reductions are reported;
5. ordered/unordered prefix curves are reported;
6. first-divergence and persistence diagnostics are reported;
7. matched D1 null/coupled behavior is reported;
8. translation/reflection/source-boundary audits pass or failures are retained
   explicitly;
9. temporal-order attribution is classified separately from probe, spectrum,
   impulse-response, and orientation effects;
10. a human-readable evidence record closes T1 before O1 is activated.
