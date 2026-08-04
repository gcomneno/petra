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

The decoder must reconstruct child order solely from bay order.

The PETRA restore adapter must derive canonical root ranks solely from
those decoded child positions.

## F. Recursive path and address correspondence

For every resolvable kernel child path:

- geometric traversal must identify the same terminal, group, or
  child relation;
- geometric path indices must equal kernel child indices;
- traversal across a terminal cell must fail;
- an out-of-range bay index must fail.

For every mirrored native PETRA address:

- adapter-projected path indices must equal PETRA address indices;
- the native resolver and geometric traversal must identify
  corresponding anchors, terms, and exponent-slot relations.

Native address resolution is a verification oracle. The geometry
encoder and decoder must not call it.

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

The Phase 1 architecture must demonstrate that:

- the geometry core depends only on the VISION kernel contract;
- native PETRA imports and validation remain confined to the adapter;
- canonical serialization is only a fixture or comparison oracle;
- native address resolution is only a compatibility oracle;
- PETRA rewrite operators are not called by geometry code;
- unrelated PETRA roadmap work does not gate the Phase 1 proof.

## J. Malformed-geometry rejection

Adversarial tests must cover at least:

- deleted outer boundary segment;
- deleted separator;
- extra separator;
- reordered bays;
- overlapping bays;
- empty bay;
- duplicate child in one bay;
- child crossing a separator;
- non-canonical translation residue;
- primitive outside the frame;
- solid frame confused with a leaf;
- hollow unit object confused with a container.

Every malformed case must produce a stable explicit failure rather
than best-effort reconstruction.

Within the Phase 1 resource envelope, malformed values retain their
structural `TypeError` or `ValueError` failures. If a value is both malformed
and outside a Phase 1 width, depth, or node limit, `ValueError` containing
`VISION_SHAPE_OUT_OF_BOUNDS` may take precedence to bound validation work;
that precedence does not make the value valid or decodable.

## K. Complexity measurements

For every corpus shape, record:

- node count;
- depth;
- maximum width;
- primitive count;
- bounding-box width;
- bounding-box height;
- encoding time;
- decoding time.

These measurements are diagnostic and do not yet impose performance
success thresholds.

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
10. all existing PETRA tests remain green;
11. results and limitations are recorded in the confidential dossier.

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

## Current hardening evidence and remaining gate work

The prototype now has focused regression coverage for the enforced structural
and geometric resource boundaries, exact native adapter runtime types,
post-construction corruption, cycles, tuple-subclass snapshots, hostile deep
chains, sparse huge-span geometry, the complete 110-shape geometry record
digest, and exact bounded roundtrips.

This is not a completion declaration. The remaining acceptance-gate evidence
still to be completed and recorded includes an independently reviewed
exhaustive corpus run, the full malformed-geometry matrix in section J,
native-address correspondence evidence, dependency-boundary review, all
PETRA-suite evidence in the review environment, and the required results and
limitations record. Native PETRA kernel hardening remains outside this Phase 1
adapter boundary.
