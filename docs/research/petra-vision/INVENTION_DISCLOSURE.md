# Invention disclosure

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

Created: 2026-08-02<br>
PETRA base revision: `87ba931865e0744534dec7a9971e1dd0822ac68c`

## Working title

**PETRA VISION: deterministic recursive geometry for faithful
visual embedding of native PETRA shapes**

## Technical field

The work concerns deterministic structural representations,
recursive geometries, machine-readable visual structures,
reversible encodings, visual verification, and multiscale
structural inspection.

## Technical problem

Conventional visual codes generally start from an independent
serialized payload and subsequently encode that payload into
graphical marks.

Conventional tree diagrams instead visualise a structure for human
inspection but normally do not define a canonical, lossless, and
directly invertible geometric representation.

The technical problem is to construct a visual geometry in which
the spatial structure itself corresponds faithfully to the native
recursive structure of a PETRA shape.

## Proposed solution

Define a deterministic mapping:

`G: Shape -> Geometry`

together with an inverse:

`D: Geometry -> Shape`

such that, for every supported canonical PETRA shape `s`:

`D(G(s)) = s`

The geometric construction must be recursive and compositional:
each structural component of a PETRA shape corresponds to a
geometric component whose containment, adjacency, orientation, or
position preserves the relevant PETRA relation.

## Essential technical concept

The proposed geometry is not a container for a separately encoded
payload.

The geometry is itself the canonical embodiment of the recursive
shape.

A conforming implementation therefore requires more than drawing a
tree or storing bytes in an image. It requires a faithful structural
correspondence between:

- PETRA node identity;
- canonical child order;
- recursive containment;
- positional addresses;
- structural depth;
- structural width;
- repeated subshape identity;
- the resulting spatial construction.

## Candidate technical effects

Subject to experimental proof, candidate technical effects include:

- exact machine reconstruction of a PETRA shape from geometry;
- deterministic visual identity for structurally equal shapes;
- direct visual comparison of structural differences;
- localised geometric change after localised shape mutation;
- multiscale inspection of nested structural levels;
- visual integrity checks derived from structural invariants;
- partial or authenticated completion of an intentionally
  incomplete geometry;
- geometry-derived indexing, recognition, or verification.

## Candidate embodiments

1. A software renderer and decoder operating on vector geometry.
2. A rasterised representation with canonical normalisation before
   decoding.
3. A physical printed or engraved representation.
4. A multiscale viewer exposing successively deeper recursive
   structure.
5. A distributed or split representation in which an authenticated
   contribution completes a missing structural region.
6. A verification system comparing decoded geometry with expected
   PETRA invariants.

## Candidate claim families for professional review

These are research categories, not legal claims.

1. A deterministic method for generating canonical recursive
   geometry from a native PETRA shape.
2. A reverse method for reconstructing the native shape from the
   canonical geometry.
3. A compositional geometric grammar preserving recursive and
   positional relations.
4. A multiscale representation exposing structurally meaningful
   levels at different inspection scales.
5. A method for detecting structural corruption through geometric
   invariant violations.
6. An authenticated completion protocol for an intentionally
   incomplete geometric structure.
7. A system combining generation, capture, normalisation, decoding,
   and structural verification.

## Matters not yet established

- The optimal geometric primitive set.
- The generalized or final canonical layout algorithm beyond the bounded
  Phase 1 proof grammar.
- Robustness under rotation, scaling, rasterisation, noise, and
  partial occlusion.
- Whether canonical geometry should be unique absolutely or unique
  only after normalisation.
- Which features produce a demonstrable technical effect beyond
  abstract mathematical representation.
- Which elements are novel over existing graph drawing, fractal
  coding, visual cryptography, fiducial markers, and machine-readable
  symbol systems.
