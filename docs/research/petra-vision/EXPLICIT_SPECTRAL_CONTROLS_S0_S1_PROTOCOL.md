# PETRA VISION Gate 3 — G3-S0/S1 protocol

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Frozen before corpus spectral evaluation.

Parent issue: #200.

Gate 3 foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

Gate 3 protocol-freeze commit preceding this subprotocol:

`3fb958c0da78d6b67d9035cb5f57a53af8628a46`

Temporal-hypothesis import commit:

`6ec5f55222983a7cd29465feca785ce74991738e`

No spectral coefficient, eigenvalue, collision partition, or discrimination
result from the frozen 110/27/137 corpora was inspected before this
subprotocol was selected.

## Purpose

G3-S0/S1 separates two questions:

1. what coarse coordinate-free information is available from the frozen
   operator or intrinsic initial state before propagation;
2. what additional distinctions, if any, are present in the exact spectrum
   of the frozen operator itself.

This is attribution only.

G3-S0/S1 does not change a Gate 2 operator, choose a new probe, tune a
parameter, or optimize a classifier.

## Environment freeze

The feasibility benchmark observed:

- Python environment:
  `/home/baltimora/Progetti/labs/petra/.venv`;
- SymPy `1.14.0`;
- SymPy ground types: `python`;
- NumPy: absent;
- SciPy: absent.

All primary S1 signatures therefore use exact SymPy arithmetic.

No floating-point eigenvalue approximation, rounding tolerance, spectral
binning, or approximate multiplicity comparison is permitted in G3-S1.

## Frozen corpus

Every result must be reported separately for:

1. Phase 1: `110` forms;
2. held-out width 4: `27` forms;
3. extended domain: `137` forms.

The 27 held-out forms must not be hidden inside a single 137-form headline
score.

## Frozen substrates

### G3-B0

Frozen Gate 0 / graph-Laplacian v1 occupied-cell graph.

S1 operator:

`L = D - A`

using the exact unweighted combinatorial Laplacian.

### G3-D1

Frozen Gate 2 distance-2 clearance graph.

S1 operator:

`L_w = D_w - A_w`

with the exact frozen integer weights:

- local axial distance-1 edge: weight `2`;
- clearance bridge: weight `1`.

The bridge rule itself is not changed.

### G3-F1

Frozen Gate 2 FGS factor-proximity system.

Gate 2 F1 is not an Euler update of a Laplacian. Therefore G3-S1 must not
silently replace its dynamics by a different Laplacian.

Its exact frozen propagation operator `P` is used directly.

For factor `i`, with pairwise proximity weights `w_ij`:

`z_i = 1 + sum_j(w_ij)`

and:

- `P_ii = 1 / z_i`;
- `P_ij = w_ij / z_i` for `i != j`.

All values are exact rational numbers.

The same `P` acts independently on each frozen F1 feature channel.

The feature-channel values are not part of the S1 operator-spectrum
signature.

### G3-L1

Frozen Gate 2 uniform full-lattice graph.

S1 operator:

`L_rect = D - A`

for the complete minimal rectangular four-neighbor lattice.

Occupancy is not part of `L_rect`.

Occupancy appears only in the frozen L1 initial scalar field.

Therefore two different geometries having the same full-lattice rectangle
necessarily have the same G3-L1 S1 operator signature.

This consequence is frozen before corpus S1 results are inspected.

## G3-S0 — static controls

S0 records separate named channels.

They must not be silently concatenated into one stronger signature unless a
combined reader is explicitly labelled as a diagnostic.

### S0 operator-elementary profile

For every substrate, record a coordinate-free elementary operator profile:

- operator order / vertex count;
- count of nonzero undirected interactions;
- number of connected components in the positive-weight support graph;
- sorted multiplicity-preserving multiset of weighted degrees.

Weights are represented exactly.

For an unweighted graph, every edge weight is the integer `1`.

For F1, the support graph is defined from the frozen symmetric proximity
weights `w_ij`, not from the generally non-symmetric normalized propagation
matrix `P`.

### S0 intrinsic-state profile

This is a separate channel and is present only when the initial state belongs
to the frozen representation independently of probe selection.

#### B0

No intrinsic-state S0 profile.

The minimum-component impulse is a probe and is deferred to G3-P1/I1.

#### D1

No intrinsic-state S0 profile.

The original-component minimum impulse is a probe and is deferred to
G3-P1/I1.

#### F1

Intrinsic state:

the unordered multiplicity-preserving multiset of the six frozen factor
feature vectors:

- vertices;
- edges;
- components;
- isolated vertices;
- total cycle rank;
- maximum degree.

Factor ordinal and left/right order are discarded.

#### L1

Intrinsic state:

the coordinate-free multiplicity-preserving multiset of the frozen occupancy
field values.

Because the field is binary, this is equivalent to retaining only the counts
of occupied and empty lattice sites.

No spatial occupancy ordering is exposed by this S0 reader.

## Exact rational serialization

Every exact scalar used in a primary signature is serialized canonically as:

`(numerator, denominator)`

with:

- denominator strictly positive;
- numerator and denominator in lowest terms;
- integer `n` represented as `(n, 1)`.

This applies to weighted degrees, rational F1 values, and S1 polynomial
coefficients.

## G3-S1 — exact operator spectrum

The primary S1 signature is the exact characteristic polynomial of the frozen
operator.

For an `n x n` operator `M`:

`chi_M(x) = det(xI - M)`

The signature is the complete ordered coefficient sequence of the monic
polynomial:

`(a_n, a_(n-1), ..., a_0)`

