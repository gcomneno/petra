# PETRA — Prime Exponent Tower Recursive Algebra

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22741778.svg)](https://doi.org/10.5281/zenodo.22741778)

PETRA is a recursive, canonical, shape-first algebra for prime-exponent tower
structures.

The project replaces the former **PET — Prime Exponent Tree** runtime. PETRA is
not a compatibility layer above PET and does not preserve historical PET
behavior merely for continuity.

## Current status

PETRA is now the maintained runtime, distribution, and command-line surface.

- The canonical PETRA architecture is defined by the specification.
- The immutable PETRA runtime is implemented under `src/petra/`.
- Canonical positional addresses, result/witness records, serialization, and
  the `SPROUT`, `SHED`, `GRAFT`, and `PRUNE` operators are implemented.
- The minimal maintained CLI is `petra`.
- Phase 8 — minimal CLI — is complete.
- The Phase 9 readiness audit concluded `PHASE_10_READY`.
- Phase 10 — complete replacement — is active.
- `src/pet/` remains temporarily in the repository as historical migration
  residue, but it is not part of the maintained PETRA distribution surface.
- Tag `v0.3.0` preserves the final historical PET release.

Do not treat the historical `pet` CLI, PET-Base JSON, `PETObject`, PET-Metrics,
PET-METICA, numeric projection, or legacy operators as PETRA behavior.

## Canonical sources

1. [PETRA specification](docs/reference/SPEC.md)
2. [PETRA vision](docs/VISION.md)
3. [PETRA implementation roadmap](ROADMAP.md)
4. [Documentation map](docs/README.md)
5. [Current project status](docs/reports/STATUS.md)
6. [Maintained PETRA CLI reference](docs/reference/CLI.md)

The specification is the sole normative source. Other documents are
explanatory, historical, planning, or research material.

## Core grammar

```text
PETRA     ::= Leaf | Container
Leaf      ::= 1
Container ::= Product(Term+)
Term      ::= Root ^ PETRA
```

PETRA uses canonical positional root ranks, state-scoped structural addresses,
and direct structural rewrites.

The canonical operators are:

- `SPROUT`;
- `SHED`;
- `GRAFT`;
- `PRUNE`.

## Maintained CLI

A maintained installation exposes the `petra` command:

```bash
petra '1' '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}'
```

The CLI accepts one canonical PETRA shape and one strict invocation JSON
document, then emits one canonical operator-result JSON document. See
[`docs/reference/CLI.md`](docs/reference/CLI.md) for the exact current boundary.

The historical `pet` command is not a maintained PETRA interface.

## Role of primes

Concrete primes are not runtime identities.

The word **Prime** describes the mathematical interpretation of recursive
exponent towers. Numeric projection, primality testing, prime generation, and
factorization are outside the initial structural core.

## Replacement policy

PETRA reuses only artifacts required by a concrete PETRA contract.

Historical PET behavior remains recoverable through Git history, tags, and
releases. Obsolete APIs, commands, formats, tests, tools, and readers are
removed or retargeted during Phase 10 rather than retained as permanent
compatibility layers.

The replacement program is tracked by
[issue #169](https://github.com/gcomneno/petra/issues/169). The current Phase 10
distribution-boundary slice is tracked by
[issue #226](https://github.com/gcomneno/petra/issues/226).

## Versioning

PETRA uses semantic versioning with an explicit discontinuity:

- `v0.1.0` ... `v0.3.0` are historical **PET** releases. They are preserved
  as Git tags for archaeological reference and are not part of the PETRA
  contract.
- `v1.0.0` is the first **PETRA** release. The version line restarts at
  `1.0.0` by design: PETRA is not a compatible successor of PET, so inheriting
  the PET version number would be misleading.
- The `petra` distribution tracks the PETRA line only. Releases with
  version `< 1.0.0` belong to the historical PET packaging and should not be
  installed for PETRA use.

Stability commitment: within the `1.x` line, the canonical serialization,
operator semantics, and CLI contract defined in
[`docs/reference/SPEC.md`](docs/reference/SPEC.md) are frozen. Additions are
allowed; breaking changes require a `2.0.0` bump.
