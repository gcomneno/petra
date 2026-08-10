# PETRA VISION Global Geometric Coupling — Evidence

## Status

Gate 2 — Global geometric coupling: complete for the declared bounded domain.

Issue: #198.

The evidence chronology begins with:

- G2-D1 — weak distance-dependent geometric coupling.

Subsequent sections evaluate G2-F0, G2-F1, G2-L1, G2-E1, and G2-C0.
The complete matrix and final Gate 2 decision are recorded below.

Protocol:

```text
petra-vision-global-geometric-coupling-distance2-v0
```

Evidence protocol:

```text
petra-vision-global-geometric-coupling-distance2-evidence-v0
```

D1 is frozen before corpus discrimination results.

## Research question

Can a weak coupling derived only from canonical geometry add reproducible
global information beyond the frozen disconnected occupied-cell graph and a
matched no-bridge control, while keeping the final reader coordinate-free?

## Frozen D1 construction

D1 retains occupied cells as the only vertices.

Edges are:

- local axial distance 1, weight 2;
- axial distance 2 through one empty midpoint, weight 1;
- no diagonal coupling;
- no coupling beyond distance 2.

Propagation uses:

- weighted combinatorial Laplacian;
- exact integer Euler numerators;
- denominator 16;
- sample steps 1, 2, 4, 8, 16, 32.

The primary probe remains matched to graph-Laplacian v1:

- one unit impulse at the lexicographically minimum vertex of every original
  four-neighbor occupied component.

The primary reader is:

- global multiset of state values at every declared sample step.

No coordinate, vertex ordering, factor ordering, structural address, AST node,
shape code, corpus index, serialization, or object identity reaches that
reader.

## Frozen G2-B0 replay

The evidence runner imports and replays the existing graph-Laplacian evidence
rather than copying or changing its dynamic core.

Observed replay:

| Corpus | Frozen B0 |
| --- | ---: |
| Phase 1 | 109/110 |
| Held-out width 4 | 27/27 |
| Extended | 136/137 |

The sole bounded B0 collision remains:

```text
G(G(G(T)),G(T,T))
G(G(T,T),G(G(T)))
```

The two geometries are exact horizontal reflections.

## D1 matched-null result

The D1 matched null keeps:

- identical occupied vertices;
- identical local edges with weight 2;
- identical distance-2 bridge locations but bridge weight 0;
- identical probe;
- identical denominator 16;
- identical sample schedule;
- identical coordinate-free reader.

Observed result:

| Corpus | D1 matched null |
| --- | ---: |
| Phase 1 | 109/110 |
| Held-out width 4 | 27/27 |
| Extended | 136/137 |

The same reflected pair remains the only collision in Phase 1 and extended.

Therefore changing the local edge weight and Euler denominator does not explain
the D1 gain.

## D1 coupled result

Observed result:

| Corpus | D1 coupled |
| --- | ---: |
| Phase 1 | 110/110 |
| Held-out width 4 | 27/27 |
| Extended | 137/137 |

Increment relative to the matched null:

- Phase 1 distinct-signature gain: +1;
- held-out gain: 0;
- extended gain: +1;
- one pre-existing collision pair split;
- zero collision pairs introduced.

The split pair is exactly the previously retained Gate 1A reflected/reordered
pair.

## Construction statistics

Observed D1 bridge coverage:

| Corpus | Geometries with bridges | Total bridge edges |
| --- | ---: | ---: |
| Phase 1 | 109/110 | 8048 |
| Held-out width 4 | 27/27 | 1606 |
| Extended | 136/137 | 9654 |

Maximum observed weighted degree:

```text
7
```

Declared analytical upper bound:

```text
12 < 16
```

Therefore the predeclared Euler denominator remains above the declared and
observed weighted-degree bounds.

## Determinism and provenance

The initial complete JSON replay was executed twice and was byte-identical.

Initial full JSON SHA256:

