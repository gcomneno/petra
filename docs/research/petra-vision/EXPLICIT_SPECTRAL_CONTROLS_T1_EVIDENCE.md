# PETRA VISION Gate 3 — G3-T1 temporal observation evidence

## Status

Complete.

Protocol:

`petra-vision-explicit-spectral-controls-t1-v0`

Evidence protocol:

`petra-vision-explicit-spectral-controls-t1-evidence-v0`

Gate boundary:

- S0/S1 complete;
- S2 complete;
- H1 complete;
- P1 complete;
- I1 complete;
- T1 complete;
- O1 not evaluated here.

No Gate 4 adversarial mutation work is part of this evidence.

## Purpose

G3-T1 asks whether discrimination in the already frozen PETRA VISION dynamics
is attributable to temporal ordering or evolution, rather than to the static
collection of sampled states alone.

T1 does not define a new dynamic construction. It applies four frozen
observation reductions to the existing B0, D1 null, D1 coupled, F1, and L1
trajectories at the common discrete sample schedule 1, 2, 4, 8, 16, 32.

## Provenance

Gate 3 foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

T1 protocol freeze:

`3f814e4` — `research: freeze Gate 3 temporal observation`

T1 implementation:

`9064e38` — `research: implement Gate 3 temporal observation`

T1 evidence runner:

`146ee7a` — `research: add Gate 3 temporal evidence runner`

T1 protocol SHA256:

`c614b2a4b9430f993103eeb2cd4b097f128780f8b8f2161e63543193e03a04ed`

T1 implementation SHA256:

`eeafb31eb570f24a3d193a7b0ca92dc874e19e570d2c94f6c7152d02ffd51d85`

T1 evidence runner SHA256:

`51680979fd6b8526fcd180ae55200c84fc8023c50f5fd707a4d2d91c93418f4b`

The implementation passed 41 structural pre-corpus tests. The combined
implementation plus evidence-runner suite passed 53 pre-corpus tests. No T1
corpus was observed before protocol, implementation, and evidence-runner
freeze.

## Frozen applicability

T1 evaluates B0, D1 null, D1 coupled, F1, and L1. P1 and I1 signatures are not
inputs. S1, S2, H1, P1, and I1 may only be used for post-result interpretation;
they are not part of the T1 evidence reader.

B0 and D1 retain their frozen coordinate-derived primary probes and are
therefore probe-qualified. Reflection audits transport the frozen source or
initial state instead of independently reselecting a source. F1 and L1 are
intrinsic/equivariant under the frozen reflection audit.

## Frozen temporal schedule

The frozen sample schedule is:

`1, 2, 4, 8, 16, 32`

Step zero is a diagnostic baseline only and is not concatenated into the
primary six-snapshot temporal signatures.

## Frozen normalization

Primary temporal attribution uses exact normalized states so that the Euler
numerator representation scale q^k cannot act as an implicit time label after
the explicit time labels are removed.

- B0 uses exact normalization by `8^k`;
- D1 uses exact normalization by `16^k`;
- L1 uses exact normalization by `8^k`;
- F1 already evolves as an exact rational propagation process and needs   no artificial Euler denominator.

Raw Euler numerator reductions are retained only as an audit. Ordered raw and
normalized partitions must match because labelled time and the frozen
denominator make the conversion invertible.

## Frozen reductions

1. `T1-ordered`: the six coordinate-free snapshots with their frozen order.
2. `T1-unordered`: the same six snapshots as a sorted, multiplicity-   preserving multiset with time labels and order removed.
3. `T1-endpoints`: the ordered labelled pair at steps 1 and 32.
4. `T1-terminal`: the single coordinate-free snapshot at step 32.

The primary temporal-order comparison is unordered to ordered. Endpoints and
terminal are separate temporal-reduction controls and were frozen before corpus
observation.

## Structural audits

