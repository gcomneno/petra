# PET — Prime Exponent Tree

[![CI](https://github.com/gcomneno/pet/actions/workflows/ci.yml/badge.svg)](https://github.com/gcomneno/pet/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/gcomneno/pet)](https://github.com/gcomneno/pet/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

PET is a Python CLI for building, validating, rendering, and explaining Prime Exponent Tree artifacts.

It treats an integer not only as a value, but also as a structured multiplicative object.
The project studies that structure at three levels:

- **PET-Base** — canonical recursive representation
- **PET-Metrics** — structural observation and comparison
- **PET-METICA** — rewrite geometry on canonical PET shapes

PET is not presented as a replacement for classical arithmetic and not as a claimed solution to a major open problem.
It is best understood as an artifact, build, validation, and explanation layer for known PET structures.

## Why this is interesting

PET gives you a way to explore integers through their recursive prime-factorization structure.

It is useful as:

- a canonical representation of integers based on prime factorization
- a CLI for inspecting structural properties and metrics
- a reproducible lab for scans, queries, summaries, and empirical reports
- a rewrite-geometric playground for studying paths, asymmetries, and families of PET shapes

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
pet scan 2 1000 --jsonl artifacts/scan-2-1000.jsonl
```

### Query the scan

```bash
pet query filter artifacts/scan-2-1000.jsonl --where "height=2" --limit 5
```

## What is stable today

### Stable / core
- recursive encoding based on prime factorization
- canonical representation
- invertibility / roundtrip behavior
- machine-facing JSON representation
- CLI-based inspection and dataset generation

### Active observational layer
- PET-derived structural metrics
- structural comparison across families
- scan / query / atlas-style workflows

### Live research line
- PET-METICA as rewrite geometry on canonical PET shapes
- local rewrite moves such as `NEW`, `DROP`, `INC`, `DEC`
- shortest paths, canonical paths, asymmetries, and rewrite friction
- empirical family behavior in explored ranges

### Still exploratory
- broad mathematical generalization beyond explored ranges
- shape algebra and related experimental operations

## Project map

Start here depending on what you need:

- [docs/README.md](docs/README.md) — documentation entry point
- [docs/VISION.md](docs/VISION.md) — project vision and layer structure
- [docs/reports/STATUS.md](docs/reports/STATUS.md) — what is stable, empirical, or exploratory
- [docs/research/notes/PET-METICA.md](docs/research/notes/PET-METICA.md) — current rewrite-geometric research line
- [docs/reference/SPEC.md](docs/reference/SPEC.md) — formal PET-Base specification
- [docs/reference/CLI.md](docs/reference/CLI.md) — command-line usage
- [docs/reports/README.md](docs/reports/README.md) — reports, generated summaries, and report data
- [docs/research/README.md](docs/research/README.md) — research notes, experiments, workflows, and datasets
- [docs/paper/README.md](docs/paper/README.md) — paper-oriented material
- [ROADMAP.md](ROADMAP.md) — current priorities and next directions
- [CHANGELOG.md](CHANGELOG.md) — public release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide

## Typical workflow

A small practical PET workflow looks like this:

1. encode or inspect specific integers
2. compute structural metrics
3. generate a bounded JSONL scan
4. query or group the scan
5. summarize the dataset with report tooling
6. explore rewrite neighborhoods and paths where relevant

## Current scope

PET is currently best understood as:

- a small Python CLI
- a reproducible research/tooling lab
- a project for studying structural properties of integers through PET representations
- an emerging rewrite-geometric framework through PET-METICA

It is not yet a polished end-user product.

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
## Official showcases

See [`docs/reference/OFFICIAL_SHOWCASES.md`](docs/reference/OFFICIAL_SHOWCASES.md).
