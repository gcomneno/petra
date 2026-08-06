# Coordinate-free collision evidence

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

Created: 2026-08-06
Protocol: `petra-vision-coordinate-free-collision-semantics-v1`

## Status and boundary

Status: **bounded reproducible computational evidence**. This record completes
the Gate 1A question for the frozen graph-Laplacian protocol only. It does not
change the Phase 1 runtime contract, the graph, propagation law, probe,
decoder status, or production modules.

The implementation is:

```text
tools/research/petra_vision_coordinate_free_collisions.py
tests/test_tools_petra_vision_coordinate_free_collisions.py
```

It loads the frozen v1 and experimental width-4 research tools through their
existing file-loader pattern; it does not copy their dynamic protocol.

## Frozen protocol and equivalence relations

The graph is occupied cells with four-neighbor orthogonal adjacency, the
Laplacian is combinatorial `L = D - A`, the probe is a unit impulse at the
lexicographically minimum vertex of every disconnected component, propagation
is exact-numerator explicit Euler, `EULER_DENOMINATOR = 8`, and samples are at
`(1, 2, 4, 8, 16, 32)`. These values are imported from
`petra-vision-graph-laplacian-v1` and are not tuned here.

For a geometry `C`, let `S_global(C)` be the frozen global multiset signature
and `S_component(C)` the frozen component-separated multiset signature. The
tested relations are explicitly:

```text
C ~global D       exactly when S_global(C) = S_global(D)
C ~component D    exactly when S_component(C) = S_component(D)
```

They are reader-defined equality relations, not a claim that the geometries
are structurally identical or physically equivalent. The oriented and
`null_oriented` observations are retained only as controls: their `110/110`
values are not coordinate-free success evidence.

## Bounded corpora and observed results

The canonical Phase 1 corpus has 110 forms. The experimental extension has
137 forms; its 27-form held-out partition is the extension minus Phase 1 and
is reported separately.

| Corpus | global multiset | component multiset | additional collisions |
| --- | ---: | ---: | --- |
| Phase 1 (110) | `109/110` | `109/110` | none |
| Held-out width 4 (27) | `27/27` | `27/27` | none |
| Extended (137) | `136/137` | `136/137` | none |

For both coordinate-free readers, the only collision in Phase 1 and the
extended corpus is Phase 1 indices `#23/#41`:

```text
G(G(G(T)),G(T,T))
G(G(T,T),G(G(T)))
```

The analyzer retains every computed equivalence class and collision in its
sorted JSON report; it does not hard-code this pair as the sole output. The
observed signature replay digests are:

| Corpus | SHA-256 replay digest |
| --- | --- |
| Phase 1 | `17dbf305dcf6611f39a98109813f01afba320957481ff41d315dae3d88ccbfb8` |
| Held-out | `fcd30fa4c2afb53761f92be32032479b772f0eadb5368a1446f5fa9da9fb2c5e` |
| Extended | `91bfafecad7f6444d39ba7ca18ded78f0817c69c4479803701f4f9d1b5d4a792` |

## Derived transformation protocol

Derived geometries are never corpus members. They are constructed from
`OrthogonalGeometry` alone, with no `VisionShape`, code, index, PETRA
serialization, address, source-cell order, filename, metadata, or adapter
state supplied to graph construction, probing, propagation, signature
derivation, or equality grouping.

The declared bounded transformations are:

- fixed translations by `(17, 23)` and `(-11, 7)`;
- horizontal reflection in the geometry bounding box;
- every distinct permutation of normalized disconnected component shapes;
- a deterministic spatial reordering for each such permutation: pack the
  components left-to-right with two empty columns between component bounding
  boxes.

The packed placement is deliberately a bounded construction, not an assertion
that arbitrary component placement is valid. Reconstructing a transformation
rejects malformed component shapes, a non-bijective permutation, malformed
displacements, overlap, components that touch and merge, or a result whose
normalized component-shape multiset changed. Thus it never silently repairs a
bad input.

The replay enumerates a raw labelled-permutation space of `329,175`
specifications. `306,258` specifications merely exchange equal normalized
component shapes, so they are reported as redundant specifications before
geometry generation rather than falsely presented as distinct cases. The
actual declared bounded family is therefore `22,917` distinct candidate
component-ordering/spatial-reordering cases. Every candidate was reconstructed
and validated: `22,917` valid reconstructed geometries, `0` invalid/rejected
cases (and hence no rejection reason), `0` duplicate generated geometries,
`22,917` unique valid generated geometries, and `22,917` dynamically evaluated
cases. An order-sensitive SHA-256 replay digest covers each generated geometry
and both coordinate-free signatures:
`a517071f00caf9945f9952572d948c6145803a1b087e6186de88abe6ff121154`.