```text
b136ccedaaf7d0b1cc7e409d583b661e251fb36909f4d73147783d7ffe6e5d5e
```

D1 source SHA256 used for that replay:

```text
2b74a936319c708e261d2d4eabba4a6d4afde1c322dbe2245443312be0f27b27
```

The evidence runner also records the frozen baseline and width-4 source
digests.

Phase 1 experimental encoder continuity remains exact:

```text
110/110
```

Translation controls pass.

The D1 source-boundary audit passes.

## Reflection causality audit

The primary 110/110 result requires a more precise interpretation than simply
saying that D1 breaks the reflected collision.

For the retained reflected pair, the audit establishes:

1. geometry B is the exact horizontal reflection of geometry A;
2. the D1 coupled weighted graph is reflection-equivariant;
3. the D1 matched-null graph is reflection-equivariant;
4. the original four-neighbor component partition is reflection-equivariant;
5. the frozen minimum, maximum, and endpoint probes selected independently in
   canonical coordinates are not transported into one another by reflection;
6. when the minimum probe on A is transported through the actual reflection
   isomorphism, both null and coupled coordinate-free signatures match B;
7. with independently selected frozen minimum probes, the null signatures
   match but the coupled signatures differ;
8. the first full-state multiset divergence occurs at propagation step 2;
9. a local-degree probe derived intrinsically from the graph is
   reflection-equivariant;
10. with that intrinsic control probe, the coupled coordinate-free signatures
    of the reflected pair match.

## Causal classification

The D1 weighted graph does not intrinsically destroy horizontal-reflection
symmetry.

The supported bounded interpretation is narrower:

> Weak cross-clearance coupling makes a difference in the coordinate-derived,
> asymmetric frozen probe globally observable. That incremental interaction
> splits the previously retained reflected pair relative to the matched null.

Therefore:

- D1 is positive relative to its declared matched null;
- the bridge coupling is necessary for the observed primary +1 distinction
  under the frozen primary protocol;
- the result is not evidence that the D1 weighted graph itself has an
  orientation-sensitive invariant;
- the result is not evidence of intrinsic coordinate-free reflection breaking;
- attribution to probe choice versus propagation is explicitly deferred to
  Gate 3 spectral/probe/observation controls.

## D1 intermediate decision

G2-D1 is retained as a **positive but qualified Gate 2 construction**.

It satisfies the declared Gate 2 criterion of reproducible incremental
information relative to a matched null:

- deterministic geometry-only construction;
- no declared hidden identity channel;
- frozen B0 replay unchanged;
- +1 distinct signature on Phase 1 and extended;
- zero newly introduced collision pairs;
- exact translation replay;
- explicit causal qualification retained.

This is not yet a final Gate 2 decision.

## What D1 does not establish

D1 does not establish:

- an intrinsic orientation-sensitive invariant of the weighted graph;
- a physical propagation mechanism;
- spectral uniqueness;
- probe independence;
- sample-time independence;
- complete dynamic decoding;
- theorem-level injectivity;
- robustness to perturbation or noise;
- independent reproduction;
- production readiness.

## G2-F0 result

G2-F0 has now been evaluated as the factor-boundary null control.

The construction is:

- native FGS immediate root factors;
- frozen graph-Laplacian v1 independently inside every factor;
- no state exchange between factors;
- multiplicity preserved;
- final factor order removed.

Observed discrimination:

| Corpus | Factor count | Static factor profile | Ordered dynamic control | F0 unordered dynamic |
| --- | ---: | ---: | ---: | ---: |
| Phase 1 | 4/110 | 47/110 | 110/110 | 63/110 |
| Held-out width 4 | 3/27 | 9/27 | 27/27 | 12/27 |
| Extended | 5/137 | 56/137 | 137/137 | 75/137 |

Primary F0 collision structure:

- Phase 1: 31 collision groups, 78 colliding forms, maximum group size 6;
- held-out: 5 collision groups, 20 colliding forms, maximum group size 6;
- extended: 36 collision groups, 98 colliding forms, maximum group size 6.

Immediate factor occurrences:

- Phase 1: 231;
- held-out: 86;
- extended: 317.

Native FGS exact recomposition passes for all 137 forms.

Factor multiplicity is preserved.

The F0 source-boundary and no-coupling audits pass.

The complete F0 JSON replay is byte-identical across two fresh runs.

Initial complete F0 JSON SHA256:

`1ac303a86ffa0d5596b586891bf80e0c0f7a641b36c72a27fe41271b9c992773`

F0 source SHA256 used for that replay:

`73dc95c14cd846f291211f1ceca76682747029accbb4e05f81311378b6b4db6e`

### F0 classification

G2-F0 is retained as a **valid, non-injective factor-boundary control**.

The result separates three effects that must not be conflated.

First, factor count alone is weak.

Second, geometry-derived information internal to each factor is meaningful:
the unordered dynamic factor reader increases the bounded distinct-signature
count from 47 to 63 on Phase 1 and from 56 to 75 on the extended domain
relative to the declared static factor-profile control.

Third, native factor order is an extremely strong channel in this bounded
domain: the labelled ordered diagnostic reaches 110/110, 27/27, and 137/137.
That result is not admissible as primary Gate 2 evidence because factor order
is precisely the information deliberately removed from F0.

The retained Gate 1A reflected/reordered pair behaves as required:

- ordered diagnostic: separated;
- primary unordered F0: colliding.

Therefore F0 does not smuggle sibling order into the reader.

F0 is not a positive global-coupling result because it contains no
inter-factor interaction.

Its scientific role is the matched factor-boundary reference for G2-F1.

## G2-F1 result

G2-F1 has now been evaluated as the first FGS-informed geometric coupling
construction.

The frozen construction uses:

- immediate native FGS factors as dynamic regions;
- geometry-reconstructed factor occurrences;
- complete pairwise factor graph;
- exact inverse minimum-Manhattan-distance weights;
- six intrinsic graph-profile feature channels per factor;
- exact rational weighted averaging;
- factor order removed from the primary reader;
- frozen F0 carried separately as the factor-boundary reference.

Observed discrimination:

| Corpus | F0 | F1 null | F1 coupled | Joint null | Joint coupled |
| --- | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | 63/110 | 47/110 | 58/110 | 63/110 | 75/110 |
| Held-out width 4 | 12/27 | 9/27 | 15/27 | 12/27 | 18/27 |
| Extended | 75/137 | 56/137 | 73/137 | 75/137 | 93/137 |

Increment from factor proximity coupling alone:

- Phase 1: +11 distinct signatures, 44 collision-pairs split;
- held-out: +6 distinct signatures, 25 collision-pairs split;
- extended: +17 distinct signatures, 69 collision-pairs split;
- zero new collision-pairs in every partition.

Increment beyond the frozen F0 factor-only channel, measured with the
predeclared joint reader:

- Phase 1: 63 -> 75 distinct signatures;
- held-out: 12 -> 18;
- extended: 75 -> 93;
- 40, 25, and 65 collision-pairs respectively are split;
- zero new collision-pairs are introduced.

Inter-factor coupling is active in:

- 84/110 Phase 1 geometries;
- 21/27 held-out geometries;
- 105/137 extended geometries.

The complete factor graph contains:

- 160 pairwise edges over Phase 1;
- 116 over held-out;
- 276 over extended.

Observed minimum factor distances range from 4 through 20.

Exact native FGS recomposition passes throughout.

Source-boundary and deterministic-replay audits pass.

The complete F1 evidence replay is byte-identical across two runs.

Initial complete F1 JSON SHA256:

`33d66468fee481d683251c669511a04173d0aa2f6b9bfc9174102741dcba277f`

