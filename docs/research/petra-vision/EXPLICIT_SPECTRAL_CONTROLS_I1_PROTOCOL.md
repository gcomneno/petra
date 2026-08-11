# PETRA VISION Gate 3 — G3-I1 impulse-response attribution protocol

## Status

Frozen before I1 implementation and before I1 corpus observation.

Protocol identifier:

`petra-vision-explicit-spectral-controls-i1-v0`

G3-I1 follows completed S0/S1, S2, H1, and P1.

This protocol defines only I1.

T1 and O1 remain inactive.

## Purpose

G3-I1 separates information attributable to the frozen operator from
information attributable to choosing a particular impulse location.

P1 established that broad changes of initial state materially alter dynamic
discrimination and that the original coordinate-derived D1 minimum probe
retains an orientation qualification.

I1 now performs the stricter mass-matched impulse-location attribution that P1
explicitly deferred.

Every elementary I1 excitation has exactly one unit of mass:

`delta_v`

with value 1 at one occupied vertex and value 0 at every other occupied vertex.

I1 asks:

1. how much discrimination is obtained from one coordinate-selected unit
   impulse;
2. whether its exact reflected counterpart behaves as required;
3. how much discrimination survives when no distinguished impulse location is
   selected at all;
4. whether D1 coupling adds information relative to its matched null under an
   intrinsic, vertex-permutation-equivariant impulse-response family.

I1 is an attribution experiment.

It is not a search for a new perfect classifier.

No impulse rule, aggregation rule, sample schedule, or reader may be modified
after corpus results are observed.

## Applicability

### B0 — applicable

B0 has a frozen scalar graph state and exact graph-Laplacian evolution.

I1 measures its responses to mass-one vertex impulses.

### D1 — applicable and primary causal target

D1 has the same occupied-cell vertex domain as B0 and exact frozen null and
coupled operators.

For every elementary impulse, D1 matched null and D1 coupled must receive the
byte-for-byte identical initial state.

They may differ only through the already frozen bridge weight.

### F1 — not applicable in I1

F1's frozen state is a six-channel intrinsic factor representation rather than
a selected scalar point excitation.

Introducing scalar unit impulses over FGS factors would create a new state
semantics not present in the frozen Gate 2 F1 construction.

No F1 impulse experiment is introduced here.

### L1 — not applicable in I1

L1's frozen initial field is the binary occupancy input itself.

Replacing that field with a single point impulse would remove the encoded
geometry rather than isolate a location choice inside the frozen construction.

No L1 point-impulse experiment is introduced here.

These N/A decisions are frozen before I1 corpus observation.

## Frozen operators and dynamics

### B0

Use unchanged:

- occupied cells as vertices;
- four-neighbor combinatorial Laplacian;
- exact integer Euler-numerator dynamics;
- denominator 8;
- sample steps 1, 2, 4, 8, 16, 32.

### D1 matched null

Use unchanged:

- occupied cells as vertices;
- local axial distance-1 edges with weight 2;
- declared distance-2 bridge positions with bridge weight 0;
- exact integer Euler-numerator dynamics;
- denominator 16;
- sample steps 1, 2, 4, 8, 16, 32.

### D1 coupled

Use unchanged:

- occupied cells as vertices;
- local axial distance-1 edges with weight 2;
- axial distance-2 bridge edges through one empty midpoint with weight 1;
- exact integer Euler-numerator dynamics;
- denominator 16;
- sample steps 1, 2, 4, 8, 16, 32.

No operator parameter is changed by I1.

## Elementary impulse

For a frozen graph with occupied vertices V and vertex v in V, define:

`delta_v(u) = 1 if u = v else 0`.

Every elementary impulse therefore has:

- exact integer entries;
- total mass 1;
- L1 norm 1;
- squared L2 norm 1.

No amplitude normalization, rescaling, or corpus-dependent adjustment is
allowed.

This is the mass-matched impulse basis for every I1 comparison.

## Elementary response reader

For one elementary impulse `delta_v`, evolve the frozen system and record at
each declared sample step only:

`sorted(state_values)`.

The elementary response signature is the ordered tuple of those global
multisets at steps:

`1, 2, 4, 8, 16, 32`.

The reader does not observe the identity of v.

It does not observe coordinates, vertex order, component ordinal, or structural
labels.

The ordering of sample times is retained in I1.

Removing temporal order belongs to T1 and must not be mixed into I1.

## Frozen I1 observation family

Evaluate exactly three declared impulse observations.

### I1-minimum

Choose the lexicographically minimum occupied cell of the complete geometry.

Apply one mass-one impulse at that vertex.

This is explicitly coordinate-derived and asymmetric.

It is a diagnostic selected-location control.

It is not the Gate 2 component-wise minimum probe and must not be described as
such.

Its purpose is to provide a clean single-impulse selected-location baseline
with exactly the same unit mass as every other elementary I1 impulse.

### I1-reflected-minimum

For geometry G:

1. horizontally reflect G through its own occupied bounding box;
2. choose I1-minimum on the reflected geometry;
3. transport that unit impulse back to G through the exact reflection cell
   bijection.

This is the true reflected counterpart of I1-minimum.

