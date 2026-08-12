# PETRA VISION Gate 3 — G3-I1 impulse-response attribution evidence

## Status

Complete.

Protocol:

`petra-vision-explicit-spectral-controls-i1-v0`

Evidence protocol:

`petra-vision-explicit-spectral-controls-i1-evidence-v0`

Gate boundary:

- S0/S1 complete;
- S2 complete;
- H1 complete;
- P1 complete;
- I1 complete;
- T1 and O1 not evaluated here.

No Gate 4 adversarial mutation work is part of this evidence.

## Purpose

G3-I1 separates information attributable to the frozen Laplacian operator from
information attributable to the chosen point-impulse location.

P1 changed the type or shape of the initial field.

I1 instead freezes every elementary excitation to the same mass-one unit
impulse and changes only how source location is handled.

The primary intrinsic observation is `all-vertices`: every occupied vertex is
excited independently by a mass-one impulse and the source identities are then
removed by a multiplicity-preserving unordered aggregation of the elementary
response signatures.

## Provenance

Gate 3 foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

I1 protocol freeze:

`68aa62a` — `research: freeze Gate 3 impulse response attribution`

I1 implementation:

`38d5ecb` — `research: implement Gate 3 impulse response attribution`

I1 evidence runner:

`62758b5` — `research: add Gate 3 impulse evidence runner`

I1 protocol SHA256:

`fcb516e0ac262af2329f31bf6a3494ca3fe028dfad752445288209325426f01b`

I1 implementation SHA256:

`ed4e9894eb76c3d7e38579337071afeb634d8d5d072029638388191c830e32a2`

I1 evidence runner SHA256:

`8fb046d016a88d4066aeb3f736d3b0e79c31cadb5ed4e314f08342804d3c4b37`

The implementation passed 47 structural pre-corpus tests.

The combined implementation + evidence-runner suite passed 61 pre-corpus tests.

No I1 corpus was observed before protocol, implementation, and evidence-runner
freeze.

## Frozen applicability

I1 evaluates B0 and D1 only.

F1 is N/A because its frozen state is an intrinsic six-channel factor feature
state; replacing that state with a scalar point impulse would change the
representation semantics.

L1 is N/A because its frozen binary occupancy field is the encoded input;
replacing that field with a scalar point impulse would erase the input
semantics.

T1 temporal reduction and O1 orientation diagnostics remain inactive.

## Frozen impulse family

Every elementary impulse is:

`delta_v(u) = 1 if u = v, otherwise 0`

Therefore every elementary impulse has:

- integer entries;
- total mass 1;
- L1 norm 1;
- squared L2 norm 1.

No impulse normalization, rescaling, amplitude search, source search, or
schedule search is permitted.

The frozen sample steps are:

`1, 2, 4, 8, 16, 32`

For each elementary impulse the reader records only the sorted global state
values at each frozen sample step.

Source vertex identity, coordinates, vertex order, component order, factor
order, AST identity, corpus index, and shape serialization are not exposed by
the elementary reader.

## Frozen observation modes

### minimum

One mass-one impulse is placed at the lexicographically minimum occupied cell
of the complete geometry.

This is coordinate-derived and asymmetric.

It is intentionally not the Gate 2 component-wise minimum probe.

### reflected-minimum

The geometry is horizontally reflected through its occupied bounding box, the
minimum occupied cell is selected on the reflected geometry, and the impulse is
transported back through the exact reflection bijection.

This is also coordinate-derived and is used as the matched reflection
counterpart of `minimum`.

### all-vertices

Every occupied vertex receives one independent mass-one impulse.

The resulting elementary response signatures are aggregated as an unordered,
multiplicity-preserving multiset.

No source identity or source order survives this aggregation.

`all-vertices` is therefore the primary intrinsic/equivariant I1 observable.

It is an intrinsic impulse-response family, not a single intrinsically selected
point impulse.

## Step-zero baseline

The sorted step-zero signature of every elementary mass-one impulse depends
only on operator order.

For `all-vertices`, the step-zero observation is the multiplicity-preserving
multiset of these elementary step-zero signatures.

Therefore the dynamic discrimination beyond step zero cannot be attributed to
a structurally rich initial field.

## Matched D1 comparison

For every I1 observation, D1 null and D1 coupled preserve:

- occupied geometry;
- occupied vertices;
- local edges;
- impulse construction;
- impulse mass;
- sample schedule;
- Euler denominator;
- response reader;
- all-vertices aggregation.

Only the frozen distance-2 bridge weight differs.

The D1 null and coupled impulse families are byte-for-byte identical before
propagation.

## Structural audits

