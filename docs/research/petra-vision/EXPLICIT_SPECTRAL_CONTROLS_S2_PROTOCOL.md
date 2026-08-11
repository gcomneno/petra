# PETRA VISION Gate 3 — G3-S2 component/factor spectral controls

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Frozen before any G3-S2 corpus evaluation.

Parent issue: #200.

Gate 3 branch:

`research/issue-200-explicit-spectral-controls`

Completed predecessor:

`G3-S0/S1`

Predecessor evidence commit:

`fcdf567`

Protocol identifier:

`petra-vision-explicit-spectral-controls-s2-v0`

No G3-S2 Phase 1, held-out, or extended discrimination result was inspected
before this protocol was selected.

## Research question

How much coordinate-free information is present in spectra of native local
structural units when their ordering and global placement are discarded?

G3-S2 distinguishes local spectral content from the spectrum or response of
the globally coupled operator.

It does not optimize a classifier.

It does not modify any Gate 0, Gate 1, Gate 2, or G3-S0/S1 construction.

## Frozen corpus discipline

Any later evidence must report separately:

1. Phase 1: 110 forms;
2. held-out width 4: 27 forms;
3. extended domain: 137 forms.

Evidence is observed in that order.

No result from a later corpus partition may be used to tune an earlier
protocol.

## Exact spectral representation

G3-S2 reuses the exact characteristic-polynomial representation frozen in
G3-S1.

For an operator `M`:

`chi_M(x) = det(xI - M)`

The signature of one local unit is the complete exact monic coefficient
sequence.

Every coefficient is canonically serialized as a reduced rational pair:

`(numerator, denominator)`

No floating-point eigensolver, spectral tolerance, root approximation,
eigenvector ordering, or numerical binning is permitted.

## Local-unit aggregation

When more than one local unit exists, their spectra are exposed only as an:

- unordered;
- multiplicity-preserving;
- coordinate-free

multiset.

Operationally, each exact local spectral signature is canonically serialized,
the signatures are sorted lexicographically only for canonical output, and
duplicates are retained.

The sort is serialization normalization, not structural order.

The final reader receives no local-unit ordinal.

## G3-S2-B0 — occupied-component spectra

### Native units

Use the connected components already derived by the frozen B0 four-neighbor
occupied-cell graph.

These are the native disconnected components of the B0 representation.

### Local operator

For each connected component independently, construct its exact unweighted
combinatorial Laplacian:

`L_c = D_c - A_c`

with weight `1` on every native four-neighbor occupied edge.

### Reader

Return the unordered multiplicity-preserving multiset of exact component
characteristic-polynomial signatures.

No component position, minimum coordinate, component ordinal, bounding box,
or original vertex identifier enters the reader.

### Causal comparison

Compare separately:

- G3-S1-B0 global exact operator spectrum;
- G3-S2-B0 component-spectrum multiset.

Because the frozen B0 operator is block diagonal across connected components,
the product of the component characteristic polynomials must exactly equal
the global B0 characteristic polynomial.

S2 may nevertheless retain more information than S1 because it preserves the
factorization of the global characteristic polynomial by native component
boundary while still discarding component order.

This consequence is frozen before results are observed.

## G3-S2-D1 — original-component local spectra

### Native units

Use `original_components` from the frozen Gate 2 D1 construction.

These components are defined from the original distance-1 local occupied
edges before distance-2 clearance bridges are added.

### Local operator

For each original component independently, construct the weighted local
Laplacian using only frozen D1 local edges:

- axial occupied distance 1;
- weight `2`.

Every D1 edge whose frozen kind is `bridge` is excluded from G3-S2-D1.

This exclusion is deliberate and causal.

G3-S2-D1 asks what spectral information existed in the original local units
before the global clearance coupling was introduced.

### Reader

Return the unordered multiplicity-preserving multiset of exact local
characteristic-polynomial signatures.

The reader receives no:

- component ordinal;
- component placement;
- coordinate;
- bridge endpoint;
- bridge count per component;
- original vertex identity.

### Causal comparison

Compare separately:

- G3-S1-D1 spectrum of the complete coupled weighted D1 operator;
- G3-S2-D1 spectra of the uncoupled original local components.

These are different causal objects and neither is declared a formal refinement
of the other.

Report partition differences explicitly rather than describing a higher
signature count as automatically better.

The purpose is to separate local spectral content from information created by
D1 clearance coupling.

## G3-S2-F1 — immediate FGS factor spectra

### Native units

Use exactly the immediate native FGS factors returned by the frozen positive
Gate 1B geometry-only factorizer.

Use only the immediate factors that correspond to the Gate 2 F1 dynamic
regions.

Do not recurse into descendants for the primary G3-S2-F1 reader.

Recursive factor spectra would be a different protocol.

### Factor-local operator

For each immediate FGS factor independently, construct the frozen B0
four-neighbor occupied-cell graph of that canonical factor geometry.

Use its exact unweighted combinatorial Laplacian.

The factor spectral signature is therefore an intrinsic spectrum of the
factor geometry itself.

It does not use:

- the F1 proximity matrix;
- factor-to-factor distance;
- F1 coupling weights;
- F1 feature values;
- factor ordinal.

### Reader

Return the unordered multiplicity-preserving multiset of immediate-factor
spectral signatures.

Repeated equal factor spectra remain repeated.

The ordered sequence returned internally by native FGS is not exposed.

### Terminal case

A terminal root has no immediate FGS factors.

Its primary G3-S2-F1 signature is therefore the empty multiset.

