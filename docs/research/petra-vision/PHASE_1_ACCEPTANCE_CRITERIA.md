# Phase 1 acceptance criteria

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Objective

Demonstrate a deterministic, injective, compositional, and exactly
reversible mapping between the bounded VISION kernel domain and the
Phase 1 minimal geometry, plus lossless compatibility with the
supported native PETRA subset through an explicit adapter.

## A. Kernel and adapter validation

The geometry encoder must:

- accept every bounded Phase 1 kernel shape;
- reject malformed kernel values;
- leave the immutable source kernel shape unchanged.

The native PETRA adapter must:

- accept every supported canonical PETRA shape;
- reject malformed non-PETRA values;
- reject non-canonical root ranks;
- leave the immutable native source shape unchanged.

## B. Exact roundtrip

For every kernel shape in the exhaustive bounded corpus:

```text
decoded = decode_geometry(encode_geometry(vision_shape))
assert decoded == vision_shape
```

For every mirrored native PETRA shape:

```text
decoded_petra = restore(
    decode_geometry(
        encode_geometry(
            adapt(petra_shape)
        )
    )
)

assert decoded_petra == petra_shape
```

Identity of Python allocations is irrelevant. Kernel structural
equality governs the geometry core; native structural equality
governs the PETRA adapter boundary.

## C. Determinism

Independently allocated equal kernel shapes must produce equal
canonical geometry.

Repeated encoding of the same shape must produce byte-for-byte
equal canonical geometry records.

## D. Injectivity

For every pair of distinct kernel shapes in the bounded corpus:

```text
a != b
```

must imply:

```text
encode_geometry(a) != encode_geometry(b)
```

No bounded corpus collision is acceptable.

## E. Order preservation

For ordered groups with structurally distinct children, every
non-identity child permutation must produce different geometry.

Left-to-right bay order carries child order. Exchanging two distinct,
complete canonical bay regions therefore produces the canonical geometry of
a different valid `OrderedGroup`; it is not malformed merely because the
semantic order changed. Reordering the serialized cell tuple is not a
semantic bay permutation: it violates the `OrthogonalGeometry`
representation order and is handled at that representation boundary.

The decoder must reconstruct child order solely from bay order.

The PETRA restore adapter must derive canonical root ranks solely from
those decoded child positions.

## F. Recursive path and address correspondence

Two distinct, private test-only oracles support this evidence. The
tuple-index kernel oracle follows child tuples independently of production
path helpers. The geometry-path oracle instead traverses canonical occupied
cell tuples directly: it derives the bounding extent, full-height frame and
separator columns, ordered bays, and normalized child-cell regions. It does
not call `decode_geometry` (or any production geometry path helper). Neither
oracle is a required production VISION path API.

For every resolvable kernel child path:

- direct occupied-cell traversal must identify the same terminal, group, or
  child relation;
- geometric path indices must equal kernel child indices;
- traversal across a terminal cell must fail;
- an out-of-range bay index must fail.

For every bounded shape, the address evidence must compare:

- `[]` with `@/`, which resolves the native anchor for the complete shape;
- every non-empty path `p` with both `@/p` and `@/p/^`;
- the selected term rank with `p[-1]`;
- the slot owner with the term selected by `@/p`; and
- the slot target, adapted back to VISION, with the complete child shape at
  `p`.

In particular, `@/p` selects the native positional `Term` owning the final
child relation. `@/p/^` selects that relation's slot: its `owner` is the same
term and its `target` is `owner.exponent`. The adapted slot target, rather
than the `Term` itself, corresponds to the complete kernel child shape.

Failure evidence must preserve the native address contract:

- extending a root `Terminal` with index `0` corresponds to native
  `ADDRESS_OUT_OF_RANGE`;
- extending a path after a term whose exponent is `Leaf` corresponds to
  native `ADDRESS_CROSSES_LEAF`;
- selecting index `len(children)` from a group corresponds to native
  `ADDRESS_OUT_OF_RANGE`; and
