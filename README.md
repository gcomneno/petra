# PET — Prime Exponent Tree

[![CI](https://github.com/gcomneno/pet/actions/workflows/ci.yml/badge.svg)](https://github.com/gcomneno/pet/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/gcomneno/pet)](https://github.com/gcomneno/pet/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

PET is a Python CLI and research toolkit for working with Prime Exponent Tree artifacts.

It studies integers not only as numeric values, but also as structured
multiplicative objects. The project now separates its layers explicitly:

- **PET-Base**: current stable tree/JSON representation for integers `N >= 2`
- **First-principles PET**: conceptual model with `PET(1)` as the recursive leaf object
- **PET-Metrics**: structural observation and comparison on canonical PETs
- **PET/PEG 2.0**: object-native model, addresses, traces, paths, and operator experiments
- **PET-METICA**: rewrite-geometry research on canonical PET shapes

PET is not presented as a replacement for classical arithmetic, not as a faster
factorization method, and not as a claimed solution to a major open problem.

It is best understood as a reproducible artifact, validation, measurement,
explanation, and research lab for known PET structures.

## Why this is interesting

PET gives you a way to inspect integers through recursive prime-exponent
structure.

It is useful as:

- a canonical machine-facing representation for integers `N >= 2`
- a first-principles notation for reasoning about recursive exponent objects
- a CLI for encoding, validating, rendering, and measuring PET artifacts
- a reproducible lab for scans, queries, summaries, and empirical reports
- a research playground for PET/PEG object structure, traces, paths, and rewrite geometry

The stable parts are intentionally separated from research-facing tooling. This
keeps the project useful without pretending that every experiment is a theorem.

## Try it in 30 seconds

### Install locally

```bash
pip install -e .
```

### Inspect a number

```bash
pet encode 72
```

Output:

```text
N = 72
[
  {
    "p": 2,
    "e": [
      {
        "p": 3,
        "e": null
      }
    ]
  },
  {
    "p": 3,
    "e": [
      {
        "p": 2,
        "e": null
      }
    ]
  }
]
decoded = 72
```

### Inspect structural metrics

```bash
pet metrics 256
```

Output:

```text
N = 256
node_count = 3
leaf_count = 1
height = 3
max_branching = 1
branch_profile = [1, 1, 1]
recursive_mass = 2
average_leaf_depth = 3.0
leaf_depth_variance = 0.0
```

### Run a small bounded scan

```bash
pet scan 2 1000 --jsonl docs/reports/data/scan-2-1000.jsonl
```

### Query the scan

```bash
pet query filter docs/reports/data/scan-2-1000.jsonl --where "height=2" --limit 5
```

## What is stable today

### Stable machine representation

PET-Base is the current stable tree/JSON representation for integers `N >= 2`.

This includes:

- recursive encoding based on prime factorization
- canonical tree/JSON representation
- validation of malformed or non-canonical documents
- invertibility / roundtrip behavior through encode/decode
- CLI-based inspection and dataset generation

In the broader first-principles model, `PET(1)` is the conceptual leaf object.
In the stable PET-Base tree/JSON representation, that leaf appears internally as
`•` / JSON `null`, not as a standalone PET-Base document.

### First-principles foundation

The foundation docs define the conceptual model used to reason about PET
objects:

- `PET(1)` as the recursive leaf object
- canonical `PET(n)` once prime-exponent structure is known
- numeric collapse
- current-level support
- height
- numeric equality vs structural equality
- the construction boundary: PET notation does not hide factorization cost

### Active observational layer

PET-Metrics studies structural properties of canonical PETs.

This includes:

- canonical structural metrics exposed by `pet metrics`
- scan / query / atlas-style workflows
- bounded reports and family comparisons
- extended metrics that remain research-facing unless explicitly promoted

### PET/PEG 2.0 object layer

The object-native model is richer than the stable PET-Base tree representation.

It includes:

- recursive PET objects
- object roles and addresses
- graph/path traversal concepts
- traces and replay certificates
- operator experiments

This layer is useful, but it should not be confused with the minimal
first-principles notation or the stable PET-Base JSON contract.

### Research-facing tooling

PET-METICA and related tooling explore rewrite geometry on canonical PET shapes.

Research-facing commands include:

    pet branch-neighbors 12
    pet rewrite pair 12 9 --overscan 120
    pet rewrite explain 12 9 --overscan 120
    pet rewrite friction --n-max 10 --overscan 40 --limit 3
    pet rewrite scan --n-max 20 --overscan 60
    pet rewrite matrix --n-max 10 --overscan 60 --json

These commands are operational, but their findings are bounded empirical results,
not general mathematical theorems.

### Still exploratory

- broad mathematical generalization beyond explored ranges
- shape algebra and related experimental operations
- routing / guarded redirect experiments
- historical or research-only CLI paths

## Project map

Start here depending on what you need:

- [docs/README.md](docs/README.md) — documentation entry point
- [docs/foundations/README.md](docs/foundations/README.md) — PET/PEG 2.0 conceptual foundations and roadmap
- [docs/foundations/pet-first-principles-implementation-audit.md](docs/foundations/pet-first-principles-implementation-audit.md) — implementation audit against first-principles PET
- [docs/VISION.md](docs/VISION.md) — project vision and layer structure
- [docs/reports/STATUS.md](docs/reports/STATUS.md) — what is stable, empirical, or exploratory
- [docs/ROADMAP.md](docs/ROADMAP.md) — post-release development roadmap
- [docs/research/notes/PET-METICA.md](docs/research/notes/PET-METICA.md) — current rewrite-geometric research line
- [docs/reference/SPEC.md](docs/reference/SPEC.md) — formal PET-Base specification
- [docs/reference/CLI.md](docs/reference/CLI.md) — command-line usage
- [docs/reports/README.md](docs/reports/README.md) — reports, generated summaries, and report data
- [docs/research/README.md](docs/research/README.md) — research notes, experiments, partial-shape material, and datasets
- [ROADMAP.md](ROADMAP.md) — current priorities and next directions
- [CHANGELOG.md](CHANGELOG.md) — public release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide

## Typical workflow

A small practical PET workflow starts with the stable layer:

1. encode or inspect specific integers
2. validate or render PET artifacts
3. compute canonical structural metrics
4. generate a bounded JSONL scan
5. query or group the scan
6. summarize the dataset with report tooling

Research-facing workflows can then explore:

7. PET/PEG object structure, addresses, traces, and paths
8. PET-METICA rewrite neighborhoods and bounded path behavior
9. structural factorization and triage tooling where explicitly useful

A current structural factorization CLI smoke run is:

    pet structural-factorization 24680 --max-depth 4

A current operator-side triage smoke run is:

    tools/pet_triage_pipeline.sh 10007 --no-fork --no-fork-follow --no-recursive

## Current scope

PET is currently best understood as:

- a small Python CLI
- a stable PET-Base artifact and JSON representation project
- a first-principles notation and documentation effort
- a reproducible metrics, scan, query, and report tooling project
- an active research lab for PET/PEG object structure and PET-METICA rewrite geometry

It is not yet a polished end-user product.

It is also not a claim that PET avoids factorization cost or proves broad
mathematical generalizations from bounded experiments.

## Development

The project targets Python 3.10+.

Local install:

```bash
pip install -e .
```

Run tests:

```bash
pytest -q
```

## License

MIT
