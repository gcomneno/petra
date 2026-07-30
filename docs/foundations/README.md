# PET/PEG Foundations

This directory contains foundational PET/PEG 2.0 research notes and one
normative future operator contract.

These documents are conceptual and research-oriented. They do not define stable
PET-Base behavior and do not change CLI defaults, routing, anchor selection, or
residual-descent semantics.

`pet-peg-2.0-object-native-operators.md` is the exception in scope: it is the
normative contract for future object-native `SPROUT`, `SHED`, `GRAFT`, and
`PRUNE` implementation. It still does not change current stable CLI behavior.

## Reading order

1. `pet-peg-2.0-object-native-operators.md` — normative object-native
    operator, positional-address, serialization, and migration contract
2. `pet-first-principles.md` — original PET seed idea and research boundary
3. `pet-first-principles-examples.md` — worked examples for the PET seed idea
4. `pet-notation-collapse.md` — canonical PET notation and numeric collapse semantics
5. `pet-first-principles-implementation-audit.md` — current implementation audit against the first-principles model
6. `pet-module-stability-classification.md` — stability classification for tracked `src/pet` modules
7. `pet-metrics-first-principles-audit.md` — audit of extended metrics against first-principles height/support semantics
8. `pet-first-principles-api-aliases.md` — design boundary for explicit first-principles API aliases
9. `pet-core-v0.md` — preliminary PET/PEG core ontology
10. `operator-algebra.md` — support-preserving and support-expanding operators
11. `projection-semantics.md` — projection and interpretation semantics
12. `path-history.md` — transformational memory and path-dependent identity
13. `operator-addresses.md` — recursive operator selectors and their PEG role
14. `operator-semantics-snapshot.md` — current research-only executable X/Y/Z operator semantics
15. `pet-peg-2.0-baseline.md` — closed executable PET/PEG 2.0 operator semantics baseline
16. `pet-2-roadmap.md` — PET 2.0 research roadmap

## Scope

The foundations layer separates:

- PET object structure
- PEG connectivity dynamics
- path-history
- projection semantics
- support-preserving operators
- support-expanding operators
- recursive operator addresses
- executable research-only operator semantics snapshots
- closed PET/PEG 2.0 executable operator semantics baseline

This material is intended to make ongoing PET/PEG dynamics research more precise
and less ad hoc.

For stable behavior, read `../reference/SPEC.md`.
For CLI behavior, read `../reference/CLI.md`.
For live research notes, read `../research/README.md`.
- `pet-peg-2.0-core-pillars.md` — PET/PEG 2.0 core pillars and boundary
- `pet-peg-2.0-root-base-recursion.md` — PET/PEG 2.0 exact and partial root-base recursion semantics
- `pet-peg-2.0-structural-addresses.md` — PET/PEG 2.0 structural address, identity, and address-outcome semantics
- `pet-peg-2.0-operator-semantics.md` — PET/PEG 2.0 NEW/DROP/INC/DEC target and value-level application semantics
- `pet-peg-2.0-graph-path-traversal.md` — PET/PEG 2.0 graph nodes, edges, paths, bounded traversal, and truncation semantics
- `pet-peg-2.0-traces-certificates.md` — PET/PEG 2.0 trace format, replay certificates, and exploration-policy boundary
- `pet-peg-2.0-object-legacy-bridge.md` — PET/PEG 2.0 migration bridge between recursive objects and legacy PET trees
- `pet-peg-2.0-object-native-metrics.md` — PET/PEG 2.0 metrics computed directly from recursive PET objects