Every coordinate-free reader matches its source for all `22,917/22,917`
evaluated cases. This is an exhaustive dynamic replay, not a combinatorial
count. The `#23` source happens to contribute `840` of those cases; it is
reported only after the general enumeration, not used to choose the family.
Every reader matches its source for all `220` fixed translations. Horizontal
reflection matches `26/110` cases for each coordinate-free reader (and
`24/110` for each oriented control); reflection is therefore not asserted as a
general invariance.

## Collision classification

The classification policy is conservative:

- **structural** means equality is explained by information intentionally
  discarded by the declared reader and is reproduced by the declared
  transformation family;
- **accidental** requires a counter-control or another frozen-protocol choice
  that shows the equality depends on that choice;
- **unclassified** is used when neither finding is supported.

The analyzer first enumerates every non-singleton class separately for each
coordinate-free reader and corpus. It then identifies the expected `#23/#41`
class from its Phase 1 reporting annotations and subtracts only that computed
class. The derived additional-collision results are empty for Phase 1,
held-out width 4, and the extended corpus; no emptiness is encoded before
enumeration. The extended class retains its extended positions and its Phase 1
annotations, so corpus separation is preserved. Evidence from the Phase 1
transformation replay is joined through the explicit Phase 1 indices `#23/#41`,
not through the extended-corpus positions `#25/#45`; the JSON classification
records this provenance as `transformation_source_phase_1_indices`.

`#23/#41` is **structural** for both `global_multiset` and
`component_multiset`, in both Phase 1 and the extended corpus. The two
geometries are horizontal reflections, have the same multiset of normalized
disconnected component shapes, and every valid declared reordering for both
Phase 1 sources matches the corresponding reader. Its explicit invariants are equal frozen reader signatures, the same
multiset of normalized disconnected component shapes, and translation-invariant
geometry-only construction. No accidental classification is manufactured: a
collision without this evidence remains unclassified.

## Identity-channel and replay audit

The AST audit uses a small explicit parameter allow-list for the new dynamic
boundary, generated-case entry point, frozen v1 graph construction, probe
selection, Euler propagation, signature derivation, geometry signature entry
point, dynamic-record assembly, and equivalence grouping. It additionally
inspects direct calls into those functions for forbidden `VisionShape`, shape
code, corpus index, serialization, structural-address, identity, filename,
reporting-annotation, metadata, and adapter tokens. It verifies that the
reporting assembler calls equivalence grouping before reading annotations and
does not call dynamic functions; coordinate-free claims iterate only the two
multiset readers, while oriented and null-oriented results are labelled
controls.

This is a meaningful source-boundary audit, not a formal information-flow
proof. It cannot prove runtime behavior inside dependencies, reflective code,
monkeypatching, or every transitive flow. The reporting-label negative control
runs two independent complete Phase 1 computations: a baseline geometry-only
signature/grouping computation and a second computation after corpus indices,
shape codes, and optional Phase 1 metadata have all been replaced. The changed
annotations flow through reporting output, while independently recomputed
signature digests and equivalence memberships remain equal. Repeated analysis
is deterministic, and `--json` serializes with sorted keys; `--write-json`
writes the same newline-terminated payload.

## Interpretation, limitations, and non-claims

The global reader preserves the sampled value multiset across all components;
the component reader additionally preserves the multiset of per-component
sample multisets. Both quotient away component position and component order.
They also retain effects of the asymmetric minimum-vertex probe, so this is a
protocol characterization rather than a universal graph-isomorphism result.

This evidence makes no theorem over unbounded shapes, arbitrary placements,
other probes, sample schedules, denominators, graph constructions, boundary
conditions, or physical media. It does not claim injectivity, a decoder, FGS,
factor graphs, robustness, security, external validation, or production
readiness. It deliberately preserves the known `109/110` result and contains
no requirement or attempt to manufacture coordinate-free `110/110`.

## Reproduction

```bash
python3 tools/research/petra_vision_coordinate_free_collisions.py
python3 tools/research/petra_vision_coordinate_free_collisions.py --json
python3 tools/research/petra_vision_coordinate_free_collisions.py --write-json /tmp/petra-coordinate-free.json
```