It is coordinate-derived and diagnostic.

The required transport identities are frozen below.

### I1-all-vertices

For every occupied vertex v independently:

1. construct the mass-one impulse `delta_v`;
2. compute its elementary coordinate-free response signature.

Then expose only the unordered multiplicity-preserving multiset of all
elementary response signatures:

`multiset({ response(delta_v) : v in V })`.

This is the primary intrinsic I1 observable.

No vertex identity or ordering survives the aggregation.

No particular vertex is selected.

No tie-breaking is required.

Every candidate excitation is mass-matched.

The I1-all-vertices observable is:

- coordinate-free at the reader;
- vertex-permutation invariant after multiset aggregation;
- translation invariant;
- horizontal-reflection invariant;
- independent of lexicographic endpoint choice.

It may retain vertex count through multiplicity.

That is part of the frozen reader and is not a protocol failure.

## Why all-vertices is the intrinsic control

An equivariant rule cannot always select one unique vertex from a symmetric
graph without either:

- arbitrary tie-breaking;
- coordinates;
- vertex identity;
- or additional structure.

I1 therefore does not invent an intrinsic distinguished point.

Instead it evaluates every mass-one point impulse and removes their identities
by an unordered multiplicity-preserving response multiset.

This separates sensitivity to a chosen location from the operator's complete
bounded family of point responses.

The resulting observable must not be described as a single intrinsic impulse.

It is an intrinsic impulse-response family.

## Step-zero control

For every elementary mass-one impulse:

`sorted(delta_v)`

depends only on operator order.

Accordingly record the step-zero impulse signature and its corpus partition.

For I1-all-vertices also record the multiplicity-preserving multiset of
elementary step-zero signatures.

No dynamic distinction beyond vertex-count information can be attributed to
the initial mass-one impulse multiset itself.

This gives I1 a stricter static baseline than P1-local-degree.

## Matched D1 causal comparison

For each declared I1 observation compare:

`D1 matched null -> D1 coupled`

while holding fixed:

- geometry;
- occupied vertex set;
- local edges;
- every elementary impulse tuple;
- denominator;
- sample schedule;
- elementary reader;
- aggregation rule.

For I1-minimum and I1-reflected-minimum the same selected impulse tuple must be
used by null and coupled.

For I1-all-vertices the complete ordered construction list before
identity-removing aggregation must be byte-for-byte identical between null and
coupled.

Only bridge weight may differ.

Report:

- distinct-signature delta;
- null collision pairs split by coupling;
- collision pairs introduced by coupling;
- exact collision groups.

## Selected-location comparison

Compare I1-minimum and I1-reflected-minimum as coordinate-derived diagnostics.

Do not interpret their difference as intrinsic orientation information.

Their scientific purpose is to expose sensitivity to which member of a
reflection-related impulse pair is selected.

## Intrinsic-response comparison

Compare I1-all-vertices against each selected-location observation.

Partition relations may be:

- refinement;
- coarsening;
- equality;
- incomparable.

No monotonic relation is assumed in advance.

A strong all-vertices result is evidence about the unordered family of impulse
responses, not about one privileged excitation.

## Historical #23/#41 control

Record the retained reflected/reordered #23/#41 pair explicitly.

Under I1-all-vertices:

- B0 must not separate an exact reflected pair;
- D1 null must not separate an exact reflected pair;
- D1 coupled must not separate an exact reflected pair.

Any such separation is a reflection/equivariance or source-boundary failure,
not a scientific result.

I1-minimum and I1-reflected-minimum are coordinate-derived diagnostics and may
produce different selected-location behavior.

Their required relationship is governed by reflection transport rather than
same-mode invariance.

## Reflection audit

For every geometry G, construct its exact horizontal reflection R(G).

### I1-minimum / I1-reflected-minimum

Require:

`signature(G, minimum) = signature(R(G), reflected-minimum)`

and:

`signature(G, reflected-minimum) = signature(R(G), minimum)`.

This must hold independently for:

- B0;
- D1 null;
- D1 coupled.

### I1-all-vertices

Require:

`signature(G, all-vertices) = signature(R(G), all-vertices)`.

Additionally verify that reflection induces a bijection between elementary
mass-one responses before aggregation.

Failure is an implementation or equivariance bug.

## Translation audit

Freeze translation vector:

`(+17, +11)`.

Translate every occupied cell by this vector.

Require exact equality of:

- selected impulse construction modulo translated coordinates;
- each elementary response after canonical value-multiset reading;
- I1-all-vertices aggregated response;
- final corpus signature.

Failure is coordinate leakage.

## Reader boundary

The elementary I1 reader may observe only:

- frozen substrate/operator;
- declared mass-one impulse;
- exact frozen evolution;
- global state-value multiset at each frozen sample step.

The I1-all-vertices aggregator may observe only the multiplicity-preserving
multiset of elementary response signatures.

It must not observe:

- vertex identity;
- vertex order;
- coordinates;
- source vertex coordinate;
- source vertex index;
- component ordinal;
- factor order;
- structural address;
- AST/tree identity;
- shape serialization;
- shape code;
- corpus index;
- S0/S1/S2/H1/P1 signatures;
- T1/O1 results.

