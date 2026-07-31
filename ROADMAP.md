# PETRA Implementation Roadmap

## Authority

This roadmap orders implementation work after the canonical
[PETRA specification](docs/reference/SPEC.md).

It does not preserve the former PET architecture as a permanent lower layer.

## Current phase — canonical specification

Complete the documentation-only architecture transition:

- establish PETRA as the sole current architecture;
- define the shape-first grammar and conformance rules;
- classify former PET material as historical or research-only;
- remove compatibility-first requirements from the active roadmap;
- keep production code unchanged until the specification is accepted.

## Phase 1 — immutable shape model

Implement:

- `Leaf`;
- `Container`;
- `Term`;
- exponent relations;
- canonical local root ranks;
- grammar invariants;
- immutable structural equality.

No addresses, operators, projections, CLI, or legacy bridges.

## Phase 2 — normalization and equality

Implement:

- recursive canonical validation;
- rank assignment from visible order;
- canonical normalization;
- explicit rejection of malformed or non-canonical input;
- fixture-oriented shape rendering needed by tests.

No numeric interpretation.

## Phase 3 — positional addresses

Implement:

- root anchor `@/`;
- positional term traversal;
- typed projections;
- exponent-relation slot `^`;
- deterministic generic failures;
- address-effect comparison helpers.

## Phase 4 — atomic rewrite model

Implement:

- immutable invocation values;
- success and failure result types;
- exact before-shape preservation;
- after-shape validation;
- resolved targets;
- exactly one success witness;
- deterministic reason precedence;
- no-op prevention.

## Phase 5 — width operators

Implement:

- `SPROUT`;
- `SHED`;
- default and explicit targeting;
- canonical leaf restoration;
- rank retargeting;
- witness-based partial inverse behavior.

## Phase 6 — depth operators

Implement:

- `GRAFT`;
- `PRUNE`;
- latent relation slots;
- singleton terminality;
- deterministic depth and tie rules;
- witness-based partial inverse behavior.

## Phase 7 — serialization

Define and implement canonical PETRA serialization for:

- shapes;
- addresses;
- invocations;
- results;
- witnesses;
- stable failure identifiers.

Historical PET JSON compatibility is not a requirement.

## Phase 8 — minimal CLI

Build a new `petra` command exposing only stable PETRA operations.

Do not mechanically rename the historical `pet` CLI.

## Phase 9 — optional derived layers

Open separate work only when concrete requirements justify:

- graphs and neighborhood traversal;
- paths;
- traces and certificates;
- PETRA-native metrics;
- prime-tower projection;
- research probes.

No historical layer is promoted automatically.

## Phase 10 — complete replacement

- remove `src/pet/`;
- remove obsolete runtime tests and tools;
- remove old package exports and commands;
- rename the distribution and CLI to `petra`;
- update CI and documentation checks;
- rename the repository when the new runtime is ready;
- publish a distinct PETRA release line.

## Guiding rule

Build from the PETRA specification. Reuse previous artifacts only after a
current requirement proves they belong.
