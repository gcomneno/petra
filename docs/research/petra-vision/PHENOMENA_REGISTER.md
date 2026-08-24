# PETRA VISION — Phenomena Register

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Initial versioned registry for the cross-gate `PHENOMENON_RECOGNITION_PROTOCOL.md`.

Issue: #201.

This registry does not change any historical Gate 3 classification. It indexes already recorded evidence so later experiments can rediscover and relate phenomena without rewriting their originating protocols.

## Registry rules

- Stable IDs use `PETRA-PHEN-####`.
- Attention level and epistemic status are separate fields.
- Historical expectations are never rewritten after explanation.
- `UNRESOLVED` is durable and is not treated as failure.
- Composition/stability evidence is not labelled independent replication.
- Gate boundaries remain authoritative.

## Evidence Ledger

| Evidence family | Artifact | Role |
| --- | --- | --- |
| Gate 3 S0/S1 | `EXPLICIT_SPECTRAL_CONTROLS_S0_S1_EVIDENCE.md` | static/full-spectrum attribution |
| Gate 3 S2 | `EXPLICIT_SPECTRAL_CONTROLS_S2_EVIDENCE.md` | local component/factor spectra |
| Gate 3 H1 | `EXPLICIT_SPECTRAL_CONTROLS_H1_EVIDENCE.md` | spectral compression |
| Gate 3 P1 | `EXPLICIT_SPECTRAL_CONTROLS_P1_EVIDENCE.md` | probe ablation |
| Gate 3 I1 | `EXPLICIT_SPECTRAL_CONTROLS_I1_EVIDENCE.md` | impulse-response attribution |
| Gate 3 T1 | `EXPLICIT_SPECTRAL_CONTROLS_T1_EVIDENCE.md` | temporal observation |
| Gate 3 O1 | `EXPLICIT_SPECTRAL_CONTROLS_O1_EVIDENCE.md` | orientation leakage control |
| Gate 3 decision | `EXPLICIT_SPECTRAL_CONTROLS_DECISION.md` | combined bounded interpretation |

The evidence artifacts remain the authority for exact counts, collision sets, protocol IDs, replay digests, and non-claims.

## Rabbit Register

### PETRA-PHEN-0001 — Common S1/P1/I1 B0/D1 discrimination quotient

- `epistemic_status`: `REPLICATED_PHENOMENON`
- `attention_level`: `4`
- `disposition`: `RETAINED`
- `origin`: Gate 3 P1/I1 attribution
- `observation`: full exact operator spectrum S1, intrinsic local-degree trajectory P1, and intrinsic all-vertices mass-one impulse-response family I1 induce the same B0/D1 discrimination partitions on the frozen Phase 1 family.
- `independent_replication`: exact partition coincidence reproduced on the independent held-out width-4 family.
- `synthetic_falsification`: Laplacian-cospectral synthetic pairs show that the coincidence is not generically forced by Laplacian dynamics.
- `fingerprint`: `partition-coincidence / materially-different-readers / B0-D1 / S1=P1=I1 / non-generic`
- `supported_claim`: replicated bounded common discrimination quotient of the frozen PETRA family.
- `non_claims`: no operator reconstruction, graph reconstruction, syntax reconstruction, or universal theorem.
- `related_evidence`: `EXPLICIT_SPECTRAL_CONTROLS_P1_EVIDENCE.md`, `EXPLICIT_SPECTRAL_CONTROLS_I1_EVIDENCE.md`, `EXPLICIT_SPECTRAL_CONTROLS_DECISION.md`.

### PETRA-PHEN-0002 — Terminal sufficiency / no sampled recollision

- `epistemic_status`: `REPLICATED_PHENOMENON`
- `attention_level`: `4`
- `disposition`: `RETAINED`
- `origin`: Gate 3 T1 temporal observation
- `observation`: ordered, order-discarding, endpoint, and terminal observations induce the same bounded discrimination partitions across the frozen B0/D1/F1/L1 channels; no sampled distinction recollides after appearing.
- `independent_replication`: held-out width-4 family reproduces the bounded partition equivalence.
- `synthetic_falsification`: synthetic trajectories show terminal sufficiency and no-recollision are not generic properties of arbitrary trajectories.
- `fingerprint`: `temporal-reduction-equivalence / terminal-sufficiency / no-sampled-recollision / non-generic`
- `supported_claim`: replicated bounded terminal-sufficiency/no-recollision phenomenon under the frozen PETRA sample schedule.
- `non_claims`: no physical time, spacetime, monotonicity theorem, or general dynamical-system claim.
- `related_evidence`: `EXPLICIT_SPECTRAL_CONTROLS_T1_EVIDENCE.md`, `EXPLICIT_SPECTRAL_CONTROLS_DECISION.md`.

### PETRA-PHEN-0003 — F1 native-order partition stasis