F1 source SHA256 used for that replay:

`9a6b7daa043f4173046319bb407ca922139be60e4bfa202b467c3f8cdf09f401`

### F1 reflection audit

The retained Gate 1A pair remains colliding under:

- F1 matched null;
- F1 coupled primary reader;
- joint F0+F1 null;
- joint F0+F1 coupled.

The audit additionally confirms that, across the factor permutation induced by
the exact horizontal reflection:

- pairwise factor distances are equivariant;
- inverse-distance weights are equivariant;
- intrinsic factor features are equivariant.

The ordered F1 diagnostic does not match across the reflected pair, as expected:
it retains native factor order and remains a labelled, inadmissible control.

The primary reader removes that order and preserves reflection symmetry.

### F1 classification

G2-F1 is retained as a **positive Gate 2 global-coupling construction**.

The strongest supported bounded claim is:

> Geometry-derived proximity coupling among immediate native FGS factors adds
> reproducible coordinate-free information beyond the frozen factor-only F0
> control while preserving the declared reflection symmetry.

This result is cleaner causally than D1:

- the gain survives the predeclared joint F0+F1 comparison;
- no factor ordinal reaches the primary reader;
- no coordinate-derived asymmetric probe is required;
- the construction and intrinsic feature state are reflection-equivariant;
- no new collision-pairs are introduced.

The result remains bounded evidence. It does not establish complete
injectivity, intrinsic orientation recovery, spectral uniqueness, a physical
mechanism, or a theorem for arbitrary geometry.

## G2-L1 result

G2-L1 has now been evaluated as the FGS-independent uniform full-lattice
construction.

The frozen construction uses:

- the exact minimal axis-aligned bounding rectangle;
- every occupied and empty lattice site as a dynamic vertex;
- uniform four-neighbor edge weight 1;
- binary occupancy only as the initial scalar field;
- exact integer Euler numerators with denominator 8;
- sample steps 1, 2, 4, 8, 16, 32;
- a global coordinate-free state multiset as the primary reader.

Observed discrimination:

| Corpus | Lattice size | Step-0 static | Matched null | L1 coupled |
| --- | ---: | ---: | ---: | ---: |
| Phase 1 | 13/110 | 31/110 | 31/110 | 67/110 |
| Held-out width 4 | 4/27 | 9/27 | 9/27 | 16/27 |
| Extended | 14/137 | 35/137 | 35/137 | 83/137 |

Increment relative to the matched no-propagation null:

- Phase 1: +36 distinct signatures and 251 collision-pairs split;
- held-out: +7 distinct signatures and 29 collision-pairs split;
- extended: +48 distinct signatures and 339 collision-pairs split;
- zero new collision-pairs in every partition.

The matched-null collision partition is exactly the step-0 static partition in
all three corpus partitions.

Therefore the observed L1 increment is not explained by merely introducing the
bounding rectangle or by counting occupied and empty sites. It appears only
when state is allowed to propagate through the uniform lattice.

Empty lattice sites are present in:

- 109/110 Phase 1 geometries;
- 27/27 held-out geometries;
- 136/137 extended geometries.

Across the extended domain the bounded L1 runs contain:

- 34,897 lattice vertices;
- 65,208 lattice edges.

Maximum observed lattice degree is 4, matching the declared analytical bound
and satisfying 4 < 8.

Translation and reflection controls pass.

The retained Gate 1A reflected pair remains colliding under both matched null
and L1 coupled readers.

The complete L1 JSON replay is byte-identical across two runs.

Initial complete L1 JSON SHA256:

`ce6ffee0c9374b6ab464ba34e930000d5e6e7379db24622f8794aae22ab3c507`

L1 source SHA256 used for that replay:

`7ec1627fdbf0f048a8ace0587594da0021a80746138f2f0b3b9424773bab5f3b`

### L1 classification

G2-L1 is retained as a **positive Gate 2 global-coupling construction**.

