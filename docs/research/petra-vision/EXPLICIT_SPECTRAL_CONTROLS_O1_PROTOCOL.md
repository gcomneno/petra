# PETRA VISION Gate 3 — G3-O1 orientation-control protocol

## Status

Frozen before any G3-O1 corpus discrimination result is observed.

Protocol ID: `petra-vision-explicit-spectral-controls-o1-v0`

## Gate boundary

- G3-S0/S1 complete;
- G3-S2 complete;
- G3-H1 complete;
- G3-P1 complete;
- G3-I1 complete;
- G3-T1 complete;
- G3-O1 active only after this protocol freeze.

No Gate 4 adversarial mutation work is part of O1. O1 is the final declared
Gate 3 attribution family and must remain separate from every Gate 4
perturbation or adversarial search.

## Governing contract

The Gate 3 contract defines O1 as an orientation control. Oriented observations
are explicitly labelled diagnostics only. They are never evidence for
coordinate-free recovery.

The sole purpose of O1-v0 is to measure how much additional bounded
discrimination becomes available when the native deterministic ordering already
present inside a frozen representation is retained instead of being removed by
its coordinate-free reader.

## Primary research question

For each frozen Gate 3 substrate, how much of the observed collision partition
changes when the same state values and same frozen dynamics are read in their
native deterministic order rather than through the matched coordinate-free
multiplicity-preserving reader?

Any gain under the oriented reader is classified as orientation or
identity-channel leakage available to that diagnostic representation. It must
not be promoted to intrinsic spectral, dynamic, geometric, or coordinate-free
information.

## No new directional feature engineering

O1-v0 does not introduce a new left/right statistic, directional moment,
quadrant histogram, signed coordinate moment, width/height orientation label,
eigenvector orientation, hand-selected axis, or corpus-dependent directional
feature.

The only information O1 is allowed to retain beyond the matched coordinate-free
reader is sequence position in the native deterministic state or factor order
that the frozen substrate implementation already uses internally.

Absolute coordinate values, cell coordinates, factor structural addresses, AST
identity, shape serialization, corpus index, and decoded shape labels are never
emitted into an O1 signature.

## Frozen substrates

- `O1-B0`: frozen occupied-cell graph-Laplacian B0;
- `O1-D1-null`: frozen D1 weighted graph with bridge weight zero;
- `O1-D1-coupled`: frozen D1 distance-2 coupled graph;
- `O1-F1-null`: frozen factor-proximity propagation with coupling disabled;
- `O1-F1-coupled`: frozen factor-proximity propagation with coupling enabled;
- `O1-L1-null`: frozen full-lattice propagation with lattice edges disabled;
- `O1-L1-coupled`: frozen full-lattice propagation with lattice edges enabled.

Null and coupled variants are retained where the frozen substrate already
defines them. They are not new constructions. Their purpose is to keep
orientation leakage separate from propagation or coupling effects.

## Common frozen schedule

The dynamic sample schedule remains exactly:

`1, 2, 4, 8, 16, 32`

O1 does not tune, shorten, extend, reorder, or search this schedule.

The complete six-snapshot trajectory is used for the dynamic diagnostic. T1
temporal reductions are not re-opened inside O1.

## Native-order principle

A native ordered state is the exact state tuple already indexed by the frozen
representation's deterministic vertex, lattice, or factor order. O1 preserves
that tuple position. The matched coordinate-free reader removes the same
position identity by sorting state values or factor states exactly as already
frozen.

O1 may expose tuple position only through the sequence ordering itself. It may
not append the underlying coordinate, factor address, or ordering key to the
signature.

## O1-B0

B0 already implements the required oriented diagnostic.
`dynamic_signatures_from_probe` returns `oriented`, the exact propagated state
tuple at every frozen sample step, and `global_multiset`, the same state values
sorted at each step.

O1-B0 therefore delegates directly to the frozen B0 construction and canonical
component probe. No replacement probe is permitted.

