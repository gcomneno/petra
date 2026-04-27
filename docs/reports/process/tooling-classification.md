# PET tooling classification

## Scope

This document classifies the current `tools/` scripts after the PET-only scope
cleanup.

The purpose of this classification is to keep PET focused on already-known
inputs and PET artifacts. Tools may analyze, build, validate, summarize, or
explain known PET structures, but they must not reintroduce structural discovery
over opaque integers.

## Boundary rule

Tools kept in this repository may operate on:

- known integers used for deterministic PET analysis
- known factorizations or factor specifications
- PET artifacts
- scan JSONL artifacts
- known PET shapes or signatures

Tools should not implement:

- ISS / IRSR structural search
- byte-stream-to-structure discovery
- partial probe or hybrid reconstruction pipelines
- preimage search
- target-directed candidate search
- opaque-integer reconstruction without known structure

## Stable report-facing tooling

These scripts or entry points are part of the current report-facing PET workflow.

### `tools/atlas_summary.py`

Status:
- stable report-facing tooling

Reason:
- consumes bounded scan JSONL artifacts
- produces atlas-style summary output
- referenced by stable reports and workflow docs

### `pet families benchmark-disjoint`

Status:
- stable report-facing CLI capability

Reason:
- defines the canonical disjoint family benchmark path
- used by generated family benchmark reports
- compatibility wrapper remains available at `tools/cluster_families_disjoint.py`

### `tools/cluster_families_disjoint.py`

Status:
- compatibility wrapper

Reason:
- retained for operator convenience
- canonical entry point is `pet families benchmark-disjoint`

### `tools/cluster_families.py`

Status:
- secondary dataset/report helper

Reason:
- related family-clustering tooling
- superseded for canonical reports by `pet families benchmark-disjoint`

### `tools/distinct_shapes.py`

Status:
- secondary dataset/report helper

Reason:
- extracts distinct PET shapes over bounded ranges

### `tools/height_distribution.py`

Status:
- secondary dataset/report helper

Reason:
- summarizes PET height distribution over bounded ranges

### `tools/shape_entropy.py`

Status:
- secondary dataset/report helper

Reason:
- computes entropy-style summaries over shape datasets

### `tools/shape_count_fast.py`

Status:
- secondary dataset/report helper

Reason:
- fast shape-counting utility over bounded ranges

### `tools/shape_first_occurrence.py`

Status:
- secondary dataset/report helper

Reason:
- reports first observed occurrence for PET shapes

### `tools/scan_query.py`

Status:
- secondary dataset/report helper

Reason:
- filters and aggregates PET scan JSONL artifacts

### `tools/pet_table.py`

Status:
- secondary dataset/report helper

Reason:
- generates PET tables from integer datasets

### `tools/pet_profile_range.py`

Status:
- secondary dataset/report helper

Reason:
- explores PET profiles over explicit numeric ranges

### `tools/pet_family_combinations.py`

Status:
- secondary dataset/report helper

Reason:
- generates or counts combinations across PET families in explicit ranges

## PET-METICA and shape research tooling

These scripts support the currently retained PET-METICA / shape-algebra research
line. They are research-facing, but they operate on known shapes, known
integers, or explicit bounded ranges.

### `tools/pet_rewrite_metric.py`

Status:
- PET-METICA research helper

Reason:
- supports rewrite-metric experiments and reports

### `tools/pet_shape_algebra.py`

Status:
- PET-METICA research helper

Reason:
- provides shape algebra operations over explicit known shapes

### `tools/pet_structural_diff.py`

Status:
- PET-METICA research helper

Reason:
- explains exact multiplicative/divisive PET updates

### `tools/shape_rewrite_arithmetic_v0.py`

Status:
- tested PET-METICA research helper

Reason:
- has dedicated test coverage
- works over explicit shape expressions and bounded shape paths

### `tools/exponent_shape_trace.py`

Status:
- PET shape research helper

Reason:
- computes exponent-shape traces over explicit exponent ranges
- supports the exponent-shape trace research note

## Usage rule

Workflow docs, contributor docs, and report regeneration notes should treat only
stable report-facing tooling as interface-stable unless this document is updated.

should not be presented as general discovery machinery.

Dataset/report helpers and PET-METICA research tools may be useful, but they
should not be presented as canonical public interfaces by default.