The strongest supported bounded claim is:

> Uniform propagation through the empty sites of the geometry-derived minimal
> lattice adds reproducible coordinate-free information beyond the identical
> static occupied/empty field with propagation disabled.

This result is independent of FGS and structural factor identity.

It also preserves the declared reflection symmetry and translation invariance.

L1 does not establish complete injectivity, orientation recovery, spectral
uniqueness, a physical diffusion mechanism, robustness, or theorem-level
behavior outside the bounded corpus.

## G2-E1 result

G2-E1 has now been evaluated as the occupancy-aware heterogeneous
full-lattice construction.

The frozen construction keeps the same minimal full lattice and binary
occupancy initial field as the L1 family, but assigns symmetric material
conductances:

- empty-empty edge: weight 1;
- occupied-empty edge: weight 2;
- occupied-occupied edge: weight 3.

The causal matched control uses the identical domain, state, edge locations,
sample schedule, reader, and Euler denominator 16, with every edge weight set
to 1.

Observed discrimination:

| Corpus | Static material | Matched uniform q16 | E1 heterogeneous q16 | Frozen L1 q8 |
| --- | ---: | ---: | ---: | ---: |
| Phase 1 | 46/110 | 67/110 | 67/110 | 67/110 |
| Held-out width 4 | 9/27 | 16/27 | 16/27 | 16/27 |
| Extended | 55/137 | 83/137 | 83/137 | 83/137 |

Relative to the causal matched-uniform q16 control, E1 produces:

- zero distinct-signature gain;
- zero collision-pairs split;
- zero new collision-pairs;

in every corpus partition.

Consequently there is no dynamic distinction requiring attribution against the
static material diagnostic.

The heterogeneous medium is nevertheless genuinely nontrivial:

- all three edge classes 1, 2, and 3 occur in the bounded corpus;
- maximum observed weighted degree is 11;
- the declared analytical bound 12 < 16 passes;
- elementary tests confirm that heterogeneous and uniform dynamics differ at
  the state level.

Across the extended domain the aggregate heterogeneous edge counts are:

- weight 1: 18,992;
- weight 2: 27,936;
- weight 3: 18,280.

Source-boundary, translation, reflection, exact-domain, weighted-degree, and
deterministic-replay audits all pass.

The retained Gate 1A reflected pair remains colliding under:

- static material diagnostic;
- matched uniform q16;
- heterogeneous E1 q16;
- frozen L1 q8.

The complete E1 JSON replay is byte-identical across two runs.

Initial complete E1 JSON SHA256:

`fc1e536003ba2547b030cbb044742cb14ca4fa74f7237e148d7155ae26dde8a6`

E1 source SHA256 used for that replay:

`f998e1653a931836e43ebb973fc27d17575a5069c46229e71986edf566263ef7`

### L1 q8 / matched-uniform q16 partition audit

A post-E1 read-only audit compared the complete corpus partitions induced by:

- frozen G2-L1 uniform propagation with `q=8`;
- the E1 matched-uniform propagation with `q=16`.

The partitions are exactly identical on all three frozen corpus partitions:

- Phase 1: 67 equivalence classes in both cases;
- held-out: 16 equivalence classes in both cases;
- extended: 83 equivalence classes in both cases.

The complete collision-pair sets are also exactly identical in every
partition.

This is a bounded cross-denominator diagnostic only.

It does not establish general denominator invariance or parameter robustness.

### E1 classification

G2-E1 is retained as **valid negative Gate 2 evidence** for the frozen
occupancy-aware conductance law.

The strongest supported bounded claim is:

> For the frozen edge law `1 + occupancy(u) + occupancy(v)`, making the
> full-lattice medium heterogeneous adds no observable coordinate-free
> discrimination beyond an otherwise matched uniform medium.

This negative result sharpens the positive L1 interpretation.