- exact frozen protocol/tool/runner digests;
- exact rational normalization;
- translation by `(17, 11)`;
- intrinsic F1/L1 reflection invariance;
- transported frozen-probe reflection audit for B0/D1;
- matched D1 null/coupled occupied state and probe construction;
- ordered raw/normalized partition equivalence for Euler channels;
- source-boundary exclusion of P1, I1, S1, S2, H1, O1, and Gate 4 inputs;
- deterministic canonical JSON serialization and replay.

All required structural audits passed on every executed corpus.

## Evidence artifacts

Phase 1:

`_work/petra-vision-gate3-t1/phase1-t1.json`

SHA256:

`f60a07aea493619917098bbdbda2f521e335a8556c0672e49da26517c87d6bd6`

Phase 1 replay is byte-for-byte identical.

Held-out:

`_work/petra-vision-gate3-t1/heldout-t1.json`

SHA256:

`ddb94a766fea8c7aa2d415adbf7910efa1420213716d32e2fb6cfbd88060c322`

Held-out replay is byte-for-byte identical.

Extended:

`_work/petra-vision-gate3-t1/extended-t1.json`

SHA256:

`e704d5ccf52358184a63e8446c7613735556e31a2ca60b1af5c21cfe2bba8d18`

Extended replay is byte-for-byte identical.

The held-out 27-form family is the independent replication set. The extended
137-form corpus is the union of Phase 1 and held-out and is not treated as a
third independent replication.

## Complete discrimination matrix

| Corpus | Channel | Step zero | Terminal | Endpoints | Unordered | Ordered | Order gain | Order splits |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | B0 | 31/110 | 109/110 | 109/110 | 109/110 | 109/110 | +0 | 0 |
| Phase 1 | D1-null | 31/110 | 109/110 | 109/110 | 109/110 | 109/110 | +0 | 0 |
| Phase 1 | D1-coupled | 31/110 | 110/110 | 110/110 | 110/110 | 110/110 | +0 | 0 |
| Phase 1 | F1 | 47/110 | 58/110 | 58/110 | 58/110 | 58/110 | +0 | 0 |
| Phase 1 | L1 | 31/110 | 67/110 | 67/110 | 67/110 | 67/110 | +0 | 0 |
| Held-out | B0 | 9/27 | 27/27 | 27/27 | 27/27 | 27/27 | +0 | 0 |
| Held-out | D1-null | 9/27 | 27/27 | 27/27 | 27/27 | 27/27 | +0 | 0 |
| Held-out | D1-coupled | 9/27 | 27/27 | 27/27 | 27/27 | 27/27 | +0 | 0 |
| Held-out | F1 | 9/27 | 15/27 | 15/27 | 15/27 | 15/27 | +0 | 0 |
| Held-out | L1 | 9/27 | 16/27 | 16/27 | 16/27 | 16/27 | +0 | 0 |
| Extended | B0 | 35/137 | 136/137 | 136/137 | 136/137 | 136/137 | +0 | 0 |
| Extended | D1-null | 35/137 | 136/137 | 136/137 | 136/137 | 136/137 | +0 | 0 |
| Extended | D1-coupled | 35/137 | 137/137 | 137/137 | 137/137 | 137/137 | +0 | 0 |
| Extended | F1 | 56/137 | 73/137 | 73/137 | 73/137 | 73/137 | +0 | 0 |
| Extended | L1 | 35/137 | 83/137 | 83/137 | 83/137 | 83/137 | +0 | 0 |

## Prefix distinction growth

At every frozen prefix length, ordered and unordered prefixes induce the same
discrimination count and zero order-dependent collision-pair splits. The
complete ordered-prefix count sequences are:

