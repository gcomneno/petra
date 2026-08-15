# PETRA VISION Gate 3 G3-O1 — Orientation Control Evidence

## Status

- Protocol: `petra-vision-explicit-spectral-controls-o1-v0`.
- Evidence runner: `petra-vision-explicit-spectral-controls-o1-evidence-v0`.
- Corpus order: Phase 1 -> independent held-out width-4 -> extended composition.
- Oriented observations are explicitly labelled diagnostics only; they are never evidence for coordinate-free recovery.
- Gate 4 adversarial mutation work is outside this evidence set.

## Frozen provenance

- O1 protocol SHA256: `80984e11e2764a435df0bf0857ff9a18c5528393d8c1033677ebc5b396ae2e91`.
- O1 implementation SHA256: `4dbb3b27de69e04287427b477e54ea2046476a49919151263c53c3ea67fd0bf1`.
- O1 core-test SHA256: `2abb807793d96ffc9ce35172622d5c291cdcc700639c8c4f6e0652c8ef766639`.
- O1 evidence-runner SHA256: `1e523d7da953ddf952b25caa666184e61997aeb43440e74405636515490b2c50`.
- O1 runner-test SHA256: `3b004615eb8781de6e5e7ceb5507f6e75febea9982862b091189bed03b2edd0d`.
- Frozen width-4 source SHA256: `348d2dfaf6c26f71cd20af75ad7e298b58d26d0e2eab94279bd860492aa35707`.

Frozen sample schedule: `1, 2, 4, 8, 16, 32`.
Frozen translation control: `(17, 11)`.

## Deterministic artifacts

- Phase 1, 110 forms: `3145b38e774d6aede2acf5a3442e7761ac18d5435c7ececd9bec0819bc7ee8db`.
- Held-out width-4, 27 forms: `5cb90a1ace14e21d1553407ac8d7020fe9083e82298f7646af7077f2833af41c`.
- Extended, 137 forms: `d047a33160d83d732547a2c10f740d7f248778bb03cc32ab0f2aa05d3d9c6f98`.

Every artifact reproduced byte-identically.
The extended corpus is the exact set union of Phase 1 and held-out. Its enumeration order is not required to be their positional concatenation.
Per-shape signature digests are identical between each original corpus and extended for all seven channels and all four observations.
The extended collision partitions also restrict exactly to the original Phase 1 and held-out partitions.

Extended is therefore a composition/stability check, not a third independent replication.

## Frozen observations

1. `coordinate-free-step0`
2. `oriented-step0`
3. `coordinate-free-dynamic`
4. `oriented-dynamic`

The oriented reader retains only native deterministic state/factor order already present inside each frozen substrate.
No new directional statistic, signed coordinate moment, chosen axis, coordinate value, AST identity, or shape serialization is added.

## Signature counts

Each cell is `distinct signatures / collision pairs`.

### Phase 1

| Channel | CF step0 | Oriented step0 | CF dynamic | Oriented dynamic |
|---|---:|---:|---:|---:|
| B0 | 31/294 | 110/0 | 109/1 | 110/0 |
| D1-null | 31/294 | 110/0 | 109/1 | 110/0 |
| D1-coupled | 31/294 | 110/0 | 110/0 | 110/0 |
| F1-null | 47/121 | 87/28 | 47/121 | 87/28 |
| F1-coupled | 47/121 | 87/28 | 58/77 | 87/28 |
| L1-null | 31/294 | 110/0 | 31/294 | 110/0 |
| L1-coupled | 31/294 | 110/0 | 67/43 | 110/0 |

### held-out

| Channel | CF step0 | Oriented step0 | CF dynamic | Oriented dynamic |
|---|---:|---:|---:|---:|
| B0 | 9/40 | 27/0 | 27/0 | 27/0 |
| D1-null | 9/40 | 27/0 | 27/0 | 27/0 |
| D1-coupled | 9/40 | 27/0 | 27/0 | 27/0 |
| F1-null | 9/40 | 24/6 | 9/40 | 24/6 |
| F1-coupled | 9/40 | 24/6 | 15/15 | 24/6 |
| L1-null | 9/40 | 27/0 | 9/40 | 27/0 |
| L1-coupled | 9/40 | 27/0 | 16/11 | 27/0 |

### extended

