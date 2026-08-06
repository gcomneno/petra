# PETRA VISION operational research pipeline

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Purpose and terminology

This document is the single operational roadmap for confidential PETRA VISION research. It sequences future work without changing the bounded static Phase 1 contract, production implementation, recorded evidence, or the historical architectural Phase plan in `EXPERIMENT_PLAN.md`.

A **Phase** is an architectural maturity milestone inherited from the original PETRA VISION roadmap. Phase 1 is formally complete only for its bounded static contract. Phases 2–7 remain architectural horizons; they are not the active task list.

A **Research Gate** is the only numbered operational unit for future research. Every gate defines a research question, scope, protocol, corpus, controls, success and failure criteria, evidence artifacts, dependencies, status, and a final decision. A **Research Track** is a non-numbered thematic label only; it may aid indexing but must never become a second roadmap.

## Immutable baseline

The operational baseline is the validated and published baseline commit `1f0404016520ee5a9550ecfad7ab9bc55cd64e9a`. It comprises the bounded static Phase 1 domain of 110 forms, exact canonical geometry roundtrip, the graph-Laplacian v1 evidence, the known coordinate-free reflected collision, and the experimental width=`4` extension. The width=`4` record covers 27 held-out forms and the full 137-form experimental domain; it does not expand the Phase 1 runtime contract. Existing evidence remains evidence of its stated protocol only.

## Status vocabulary

Only these statuses are used: `complete`, `next`, `planned`, `deferred`, `blocked`, `failed`, `inconclusive`, and `superseded`.

## Compact gate register

| Gate | Operational subject | Status |
| --- | --- | --- |
| 0 | Consolidated baseline | complete |
| 1 | Structural units and coordinate-free semantics | next |
| 2 | Global geometric coupling | planned |
| 3 | Explicit spectral controls | planned |
| 4 | Adversarial collision generation | planned |
| 5 | Orthogonal structural scaling | planned |
| 6 | Independent reproduction | planned |
| 7 | Structural locality and sensitivity | planned |
| 8 | Dynamic decoding | deferred |
| 9 | Perturbed observation | deferred |
| 10 | Multiscale semantics | deferred |
| 11 | Authenticated completion | deferred |

## Gate 0 — Consolidated baseline

**Status:** `complete`

**Research question:** What bounded evidence is fixed before further work?

**Scope, protocol, and corpus:** Preserve the 110-form bounded static Phase 1 corpus, exact canonical roundtrip evidence, graph-Laplacian v1 protocol and its coordinate-free reflected collision, plus the separate width=`4` extension (27 held-out forms; 137 forms total). **Controls:** retain the recorded geometry-only identity-channel audits and declared observation controls. **Success/failure criteria:** the gate is complete as a frozen baseline; it fails as a baseline if a later claim silently changes any recorded contract, corpus, result, or limitation. **Evidence artifacts:** the Phase 1, graph-Laplacian, and width=`4` evidence documents, with the baseline commit above. **Dependencies:** none. **Final decision:** retain as the immutable comparison point; it establishes neither universal decoding nor robustness, security, physical mechanism, or external generalization.

## Gate 1 — Structural units and coordinate-free semantics

**Status:** `next`

**Research question:** Which structural units can be defined from canonical geometry without importing identity metadata, and what coordinate-free equivalence is actually observed?

**Scope:** Gate 1 consists of ordered subgates 1A and 1B. **Protocol and corpus:** use the Gate 0 corpus first, with explicit controls and frozen replay artifacts. **Success/failure criteria:** each subgate has its own decision; Gate 1 does not convert a feasibility result into a decoding claim. **Evidence artifacts:** protocol, corpus manifest and digests, implementation provenance, per-form results, counterexamples, and a decision record. **Dependencies:** Gate 1A may proceed independently from the basic FGS contract. Gate 1B levels 1 and 2 may proceed immediately. Gate 1B level 3 must define its native geometric boundary before Gate 2 uses factors as dynamic units. **Final decision:** pending the subgate decisions.

### Gate 1A — Coordinate-free collision semantics

**Status:** `complete`

**Research question:** What equivalence relation is actually represented by the coordinate-free graph-Laplacian reader?

