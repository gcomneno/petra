# PETRA VISION Global Geometric Coupling — Contract v0

## Status

Gate 2 — Global geometric coupling.

Issue: #198.

Status: contract frozen before implementation or corpus discrimination results.

This document defines the experimental boundary for Gate 2. It is a
research-only contract. It is not a production API, a physical propagation
claim, a decoder, or a uniqueness theorem.

## Research question

Can a coupling derived only from PETRA VISION geometry recover global
information that the frozen disconnected occupied-cell graph loses, while the
result remains observable through a coordinate-free reader and matched controls
without exposing coordinate or structural identity metadata to that reader?

The target is incremental information attributable to a declared coupling, not
a target score such as 110/110 or 137/137.

## Frozen dependencies

Gate 2 starts from completed Gates 0 and 1.

The following results remain frozen:

- Gate 0 canonical geometry and bounded corpora;
- graph-Laplacian v1 as the immutable occupied-cell baseline;
- Gate 1A coordinate-free quotient characterization;
- the structural reflected/reordered collision derived from Phase 1 #23/#41;
- Gate 1B native Structural Geometric Factorization (FGS).

Gate 2 must not repair or silently redefine those earlier protocols.

## Frozen corpus partitions

Results must remain separately reported for:

1. Phase 1: 110 forms;
2. held-out width 4: 27 forms;
3. extended domain: 137 forms.

The held-out 27-form partition must not disappear into the extended aggregate.

## Candidate construction matrix

### G2-B0 — frozen occupied-cell v1

Purpose: immutable baseline.

Expected replay:

- Phase 1 coordinate-free result: 109/110;
- held-out width-4 result: 27/27;
- extended result: 136/137;
- sole known bounded collision: the reflected/reordered family derived from
  Phase 1 #23/#41.

No implementation or parameter of G2-B0 may be changed to improve Gate 2.

### G2-C0 — component-null representation

Represent the disconnected occupied components without introducing
inter-component geometric coupling.

Purpose: negative control for representation changes that preserve the
component-order quotient.

### G2-F0 — FGS units without global coupling

Use native FGS-derived geometric regions as units but introduce no global
interaction between them.

The reader must not receive factor ordinal, left/right position, structural
address, decoded AST labels, or equivalent identity information.

Purpose: separate factor-boundary information from coupling information.

### G2-D1 — weak distance-dependent geometric coupling

This is the first implementation target.

It extends the occupied-cell graph by deterministic weak geometric bridges
across exactly one empty axial lattice cell.

The complete D1 protocol is frozen below before discrimination results are
observed.

### G2-F1 — FGS-informed geometric coupling

Use FGS regions as candidate dynamic regions while deriving interactions from
geometry rather than recovered structural labels.

FGS may define geometry-derived regions. It may not be converted into an
ordinary labelled-tree reader.

### G2-L1 — full lattice

Treat the declared bounded ambient lattice, including empty sites, as the
propagation medium under a separately frozen boundary rule.

### G2-E1 — occupied/empty field

Represent occupied and empty sites as declared medium states and evolve them
under a separately frozen local rule.

## Unit versus coupling boundary

FGS is an admissible bounded geometric research object after Gate 1B, but FGS
alone is not evidence for global coupling.

No Gate 2 primary reader may receive:

- original x/y coordinates;
- factor ordinal or sibling index;
- left/right labels;
- structural addresses;
- VisionShape;
- Terminal or OrderedGroup identity;
- decoded AST nodes;
- shape codes;
- serialization;
- corpus indices;
- filenames;
- object identity;
- annotated factor boundaries not derived inside the declared construction.

Coordinates may determine physical/geometric construction, distance, adjacency,
weights, probe placement, or boundary membership. They may not be emitted to
the final coordinate-free reader as identity metadata.

## Common conceptual boundary

Every positive construction follows:

```text
canonical geometry
    -> declared geometric construction
    -> declared propagation
    -> coordinate-free observation
```

Construction, propagation, and observation must remain separately inspectable.

## G2-D1 input boundary

The D1 constructor accepts an exact OrthogonalGeometry.

Evidence-corpus inputs are canonical geometries.

Translated copies may be supplied only for translation controls.

The D1 dynamic core must not import or decode VisionShape, structural
addresses, serialization, corpus metadata, or FGS.

FGS is intentionally excluded from D1 so that D1 tests pure geometric coupling
before factor-informed coupling is introduced.

## G2-D1 vertices

D1 uses exactly the occupied cells as vertices.

No empty cell becomes a dynamic vertex in D1.

Therefore D1 changes coupling only; it does not yet test a full ambient medium.

## G2-D1 edge classes

For distinct occupied cells u=(x1,y1) and v=(x2,y2), define axial distance

```text
d_axis(u, v) =
    |x1-x2| + |y1-y2|
```

only when either x1=x2 or y1=y2.