Frozen B0 observations:

- `oriented-step0`: the exact canonical component-probe tuple in native   `graph.cells` order;
- `coordinate-free-step0`: the sorted multiset of the same probe entries;
- `oriented-dynamic`: the existing B0 `oriented` six-snapshot reader;
- `coordinate-free-dynamic`: the existing B0 `global_multiset` reader.

The existing B0 `null_oriented` historical reader may be checked for
compatibility but is not a separate headline O1 result; O1 uses the explicit
step-zero signature as the static orientation baseline.

## O1-D1

D1 builds its frozen occupied-cell graph with `cells =
tuple(sorted(current.cells))`. Its propagation state is therefore already
indexed by a deterministic coordinate-derived native cell order. The frozen
public coordinate-free reader removes this position identity by sorting the
state values at every sample.

O1-D1 retains the exact propagated state tuple before that final sort. This is
not a new dynamic construction: it is the same frozen D1 state, probe,
denominator, graph, bridge weight, and sample schedule, with only the final
observation quotient removed.

Both D1-null and D1-coupled use the same frozen original-component probe. No
minimum/maximum, P1, I1, or alternative probe is introduced.

Frozen D1 observations:

- `oriented-step0`: frozen original-component probe in native cell order;
- `coordinate-free-step0`: sorted multiset of the same probe entries;
- `oriented-dynamic`: exact native-order propagated state at the six   frozen steps;
- `coordinate-free-dynamic`: frozen   `coordinate_free_dynamic_signature`.

## O1-F1

F1 already exposes the diagnostic `ordered_factor_proximity_signature`,
explicitly documented as the labelled ordered trajectory for diagnostics only.
Its matched coordinate-free reader is `factor_proximity_signature`, which
removes factor order by sorting the factor states at each sample.

O1-F1 uses these two existing readers without altering native FGS, factor
features, factor occurrence reconstruction, proximity distances, weights,
propagation equations, or sample schedule.

Frozen F1 observations:

- `oriented-step0`: frozen `initial_state` in native FGS factor order;
- `coordinate-free-step0`: sorted multiset of those factor feature states;
- `oriented-dynamic`: existing `ordered_factor_proximity_signature`;
- `coordinate-free-dynamic`: existing `factor_proximity_signature`.

Both F1-null and F1-coupled are evaluated. Factor ordinal itself remains a
diagnostic identity channel and is never interpreted as intrinsic orientation.

## O1-L1

L1 builds the complete bounding-box lattice in the deterministic native order
generated by increasing x and then increasing y. Its frozen initial state is
the binary occupancy field indexed in that lattice order. The frozen
coordinate-free dynamic reader removes lattice-site identity by sorting the
propagated state values at every sample.

O1-L1 preserves the exact native lattice state tuple before that sort. No
coordinate values are emitted. The same bounding rectangle, occupancy field,
graph, denominator, sample schedule, and propagation are retained.

Frozen L1 observations:

- `oriented-step0`: exact binary occupancy field in native lattice order;
- `coordinate-free-step0`: sorted multiset of the same occupancy entries;
- `oriented-dynamic`: exact native-order propagated lattice state at the   six frozen steps;
- `coordinate-free-dynamic`: frozen `full_lattice_signature`.

Both L1-null and L1-coupled are evaluated.

## Exact arithmetic

B0, D1, and L1 retain their frozen exact integer Euler numerator states. F1
retains its exact rational factor states. No floating-point approximation,
tolerance, quantization, or hashing-based equality is used to determine
collisions.

Because O1 keeps the sample instants explicitly labelled and compares forms
only at the same frozen instants, the common Euler representation factor at a
given step cannot encode a form-specific orientation. Exact
raw-versus-normalized partition equivalence for B0, D1, and L1 is retained as
an audit rather than as a separate attribution family.

## Primary matched comparisons

