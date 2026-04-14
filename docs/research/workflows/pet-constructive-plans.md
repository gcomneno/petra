# Constructive PET plans

## Goal

Explore a forward constructive use of PET updates.

Instead of starting from a large integer and asking for inverse factorization, we start from a small integer and apply a local update plan:

- `attach p`: add a new prime branch
- `bump p`: increment an existing prime branch

The goal is to build integers directly from a structural history, then inspect:

- final integer
- PET generator
- PET signature
- local branch evolution

This stays inside a domain where PET is operational in forward mode.

## Plan model

Current prototype tool:

- `tools/pet_constructive_plan.py`

Accepted plan shape:

```json
{
  "start": 2,
  "steps": [
    {"op": "attach", "prime": 3},
    {"op": "bump", "prime": 2},
    {"op": "attach", "prime": 5}
  ]
}
```

Optional repetition is supported:

```json
{"op": "bump", "prime": 2, "repeat": 10}
```

Validation rules:

- `attach p` is valid only if `p` is not already present in the current factorization
- `bump p` is valid only if `p` is already present
- each repeated step is validated again on the current state

## Observations

### 1. `attach` is linear and easy to read

Example plan:

```json
{
  "start": 2,
  "steps": [
    {"op": "attach", "prime": 3},
    {"op": "attach", "prime": 5},
    {"op": "attach", "prime": 7},
    {"op": "attach", "prime": 11}
  ]
}
```

Result:

- final integer: `2310`
- generator: `2310`
- signature: `[[], [], [], [], []]`

Interpretation:

- each `attach` adds one new leaf branch
- the global shape growth is monotone
- this is the cleanest constructive regime

### 2. `bump` is local but not structurally monotone

Example plan:

```json
{
  "start": 2,
  "steps": [
    {"op": "bump", "prime": 2, "repeat": 10}
  ]
}
```

Result:

- final integer: `2048 = 2^11`
- generator: `4`
- signature: `[[[]]]`

This is the key phenomenon:

- the integer becomes large by forward construction
- but the PET shape class may still have a very small generator
- arithmetic size and PET shape complexity are strongly decoupled

Local branch evolution for the bumped branch shows why:

- `1 -> 2`: `[] -> [[]]`
- `2 -> 3`: `[[]] -> [[]]`
- `3 -> 4`: `[[]] -> [[[]]]`
- `4 -> 5`: `[[[]]] -> [[]]`
- `5 -> 6`: `[[]] -> [[], []]`
- `6 -> 7`: `[[], []] -> [[]]`
- `7 -> 8`: `[[]] -> [[[]]]`
- `8 -> 9`: `[[[]]] -> [[[]]]`
- `9 -> 10`: `[[[]]] -> [[], []]`
- `10 -> 11`: `[[], []] -> [[]]`

So a repeated `bump` does not produce monotone branch growth.
It follows the PET structure of the successive exponents.

### 3. Mixed constructive histories can produce large integers with much smaller generators

Example plan:

```json
{
  "start": 6,
  "steps": [
    {"op": "bump", "prime": 2, "repeat": 3},
    {"op": "bump", "prime": 3, "repeat": 2},
    {"op": "attach", "prime": 5},
    {"op": "bump", "prime": 5, "repeat": 2}
  ]
}
```

Result:

- final integer: `54000`
- generator: `3600`

Interpretation:

- a coherent forward local history can build a large integer directly
- the resulting PET shape can still compress to a much smaller generator
- the tool therefore exposes not only construction, but also shape compression

## Provisional conclusion

A constructive PET workflow is viable.

We can:

1. specify a local forward update history
2. build the final integer directly
3. validate local `attach` / `bump` coherence at each step
4. inspect final generator and signature
5. avoid starting from an already-given large integer and asking for inverse factorization

However, the constructive history does **not** imply monotone growth of global PET shape complexity.

In particular:

- `attach` behaves cleanly and monotonically
- `bump` is governed by the PET structure of the updated exponent
- large forward-constructed integers may still belong to shape classes with small generators

## Exponent-shape trace

For a repeated `bump` on a fixed prime branch, the most informative local observable is not the full PET signature of the whole integer, but the shape evolution of the updated exponent itself.

We call this local sequence the **exponent-shape trace**.

For a bump on prime `p`, each local transition is:

- `exp_before -> exp_after`
- `branch_before = signature(exp_before)`
- `branch_after = signature(exp_after)`

So the trace records the PET shape evolution of the successive exponents attached to that branch.

### Example

For the plan

```json
{
  "start": 2,
  "steps": [
    {"op": "bump", "prime": 2, "repeat": 10}
  ]
}
```

the exponent-shape trace is:

- `1 -> 2`: `[] -> [[]]`
- `2 -> 3`: `[[]] -> [[]]`
- `3 -> 4`: `[[]] -> [[[]]]`
- `4 -> 5`: `[[[]]] -> [[]]`
- `5 -> 6`: `[[]] -> [[], []]`
- `6 -> 7`: `[[], []] -> [[]]`
- `7 -> 8`: `[[]] -> [[[]]]`
- `8 -> 9`: `[[[]]] -> [[[]]]`
- `9 -> 10`: `[[[]]] -> [[], []]`
- `10 -> 11`: `[[], []] -> [[]]`

### Immediate observations

1. The exponent-shape trace is local.

   It isolates the structural dynamics of the updated branch and avoids mixing it with unrelated global shape changes elsewhere in the integer.

2. The exponent-shape trace is generally non-monotone.

   Successive exponent shapes may repeat, collapse, or branch in different ways.
   A repeated `bump` therefore does not correspond to monotone structural growth.

3. The exponent-shape trace explains why forward constructive plans can be easy to execute but hard to summarize globally.

   The arithmetic update is trivial (`n -> n * p`), but the induced PET branch evolution is governed by the PET structure of the new exponent.

### Usefulness

This notion is useful because it separates two different questions:

- **construction**: can we build the integer forward by local valid updates?
- **structural evolution**: how does the PET shape of the updated branch evolve under those updates?

The current prototype tool already exposes enough local data to study exponent-shape traces directly.

## Status

This is currently a research-facing prototype only.

- tool: `tools/pet_constructive_plan.py`
- not promoted to public CLI
- no package-level API changes
- suitable as a base for further experiments on constructive PET histories