**Scope:** Analyze disconnected-component permutations, reflected or spatially reordered components, and the distinction between inevitable and accidental collisions. Formally state the resulting quotient or equivalence-class interpretation. **Protocol:** adversarially enumerate the available component permutations, replay the declared reader deterministically, and classify each collision against that interpretation. Do not try to force a perfect score by silently preserving orientation. **Corpus:** the 110 Phase 1 forms initially, with targeted derived permutations and the recorded collision; later replays may use the 27 held-out and 137-form domains. **Controls:** oriented and coordinate-free readers remain separately labelled; audit that no orientation or coordinate identity enters the coordinate-free reader.

**Success criteria:** a precise, reproducible equivalence relation explains the observed collisions and distinguishes inevitable from accidental ones. **Failure criteria:** unexplained collisions, non-deterministic classes, or a reader whose result depends on an undeclared identity channel. **Evidence artifacts:** enumeration manifest, signatures, equivalence definition, collision classification, identity audit, and replay digests. **Dependencies:** Gate 0. **Final decision:** complete for the frozen v1 readers and declared bounded corpora. Both coordinate-free readers yield `109/110` on Phase 1, `27/27` on held-out width 4, and `136/137` on the 137-form extension; the only collision is `#23/#41`, classified structural because the readers discard disconnected-component spatial ordering. The declared distinct reordering family was fully reconstructed, validated, signed, and dynamically replayed (`22,917/22,917` matches for each coordinate-free reader); raw repeated-component permutation specifications are separately reported. Collision classes are enumerated before the known class is annotated and subtracted, and the reporting-metadata control uses independent replays. See `COORDINATE_FREE_COLLISION_EVIDENCE.md`. This is a quotient characterization, not complete structural discrimination or a theorem beyond the declared bounds.

### Gate 1B — Structural Geometric Factorization (FGS)

**Status:** `next`

**Research question:** Can a valid canonical PETRA VISION geometry be decomposed directly into ordered canonical geometric factors corresponding exactly to the immediate branches of its structural root, and then recomposed without loss?

FGS (Italian: *Fattorizzazione Geometrica Strutturale*; identifier: `FGS`) is conservatively defined as recursive, ordered, non-commutative, multiplicity-preserving, geometry-derived, exactly recomposable, and free from hidden identity or serialization channels.

There are three distinct levels:

1. **Structural factorization:** `VisionShape` to its immediate ordered children. This is straightforward.
2. **Decoder-based geometric factorization:** canonical geometry to `VisionShape` to ordered child factors. This is highly feasible using the existing bounded decoder.
3. **Native structural geometric factorization:** canonical geometry directly to ordered branch regions without first invoking the complete structural decoder. This is the actual new research claim.

No analogy to unique prime factorization is established. `Terminal` is only an irreducible element relative to the current grammar, and composition is ordered and n-ary, not arithmetic multiplication.

**Scope and protocol:** first specify a native geometric boundary and ownership rule, then extract immediate factors and recursively replay on them. Compare decoder-based and native factorization using the same inputs and an independent structural oracle derived from abstract grammar children. The factorizer must not use shape codes, PETRA addresses, serialization, node IDs, original child lists, encoder metadata, or annotated coordinates. Require exact child order, exact multiplicity, deterministic replay, cell ownership without loss or duplication, canonical normalization of extracted factors, recursive applicability, exact recomposition, and malformed-geometry rejection.

**Corpus:** begin exhaustively with all 110 Phase 1 forms. Replay later on the 27 width=`4` held-out forms and the full 137-form domain. **Controls:** independent grammar-child oracle; identity-channel audit; decoder-based baseline; deterministic duplicate runs; negative cases for incomplete frames, overlapping factor regions, children outside the parent, noncanonical spacing, isolated cells, ambiguous parent ownership, duplicate cell attribution, missing cells, and geometries that factor locally but cannot be recomposed canonically.

