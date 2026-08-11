# PETRA VISION Gate 3 — G3-S2 local spectral controls evidence

## Status

Complete.

G3-S2 evaluates exact local spectra on the native structural units frozen by
the Gate 3 S2 protocol.

This evidence record covers only S2.

H1, P1, I1, T1, and O1 remain outside this experiment and were not executed.

## Protocol

Protocol:

`petra-vision-explicit-spectral-controls-s2-v0`

Protocol document:

`EXPLICIT_SPECTRAL_CONTROLS_S2_PROTOCOL.md`

Protocol freeze commit:

`d80abf3`

Implementation commit:

`e4ae805`

Evidence runner commit:

`171571d8be3fab9d4ab5f2c0724c952fcd32f020`

Evidence protocol:

`petra-vision-explicit-spectral-controls-s2-evidence-v0`

## Frozen readers

### B0

Native units are connected components of the frozen occupied 4-neighbor graph.

Each unit contributes the exact characteristic polynomial of its unweighted
combinatorial Laplacian.

The S2 reader is the unordered multiplicity-preserving multiset of those exact
local spectra.

### D1

Native units are the frozen original components before distance-2 clearance
bridges are added.

Only original local edges of weight 2 are included in each local operator.

Clearance bridges are explicitly excluded.

The S2 reader is the unordered multiplicity-preserving multiset of the exact
local spectra.

### F1

Native units are exactly the immediate native FGS factors returned by the
frozen Gate 1B geometry-only factorization.

No recursive factor decomposition is used by the primary S2 reader.

Each factor contributes the exact characteristic polynomial of the B0
unweighted occupied-graph Laplacian of its canonical factor geometry.

The reader is unordered and multiplicity preserving.

### L1

S2 is not applicable.

The frozen L1 substrate is one connected rectangular lattice. No artificial
component, row, tile, or FGS partition is introduced for S2.

## Reproducibility

All three corpus observations were replayed byte-for-byte.

### Phase 1

Forms: 110

Artifact:

`_work/petra-vision-gate3-s2/phase1-s2.json`

SHA256:

`cd1535a2219f5a8ba4b3d593f1a349d724c7a393278e0be7c83dfa982d33c78f`

Replay: byte-for-byte identical.

### Held-out

Forms: 27

Artifact:

`_work/petra-vision-gate3-s2/heldout-s2.json`

SHA256:

`4a007d2211ce7fc41b4f28b8b5e66c431cbe6920f83f48053399851fbdbb2719`

Replay: byte-for-byte identical.

### Extended

Forms: 137

Artifact:

`_work/petra-vision-gate3-s2/extended-s2.json`

SHA256:

`377d0bc087e1fd5ea4f8a1a356aea4f1eee4b687863271bf8cef631848cd22ce`

Replay: byte-for-byte identical.

## Source provenance

S2 implementation SHA256:

`d5bd857fa25a2464ba2f701333a4cec99e81627e31230e239bf685b0f0caa3d3`

Evidence runner SHA256:

`5b39dc8e377727eb65f8e9515adc8f5d10c84f3ebf22789d7903962d67772f0a`

## Results

### B0

| Corpus | S1 global | S2 local | Delta | S1 pairs split by S2 | Pairs introduced by S2 |
|---|---:|---:|---:|---:|---:|
| Phase 1 | 62/110 | 62/110 | 0 | 0 | 0 |
| Held-out | 16/27 | 16/27 | 0 | 0 | 0 |
| Extended | 78/137 | 78/137 | 0 | 0 | 0 |

On all observed corpora, preserving the individual connected-component spectra
does not refine the partition induced by the global B0 spectrum.

This is compatible with the frozen block-diagonal structure of B0.

No claim is made that this equivalence holds for arbitrary graphs or arbitrary
corpora.

### D1

| Corpus | S1 coupled | S2 pre-bridge local | Delta | S1 pairs split by S2 | Pairs introduced by S2 |
|---|---:|---:|---:|---:|---:|
| Phase 1 | 67/110 | 62/110 | -5 | 0 | 20 |
| Held-out | 16/27 | 16/27 | 0 | 0 | 0 |
| Extended | 83/137 | 78/137 | -5 | 0 | 20 |

On Phase 1 and the extended corpus, removing the clearance bridges before
spectral observation loses discrimination.

The 20 introduced collision pairs in the extended corpus are exactly the
Phase 1 contribution; the held-out subset introduces none.

This supports the bounded attribution that some exact D1 spectral information
is carried by the frozen clearance coupling rather than by the spectra of the
original disconnected units alone.