- malformed address text remains covered by the native address contract and
  is not a geometry failure.

Native address resolution is a verification oracle. The geometry
encoder and decoder, and production adapter code, must not call it.

The committed direct-cell evidence uses an independently enumerated ordered
tree grammar with one terminal, non-empty ordered groups of width at most
three, root depth zero, maximum depth three, and at most seven structural-node
occurrences. It contains 110 shapes with exact node-count distribution
`1, 1, 2, 5, 12, 28, 61` for counts one through seven. Across that corpus it
records 110 root anchors, 574 non-root geometry paths, 574 term resolutions,
574 exponent-slot resolutions, and 1,258 positive resolutions. This is
evidence for the bounded implementation only. The final consolidated
validation and the results and limitations record are complete as documented
for the validated implementation and evidence head
`ee88cec361b673e4a7b9f17de9300344d5c87d06`. The complete dossier and exact
pull-request state at `e45f34859d5111317d8847248e55bca71c2b344a` received the
final independent read-only completion audit; that audit did not rerun the
consolidated implementation validation.

## G. Compositionality

Parent geometry must be computable from:

- canonical child geometries;
- bounded grammar constants;
- child order.

Re-encoding an unrelated part of the complete VISION kernel shape
must not be required to construct one parent frame.

## H. No hidden channel

The proof fails if decoding depends on:

- canonical PETRA serialization;
- integer projection;
- root labels;
- node IDs;
- metadata;
- element names;
- colour;
- rendering sequence;
- adapter-side state;
- an external manifest.

Tests must remove or randomise non-geometric representation details
where applicable.

## I. Dependency boundary

The Phase 1 dependency contract distinguishes exact direct production imports,
permitted eager facade initialization, test-only oracle imports, and build and
packaging dependencies.

- Direct production imports are exact: `kernel` has only permitted
  standard-library imports; `geometry` has exactly its permitted internal
  kernel edge; and `adapter` has exactly its permitted native model and kernel
  edges.
- VISION production modules contain no dynamic loading or `sys.modules`
  lookup used to bypass those direct edges. Geometry and adapter operations do
  not call addresses, serialization, rewrites, results, canonical-data
  helpers, numeric projection, external manifests, filesystem, environment,
  network, database, cache, or registry channels.
- The eager `petra.vision` facade exports the documented exact public API.
  Its eager loading is packaging behavior and does not weaken the direct
  module dependency contract.
- Addresses, canonical serialization, canonical-data helpers, and rewrite
  operators are test-only compatibility oracles where applicable; native
  imports and validation remain confined to the adapter.
- Setuptools, pytest, and similar tooling are build or test dependencies, not
  semantic decoder dependencies. Unrelated PETRA roadmap work does not gate
  the Phase 1 proof.

The dependency gate is complete. Committed evidence in
`tests/test_petra_vision_dependencies.py` records five passing
dependency-boundary tests over an independent bounded corpus of exactly 110
shapes. It proves the exact direct AST import graph for the kernel, geometry,
adapter, and VISION facade; the absence of `__import__`, importlib dynamic
loading calls, and `sys.modules` bypasses in kernel, geometry, and adapter;
and the exact ordered public exports of the eager `petra.vision` facade. The
evidence also documents eager parent-package loading in a fresh interpreter.

Across all 110 bounded shapes, the same evidence proves operational
independence while address, serialization, canonical-data, normalization, and
rewrite entry points are replaced with fail-fast sentinels. No production
implementation was changed for this validation.

## J. Malformed-geometry rejection

The malformed-geometry matrix defines and covers, at the
occupied-cell level, at least:

- a deleted outer-boundary cell or segment;
- a deleted separator cell;
- an add-only, full-height separator that produces a noncanonical
  partition;
- child payload cells transplanted into fixed incompatible bay extents
  without rebuilding the canonical parent geometry;
- a payload intrusion or bridge through required clearance across a
  separator;
- empty bay;
- two distinct disconnected child components in one bay;
- partial translation, non-uniform translation, or residual cells from the
  pre-translation record;