| Channel | CF step0 | Oriented step0 | CF dynamic | Oriented dynamic |
|---|---:|---:|---:|---:|
| B0 | 35/393 | 137/0 | 136/1 | 137/0 |
| D1-null | 35/393 | 137/0 | 136/1 | 137/0 |
| D1-coupled | 35/393 | 137/0 | 137/0 | 137/0 |
| F1-null | 56/161 | 111/34 | 56/161 | 111/34 |
| F1-coupled | 56/161 | 111/34 | 73/92 | 111/34 |
| L1-null | 35/393 | 137/0 | 35/393 | 137/0 |
| L1-coupled | 35/393 | 137/0 | 83/54 | 137/0 |

## Primary O1 result

For every channel on Phase 1, held-out, and extended, `oriented-step0 -> oriented-dynamic` has signature delta `0`, split count `0`, and introduced-collision count `0`.

**The frozen dynamics adds no discrimination beyond the native ordered step-zero representation.**

For B0, D1-null, D1-coupled, L1-null, and L1-coupled the oriented reader is already injective at step zero:

- `110/110` on Phase 1;
- `27/27` on held-out;
- `137/137` on extended.

Those perfect scores are static positional/native-order leakage. They are not intrinsic orientation recovery.

## F1 replicated bounded rabbit

F1 is the nontrivial control because its oriented step-zero representation remains non-injective.

| Corpus | Distinct | Collision groups | Collision pairs |
|---|---:|---:|---:|
| Phase 1 | 87 | 18 | 28 |
| held-out | 24 | 1 | 6 |
| extended | 111 | 19 | 34 |

For every corpus view, the exact collision partition is identical across:

- F1 oriented step zero;
- F1-null oriented dynamics;
- F1-coupled oriented dynamics.

The held-out result is nontrivial: one four-form collision group, hence six collision pairs, independently reproduces the partition stasis.

A synthetic operator-level falsification established that identical ordered F1 initial states do not generically force identical coupled evolution: changing the exact proximity weights preserved null evolution but changed coupled evolution.

**Classification: Level 4 replicated bounded rabbit.**

Safe claim: across the frozen Phase 1 and independent held-out PETRA families, F1 native-order discrimination is fully determined at step zero; neither frozen null nor coupled F1 dynamics refines that non-injective ordered partition.

The synthetic counterexample shows that this stasis is not generically forced by the F1 operator.

This is not graph reconstruction, syntax recovery, universal injectivity, or a generic theorem.

## F1 orientation leakage versus coordinate-free coupling

| Corpus | Static orientation splits | Coordinate-free coupling splits | Coupling subset of static orientation splits |
|---|---:|---:|---|
| Phase 1 | 93 | 44 | yes |
| held-out | 34 | 25 | yes |
| extended | 127 | 69 | yes |

Every pair split by F1 coordinate-free coupled dynamics is already distinguishable through native order at step zero.

This does not convert native order into intrinsic information; it only attributes where the available distinctions already reside.

## Null-to-coupled coordinate-free dynamics

### Phase 1

| Family | Signature delta | Split pairs | Introduced pairs |
|---|---:|---:|---:|
| D1 | 1 | 1 | 0 |
| F1 | 11 | 44 | 0 |
| L1 | 36 | 251 | 0 |

### held-out

| Family | Signature delta | Split pairs | Introduced pairs |
|---|---:|---:|---:|
| D1 | 0 | 0 | 0 |
| F1 | 6 | 25 | 0 |
| L1 | 7 | 29 | 0 |

### extended

| Family | Signature delta | Split pairs | Introduced pairs |
|---|---:|---:|---:|
| D1 | 1 | 1 | 0 |
| F1 | 17 | 69 | 0 |
| L1 | 48 | 339 | 0 |

These are coordinate-free substrate results and are not reclassified as O1 orientation evidence.

## Reflection controls

Translation and transported-reflection equivariance pass for every channel on every corpus.

The tables below report changed-form counts after independent canonical horizontal reflection.

### Phase 1

| Channel | CF step0 | Oriented step0 | CF dynamic | Oriented dynamic |
|---|---:|---:|---:|---:|
| B0 | 0 | 86 | 84 | 86 |
| D1-null | 0 | 86 | 84 | 86 |
| D1-coupled | 0 | 86 | 86 | 86 |
| F1-null | 0 | 70 | 0 | 70 |
| F1-coupled | 0 | 70 | 0 | 70 |
| L1-null | 0 | 86 | 0 | 86 |
| L1-coupled | 0 | 86 | 0 | 86 |

