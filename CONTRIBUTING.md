# Contributing to PET

Thanks for your interest in PET.

This project is currently a small Python CLI and PET artifact/report tooling project for exploring recursive prime-exponent-tree representations of integers.

## Before you start

Please prefer:

- small, focused changes
- clear commit messages
- tests for behavior changes
- documentation updates when user-facing behavior changes

When possible, do not mix unrelated work in the same change.

For example, avoid combining:
- a bug fix
- a refactor
- a documentation rewrite

in the same PR.

## Local setup

Create and activate a virtual environment, then install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running tests

Run the test suite with:

```bash
pytest -q
```

You can also use the Makefile test target:

```bash
make test
```

## Useful project entry points

If you are changing behavior or documentation, these files are usually the most relevant:

- `README.md`
- `docs/README.md`
- `docs/VISION.md`
- `docs/reports/STATUS.md`
- `docs/reference/CLI.md`
- `docs/reference/SPEC.md`
- `docs/reports/README.md`
- `docs/research/README.md`

Core package implementation lives under:

- `src/pet/`

Operator-side tools are namespaced by role:

- `tools/core/` — PET triage core and policy-first handoff
- `tools/classic/` — bounded classic verification support
- `tools/legacy/` — historical lens diagnostics
- `tools/research/` — dataset/report helpers and research helpers

Root-level `tools/*.py` and `tools/*.sh` entries are usually compatibility wrappers.
When adding new tooling, prefer the appropriate namespaced directory.

Tests live under:

- `tests/`

## Change guidelines

### CLI and behavior changes

If you change CLI behavior, output shape, or semantics:

- update the relevant CLI documentation
- update or add tests
- keep examples aligned with actual output

In practice, this usually means checking:

- `docs/reference/CLI.md`
- `README.md`
- `docs/reports/process/canonical-workflow.md`
- `docs/reports/process/tooling-classification.md`

### Stable vs exploratory material

PET contains both stable/core material and exploratory/research-facing material.

Please keep that distinction explicit:

- stable definitions, contracts, and behavior belong in the main docs and implementation
- empirical observations, bounded patterns, and research-facing notes should stay in the appropriate research/report documents

Do not present exploratory observations as established facts.

### Documentation discipline

Please preserve the current documentation hierarchy:

- root docs for project-wide orientation and source of truth
- `docs/reference/` for stable specification and CLI reference
- `docs/research/` for active research notes, experiments, partial-shape material, and datasets
- `docs/reports/` for report-oriented process docs, generated summaries, and report data

If you move or rename docs, update cross-links in the affected README files.

`NEW`, `DROP`, `INC`, and `DEC` are legacy value-level semantics. Do not
introduce or reintroduce them as active PET semantics in specifications,
documentation, public command descriptions, or new semantic APIs. The sole
normative future PET/PEG 2.0 operator contract is
[`docs/foundations/pet-peg-2.0-object-native-operators.md`](docs/foundations/pet-peg-2.0-object-native-operators.md).
Any indispensable legacy reference must be explicitly marked as legacy/archive
or as an implementation-compatibility reference.

### Scope discipline

Prefer one kind of change per PR when possible:

- docs
- behavior
- refactor
- tooling

Small, reviewable PRs are strongly preferred over broad mixed changes.

## Style

There is no heavy formal contribution process yet.

For now:

- follow the existing code and doc style
- keep names and output consistent with the rest of the repo
- prefer clarity over cleverness
- keep stable claims, empirical findings, and exploratory ideas clearly separated

## Pull requests

A good pull request should make it easy to answer:

- what changed
- why it changed
- how it was validated

Include test or reproduction notes when relevant.

## Issues

Bug reports and focused improvement suggestions are welcome.

When reporting a problem, include:

- the command you ran
- the observed output or traceback
- the expected behavior
- enough context to reproduce the issue
