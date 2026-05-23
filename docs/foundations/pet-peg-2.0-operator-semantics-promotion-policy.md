# PET/PEG 2.0 Operator Semantics Promotion Policy

This document defines the current promotion boundary for PET/PEG 2.0 operator
semantics tooling.

The goal is to stop treating every operator-semantics artifact as equally
research-only while avoiding premature promotion into stable PET behavior.

## Decision

PET/PEG 2.0 operator semantics does not graduate as one block.

Only aggregated operator-semantics reports are promoted from research-only
probes to experimental documented tooling:

- `tools/research/pet_operator_semantics_report.py`
- `tools/research/pet_operator_semantics_report_matrix.py`

These reports are now classified as:

    experimental PET/PEG 2.0 operator semantics reports

They remain outside the stable `pet` CLI contract.

## Still research-only

Primitive probes remain research-only:

- `tools/research/pet_operator_address_probe.py`
- `tools/research/pet_operator_x_address_probe.py`
- `tools/research/pet_operator_y_address_probe.py`
- `tools/research/pet_operator_y_mutation_probe.py`
- `tools/research/pet_operator_z_route_probe.py`
- `tools/research/pet_operator_xy_commutativity_probe.py`
- `tools/research/pet_operator_address_stability_probe.py`
- `tools/research/pet_operator_axis_invariant_probe.py`

These tools expose laboratory-level observations and may change as the operator
model evolves.

## Promotion ladder

Current ladder:

    primitive probes
    -> research-only

    aggregated reports
    -> experimental documented tooling

    stable pet CLI
    -> not promoted yet

The experimental report layer may expose documented command examples, JSON
schemas, summaries, and pattern grouping behavior.

It must not define default PET semantics.

## Experimental report contract

The experimental report tools may promise:

- deterministic output for the same repository version and inputs
- schema-versioned JSON payloads
- documented command examples
- additive JSON fields when possible
- tested behavior for known seed ranges and representative examples

They do not promise:

- stable long-term CLI compatibility
- stable PET core semantics
- stable operator algebra completeness
- stable routing or factorization policy
- support as part of the public `pet` command

## Boundary

This promotion does not change:

- stable CLI behavior
- PET core factorization behavior
- residual routing
- anchor selection
- verification logic
- default operator semantics
- PEG algebra completeness claims

## Next possible promotion

A future tranche may add an explicit opt-in experimental CLI wrapper, for
example:

    pet experimental operator-semantics report N
    pet experimental operator-semantics matrix --range START END

That future step requires a separate decision and implementation tranche.

It must not happen accidentally as part of research probe expansion.