Two edge classes are permitted.

### Local edge

A local edge exists when:

- the cells are axially aligned; and
- d_axis(u,v) = 1.

Its integer weight is:

```text
w_local = 2
```

This preserves the existing four-neighbor occupied-cell adjacency as the
strong interaction.

### Clearance bridge

A weak bridge exists when:

- the cells are axially aligned;
- d_axis(u,v) = 2; and
- the unique lattice midpoint between them is empty.

Its integer weight is:

```text
w_bridge = 1
```

Thus D1 crosses exactly one empty axial lattice cell.

No diagonal edge is allowed.

No bridge at distance greater than 2 is allowed.

No distance-2 shortcut is added when the midpoint is occupied.

The 2:1 local-to-bridge weight ratio is frozen before corpus evaluation and
must not be tuned to improve discrimination.

## Why radius 2 is frozen

The existing occupied-cell graph fails to communicate through one-cell
clearance regions in the canonical nested-frame geometry.

D1 therefore tests the minimal axial extension that can cross exactly one such
empty site while retaining occupied cells as the only dynamic vertices.

This is a hypothesis about a geometric construction, not a claim of physical
correctness.

## G2-D1 matched null

Every D1 result must be compared with a matched null construction.

The matched null has:

- the same occupied vertices;
- the same local edges;
- local weight 2;
- bridge weight 0;
- the same probe;
- the same Euler denominator;
- the same sampling schedule;
- the same reader.

Only the clearance bridges differ.

This control isolates the incremental effect of cross-clearance coupling from
the effects of weighted local dynamics or changed integration denominator.

## Frozen probe

Probe selection remains matched to graph-Laplacian v1.

First derive the connected components of the original four-neighbor occupied
graph, before D1 bridges are added.

Place one unit impulse at the lexicographically minimum occupied vertex of each
such original component.

The identical initial state is used for D1 and its matched null.

This probe is deliberately asymmetric and remains a declared protocol choice.
Gate 2 does not reinterpret that asymmetry as a universal property.

Probe ablation belongs to Gate 3 unless a Gate 2 falsification requires an
explicit matched control.

## Weighted Laplacian

For weighted adjacency W, define:

```text
L_w = D_w - W
```

where D_w contains the integer weighted degree of each vertex.

D1 uses exact integer weights only.

## Frozen Euler propagation

For current numerator state x[k], one exact step is:

```text
x[k+1] = 16*x[k] - L_w*x[k]
```

The common Euler denominator is therefore:

```text
q = 16
```

This value is fixed analytically rather than by corpus discrimination.

Under the declared D1 edge rule, an occupied vertex can have at most four local
neighbors of weight 2 and four axial distance-2 neighbors of weight 1.

Therefore:

```text
maximum possible weighted degree <= 4*2 + 4*1 = 12 < 16
```

No corpus scan is needed to select q.

The matched null also uses q=16.

## Frozen sample schedule

Use the graph-Laplacian v1 sample schedule unchanged:

```text
1, 2, 4, 8, 16, 32
```

No additional sample time may be selected after observing discrimination
results and then included in the primary D1 claim.

## Primary coordinate-free reader

At every sampled step, sort the complete state values and record only the
resulting multiset.

The primary signature is the ordered sequence of those sampled multisets.

The reader receives no cell coordinates, vertex ordering, component ordering,
factor ordering, or structural labels.

## Static and null observations

For every geometry record:

- the step-0 global multiset of probe values;
- D1 matched-null dynamic signature;
- D1 coupled dynamic signature;
- declared construction statistics.

A discrimination gain is attributed to D1 only relative to the matched-null
dynamic signature under the same probe, q, sample schedule, and reader.

Static construction statistics are controls and are not substitutes for a
dynamic coordinate-free result.

## Frozen baseline replay

Before interpreting D1, the evidence tool must reproduce G2-B0 from the
existing frozen implementation rather than copy or modify it.

Expected bounded results remain:

- 109/110 on Phase 1;
- 27/27 on held-out width 4;
- 136/137 on the extended domain.

Any divergence must stop interpretation until explained.

## Required D1 controls

At minimum D1 evidence must include:

1. frozen G2-B0 replay;
2. D1 matched null;
3. step-0 coordinate-free probe multiset;
4. deterministic duplicate replay;
5. translation control;
6. exact retention and classification of collision groups;
7. explicit replay of the Gate 1A reflected/reordered collision family;
8. source/AST identity-channel audit;
9. construction statistics, including local-edge and bridge-edge counts;
10. Phase 1, held-out, and extended partitions reported separately.

## Translation control

A fixed translation of every occupied coordinate must leave:

- local edge structure;
- clearance-bridge structure;
- probe-relative state;
- matched-null signature;
- D1 coordinate-free signature

unchanged up to the declared coordinate-free observation.

The constructor must not depend on absolute origin.

