# PET — Diagonal Growth Experiments

Dataset:
docs/paper/data/shape_first_occurrence.txt

We study the growth of the generator sequence

n_k = minimal integer realizing the k-th PET shape.

Goal:
understand the asymptotic law of n_k.

---

## Empirical observation

From the dataset we observe:

log(n_k) ≈ 0.15585 * sqrt(k) + 24.5129

which implies

n_k ≈ 4.424 × 10^10 · exp(0.15585 √k)

The fit is extremely accurate for k ≥ 200.

---

## Empirical verification

Example at k = 400

Observed:

log(n_400) = 27.6299

Prediction:

0.155852 * sqrt(400) + 24.5129  
= 27.6299

Relative error ≈ 0.0001%.

The model matches the tail of the dataset almost perfectly.

---

## Geometric interpretation

If

log(n_k) ≈ c √k

then

k ≈ (log n_k)^2 / c^2

This is consistent with the empirical shape count:

S(N) ≈ (log N)^2

Thus:

• the number of PET shapes ≤ N  
• the position of the minimal generator n_k  

appear governed by the same log² geometry.


---

## PET Shape Growth Conjecture

Let S(N) be the number of distinct PET shapes realized by integers n ≤ N.

Empirical data up to N = 10^24 strongly suggests:

S(N) ~ C (log N)^2

with

C ≈ 0.52

Equivalently, if n_k denotes the minimal integer realizing the k-th PET shape,

k ~ C (log n_k)^2

or

log(n_k) ~ sqrt(k / C)

This indicates that the space of PET shapes behaves like a two–dimensional geometry in logarithmic scale.


---

## PET Diagonal Law

Let n_k denote the minimal integer realizing the k-th PET shape.

Empirical analysis of the generator sequence suggests the asymptotic relation

log(n_k) ~ c √k

with

c ≈ 0.155

Equivalently,

n_k ~ exp(c √k)

This law describes the growth of the minimal generators along the diagonal of the PET shape space.

Combined with the empirical relation

S(N) ~ C (log N)^2

this implies

S(n_k) ~ k

meaning that the diagonal generators traverse the PET shape space approximately linearly.

