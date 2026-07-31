# PETRA — Prime Exponent Tower Recursive Algebra

PETRA is a recursive, canonical, shape-first algebra for prime-exponent tower
structures.

The project is replacing the former **PET — Prime Exponent Tree** runtime.
PETRA is not a compatibility layer above PET-Base and does not maintain a
parallel legacy model.

## Current status

The repository is in a documentation-first replacement phase.

- The canonical PETRA architecture is defined.
- The immutable PETRA runtime has not been implemented yet.
- Existing code under `src/pet/` belongs to the historical PET baseline.
- Tag `v0.3.0` preserves the final historical PET release.
- New implementation work will be created under `src/petra/`.

Do not treat the current `pet` CLI, PET-Base JSON, `PETObject`, PET-Metrics,
PET-METICA, or legacy operators as PETRA behavior.

## Canonical sources

1. [PETRA specification](docs/reference/SPEC.md)
2. [PETRA vision](docs/VISION.md)
3. [PETRA implementation roadmap](ROADMAP.md)
4. [Documentation map](docs/README.md)
5. [Current project status](docs/reports/STATUS.md)

The specification is the sole normative source. Other documents are explanatory,
historical, or research material.

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

## Role of primes

Concrete primes are not runtime identities.

The word **Prime** describes the mathematical interpretation of recursive
exponent towers. Numeric projection, primality testing, prime generation, and
factorization are outside the initial structural core.

## Replacement policy

PETRA reuses only artifacts required by a concrete PETRA contract.

The former PET implementation remains available through Git history, tags, and
releases. Obsolete APIs, commands, formats, tests, tools, and readers will be
removed from the active runtime rather than retained as permanent compatibility
layers.

## Development

The current documentation-only milestone is tracked by
[issue #170](https://github.com/gcomneno/pet/issues/170), under the replacement
program in
[issue #169](https://github.com/gcomneno/pet/issues/169).

Runtime implementation begins only after the canonical specification is
accepted.