## Reflection and component-reordering controls

Gate 1A established that the frozen coordinate-free v1 reader quotients away
disconnected-component spatial ordering.

D1 must retain the corresponding reflected/reordering cases and report whether
cross-clearance coupling:

- preserves those equivalences;
- splits some of them; or
- introduces new collisions.

A split is not automatically a success: it must be absent from the matched null
and must not arise from coordinates leaking into the reader.

## Parameter discipline

Primary D1 parameters are frozen by this contract:

- vertex set: occupied cells;
- local support: axial distance 1;
- local weight: 2;
- bridge support: axial distance 2 with empty midpoint;
- bridge weight: 1;
- diagonal coupling: absent;
- longer-range coupling: absent;
- probe: minimum vertex of every original occupied component;
- Euler denominator: 16;
- sample steps: 1,2,4,8,16,32;
- reader: global coordinate-free state multiset.

If D1 is negative, these parameters remain negative evidence.

A revised parameter family requires a new protocol identifier and explicit
separation from D1. It must not overwrite the D1 result.

## Protocol identifier

The primary protocol identifier is:

```text
petra-vision-global-geometric-coupling-distance2-v0
```

The matched null must be explicitly identified as the null member of the same
frozen protocol.

## Success criteria for D1

D1 is positive only if all of the following hold:

- construction is deterministic;
- translation control passes;
- no undeclared identity channel is present;
- frozen G2-B0 replay remains unchanged;
- D1 and its matched null use identical non-coupling parameters;
- at least one reproducible coordinate-free distinction is added by D1 relative
  to its matched null;
- all collision groups are retained and reported;
- Phase 1, held-out, and extended results replay deterministically.

Perfect corpus injectivity is not required.

## D1 falsification criteria

Record D1 as negative or invalid if:

- D1 and its matched null have identical coordinate-free results everywhere;
- an apparent gain is already present in the matched null;
- coordinates or positional labels reach the reader;
- bridge construction depends on corpus identity or structural metadata;
- parameters are changed after inspecting discrimination results;
- the frozen B0 baseline changes;
- replay is non-deterministic;
- collisions are suppressed rather than retained;
- the implementation silently normalizes malformed or translated inputs in a
  way that changes the declared construction.

A negative D1 result remains part of Gate 2 evidence.

## Relationship to G2-F1

D1 intentionally excludes FGS.

Only after D1 is frozen and evaluated may Gate 2 introduce FGS-informed
coupling.

This ordering separates:

- geometric coupling across empty clearance;
- factor-boundary information;
- factor-informed coupling.

## Relationship to G2-L1 and G2-E1

D1 retains occupied cells as the only dynamic vertices.

Therefore a negative D1 result does not falsify full-lattice or occupied/empty
field propagation.

Those are distinct constructions and require their own frozen contracts.

## Relationship to Gate 3

Gate 2 asks which declared global coupling constructions add reproducible
information.

Gate 2 does not attribute a positive or negative D1 result to:

- eigenvalues;
- spectral uniqueness;
- isospectrality;
- heat traces;
- probe optimality;
- sample-time optimality;
- per-component spectra;
- per-factor spectra.

Those questions belong to Gate 3 — Explicit spectral controls.

## Non-claims

Gate 2 and D1 do not establish:

- a physical propagation law;
- complete dynamic decoding;
- theorem-level injectivity;
- spectral uniqueness;
- robustness to noise or damage;
- independent reproduction;
- multiscale semantics;
- authenticated recognition;
- cryptographic security;
- production readiness.

## Gate 2 completion rule

Gate 2 is complete only after enough of the declared construction matrix has
been evaluated to decide which forms of global geometric coupling, if any,
provide reproducible incremental information beyond matched controls.

Positive and negative candidates must both remain documented.

## G2-F0 frozen protocol

G2-F0 is the factor-boundary null construction evaluated before G2-F1.

Its purpose is to measure information supplied by native FGS factor boundaries
without any interaction between factors.

### Input boundary

F0 accepts canonical OrthogonalGeometry.

Immediate root factors are obtained only through the frozen native Gate 1B
native_fgs operation.

F0 must not decode VisionShape or use structural addresses, shape codes,
serialization, corpus indices, filenames, object identity, or annotated factor
metadata.

### Factor scope

F0 uses exactly the immediate root factors returned by native_fgs.

It does not recursively flatten the complete factor tree into one observation.

Terminal geometry has no immediate factors and therefore emits the empty factor
multiset.

### Per-factor observation

Every immediate factor is evaluated independently with the frozen
graph-Laplacian v1 dynamic protocol.

For each factor use:

- its occupied-cell four-neighbor graph;
- the frozen v1 minimum-component probe;
- Euler denominator 8;
- sample steps 1, 2, 4, 8, 16, 32;
- the coordinate-free global_multiset dynamic reader.

