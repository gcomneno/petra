# PET/PEG Executable Operator Semantics Snapshot v0

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


> **Legacy/research snapshot.** The executable value-level `NEW`, `DROP`,
> `INC`, and `DEC` semantics below are not canonical PET operator semantics.
> The future normative object-native contract is
> [`../reference/SPEC.md`](../reference/SPEC.md).

## Purpose

This document records the current research-only executable PET/PEG 2.0
operator semantics snapshot.

It aligns the foundation notes with the current research probes.

This is not stable PET-Base behavior.

## Boundary

This snapshot is research semantics only.

It does not change:

- stable CLI behavior
- PET core behavior
- default operator semantics
- routing
- residual descent
- anchor selection
- verification
- factorization claims

## Probe inventory

The current executable research layer is represented by:

```text
tools/research/pet_operator_axis_invariant_probe.py
tools/research/pet_operator_address_probe.py
tools/research/pet_operator_x_address_probe.py
tools/research/pet_operator_y_address_probe.py
tools/research/pet_operator_y_mutation_probe.py
tools/research/pet_operator_z_route_probe.py
```

Recursive addresses

A PET/PEG recursive address is a labeled selector through PET baselines.

Examples:

[]
[p]
[p, q]
[p, q, r]

The empty address [] refers to the current PET object.

A non-empty address selects a primal root at each recursive PET level.

Axis summary
X = support topology
Y = recursive refinement
Z = route / connectivity / path-history dynamics
X-axis — support topology

The current research-only executable form is the uniform parent-support form:

NEW(parent_address, q)
DROP(parent_address, p)

parent_address resolves to the PET object whose baseline/support is
hypothetically mutated.

NEW(parent_address, q)

Adds a new primal root q to the baseline of the PET object resolved by
parent_address.

Example:

NEW(parent_address=[], q=11)

adds 11 to the top-level baseline.

Example:

NEW(parent_address=[7], q=11)

enters the exponent-object associated with top-level root 7 and adds 11
to that recursive baseline.

DROP(parent_address, p)

Removes primal root p from the baseline of the PET object resolved by
parent_address.

Example:

DROP(parent_address=[], p=5)

removes top-level root 5.

Example:

DROP(parent_address=[7], p=3)

enters the exponent-object associated with top-level root 7 and removes
local root 3 from that recursive baseline.

Y-axis — recursive refinement

The current research-only target form is:

INC(address)
DEC(address)

address resolves to a selected primal root.

The Y-axis target is the exponent-object associated with that selected root.

INC(address)

INC(address) is valid when the address resolves to an existing selected root.

The current hypothetical value-level mutation candidate is:

exponent k -> k + 1

Examples:

INC(address=[3])
INC(address=[7, 2])
DEC(address)

DEC(address) is partial.

The current hypothetical value-level mutation candidate is:

exponent k -> k - 1

and is valid only when k > 1.

A selected leaf exponent represents exponent 1, so current research probes
classify DEC on a leaf exponent as invalid.

Z-axis — route / connectivity / path-history dynamics

Z-axis operators do not mutate PET object structure.

The current research-only history-prefix form is:

REDIRECT(at_history_prefix, from_next, to_next)
SHADOW_SELECT(at_history_prefix, selected_next)

A Z-axis operator references route/history semantics.

Addresses may appear inside operator invocation labels, but Z does not treat
addresses as direct mutation targets.

REDIRECT(at_history_prefix, from_next, to_next)

REDIRECT is a route/history event.

It is interpreted as:

after this path-history prefix,
replace or consider replacing the expected next step with another candidate
next step
SHADOW_SELECT(at_history_prefix, selected_next)

SHADOW_SELECT is a candidate-route selection event.

It is interpreted as:

after this path-history prefix,
select this candidate next step
Current working forms
NEW(parent_address, q)
DROP(parent_address, p)

INC(address)
DEC(address)

REDIRECT(at_history_prefix, from_next, to_next)
SHADOW_SELECT(at_history_prefix, selected_next)
X/Y composition observations

A research-only X/Y commutativity probe now compares two orderings from the
same starting PET object:

    X then Y
    Y then X

The probe currently observes and classifies executable composition behavior.
It does not promote a final algebra.

Initial observed classifications include:

    commutes
    non-commutes
    both-invalid
    support-created-y-target
    support-removed-y-target

Observed examples:

    NEW(parent_address=[], q=7) and INC(address=[3]) on 60 commute.

    NEW(parent_address=[], q=7) before INC(address=[7]) creates a Y target
    that does not exist in the reverse order.

    DROP(parent_address=[], p=2) before INC(address=[2]) removes a Y target
    that exists in the reverse order.

    NEW(parent_address=[2], q=5) and INC(address=[2]) on 60 are both valid
    in both orders, but do not commute.

These observations are still research-only and value-level. They do not define
final PET/PEG algebraic closure.

Address stability observations

A research-only address stability probe now compares resolution of a tracked
recursive address before and after one operator.

Initial observed classifications include:

    stable
    created
    destroyed
    retargeted
    leaf-blocked
    still-invalid
    operator-invalid

The key distinction is that an address can remain syntactically valid while
its resolved exponent-object changes. Current probes classify that case as
retargeted.

These observations remain research-only and do not define final address
stability rules.

Open questions
Are value-level Y mutations the final Y-axis semantics, or only one candidate?
How should X/Y mutations compose with path-history?
Can addresses survive arbitrary NEW, DROP, INC, and DEC sequences?
When do two distinct histories represent the same structural state?
Which Z-axis invariants should be validated first?
How should synthetic route labels evolve into structured PEG edge payloads?
Status

This document is a snapshot of current research-only executable semantics.

It should be revised as PET/PEG 2.0 operator semantics mature.
