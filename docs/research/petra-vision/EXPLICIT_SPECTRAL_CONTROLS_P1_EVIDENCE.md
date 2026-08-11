# PETRA VISION Gate 3 — G3-P1 probe-ablation evidence

## Status

Complete.

Protocol:

`petra-vision-explicit-spectral-controls-p1-v0`

Evidence protocol:

`petra-vision-explicit-spectral-controls-p1-evidence-v0`

Gate boundary:

- S0/S1 complete;
- S2 complete;
- H1 complete;
- P1 complete;
- I1, T1, and O1 not evaluated here.

## Provenance

Gate 3 foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

P1 protocol freeze:

`e59facf` — `research: freeze Gate 3 probe ablation`

P1 implementation:

`8f6806b` — `research: implement Gate 3 probe ablation`

P1 evidence runner:

`f09ffaa` — `research: add Gate 3 probe evidence runner`

P1 protocol SHA256:

`06406f66990624f44587717a983bb748a81cbcf4783af86afb92b10671cf07e7`

P1 implementation SHA256:

`5915f11db4d49e352e2ea5b2f01c43a05b3a61b16b34963c819f41393210deae`

P1 evidence runner SHA256:

`196aefe2a6e37c56a75113aea9eff75684742f2fc8e8a09475689641c91dfd7d`

The implementation passed 33 structural pre-corpus tests.

The combined implementation + evidence-runner suite passed 48 pre-corpus tests after
replacing one self-referential source-string guard with an AST check for actual
frozen-corpus calls.

No P1 corpus was observed before protocol, implementation, and evidence-runner
freeze.

## Frozen probe family

P1 evaluates B0 and D1 only.

The five frozen probes are:

- `minimum`: one unit at the lexicographically minimum occupied cell of each
  native four-neighbor component;
- `reflected-minimum`: the exact transported horizontal-reflection counterpart
  of `minimum`;
- `local-degree`: exact unweighted four-neighbor occupied-cell degree at every
  occupied vertex, excluding D1 distance-2 bridge information;
- `constant`: value 1 at every occupied vertex;
- `zero`: value 0 at every occupied vertex.

F1 and L1 are explicitly N/A for this probe ablation because changing their
frozen initial states would change representation semantics rather than ablate
the selected B0/D1 point probe.

For every D1 mode, matched null and coupled operators receive the byte-for-byte
same initial-state tuple.

## Evidence artifacts

Phase 1:

`_work/petra-vision-gate3-p1/phase1-p1.json`

SHA256:

`f5b785a7404ed01413c2343206eabb063b35d95bec3da00c4d0ad5446b928473`

Phase 1 replay is byte-for-byte identical.

Held-out:

`_work/petra-vision-gate3-p1/heldout-p1.json`

SHA256:

`8b718b0dd22b11a841146d91b6ecd73768b404773d35c0e1853e70a89237c2a3`

Held-out replay is byte-for-byte identical.

Extended:

`_work/petra-vision-gate3-p1/extended-p1.json`

SHA256:

`bddfdd20f21c44c805fcb319b8f19f581ac3e59920ac120017791b5b1467fc8c`

Extended replay is byte-for-byte identical.

The extended set is the union of Phase 1 and held-out and is not treated as an
independent third replication.

## Complete discrimination matrix

| Corpus | Probe | Step zero | B0 dynamic | D1 null | D1 coupled | D1 delta | Split pairs | Introduced |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | minimum | 31/110 | 109/110 | 109/110 | 110/110 | +1 | 1 | 0 |
| Phase 1 | reflected-minimum | 31/110 | 109/110 | 109/110 | 110/110 | +1 | 1 | 0 |
| Phase 1 | local-degree | 42/110 | 62/110 | 62/110 | 67/110 | +5 | 20 | 0 |
| Phase 1 | constant | 29/110 | 29/110 | 29/110 | 29/110 | +0 | 0 | 0 |
| Phase 1 | zero | 29/110 | 29/110 | 29/110 | 29/110 | +0 | 0 | 0 |
| Held-out | minimum | 9/27 | 27/27 | 27/27 | 27/27 | +0 | 0 | 0 |
| Held-out | reflected-minimum | 9/27 | 27/27 | 27/27 | 27/27 | +0 | 0 | 0 |
| Held-out | local-degree | 9/27 | 16/27 | 16/27 | 16/27 | +0 | 0 | 0 |
| Held-out | constant | 9/27 | 9/27 | 9/27 | 9/27 | +0 | 0 | 0 |
| Held-out | zero | 9/27 | 9/27 | 9/27 | 9/27 | +0 | 0 | 0 |
| Extended | minimum | 35/137 | 136/137 | 136/137 | 137/137 | +1 | 1 | 0 |
| Extended | reflected-minimum | 35/137 | 136/137 | 136/137 | 137/137 | +1 | 1 | 0 |
| Extended | local-degree | 50/137 | 78/137 | 78/137 | 83/137 | +5 | 20 | 0 |
| Extended | constant | 31/137 | 31/137 | 31/137 | 31/137 | +0 | 0 | 0 |
| Extended | zero | 31/137 | 31/137 | 31/137 | 31/137 | +0 | 0 | 0 |