The factor geometry is canonical and no factor receives information from any
other factor.

### Final F0 reader

The final F0 signature is the sorted multiset of the independent per-factor
global_multiset signatures.

Therefore the final reader preserves:

- factor multiplicity;
- per-factor coordinate-free dynamic content;
- number of immediate factors.

It deliberately discards:

- factor ordinal;
- left/right placement;
- sibling order;
- root-bay index;
- original factor coordinates;
- inter-factor distance;
- structural addresses.

### No-coupling rule

F0 has no inter-factor graph edges, shared state, propagation, averaging,
message passing, synchronization, or other cross-factor interaction.

Any later F1 gain must be measured relative to this F0 boundary.

### Known reflected-pair control

For the retained Gate 1A pair

G(G(G(T)),G(T,T))

and

G(G(T,T),G(G(T)))

the immediate root factors are the same two factors in opposite order.

Because F0 deliberately discards factor order, this pair must remain
indistinguishable under F0.

If F0 separates this pair, the implementation violates the declared unordered
factor-reader boundary.

### Multiplicity

Repeated equal factors remain repeated entries in the final multiset.

F0 must not deduplicate equal factor observations.

### Frozen protocol identifier

The F0 protocol identifier is:

petra-vision-global-geometric-coupling-fgs-null-v0

### F0 success criterion

F0 is a control, not a candidate required to improve corpus discrimination.

A valid F0 result requires:

- deterministic native FGS extraction;
- frozen v1 per-factor dynamics;
- exact factor multiplicity;
- factor order removed before final observation;
- no inter-factor coupling;
- no hidden structural or coordinate identity channel;
- deterministic replay.

The scientifically expected role of F0 is to quantify what factor boundaries
alone contribute before G2-F1 introduces factor-informed coupling.

### F0 falsification criteria

F0 is invalid if:

- factor order reaches the final reader;
- factor ordinal or original coordinates reach the reader;
- factors exchange state or messages;
- native FGS is replaced by decoded structural metadata;
- equal repeated factors are deduplicated;
- the retained reflected/reordered pair is separated solely because its two
  immediate factors are presented in opposite order;
- frozen v1 per-factor dynamics are modified to improve discrimination.

A negative discrimination result is not a failure of F0. It is valid control
evidence.

### F0 matched observation controls

Before corpus discrimination is evaluated, two labelled controls are frozen.

#### Static factor-profile control

For every immediate FGS factor, derive the frozen v1 coordinate-free static
graph profile:

- occupied vertex count;
- edge count;
- connected-component count;
- isolated-vertex count;
- component cycle-rank multiset;
- maximum degree.

The final static control is the unordered multiplicity-preserving multiset of
those per-factor profiles.

This control contains no propagation.

A dynamic F0 distinction must not automatically be attributed to propagation
when the same distinction already exists in this static factor-profile control.

#### Ordered-factor diagnostic control

Record the same per-factor dynamic signatures in the native FGS order before
the final F0 sorting operation.

This ordered observation is a labelled diagnostic control only.

It is not admissible as primary coordinate-free F0 evidence because it retains
root factor order.

Its purpose is to show explicitly what information is removed by the final
unordered F0 reader.

No result from the ordered control may be used to upgrade F0 discrimination.

## G2-F1 frozen protocol

G2-F1 is the first factor-informed global coupling construction.

It is evaluated only after G2-F0 has established the factor-boundary null.

### Research question

Can geometry-derived proximity among immediate native FGS factor occurrences
add reproducible information beyond factor-only controls while preserving a
coordinate-free final reader?

### Input boundary

F1 accepts exact canonical OrthogonalGeometry.

Immediate factors are obtained only from frozen Gate 1B native_fgs.

No VisionShape, decoded AST, structural address, shape code, serialization,
corpus index, filename, or object identity is permitted in the F1 dynamic core.

### Factor nodes

Every immediate root factor is one F1 node.

Terminal geometry therefore has zero F1 nodes.

A one-factor geometry has one node and no inter-factor edge.

Factor multiplicity is preserved.

### Geometric occurrences

Native FGS factors are canonical normalized geometries.

For F1 only, their source occurrences are reconstructed geometrically using
the same frozen FGS recomposition grammar:

- root height is max factor height plus 4;
- first left boundary is x=0;
- factor x offset is left boundary plus 2;
- factor y offset is root height minus factor height minus 2;
- next boundary follows the frozen factor width recurrence.

The reconstructed occurrence union must agree with the payload placement of
the source geometry under exact FGS recomposition.

Native FGS order may be used internally to reconstruct the geometry that
native_fgs itself extracted.

That ordinal must not reach the final reader.

### Factor distance

For two distinct factor occurrences i and j define d(i,j) as the minimum
Manhattan distance between any occupied cell of occurrence i and any occupied
cell of occurrence j.

Only positive finite distances are valid.