**Initial bounded success result:** all 110 valid Phase 1 geometries produce the exact immediate ordered factors, preserved multiplicity, deterministic output, exact recomposition, no hidden channel, and correct terminal handling. **Failure criteria:** any mismatch to the independent oracle, loss or duplication of cell ownership, noncanonical factor, nondeterminism, accepted malformed geometry, unrecomposable output, or undeclared identity dependency. **Evidence artifacts:** frozen corpus and digests; protocol; oracle output; per-form factor, ownership, normalization, and recomposition records; identity audit; negative-case results; decoder-based/native comparison; and decision record. **Dependencies:** Gate 0; level 3 additionally requires a declared native boundary. **Final decision:** pending. Only a positive level 3 decision authorizes factor-based units in Gate 2; neither levels 1–2 nor FGS alone constitute complete dynamic decoding.

## Gate 2 — Global geometric coupling

**Status:** `planned`

**Question/scope:** Compare the current local occupied-cell graph, component graph, factor graph only if Gate 1B establishes a valid factor boundary, weak distance-dependent coupling, and full-lattice or occupied/empty-field propagation. **Protocol/corpus/controls:** replay each construction on frozen Gate 0 corpora with coordinate-free readers, identity audits, null and matched coupling controls. Coordinates may determine physical or geometric construction but must not be handed directly to the final reader as identity metadata. **Success/failure:** retain only effects separable from controls; fail a construction that needs identity metadata or cannot replay. **Evidence:** specification, source provenance, signatures, controls, digests, and decision. **Dependencies:** Gate 1A; factor graph additionally requires positive Gate 1B level 3. **Final decision:** pending.

## Gate 3 — Explicit spectral controls

**Status:** `planned`

**Question/scope:** Separate contributions from static graph statistics, Laplacian spectrum, per-component spectrum, per-factor spectrum only if FGS succeeds, heat trace, probe choice, impulse response, temporal observation, and orientation. **Protocol/corpus/controls:** ablate one contribution at a time on frozen Gate 0 replay corpora using matched probes and oriented versus coordinate-free controls. **Success/failure:** attribute only reproducible incremental information; fail claims confounded by observation or probe. **Evidence:** ablation matrix, signatures, collision sets, digests, decision. **Dependencies:** Gate 2; per-factor work requires positive Gate 1B. **Final decision:** pending.

## Gate 4 — Adversarial collision generation

**Status:** `planned`

**Question/scope:** Generate reflection, component permutation, factor permutation, displacement, duplication, wrapping, unwrapping, statistic-preserving substitutions, and deliberately constructed counterexamples. **Protocol/corpus/controls:** enumerate valid and invalid mutations from frozen forms and compare declared readers to matched originals. **Success/failure:** classify each result without repairing it through hidden metadata; fail unclassified or non-replayable cases. **Evidence:** generator, manifests, counterexamples, signatures, classifications, decision. **Dependencies:** Gates 1A–3; factor permutations require positive Gate 1B. **Final decision:** pending.

## Gate 5 — Orthogonal structural scaling

**Status:** `planned`

**Question/scope:** Scale separately through 5A depth=`4`, width≤`3`, nodes≤`7`; 5B nodes=`8`, width≤`3`, depth≤`3`; 5C width=`5`, depth≤`3`, nodes≤`7`; and 5D controlled combinations. **Protocol/corpus/controls:** grammar-generate each bounded corpus independently, replay compatible protocols, and retain domains separately. **Success/failure:** report rather than extrapolate when a protocol does not remain compatible; fail any hidden contract expansion. **Evidence:** for each subgate record corpus size, geometry growth, number of components, number and depth of factors, collisions, computational cost, mutation locality, and protocol compatibility. **Dependencies:** relevant prior protocol gates. **Final decision:** pending per subgate and overall.

## Gate 6 — Independent reproduction

**Status:** `planned`

**Question/scope:** Can results be reproduced independently? **Protocol:** independent corpus generation and implementation, with no imports from the original experimental tools; freeze JSON artifacts and digests, preferably in a different language or implementation paradigm. **Corpus/controls:** use published frozen manifests and compare only declared outputs. **Success/failure:** reproduce within declared protocol or record divergence; fail independence if original tools are imported. **Evidence:** source provenance, environments, JSON, digests, comparison report, decision. **Dependencies:** stable prior gate artifacts; include FGS if Gate 1B is positive. **Final decision:** pending.