The frozen implementation and runner verify:

- exact mass-one elementary impulses;
- independent elementary propagation;
- exact batched propagation equivalent to independent propagation;
- translation by `(17, 11)`;
- minimum/reflected-minimum reflection transport;
- all-vertices reflection invariance;
- elementary response bijection under reflection before aggregation;
- source-order removal after aggregation;
- matched D1 null/coupled impulse families;
- B0/D1 delegation to the frozen operator implementations;
- source-boundary exclusion of P1, S2, H1, T1, and O1 readers.

All required structural audits passed on all executed corpora.

## Evidence artifacts

Phase 1:

`_work/petra-vision-gate3-i1/phase1-i1.json`

SHA256:

`352890c5cd88ba33328a38ec034ea8e00831aaf857d7d35e628bff537d5436a5`

Phase 1 replay is byte-for-byte identical.

Held-out:

`_work/petra-vision-gate3-i1/heldout-i1.json`

SHA256:

`b15b3452ef70a5be79346cfc331375bc7041d637fdd54b702a8fa48d5474d0a8`

Held-out replay is byte-for-byte identical.

Extended:

`_work/petra-vision-gate3-i1/extended-i1.json`

SHA256:

`0c3da90040188903c1da7031c79857b022165bdb43286a9230f16b0305edb743`

Extended replay is byte-for-byte identical.

The extended set is the union of Phase 1 and held-out and is not treated as an
independent third replication.

## Complete discrimination matrix

| Corpus | I1 observation | Step zero | B0 dynamic | D1 null | D1 coupled | D1 delta | Split pairs | Introduced |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | minimum | 29/110 | 82/110 | 82/110 | 110/110 | +28 | 38 | 0 |
| Phase 1 | reflected-minimum | 29/110 | 82/110 | 82/110 | 110/110 | +28 | 38 | 0 |
| Phase 1 | all-vertices | 29/110 | 62/110 | 62/110 | 67/110 | +5 | 20 | 0 |
| Held-out | minimum | 9/27 | 24/27 | 24/27 | 27/27 | +3 | 6 | 0 |
| Held-out | reflected-minimum | 9/27 | 24/27 | 24/27 | 27/27 | +3 | 6 | 0 |
| Held-out | all-vertices | 9/27 | 16/27 | 16/27 | 16/27 | +0 | 0 | 0 |
| Extended | minimum | 31/137 | 105/137 | 105/137 | 137/137 | +32 | 46 | 0 |
| Extended | reflected-minimum | 31/137 | 105/137 | 105/137 | 137/137 | +32 | 46 | 0 |
| Extended | all-vertices | 31/137 | 78/137 | 78/137 | 83/137 | +5 | 20 | 0 |

## Selected-location classification

`minimum` and `reflected-minimum` produce strong discrimination.

Phase 1:

`29/110 step-zero -> 82/110 D1 null -> 110/110 D1 coupled`

The D1 coupling:

- adds 28 signature classes;
- splits 38 null collision pairs;
- introduces zero collision pairs.

Held-out:

`9/27 step-zero -> 24/27 D1 null -> 27/27 D1 coupled`

The D1 coupling:

- adds 3 signature classes;
- splits 6 null collision pairs;
- introduces zero collision pairs.

Extended:

`31/137 step-zero -> 105/137 D1 null -> 137/137 D1 coupled`

The D1 coupling:

- adds 32 signature classes;
- splits 46 null collision pairs;
- introduces zero collision pairs.

The historical reflected #23/#41 pair is separated by D1 coupled under the
coordinate-derived selected-location observation.

The strong selected-location result therefore demonstrates that D1 contains
information that can become globally visible from a privileged point
excitation.

It is not classified as intrinsic/equivariant discrimination because the
selected source depends on coordinates.

## Intrinsic all-vertices classification

`all-vertices` removes privileged source selection by evaluating every
mass-one point impulse and discarding the source identities after propagation.

### Phase 1

`29/110 step-zero -> 62/110 D1 null -> 67/110 D1 coupled`

The D1 coupling:

- adds 5 signature classes;
- splits 20 null collision pairs;
- introduces zero collision pairs.

The historical #23/#41 reflected pair remains a collision under B0, D1 null,
and D1 coupled.

Therefore the Phase 1 D1 gain survives removal of the privileged source
location.

This is a genuine bounded intrinsic impulse-family effect on Phase 1.

### Held-out

`9/27 step-zero -> 16/27 D1 null -> 16/27 D1 coupled`

The D1 coupling:

- adds zero signature classes;
- splits zero collision pairs;
- introduces zero collision pairs.