where `a_n = 1`.

Each coefficient is serialized as an exact canonical rational pair.

No eigenvectors are observed.

No vertex ordering is exposed to the final signature.

No numerical eigensolver is used.

No root approximation is used.

Equality means exact coefficient equality.

## S1 computation by substrate

### B0

Construct the exact integer combinatorial Laplacian and use SymPy
`Matrix.charpoly()`.

Feasibility benchmark at the largest observed order:

- order: `181`;
- exact direct charpoly: successful.

### D1

Construct the exact integer weighted Laplacian and use SymPy
`Matrix.charpoly()`.

Feasibility benchmark at the largest observed order:

- order: `181`;
- exact direct charpoly: successful.

### F1

Construct the exact rational frozen propagation matrix `P` and use SymPy
`Matrix.charpoly()` over exact rational values.

Feasibility benchmark at the largest observed order:

- order: `4`;
- exact direct charpoly: successful.

### L1

A direct `325 x 325` exact charpoly exceeded the pre-result 30-second
feasibility bound and is not the frozen primary implementation.

The full L1 lattice is the Cartesian product of two path graphs.

For rectangle dimensions `w` and `h`:

`Grid(w,h) = P_w square P_h`

and the Laplacian eigenvalues are pairwise sums of the path-Laplacian
eigenvalues.

The exact characteristic polynomial is therefore computed algebraically as:

`Res_y(chi_Pw(y), chi_Ph(x - y))`

where `Res` is the exact polynomial resultant.

The two rectangle dimensions are sorted before this computation so the
implementation itself is invariant to exchanging the two lattice axes.

The resulting polynomial is normalized to monic form before serialization.

Feasibility benchmark at the largest observed lattice:

- order: `325`;
- direct exact charpoly: timeout beyond the frozen 30-second benchmark bound;
- exact Cartesian-product resultant: successful.

The resultant is only a computational route to the spectrum of the same
frozen L1 operator. It is not a different reader or approximation.

## Required implementation verification before corpus evaluation

Before any 110/27/137 discrimination result is generated, implementation tests
must establish at minimum:

1. exact rational canonicalization;
2. matrix symmetry for B0, D1, and L1 Laplacians;
3. exact frozen F1 propagation-matrix construction;
4. characteristic polynomial degree equals operator order;
5. all primary characteristic polynomials are monic;
6. direct L1 charpoly equals resultant L1 charpoly on a declared suite of
   small rectangles;
7. swapping L1 rectangle dimensions leaves the resultant signature unchanged;
8. relabelling vertices leaves B0/D1 characteristic-polynomial signatures
   unchanged on explicit small controls;
9. no eigenvector, coordinate, factor ordinal, corpus index, shape code,
   serialization, or object identity enters a primary S1 signature;
10. deterministic replay returns byte-identical serialized signatures.

These tests may use synthetic small operators.

They must not report frozen corpus discrimination before the implementation
verification passes.

## Primary comparisons

For each substrate report separately:

- S0 operator-elementary partition;
- S0 intrinsic-state partition where defined;
- S1 exact operator-spectrum partition.

Do not initially combine S0 and S1 into a joint signature.

The first causal question is whether S1 separates shapes that collide under
the corresponding elementary operator profile.

For F1 and L1, intrinsic-state information remains a separate control because
the frozen dynamics depend on both operator and initial state.

## Collision accounting

For each corpus/substrate/control report:

- distinct-signature count;
- exact collision groups;
- collision-pair count;
- pairs split relative to the matched S0 operator-elementary control;
- pairs newly colliding relative to that control;
- behavior of the retained Gate 1A `#23/#41` pair when both forms belong to
  the evaluated corpus.

No collision may be removed from reporting merely because it contradicts a
hypothesis.

## Translation and reflection discipline

Characteristic-polynomial signatures are operator invariants.

For B0, D1, and L1, explicit translation controls must reproduce the same S1
signature.

Declared reflection controls must also reproduce the same S1 signature when
the frozen operator construction is reflection-equivariant.

F1 must retain the existing Gate 2 geometry-derived proximity law and must not
receive factor order in the S1 reader.

## Source boundary

Primary S0/S1 implementations may import frozen geometry-derived Gate 0–2
research tools required to construct the declared operators.

They must not use:

- decoded `VisionShape` as reader input;
- shape codes as reader input;
- corpus index;
- filenames;
- expected collision labels;
- structural address;
- factor ordinal;
- object identity;
- original coordinates as signature metadata.

Shape codes may appear only in evidence reporting after a signature has
already been computed.

## Evidence provenance

Final S0/S1 evidence must record:

- this protocol identifier;
- SymPy version;
- implementation source SHA256;
- evidence-runner SHA256;
- frozen substrate protocol identifiers;
- corpus provenance;
- deterministic JSON digest.

## Protocol identifier

`petra-vision-explicit-spectral-controls-s0-s1-v0`

## Interpretation boundary

A positive S1 result means only that the exact frozen operator spectrum
contains more bounded discrimination than the declared elementary static
operator control.

It does not imply:

- spectral uniqueness;
- graph isomorphism reconstruction;
- geometry reconstruction;
- complete PETRA decoding;
- intrinsic orientation;
- robustness;
- theorem-level injectivity.

A negative S1 result is equally valid.

## Next gate-internal step

After this protocol is committed:

1. implement S0/S1 without corpus-result reporting;
2. pass the declared implementation tests;
3. only then run the frozen Phase 1 / held-out / extended evidence;
4. interpret S0/S1 before beginning G3-P1/I1;
5. do not activate G3-T1 experiments yet.
