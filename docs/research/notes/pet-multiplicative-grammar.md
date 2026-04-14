# PET multiplicative grammar

## Scope

This note records a small structural grammar for PET in the **multiplicative domain**.

It does **not** solve exact PET computation for large integers without factorization.
It does **not** provide a general rule for additive exponent collision (`e1 + e2`).

What it does provide is a compact set of local structural operators that appear to govern how PET behaves under multiplication and exact division.

---

## Core observation

PET behaves much more cleanly under **multiplication** than under additive exponent collision.

Two regimes must be kept separate:

- **coprime composition**
- **shared-prime update**

For coprime factors, PET composition appears to be a canonical multiset union of branches.
For shared primes, multiplication acts as a local update of an existing branch.

The same grammar also admits a natural inverse in the case of **exact division**.

---

## Operator 1: `coprime_union(A, B)`

### Meaning

Combine two PET signatures coming from coprime factors.

### Rule

If `gcd(a, b) = 1`, then:

```text
signature(a*b) = canon(signature(a) ⊎ signature(b))
```

where:

- `⊎` is multiset union
- `canon(...)` is canonical sorting / normalization of the signature

### Interpretation

No collision happens.
No existing branch is modified.
The branches are simply accumulated.

---

## Operator 2: `attach_branch(S)`

### Meaning

Introduce a new prime factor with exponent `1`.

### Effect

Add a new root branch of shape:

```text
[]
```

to the signature `S`, then canonicalize.

### Arithmetic interpretation

This corresponds to multiplying by a prime `p` that is **not yet present** in the current factorization.

---

## Operator 3: `bump_branch(S, branch)`

### Meaning

Update the branch associated with a prime that is already present.

### Effect

If the current branch corresponds to exponent `k`, replace:

```text
sig(k) -> sig(k+1)
```

leaving all other branches unchanged, then canonicalize.

### Arithmetic interpretation

This corresponds to multiplying by a prime `p` that is **already present** in the current factorization.

### Important note

This operator is conceptually clear, but on a pure PET signature the branches are not labeled by concrete primes.
So this operator is best understood as a structural rule that requires extra bookkeeping if one wants to implement it directly.

---

## Operator 4: `prime_multiply(S, p)`

### Meaning

Local multiplication by a prime `p`.

### Effect

- if `p` is new: apply `attach_branch(S)`
- if `p` is already present: apply `bump_branch(S, branch_of_p)`

### Interpretation

This is the fundamental local operator of the multiplicative grammar.

---

## Derived operator: `multiply_by_factor(S, m)`

If:

```text
m = ∏ p_i^a_i
```

then multiplying by `m` can be understood as a sequence of local `prime_multiply` updates, one for each prime factor `p_i`, repeated `a_i` times.

This turns general multiplication into a sequence of local branch operations.

---

## Inverse operator 1: `detach_branch(S, branch)`

### Meaning

Remove a branch whose exponent drops from `1` to `0`.

### Effect

Remove the corresponding root branch of shape:

```text
[]
```

from the signature `S`, then canonicalize.

### Arithmetic interpretation

This corresponds to exact division by a prime `p` whose current exponent is `1`.

---

## Inverse operator 2: `decrement_branch(S, branch)`

### Meaning

Decrease by one the exponent represented by an existing branch.

### Effect

If the current branch corresponds to exponent `k > 1`, replace:

```text
sig(k) -> sig(k-1)
```

leaving all other branches unchanged, then canonicalize.

### Arithmetic interpretation

This corresponds to exact division by a prime `p` that is already present with exponent greater than `1`.

---

## Inverse operator 3: `prime_divide(S, p)`

### Meaning

Local exact division by a prime `p`.

### Effect

- if the exponent of `p` is `1`: apply `detach_branch(S, branch_of_p)`
- if the exponent of `p` is greater than `1`: apply `decrement_branch(S, branch_of_p)`

### Interpretation

This is the local inverse of `prime_multiply(S, p)` in the exact-divisibility regime.