### Factor proximity graph

F1 uses the complete undirected graph on immediate factor nodes.

For every pair i != j, the exact coupling weight is:

w(i,j) = 1 / d(i,j)

using exact rational arithmetic.

There is no distance cutoff, radius tuning, nearest-neighbor selection, or
post-result edge pruning.

The inverse-distance law is frozen before corpus evaluation.

### Intrinsic factor feature vector

Every factor starts with the following fixed six-dimensional integer vector
derived only from the frozen v1 graph profile of that canonical factor:

1. occupied vertex count;
2. occupied four-neighbor edge count;
3. connected-component count;
4. isolated-vertex count;
5. total component cycle rank;
6. maximum degree.

The total component cycle rank is the sum of the frozen v1
component_cycle_ranks tuple.

No coordinate, factor index, sibling order, or shape code is part of this
initial state.

### Matched F1 null

The matched null uses:

- the identical FGS factors;
- the identical reconstructed occurrences;
- the identical intrinsic factor feature vectors;
- the identical sample schedule;
- the identical coordinate-free reader;

but all inter-factor weights are zero.

Thus the null propagation is the identity.

### Exact factor propagation

Each feature channel evolves independently.

For factor i and one scalar feature channel x:

x_i(k+1) =
    (x_i(k) + sum_j w(i,j) * x_j(k))
    / (1 + sum_j w(i,j))

All arithmetic is exact Fraction arithmetic.

The rule is a deterministic weighted averaging process.

It introduces no orientation label and requires no Euler stability parameter.

### Frozen sample schedule

Use steps:

1, 2, 4, 8, 16, 32.

This schedule is frozen before F1 corpus results.

### Coordinate-free F1 reader

At each sampled step:

- construct the six-channel state vector of every factor;
- sort the complete factor-state vectors;
- record only that multiset.

The final F1 signature is the sequence of these sampled multisets.

The final reader receives no factor ordinal, original coordinate, left/right
position, adjacency-list index, or structural address.

### F0 comparison

F0 remains independently frozen.

F1 must report separately:

- F0 unordered dynamic signature;
- F1 matched-null signature;
- F1 coupled proximity signature.

In addition, a predeclared joint comparison is permitted:

- joint null = (F0 unordered dynamic, F1 matched null);
- joint coupled = (F0 unordered dynamic, F1 coupled).

The joint comparison measures whether proximity coupling adds distinctions
beyond the already available F0 factor-only evidence.

It must not be introduced or altered after corpus results are seen.

### Reflection control

The F1 construction is intended to be reflection-equivariant.

For the retained exact horizontal-reflection pair

G(G(G(T)),G(T,T))

and

G(G(T,T),G(G(T)))

the following are frozen expectations:

- factor proximity graphs are isomorphic under reflection;
- intrinsic factor features are transported by that isomorphism;
- matched-null signatures collide;
- F1 coupled coordinate-free signatures collide;
- joint F0+F1 signatures collide.

Separating this pair would require an audit before any positive interpretation.

It must not be presented as intrinsic reflection breaking.

### Ordered diagnostic

An ordered factor-state trajectory may be recorded only as a labelled
diagnostic.

It is not admissible as primary F1 evidence.

### F1 success criterion

F1 is positive only if the coupled proximity construction adds reproducible
distinctions relative to its matched null and the effect survives the declared
identity/source-boundary audits.

For incremental value beyond factor-only evidence, the predeclared joint
coupled signature must also be compared with the predeclared joint null.

Perfect corpus injectivity is not required.

### F1 negative result

F1 remains valid negative evidence if geometric proximity adds no distinction
beyond its null or beyond F0.

Parameters must not be changed to force a positive result.

### F1 falsification criteria

F1 is invalid if:

- factor ordinal or left/right position reaches the final reader;
- source coordinates are emitted as reader metadata;
- structural AST identity is used;
- proximity weights depend on corpus identity;
- the inverse-distance law is changed after seeing results;
- factor feature channels are changed after seeing results;
- the sample schedule is changed after seeing results;
- the reflected pair is separated without a causal audit;
- exact deterministic replay fails.

### Protocol identifier

The frozen primary protocol identifier is:

petra-vision-global-geometric-coupling-fgs-proximity-v0

## G2-L1 frozen protocol

G2-L1 tests global propagation through a uniform full lattice.

It is independent of FGS.

### Research question

Can a uniform lattice containing both occupied and empty geometric sites make
global layout dynamically observable through a coordinate-free reader beyond a
matched no-propagation control?

### Input boundary

L1 accepts exact OrthogonalGeometry.

The dynamic core must not import VisionShape, decoded AST nodes, FGS, shape
codes, structural addresses, serialization, corpus indices, filenames, or
object identity.

Translated geometry is permitted only as a translation control.

### Lattice domain

For source occupied cells define:

- xmin = minimum occupied x;
- xmax = maximum occupied x;
- ymin = minimum occupied y;
- ymax = maximum occupied y.

The L1 vertex set is every integer lattice site in the exact minimal
axis-aligned bounding rectangle:

xmin <= x <= xmax
ymin <= y <= ymax

No external padding is added.

The domain is derived from the geometry rather than from an absolute origin.

### Lattice adjacency

Every lattice site is connected only to orthogonally adjacent lattice sites
inside the bounding rectangle.

Every such edge has integer weight 1.

There are:

- no diagonal edges;
- no wraparound edges;
- no long-range edges;
- no occupancy-dependent edge weights.

The medium is uniform.

### Initial field

The initial scalar field is the occupancy indicator:

- occupied source cell -> 1;
- empty lattice cell -> 0.

Occupancy affects only this initial state.

It does not alter lattice adjacency, edge weights, propagation coefficients, or
the final reader.

### Matched L1 null

The matched null uses:

- the identical lattice domain;
- the identical vertex ordering internally;
- the identical occupancy-indicator initial field;
- the identical Euler denominator;
- the identical sample schedule;
- the identical coordinate-free reader;

but every lattice edge weight is zero.

Thus the null preserves the static occupied/empty field but provides no spatial
communication.

### Exact propagation

L1 uses the combinatorial Laplacian of the uniform four-neighbor lattice.

For exact integer numerator state x:

x[k+1] = 8*x[k] - L*x[k]

The frozen Euler denominator is:

8

A lattice vertex has degree at most 4, therefore:

maximum degree <= 4 < 8

The denominator is fixed analytically before corpus evaluation.

### Frozen sample schedule

Use:

1, 2, 4, 8, 16, 32

No sample time may be selected after observing discrimination results and added
to the primary L1 claim.

### Primary coordinate-free reader

At every sampled step, sort the complete scalar state over all lattice sites.

The L1 signature is the sequence of those global state multisets.

The reader receives no:

- lattice coordinates;
- vertex ordering;
- row/column labels;
- width/height orientation label;
- occupied-cell identity;
- structural metadata.

### Static control

Record the step-0 global state multiset separately.

This static multiset contains only the counts of occupied and empty lattice
sites.

A dynamic L1 gain must be reported relative to the matched null, not merely
relative to a different domain size.

### Translation control

Translating all occupied coordinates by a fixed integer offset must leave the
L1 null and coupled coordinate-free signatures unchanged.

### Reflection control

The L1 construction is reflection-equivariant.

For the retained Gate 1A exact horizontal-reflection pair:

G(G(G(T)),G(T,T))

and

G(G(T,T),G(G(T)))

the frozen expectation is:

- matched-null signatures collide;
- coupled L1 signatures collide.

Separating that pair requires an audit before interpretation and must not be
presented as intrinsic reflection breaking.

### Relationship to G2-E1

L1 uses a uniform medium.

Occupied and empty sites differ only in the initial field value.

G2-E1, if evaluated later, may assign different declared medium properties to
occupied and empty sites.

Therefore L1 and E1 are distinct hypotheses and must remain separate.

### L1 success criterion

L1 is positive if uniform lattice propagation adds reproducible distinctions
relative to its matched no-propagation null while:

- preserving the coordinate-free reader boundary;
- passing translation and reflection controls;
- introducing no hidden identity channel;
- replaying deterministically.

Perfect corpus injectivity is not required.

### L1 negative result

L1 remains valid evidence if the uniform lattice adds no distinctions beyond
its null.

Parameters must not be changed to force a positive result.

### L1 falsification criteria

L1 is invalid if:

- coordinates reach the final reader;
- occupancy changes medium weights or adjacency;
- padding is changed after corpus results;
- diagonal, wraparound, or long-range edges are introduced;
- the denominator or sample schedule is tuned after results;
- structural identity metadata is used;
- the reflected pair is separated without causal audit;
- deterministic replay or translation control fails.

### Protocol identifier

The frozen primary L1 protocol identifier is:

petra-vision-global-geometric-coupling-full-lattice-v0

## G2-E1 frozen protocol

G2-E1 tests an occupancy-aware heterogeneous propagation medium on the same
minimal full-lattice domain used conceptually by G2-L1.

It is independent of FGS.

### Research question

Does a deterministic material distinction between occupied and empty lattice
sites add reproducible coordinate-free information beyond a matched uniform
full-lattice propagation process?

### Input boundary

E1 accepts exact OrthogonalGeometry.

The dynamic core must not import VisionShape, decoded AST nodes, native FGS,
shape codes, structural addresses, serialization, corpus indices, filenames,
or object identity.

### Lattice domain

The vertex set is every integer site in the exact minimal axis-aligned bounding
rectangle of the occupied geometry.

No external padding is added.

The domain definition is identical in meaning to G2-L1.

### Fixed material label