| Corpus | Channel | t<=1 | t<=2 | t<=4 | t<=8 | t<=16 | t<=32 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | B0 | 42 | 42 | 42 | 71 | 107 | 109 |
| Phase 1 | D1-null | 42 | 42 | 42 | 71 | 107 | 109 |
| Phase 1 | D1-coupled | 55 | 103 | 110 | 110 | 110 | 110 |
| Phase 1 | F1 | 58 | 58 | 58 | 58 | 58 | 58 |
| Phase 1 | L1 | 46 | 59 | 67 | 67 | 67 | 67 |
| Held-out | B0 | 9 | 9 | 9 | 15 | 25 | 27 |
| Held-out | D1-null | 9 | 9 | 9 | 15 | 25 | 27 |
| Held-out | D1-coupled | 14 | 23 | 27 | 27 | 27 | 27 |
| Held-out | F1 | 15 | 15 | 15 | 15 | 15 | 15 |
| Held-out | L1 | 9 | 16 | 16 | 16 | 16 | 16 |
| Extended | B0 | 50 | 50 | 50 | 85 | 132 | 136 |
| Extended | D1-null | 50 | 50 | 50 | 85 | 132 | 136 |
| Extended | D1-coupled | 69 | 126 | 137 | 137 | 137 | 137 |
| Extended | F1 | 73 | 73 | 73 | 73 | 73 | 73 |
| Extended | L1 | 55 | 75 | 83 | 83 | 83 | 83 |

## Temporal-order classification

The primary T1 question has a negative result. On Phase 1, independent
held-out, and extended composition, normalized ordered signatures never refine
normalized unordered signatures for B0, D1 null, D1 coupled, F1, or L1.

Every unordered-to-ordered comparison has zero signature-class gain, zero
collision-pair splits, and zero introduced collision pairs. This remains true
at every frozen prefix length.

Therefore the bounded evidence does not support the hypothesis that temporal
ordering of the six frozen sampled states contributes additional discrimination
on the studied PETRA family.

## Raw representation-scale control

For B0, D1 null, D1 coupled, and L1, the raw Euler numerator audit gives the
same unordered discrimination partition as the exact normalized reader on every
corpus. F1 has no raw Euler numerator channel.

Therefore no T1 discrimination is being attributed to the q^k numerator scale
that could otherwise encode sample time after labels are removed.

## Replicated bounded terminal-sufficiency/no-recollision rabbit

A stronger post-result property emerged after the negative temporal-order
result. For every frozen channel, T1-terminal, T1-endpoints, T1-unordered, and
T1-ordered induce exactly the same complete collision partition.

| Corpus | Channel | Terminal | Endpoints | Unordered | Ordered | Terminal collision pairs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | B0 | 109/110 | 109/110 | 109/110 | 109/110 | 1 |
| Phase 1 | D1-null | 109/110 | 109/110 | 109/110 | 109/110 | 1 |
| Phase 1 | D1-coupled | 110/110 | 110/110 | 110/110 | 110/110 | 0 |
| Phase 1 | F1 | 58/110 | 58/110 | 58/110 | 58/110 | 77 |
| Phase 1 | L1 | 67/110 | 67/110 | 67/110 | 67/110 | 43 |
| Held-out | B0 | 27/27 | 27/27 | 27/27 | 27/27 | 0 |
| Held-out | D1-null | 27/27 | 27/27 | 27/27 | 27/27 | 0 |
| Held-out | D1-coupled | 27/27 | 27/27 | 27/27 | 27/27 | 0 |
| Held-out | F1 | 15/27 | 15/27 | 15/27 | 15/27 | 15 |
| Held-out | L1 | 16/27 | 16/27 | 16/27 | 16/27 | 11 |
| Extended | B0 | 136/137 | 136/137 | 136/137 | 136/137 | 1 |
| Extended | D1-null | 136/137 | 136/137 | 136/137 | 136/137 | 1 |
| Extended | D1-coupled | 137/137 | 137/137 | 137/137 | 137/137 | 0 |
| Extended | F1 | 73/137 | 73/137 | 73/137 | 73/137 | 92 |
| Extended | L1 | 83/137 | 83/137 | 83/137 | 83/137 | 54 |

The equality is exact partition equality, not merely equality of signature
counts.

### No sampled recollision

Across every pair in every corpus and channel, a sampled distinction either
never appears or, once it appears, remains present through step 32. No pair
diverges and then re-collides within the frozen sample schedule.

