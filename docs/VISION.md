# PET Vision

## Overview

PET, **Prime Exponent Tree**, is a canonical recursive representation of positive integers `N >= 2` based on prime factorization and the internal structure of exponents.

The core idea is simple:

- every integer factorizes into primes
- each exponent is represented recursively using the same logic
- the result is a canonical tree
- the representation is invertible and lossless

PET does not aim to replace classical arithmetic.
Its value is structural: it offers a way to study integers through their recursive shape.

---

## General vision

PET is best understood as a project with **three main layers**:

1. **PET-Base**
2. **PET-Metrics**
3. **PET-METICA**

This separation avoids confusion between:

- canonical representation
- structural observation
- rewrite geometry and transport between shapes

A fourth area may exist later as a broader experimental frontier, but the current live architecture is centered on these three layers.

---

## 1. PET-Base

PET-Base is the rigorous core of the project.

At this level, PET is defined as a canonical recursive representation of integers `N >= 2`:

- grounded in unique prime factorization
- recursive on exponents
- invertible via `decode`
- validatable at the implementation level
- serializable in canonical JSON form

### Objective

Answer the question:

> What is the canonical PET representation of this integer?

### Core properties

- **canonicality**: the construction yields one PET for each integer
- **invertibility**: the integer can be reconstructed from its PET
- **losslessness**: the representation preserves all information needed for reconstruction
- **validatability**: malformed or non-canonical PET documents can be rejected explicitly
- **serializability**: PET has a canonical machine-facing JSON representation

### Role

PET-Base is the foundational grammar of the project.
It should remain as stable, simple, and rigorous as possible.

---

## 2. PET-Metrics

PET-Metrics studies the shape of canonical PETs.

Once an integer is represented as a tree, natural questions follow:

- how deep is it?
- how branched is it?
- how wide or narrow is it?
- how symmetric is it?
- how structurally complex is it?

### Objective

Use PET as a **morphological lens** on integers.

### Examples of metrics

- `height`
- `node_count`
- `leaf_count`
- `max_branching`
- `verticality_ratio`
- branch profile by level
- recursive exponential mass
- structural asymmetry

### Role

PET-Metrics is the observational layer of the project.

Its purpose is not to change PETs, but to measure them, compare them, and detect possible non-trivial regularities across families of integers.

If PET becomes more than an elegant encoding, this layer is one of the first places where that added value should become visible.

---

## 3. PET-METICA

PET-METICA is the rewrite-geometric layer.

At this level, the interesting object is no longer only the static PET representation of an integer, but also the **space of transformations** between canonical PET shapes.

The key shift is this:

- classical arithmetic asks what result an operation gives
- PET-METICA asks how one canonical PET shape can be transformed into another

### Core idea

PET-METICA treats:

- a canonical PET shape as a state
- local rewrite moves as primitive operations
- sequences of rewrites as paths
- minimal rewrite cost as distance

Typical local moves include:

- `NEW`
- `DROP`
- `INC`
- `DEC`

### Objective

Study integers through the **geometry of transport between PET shapes**.

The central questions become:

- which shapes are close under canonical rewrite?
- which transformations are easy or hard?
- which nodes act as hubs?
- where do asymmetries appear?
- which families of integers appear favored or disfavored in bounded rewrite scans?

### Role

PET-METICA is not a replacement for arithmetic syntax.
It is an experimental but increasingly concrete layer for studying:

- shortest rewrite paths
- canonical rewrite paths
- directed asymmetries
- local friction of moves
- bounded and large-scale structure of the rewrite graph

The current evidence suggests that this layer has genuine mathematical content and should be treated as a first-class research direction, not as a decorative add-on.

### Important note

PET-METICA must not alter PET-Base.

The canonical representation of an integer remains fixed.
PET-METICA works **on top of** that canonical layer, studying how canonical shapes relate and transform.

---

## 4. Broader experimental frontier

Beyond the three active layers above, PET may later support additional experimental directions, such as:

- explicit shape algebra
- subtree substitution or grafting
- partial shape workflows
- bounded completion spaces

These directions are real and worth exploring, but they should be kept clearly separate from the core definition of PET and from the current live rewrite-geometric line of PET-METICA.

---

## Why PET may be valuable

PET does not currently claim to solve a major classical problem.

Its potential value lies elsewhere:

- offering a canonical recursive representation of integers
- making their recursive exponent structure visible
- supporting structural comparison between integers
- enabling metric and geometric observations on canonical shapes
- opening the way to a rewrite-based structural arithmetic

In this sense, PET is not a replacement for number theory.
It is better understood as a **platform for studying the shape and transformability of integers**.

---

## Conceptual roadmap

### Phase A — consolidate PET-Base

- formal definition
- canonical JSON format
- encode/decode
- robust validation

### Phase B — develop PET-Metrics

- define stable structural metrics
- compare families of numbers
- search for non-trivial patterns
- separate robust observations from suggestive ones

### Phase C — develop PET-METICA

- define local rewrite moves cleanly
- study shortest paths and canonical paths
- measure asymmetries and rewrite friction
- identify hubs and bounded favored/disfavored family behavior
- understand the large-scale geometry induced by rewrite

### Phase D — expand the experimental frontier carefully

- shape algebra
- partial shape workflows

This last phase should remain explicitly experimental and should never blur the boundaries of PET-Base.

---

## Conclusion

PET is a structural framework with:

- a rigorous core (**PET-Base**)
- an observational layer (**PET-Metrics**)
- a rewrite-geometric layer (**PET-METICA**)

Today, the most promising live direction beyond PET-Base is not a vague “tree algebra”, but the more concrete study of **rewrite geometry on canonical PET shapes**.

That is the line currently captured by PET-METICA.
