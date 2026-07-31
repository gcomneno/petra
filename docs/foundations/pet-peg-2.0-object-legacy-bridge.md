# PET/PEG 2.0 Object Legacy Bridge

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


This note defines the bridge between the PET/PEG 2.0 recursive object model and
the legacy PET tree representation.

The bridge exists for migration.

It does not make the legacy tree representation the PET/PEG 2.0 conceptual core.

## Background

The historical PET implementation still uses legacy tree APIs in many places:

- `encode`
- `decode`
- `validate`
- `metrics_dict`
- `to_jsonable`
- `from_jsonable`
- `shape_signature_dict`

PET/PEG 2.0 introduced a recursive object model:

- `PETObject`
- root/child roles
- atomic/composite distinction
- structural addresses
- structural identity
- root-base semantics
- operators
- graph paths
- traces and certificates

The bridge lets old and new code interoperate while migration proceeds.

## Legacy tree to PETObject

Current implementation:

- `pet_object_from_legacy_tree(tree)`

Semantics:

1. validate the legacy PET tree
2. decode the represented integer
3. rebuild a PET/PEG 2.0 `PETObject`

This preserves represented integer value and canonical object shape.

Example:

    pet_object_from_legacy_tree(encode(60)) -> PETObject(60)

## PETObject to legacy tree

Current implementation:

- `pet_object_to_legacy_tree(obj)`

Semantics:

1. read the recursive PET object children
2. rebuild the corresponding legacy PET tree
3. validate the resulting tree

This works for root objects and selected child objects.

Examples:

    pet_object_to_legacy_tree(PETObject(60)) == encode(60)
    pet_object_to_legacy_tree(PETObject(60).at((2,))) == encode(4)
    pet_object_to_legacy_tree(PETObject(60).at((3,))) == encode(3)

## Boundary

This bridge does not claim:

- mass replacement of `encode`
- stable CLI behavior change
- routing-policy promotion
- factorization-performance improvement
- PEG algebra completeness
- legacy tree model as PET/PEG 2.0 conceptual core

The bridge is a migration seam.

Future work may move specific APIs from legacy trees to `PETObject`, but those
changes should be explicit and tested one API at a time.

## Current implementation

Implementation:

- `src/pet/object_model.py`
- `pet_object_from_legacy_tree`
- `pet_object_to_legacy_tree`

Tests:

- `tests/test_object_legacy_bridge.py`