Coordinates may be used only to construct the explicitly labelled
I1-minimum/reflected-minimum diagnostic pair and to perform translation and
reflection audits.

Shape code may appear only in evidence metadata for collision reporting.

## Source isolation

I1 may call frozen B0 and D1 construction/dynamics helpers.

It must not modify their implementation.

I1 must not use P1 dynamic signatures as input.

P1 may be referenced only as completed scientific context in human-readable
interpretation after I1 results exist.

S1 or other Gate 3 evidence may likewise be used only in explicitly labelled
post-result rabbit isolation, never as an I1 reader input.

## Computational implementation

The exact semantic definition is one elementary unit impulse per occupied
vertex.

An implementation may evaluate those impulses independently or batch them
algebraically for efficiency.

Any batched implementation must be proven by focused tests to produce exactly
the same elementary and aggregated signatures as independent propagation.

Optimization must not change:

- integer arithmetic;
- denominator;
- sample steps;
- elementary response;
- multiplicity;
- aggregation semantics.

No corpus-dependent optimization decision may alter the protocol.

## Corpus order

Observe corpora separately and strictly in this order:

1. Phase 1 — 110 forms;
2. held-out width-4 — 27 forms;
3. extended frozen domain — 137 forms.

Phase 1 must be interpreted before held-out is observed.

Held-out must be interpreted before extended is observed.

The extended domain is the union of Phase 1 and held-out and is not an
independent third replication.

## Required measurements

For every corpus, substrate, operator variant, and I1 observation record:

- protocol identifier;
- exact impulse rule;
- mass-one invariant;
- step-zero signature count;
- dynamic signature count;
- exact collision groups;
- collision-pair count;
- selected-location versus all-vertices partition comparisons;
- D1 null-to-coupled split pairs;
- D1 null-to-coupled introduced collision pairs;
- #23/#41 behavior;
- deterministic replay;
- translation audit;
- reflection/transport audit;
- elementary-response aggregation audit;
- source-boundary audit;
- source SHA256;
- evidence SHA256.

Retain Phase 1, held-out, and extended separately.

## Interpretation classes

### Selected-location dependent

A distinction observed under I1-minimum but absent from I1-all-vertices cannot
be attributed to an intrinsic distinguished impulse location.

It is evidence of selected-location dependence under the bounded protocol.

### Intrinsic impulse-family positive

If I1-all-vertices retains or adds discrimination with all reflection and
source-boundary audits passing, this is bounded evidence that the operator's
unordered mass-one impulse-response family carries that information without
privileging a source vertex.

### Intrinsic D1 coupling positive

If D1 coupled splits matched-null collision pairs under I1-all-vertices with
zero introduced collisions and all audits clean, this is bounded evidence that
the bridge coupling changes the intrinsic impulse-response family.

A held-out replication is required before describing such a gain as
replicated.

### Static-count effect

Any distinction already present in the step-zero mass-one signature or its
multiplicity must not be attributed solely to propagation.

## Rabbit-watch conditions

Stop normal progression and isolate a candidate if:

- I1-all-vertices yields unexpectedly high discrimination beyond step zero;
- D1 coupled gains clean collision splits over its matched null under
  I1-all-vertices;
- such a gain independently replicates held-out;
- I1-all-vertices induces an unexpected exact partition equality with a
  previously frozen coordinate-free invariant;
- B0 and D1 show a sharp qualitative difference under the same intrinsic
  impulse-family observation.

False-rabbit conditions requiring immediate audit include:

- I1-all-vertices separates an exact reflected pair;
- null and coupled do not receive identical elementary impulse families;
- multiplicity or vertex identity is accidentally dropped or exposed;
- source position reaches the primary reader;
- temporal order is changed inside I1;
- impulse amplitude or sample schedule is tuned after observation;
- P1, T1, or O1 reader information is mixed into I1.

## Non-claims

G3-I1 does not establish:

- universal injectivity;
- universal graph reconstruction from impulse responses;
- universal spectral reconstruction;
- intrinsic orientation recovery;
- existence of a unique intrinsic source vertex;
- temporal-order attribution;
- physical impulse propagation;
- physical time;
- robustness outside the frozen PETRA domain;
- theorem-level reconstruction.

A positive I1-all-vertices result remains a bounded property of the frozen
PETRA operator family and declared reader.

## Gate boundary

Freeze this protocol before implementing I1 or observing any I1 corpus result.

After protocol freeze:

1. implement exact elementary mass-one impulse responses for B0 and D1;
2. implement I1-minimum, I1-reflected-minimum, and I1-all-vertices;
3. add focused independent-vs-batched, mass, reflection, translation, and
   source-boundary tests;
4. freeze a deterministic one-corpus evidence runner;
5. observe Phase 1 only;
6. interpret Phase 1;
7. replay Phase 1;
8. observe held-out only;
9. interpret held-out;
10. replay held-out;
11. observe extended;
12. interpret and isolate any rabbit trigger;
13. replay extended;
14. write the human-readable I1 evidence record and close I1 formally.

G3-T1 and G3-O1 remain inactive throughout I1.