## Gate 7 — Structural locality and sensitivity

**Status:** `planned`

**Question/scope:** Study insert, delete, replace, sibling swap, wrap, unwrap, duplicate, and subtree movement. **Protocol/corpus/controls:** generate one declared mutation at a time with matched originals. Measure structural, factor-level, geometric, graph, signature, and propagation distance. **Success/failure:** report distributions and counterexamples without claiming robustness; fail undeclared mutations or irreproducible measures. **Evidence:** mutation manifest, metric definitions, per-case results, digests, decision. **Dependencies:** Gates 2–4; factor-level metric requires positive Gate 1B. **Final decision:** pending.

## Gate 8 — Dynamic decoding

**Status:** `deferred`

**Question/scope:** Progress from classification among known shapes to graph reconstruction, factor reconstruction, and `VisionShape` reconstruction. **Protocol/corpus/controls:** prevent corpus indices, shape codes, serialization, original coordinates, object identities, and structural metadata from entering the reader. **Success/failure:** establish only the declared reconstruction level with adversarial controls; fail hidden channels or overclaimed scope. **Evidence:** reader contract, audits, corpus manifests, outputs, counterexamples, decision. **Dependencies:** Gates 1–7; FGS may be an intermediate decomposition primitive, not complete dynamic decoding. **Final decision:** deferred.

## Gate 9 — Perturbed observation

**Status:** `deferred`

**Question/scope:** Progress through exact vector geometry, perfect rasterization, scaling, antialiasing, quantization, noise, missing cells, and occlusion. **Protocol/corpus/controls:** introduce one perturbation family and level at a time against exact-vector controls; measure factor-boundary stability if Gate 1B succeeds. **Success/failure:** retain only declared observations; fail unsupported recovery claims. **Evidence:** renderer and perturbation specifications, levels, outcomes, digests, decision. **Dependencies:** Gate 8 and positive Gate 1B for factor boundaries. **Final decision:** deferred.

## Gate 10 — Multiscale semantics

**Status:** `deferred`

**Question/scope:** Determine whether each scale level corresponds to a documented PETRA structural boundary. **Protocol/corpus/controls:** map each level to an independently specified boundary and test alternative mappings. Recursive FGS could provide candidate scale boundaries, but that remains a hypothesis until separately validated. **Success/failure:** accept only documented deterministic correspondences; fail arbitrary visual levels. **Evidence:** boundary definitions, mapping results, controls, digests, decision. **Dependencies:** Gates 5, 7, and any applicable positive FGS decision. **Final decision:** deferred.

## Gate 11 — Authenticated completion

**Status:** `deferred`

**Question/scope:** Assess authenticated completion only with established cryptographic primitives, a threat model, and explicit trust boundaries. **Protocol/corpus/controls:** use standard components and adversarial threat cases; state explicitly that geometric incompleteness alone is not encryption. **Success/failure:** accept only a documented, scoped security analysis; fail home-grown cryptography, omitted trust boundaries, or security implication from geometry alone. **Evidence:** primitive specifications, threat model, trust-boundary diagram, tests or analysis, decision. **Dependencies:** prior structural and observation decisions. **Final decision:** deferred.

## Dependency order and stop conditions

Current gate: **Gate 1 — Structural units and coordinate-free semantics**. Current subgates: **Gate 1A and Gate 1B feasibility/contract work may proceed in parallel, while native FGS results must precede factor-based use in Gate 2.**

Stop or defer the affected gate when inverse work requires hidden serialized data; canonical normalization creates unresolved collisions; factor ownership is ambiguous or lossy; geometry has no usable stated bound; canonicality rests on arbitrary renderer behavior; a scale lacks a PETRA boundary; or a result is only an ordinary labelled-tree representation. A stopped gate must record its negative evidence and receive one of the defined statuses; it must not be rescued by changing the reader or corpus silently.

Research Gates sequence operational evidence. They do not renumber, complete, or replace the original architectural Phases: Phase 1 remains complete only for the bounded static contract, while Phases 2–7 remain horizons recorded in `EXPERIMENT_PLAN.md`.