Within the bounded domain, the important gain appears when empty space becomes
part of a communicating lattice. The tested occupancy-dependent modification
of that medium does not add further distinctions.

This does not establish that every possible heterogeneous medium is
uninformative. It applies only to the frozen E1 law, state, schedule, and
reader.

## Gate 2 matrix finalization

The evaluated matrix now contains:

- G2-B0 — frozen occupied-cell baseline;
- G2-D1 — positive but probe-qualified weak clearance coupling;
- G2-F0 — valid non-injective factor-boundary control;
- G2-F1 — positive FGS-informed proximity coupling;
- G2-L1 — positive uniform full-lattice propagation;
- G2-E1 — valid negative occupancy-aware heterogeneous-medium result.

Before the final Gate 2 decision, G2-C0 must either be replayed or explicitly
classified from its previously declared control contract. No new positive
construction should be invented merely to improve corpus discrimination.

## G2-C0 result

G2-C0 has now been evaluated as the final declared Gate 2 matrix control.

C0 explicitly preserves disconnected occupied-component boundaries while
removing component placement, displacement, and ordering.

Each independently normalized component is observed through the unchanged
frozen graph-Laplacian v1 `global_multiset` reader.

Observed discrimination:

| Corpus | Component count | Static component profile | Frozen B0 | C0 dynamic |
| --- | ---: | ---: | ---: | ---: |
| Phase 1 | 7/110 | 47/110 | 109/110 | 109/110 |
| Held-out width 4 | 3/27 | 9/27 | 27/27 | 27/27 |
| Extended | 7/137 | 56/137 | 136/137 | 136/137 |

Relative to frozen B0, C0 produces in every corpus partition:

- zero distinct-signature gain;
- zero collision-pairs split;
- zero new collision-pairs.

The retained Gate 1A reflected/reordered pair remains colliding under both B0
and C0.

The bounded C0 corpus contains:

- 684 component occurrences in Phase 1;
- 182 in held-out;
- 866 in the extended domain;
- at most 7 disconnected components per geometry.

Source-boundary, translation, displacement, component-order, exact-partition,
multiplicity, reflected-pair, and deterministic-replay audits all pass.

The complete C0 evidence replay is byte-identical across two runs.

Initial complete C0 JSON SHA256:

`de521bf9f188b6d59ed4cf8303ec0bebdcb110b73d43ee16c78b38ce577d152d`

C0 source SHA256 used for that replay:

`37d3abaeb4846de0fcaaaa88dd9022f4b86a9992131d01e86265f5e54d216ead`

### C0 classification

G2-C0 is retained as a **valid negative representation control**.

The strongest supported bounded claim is:

> Explicitly preserving disconnected component boundaries, while discarding
> their placement and order and introducing no inter-component interaction,
> adds no coordinate-free discrimination beyond frozen B0 on the declared
> corpus.

Therefore component-boundary representation alone does not explain the positive
global-coupling effects observed elsewhere in Gate 2.

## Gate 2 final matrix

| Construction | Role | Phase 1 | Held-out | Extended | Classification |
| --- | --- | ---: | ---: | ---: | --- |
| G2-B0 | Frozen occupied-cell baseline | 109/110 | 27/27 | 136/137 | baseline |
| G2-C0 | Component-boundary representation, no coupling | 109/110 | 27/27 | 136/137 | valid negative control |
| G2-D1 | Weak distance-2 clearance coupling | 110/110 | 27/27 | 137/137 | positive but probe-qualified |
| G2-F0 | Unordered independent FGS factors | 63/110 | 12/27 | 75/137 | valid non-injective control |
| G2-F1 | FGS factor-proximity coupling, joint F0+F1 | 75/110 | 18/27 | 93/137 | positive |
| G2-L1 | Uniform full-lattice propagation | 67/110 | 16/27 | 83/137 | positive |
| G2-E1 | Occupancy-aware heterogeneous full lattice | 67/110 | 16/27 | 83/137 | valid negative versus matched uniform |