This is frozen before corpus evaluation.

### Causal comparisons

Compare G3-S2-F1 separately with:

1. G3-S0-F1 intrinsic factor-state control;
2. G3-S1-F1 global F1 propagation-operator spectrum;
3. the later frozen Gate 2 F1 dynamic result only at interpretation time.

Do not concatenate these channels into a joint signature during the initial
S2 evaluation.

G3-S2 asks only whether factor-local spectra contribute information that is
absent from the previously isolated controls.

## G3-S2-L1 — not applicable

The frozen L1 representation has one connected full rectangular lattice as
its propagation medium.

It does not have native disconnected operator components.

Gate 1B FGS factors are not part of the frozen L1 representation.

Therefore the primary G3-S2 protocol declares L1:

`not_applicable`

G3-S2 must not create artificial units from:

- connected components of occupied cells;
- rows or columns of the lattice;
- rectangular tiles;
- FGS factors recovered only for this control;
- occupancy clusters.

Doing so would replace the frozen L1 representation with a new factorization.

L1 remains covered by:

- G3-S0 intrinsic occupancy control;
- G3-S1 global medium spectrum;
- later matched propagation/temporal attribution.

## Relationship to G3-S0/S1

G3-S2 does not supersede G3-S0/S1.

The channels remain distinct:

- S0 operator elementary information;
- S0 intrinsic state where defined;
- S1 global operator spectrum;
- S2 native local-unit spectral multiset.

No initial S2 evidence runner may concatenate these into a stronger joint
reader.

Any future joint diagnostic must be separately labelled and justified.

## Required measurements

For every applicable substrate and corpus partition record:

- local-unit count distribution;
- S2 distinct-signature count;
- exact collision groups;
- collision-pair count;
- behavior of the Gate 1A `#23/#41` pair where both forms are present;
- partition differences relative to the declared matched S1 control;
- for F1, partition differences relative to S0 intrinsic state as a separate
  comparison;
- deterministic replay;
- source SHA256;
- evidence-runner SHA256;
- exact evidence digest.

When comparing two partitions report:

- pairs split;
- pairs introduced.

No collision group is suppressed.

## Structural verification before corpus evidence

Before any G3-S2 corpus result is observed, implementation tests must establish
at minimum:

1. B0 component extraction uses only the frozen B0 graph components;
2. B0 local component matrices use only native weight-1 occupied edges;
3. the product of B0 component characteristic polynomials equals the global
   B0 characteristic polynomial on declared synthetic controls;
4. B0 S2 is invariant to permutation of component presentation order;
5. B0 S2 is invariant to vertex relabelling within a component;
6. D1 units equal the frozen `original_components`;
7. D1 local matrices contain only `local` edges with weight `2`;
8. no D1 `bridge` edge enters an S2 local matrix;
9. D1 S2 is invariant to permutation of component presentation order;
10. F1 factors come from the frozen geometry-only `native_fgs`;
11. the immediate factors exactly recompose the source geometry through the
    existing Gate 1B contract;
12. F1 S2 discards factor order while preserving repeated spectra;
13. terminal F1 produces the empty S2 multiset;
14. L1 returns an explicit not-applicable result rather than inventing a local
    decomposition;
15. primary S2 serialization is byte deterministic;
16. no probe, impulse-response, temporal, oriented-reader, corpus-index, shape
    code, decoded AST identity, or serialization identity enters a primary S2
    signature.

These structural tests may use synthetic geometries.

They must pass before any frozen 110/27/137 S2 discrimination is generated.

## Identity-channel boundary

Primary S2 signature construction may use only geometry-derived structures
already admitted by the frozen substrate contracts.

The primary reader must not receive:

- `VisionShape`;
- `Terminal`;
- `OrderedGroup`;
- `decode_geometry`;
- shape code;
- corpus position;
- filename;
- PETRA structural address;
- component ordinal;
- factor ordinal;
- original coordinates as signature metadata;
- object identity.

Shape codes may be used only after signature computation for human-readable
evidence reporting.

## Reflection and translation discipline

Local spectral signatures are coordinate-free operator invariants.

For declared translation and reflection controls, a geometry-derived unit and
its transformed counterpart must produce the same local spectral signature
whenever the frozen unit extraction itself is equivariant.

No orientation-sensitive local reader is evidence for G3-S2.

## Success interpretation

A positive G3-S2 result means only that preserving an unordered multiset of
native local spectra adds bounded discrimination relative to the declared
comparison.

It does not establish:

- uniqueness of spectral decomposition;
- graph reconstruction;
- factor reconstruction;
- geometry reconstruction;
- complete PETRA decoding.

A negative result is equally valid and must be retained.

## Gate boundary

G3-S2 does not execute:

- G3-H1 heat-trace compression;
- G3-P1 probe ablation;
- G3-I1 impulse-response attribution;
- G3-T1 temporal observation;
- G3-O1 orientation diagnostics;
- Gate 4 adversarial mutation generation.

The next Gate 3 step after completed S2 evidence is G3-H1.

## Non-claims

G3-S2 does not establish:

- universal injectivity;
- spectral uniqueness;
- canonical prime-like factorization beyond the bounded FGS contract;
- intrinsic orientation;
- robustness;
- physical propagation;
- physical time or spacetime;
- theorem-level reconstruction.

## Completion condition

G3-S2 is complete when B0, D1, and F1 local spectral controls have been
evaluated separately on the frozen 110/27/137 corpus partitions with
deterministic replay and explicit partition comparisons, while L1 remains
explicitly not applicable under the frozen representation.
