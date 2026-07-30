> Historical note.
> This note describes the legacy lens transition workflow. Current PET operator
> workflow is triage-first via `tools/core/pet_triage_pipeline.sh`; lens tools
> live under `tools/legacy/` and root-level wrappers remain available for
> compatibility. Its `NEW`, `DROP`, `INC`, and `DEC` labels are not canonical
> PET semantics; the sole normative future operator contract is
> [`../foundations/pet-peg-2.0-object-native-operators.md`](../foundations/pet-peg-2.0-object-native-operators.md).

# PET lens transition notes

Status: experimental note.

This note records the current PET lens transition chain.

## Chain

The current diagnostic chain is:

- pet_lens_hint
- pet_lens_candidates
- pet_lens_transition

In short:

hint -> candidate -> transition

## Layer 1: lens hint

The lens hint reads N and reports:

- blade_index
- target_lens
- target_leaf_count
- flatten_first

Example:

N = 3027009081

- blade_index = 10
- target_lens = two-leaf
- target_leaf_count = 2
- flatten_first = no

This selects the surface scale and the structural lens shape.

## Layer 2: lens candidates

The candidate helper turns the target lens into a minimal PET representative.

Example:

N = 3027009081

- source_generator = 30
- source_signature = [[], [], []]
- target_lens = two-leaf
- target_leaf_count = 2
- target_generator = 6
- target_signature = [[], []]

Interpretation:

The source is a three-leaf PET form.

The target lens is a two-leaf PET form.

The target generator is the minimal PET representative of that lens shape.

It is not asserted to be an arithmetic factor of N.

## Layer 3: lens transition

The transition helper compares the source generator and target generator.

Example:

N = 3027009081

- source_generator = 30
- target_generator = 6
- distance = 1
- structural_distance = 1
- transition = DROP
- representative_target = 15

Interpretation:

The source three-leaf form moves toward the target two-leaf lens by one PET DROP move.

The representative target is a value-level representative produced by the PET move, but it is not claimed to be a factor.

## Current examples

### Three-leaf to two-leaf

N = 3027009081

- source_generator = 30
- target_generator = 6
- transition = DROP
- representative_target = 15

PET reading:

The dominant next structural movement is three-leaf -> two-leaf.

### Two-leaf to one-leaf

N = 6345405191

- source_generator = 6
- target_generator = 2
- transition = DROP
- representative_target = 3

PET reading:

The dominant next structural movement is two-leaf -> one-leaf.

### Non-flat power-like case

N = 49

- source_generator = 4
- target_generator = 2
- flatten_first = yes
- transition_available = no

PET reading:

The source is non-flat / power-like.

A flat DROP transition is not directly available.

Flattening or a DEC-style transition is the more natural next family to investigate.

## Current claim

PET lens transition is diagnostic only.

It does not factor N.

It does not prove primality.

It identifies a structural movement between PET forms.

## Important distinction

The transition describes movement in PET shape space, not arithmetic division.

Example:

source_generator = 30
target_generator = 6
transition = DROP
representative_target = 15

This does not mean 15 divides the original N.

It means that a PET DROP move from the source structural representative reaches a value whose PET generator matches the target lens.

## Next open problem

The next open problem is to turn this transition into a useful PET-local probe.

Current chain:

N -> hint -> candidate -> transition

Next desired chain:

N -> hint -> candidate -> transition -> local probe proposal

The local probe should use the transition type, source generator, target generator, representative target, and mass-response bands to propose where PET should inspect next.