## Minimum and reflected-minimum classification

The coordinate-derived `minimum` probe reproduces Gate 2 exactly.

Phase 1:

- B0 = 109/110;
- D1 null = 109/110;
- D1 coupled = 110/110;
- coupling splits exactly one null collision pair and introduces zero;
- that split is the retained historical reflected/reordered #23/#41 pair.

Held-out:

- B0 = D1 null = D1 coupled = 27/27;
- no incremental null-to-coupled split is available because the held-out
  partition is already fully discriminated under the null.

Extended:

- B0 = D1 null = 136/137;
- D1 coupled = 137/137;
- the same single #23/#41 split is retained.

`reflected-minimum` gives the same discrimination counts and the required
reflection-transport behavior.

These coordinate-derived probes therefore reproduce the Gate 2 perfect D1
headline result while retaining its known orientation/probe qualification.

## Intrinsic local-degree causal classification

`local-degree` is coordinate-free, vertex-permutation equivariant,
horizontal-reflection equivariant, and contains no D1 bridge information.

Its step-zero and dynamic results are:

Phase 1:

`42/110 step-zero -> 62/110 D1 null -> 67/110 D1 coupled`

The D1 coupling:

- adds 5 signature classes;
- splits 20 null collision pairs;
- introduces zero collision pairs.

Held-out:

`9/27 step-zero -> 16/27 D1 null -> 16/27 D1 coupled`

The D1 coupling:

- adds zero signature classes;
- splits zero collision pairs;
- introduces zero collision pairs.

Extended:

`50/137 step-zero -> 78/137 D1 null -> 83/137 D1 coupled`

All 20 Phase 1 split pairs persist in the union.

There are:

- zero additional held-out split pairs;
- zero additional cross-partition split pairs beyond the Phase 1 effect;
- zero introduced collision pairs.

Therefore the intrinsic-probe D1 coupling gain is a real bounded Phase 1
effect, but it does not independently replicate on the held-out partition.

It must not be classified as a replicated coupling-gain result.

## Constant and zero controls

`constant` and `zero` retain only the information visible through state
multiplicity / occupied-vertex count under the frozen reader.

Phase 1:

- step zero = B0 = D1 null = D1 coupled = 29/110.

Held-out:

- all channels = 9/27.

Extended:

- all channels = 31/137.

No propagation gain and no D1 coupling gain is observed for either control.

This is the expected negative-excitation behavior.

## Historical #23/#41 control

For `local-degree`, `constant`, and `zero`, the exact reflected/reordered
#23/#41 pair remains colliding under:

- B0;
- D1 matched null;
- D1 coupled.

This holds wherever the pair is present.

Therefore the intrinsic/reflection-equivariant probes do not create orientation
information.

Under `minimum` and `reflected-minimum`, D1 coupled separates the pair while the
matched null does not, reproducing the already qualified coordinate-derived
Gate 2 effect.

## Replicated P1-local-degree / S1 partition equivalence

A post-extended rabbit-watch audit compared exact collision partitions from the
already observed P1 artifacts against the frozen S1 exact-spectrum partitions.

It did not compare signature counts alone.

| Corpus | B0 P1 local-degree | B0 S1 | B0 collision pairs | D1 P1 local-degree coupled | D1 S1 | D1 collision pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | 62/110 | 62/110 | 63 | 67/110 | 67/110 | 43 |
| Held-out | 16/27 | 16/27 | 11 | 16/27 | 16/27 | 11 |
| Extended | 78/137 | 78/137 | 74 | 83/137 | 83/137 | 54 |

For every declared corpus:

- B0 `local-degree` dynamics induces exactly the B0 S1 collision partition;
- D1 matched-null `local-degree` dynamics induces exactly the B0 S1 collision
  partition;
- D1 coupled `local-degree` dynamics induces exactly the D1 S1 collision
  partition.

The held-out 27-form partition independently repeats the exact partition
equivalence observed on Phase 1.

The extended 137-form union preserves it without additional cross-partition
mismatch.

Under the project rabbit-watch rubric this is classified as a replicated
Level-4 bounded result.

A precise description is:

**bounded replicated spectral-partition equivalence between the frozen
P1-local-degree dynamic observable and the corresponding S1 global-spectrum
partition on the PETRA family.**

The word `equivalence` refers only to the induced discrimination partition on
the frozen finite domain.

It does not mean that the trajectory numerically reconstructs the
characteristic polynomial or eigenvalue multiset.