For every applicable substrate and corpus, O1 records complete collision
partitions for the four frozen observations and performs the following
predeclared comparisons.

1. `coordinate-free-step0 -> oriented-step0`: orientation/identity    information already available before propagation.
2. `coordinate-free-dynamic -> oriented-dynamic`: total additional    discrimination available when native state/factor order is retained.
3. `oriented-step0 -> oriented-dynamic`: dynamic refinement after the    oriented static baseline.
4. `coordinate-free-step0 -> coordinate-free-dynamic`: matched    coordinate-free dynamic refinement, reported for context.

For each nested comparison O1 reports signature-count delta, exact collision
pairs split, and newly introduced collision pairs. A purported refinement with
introduced collision pairs fails the expected partition relationship and must
be investigated before proceeding.

## Orientation gain classification

An `orientation gain` means that the oriented diagnostic strictly refines its
matched coordinate-free collision partition while the underlying state values
and dynamics are identical.

Such a gain is positive evidence only for the existence of information in the
retained ordering/identity channel. It is negative evidence against attributing
that same distinction to the coordinate-free reader.

O1 never converts an oriented gain into evidence for intrinsic left/right
recovery, reflection breaking, geometric reconstruction, spectral uniqueness,
or coordinate-free injectivity.

## Translation audit

Every O1 signature is evaluated under translation by `(17, 11)`, matching the
already frozen Gate 3 transform audit.

Translation must leave both coordinate-free and native-order signatures
unchanged because uniform translation preserves the deterministic relative
ordering used by B0/D1/L1 and does not alter the F1 normalized factor
construction.

A translation failure is a protocol or implementation failure, not an O1
positive result.

## Reflection/equivariance audit

Horizontal reflection is treated differently from translation because O1
intentionally preserves an orientation-sensitive ordering.

For every substrate the implementation must first verify propagation
equivariance under the exact horizontal-reflection bijection. A reflected state
transported back through that bijection must reproduce the original state
trajectory exactly.

After this equivariance audit, O1 also compares the canonical native-order
signature of the original geometry with the canonical native-order signature of
the reflected geometry without transporting the output indices back. A
difference in this second comparison is the declared O1 orientation diagnostic.

Coordinate-free reflection behavior remains governed by each frozen substrate's
existing qualification. In particular, a difference caused by independent
coordinate-derived B0/D1 probe selection is not intrinsic orientation evidence.

## Historical #23/#41 control

The retained reflected/reordered pair `G(G(G(T)),G(T,T))` / `G(G(T,T),G(G(T)))`
is reported explicitly wherever present.

O1 records its collision/split status under coordinate-free step zero, oriented
step zero, coordinate-free dynamics, and oriented dynamics for every applicable
substrate.

If an oriented reader separates this pair while the matched coordinate-free
reader collides, the result is classified only as a direct demonstration of
orientation/identity-channel leakage.

If D1-coupled already separates the pair under its frozen coordinate-free
probe-qualified reader, O1 must not count that existing split as new
orientation information.

## Corpus order

O1 must be evaluated in exactly this order:

1. frozen Phase 1 corpus — 110 forms;
2. deterministic Phase 1 replay;
3. independent held-out width-4 corpus — 27 forms;
4. deterministic held-out replay;
5. complete extended domain — 137 forms;
6. deterministic extended replay.

The extended corpus is a composition of Phase 1 and held-out, not an
independent third replication.

## Required measurements

For every corpus and O1 channel record:

- protocol identifier and frozen source digests;
- form count;
- exact signature counts for all four observations;
- exact collision groups and collision pairs;
- split and introduced collision pairs for every declared comparison;
- explicit #23/#41 behavior where present;
- translation audit;
- reflection-equivariance transport audit;
- canonical original-versus-reflected oriented diagnostic;
- raw-versus-normalized partition audit for Euler substrates;
- source-boundary audit;
- deterministic evidence digest and byte-identical replay.

