# tools

This directory contains auxiliary scripts that operate on already-known
PETRA or research inputs. Presence in `tools/` does not imply that a
script is part of the canonical PETRA CLI interface or that its interface
is stable.

## Scope

Tools kept here must operate on known inputs:

- known integers used for deterministic PETRA analysis
- known PETRA shapes or signatures
- bounded research datasets

Tools must not implement structural discovery over opaque integers.

## Layout

- `research/` — dataset/report helpers and shape analysis scripts.
  Root-level wrappers with the same names are compatibility shims that
  delegate to `research/`.

## Research helpers

- `research/distinct_shapes.py` — distinct-shape extraction over bounded ranges
- `research/height_distribution.py` — height distribution over bounded ranges
- `research/shape_count_fast.py` — fast shape counting utility
- `research/shape_entropy.py` — entropy-style summaries over shape datasets
- `research/shape_first_occurrence.py` — first-occurrence reporting for shapes
- `research/surface_signature.py` — surface signature helper

## Historical note

During Phase 10, the historical PET runtime and its operator-side triage
tooling were removed. The following categories no longer exist in the
working tree:

- the `pet` CLI and all its subcommands
- the `pet_*` triage scripts and their compatibility wrappers
- the lens diagnostics and guarded redirect probes
- the scan/query dataset pipeline

They are preserved in Git history and in the audit documents under
`docs/reports/petra-phase-10-*.md`.

## Boundary

Nothing in this directory is part of the maintained PETRA distribution.
The canonical PETRA runtime lives under `src/petra/`. The Resolver
satellite lives under `resolver/`.
