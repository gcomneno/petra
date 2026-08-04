# PETRA VISION confidential research dossier

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

Created: 2026-08-02<br>
PETRA integration reference: `594fb8dcc2b42643e89cd229523f67e1fef2d599`

## Purpose

This directory records the confidential technical foundation of
PETRA VISION before implementation work begins.

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
- `PUBLIC_DISCLOSURE_BOUNDARY.md`
  separates previously public work from the new confidential work.
- `EXPERIMENT_PLAN.md`
  defines the staged proof and implementation programme.
- `CONFIDENTIALITY_RULES.md`
  defines operational rules for preserving confidentiality.

## Research status

Current phase: Phase 1 kernel, adapter, and minimal geometric
grammar specification.

No production implementation, public specification, public issue,
public presentation, or public benchmark is authorised from this
directory.

## Core research question

Can every supported native PETRA shape be adapted into a minimal
ordered recursive domain and embedded into deterministic canonical
geometry such that the original PETRA shape can be recovered exactly,
while preserving recursive structure, positional identity, and
compositional meaning?