Every lattice vertex v has a frozen binary material label:

o(v) = 1 if v is an occupied source cell
o(v) = 0 otherwise

This material label is fixed throughout propagation.

It is distinct from the evolving scalar state even though both use the same
binary occupancy pattern at step 0.

### E1 heterogeneous edge law

Every orthogonal neighboring pair u,v inside the lattice receives the symmetric
integer conductance

w(u,v) = 1 + o(u) + o(v)

Therefore:

- empty-empty edge: weight 1;
- occupied-empty edge: weight 2;
- occupied-occupied edge: weight 3.

This rule is frozen before corpus evaluation.

There is:

- no learned parameter;
- no distance tuning;
- no orientation label;
- no diagonal edge;
- no wraparound;
- no long-range edge.

### Matched uniform-medium control

The primary E1 matched control uses:

- the identical lattice vertices;
- the identical edge locations;
- the identical initial state;
- the identical denominator;
- the identical sample schedule;
- the identical coordinate-free reader;

but sets every existing lattice-edge weight to 1.

Thus heterogeneous versus matched-uniform differs only in the declared
occupancy-dependent conductance law.

Frozen G2-L1 is reported separately because its Euler denominator is 8, whereas
the causal E1 matched comparison uses denominator 16 for both arms.

### Initial scalar field

The evolving scalar state begins as:

x_v(0) = o(v)

Therefore:

- occupied -> 1;
- empty -> 0.

No coordinate reaches the final reader.

### Exact weighted propagation

E1 uses the weighted combinatorial Laplacian.

For exact integer numerator state x:

x[k+1] = 16*x[k] - L_w*x[k]

The frozen Euler denominator is 16.

Every lattice vertex has at most four neighbors and each edge has weight at
most 3, hence:

maximum weighted degree <= 12 < 16

The bound and denominator are fixed analytically before corpus evaluation.

### Frozen sample schedule

Use steps:

1, 2, 4, 8, 16, 32.

No sample time may be selected after corpus results and added to the primary
claim.

### Primary coordinate-free reader

At each sampled step, sort the complete scalar state over all lattice vertices.

The E1 signature is the sequence of these state multisets.

The reader receives no:

- coordinates;
- vertex ordering;
- row or column labels;
- orientation labels;
- structural metadata;
- material-location ordering.

### Static heterogeneous-medium diagnostic

Before dynamic corpus results, the following labelled diagnostic is frozen.

For every lattice vertex record the pair:

(o(v), weighted_degree(v))

and sort the complete set of vertex pairs.

Also record the global edge-weight histogram for weights 1, 2, and 3.

These static diagnostics are coordinate-free but contain no propagation.

They are not substitutes for the primary dynamic E1 reader.

If a dynamic distinction is already present in the static material diagnostic,
that fact must be reported rather than automatically attributed to propagation.

### Frozen L1 comparison

Evidence must report, separately:

- frozen L1 coupled discrimination;
- E1 matched-uniform discrimination;
- E1 heterogeneous discrimination.

The frozen L1 result must not be treated as the causal E1 null because the
denominators differ.

### Translation control

A rigid integer translation of the source occupied geometry must leave:

- static heterogeneous-medium diagnostics;
- matched-uniform dynamic signature;
- heterogeneous E1 dynamic signature

unchanged.

### Reflection control

The E1 material rule and weighted graph are reflection-equivariant.

For the retained Gate 1A reflected pair

G(G(G(T)),G(T,T))

and

G(G(T,T),G(G(T)))

the frozen expectation is:

- static heterogeneous-medium diagnostics collide;
- matched-uniform signatures collide;
- E1 heterogeneous signatures collide.

Separating the pair requires an audit before interpretation and must not be
presented as intrinsic reflection breaking.

### E1 success criterion

E1 is positive if the heterogeneous medium adds reproducible distinctions
relative to the matched uniform-medium control while:

- preserving source-boundary constraints;
- passing translation and reflection controls;
- replaying deterministically.

Perfect injectivity is not required.

### E1 negative result

E1 remains valid negative evidence if occupancy-dependent material conductance
adds no distinction beyond the matched uniform medium.

The edge law, denominator, and sample schedule must not be changed to force a
positive result.

### E1 falsification criteria

E1 is invalid if:

- coordinates reach the final reader;
- FGS or structural identity is used;
- the edge law changes after seeing results;
- the denominator or sample schedule is tuned after results;
- padding or lattice extent is changed after results;
- orientation-sensitive material labels are introduced;
- the reflected pair is separated without causal audit;
- translation or deterministic replay fails.

### Protocol identifier

The frozen primary E1 protocol identifier is:

petra-vision-global-geometric-coupling-occupied-empty-field-v0

## G2-C0 frozen protocol

G2-C0 is the component-null representation control.

Protocol identifier:

`petra-vision-global-geometric-coupling-component-null-v0`

