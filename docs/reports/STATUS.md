# PETRA Status

## Current architecture

**PETRA — Prime Exponent Tower Recursive Algebra** is the sole current project
architecture.

Status: **canonical specification transition in progress**.

## Completed

- the PETRA name and expansion are approved;
- the project is shape-first rather than value-first;
- `SPROUT`, `SHED`, `GRAFT`, and `PRUNE` are the canonical operators;
- numeric projection, primality, and factorization are outside the initial core;
- permanent PET compatibility is not a requirement;
- the former PET runtime is preserved historically through Git and tag `v0.3.0`.

## Current work

The active milestone establishes:

- one canonical PETRA specification;
- one vision;
- one implementation roadmap;
- clear historical classification of prior PET material.

This milestone is documentation-only.

## Not yet implemented

- `src/petra`;
- immutable PETRA shapes;
- canonical normalization and equality;
- positional address resolution;
- direct structural rewrite results;
- PETRA operators;
- PETRA serialization;
- the `petra` CLI.

## Historical runtime

The current checkout still contains the former `src/pet` runtime and its tests.

That code remains executable during the transition but does not define PETRA.
It will be removed after the replacement implementation is complete.

## Source of truth

The sole normative source is:

- [`../reference/SPEC.md`](../reference/SPEC.md)
