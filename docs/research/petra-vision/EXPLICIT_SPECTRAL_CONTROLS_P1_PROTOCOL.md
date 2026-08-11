# PETRA VISION Gate 3 — G3-P1 probe-ablation protocol

## Status

Frozen before P1 implementation and before P1 corpus observation.

Protocol identifier:

`petra-vision-explicit-spectral-controls-p1-v0`

G3-P1 follows the completed S0/S1, S2, and H1 controls.

This protocol defines only P1.

I1, T1, and O1 remain inactive.

## Purpose

G3-P1 measures how much of the frozen dynamic discrimination depends on the
choice of initial probe rather than on the operator alone.

The primary causal target is the Gate 2 D1 qualification.

Gate 2 established that the frozen D1 weighted graph is
reflection-equivariant, but its primary 110/110 Phase 1 result used a
coordinate-derived asymmetric minimum probe.

P1 therefore asks:

1. which distinctions survive when the probe is changed;
2. which distinctions specifically require the coordinate-derived minimum
   probe;
3. whether an intrinsic reflection-equivariant probe still exposes an
   incremental D1 coupling effect relative to its matched null;
4. how much discrimination is already present in the initial probe multiset
   before propagation.

P1 is an attribution experiment, not a search for a new perfect classifier.

No probe may be added, removed, rescaled, or tuned after P1 corpus results are
observed.

## P1 applicability

### B0 — applicable

B0 has a frozen single-channel scalar state over occupied-cell graph vertices
and a selected component-wise point probe.

P1 evaluates the frozen B0 operator under the complete declared probe family.

### D1 — applicable and primary causal target

D1 has the same occupied-cell vertex domain and a frozen selected
component-wise point probe.

P1 evaluates both:

- the frozen D1 matched null;
- the frozen D1 coupled operator;

under exactly the same probe for each comparison.

### F1 — not applicable in P1

F1 does not use an externally selected single-channel point probe.

Its frozen initial state is the intrinsic six-channel feature vector attached
to each geometry-derived FGS factor.

Replacing that state with a scalar point probe would change the representation
semantics rather than ablate the frozen probe choice.

No F1 initial-state mutation is introduced by P1.

### L1 — not applicable in P1

L1 does not use a selected point probe.

Its frozen initial scalar field is the binary occupied/empty geometry field
itself.

Replacing the encoded occupancy field by a point impulse, constant field, or
degree field would erase or replace the encoded input rather than ablate the
coordinate-derived probe implicated in the D1 qualification.

No L1 input-field mutation is introduced by P1.

These N/A classifications are part of the frozen P1 scope and must not be
silently changed after corpus observation.

## Frozen substrate dynamics

### B0

Keep unchanged:

- occupied cells as vertices;
- four-neighbor combinatorial Laplacian;
- exact integer Euler numerators;
- denominator 8;
- sample steps 1, 2, 4, 8, 16, 32;
- primary reader: global multiset of state values at every sampled step.

### D1 matched null

Keep unchanged:

- occupied cells as vertices;
- local axial distance-1 edges with weight 2;
- declared distance-2 bridge positions with bridge weight 0;
- exact integer Euler numerators;
- denominator 16;
- sample steps 1, 2, 4, 8, 16, 32;
- primary reader: global multiset of state values at every sampled step.

### D1 coupled

Keep unchanged:

- occupied cells as vertices;
- local axial distance-1 edges with weight 2;
- axial distance-2 bridge edges through one empty midpoint with weight 1;
- exact integer Euler numerators;
- denominator 16;
- sample steps 1, 2, 4, 8, 16, 32;
- primary reader: global multiset of state values at every sampled step.

The D1 null and D1 coupled calculation must differ only in bridge weight.

For every P1 mode they must receive byte-for-byte identical initial-state
tuples.

## Frozen component basis

For B0 point-probe construction, use the frozen connected components of the
four-neighbor occupied-cell graph.

For D1 point-probe construction, use the frozen original four-neighbor
occupied components before distance-2 bridges are added.

This preserves the Gate 2 probe semantics.

## Frozen probe family

Evaluate every declared mode.

### P1-minimum

For every native occupied component, place value 1 at its lexicographically
minimum occupied cell and value 0 at all other vertices.

This is the frozen coordinate-derived baseline probe.

For D1 this must reproduce the existing Gate 2 primary probe exactly.

It is not classified as intrinsic or reflection-equivariant.

### P1-reflected-minimum

This is the actual horizontal-reflection counterpart of P1-minimum.

For geometry G:

1. horizontally reflect G through its own occupied bounding box;
2. construct P1-minimum on the reflected geometry;
3. transport that state back to G through the exact reflection cell
   bijection.

The resulting probe is evaluated on G.

This is a coordinate-derived diagnostic control.

It must not be described as an intrinsic probe.

It is included instead of an independently chosen lexicographic maximum
because the exact transported counterpart gives the cleaner reflection-matched
causal control.

### P1-local-degree

Use one exact integer scalar per occupied vertex equal to its unweighted
four-neighbor occupied-cell degree.

This probe is derived only from the native local occupied graph.

For D1 it explicitly excludes distance-2 bridge edges and bridge weights.

Consequently the D1 matched null and coupled operator receive the exact same
P1-local-degree state.

This probe is:

- coordinate-free;
- vertex-permutation equivariant;
- horizontal-reflection equivariant;
- independent of the D1 bridge coupling being tested.

No tie-breaking or selected vertex identity is used.

### P1-constant

Assign value 1 to every occupied vertex.

This is a spatially uniform negative excitation control.

Because the primary reader preserves multiplicity, the signature may still
retain operator-order / vertex-count information.

Therefore P1-constant is not expected to collapse all forms to one signature.

### P1-zero

Assign value 0 to every occupied vertex.

This is the no-excitation negative control.

Because each sampled state retains its multiplicity, P1-zero may still encode
vertex count.

A non-singleton signature count under P1-zero is therefore not by itself a
protocol failure.

## No probe normalization

Do not normalize probe mass, L1 norm, L2 norm, or amplitude across modes.

The exact integer states above are the protocol.

P1 is a broad probe/initial-condition ablation.

Claims that require a strictly mass-matched impulse-location comparison belong
to G3-I1 and must not be inferred from P1 alone.

## Step-zero probe control

For every geometry and every probe mode, record the coordinate-free initial
probe signature before propagation:

`sorted(probe_state)`

This establishes how much discrimination is present in the probe itself.

The dynamic P1 signature remains the ordered tuple of sampled global state
multisets at steps:

`(1, 2, 4, 8, 16, 32)`.

Evidence must report the step-zero probe partition separately from the dynamic
partition.

A strong dynamic result from P1-local-degree must not be attributed solely to
propagation if the same distinctions are already present in the step-zero
degree multiset.

## Matched D1 causal comparison

For every corpus and every probe mode, compare:

`D1 matched null -> D1 coupled`

while holding fixed:

- geometry;
- vertex set;
- local edges;
- probe tuple;
- denominator;
- sample schedule;
- reader.

Report:

- distinct-signature delta;
- collision pairs split by coupling;
- collision pairs introduced by coupling;
- exact collision groups.

This is the primary P1 causal comparison.

## B0 probe sensitivity comparison

For B0 report every probe mode separately.

Also compare each non-baseline probe partition against P1-minimum.

These comparisons measure sensitivity of the frozen B0 dynamic reader to probe
choice.

Partition relations may be incomparable.

No monotonic refinement relation is assumed between different probes.

## Historical #23/#41 control

The retained reflected/reordered #23/#41 family is a mandatory explicit
control.

Record its status for:

- B0 under every probe;
- D1 matched null under every probe;
- D1 coupled under every probe.

P1-minimum is allowed to reproduce the known D1 split.

P1-reflected-minimum is a coordinate-derived diagnostic and is also allowed to
separate the pair.

P1-local-degree, P1-constant, and P1-zero are reflection-equivariant probe
families.

For these three modes, separation of an exact reflected pair by either B0,
D1 null, or D1 coupled is an implementation/source-boundary failure and must
stop corpus progression.

In particular, a D1-local-degree separation of #23/#41 would contradict the
declared intrinsic reflection-equivariant control.

## Reflection audit

For every observed geometry, build its exact horizontal reflection.

For each of:

- P1-local-degree;
- P1-constant;
- P1-zero;

the coordinate-free dynamic signature must be identical between the original
and reflected geometry for the same substrate/operator.

For P1-minimum and P1-reflected-minimum, require the transported-pair
identities:

- signature(G, minimum) equals
  signature(reflect(G), reflected-minimum);
- signature(G, reflected-minimum) equals
  signature(reflect(G), minimum).

Failure is a probe-transport or equivariance bug, not a scientific result.

## Translation audit

Freeze translation vector:

`(+17, +11)`.

Translate every occupied cell by that vector without changing relative
geometry.

Every P1 probe mode and every coordinate-free dynamic signature must remain
identical after translation.

Failure is a coordinate leakage or implementation error.

