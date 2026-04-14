# PET shape families — short research note

## Scope

This note collects a few small but structurally meaningful observations that emerged from bounded PET scans and direct CLI exploration.

The aim is not to state general theorems without proof, but to separate:

- families that are essentially exact by construction,
- small patterns that are strongly supported by bounded evidence,
- broader growth-law heuristics that remain empirical.

---

## Canonical shape notation

We use the PET `branch_profile` notation already exposed by the CLI and scan datasets.

Examples:

- `[k]` means a root with `k` leaf children and no deeper recursion.
- `[k,1]` means a root with `k` children, exactly one of which carries a minimal extra recursive step.
- `[2,2]`, `[2,2,1]`, `[3,2]` represent mixed-width recursive profiles.

All statements below refer to the first observed generator of a given structural profile.

---

## Table of small shape families

| Shape family | First observed generator | Candidate law | Status | Notes |
|---|---:|---|---|---|
| `[2]` | `6` | primorial of first 2 primes | exact-by-construction | `6 = 2 * 3` |
| `[3]` | `30` | primorial of first 3 primes | exact-by-construction | `30 = 2 * 3 * 5` |
| `[4]` | `210` | primorial of first 4 primes | exact-by-construction | `210 = 2 * 3 * 5 * 7` |
| `[5]` | `2310` | primorial of first 5 primes | exact-by-construction | `2310 = 2 * 3 * 5 * 7 * 11` |
| `[2,1]` | `12` | `2 ×` generator of `[2]` | exact-by-construction / minimal constructive pattern | `12 = 2^2 * 3` |
| `[3,1]` | `60` | `2 ×` generator of `[3]` | exact-by-construction / minimal constructive pattern | `60 = 2^2 * 3 * 5` |
| `[4,1]` | `420` | `2 ×` generator of `[4]` | exact-by-construction / minimal constructive pattern | `420 = 2^2 * 3 * 5 * 7` |
| `[5,1]` | `4620` | `2 ×` generator of `[5]` | exact-by-construction / minimal constructive pattern | `4620 = 2^2 * 3 * 5 * 7 * 11` |
| `[2,2]` | `36` | no closed law claimed here | bounded empirical fact | first balanced binary-recursive profile seen in small scans |
| `[2,1,1]` | `48` | no closed law claimed here | bounded empirical fact | first deeper hybrid profile seen in small scans |
| `[1,2]` | `64` | no closed law claimed here | bounded empirical fact | tower-like profile that opens at the next level |
| `[2,2,1]` | `144` | no closed law claimed here | bounded empirical fact | first profile seen with `recursive_mass = 3` |
| `[3,2]` | `180` | no closed law claimed here | bounded empirical fact | first genuinely wide-recursive mixed profile seen in small scans |
| `[3,1,1]` | `240` | no closed law claimed here | bounded empirical fact | first broad-and-deeper hybrid profile seen in bounded scans |

---

## Why `[k]` is exact-by-construction

The profile `[k]` requires:

- exactly `k` root branches,
- all branches to be leaves,
- no recursive exponent structure.

So the smallest integer with that PET shape is the product of the `k` smallest distinct primes:

`2 * 3 * 5 * ... * p_k`

That is exactly the `k`-prime primorial.

---

## Why `[k,1]` strongly suggests a minimal constructive law

The profile `[k,1]` can be read as:

- the same wide root as `[k]`,
- plus one branch upgraded from leaf to the smallest nontrivial recursive exponent.

Empirically, in the small families checked so far:

- `[2,1]` appears first at `12 = 2 × 6`,
- `[3,1]` appears first at `60 = 2 × 30`,
- `[4,1]` appears first at `420 = 2 × 210`,
- `[5,1]` appears first at `4620 = 2 × 2310`.

This strongly supports the rule:

`first([k,1]) = 2 × first([k])`

At the current stage this can be treated as a very natural minimal constructive law, but it is still worth separating from fully formalized theorem language unless written out carefully in PET-native terms.

---

## Small-zoo interpretation

Bounded scans suggest that PET complexity appears in layers:

1. **Pure flat width** appears first: `[2]`, `[3]`, `[4]`, `[5]`.
2. **Minimal width-plus-recursion** appears next: `[k,1]`.
3. **Balanced or mixed recursive hybrids** appear later: `[2,2]`, `[2,2,1]`, `[3,2]`, `[3,1,1]`.
4. **Global shape growth** appears ordered, but current evidence remains empirical.

This supports the practical view that PET structural space does not grow chaotically in the small range: new families appear in a fairly disciplined order.

---

## What is safe to claim now

### Safe

- The first generator of flat width profile `[k]` is the primorial of the first `k` primes.
- The small checked family `[k,1]` follows the minimal rule `2 × primorial_k` for `k = 2, 3, 4, 5`.
- Profiles such as `[2,2]`, `[2,2,1]`, `[3,2]`, `[3,1,1]` emerge later than the flat-width families in bounded scans.

### Not yet safe as a strong theorem

- Any global asymptotic law for first occurrence `n_k` across all PET shapes.
- Any fitted relation inferred only from plots such as `log(n_k)` vs `sqrt(k)` or `S(N)` vs `(log N)^2`.
- Any claim that the observed order of family emergence is universal without a PET-native proof.

---

## Recommended next steps

Small, concrete next steps that fit the current repo direction:

1. Add a short research-facing note or table of first generators by shape family.
2. Keep exact constructive families (`[k]`, maybe `[k,1]`) clearly separated from bounded empirical patterns.
3. Only after that, decide whether shape-family exploration deserves a dedicated CLI/report helper.

