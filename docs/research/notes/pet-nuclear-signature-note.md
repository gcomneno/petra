# PET nuclear signature note

## Claim

A **nuclear signature** extracted from local shape simplifications appears to add real structural information beyond standard PET shape metrics.

In particular, it can separate shapes that collide under the usual coarse metrics:
- `node_count`
- `height`
- `max_branching`
- `branch_profile`

## Setup

We worked purely at the level of **PET structural shapes**, ignoring numeric labels.

A shape was represented canonically as a nested unlabeled forest.

We defined three local simplification rewrites on shapes:

1. **prune-leaf**
   - remove one leaf occurrence

2. **contract-unary**
   - collapse a unary chain by one level

3. **dedup-siblings**
   - merge duplicate sibling subshapes

These rewrites were explored externally in tooling only, without modifying core PET semantics.

## Nuclear signature

Given a shape `S`, we explored the simplification closure of `S` up to bounded depth.

For each reached simplified shape, we computed its minimal canonical generator.

From this we defined:

- **first_nontrivial_nuclei**  
  the set of nontrivial generators reached at the minimum positive simplification depth

- **all_nontrivial_nuclei**  
  the set of all nontrivial generators reached within the bounded closure

By default, the trivial empty-shape generator `1` was excluded.

## Main observation

The nuclear signature distinguishes shapes that standard PET metrics do not distinguish.

### Collision 1

Both shapes have identical coarse metrics:

- `node_count = 4`
- `height = 2`
- `max_branching = 2`
- `branch_profile = [2, 2]`

But they differ in nuclear signature.

#### Shape A
- representative generator: `36`
- render: `[[[]], [[]]]`
- first nuclei: `[4, 12]`
- all nuclei: `[2, 4, 6, 12]`

#### Shape B
- representative generator: `192`
- render: `[[[], []], []]`
- first nuclei: `[12, 64]`
- all nuclei: `[2, 4, 6, 12, 64]`

So the standard metrics collide, while the nuclear signature separates the two shapes.

### Collision 2

Both shapes again share identical coarse metrics:

- `node_count = 5`
- `height = 2`
- `max_branching = 3`
- `branch_profile = [3, 2]`

But nuclear signatures differ.

#### Shape A
- representative generator: `180`
- render: `[[[]], [[]], []]`
- first nuclei: `[12, 36, 60]`
- all nuclei: `[2, 4, 6, 12, 30, 36, 60]`

#### Shape B
- representative generator: `960`
- render: `[[[], []], [], []]`
- first nuclei: `[60, 192]`
- all nuclei: `[2, 4, 6, 12, 30, 60, 64, 192]`

Again, metric collision is resolved by the nuclear signature.

## Interpretation

The standard metrics describe a shape mostly by **static coarse geometry**.

The nuclear signature instead captures something closer to the shape's **local collapse dynamics** under simplification rewrites.

So it behaves like a dynamic structural fingerprint rather than a purely static one.

## Early nucleus picture

In small ranges, after excluding the trivial nucleus `1`, the most recurrent nontrivial nuclei were:

- `2`
- `4`
- `6`
- `12`

This suggests a small family of recurrent structural attractors, with `12` emerging as a particularly important intermediate nucleus.

## Status

This is an external exploratory result only.

We have **not** yet promoted the nuclear signature into public PET API or core metrics.

Current evidence supports the following modest claim:

> Nuclear signature is a promising structural feature that can separate at least some real collisions of the current coarse PET metrics.

## Tooling used

External experimental tools used in this exploration included:

- `tools/shape_simplify_playground.py`
- `tools/shape_simplify_neighbors.py`
- `tools/shape_simplify_closure.py`
- `tools/shape_nucleus_census.py`
- `tools/shape_nucleus_signature.py`
- `tools/shape_nucleus_collision_probe.py`

## Next questions

Natural follow-ups:

1. measure how often nuclear signature separates collisions in larger scan ranges
2. study sensitivity to closure depth
3. test whether a reduced signature (for example first nuclei only) is already sufficient in many cases
4. determine whether some rewrite subset gives a cleaner or more stable notion of nucleus
