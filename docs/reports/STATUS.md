# PETRA Status

## Current architecture

**PETRA — Prime Exponent Tower Recursive Algebra** is the sole current project
architecture and maintained runtime surface.

Status: **Phase 10 complete — PETRA v2.0.0 shipped**.

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
- Phase 10 completed: the historical PET runtime was removed
  (`af08caf`), PETRA is the sole maintained distribution and CLI
  surface, and v2.0.0 was released (`6e642cb`);
- numeric projection, primality, and factorization remain outside the initial
  core;
- permanent PET compatibility is not a requirement;
- the former PET runtime remains historically recoverable through Git and tag
  `v0.3.0`.

## Current work

Phase 10 is complete. The active front is research, tracked in
[`../research/notes/open-problems.md`](../research/notes/open-problems.md).
The T-series of research threads is archived in
[`../research/notes/open-threads.md`](../research/notes/open-threads.md).

The maintained surfaces are `src/petra/` (canonical runtime) and
`resolver/` (research satellite). The resolver passes ruff and mypy
clean; the test suite passes 718/718.

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

The former `src/pet/` runtime and the historical PET test/tool surface
were removed during Phase 10 (`af08caf`). They are preserved by
repository history (tag `v0.3.0`) rather than in the working tree.

PETRA does not depend on any historical PET surface.

## Research boundary

Research under `docs/research/` and related research tooling remains
non-canonical unless explicitly promoted through a separate decision
and canonical implementation change.

The active research front is tracked in
[`../research/notes/open-problems.md`](../research/notes/open-problems.md).

## Source of truth

The sole normative source is:

- [`../reference/SPEC.md`](../reference/SPEC.md)

Work ordering is recorded in:

- [`../../ROADMAP.md`](../../ROADMAP.md)

The Phase 9 → Phase 10 readiness evidence is recorded in:

- [`petra-phase-9-to-10-audit.md`](petra-phase-9-to-10-audit.md)