| Corpus | Pairs per channel | Channels | Sampled recollision pairs |
| --- | ---: | ---: | ---: |
| Phase 1 | 5995 | 5 | 0 |
| Held-out | 351 | 5 | 0 |
| Extended | 9316 | 5 | 0 |

### Synthetic non-generic falsification

After the Phase 1 result, a synthetic six-snapshot control was evaluated with
the frozen T1 reduction machinery. Two synthetic trajectories were constructed
with equal terminal snapshots but different ordered trajectories.

`left = (1, 2, 3, 4, 5, 9)`

`right = (1, 8, 7, 6, 5, 9)`

Their terminal reductions are equal, their ordered reductions are different,
and their frozen persistence classifier reports `diverges-then-collides-again`
with the sampled difference pattern `(False, True, True, True, False, False)`.

This falsifies the claim that terminal sufficiency or no-recollision is a
generic consequence of the T1 reduction semantics. The synthetic trajectories
are not claimed to arise from PETRA dynamics, so this control does not
establish non-genericity for every diffusion family.

### Held-out replication

The complete terminal/endpoints/unordered/ordered partition equality and
zero-recollision property independently replicate on the 27 held-out width-4
forms for all five frozen channels.

The result is therefore classified as Level 4 rather than as a Phase 1-only
coincidence.

### Extended composition

The same property remains valid on the 137-form union. For every channel and
reduction, the Phase 1 and held-out signature-digest sets are disjoint, so the
extended union introduces no cross-subset signature collision.

The extended result is compositionally stable but is not treated as an
independent third replication.

### Rabbit classification

**Level 4 — replicated bounded rabbit.**

The supported bounded claim is: on the frozen PETRA Phase 1 family and
independent held-out family, and consistently on their 137-form union, the
normalized terminal snapshot at step 32 induces exactly the same discrimination
partition as the complete six-snapshot ordered trajectory for B0, D1 null, D1
coupled, F1, and L1. Across the frozen sampled schedule, no compared pair
separates and later re-collides.

This is an empirical property of the frozen PETRA family and sample schedule.
It is not a theorem about arbitrary graphs, arbitrary diffusions, continuous
time, or unsampled intermediate times.

## D1 causal classification

The D1 null-to-coupled result must be kept separate from the replicated
terminal-sufficiency/no-recollision rabbit because the causal D1 gain does not
independently replicate held-out.

| Corpus | Reduction | D1 null | D1 coupled | Delta | Split pairs | Introduced |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | terminal | 109/110 | 110/110 | +1 | 1 | 0 |
| Phase 1 | endpoints | 109/110 | 110/110 | +1 | 1 | 0 |
| Phase 1 | unordered | 109/110 | 110/110 | +1 | 1 | 0 |
| Phase 1 | ordered | 109/110 | 110/110 | +1 | 1 | 0 |
| Held-out | terminal | 27/27 | 27/27 | +0 | 0 | 0 |
| Held-out | endpoints | 27/27 | 27/27 | +0 | 0 | 0 |
| Held-out | unordered | 27/27 | 27/27 | +0 | 0 | 0 |
| Held-out | ordered | 27/27 | 27/27 | +0 | 0 | 0 |
| Extended | terminal | 136/137 | 137/137 | +1 | 1 | 0 |
| Extended | endpoints | 136/137 | 137/137 | +1 | 1 | 0 |
| Extended | unordered | 136/137 | 137/137 | +1 | 1 | 0 |
| Extended | ordered | 136/137 | 137/137 | +1 | 1 | 0 |

On Phase 1, every D1 reduction splits exactly the retained reflected #23/#41
pair and introduces no collision pairs. The same single split persists in the
extended composition.

On held-out, D1 null and coupled are both already 27/27 under terminal,
endpoints, unordered, and ordered, so the D1 gain is zero. The Phase 1 causal
gain therefore persists in the union but does not independently replicate.