---

## Derived inverse operator: `divide_by_factor(S, m)`

If:

```text
m = ∏ p_i^a_i
```

and the division is exact, then dividing by `m` can be understood as a sequence of local `prime_divide` updates, one for each prime factor `p_i`, repeated `a_i` times.

This turns exact division into a sequence of local branch-removal or branch-decrement operations.

---

## Inverse structural operator: `partition_signature(S)`

In the coprime regime, partitioning a signature into blocks corresponds to structural coprime decomposition.

If:

```text
S = canon(A ⊎ B)
```

then `A` and `B` can be read as the PET contributions of two coprime factors.

This acts as a structural inverse to `coprime_union`.

---

## What this grammar captures

This grammar captures:

- canonical union of coprime PET components
- local branch creation for new primes
- local branch update for existing primes
- local branch removal under exact division
- local branch decrement under exact division
- decomposition of multiplication and exact division into branch-level operations

---

## What this grammar does not capture

This grammar does **not** yet capture the additive collision problem:

```text
e1 + e2
```

In particular, the experiments suggest that additive collision is **not** determined by PET signature alone, and likely requires additional arithmetic information beyond the compressed PET form.

So the current grammar should be understood as a **multiplicative PET grammar**, not as a complete PET calculus.

---

## Working interpretation

PET is not only a static anatomy of multiplicative structure.
In the multiplicative domain, it also admits a local transformation grammar:

- new prime -> attach branch
- existing prime -> bump branch
- exact division on exponent-1 branch -> detach branch
- exact division on deeper branch -> decrement branch
- coprime composition -> union
- general multiplication -> sequence of local updates
- exact division -> sequence of local inverse updates

This appears to be the first solid layer of PET "musculature".

---

# Minimal worked examples

These examples match the current research-facing prototype
`tools/pet_structural_diff.py`.

### Example 1: `12 * 15 = 180`

Factorizations:

```text
12  = 2^2 * 3
15  = 3 * 5
180 = 2^2 * 3^2 * 5
```

Structural update:

- `5` is new at the root → `attach_branch`
- `3` is already present and its exponent goes `1 -> 2` → `bump_branch`
- `2` is unchanged

Prototype classification:

```text
attached:    5
bumped:      3
unchanged:   2
```

### Example 2: `20 * 18 = 360`

Factorizations:

```text
20  = 2^2 * 5
18  = 2 * 3^2
360 = 2^3 * 3^2 * 5
```

Structural update:

- `3` is new at the root → `attach_branch`
- `2` is already present and its exponent goes `2 -> 3` → `bump_branch`
- `5` is unchanged

Prototype classification:

```text
attached:    3
bumped:      2
unchanged:   5
```

### Example 3: `180 / 15 = 12`

Factorizations:

```text
180 = 2^2 * 3^2 * 5
15  = 3 * 5
12  = 2^2 * 3
```

Structural update:

- `5` goes `1 -> 0` → `detach_branch`
- `3` goes `2 -> 1` → `decrement_branch`
- `2` is unchanged

Prototype classification:

```text
removed:       5
decremented:   3
unchanged:     2
```

### Example 4: `360 / 18 = 20`

Factorizations:

```text
360 = 2^3 * 3^2 * 5
18  = 2 * 3^2
20  = 2^2 * 5
```

Structural update:

- `3` goes `2 -> 0` → `detach_branch`
- `2` goes `3 -> 2` → `decrement_branch`
- `5` is unchanged

Prototype classification:

```text
removed:       3
decremented:   2
unchanged:     5
```

## Relation to the prototype

The current prototype does not attempt to update a pure unlabeled signature directly.

Instead, it works on concrete prime factorizations and reports the corresponding
root-level branch events:

- multiplication: `attached_branches`, `bumped_branches`
- exact division: `removed_branches`, `decremented_branches`

This is intentional: the structural grammar is clean, but branch identity under
shared-prime updates still requires concrete prime bookkeeping.
