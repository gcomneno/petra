# PETRA VISION confidential research dossier

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

Created: 2026-08-02<br>
PETRA integration reference: `594fb8dcc2b42643e89cd229523f67e1fef2d599`

## Purpose

This directory records the confidential technical foundation,
implementation, and evidence for PETRA VISION.

PETRA VISION investigates a deterministic and reversible mapping
between a minimal recursive structural kernel and canonical visual
geometry. Native PETRA shapes enter and leave that kernel through a
narrow, explicit adapter.

The intended principle is:

> The geometry is the structural message itself.

The geometry must not merely contain, decorate, label, serialize,
or visually accompany a separate PETRA representation.

## Architecture boundary

Phase 1 defines the geometry core over this minimal mathematical
domain:

```text
VisionShape ::= Terminal
              | OrderedGroup(
                    VisionShape[0],
                    ...,
                    VisionShape[n-1]
                )

n >= 1
```

This kernel is a semantic contract, not a second public PETRA runtime
model.

The implemented canonical layout applies to this bounded proof grammar only.
Generalized or final layout rules for domains beyond those bounds remain later
research work.

Native PETRA integration follows two explicit boundaries:

```text
PetraShape -> VisionShape -> Geometry
Geometry -> VisionShape -> PetraShape
```

Only the PETRA adapter knows about `Leaf`, `Container`, `Term`, and
`Root`. The geometry core knows only terminal values and recursively
ordered children.

Canonical PETRA serialization, structural addresses, and rewrite
operators may be used as test oracles. They must not become geometry
inputs, metadata channels, or implementation dependencies.

Phase 1 therefore does not wait for completion of the overall PETRA
roadmap or for unrelated PETRA utilities that are not used by the
adapter.

### Dependency layers

The Phase 1 boundary distinguishes four layers:

1. Production module implementation imports: `kernel` uses only the Python
   standard library; `geometry` directly imports only the kernel plus the
   standard library; and `adapter` directly imports only the native model plus
   the kernel.
2. Package-facade initialization and re-exports: `petra.vision` is an
   intentionally eager public facade in Phase 1. Under normal Python import
   semantics, importing a VISION submodule still initializes its parent
   packages and can therefore cause eager transitive loading.
3. Test-only compatibility oracles: addresses, serialization,
   canonical-data helpers, and rewrite operators remain test-only oracles
   where applicable, rather than inputs or callable dependencies of geometry
   or adapter operations.
4. Packaging and build dependencies: setuptools, pytest, and similar tooling
   are build or test concerns, not semantic decoder dependencies.

Eager facade loading is not a direct implementation dependency of the
geometry algorithm and does not authorize geometry or adapter code to call
unrelated native facilities.

### Dependency-boundary evidence

The dependency-boundary gate is complete. The committed
`tests/test_petra_vision_dependencies.py` evidence has five passing tests over
an independent bounded corpus of exactly 110 shapes. It proves the exact
direct AST import graph of kernel, geometry, adapter, and the VISION facade;
the absence of `__import__`, importlib dynamic-loading calls, and `sys.modules`
bypasses in kernel, geometry, and adapter; and the exact ordered public
exports of the eager `petra.vision` facade. It also documents eager
parent-package loading in a fresh interpreter.

With address, serialization, canonical-data, normalization, and rewrite entry
points replaced by fail-fast sentinels, the evidence proves operational
independence across all 110 bounded shapes. No production implementation was
changed for this validation.

## Document map

- `INVENTION_DISCLOSURE.md`
  records the technical problem, proposed solution, embodiments,
  and candidate inventive boundaries.
- `TECHNICAL_CONTRACT.md`
  defines the shape-to-geometry and geometry-to-shape contracts.
- `PHASE_1_SHAPE_DOMAIN.md`
  defines the bounded VISION kernel and native PETRA adapter boundary.
- `PHASE_1_GEOMETRIC_GRAMMAR.md`
  defines the minimal nested-frame proof geometry.
- `PHASE_1_ACCEPTANCE_CRITERIA.md`
  defines the executable proof obligations and completion gate.
- `PHASE_1_COMPLEXITY_DATA.json`
  records the deterministic, schema-governed Phase 1 complexity evidence.
- `PHASE_1_COMPLEXITY_RESULTS.md`
  records the readable Phase 1 complexity evidence results and limitations.
- `PUBLIC_DISCLOSURE_BOUNDARY.md`
  separates previously public work from the new confidential work.
- `EXPERIMENT_PLAN.md`
  defines the staged proof and implementation programme.
- `CONFIDENTIALITY_RULES.md`
  defines operational rules for preserving confidentiality.

## Research status

Current phase: Phase 1 kernel, adapter, and minimal geometric
grammar specification. Complexity evidence is complete: the committed JSON
and Markdown artifacts record schema `petra.vision.phase1.complexity.v1`,
version `1`, for an independent 110-shape corpus, with nine passing complexity
contract tests. Timing values are diagnostic only, and no production
implementation was modified for this validation. Phase 1 remains incomplete
pending final independent completion review of the combined exhaustive
evidence, final consolidated PETRA-suite evidence in the review environment,
and the final results and limitations record.

No production implementation, public specification, public issue,
public presentation, or public benchmark is authorised from this
directory.

## Core research question

Can every supported native PETRA shape be adapted into a minimal
ordered recursive domain and embedded into deterministic canonical
geometry such that the original PETRA shape can be recovered exactly,
while preserving recursive structure, positional identity, and
compositional meaning?
