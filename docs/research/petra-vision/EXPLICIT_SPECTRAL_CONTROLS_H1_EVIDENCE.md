# PETRA VISION Gate 3 — G3-H1 heat-trace evidence

## Status

Complete.

Protocol:

`petra-vision-explicit-spectral-controls-h1-v0`

Evidence protocol:

`petra-vision-explicit-spectral-controls-h1-evidence-v0`

Gate boundary:

- S0/S1 complete;
- S2 complete;
- H1 complete;
- P1, I1, T1, and O1 not evaluated here.

## Provenance

Gate 3 foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

H1 protocol freeze:

`7dbcdcc` — `research: freeze Gate 3 heat-trace controls`

H1 implementation:

`a1ad50c` — `research: implement Gate 3 heat-trace controls`

H1 evidence runner:

`f82efe5` — `research: add Gate 3 heat-trace evidence runner`

H1 implementation SHA256:

`de672fc826c6c84aa40cba55e3090c5e1262a963f7bd0400e91c60150a7d9743`

H1 evidence runner SHA256:

`f3563c5c1e4867def36b2ba7873a88e8694ef52a75b072d901d45054c9c30901`

## Frozen observable

For a frozen global operator A with eigenvalues lambda_i:

`p_k = trace(A^k) = sum_i lambda_i^k`

and:

`p_0 = operator order`.

The frozen compression ladder is:

- M1 = `(p_0, p_1)`;
- M2 = `(p_0, p_1, p_2)`;
- M4 = `(p_0, ..., p_4)`;
- M8 = `(p_0, ..., p_8)`.

All values are reconstructed exactly from the frozen S1 characteristic
polynomial using exact rational arithmetic and Newton identities.

H1 is therefore a deterministic compression of S1 and cannot legitimately
split an S1 collision.

## Evidence artifacts

Phase 1:

`_work/petra-vision-gate3-h1/phase1-h1.json`

SHA256:

`2c26a00799f47cb2d37b844a40dd36df60d03bfd94c12de658a7985d20ea75de`

Phase 1 replay is byte-for-byte identical.

Held-out:

`_work/petra-vision-gate3-h1/heldout-h1.json`

SHA256:

`26c61b0fa4ff6c6d77f4ae1030cfc2c2016dca0d2d819fdd88f74b5b869fd1ca`

Held-out replay is byte-for-byte identical.

Extended:

`_work/petra-vision-gate3-h1/extended-h1.json`

SHA256:

`29fc051c7729e93481600207122526d0129f00c6bd6bfce039b9eed50a31fd90`

Extended replay is byte-for-byte identical.

The extended set is the union of Phase 1 and held-out and is not treated as
an independent third replication.

## Complete discrimination matrix

| Corpus | Substrate | M1 | M2 | M4 | M8 | S1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | B0 | 29/110 | 42/110 | 42/110 | 42/110 | 62/110 |
| Phase 1 | D1 | 39/110 | 52/110 | 60/110 | 61/110 | 67/110 |
| Phase 1 | F1 | 7/110 | 7/110 | 7/110 | 7/110 | 7/110 |
| Phase 1 | L1 | 13/110 | 13/110 | 13/110 | 13/110 | 13/110 |
| Held-out | B0 | 9/27 | 9/27 | 9/27 | 9/27 | 16/27 |
| Held-out | D1 | 9/27 | 11/27 | 16/27 | 16/27 | 16/27 |
| Held-out | F1 | 6/27 | 6/27 | 6/27 | 6/27 | 6/27 |
| Held-out | L1 | 4/27 | 4/27 | 4/27 | 4/27 | 4/27 |
| Extended | B0 | 31/137 | 50/137 | 50/137 | 50/137 | 78/137 |
| Extended | D1 | 44/137 | 63/137 | 76/137 | 77/137 | 83/137 |
| Extended | F1 | 11/137 | 11/137 | 11/137 | 11/137 | 11/137 |
| Extended | L1 | 14/137 | 14/137 | 14/137 | 14/137 | 14/137 |

## B0 classification

B0 is a valid negative compression result.

Phase 1:

- M1 retains 29 of 62 S1 signature classes;
- M2 rises to 42;
- M4 and M8 remain at 42.

Held-out:

- M1 through M8 all remain at 9;
- S1 has 16 classes.

Extended:

- M1 = 31;
- M2 = M4 = M8 = 50;
- S1 = 78.

Therefore the first eight exact spectral moments do not recover the full B0
spectral partition on the frozen domain.

The M2/M4/M8 plateau is an empirical property of the frozen corpus, not a
general theorem about graph spectra.

## D1 classification

D1 shows strong but incomplete spectral compression.

Phase 1:

`39 -> 52 -> 60 -> 61 -> 67`

for:

`M1 -> M2 -> M4 -> M8 -> S1`.

Held-out:

`9 -> 11 -> 16 -> 16 -> 16`.

Thus M4 already matches S1 on the held-out set.

Extended:

`44 -> 63 -> 76 -> 77 -> 83`.

Higher moments therefore add genuine discrimination for D1, but M8 does not
recover the full S1 partition on the complete frozen domain.

This retention behavior is corpus-dependent.

## F1 classification

F1 is the strongest bounded H1 compression result.

Phase 1:

- M1 = S1 = 7/110;
- the equality holds on the full collision partition, not only on the count.

Held-out:

- M1 = S1 = 6/27;
- this independently repeats the phenomenon;
- the held-out set contains nineteen F1 operators of order four.

Extended:

- M1 = S1 = 11/137;
- zero S1 collision pairs are split;
- zero collision pairs are introduced;
- zero cross-partition collision pairs are introduced.