Because B0/D1 use the frozen coordinate-derived probe, this D1 causal result
remains probe-qualified.

## Historical #23/#41 control

On Phase 1 and extended, the retained reflected pair `G(G(G(T)),G(T,T))` /
`G(G(T,T),G(G(T)))` collides under every B0 and D1-null T1 reduction and is
split under every D1-coupled T1 reduction.

The pair is not present in the independent held-out family. Under T1 the D1
split is already completely visible in the terminal step-32 snapshot; temporal
order or intermediate-history retention adds no further split.

## Interpretation

T1 answers its primary attribution question negatively. Across the studied
bounded PETRA family, the order of the six frozen observations does not add
discrimination beyond the multiplicity-preserving collection of those same
states.

The stronger empirical result is that even this collection is unnecessary for
preserving the observed collision partition: the terminal step-32 snapshot
alone is sufficient on every frozen channel, independently replicates on
held-out forms, and remains stable on the full 137-form composition.

The no-recollision diagnostic provides the pairwise dynamic counterpart of this
terminal sufficiency over the sampled horizon. It does not imply that unsampled
intermediate times cannot re-collide.

The mechanism behind terminal sufficiency remains open. T1-v0 does not claim
graph reconstruction, spectral reconstruction, an invertibility theorem, or a
continuous-time monotonicity theorem.

## Claims supported

1. Temporal ordering adds no discrimination beyond the unordered sampled    state multiset on Phase 1.
2. The negative temporal-order result independently replicates on the    held-out family.
3. The negative temporal-order result remains stable on the 137-form    union.
4. Terminal, endpoints, unordered, and ordered induce the same exact    collision partition on every frozen channel.
5. Terminal sufficiency independently replicates on held-out forms.
6. No sampled pair diverges and then re-collides in Phase 1, held-out, or    extended.
7. A synthetic control shows that terminal sufficiency/no-recollision is    not forced by T1 reduction semantics alone.
8. The terminal-sufficiency/no-recollision result is a Level 4 replicated    bounded rabbit.
9. The rabbit remains compositionally stable on all 137 frozen forms.
10. Raw Euler numerator scale adds no unordered discrimination after exact     normalization.
11. The Phase 1 D1 null-to-coupled gain is already fully visible in the     terminal snapshot.
12. The Phase 1 D1 gain does not independently replicate held-out.

## Claims not supported

- temporal order is irrelevant for arbitrary graphs or arbitrary dynamics;
- terminal step 32 reconstructs the earlier trajectory numerically;
- terminal sufficiency holds outside the frozen PETRA families;
- no re-collision occurs between unsampled discrete steps;
- no re-collision occurs in continuous time;
- the frozen propagators are generically invertible;
- the terminal partition determines the Laplacian spectrum;
- the terminal partition determines P1 or I1 signatures;
- the terminal partition reconstructs graph geometry or syntax;
- the synthetic trajectories are PETRA-realizable;
- the D1 causal gain independently replicates held-out;
- D1 breaks horizontal reflection intrinsically;
- orientation-sensitive O1 diagnostics have been evaluated;
- Gate 4 adversarial mutation behavior has been evaluated.

## Final G3-T1 conclusion

G3-T1 is complete.

The frozen temporal-order attribution is negative: for every evaluated channel
and corpus, ordered observation produces no discrimination beyond the unordered
multiplicity-preserving collection of the same six exact normalized sampled
states.

A stronger property emerged post-result. The terminal step-32 snapshot alone
induces exactly the same complete discrimination partition as endpoints,
unordered observation, and the full ordered trajectory, with zero sampled
re-collisions. This property replicates on the independent held-out family,
survives deterministic replay, and remains compositionally stable on the full
137-form union.

The resulting terminal-sufficiency/no-recollision property is retained as a
Level 4 replicated bounded rabbit.

The D1 causal gain remains separate: it is real and terminal-visible on Phase
1, persists in extended composition, but does not independently replicate
held-out.

G3-T1 closes without activating O1 and without entering Gate 4.