## Source boundary

O1 may delegate only to the frozen B0, D1, F1, and L1 substrate implementations
required to obtain their exact native states and existing coordinate-free
readers.

O1 must not consume S0/S1, S2, H1, P1, I1, or T1 signatures, collision tables,
classifications, evidence JSON, or evidence Markdown as inputs.

Prior Gate 3 results may be compared only after O1 corpus results exist, for
interpretation or rabbit isolation. They may never alter the frozen O1
observation contract.

Gate 4 mutation generators, adversarial corpora, or perturbation results are
forbidden O1 inputs.

## No parameter search

O1 contains no tunable orientation parameter. No axis choice, order choice,
sample-step choice, directional statistic, probe search, factor reordering,
coordinate transform search, or signature combination may be selected after
corpus discrimination is observed.

Any additional orientation diagnostic proposed after O1-v0 results would
require a separately frozen follow-up protocol and may not be folded into the
O1-v0 headline evidence.

## Rabbit watch

O1 is expected to reveal orientation leakage, so high oriented discrimination
by itself is not a rabbit. The following post-result patterns are the only
predeclared reasons to stop normal corpus progression for rabbit isolation.

1. An oriented partition unexpectedly equals a previously frozen intrinsic    partition under materially different construction, and the equality is    exact rather than count-only.
2. Orientation gain appears in an intrinsic/equivariant coordinate-free    reader without a source/probe/ordering explanation.
3. A canonical oriented reader is unexpectedly reflection-invariant over a    nontrivial family despite preserving native order.
4. An orientation-leakage partition discovered on Phase 1 reproduces    exactly on independent held-out forms in a structurally surprising way    beyond trivial injectivity.
5. Reflection transport fails despite the frozen dynamics being expected    equivariant.

A perfect or near-perfect oriented score is explicitly not a rabbit when it is
explained by retained native positional identity.

## Success classification

O1 succeeds when it cleanly quantifies the extra discrimination made available
by native ordering and demonstrates that the corresponding information
disappears or is reduced when the matched coordinate-free quotient is restored.

A zero orientation gain is also a valid result: it means the retained native
order did not refine that particular frozen collision partition.

## Failure classification

O1 fails or becomes confounded if an oriented signature includes explicit
coordinates, shape serialization, factor structural addresses, corpus identity,
decoded syntax, an undeclared probe, or any post-result directional feature.

Replay failure, translation failure, or reflection-transport equivariance
failure also blocks interpretation until resolved.

## Claims allowed

O1 may support bounded statements such as:

- retaining native state order exposes additional discrimination;
- that additional discrimination is orientation/identity-channel   dependent;
- a particular coordinate-free collision is separable by an explicitly   oriented diagnostic;
- the underlying frozen dynamics remain reflection-equivariant even when   the canonical ordered reader is reflection-sensitive;
- an apparent distinction in an earlier probe-qualified result is   consistent with orientation leakage rather than intrinsic reflection   breaking.

## Claims forbidden

O1 does not establish:

- coordinate-free orientation recovery;
- intrinsic left/right identity;
- intrinsic reflection breaking;
- graph or geometry reconstruction;
- AST or syntax reconstruction;
- universal injectivity;
- generic spectral uniqueness;
- eigenvector orientation recovery;
- physical orientation;
- robustness to perturbation or noise;
- Gate 4 adversarial robustness.

## Completion condition

G3-O1-v0 is complete only after protocol, implementation, and evidence runner
are frozen pre-corpus; Phase 1, held-out, and extended evidence are evaluated
in order with deterministic replay; orientation gains and reflection controls
are classified; exact source and evidence digests are recorded; and a
human-readable O1 evidence report is committed.

Only after O1 is formally closed may the complete Gate 3 attribution matrix be
synthesized into the final Gate 3 decision. Gate 4 remains inactive until that
Gate 3 decision is complete.
