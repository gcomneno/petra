# PETRA VISION technical contract

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## 1. Domains

Let:

- `P` be the set of supported canonical native PETRA shapes;
- `V` be the set of bounded canonical VISION kernel shapes;
- `C` be the set of canonical PETRA VISION geometries;
- `R` be the set of later rendered or physical observations.

The foundational functions are:

- `adapt: P -> V`
- `restore: V -> P`
- `encode_geometry: V -> C`
- `decode_geometry: C -> V`

A later observation pipeline may introduce:

- `render: C -> R`
- `normalise: R -> C`

## 2. Exact roundtrip

For every supported `v` in `V`:

`decode_geometry(encode_geometry(v)) == v`

Equality is VISION kernel structural equality.

For every supported `p` in `P`:

`restore(decode_geometry(encode_geometry(adapt(p)))) == p`

Equality is native PETRA structural equality, not merely equality of a
serialized integer or textual representation.

## 3. Determinism

For equal canonical VISION kernel shapes, `encode_geometry` must produce the
same canonical geometric model.

Rendering differences caused by display resolution must not change
canonical geometric identity.

## 4. Injectivity

Distinct supported VISION kernel shapes must not map to the same canonical
geometry. Native PETRA compatibility is supplied through `adapt` and
`restore`.

Formally:

`for all a, b in V: encode_geometry(a) == encode_geometry(b) => a == b`

## 5. Recursive correspondence

A recursive VISION kernel subshape must correspond to an identifiable
recursive geometric region or construction. The adapter establishes the
correspondence between supported native PETRA subshapes and VISION kernel
subshapes.

Decoding must not depend on a hidden serialized copy of the complete VISION
kernel shape or native PETRA shape.

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