- a primitive outside the canonical frame;
- a solid non-terminal block;
- a 3x3 hollow object smaller than the minimum container frame;
- incorrect child top alignment;
- incorrect child width or horizontal alignment;
- noncanonical bottom clearance;
- a bay that is too narrow;
- a decoded structure exceeding Phase 1 structural bounds; and
- a cell-count, width, height, or coordinate resource-envelope violation.

A complete geometry translated by one uniform offset is valid and is
normalised before decoding; it is not a malformed translation case.

Drawing an identical child twice at the same coordinates adds no observable
geometry: canonical geometry is an occupied-cell set, so this cannot be a
malformed decoder case. Source-layer identity and overlapping identical
drawings are not represented.

Every decoder-reached malformed case must raise `GeometrySyntaxError`
containing `GEOMETRY_MALFORMED`, rather than produce best-effort
reconstruction. The listed malformed-geometry matrix has been implemented
and tested as completed hardening evidence.

At the representation boundary, malformed records retain their structural
`TypeError` or `ValueError` failures. A successfully constructed record that
reaches the decoder and is outside a Phase 1 structural or geometric resource
limit remains malformed and must follow the decoder failure contract above.

## K. Complexity measurements

Complexity evidence SHALL use schema identifier
`petra.vision.phase1.complexity.v1` at schema version `1`. Its JSON top level
SHALL contain exactly `schema`, `schema_version`, `environment`,
`methodology`, `corpus`, `summary`, and `shapes`.

`environment` SHALL contain exactly `python_implementation`, `python_version`,
`platform`, and `timer`. The Python version SHALL be the timestamp-free Python
release version. Evidence SHALL NOT contain timestamps, Python build dates,
repository paths, usernames, hostnames, Git branch or commit metadata, or
network-derived metadata.

`methodology` SHALL contain exactly `samples`, `iterations`, `warmup`,
`timing`, `limitations`, `shape_identifier_derivation`, and
`geometry_digest_derivation`. Timing is the median of per-batch integer
nanoseconds per operation: each raw batch duration is floor-divided by the
iteration count before the median is taken. Loop overhead is not subtracted.

`corpus` SHALL contain exactly `shape_count`, `maximum_width`,
`maximum_depth`, and `maximum_structural_node_occurrences`. `summary` SHALL
contain exactly `deterministic_maxima`,
`encoding_nanoseconds_per_operation`, and
`decoding_nanoseconds_per_operation`; each timing aggregate SHALL contain
integer `minimum`, `median`, and `maximum` values.

Each `shapes` record SHALL contain exactly the following fields and types:

- `index` (integer);
- `shape_id` (string);
- `structural_node_count`, `structural_depth`, and
  `maximum_ordered_group_width` (integers);
- `occupied_primitive_count`, `geometry_bounding_box_width`, and
  `geometry_bounding_box_height` (integers);
- `geometry_cells_digest` (string);
- `roundtrip_verified` (boolean);
- `encoding_median_nanoseconds_per_operation` and
  `decoding_median_nanoseconds_per_operation` (integers).

Both digest fields SHALL be lowercase, 64-character hexadecimal SHA-256
values. A shape identifier is SHA-256 over UTF-8 text using this canonical
tagged recursive encoding: `Terminal` is `T`; an ordered group with children
`child0` through `childn` is `G[encoding(child0),...,encoding(childn)]`. The
geometry digest is SHA-256 over the UTF-8 canonical compact JSON serialization
of the geometry cell record, using JSON separators `,` and `:`.

These measurements are diagnostic only. They impose no performance threshold
and make no performance-success, optimality, production-readiness, or
cross-machine-comparison claim.

## L. Phase 1 completion gate

Phase 1 is complete only when:

1. the exhaustive bounded kernel corpus is deterministic;
2. every kernel shape roundtrips exactly;
3. every mirrored native PETRA shape roundtrips through the adapter;
4. no pair of kernel shapes collides;
5. every required malformed geometry is rejected;
6. kernel path traversal is internally consistent;
7. PETRA address resolution agrees with the adapter projection;
8. the decoder uses geometry alone;
9. the dependency boundary is verified;
10. the consolidated canonical PETRA-only suite remains green;
11. results and limitations are recorded in the confidential dossier.
12. **Satisfied:** a final independent completion audit confirms the complete
    dossier and exact pull-request state as internally consistent and free of
    blocking findings.

All Phase 1 completion-gate items are satisfied. The final independent
read-only completion audit of the complete dossier and exact pull-request
state at `e45f34859d5111317d8847248e55bca71c2b344a` ended with
`READY TO RECORD PHASE 1 COMPLETION`. Phase 1 is formally complete for the
declared bounded static contract only: the 110 ordered-shape kernel domain,
maximum width 3, maximum depth 3, maximum structural-node count 7, the
declared canonical static geometry, the native PETRA adapter subset, and the
recorded malformed-input, dependency, correspondence, complexity, and
validation evidence. The independently validated implementation and evidence
revision remains `ee88cec361b673e4a7b9f17de9300344d5c87d06`; the later audit
did not rerun its consolidated 1,006-test implementation validation.

## Explicit non-claim

Passing Phase 1 proves feasibility of one minimal reversible
geometry.

It does not establish:

- novelty;
- inventive step;
- optimality;
- physical robustness;
- cryptographic security;
- final visual language;
- production readiness.

## Current hardening evidence and completion record

The prototype now has focused regression coverage for the enforced structural
and geometric resource boundaries, exact native adapter runtime types,
post-construction corruption, cycles, tuple-subclass snapshots, hostile deep
chains, sparse huge-span geometry, the complete 110-shape geometry record
digest, exact bounded roundtrips, the complete malformed-geometry matrix, and
exhaustive native-address correspondence across 110 anchors and 574 non-root
child paths.

The address evidence records 574 term resolutions, 574 exponent-slot
resolutions, 1,258 positive address resolutions in total, and the three
required failure-correspondence cases.

The complexity evidence is complete. It conforms to the normative Section K
schema `petra.vision.phase1.complexity.v1` at version `1`, over an independent
corpus with node-occurrence counts `1, 1, 2, 5, 12, 28, 61` and total size
`110`. The deterministic maxima recorded are 7 nodes, depth 3, ordered-group
width 3, 181 occupied cells, and geometry dimensions 25 by 13. The diagnostic
timing run records 7 samples with 100 iterations per batch. Its values remain
diagnostic only. The committed complexity contract evidence records nine
passing tests; no production implementation was modified for this validation.

The dedicated independent evidence-oracle suite passed with 7 passed. After
the oracle repair, the focused PETRA VISION suite passed with 566 passed. The
final consolidated canonical PETRA-only validation covered 12
`tests/test_petra_*.py` files and passed with 1,006 passed, zero failures, in
3.48 seconds. Push and pull-request CI both passed on the validated
implementation and evidence head `ee88cec361b673e4a7b9f17de9300344d5c87d06`;
the repository remained unchanged after the PETRA-only validation.

This is a completion declaration for the declared bounded static contract
only. The final independent read-only audit of the complete dossier and exact
pull-request state at `e45f34859d5111317d8847248e55bca71c2b344a` ended with
`READY TO RECORD PHASE 1 COMPLETION`, with no blocking findings and no bounded
Phase 1 production defect. It confirmed consistency among implementation,
tests, generated evidence, dossier, revision attribution, and exact remote
PR/CI state; it independently recomputed the 110-shape corpus, deterministic
records, digests, injectivity, and roundtrips, and confirmed the stated
boundary segregation. The 1,006-test consolidated validation remains
attributed solely to `ee88cec361b673e4a7b9f17de9300344d5c87d06` and was not
rerun on the later documentation revision. Native PETRA kernel hardening and
the repository-wide PET-to-PETRA migration remain outside this Phase 1 adapter
boundary; the incomplete historical migration is a separate workstream, not a
Phase 1 requirement or regression.