## Non-generic falsification

The P1-local-degree / S1 equivalence is not a generic consequence of Laplacian
dynamics with a degree probe.

### Generic B0-style graph control

Two connected 3-regular graphs were used:

- `K3,3`;
- the triangular prism.

Both have identical degree probe:

`(3, 3, 3, 3, 3, 3)`.

Their exact combinatorial-Laplacian characteristic polynomials differ:

`K3,3`:

`(1, -18, 126, -432, 729, -486, 0)`

Triangular prism:

`(1, -18, 126, -428, 705, -450, 0)`

Yet their declared degree-probe trajectories are identical.

The exact reason is that the degree probe is `3 * 1` and every Laplacian
annihilates the constant vector.

Therefore different spectra can produce identical local-degree dynamics.

### D1-style weighted control

A synthetic six-vertex cycle supplies the common local degree probe:

`(2, 2, 2, 2, 2, 2)`.

Local cycle edges have weight 2.

Two weighted operators differ only by adding one versus two weight-1
nonlocal bridge edges.

Their exact characteristic polynomials are:

A:

`(1, -26, 256, -1184, 2544, -2016, 0)`

B:

`(1, -28, 300, -1536, 3744, -3456, 0)`

The spectra differ while the local-degree trajectories remain identical.

This synthetic D1-style construction is not claimed to be a realizable PETRA
geometry. Its purpose is only to falsify generic algebraic necessity.

Therefore the replicated PETRA partition equivalence is not forced by a
universal Laplacian identity.

It remains a bounded property of the frozen PETRA geometry/operator family.

## Step-zero attribution

The intrinsic `local-degree` result is not merely a static degree-multiset
effect.

Phase 1:

- step-zero = 42;
- B0 / D1-null dynamic = 62;
- D1-coupled dynamic = 67.

Held-out:

- step-zero = 9;
- B0 / D1-null dynamic = 16;
- D1-coupled dynamic = 16.

Extended:

- step-zero = 50;
- B0 / D1-null dynamic = 78;
- D1-coupled dynamic = 83.

Propagation therefore exposes substantial discrimination beyond the initial
degree multiset on every declared corpus.

## Translation, reflection, and source-boundary audits

Every frozen P1 mode passed translation by:

`(+17, +11)`.

Every frozen mode passed its declared reflection audit:

- intrinsic `local-degree`, `constant`, and `zero` signatures are invariant
  under horizontal reflection;
- `minimum` and `reflected-minimum` satisfy the exact transported-pair
  identities.

The P1 reader consumes only:

- the frozen B0/D1 substrate/operator;
- the declared initial state;
- exact frozen dynamics;
- global state-value multisets at steps 1, 2, 4, 8, 16, and 32.

The `local-degree` constructor uses only native unweighted four-neighbor
adjacency.

No S1/S2/H1 value reaches the P1 primary reader.

S1 artifacts were used only after all P1 corpora had already been observed, as
a read-only rabbit-isolation comparison.

No I1/T1/O1 result or reader is mixed into P1.

## Scientific decision

G3-P1 succeeds as an attribution control.

The results separate three effects that were conflated by the original Gate 2
minimum-probe headline:

1. the specific perfect D1 separation of #23/#41 depends on the
   coordinate-derived asymmetric probe and disappears under intrinsic
   reflection-equivariant `local-degree`;
2. D1 coupling nevertheless produces a genuine intrinsic local-degree gain on
   Phase 1, splitting 20 matched-null collision pairs with zero introduced
   pairs, although this incremental gain does not replicate held-out;
3. independently of that causal gain, the local-degree dynamic observable
   induces exactly the same discrimination partition as S1 for B0 and D1 on
   Phase 1 and held-out, and therefore on their 137-form union.

The third result is the strongest P1 finding.

Its held-out replication and explicit synthetic falsification support treating
it as a nontrivial bounded property of the frozen PETRA family rather than a
generic Laplacian identity.

## Non-claims

G3-P1 does not establish:

- universal probe independence;
- universal P1-local-degree / spectrum equivalence;
- numerical reconstruction of eigenvalues or characteristic polynomials from
  the dynamic trajectory;
- universal spectral uniqueness;
- universal injectivity;
- intrinsic orientation recovery;
- a held-out-replicated D1 null-to-coupled gain under local-degree;
- mass-matched impulse-location attribution;
- impulse-response attribution;
- temporal-order attribution;
- physical excitation or physical time;
- robustness outside the frozen PETRA domain.

In particular, the replicated P1-local-degree / S1 result is a
discrimination-partition equivalence, not a generic spectral-reconstruction
theorem.

## Gate boundary

G3-P1 is complete.

The next declared Gate 3 family is G3-I1 impulse response.

I1 must receive its own protocol freeze before any I1 corpus result is
observed.

G3-T1 and G3-O1 remain inactive.