### Causal interpretation

The matrix supports several distinct conclusions.

1. **Representation alone is insufficient.**

   G2-C0 preserves disconnected component boundaries explicitly but induces
   exactly the same bounded partition as B0.

2. **FGS factor boundaries alone are insufficient.**

   G2-F0 is strongly non-injective when factor order is removed.

   Its labelled ordered diagnostic is perfectly discriminative on the bounded
   corpus but is inadmissible as primary evidence because it exposes factor
   order.

3. **Geometry-derived factor proximity adds information.**

   Relative to the predeclared joint F0+F1 null, G2-F1 improves:

   - 63 -> 75 classes on Phase 1;
   - 12 -> 18 on held-out;
   - 75 -> 93 on extended.

   It splits 40, 25, and 65 collision-pairs respectively and introduces none.

   The retained reflection pair remains colliding and the factor distances,
   weights, and intrinsic features are reflection-equivariant.

4. **Uniform propagation through empty space adds information.**

   Relative to its matched no-propagation null, G2-L1 improves:

   - 31 -> 67 classes on Phase 1;
   - 9 -> 16 on held-out;
   - 35 -> 83 on extended.

   It splits 251, 29, and 339 collision-pairs respectively and introduces none.

   The matched null has exactly the same collision partition as the step-0
   occupied/empty multiset.

   Thus the increment appears only when the full lattice becomes a communicating
   medium.

5. **The frozen heterogeneous material law adds no further information.**

   G2-E1 and its matched uniform q=16 control induce exactly the same bounded
   partitions.

   This is valid negative evidence for the frozen
   `1 + occupancy(u) + occupancy(v)` law, not for all possible heterogeneous
   media.

6. **The L1 result is not an artifact of the tested Euler denominator.**

   A bounded read-only diagnostic confirms that uniform full-lattice propagation
   at q=8 and q=16 induces exactly the same equivalence partition and exactly
   the same collision-pair set on Phase 1, held-out, and extended corpora.

   This is not a general denominator-invariance theorem.

7. **D1 remains causally qualified.**

   D1 reaches 110/110 and 137/137, but the weighted graph itself remains
   reflection-equivariant.

   Its additional distinction is attributable to the interaction between the
   new coupling and the frozen coordinate-derived asymmetric probe.

   D1 therefore cannot be used as evidence of intrinsic reflection breaking.

## Gate 2 final decision

Gate 2 is **complete with positive bounded support for global geometric
coupling**.

The central supported conclusion is:

> Geometry-derived interaction can make global information observable to a
> coordinate-free reader beyond what is available from disconnected
> representation alone.

Two independent positive constructions support that conclusion:

- G2-F1: proximity coupling among geometry-derived FGS regions;
- G2-L1: uniform propagation through the full geometry-derived lattice,
  including empty sites.

These effects survive their declared matched controls and introduce no new
collision-pairs on the frozen corpora.

G2-C0 rules out explicit component-boundary preservation as an explanation for
the occupied-cell baseline result.

G2-F0 separates factor representation from factor interaction.

G2-E1 demonstrates that a more elaborate local material law is not
automatically more informative.

The retained exact horizontal-reflection pair remains unresolved by the
coordinate-free primary readers of C0, F0/F1, L1, and E1.

Therefore Gate 2 does **not** establish:

- universal injectivity;
- intrinsic orientation recovery;
- intrinsic reflection breaking;
- spectral uniqueness;
- robustness under perturbation;
- dynamic decoding;
- physical or cosmological equivalence;
- theorem-level behavior for arbitrary geometries.

Those questions remain outside Gate 2.

No Gate 3 result is used in this decision.

## Gate 2 status

**Complete.**

The declared Gate 2 matrix has been evaluated without adding a post-result
construction to improve discrimination.

The next gate remains Gate 3, but it is not activated by this decision.
