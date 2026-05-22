# PET/PEG 2.0 Executable Operator Semantics Baseline

## Purpose

This document closes the PET/PEG 2.0 research-only executable operator
semantics baseline.

The baseline makes recursive PET/PEG operator semantics explicit, executable,
testable, and documented.

It does not define stable PET-Base behavior.

It does not claim that PEG algebra is complete.

## Baseline status

PET/PEG 2.0 currently has research-only executable probes for:

    recursive operator addresses
    X-axis support topology
    Y-axis target resolution
    Y-axis hypothetical value mutation
    Z-axis history-prefix route semantics
    X/Y composition and commutativity observations
    address stability across one operator

This is a coherent executable research baseline, not a final algebra.

## Operator address layer

Recursive addresses select locations inside PET objects.

Current executable probe:

    tools/research/pet_operator_address_probe.py

An address such as:

    []
    [2]
    [2, 2]

is resolved against the recursive PET object produced by the existing PET core
encoding.

The empty address [] resolves to the current PET object.

A non-empty address selects recursive primal roots through exponent-objects.

## X-axis baseline

X-axis operators currently use parent-support form:

    NEW(parent_address, q)
    DROP(parent_address, p)

Current executable probe:

    tools/research/pet_operator_x_address_probe.py

X-axis operators are support-topology operations on the PET object resolved by
parent_address.

The probe classifies validity. It does not change stable core behavior.

## Y-axis baseline

Y-axis operators currently use selected-root form:

    INC(address)
    DEC(address)

Current executable probes:

    tools/research/pet_operator_y_address_probe.py
    tools/research/pet_operator_y_mutation_probe.py

The Y-axis target is the exponent-object associated with the selected primal
root.

The current hypothetical value-level mutation probe models:

    INC(address): exponent k -> k + 1
    DEC(address): exponent k -> k - 1, only when k > 1

DEC on a leaf exponent is invalid in the current research probes.

This is still a candidate value-level semantics, not a final Y-axis theory.

## Z-axis baseline

Z-axis operators currently use history-prefix route references:

    REDIRECT(at_history_prefix, from_next, to_next)
    SHADOW_SELECT(at_history_prefix, selected_next)

Current executable probe:

    tools/research/pet_operator_z_route_probe.py

Z-axis operators do not directly mutate PET object structure.

They operate on route/history/connectivity semantics.

The current probe validates synthetic history-prefix payloads and candidate
next-step references. It does not execute route changes.

## X/Y composition baseline

Current executable probe:

    tools/research/pet_operator_xy_commutativity_probe.py

The probe compares two orderings from the same starting PET object:

    X then Y
    Y then X

Observed classifications include:

    commutes
    non-commutes
    both-invalid
    left-invalid
    right-invalid
    support-created-y-target
    support-removed-y-target

This establishes an executable observation layer for X/Y composition.

It does not claim complete algebraic closure.

## Address stability baseline

Current executable probe:

    tools/research/pet_operator_address_stability_probe.py

The probe resolves a tracked address before and after one operator invocation.

Observed classifications include:

    stable
    created
    destroyed
    retargeted
    leaf-blocked
    still-invalid
    operator-invalid

The important distinction is that an address may remain syntactically valid
while resolving to a changed exponent-object. Current probes classify that case
as retargeted.

## Current test coverage

The baseline is covered by focused tests for each executable research probe:

    tests/test_tools_pet_operator_address_probe.py
    tests/test_tools_pet_operator_x_address_probe.py
    tests/test_tools_pet_operator_y_address_probe.py
    tests/test_tools_pet_operator_y_mutation_probe.py
    tests/test_tools_pet_operator_z_route_probe.py
    tests/test_tools_pet_operator_xy_commutativity_probe.py
    tests/test_tools_pet_operator_address_stability_probe.py

## Boundaries

This baseline is research-only.

It does not change:

    stable CLI behavior
    PET core factorization behavior
    residual routing
    anchor selection
    verification logic
    default operator semantics

It does not introduce lookup tables or special-case catalogues.

It does not claim that PET magically factors integers.

## Post-2.0 questions

The following work moves beyond this baseline:

    longer operator sequences
    broader X/Y commutativity families
    address stability across multi-step histories
    path-history identity
    structured PEG edge payloads
    Z-axis route execution experiments
    possible future CLI opt-in research modes

These are post-2.0 research questions, not requirements for this baseline.
