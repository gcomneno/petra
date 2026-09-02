# AGENTS.md

## Purpose

This file defines how coding and research agents should work in this repository.
It is an operational contract, not a semantic specification for PETRA.

## Sources of truth

- `docs/reference/SPEC.md` is the sole normative source for PETRA semantics.
- `docs/VISION.md` describes architectural direction and project intent; it does not override the specification.
- `ROADMAP.md` orders planned work; it does not make experimental behavior normative.
- `docs/research/` contains exploratory or historical material. Research becomes canonical only through an explicit promotion into the normative specification and the corresponding implementation work.

Do not duplicate PETRA semantics in this file. When a semantic question is unclear, resolve it against the canonical specification before changing code.

## Shape-first boundary

PETRA is shape-first. New work must preserve the distinction between primary canonical structure and optional projections or interpretations.

Do not reintroduce value-first, prime-labelled, or legacy PET behavior unless an explicit current PETRA requirement calls for it.

Historical code is not retained merely because it already exists. Git history, tags, releases, and archived research are the preservation mechanism for obsolete PET behavior.

## Change discipline

Before starting work:

1. inspect the current branch and repository state;
2. inspect open issues and pull requests for overlap or prerequisite work;
3. identify the canonical contract affected by the change;
4. keep one primary concern per change whenever practical.

For behavioral changes, prefer evidence and regression coverage before implementation. Preserve existing public contracts unless the active issue or canonical specification explicitly changes them.

Verification must be proportional to scope and should include the smallest focused check that demonstrates the changed contract plus broader regression coverage when the change can affect shared behavior.

## Research discipline

Research is not implementation by default.

Before running an experiment, freeze:

- the research question;
- the scope and controlled inputs;
- the measurements or comparison axes;
- the falsification criteria;
- the possible outcome classes.

Do not add success criteria after seeing the result merely to make an experiment pass.
Record negative and partial results as first-class evidence.

A successful experiment does not automatically become:

- PETRA semantics;
- a roadmap commitment;
- production API behavior;
- an upstream or downstream integration proposal.

Promotion requires a separate explicit decision and the appropriate canonical change.

## Cross-domain PETRA-inspired work

Keep these three layers distinct:

1. **PETRA semantics** — the canonical runtime and algebra defined by `docs/reference/SPEC.md`;
2. **PETRA-inspired design transfer** — applying a PETRA principle, such as canonical-structure-first / projection-second, to another domain;
3. **integration proposal** — a concrete proposal to change PETRA or another project based on evidence from that transfer.

Do not describe PETRA-inspired research as a PETRA feature unless it has been explicitly promoted into the canonical project.
Do not involve external maintainers or present an integration proposal as established until the local evidence justifies doing so.

## Legacy and migration

PETRA replaces the historical PET architecture rather than wrapping it permanently.
Reuse legacy artifacts only when a current PETRA requirement demonstrably needs them.
Do not preserve obsolete APIs, formats, operators, tests, probes, or compatibility layers solely for continuity.

## Agent collaboration

Prefer repository-visible evidence over assumptions or remembered state.
If another issue, pull request, branch, or research gate already owns the same concern, coordinate with that work instead of opening an overlapping implementation.

When uncertainty remains, make the boundary explicit in code, tests, or research notes rather than silently choosing a convenient interpretation.
