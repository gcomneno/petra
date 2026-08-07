# PETRA VISION Structural Geometric Factorization — Evidence

## Status

Gate 1B — Structural Geometric Factorization (FGS): complete for the
declared bounded domain.

Protocol family:

- `petra-vision-structural-geometric-factorization-v0`
- `petra-vision-structural-geometric-factorization-width4-v0`
- `petra-vision-structural-geometric-factorization-extended-v0`

The final decision is positive for the declared canonical geometric grammar and
the bounded 137-form domain only.

It is not a theorem of general or arithmetic unique factorization.

## Research question

Gate 1B asks whether a valid canonical PETRA VISION geometry can be decomposed
directly into ordered canonical geometric factors corresponding exactly to the
immediate branches of its structural root and then recomposed without loss.

The new research claim is specifically the native geometry-only route.

The existing structural and decoder-mediated routes are controls.

## Factorization levels

Three levels remain distinct.

1. Structural factorization obtains the immediate ordered children directly
   from `VisionShape`. This is the independent structural oracle.
2. Decoder-mediated factorization decodes canonical geometry to `VisionShape`
   and re-encodes the immediate children. This is a Phase 1 control.
3. Native FGS operates directly on `OrthogonalGeometry`, extracts ordered
   geometric factor payloads, normalizes them, and recursively reapplies the
   same geometry-only operation.

Only the third level supports the Gate 1B native claim.

## Frozen native boundary

The native factorizer is:

`tools/research/petra_vision_structural_geometric_factorization.py`

Its source SHA256 for all final Phase 1, held-out, and extended replays is:

`0362fa812c12ae718066cc077ab14e91d742af06c2e91c4e795e121900ca87ff`

The native implementation imports only the geometry representation and
`geometry_extent` from `petra.vision.geometry`.

Its public research boundary receives `OrthogonalGeometry`.

The native implementation does not use:

- `VisionShape`;
- `Terminal`;
- `OrderedGroup`;
- `decode_geometry`;
- `encode_geometry`;
- PETRA adapters;
- structural addresses;
- shape codes;
- serialization;
- corpus positions;
- filenames;
- object identity;
- annotated factor boundaries.

The source/AST audit passed.

This audit establishes the inspected source boundary. It is not a formal
transitive information-flow proof.

## Native geometric rule

A non-terminal canonical geometry contains ordered root bays separated by
full-height vertical columns.

Native FGS:

1. identifies the full-height root boundaries from occupied cells;
2. reads adjacent boundary pairs as ordered bays;
3. extracts the occupied payload strictly inside each bay;
4. verifies the declared geometric clearances and alignments;
5. translates each payload to canonical origin;
6. emits one `OrthogonalGeometry` per factor in left-to-right order.

Repeated equal factors remain repeated occurrences.

Therefore the operation preserves order and multiplicity.

The terminal one-cell geometry produces the empty factor tuple.

## Cell ownership

`OrthogonalGeometry` contains only occupied integer-lattice cells and has no
additional per-cell attributes.

For every accepted non-terminal parent, the source cells are accounted for by
two disjoint classes:

- root scaffold cells: frame and full-height separators;
- translated immediate-factor cells.

The implementation rejects overlap and requires the union of those classes to
equal the complete source geometry exactly.

No occupied source cell may be lost or duplicated.

## Exact recomposition

Recomposition is performed directly from the ordered factor geometries.

It reconstructs:

- parent height from maximum factor height plus the frozen clearance;
- root frame and separators;
- bay widths from factor widths;
- factor placement from the frozen geometric alignment rule.

For every successful source in the declared domain:

`recompose_fgs(native_fgs(G)) == G`

The comparison is exact `OrthogonalGeometry` equality, not only structural or
reader equivalence.

## Phase 1 evidence

Corpus:

- 110 exhaustive bounded Phase 1 forms;
- maximum 7 nodes;
- maximum depth 3;
- maximum width 3.

Results:

| Check | Result |
|---|---:|
| Immediate native factors vs structural oracle | 110/110 |
| Decoder-mediated factors vs structural oracle | 110/110 |
| Recursive native structure vs structural oracle | 110/110 |
| Exact recomposition | 110/110 |
| Deterministic replay | 110/110 |
| Recursive non-root occurrences | 574/574 |
| Malformed controls | 7/7 |
| Native identity/source audit | pass |

The recursive result is stronger than root-only agreement: all 574 non-root
factor occurrences represented across the 110 forms are recovered through
repeated geometry-only factorization.

## Malformed controls

The Phase 1 evidence includes explicit negative controls for:

- noncanonical global translation under Contract v0;
- incomplete outer frame;
- empty bay;
- invalid horizontal child clearance;
- extra full-height separator;
- a parent whose immediate extraction is locally valid while its nested child
  is malformed.

The nested control verifies that the parent is accepted at the root level and
that recursive native factorization rejects the malformed extracted child.

No malformed geometry in these controls is silently repaired.

## Held-out width-4 evidence

The held-out set consists of the 27 width-4 forms present in the extended
domain and absent from Phase 1.

It is disjoint from the 110-form Phase 1 corpus.

The native factorizer was not changed after obtaining the Phase 1 result.

Results:

| Check | Result |
|---|---:|
| Immediate native factors vs structural oracle | 27/27 |
| Recursive native structure vs structural oracle | 27/27 |
| Exact recomposition | 27/27 |
| Deterministic replay | 27/27 |
| Recursive non-root occurrences | 155/155 |
| Native identity/source audit | pass |

The production Phase 1 decoder was deliberately not extended to width 4 and is
not used as a held-out baseline.

The held-out structural oracle and geometry generation remain in the evidence
layer.

## Extended 137-form evidence

The extended domain is the exact partition:

- 110 Phase 1 forms;
- 27 held-out width-4 forms;
- 137 total forms.

The experimental width-4 encoder reproduces the frozen Phase 1 geometry
exactly on all 110 original forms:

| Check | Result |
|---|---:|
| Phase 1 encoder continuity | 110/110 |
| Extended immediate native factors vs oracle | 137/137 |
| Extended recursive native structure vs oracle | 137/137 |
| Extended exact recomposition | 137/137 |
| Extended deterministic replay | 137/137 |
| Extended recursive non-root occurrences | 729/729 |

The occurrence count is exactly:

`574 + 155 = 729`

The native factorizer source SHA256 remains `0362fa812c12ae718066cc077ab14e91d742af06c2e91c4e795e121900ca87ff`.

## Deterministic replay and provenance

Each final evidence report was generated independently twice and compared
byte-for-byte.

All three A/B pairs were identical.

Serialized JSON SHA256 values from the final provenance replay are:

| Evidence | SHA256 |
|---|---|
| Phase 1 | `ef4d4902b8897a773d466b8cd18ed3f6e488834d668dc61acd3bc1af89f33f64` |
| Held-out width 4 | `48093c24473637d22b638b8257e3365a277b669817dff45a1653048636e98b04` |
| Extended 137 | `a730ded194261c2031e2976ac23b1fa393a36a8419626982a013e66d6e491e87` |

The extended report's canonical internal report digest is:

`f0d84ac99b2b2aeb9892dfc60d4ddec2dfbd65effd9c2d5add284407250411a4`

All three reports embed the same native factorizer source SHA256 and that value
matches the factorizer file on the filesystem.

This turns the statement that the factorizer remained unchanged across the
three experiments into reproducible provenance evidence rather than reporting
metadata alone.

## Interpretation

Within the declared canonical grammar and bounded corpora, immediate structural
branch boundaries are directly recoverable from geometry.

The evidence supports the following bounded statements.

1. The root scaffold provides a geometry-only rule for locating ordered bays.
2. Each bay yields one canonical immediate factor without invoking the complete
   structural decoder.
3. Factor order is carried by geometric left-to-right bay position.
4. Repeated equal factors preserve multiplicity.
5. The same operation recursively reproduces the complete bounded structural
   branching pattern.
6. The emitted factors exactly recompose the original source geometry.
7. The Phase 1-derived native factorizer generalizes unchanged to the held-out
   width-4 corpus.
8. No declared hidden identity channel is present in the inspected native
   source boundary.

## Relationship to Gate 1A

Gate 1A showed that the frozen coordinate-free dynamic readers intentionally
discard enough spatial ordering to create one structural collision class.

Gate 1B asks a different question.

FGS operates on the complete canonical occupied-cell geometry before applying
those coordinate-free reader quotients.

The positive Gate 1B result therefore does not contradict the Gate 1A
collision. It shows that the canonical geometry itself contains immediate
ordered structural boundaries that the coordinate-free readers may later
discard.

## Final decision

Gate 1B is complete for the declared bounded domain.

Native FGS is accepted as a valid research object for downstream PETRA VISION
experiments because it satisfies, on the declared evidence:

- geometry-only immediate extraction;
- exact factor order;
- multiplicity preservation;
- recursive applicability;
- exact cell ownership;
- canonical normalization;
- exact recomposition;
- deterministic replay;
- malformed-input rejection;
- inspected source-boundary independence from structural identity channels;
- unchanged held-out width-4 generalization.

This permits FGS factors to be used as candidate dynamic units in Gate 2.

## Limitations and non-claims

The evidence does not establish:

- theorem-level uniqueness over arbitrary geometries;
- validity outside the declared canonical grammar;
- robustness to noise or damaged geometries;
- factor-boundary recovery under adversarial perturbation;
- arithmetic prime factorization;
- a commutative multiplication law;
- spectral uniqueness of individual factors;
- Gate 2 factor-graph semantics;
- complete dynamic decoding;
- production API readiness.

`Terminal` is irreducible only relative to the frozen PETRA VISION grammar.

The composition operation is ordered and n-ary.

No stronger prime-factorization analogy is claimed.

## Research artifacts

Contract:

- `STRUCTURAL_GEOMETRIC_FACTORIZATION_CONTRACT.md`

Native factorizer:

- `tools/research/petra_vision_structural_geometric_factorization.py`

Evidence tools:

- `tools/research/petra_vision_structural_geometric_factorization_evidence.py`
- `tools/research/petra_vision_structural_geometric_factorization_width4_evidence.py`
- `tools/research/petra_vision_structural_geometric_factorization_extended_evidence.py`

Focused tests:

- `tests/test_tools_petra_vision_structural_geometric_factorization.py`

Pipeline:

- `RESEARCH_PIPELINE.md`
