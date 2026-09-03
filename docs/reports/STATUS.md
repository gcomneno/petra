# PETRA Status

## Current architecture

**PETRA — Prime Exponent Tower Recursive Algebra** is the sole current project
architecture and maintained runtime surface.

Status: **Phase 10 — complete replacement in progress**.

## Completed

- the PETRA name and expansion are approved;
- the project is shape-first rather than value-first;
- immutable PETRA shapes, normalization, equality, and positional addresses are
  implemented under `src/petra/`;
- typed operator results and witnesses are implemented;
- `SPROUT`, `SHED`, `GRAFT`, and `PRUNE` are the canonical operators;
- canonical shape, invocation, and result serialization are implemented;
- Phase 8 delivered the minimal canonical `petra` CLI;
- the Phase 9 transition audit concluded `PHASE_10_READY`;
- numeric projection, primality, and factorization remain outside the initial
  core;
- permanent PET compatibility is not a requirement;
- the former PET runtime remains historically recoverable through Git and tag
  `v0.3.0`.

## Current work

Phase 10 is replacing the remaining mixed PET/PETRA repository surfaces.

The active distribution-boundary slice makes PETRA the sole maintained package
and CLI identity while leaving `src/pet/` temporarily present as migration
residue. Subsequent Phase 10 slices may remove or retarget obsolete PET tests,
tools, documentation, and source files.

## Maintained runtime

The maintained PETRA surface includes:

- `src/petra/`;
- canonical PETRA shapes and addresses;
- typed result/witness records;
- direct structural operators;
- canonical serialization;
- the `petra` console command.

The maintained runtime does not depend on `src/pet/`.

## Historical runtime

The current checkout still contains the former `src/pet/` runtime and a large
historical PET test/tool surface.

That code is migration residue during Phase 10. Its presence does not make it a
maintained product surface and does not create a PETRA requirement. Historical
behavior is preserved by repository history rather than permanent
compatibility.

## Research boundary

Research under `docs/research/` and related research tooling remains
non-canonical unless explicitly promoted through a separate decision and
canonical implementation change. Sparse-image and PETRA VISION research are
not part of this Phase 10 distribution-boundary slice.

## Source of truth

The sole normative source is:

- [`../reference/SPEC.md`](../reference/SPEC.md)

Work ordering is recorded in:

- [`../../ROADMAP.md`](../../ROADMAP.md)

The Phase 9 → Phase 10 readiness evidence is recorded in:

- [`petra-phase-9-to-10-audit.md`](petra-phase-9-to-10-audit.md)