## Reader boundary

The primary P1 reader may observe only:

- frozen substrate/operator identity;
- exact frozen operator dynamics;
- exact declared initial state;
- global state-value multiset at the frozen sample steps.

The P1-local-degree constructor may additionally observe only native
four-neighbor adjacency required to derive local degree.

The P1-reflected-minimum constructor may use coordinates solely to construct
the explicitly labelled reflected diagnostic probe.

The primary reader must not observe:

- vertex identity;
- vertex order;
- raw coordinates;
- bounding-box position;
- factor order;
- component ordinal;
- AST/tree identity;
- structural address;
- shape serialization;
- shape code;
- corpus index;
- S1/S2/H1 signatures;
- future I1/T1/O1 results.

Shape code may be used only as evidence metadata for collision reporting.

## Corpus order

Observe corpora separately and strictly in this order:

1. Phase 1 — 110 forms;
2. held-out width-4 — 27 forms;
3. extended frozen domain — 137 forms.

Phase 1 must be interpreted before held-out is executed.

Held-out must be interpreted before extended is executed.

The extended domain is the union of the previous two partitions and is not an
independent third replication.

## Required measurements

For B0 and for D1 null/coupled, for every declared probe mode record:

- probe protocol name;
- initial-state mass;
- step-zero distinct signatures;
- step-zero exact collision groups;
- dynamic distinct signatures;
- dynamic exact collision groups;
- dynamic collision-pair count;
- comparison against P1-minimum where applicable;
- D1 null-to-coupled collision splits and introduced collisions;
- #23/#41 behavior;
- deterministic replay;
- translation audit;
- reflection/transport audit;
- source-boundary audit;
- source SHA256;
- evidence SHA256.

Evidence must retain Phase 1, held-out, and extended results separately.

## Interpretation classes

### Probe-dependent positive

A distinction present under P1-minimum but absent under intrinsic
P1-local-degree is evidence that the distinction depends on the selected
coordinate-derived excitation under the tested bounded protocol.

### Intrinsic-probe coupling positive

If D1 coupled splits collision pairs relative to its matched null under
P1-local-degree, with zero source-boundary/reflection violations, this is
bounded evidence that geometry-derived coupling exposes additional information
under an intrinsic equivariant excitation.

This would strengthen D1 beyond its Gate 2 coordinate-derived probe
qualification.

### Probe-static effect

If a distinction is already present in the step-zero probe partition, do not
attribute that distinction solely to propagation.

### Negative control

P1-zero and P1-constant may retain vertex-count information because state
multiplicity is part of the reader.

Their scientific role is to determine what remains without localized
excitation, not to force a one-class result.

## Rabbit-watch conditions

A potential P1 rabbit requiring immediate isolation and verification includes:

- D1 coupled gains reproducible collision splits over its matched null under
  P1-local-degree;
- an intrinsic P1-local-degree result retains unexpectedly high dynamic
  discrimination beyond its own step-zero partition;
- a strong intrinsic-probe effect appears in Phase 1 and independently
  replicates on held-out;
- a sharp qualitative difference between B0 and D1 survives all matched
  intrinsic-probe controls.

The following are false rabbits and require immediate audit:

- P1-local-degree separates an exact horizontal-reflection pair;
- D1 null and coupled receive different probe tuples in a matched comparison;
- source coordinates reach the primary reader;
- probe parameters are changed after corpus observation;
- an apparent dynamic gain is actually present unchanged at step zero;
- a later Gate 3 family is mixed into P1.

## Non-claims

G3-P1 does not establish:

- universal probe independence;
- universal injectivity;
- spectral uniqueness;
- intrinsic orientation recovery;
- mass-matched impulse-location attribution;
- impulse-response attribution;
- temporal-order attribution;
- physical excitation or physical time;
- robustness outside the frozen domain.

A positive P1-local-degree result would remain bounded evidence for the frozen
PETRA geometry/operator family.

## Gate boundary

Freeze this protocol before implementing P1 or observing any P1 corpus result.

After protocol freeze:

1. implement the five exact probe modes without modifying frozen B0/D1 cores;
2. add focused structural, reflection, translation, and matched-probe tests;
3. freeze a deterministic one-corpus evidence runner;
4. observe Phase 1 only;
5. interpret Phase 1 before held-out;
6. replay deterministically;
7. observe held-out only after Phase 1 interpretation;
8. interpret held-out before extended;
9. observe and replay extended;
10. write the P1 evidence record and close P1 formally.

G3-I1, G3-T1, and G3-O1 remain inactive throughout P1.
