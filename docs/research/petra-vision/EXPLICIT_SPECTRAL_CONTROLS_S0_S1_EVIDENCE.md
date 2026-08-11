# PETRA VISION Gate 3 — G3-S0/S1 evidence

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Complete bounded evidence for G3-S0/S1.

Parent issue: #200.

Protocol:

`petra-vision-explicit-spectral-controls-s0-s1-v0`

Evidence protocol:

`petra-vision-explicit-spectral-controls-s0-s1-evidence-v0`

The protocol, implementation, structural tests, and evidence runner were frozen
before corpus discrimination was observed.

G3-P1, G3-I1, G3-T1, and G3-O1 were not executed as part of this evidence.

## Frozen implementation provenance

Gate 3 protocol freeze:

`3fb958c0da78d6b67d9035cb5f57a53af8628a46`

Temporal hypothesis import:

`6ec5f55222983a7cd29465feca785ce74991738e`

S0/S1 protocol freeze:

`3ad8eb5`

S0/S1 implementation:

`c9eff4e`

Evidence runner freeze:

`b73db2c16524365c74e2266c2d19c17aee62426b`

S0/S1 implementation SHA256:

`21870c7f06f09d9ab50bed318d2a1eeaf7640e11f4e5ff88a57ca61d1387e186`

Evidence runner SHA256:

`f1ad5a77ad01e7b3b035a4b6be4c983a688afe44a570940042ef54c034d3361e`

Environment:

- SymPy `1.14.0`;
- exact rational/integer arithmetic;
- no NumPy/SciPy eigensolver;
- no floating-point spectral tolerance.

## Determinism

All three frozen corpus partitions were generated separately.

Phase 1 evidence SHA256:

`036562a060374eea1a6bc889bc197810389bd7be72b658a14e44ded9f1ea6302`

Held-out evidence SHA256:

`e77e373042359b259b0a0b84fefb8ec45d9783a2c5aeebd518bc9df5cc91ac2f`

Extended evidence SHA256:

`f7de93da4e900463040b84190f77583d1cc48d4af88d9450a7d0796aa52ca427`

Phase 1, held-out, and extended deterministic replays are byte-for-byte
identical to their corresponding original JSON evidence artifacts.

Generated JSON remains research-working evidence under `_work/`; the digests,
source provenance, protocol, results, and bounded decision are versioned here.

## Result matrix

| Substrate | Corpus | S0 operator | S0 intrinsic | S1 exact spectrum | S0→S1 gain | Pairs split | Pairs introduced |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B0 | Phase 1 | 42/110 | n/a | 62/110 | +20 | 102 | 0 |
| B0 | Held-out | 9/27 | n/a | 16/27 | +7 | 29 | 0 |
| B0 | Extended | 50/137 | n/a | 78/137 | +28 | 147 | 0 |
| D1 | Phase 1 | 52/110 | n/a | 67/110 | +15 | 50 | 0 |
| D1 | Held-out | 11/27 | n/a | 16/27 | +5 | 16 | 0 |
| D1 | Extended | 63/137 | n/a | 83/137 | +20 | 66 | 0 |
| F1 | Phase 1 | 7/110 | 47/110 | 7/110 | 0 | 0 | 0 |
| F1 | Held-out | 6/27 | 9/27 | 6/27 | 0 | 0 | 0 |
| F1 | Extended | 11/137 | 56/137 | 11/137 | 0 | 0 | 0 |
| L1 | Phase 1 | 13/110 | 31/110 | 13/110 | 0 | 0 | 0 |
| L1 | Held-out | 4/27 | 9/27 | 4/27 | 0 | 0 | 0 |
| L1 | Extended | 14/137 | 35/137 | 14/137 | 0 | 0 | 0 |

The Gate 1A reflected/reordered `#23/#41` pair remains colliding under both
the S0 operator profile and S1 exact spectrum wherever both forms are present.
The pair also remains colliding under the F1 and L1 S0 intrinsic controls.

## B0 classification

**Classification: positive bounded spectral attribution.**

The exact occupied-cell combinatorial-Laplacian spectrum adds reproducible
coordinate-free discrimination beyond the declared elementary operator
profile:

- Phase 1: `42 -> 62`;
- held-out: `9 -> 16`;
- extended: `50 -> 78`.

The spectral refinement splits collision pairs and introduces none in all
three corpus partitions.

The spectrum remains substantially non-injective. It does not explain the
much stronger frozen graph-Laplacian v1 dynamic reader by itself.

## D1 classification

**Classification: positive bounded spectral attribution, insufficient to
explain the Gate 2 dynamic result.**

The exact weighted D1 Laplacian spectrum adds reproducible discrimination:

- Phase 1: `52 -> 67`;
- held-out: `11 -> 16`;
- extended: `63 -> 83`.

Again, collision pairs are split and none are introduced.

However, the frozen Gate 2 D1 dynamic reader produced:

- `110/110`;
- `27/27`;
- `137/137`.

Therefore the perfect bounded D1 dynamic separation cannot be attributed to
the operator spectrum alone.

This preserves the Gate 2 probe qualification and makes G3-P1/G3-I1 necessary
for D1.

## F1 classification

**Classification: valid negative spectral attribution.**

The exact characteristic polynomial of the frozen rational F1 propagation
operator induces exactly the same equivalence partition as the elementary
operator profile on every corpus partition:

- Phase 1: `7 -> 7`;
- held-out: `6 -> 6`;
- extended: `11 -> 11`.

No collision pair is split or introduced.

The separate intrinsic factor-state control is much richer:

- `47/110`;
- `9/27`;
- `56/137`.

The frozen Gate 2 F1 joint dynamic reader yielded:

- `75/110`;
- `18/27`;
- `93/137`.

Therefore the Gate 2 F1 gain is not explained by operator spectrum alone.

Later Gate 3 attribution must keep separate:

- intrinsic factor state;
- propagation operator;
- response under propagation;
- temporal observation.

No claim is made here about which later contribution is sufficient.

## L1 classification

**Classification: valid negative spectral attribution.**

The exact rectangular-grid Laplacian spectrum adds zero discrimination beyond
the elementary L1 operator profile:

- Phase 1: `13 -> 13`;
- held-out: `4 -> 4`;
- extended: `14 -> 14`.

This result is consistent with the protocol-level structural fact frozen
before evidence observation: the uniform L1 propagation operator depends only
on the dimensions of the full rectangular lattice.

Occupancy is not encoded in that operator. It enters only through the initial
binary field.

The separate intrinsic occupancy-state controls yield:

- `31/110`;
- `9/27`;
- `35/137`.

The frozen Gate 2 L1 dynamic reader yielded:

- `67/110`;
- `16/27`;
- `83/137`.

Therefore the L1 dynamic gain is not explained by the spectrum of the uniform
medium alone.

Later Gate 3 attribution must test the response of the frozen occupancy field
under propagation and the contribution of temporal observation.

## Cross-substrate decision

G3-S0/S1 is a **mixed bounded result**:

- B0: positive spectral attribution;
- D1: positive spectral attribution, dynamically insufficient;
- F1: valid negative spectral attribution;
- L1: valid negative spectral attribution.

This is not a failure of Gate 3. The purpose of the gate is causal
attribution, and negative attribution is an explicit valid outcome.

The result narrows the next questions:

1. component/factor-local spectra must be separated from global spectra;
2. heat-trace compression must be compared with the exact spectrum;
3. D1 probe dependence must be resolved explicitly;
4. dynamic response must remain separated from static spectrum;
5. temporal attribution must remain deferred until its own protocol is
   activated.

## Non-claims

This evidence does not establish:

- spectral uniqueness;
- universal graph or geometry reconstruction;
- complete PETRA decoding;
- intrinsic orientation or reflection breaking;
- robustness;
- physical propagation;
- physical time or spacetime;
- theorem-level injectivity.

## Decision

G3-S0/S1 is complete for the frozen bounded 110/27/137 corpus partitions.

Proceed next to G3-S2 component/factor spectral controls.

G3-H1 follows S2.

G3-P1/G3-I1 follow the spectral-control family.

G3-T1 remains inactive.