Therefore, on all 137 frozen PETRA forms, the two-scalar signature:

`(operator order, operator trace)`

induces exactly the same discrimination partition as the complete exact F1
operator spectrum.

This is classified as:

**bounded lossless discrimination compression on the frozen PETRA F1 family.**

The word `lossless` refers specifically to discrimination partition
preservation. It does not claim that M1 reconstructs every eigenvalue or the
full characteristic polynomial numerically.

### Non-generic control

The equality M1 = S1 is not forced by the symmetric inverse-distance
normalization law itself.

Two synthetic three-factor controls were constructed using exactly the frozen
F1 propagation-matrix normalization and reciprocal-integer pair weights.

Distance triples:

- A = `(2, 10, 10)`;
- B = `(3, 6, 6)`.

Both produce:

`M1 = ((3, 1), (25, 12))`

but their exact S1 spectrum digests differ:

- A: `23883a5cf6f4`;
- B: `ee26b51e4f49`.

Thus equal M1 does not generically imply equal S1 for arbitrary operators built
with the same normalization law.

The observed F1 lossless discrimination compression must therefore be
attributed to the frozen geometry-generated F1 operator family and/or bounded
domain, not to a universal matrix identity.

### Nontrivial observed orders

For the Phase 1 order-three F1 subset:

- 38 forms;
- 4 distinct M1 signatures;
- 4 distinct S1 spectra;
- every M1 class determines one S1 class.

For the held-out order-four F1 subset:

- 19 forms;
- 4 distinct M1 signatures;
- 4 distinct S1 spectra;
- every M1 class determines one S1 class.

This strengthens the bounded observation beyond trivial order-zero,
order-one, or order-two cases.

## L1 classification

L1 also has exact M1-to-S1 discrimination preservation, but here the reason is
structurally understood.

For an `m x n` rectangular grid:

`p_0 = mn`.

The number of grid edges is:

`|E| = (m - 1)n + m(n - 1) = 2mn - m - n`.

For the combinatorial Laplacian:

`p_1 = trace(L) = 2|E| = 4mn - 2m - 2n`.

Therefore:

`mn = p_0`

and:

`m + n = (4p_0 - p_1) / 2`.

The unordered dimensions `{m, n}` are the two roots of:

`x^2 - (m+n)x + mn = 0`.

Hence M1 determines the unordered rectangular dimensions, and those dimensions
determine the complete L1 rectangular-grid Laplacian spectrum.

A synthetic verification over all unordered rectangles with sides from 1
through 50 checked 1275 rectangles with exact recovery.

Accordingly, L1 M1=S1 is a structural property of this rectangular operator
family rather than merely a frozen-corpus coincidence.

This does not imply the same result for arbitrary graphs or arbitrary lattice
domains.

## Cross-partition behavior

Relative to S1, the extended-domain newly introduced collision pairs include:

### B0

- M1: 357 total, of which 85 are cross-partition;
- M2: 147 total, of which 16 are cross-partition;
- M4: 147 total, of which 16 are cross-partition;
- M8: 147 total, of which 16 are cross-partition.

### D1

- M1: 167 total, of which 35 are cross-partition;
- M2: 66 total, with zero cross-partition contribution;
- M4: 26 total, with zero cross-partition contribution;
- M8: 22 total, with zero cross-partition contribution.

### F1

All truncations introduce zero collision pairs, including zero cross-partition
collisions.

### L1

All truncations introduce zero collision pairs, including zero cross-partition
collisions.

## Historical #23/#41 control

The retained reflected/reordered #23/#41 pair remains colliding under every H1
truncation wherever present.

This is the required behavior for a coordinate-free observable derived only
from S1.

H1 does not introduce orientation information.

## Anti-false-rabbit checks

All frozen H1 invariants hold:

- H1 never splits an S1 collision;
- M2 refines or equals M1;
- M4 refines or equals M2;
- M8 refines or equals M4;
- #23/#41 does not separate;
- H1 uses no probe, impulse response, temporal trajectory, S2 factor order, or
  orientation channel;
- all three corpus artifacts replay deterministically byte-for-byte.

No positive H1 finding depends on violation of the frozen reader boundary.

## Scientific decision

G3-H1 succeeds as an attribution control.

The four substrates exhibit materially different compression behavior:

- B0: low-order spectral moments retain only a bounded subset of S1
  discrimination;
- D1: increasingly higher moments recover progressively more spectral
  discrimination but remain incomplete on the extended domain;
- F1: M1 preserves the complete S1 discrimination partition on all 137 frozen
  forms, despite this not being a generic property of normalized
  inverse-distance operators;
- L1: M1 preserves S1 because rectangular dimensions are algebraically
  recoverable from order and trace.

This demonstrates that the amount and organization of spectral information
visible to low-order heat-trace moments is strongly substrate-dependent.

## Non-claims

G3-H1 does not establish:

- universal spectral reconstruction from low-order moments;
- universal F1 M1 sufficiency;
- universal injectivity;
- recovery of PETRA syntax or AST identity;
- orientation recovery;
- probe independence;
- impulse-response attribution;
- temporal attribution;
- physical heat diffusion or physical time;
- robustness beyond the frozen domain.

In particular, the F1 result is a lossless discrimination compression result
for the frozen PETRA F1 family, not a theorem that order and trace determine
arbitrary F1 spectra.

## Gate boundary

G3-H1 is complete.

The next declared Gate 3 family is G3-P1 probe ablation.

P1 must receive its own protocol freeze before any P1 corpus result is
observed.

G3-I1, G3-T1, and G3-O1 remain inactive.