- `epistemic_status`: `REPLICATED_PHENOMENON`
- `attention_level`: `4`
- `disposition`: `RETAINED`
- `origin`: Gate 3 O1 orientation control
- `observation`: the non-injective F1 native-order collision partition is unchanged from oriented step zero through frozen null and coupled F1 dynamics.
- `independent_replication`: the held-out family contains a nontrivial four-form collision group and reproduces the same exact step0/null/coupled partition stasis.
- `synthetic_falsification`: exact synthetic F1 proximity operators with the same ordered initial state can diverge under coupled evolution, disproving generic necessity.
- `fingerprint`: `partition-stasis / F1-native-order / step0=null=coupled / non-injective / non-generic`
- `supported_claim`: replicated bounded F1 native-order partition stasis.
- `non_claims`: no coordinate-free orientation recovery, syntax reconstruction, or generic factor-proximity theorem.
- `related_evidence`: `EXPLICIT_SPECTRAL_CONTROLS_O1_EVIDENCE.md`, `EXPLICIT_SPECTRAL_CONTROLS_DECISION.md`.

### PETRA-PHEN-0004 — Bounded F1 lossless spectral compression

- `epistemic_status`: `CANDIDATE_PHENOMENON`
- `attention_level`: `2`
- `disposition`: `RETAINED`
- `origin`: Gate 3 H1 spectral compression
- `observation`: frozen H1-M1 `(operator order, trace)` reproduces the full F1 S1 discrimination partition over the declared bounded domain.
- `synthetic_falsification`: an inverse-distance synthetic counterexample shows that this compression is not generically lossless.
- `fingerprint`: `spectral-compression / F1 / order+trace / partition-equivalence / non-generic`
- `supported_claim`: bounded lossless discrimination compression under the frozen PETRA family.
- `non_claims`: no generic spectral identity or theorem-level sufficiency.
- `related_evidence`: `EXPLICIT_SPECTRAL_CONTROLS_H1_EVIDENCE.md`, `EXPLICIT_SPECTRAL_CONTROLS_DECISION.md`.

## Unresolved Phenomena Register

No Gate 3 result is newly reclassified here as unresolved.

Future unresolved entries must remain present until they receive a durable disposition such as `RETAINED`, `FALSIFIED`, `EXPLAINED_AS_ARTIFACT`, `EXPLAINED_AS_LEAKAGE`, `EXPLAINED_AS_TRIVIAL_CONTROL_EFFECT`, or `SUPERSEDED`.

An unresolved record may be valuable even when it does not improve discrimination and even when no application domain is known.

## Falsified Expectations Register

### FE-0001 — Temporal ordering might provide additional discrimination

- `origin`: pre-Gate-3 temporal hypothesis and T1 protocol motivation.
- `expectation_type`: hypothesis, not fact.
- `expectation`: retaining ordered sampled trajectories could reveal distinctions lost by endpoint or order-discarding reductions.
- `contradicting_evidence`: under the frozen T1 channels/corpora, ordered and reduced observations induce the same bounded discrimination partitions.
- `result`: expectation not supported for the frozen bounded experiment.
- `replacement`: terminal-sufficiency/no-recollision retained as a bounded replicated phenomenon, not a universal law.

### FE-0002 — A strong orientation reader might indicate intrinsic orientation information

- `origin`: orientation attribution risk addressed by O1.
- `expectation_type`: confounding risk / possible interpretation.
- `expectation`: high oriented discrimination could be read as evidence of intrinsic directional information.
- `contradicting_evidence`: B0/D1/L1 are already injective through native order at step zero, and oriented dynamics adds no further discrimination; F1 likewise shows static native-order dominance while remaining non-injective.
- `result`: strong oriented scores are explained as orientation/identity leakage controls, not coordinate-free recovery.
- `replacement`: orientation leakage must remain separated from coordinate-free spectral/dynamic evidence.

### FE-0003 — Exact F1 oriented partition stasis could be forced by the operator construction

- `origin`: O1 rabbit-isolation working interpretation.
- `expectation_type`: post-observation necessity hypothesis.
- `expectation`: identical ordered F1 initial states might force identical coupled evolution under the relevant construction.
- `contradicting_evidence`: synthetic exact proximity operators preserve the same ordered initial state but diverge under coupled evolution.
- `result`: generic necessity falsified.
- `replacement`: retain only the replicated bounded PETRA-family stasis claim.

## Re-discovery rule

Before assigning a new PETRA-PHEN identifier, compare the new observation with the existing `fingerprint` fields.

A fingerprint match does not prove common cause. It requires the older record to be surfaced and compared before a new interpretation is accepted.

## Next insertion

The next phenomenon discovered after this registry freeze receives `PETRA-PHEN-0005` unless it is demonstrably another observation of an existing record.
