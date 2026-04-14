# PET local generator algebra (bounded note)

## Status

Empirical bounded note.
This is evidence, not a proof.

## Scope

This note concerns canonical PET generators, not arbitrary integers in the same PET shape class.

Let `G(T)` denote the minimal generator of a PET shape `T`.

## Local node operator

If a canonical PET node has child generators

`g_1 >= g_2 >= ... >= g_k >= 1`

then its generator is given by the local operator

`Ω(g_1, ..., g_k) = product_i p_i ^ g_i`

where `p_i` is the `i`-th prime.

This is the local construction rule of a canonical node from the canonical generators of its children.

## Local factorization law

The same expression can be rewritten as

`Ω(g_1, ..., g_k) = primorial(k) * product_i p_i ^ (g_i - 1)`

So a node splits naturally into:

- an arity shell: `primorial(k)`
- a structural payload: `product_i p_i ^ (g_i - 1)`

Leaf children (`g_i = 1`) contribute only to the arity shell and disappear from the payload.

## Local rewrite laws

### 1. Add-leaf law

Adding one leaf child at the end gives

`Ω(g_1, ..., g_k, 1) = Ω(g_1, ..., g_k) * p_(k+1)`

So adding a leaf at root multiplies the generator by the next prime.

### 2. Positional rewrite law

If child generators change from

`(g_1, ..., g_k)` to `(g'_1, ..., g'_k)`

without changing canonical order, then

`Ω(g'_1, ..., g'_k) / Ω(g_1, ..., g_k) = product_i p_i ^ (g'_i - g_i)`

So rewriting a child at position `i` propagates upward as a multiplicative factor on the prime attached to that position.

### 3. Commutation with leaf-padding

Consider two compatible fixed prefixes

`(g_1, ..., g_m)` and `(g'_1, ..., g'_m)`

with canonical order preserved.

Then the induced rewrite factor

`product_i p_i ^ (g'_i - g_i)`

is independent of how many leaf children are appended after the prefix.

Equivalently: local rewrite on the non-leaf prefix commutes with adding trailing leaf children.

### 4. Composition law

If three compatible prefixes satisfy

`a -> b -> c`

then the corresponding rewrite factors compose multiplicatively:

`F(a -> c) = F(a -> b) * F(b -> c)`

where `F` is the rewrite factor induced by the positional rewrite law.

This means that bounded local rewrites behave like a multiplicative calculus on canonical child-generator tuples.

## Bounded evidence

### Node factorization check

On unique observed PET shapes up to `1,000,000`:

- checked: `78`
- mismatches: `0`

This checks the factorization

`G = primorial(k) * product_i p_i ^ (g_i - 1)`

using the canonical child generators of the root.

### Add-leaf check

On recurring fixed-prefix families observed up to `1,000,000`:

- checked transitions: `53`
- mismatches: `0`

This checks

`Ω(g_1, ..., g_k, 1) = Ω(g_1, ..., g_k) * p_(k+1)`

### Positional rewrite check

On bounded comparable fixed-prefix families observed up to `1,000,000`:

- checked comparisons: `80`
- mismatches: `0`

This checks

`Ω(g'_1, ..., g'_k) / Ω(g_1, ..., g_k) = product_i p_i ^ (g'_i - g_i)`

for cases where canonical rank order is preserved.

### Commutation with leaf-padding check

On bounded comparable fixed-prefix families observed up to `1,000,000`:

- checked comparisons: `110`
- mismatches: `0`

This checks that the rewrite factor between two compatible prefixes does not depend on the total arity `k`, as long as the same prefix rewrite is being compared after appending leaf children.

### Rewrite composition check

On bounded triples of compatible fixed-prefix families observed up to `1,000,000`:

- checked triples: `196`
- mismatches: `0`

This checks

`F(a -> c) = F(a -> b) * F(b -> c)`

for bounded compatible prefix rewrites.

## Small examples

### Add leaf

- `[2,2] -> [2,2,1]`
- `36 -> 180`
- factor: `5`

- `[6,1] -> [6,1,1]`
- `192 -> 960`
- factor: `5`

### Positional rewrite

- `[2] -> [6]`
- ratio: `2 -> 32`
- factor: `2^(6-2) = 16`

- `[4,2] -> [12,2]`
- ratio: `24 -> 6144`
- factor: `2^(12-4) = 256`

- `[2,2,2] -> [4,2,2]`
- ratio: `30 -> 120`
- factor: `2^(4-2) = 4`

### Commutation with leaf-padding

The rewrite

- `[2] -> [6]`

has constant factor `16` across all observed families

- `[2] -> [6]`
- `[2,1] -> [6,1]`
- `[2,1,1] -> [6,1,1]`
- ...

Similarly,

- `[2,2] -> [4,2]`

has constant factor `4` across all observed compatible arities.

### Rewrite composition

- `[2] -> [4] -> [6]`
- factors: `4 * 4 = 16`
- direct factor: `[2] -> [6] = 16`

- `[2,2] -> [4,2] -> [6,4]`
- factors: `4 * 36 = 144`
- direct factor: `[2,2] -> [6,4] = 144`

- `[2,2,2] -> [4,2,2] -> [4,4,2]`
- factors: `4 * 9 = 36`
- direct factor: `[2,2,2] -> [4,4,2] = 36`

## Interpretation

This suggests a local multiplicative rewrite algebra on canonical PET generators.

The relevant local state of a node is:

- its arity
- the ordered tuple of canonical child generators

The main bounded picture is:

- node construction is local and multiplicative
- leaf-padding acts as a simple arity extension
- compatible rewrites act through prime-weighted multiplicative factors
- these factors commute with leaf-padding
- these factors compose multiplicatively along rewrite chains

Branch-profile does not capture this law; it is only a lossy projection.

## Open points

- prove that the recursive canonical encoding is globally minimal
- characterize when canonical order is preserved under local rewrites
- determine whether this local algebra extends cleanly beyond the bounded regime explored here
- understand whether the rewrite factors admit a more abstract algebraic presentation
