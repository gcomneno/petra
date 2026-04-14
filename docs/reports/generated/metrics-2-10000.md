# First reproducible PET metrics report (2..10000)

## Scope

This report summarizes a bounded empirical scan of PET representations for integers
in the closed range `2..10000`.

It is intended as a first reproducible report for PET metrics, with explicit inputs,
generation path, and compact observations separated from interpretation.

## Reproduction

### Command

    python3 -m src.pet.cli scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl

### Output dataset

- path: `docs/reports/data/scan-2-10000.jsonl`
- record count: `9999`
- schema: JSONL scan schema v1

## Summary statistics

### Height distribution

| height | count |
|---|---:|
| 1 | 6082 |
| 2 | 3477 |
| 3 | 440 |

### Maximum branching distribution

| max_branching | count |
|---|---:|
| 1 | 1276 |
| 2 | 4101 |
| 3 | 3695 |
| 4 | 894 |
| 5 | 33 |

### Other aggregate results

| metric | value |
|---|---:|
| total records | 9999 |
| records with `recursive_mass = 0` | 6082 |
| maximum `node_count` | 7 |
| first `n` with maximum `node_count` | 3600 |
| maximum `height` | 3 |
| first `n` with maximum `height` | 16 |
| maximum `max_branching` | 5 |
| first `n` with maximum `max_branching` | 2310 |

## Concrete examples

### First record reaching maximum height

- `n = 16`
- `height = 3`

### First record reaching maximum branching

- `n = 2310`
- `max_branching = 5`

### First record reaching maximum node count

- `n = 3600`
- `node_count = 7`

## Observations

1. Most PETs in `2..10000` are shallow: height `1` or `2` accounts for `9559 / 9999` records.

2. Height `1` occurs exactly `6082` times, which matches the number of records with `recursive_mass = 0` in this dataset.

3. The most common local branching values are `2` and `3`, while `max_branching = 5` is rare (`33` cases in `9999` records).

4. The first record reaching maximum height is `16`, while the first record reaching maximum branching is `2310`, showing that depth and width peak on different inputs.

5. The first record reaching the maximum observed `node_count` is `3600`, indicating that larger structural mass appears before the upper bound of the scan.

## Interpretation and limits

This report is descriptive only.

It does not claim asymptotic laws, universality, or deep classification results.
All observations above are bounded to the explicit range `2..10000` and depend on the current PET encoding and metric definitions.

In particular:

- the report is intended as a reproducible empirical baseline
- it does not replace broader scans such as `2..10^5` or `2..10^6`
- it does not prove that the observed distributions remain stable beyond this range

### Metric-signature collision note

In exploratory checks on PET scan data, the canonical metric signature

- `node_count`
- `leaf_count`
- `height`
- `max_branching`
- `branch_profile`
- `recursive_mass`
- `average_leaf_depth`
- `leaf_depth_variance`

was observed to produce many repeated signatures across different integers, as expected for structural family-level descriptors.

However, in empirical checks on the ranges `2..200`, `2..1000`, and `2..10000`, no collisions were found between **different unordered PET shapes** under this signature. All observed collisions corresponded only to permutations of sibling subtrees.

This does **not** establish a general theorem. It is only an observational result for the tested ranges, but it supports the current canonical metric set as a compact descriptor of unordered PET structural shape.

### Canonical metric signature vs atlas shape granularity

In empirical checks on the range `2..10000`:

- distinct canonical metric signatures: `33`
- distinct unordered PET shapes: `33`
- distinct ordered PET shapes (atlas structural shapes): `63`

This suggests that, on the tested range, the canonical metric signature matches unordered PET structural shape exactly, while the atlas distinguishes a finer ordered-shape granularity.

Equivalently:

- canonical metrics act as a compact descriptor of **unordered** PET shape
- the atlas captures a more detailed notion of **ordered** PET shape

This is an empirical observation for the tested range, not a general proof.

### Stress check beyond `10000`

A broader empirical check on the range `2..50000` found the first counterexample to the correspondence between canonical metric signature and unordered PET shape.

Observed summary on `2..50000`:

- bad signature groups (same canonical metric signature, different unordered shapes): `1`
- rows in bad signature groups: `4`

So the current canonical metric signature remains a very strong descriptor of unordered PET shape, but it is **not** a complete identifier in general.

This refines the earlier `2..10000` observation: the correspondence holds on that smaller tested range, but extremely rare counterexamples do appear beyond it.

The first unordered-shape counterexample beyond `10000` is not explained by leaf-depth information loss alone. Instead, it reflects a finer difference in how branching and recursive mass are grouped across internal subtrees.

In the observed counterexample, the current canonical metrics capture the same global depth/profile statistics, but they do not distinguish between:

- a shape combining a dedicated fork subtree and a dedicated chain subtree
- a shape where the same structural mass is grouped into a more locally mixed subtree pattern

So the current canonical metric set captures global structural distribution very well, but it does not fully capture local subtree grouping.

In the broader `2..100000` check, the ambiguous unordered-shape signature still appears to be dominated by one recurring shape, while the alternative locally mixed shape was observed only once (`36864`) in the tested range.

An experimental extended metric, `subtree_mixing_score`, was then added as a research-only probe for this blind spot. In its current form, it measures local child-subtree shape heterogeneity inside internal exponent subtrees. Empirically, it remains extremely sparse: on `2..10000` it is positive only for `4096`, and on `2..1000000` it is positive for `125` cases. In this first version it behaves more like a rare binary detector of local structural mixing than like a graded general-purpose metric, so it does **not** justify promotion into the canonical metric set at this stage.

When checked directly against the three known bad canonical-signature groups observed on `2..1000000`, `subtree_mixing_score` separated them cleanly: the more separated/dedicated shape scored `0.0`, while the corresponding locally mixed alternative scored `1.0` in all three groups.