S1 and S2 are different causal objects here and neither is claimed to be a
formal refinement of the other in general.

### F1

#### Against global F1 operator spectrum

| Corpus | S1 global | S2 local | Delta | S1 pairs split by S2 | Pairs introduced by S2 |
|---|---:|---:|---:|---:|---:|
| Phase 1 | 7/110 | 51/110 | +44 | 1511 | 44 |
| Held-out | 6/27 | 10/27 | +4 | 50 | 21 |
| Extended | 11/137 | 61/137 | +50 | 1803 | 65 |

The exact local factor spectra contain substantially different information from
the spectrum of the frozen F1 proximity propagation operator.

These two readers are not formal refinements of one another.

#### Against frozen F1 intrinsic state

| Corpus | S0 intrinsic | S2 local | Delta | Intrinsic pairs split by S2 | Pairs introduced by S2 |
|---|---:|---:|---:|---:|---:|
| Phase 1 | 47/110 | 51/110 | +4 | 14 | 0 |
| Held-out | 9/27 | 10/27 | +1 | 4 | 0 |
| Extended | 56/137 | 61/137 | +5 | 18 | 0 |

This is the primary positive S2 result.

On every observed corpus, the exact local spectra of the immediate native FGS
factors strictly refine the frozen six-feature intrinsic F1 representation:

- existing intrinsic distinctions are preserved;
- additional intrinsic collision pairs are separated;
- no new collision pair is introduced.

The held-out result is especially important because it introduces exact
spectral witnesses not present among the Phase 1 split witnesses while
preserving the same refinement relation.

On the combined 137-form corpus:

- all 14 Phase 1 split pairs remain split;
- all 4 held-out split pairs remain split;
- there are 18 split pairs total;
- there are no additional cross-partition split pairs;
- there are no cross-partition collisions introduced.

Therefore the two observed witness families coexist without contradiction on
the combined corpus.

## Local spectral witness family

Inspection of the Phase 1 F1 split pairs shows a small number of recurring
primitive spectral witnesses rather than 14 unrelated effects.

The observed qualitative pattern distinguishes different internal placements
or separations while preserving reflection equivalence.

Examples include distinctions consistent with:

- peripheral versus more central placement;
- adjacent versus separated internal structure.

The held-out corpus introduces a new arity-4 witness family with new exact
spectral signatures.

Within that family, the two outer placements share one spectrum and the two
inner placements share another spectrum.

This is consistent with a reflection-invariant distinction related to position
relative to the boundary rather than recovery of absolute left/right
orientation.

This interpretation is an empirical characterization of the frozen corpus,
not a theorem about Laplacian spectra.

## Historical collision #23/#41

The known reflection-related pair:

`G(G(G(T)),G(T,T))`

and

`G(G(T,T),G(G(T)))`

remains colliding under S2 wherever applicable.

S2 therefore does not provide evidence of orientation recovery for this pair.

The persistence of this collision is compatible with the coordinate-free,
unordered, reflection-equivariant construction of the reader.

## Classification

G3-S2 is classified as follows.

### B0

Valid neutral result.

Native component spectral factorization does not increase discrimination over
the global exact B0 spectrum on the frozen corpora.

### D1

Valid bounded attribution result.

Some exact spectral discrimination of the coupled D1 substrate is absent when
the clearance bridges are removed.

### F1

Positive bounded local spectral attribution result.

Exact spectra of immediate native FGS factor geometry preserve all distinctions
of the frozen intrinsic six-feature representation and add further
discrimination on Phase 1, held-out, and extended corpora.

The positive result replicates on held-out data and remains compatible on the
combined 137-form corpus.

### L1

Not applicable for S2 by protocol.

## What this evidence does not establish

This evidence does not establish:

- universal injectivity;
- universal spectral uniqueness;
- recovery of the PETRA AST;
- absolute orientation or left/right recovery;
- separation of the historical #23/#41 reflection collision;
- that local factor spectra alone explain the full Gate 2 F1 dynamic result;
- robustness outside the frozen corpora;
- a theorem that the observed positional interpretation holds for arbitrary
  PETRA geometries;
- physical or cosmological equivalence.

In particular, F1 S2 reaches 61/137 signatures while the frozen Gate 2 dynamic
F1 reader reaches 93/137.

A substantial attribution gap therefore remains.

That gap is intentionally left to later Gate 3 controls in their frozen order.

## Gate boundary

G3-S2 is complete.

The next Gate 3 family is G3-H1 heat trace.

P1, I1, T1, and O1 remain inactive until their respective turn.
