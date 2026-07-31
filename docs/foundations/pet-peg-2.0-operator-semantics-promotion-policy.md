# PET/PEG 2.0 Operator Semantics Promotion Policy

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


> **Historical promotion policy.** Its `NEW`/`DROP`/`INC`/`DEC` reports and
> experimental CLI boundary remain legacy research material. The canonical
> future operator contract is
> [`../reference/SPEC.md`](../reference/SPEC.md);
> this policy does not promote or define `SPROUT`, `SHED`, `GRAFT`, or `PRUNE`.

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

They remain outside the stable `pet` CLI contract, but may be exposed through
an explicit opt-in `pet experimental ...` wrapper.

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

## Experimental CLI wrapper

The aggregated reports may be exposed through explicit opt-in commands:

    pet experimental operator-semantics report N
    pet experimental operator-semantics matrix --range START END

This wrapper delegates to the experimental report tools. It must stay thin and
must not redefine operator semantics in the stable CLI layer.

Promotion beyond this opt-in experimental wrapper requires a separate decision.