### held-out

| Channel | CF step0 | Oriented step0 | CF dynamic | Oriented dynamic |
|---|---:|---:|---:|---:|
| B0 | 0 | 22 | 22 | 22 |
| D1-null | 0 | 22 | 22 | 22 |
| D1-coupled | 0 | 22 | 22 | 22 |
| F1-null | 0 | 18 | 0 | 18 |
| F1-coupled | 0 | 18 | 0 | 18 |
| L1-null | 0 | 22 | 0 | 22 |
| L1-coupled | 0 | 22 | 0 | 22 |

### extended

| Channel | CF step0 | Oriented step0 | CF dynamic | Oriented dynamic |
|---|---:|---:|---:|---:|
| B0 | 0 | 108 | 106 | 108 |
| D1-null | 0 | 108 | 106 | 108 |
| D1-coupled | 0 | 108 | 108 | 108 |
| F1-null | 0 | 88 | 0 | 88 |
| F1-coupled | 0 | 88 | 0 | 88 |
| L1-null | 0 | 108 | 0 | 108 |
| L1-coupled | 0 | 108 | 0 | 108 |

### Reflection interpretation

- F1 and L1 coordinate-free readers remain canonically reflection-invariant at step zero and dynamically.
- Their oriented reflection differences are native-order leakage diagnostics.
- B0 and D1 require qualification because the frozen canonical component probe is lexicographic and therefore coordinate-derived/asymmetric when independently reselected after reflection.
- B0/D1 differences in independently canonicalized `coordinate-free-dynamic` observations are therefore probe-qualified and are not intrinsic orientation evidence.
- The transported-reflection audit passes, establishing equivariance when the original source state/probe is transported.

## Historical reflected/reordered pair #23/#41

On Phase 1:

- B0 and D1-null coordinate-free dynamics retain the pair collision.
- D1-coupled coordinate-free dynamics splits it, reproducing the previously established D1 coupling result.
- F1 and L1 coordinate-free dynamics retain it.
- Every oriented reader splits it via native order.

The oriented split is therefore a control for orientation leakage and cannot be counted as coordinate-free recovery.

## Exact arithmetic

For B0, D1-null, D1-coupled, L1-null, and L1-coupled, raw Euler-numerator and normalized exact-rational dynamic partitions match for both coordinate-free and oriented readers on every corpus view.

F1 uses its frozen exact rational propagation directly; no artificial Euler normalization is applied.

## Extended composition audit

Extended contains exactly the Phase 1 and held-out shape-code sets and no others.

Its enumeration order differs from simple positional concatenation, but this is immaterial: per-shape digest maps coincide exactly for all 28 channel/observation combinations.

Extended partitions restricted to Phase 1 and held-out also reproduce the corresponding original partitions exactly.

Extended therefore contributes composition/stability evidence only.

## Source boundary

O1 evidence consumes the frozen O1 implementation and the frozen width-4 geometry/corpus source only; shape codes are reporting metadata.

S1, S2, H1, P1, I1, and T1 signatures are not O1 inputs. No Gate 4 mutation or adversarial-generation result is consumed.

Prior results enter only as post-result interpretation, including the known B0/D1 probe qualification and historical #23/#41 control.

## Conclusion

G3-O1 succeeds as an orientation-control experiment.

Native deterministic order leaks substantial positional/orientation identity and is usually already injective before dynamics begins. The frozen dynamics adds no further discrimination to that oriented channel.

F1 supplies the nontrivial replicated case: its native ordered step-zero representation remains non-injective, yet exactly the same collision partition survives both null and coupled dynamics on Phase 1 and on the independent held-out family.

**Native-order orientation leakage is separable from coordinate-free spectral/dynamic discrimination, and G3-O1 establishes no new coordinate-free orientation recovery.**

The F1 partition-stasis result is retained as a Level 4 replicated bounded rabbit about discrimination within the frozen PETRA family.

## Claim boundary

G3-O1 does not establish:

- intrinsic left/right recovery;
- coordinate-free orientation reconstruction;
- intrinsic reflection breaking;
- AST or syntax recovery;
- graph reconstruction;
- universal injectivity;
- generic F1 partition stasis;
- physical spacetime or cosmological interpretation.

Gate 4 remains separate and inactive in this evidence document.