Therefore the Phase 1 `+5 / 20 split` intrinsic coupling gain does not
independently replicate on the held-out corpus.

The causal D1 gain must not be classified as a replicated result.

### Extended

`31/137 step-zero -> 78/137 D1 null -> 83/137 D1 coupled`

The D1 coupling:

- adds 5 signature classes;
- splits exactly the same 20 Phase 1 null collision pairs;
- introduces zero collision pairs.

The held-out subset contributes no additional split pairs.

There are zero cross-subset collision pairs for B0, D1 null, and D1 coupled.

The extended result is therefore a clean composition of the Phase 1 effect and
the held-out no-gain result.

## Replicated bounded partition-equivalence rabbit

A post-result rabbit isolation compared the intrinsic I1 `all-vertices`
partition with the already frozen P1 `local-degree` partition and the exact S1
operator-spectrum partition.

No P1 or S1 result was used as an I1 input.

### Phase 1

For B0:

- I1 all-vertices = 62 classes, 63 collision pairs;
- P1 local-degree = 62 classes, 63 collision pairs;
- S1 = 62 classes, 63 collision pairs;
- the complete collision partitions are exactly equal.

For D1 null:

- I1 all-vertices = 62 classes, 63 collision pairs;
- P1 local-degree = 62 classes, 63 collision pairs;
- B0 S1 = 62 classes, 63 collision pairs;
- the complete collision partitions are exactly equal.

For D1 coupled:

- I1 all-vertices = 67 classes, 43 collision pairs;
- P1 local-degree = 67 classes, 43 collision pairs;
- D1 S1 = 67 classes, 43 collision pairs;
- the complete collision partitions are exactly equal.

The D1 null-to-coupled comparison produces the same exact set of 20 split pairs
under I1, P1, and S1, with zero introduced pairs.

### Held-out replication

For B0, D1 null, and D1 coupled:

- I1 all-vertices = 16 classes, 11 collision pairs;
- P1 local-degree = 16 classes, 11 collision pairs;
- the corresponding S1 partition = 16 classes, 11 collision pairs;
- the complete partitions are exactly equal.

The D1 gain is zero for I1, P1, and S1.

Therefore the partition equality discovered on Phase 1 independently
replicates on the 27 held-out width-4 forms.

### Extended composition

For B0 and D1 null:

- I1 all-vertices = 78 classes, 74 collision pairs;
- P1 local-degree = 78 classes, 74 collision pairs;
- B0 S1 = 78 classes, 74 collision pairs.

For D1 coupled:

- I1 all-vertices = 83 classes, 54 collision pairs;
- P1 local-degree = 83 classes, 54 collision pairs;
- D1 S1 = 83 classes, 54 collision pairs.

The same 20 Phase 1 D1 split pairs persist exactly.

No new held-out or cross-subset D1 split is added.

The extended corpus therefore preserves the replicated partition equivalence
without being treated as a third independent replication.

## Synthetic non-generic falsification

The equality between I1 all-vertices and S1 was explicitly tested for generic
necessity after the Phase 1 result and before held-out observation.

Two synthetic connected six-vertex unweighted graphs were constructed with the
same Laplacian characteristic polynomial:

`(1, -14, 73, -176, 192, -72, 0)`

Their S1 operator spectra are therefore identical.

Their I1 all-vertices response families are different.

The corresponding I1 response digests are:

- graph A: `380778810417d209aa0a20b8be88bded25e4a43d210f0c209b6e81f9ac27bac1`;
- graph B: `9e359f0b58dca62d69dde49a91a6744019c7961e660d8ca82aa26cd1055e2bea`.

The same construction with all edge weights scaled by 2 gives identical
weighted Laplacian characteristic polynomials:

`(1, -28, 292, -1408, 3072, -2304, 0)`

while retaining different I1 all-vertices responses.

The weighted I1 response digests are:

- graph A: `88f7787c2dbc7a29990b780f5369f9eb95e2f1717596c5c8b1e1197d8a49241a`;
- graph B: `6d9e5a42c34c0917595b2c0f3b9bb48b5a9b90dde1ec147ae0e341fdca8e7fe6`.

These synthetic graphs are not claimed to be PETRA-realizable.

They are an algebraic falsification control only.

The control proves that equal S1 operator spectra do not generically determine
equal I1 all-vertices response families.

Therefore the observed PETRA partition equality is not a universal consequence
of Laplacian evolution or cospectrality.

## Rabbit classification

The I1/P1/S1 result is classified as:

**Level 4 — replicated bounded rabbit.**

The supported bounded claim is:

> On the frozen PETRA family, the intrinsic all-vertices mass-one
> impulse-response family, the P1 local-degree trajectory, and the exact S1
> operator spectrum induce exactly the same discrimination partition for B0
> and D1. The equality replicates on the independent held-out width-4 corpus,
> remains consistent on the 137-form union, and is not a generic consequence
> of Laplacian cospectrality.

The result is stronger than equality of signature counts because the complete
collision partitions are equal.

It is also stronger than a Phase 1-only coincidence because the partition
equality independently replicates on held-out forms.

## Causal classification

The replicated partition-equivalence rabbit must be kept separate from the D1
causal gain.

For intrinsic I1 all-vertices:

- Phase 1 D1 null -> coupled: `62 -> 67`, +5 classes, 20 splits, 0 introduced;
- held-out D1 null -> coupled: `16 -> 16`, +0 classes, 0 splits, 0 introduced;
- extended D1 null -> coupled: `78 -> 83`, +5 classes, the same 20 Phase 1
  splits, 0 introduced.

Therefore:

- the intrinsic D1 coupling gain is real on the bounded Phase 1 corpus;
- it persists in the 137-form union;
- it does not independently replicate on held-out forms.

It remains a Level 3 bounded causal effect, not a Level 4 replicated causal
effect.

## Historical #23/#41 control

Under I1 all-vertices the historical exact reflected pair remains colliding
for:

- B0;
- D1 null;
- D1 coupled.

This is required by the frozen intrinsic/reflection-equivariant protocol.

Any separation of this pair under all-vertices would have indicated a
reflection, aggregation, or source-boundary failure.

The required collision is preserved.

## Interpretation

I1 resolves the principal attribution question raised by the earlier
coordinate-derived probe results.

D1 can produce dramatic complete discrimination when a privileged
coordinate-derived source is selected.

After privileged source selection is removed, D1 still produces a real Phase 1
gain under the intrinsic all-vertices impulse family, but that gain does not
replicate held-out.

Separately, the intrinsic impulse-response family reproduces exactly the same
bounded discrimination partition as P1 local-degree dynamics and the exact S1
operator spectrum.

Because synthetic Laplacian-cospectral controls show that I1 can distinguish
operators that S1 cannot, this equality is not a generic spectral identity.

The equality is therefore an empirical structural property of the frozen PETRA
family studied here.

## Claims supported

This evidence supports the following bounded claims:

1. Selected point-impulse location can strongly amplify D1 discrimination.
2. The intrinsic all-vertices impulse-response family contains substantially
   more discrimination than its step-zero operator-order baseline.
3. D1 produces a real intrinsic all-vertices gain on Phase 1.
4. That causal gain does not independently replicate on held-out forms.
5. I1 all-vertices, P1 local-degree, and S1 induce the same complete
   discrimination partition on Phase 1.
6. That partition equality independently replicates on the held-out corpus.
7. The equality remains consistent on the complete 137-form union.
8. The equality is not a generic mathematical necessity of Laplacian
   cospectrality.
9. No cross-subset collision pairs appear in the extended all-vertices
   composition.

## Claims not supported

This evidence does not establish that:

- I1 all-vertices reconstructs the graph;
- I1 all-vertices reconstructs the Laplacian spectrum;
- S1 reconstructs I1 all-vertices;
- I1 and S1 are generically equivalent;
- P1 local-degree, I1 all-vertices, and S1 are numerically reconstructible from
  one another;
- D1 breaks horizontal reflection symmetry;
- the Phase 1 D1 intrinsic coupling gain replicates held-out;
- the selected minimum result is intrinsic;
- the synthetic counterexample graphs are PETRA-realizable;
- the bounded partition equality is a theorem for arbitrary graphs;
- temporal ordering has been evaluated;
- orientation-sensitive diagnostics have been evaluated;
- Gate 4 adversarial mutation behavior has been evaluated.

## Final G3-I1 conclusion

G3-I1 is complete.

The selected-location experiments show that privileged point-source placement
can expose enough D1 information to discriminate all frozen forms in both
Phase 1 and held-out.

The intrinsic all-vertices experiment removes that privileged source identity
and reveals two distinct conclusions.

First, the D1 coupling has a genuine but non-replicated intrinsic Phase 1
effect.

Second, and more importantly, the complete I1 all-vertices discrimination
partition is exactly equal to both P1 local-degree dynamics and S1 on Phase 1,
replicates on the independent held-out corpus, and remains coherent in the
137-form union.

Synthetic cospectral counterexamples falsify generic necessity.

The resulting I1/P1/S1 partition equality is therefore retained as a Level 4
replicated bounded rabbit.

G3-I1 closes without activating T1 or O1.
