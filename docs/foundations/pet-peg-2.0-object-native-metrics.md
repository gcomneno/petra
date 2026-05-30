# PET/PEG 2.0 Object-Native Metrics

This note defines PET/PEG 2.0 object-native metrics.

The object-native metrics layer computes metrics directly from `PETObject`
without requiring callers to convert into the legacy PET tree representation.

This is an integration step.

It does not replace the legacy metrics API yet.

## Background

The historical PET metrics API operates on legacy PET trees:

- `node_count(tree)`
- `leaf_count(tree)`
- `height(tree)`
- `max_branching(tree)`
- `branch_profile(tree)`
- `recursive_mass(tree)`
- `metrics_dict(tree)`

PET/PEG 2.0 now has a recursive semantic object model:

- `PETObject`
- root/child roles
- atomic/composite distinction
- structural addresses
- graph paths
- traces
- certificates

Object-native metrics allow PET/PEG 2.0 code to measure recursive objects
directly.

## Current implementation

Current implementation:

- `src/pet/object_metrics.py`

Public functions:

- `pet_object_node_count(obj)`
- `pet_object_leaf_count(obj)`
- `pet_object_height(obj)`
- `pet_object_max_branching(obj)`
- `pet_object_branch_profile(obj)`
- `pet_object_recursive_mass(obj)`
- `pet_object_average_leaf_depth(obj)`
- `pet_object_leaf_depth_variance(obj)`
- `pet_object_metrics_dict(obj)`

## Root object rule

A PET/PEG 2.0 root object is treated as a container for the top-level baseline.

The metric roots of a root object are therefore its children.

Example:

    PETObject(60)

represents:

    60 = 2^2 * 3 * 5

Its metric tree has top-level children:

    2^2, 3, 5

So the branch profile is:

    [3, 1]

This matches legacy `metrics_dict(encode(60))`.

## Selected child object rule

A selected child object can be measured as a standalone represented PET object.

Examples:

    PETObject(60).at((2,)) -> PETObject(4)
    PETObject(60).at((3,)) -> PETObject(3)

So:

    pet_object_metrics_dict(PETObject(60).at((2,))) == metrics_dict(encode(4))
    pet_object_metrics_dict(PETObject(60).at((3,))) == metrics_dict(encode(3))

## Legacy compatibility

Object-native metrics are currently legacy-compatible.

For representative values, this holds:

    pet_object_metrics_dict(pet_object_from_int(n)) == metrics_dict(encode(n))

This compatibility is deliberate. It allows migration without changing metric
meaning.

## Boundary

This layer does not claim:

- replacement of legacy `metrics_dict(tree)`
- mass migration of callers
- CLI behavior change
- routing-policy promotion
- factorization-performance improvement
- PEG algebra completeness

It is a PET/PEG 2.0 integration seam.

Future work may migrate selected callers from legacy tree metrics to
object-native metrics one at a time.
