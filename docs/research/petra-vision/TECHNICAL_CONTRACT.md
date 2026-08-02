# PETRA VISION technical contract

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## 1. Domains

Let:

- `S` be the set of supported canonical PETRA shapes;
- `C` be the set of canonical PETRA VISION geometries;
- `R` be the set of rendered physical or raster observations.

The foundational functions are:

- `encode_geometry: S -> C`
- `decode_geometry: C -> S`

A later observation pipeline may introduce:

- `render: C -> R`
- `normalise: R -> C`

## 2. Exact roundtrip

For every supported shape `s`:

`decode_geometry(encode_geometry(s)) == s`

Equality is native PETRA structural equality, not merely equality of
a serialized integer or textual representation.

## 3. Determinism

For equal canonical input shapes, `encode_geometry` must produce the
same canonical geometric model.

Rendering differences caused by display resolution must not change
canonical geometric identity.

## 4. Injectivity

Distinct supported PETRA shapes must not map to the same canonical
geometry.

Formally:

`encode_geometry(a) == encode_geometry(b) => a == b`

## 5. Recursive correspondence

A recursive PETRA subshape must correspond to an identifiable
recursive geometric region or construction.

Decoding must not depend on a hidden serialized copy of the complete
PETRA shape.

## 6. Positional preservation

Canonical PETRA positional addresses must be recoverable from
geometric relations.

Child order must be encoded by the geometric grammar rather than by
external labels alone.

## 7. Compositionality

There must exist a composition operation through which the geometry
of a parent shape can be constructed from canonical geometries of
its children plus bounded parent-level structure.

## 8. Local stability

A local structural mutation should produce a geometrically local or
otherwise bounded change whenever compatible with canonicality.

This is a desired property and must be measured rather than assumed.

## 9. Multiscale semantics

Coarser observations may expose higher-level structure while finer
observations expose deeper recursive detail.

Every recognised level must correspond to an explicit PETRA
structural boundary.

Physical resolution alone must not be treated as a security
mechanism.

## 10. Canonical normalisation

Permitted transformations such as translation, scale, and rotation
must be explicitly defined.

Two observations are geometrically equivalent only after application
of the authorised normalisation rules.

## 11. Failure behaviour

Decoding must reject:

- ambiguous geometries;
- geometries violating canonical order;
- malformed recursive regions;
- impossible positional relationships;
- incomplete geometry unless an explicit partial-decoding protocol
  is active.

Silent best-effort reconstruction is forbidden in the canonical
decoder.

## 12. Separation from cryptography

PETRA VISION geometry may participate in cryptographic protocols,
but must not invent proprietary cryptographic primitives.

Authentication, secret sharing, signatures, encryption, and
threshold reconstruction must rely on established cryptographic
constructions through a separate boundary.