### Research question

Does explicitly representing each disconnected occupied component as an
independent geometry-derived unit change coordinate-free discrimination without
introducing any inter-component geometric coupling?

C0 is a representation control, not a positive coupling construction.

### Input boundary

C0 accepts exact `OrthogonalGeometry`.

The source occupied cells are partitioned only by orthogonal four-neighbor
connectivity.

C0 must not use:

- decoded AST nodes;
- VisionShape identity;
- native FGS;
- structural addresses;
- shape codes;
- corpus indices;
- filenames;
- D1 bridges;
- factor proximity;
- full-lattice propagation;
- occupied/empty material fields.

### Component extraction

Two occupied cells belong to the same component exactly when connected by a
path of orthogonal occupied-cell steps.

Every occupied source cell belongs to exactly one component.

Component multiplicity is preserved.

### Component normalization

Each extracted component is rigidly translated independently so that:

- its minimum x coordinate is 0;
- its minimum y coordinate is 0.

No rotation, reflection, scaling, deformation, or canonical structural decoding
is allowed.

Independent translation removes absolute placement while retaining the exact
occupied-cell geometry internal to each component.

### Frozen inner dynamics

Every normalized component is processed independently by the already frozen
occupied-cell graph-Laplacian v1 protocol:

`petra-vision-graph-laplacian-v1`

The inner protocol remains unchanged.

In particular it retains:

- occupied cells as graph vertices;
- four-neighbor occupied adjacency;
- combinatorial Laplacian;
- frozen v1 probe rule;
- denominator 8;
- exact integer numerator propagation;
- sample steps 1, 2, 4, 8, 16, 32;
- coordinate-free global state multiset reader.

No C0-specific parameter may modify the inner v1 dynamics.

### No inter-component coupling

Every component evolves in complete isolation.

There are no:

- edges between components;
- shared states;
- distance-dependent interactions;
- common empty-space lattice;
- factor interactions;
- component-to-component messages.

The position, distance, direction, and ordering of disconnected components are
unavailable to the primary reader.

### Primary C0 reader

For each normalized component, compute its complete frozen v1 dynamic
signature.

The C0 signature is the sorted multiplicity-preserving multiset of those
per-component signatures.

Therefore the primary reader retains:

- component multiplicity;
- internal component geometry as observable through frozen v1 dynamics.

It discards:

- component ordinal;
- left/right order;
- absolute coordinates;
- inter-component displacement;
- inter-component distance;
- source component enumeration order.

### Component-count control

The number of disconnected occupied components is recorded separately as a
static control.

It must not be confused with the primary dynamic component representation.

### Static component-profile control

Evidence may also record the unordered multiplicity-preserving multiset of the
same frozen coordinate-free graph-profile fields already used in Gate 2
controls:

- vertices;
- edges;
- connected components;
- isolated vertices;
- component cycle rank;
- maximum degree.

This static control contains no propagation.

### B0 comparison

Evidence must report frozen G2-B0 separately.

B0 and C0 answer different questions:

- B0 evolves all occupied components in one disconnected occupied-cell graph and
  then globally pools the state values;
- C0 preserves the boundary between disconnected components and pools complete
  per-component signatures only after each component has evolved independently.

Any C0 gain over B0 is therefore representation information.

It must not be described as global geometric coupling.

### Reflected/reordered control

The retained Gate 1A pair

`G(G(G(T)),G(T,T))`

and

`G(G(T,T),G(G(T)))`

contains the same disconnected component geometries in opposite spatial order.

The frozen expectation is that C0 preserves this collision.

If C0 separates the pair, the implementation must be audited before any
interpretation.

### Translation and displacement controls

Rigid translation of the complete source geometry must leave the C0 signature
unchanged.

Changing only the displacement between disconnected components, without
changing their internal geometries, must also leave the C0 signature unchanged.

### C0 success criterion

C0 is valid if it:

- exactly partitions the occupied geometry into four-neighbor components;
- preserves multiplicity;
- uses frozen v1 independently inside each component;
- removes absolute component placement;
- introduces no inter-component coupling;
- preserves the declared reordered/reflected collision;
- replays deterministically.

C0 may be injective or non-injective on the bounded corpus.

Its role remains a representation control either way.

### C0 falsification criteria

C0 is invalid if:

- component order reaches the final reader;
- absolute coordinates reach the final reader;
- inter-component distance reaches the final reader;
- components exchange state;
- empty space connects components;
- FGS or decoded structural identity is used;
- frozen v1 parameters are altered;
- multiplicity is lost;
- the retained reordered pair is separated without causal audit;
- deterministic replay fails.

### Claim boundary

C0 can establish only the bounded information contributed by explicitly
preserving disconnected component boundaries.

It cannot establish global coupling, orientation recovery, structural decoding,
spectral uniqueness, robustness, or theorem-level uniqueness.
