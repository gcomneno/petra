# PET/PEG Recursive Operator Addresses v0

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


> **Legacy/research address note.** Its prime-label selectors support the
> historical `NEW`, `DROP`, `INC`, and `DEC` experiments. The normative
> positional `@/…` and `^` contract is
> [`../reference/SPEC.md`](../reference/SPEC.md).

## Purpose

PET/PEG operators need explicit recursive addresses.

An operator name alone is not enough once PET objects are treated as recursive
structures whose exponents are themselves PET objects.

For example, in a PET object such as:

    2^(3*5) * 3 * 5^2 * 7^(2^((2*3)^11)*3*5)

the top-level baseline is:

    {2, 3, 5, 7}

but the exponent of 7 is itself a PET object:

    E_7 = 2^((2*3)^11) * 3 * 5

So INC is ambiguous unless it says where it applies.

## Address

An address is a recursive selector inside a PET object.

Examples:

    []
    [7]
    [7, 2]
    [7, 2, 3]

Each step selects a primal root in the baseline of the current recursive PET
object.

The empty address [] refers to the current PET object itself.

## Operator invocation

An operator invocation is an operator plus its address and arguments.

Examples:

    NEW(parent_address=[], q=11)
    DROP(parent_address=[], p=5)
    INC(address=[7])
    DEC(address=[7, 2])

The current executable research snapshot refines X-axis operators to use a
uniform parent-support form. See `operator-semantics-snapshot.md`.

## X-axis operators

X-axis operators change support topology at an addressed parent PET object.

The current executable research snapshot uses a uniform parent-support form:

    NEW(parent_address, q)
    DROP(parent_address, p)

### NEW(parent_address, q)

Adds a new primal root q to the baseline of the PET object resolved by
parent_address.

Example:

    NEW(parent_address=[], q=11)

adds 11 to the top-level baseline.

    NEW(parent_address=[7], q=11)

adds 11 inside the exponent-object associated with the top-level root 7.

### DROP(parent_address, p)

Removes primal root p from the baseline of the PET object resolved by
parent_address.

Example:

    DROP(parent_address=[], p=5)

removes the top-level root 5.

    DROP(parent_address=[7], p=3)

enters the exponent-object of 7 and removes the local root 3.

## Y-axis operators

Y-axis operators refine or reduce the exponent-object associated with the
selected primal root while preserving the baseline of the parent PET object.

### INC(address)

Refines the exponent-object associated with the selected primal root.

Example:

    INC(address=[2])

refines the exponent-object of the top-level root 2.

    INC(address=[7, 2])

enters the exponent-object of top-level 7, then refines the exponent-object
associated with local root 2.

### DEC(address)

Reduces the exponent-object associated with the selected primal root.

DEC is partial: it is valid only when the selected exponent-object has a
defined predecessor.

## Z-axis operators

Z-axis operators do not directly mutate PET object structure.

They affect route choice, connectivity, or traversal dynamics.

Examples:

    REDIRECT(at_history_prefix=H, from_next=A, to_next=B)
    SHADOW_SELECT(at_history_prefix=H, selected_next=A)

A Z-axis operator may reference route/history semantics. Addresses may appear
inside operator invocation labels, but Z is not itself a support-topology or
recursive-refinement mutation.

## PEG role

An address is not the PEG.

The distinction is:

    address
      structural coordinate inside a PET object

    operator(address)
      local transformation request

    PEG edge
      transition between PET states labeled by operator(address)

    path-history
      ordered sequence of PEG edges / operator invocations

So an address becomes PEG-relevant when it labels an operator transition.

Example:

    state_A -- INC(address=[7,2]) --> state_B

The corresponding path-history records the addressed invocation:

    [
      NEW(parent_address=[], q=7),
      INC(address=[7]),
      INC(address=[7,2]),
      DEC(address=[5])
    ]

## Shape-level paths vs PET addresses

The current shape-level algebra uses anonymous normalized paths:

    INC(path)
    DEC(path)

PET/PEG 2.0 uses labeled recursive addresses:

    INC(address)
    DEC(address)

Shape paths are useful for normalized structural probes.

PET addresses are needed for labeled recursive PET semantics and PEG
path-history.

## Address stability observations

A research-only address stability probe now resolves a tracked address before
and after one operator invocation.

The probe observes whether an address remains valid, becomes valid, becomes
invalid, or survives while resolving to a changed target.

Initial observed classifications include:

    stable
    created
    destroyed
    retargeted
    leaf-blocked
    still-invalid
    operator-invalid

Observed examples on 60:

    NEW(parent_address=[], q=7) preserves unrelated address [3].

    NEW(parent_address=[], q=7) creates address [7].

    DROP(parent_address=[], p=2) destroys address [2].

    INC(address=[2]) preserves address [2] syntactically, but changes the
    selected exponent-object, so the tracked address is classified as
    retargeted.

    DEC(address=[2]) makes recursive address [2,2] leaf-blocked because the
    exponent of 2 becomes a leaf exponent.

These observations are research-only. They classify executable address behavior
for current probes and do not define final PET/PEG address algebra.

## Open questions

- Should addresses be primal-root based, shape-path based, or represented in both forms?
- How stable are addresses after normalization?
- What invalidates an address?
- Can an address survive NEW, DROP, INC, and DEC?
- Are two histories distinct if they reach the same structure through different addresses?
- How should REDIRECT and SHADOW_SELECT reference addresses, routes, or both?

## Boundary

This document is research semantics only.

It does not change:

- stable CLI behavior
- default routing
- anchor selection
- residual descent
- verification
- factorization claims
