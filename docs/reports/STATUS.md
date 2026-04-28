# PET Status

Current source of truth for the status of the PET project.

This document separates:

1. **PET-Base** — what is already defined and stable
2. **PET-Metrics** — stable canonical metrics plus exploratory extended metrics
3. **PET-METICA** — the current rewrite-geometric research line
4. **Open frontier** — active but not yet stabilized directions

---

## 1. PET-Base

### Status
**Stable core**

### Scope
PET-Base is the canonical recursive representation of integers `N >= 2` via prime factorization and recursive exponent encoding.

### Claims currently treated as established

- PET represents every integer `N >= 2`
- PET is canonical by construction
- PET is invertible
- PET is lossless
- PET has a canonical machine-facing JSON representation
- malformed or non-canonical PET documents can be rejected explicitly
- PET-Base is the stable foundational layer of the project

### Evidence
- formal project definition
- encode/decode behavior
- validation rules
- tests and implementation constraints
- `SPEC.md`

### Confidence
**High**

---

## 2. PET-Metrics

### Status
**Active observational layer**

### Scope
PET-Metrics studies structural properties of canonical PETs. The canonical metric set is stable and exposed by `pet metrics` and scan JSONL records; extended/research metrics remain exploratory and are exposed separately by `pet xmetrics`.

### Claims currently treated as established

- PET-Metrics is a legitimate observational layer on top of PET-Base
- canonical PETs can be measured structurally
- families of integers can be compared through PET-derived structural descriptors

### Claims currently treated as empirical / exploratory

- canonical structural metrics are stable enough for CLI, scan, query, and bounded reports
- extended/research metrics may reveal non-trivial regularities but are not part of the canonical metric contract
- some metric patterns may be stable across large ranges
- some integer families may have recognizably different PET profiles

### Evidence
- CLI metrics layer
- atlas / scan / report workflows
- exploratory datasets and research notes

### Confidence
**Medium**
for the existence of the layer, **lower** for any specific broad mathematical claim not yet stabilized in docs

---

## 3. PET-METICA

### Status
**Live research line**

### Scope
PET-METICA studies canonical PET shapes as states in a rewrite space, with local moves such as:

- `NEW`
- `DROP`
- `INC`
- `DEC`

and with paths, shortest paths, canonical paths, asymmetries, and rewrite friction as the main objects of interest.

### Claims currently treated as established at the experimental level

- PET rewrite paths can be computed operationally in bounded settings
- PET distance does not collapse to ordinary numeric distance
- the rewrite graph exhibits real hubs
- local reversibility depends strongly on the prime involved
- rewrite asymmetry is real and measurable
- some multiplicative families behave differently at the global level

### Empirical conclusions currently supported by experiments

- PET distance can differ sharply from `|m-n|`
- hubs such as `4`, `6`, `12`, `30` emerge in explored ranges
- local rewrite friction grows strongly with the prime involved
- the observed local friction hierarchy is:
  `2 < 3 < 5 < 7`
- powers of `2` behave as a globally favored family in explored ranges
- powers of `3` appear weaker / borderline favorable
- powers of `5` appear globally repulsive
- powers of `7` appear strongly repulsive

### Important caution

These are **empirical computational findings**, not proved theorems.

PET-METICA is the most promising current research direction beyond PET-Base, but it remains an experimental layer.

### Evidence
- `../research/notes/PET-METICA.md`
- `tools/pet_rewrite_metric.py`
- pair / scan / matrix experiments
- family reports
- one-step return cost reports

### Confidence
**Medium**
for the existence of the rewrite-geometric structure, **medium-low to medium**
for broad generalization beyond explored ranges

---

## 4. Open frontier

### Status
**Exploratory**

### Includes
- shape algebra
- subtree substitution / grafting
- partial shape workflows
- bounded completion spaces

### Current position
These directions are real and useful, but they are **not** currently the main source of truth for the project architecture.

They should remain clearly separated from:

- PET-Base as stable core
- PET-Metrics as observational layer
- PET-METICA as the current live rewrite-geometric line

### Confidence
**Open / experimental**

---

## 5. Current project picture

### Stable
- PET-Base

### Active and useful
- PET-Metrics

### Most promising live research direction
- PET-METICA

### Still experimental frontier
- shape algebra / partial shape workflows

---

## 6. What this file is not

This file is not a proof document.

It is a **status map**:
- what is stable
- what is empirical
- what is active
- what is still exploratory

For formal core behavior, see `reference/SPEC.md`.
For project vision, see `VISION.md`.
For rewrite-geometric status, see `../research/notes/PET-METICA.md`.
