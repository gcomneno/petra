# PETRA Research Source Register

## Status

This file is the maintained register for external research material used by
PETRA as direct related work, methodological inspiration, or unpromoted source
material.

It is **non-normative for PETRA semantics**. Canonical semantics remain in
[`../reference/SPEC.md`](../reference/SPEC.md). Novelty boundaries are maintained
in [`RELATED-WORK.md`](RELATED-WORK.md).

## Source classes

### A. Direct related work

Use this class when a source has substantive conceptual, mathematical, or
algorithmic overlap with PETRA and therefore constrains how PETRA can describe
its novelty.

A direct-related-work source should normally be represented in
`RELATED-WORK.md` with an explicit statement of overlap and distinction.

### B. Methodological inspiration

Use this class when a source is useful for experimental design, observables,
statistical methods, framing, or research questions without being direct prior
art for PETRA's specific structure or operator system.

Methodological inspiration may motivate an experiment, but does not by itself:

- change PETRA semantics;
- establish a PETRA theorem;
- justify a novelty claim;
- become a dependency; or
- become direct related work.

Promotion to direct related work requires an explicit overlap assessment.

### C. Unpromoted source material

Downloaded papers, article bundles, notes, and other reading material remain in
this class until individually assessed. Their presence in a working corpus is
not evidence that PETRA depends on them or that every item is relevant to
PETRA.

Third-party PDFs are not committed to the repository merely to preserve a
reading list. Prefer stable DOI or official publication links in this register.

## Current sources

### Contucci et al. — rooted-tree encoding of N

**Classification:** A — direct related work; B — methodological inspiration.

Pierluigi Contucci, Claudio Giberti, Godwin Osabutey, Cecilia Vernia,
"Statistical properties of the rooted-tree encoding of N", *Physica A* 686
(2026), 131361.

DOI: <https://doi.org/10.1016/j.physa.2026.131361>

Why it matters to PETRA:

- recursively factorizes natural numbers down through their exponents;
- passes from prime-decorated trees to undecorated planar rooted trees;
- uses Dyck words as a one-to-one representation of those planar rooted trees;
- studies dictionary growth, structural reuse, orientation, entropy,
  compressibility, rank-frequency behavior, mean-squared displacement, and
  cross-correlation over the resulting deterministic corpus.

The paper reports a dataset extending to `6.5 * 10^9` natural numbers and finds
sublinear dictionary growth together with strong structural reuse. These
observables are useful methodological references for PETRA research, but the
paper studies the arithmetic-generated sequence of undecorated planar rooted
trees rather than PETRA's canonical operator algebra.

This source is already part of PETRA's maintained novelty-boundary discussion
in `RELATED-WORK.md`.

### Physica A 686 (2026) methodological bundle — 17 Sep 2026

**Classification:** B — methodological inspiration corpus; C until each item is
individually assessed.

A nine-paper reading bundle was supplied during the PETRA v2.0.0 state-of-the-art
review. It is retained conceptually as a lateral methods library rather than
being promoted wholesale into `RELATED-WORK.md`.

Current bundle inventory:

1. Andrej Dobovisek, Ales Fajmut, "Symmetry-induced maximum entropy production
   in enzyme kinetics: A noether-type mechanism", *Physica A* 686 (2026),
   131366. DOI: <https://doi.org/10.1016/j.physa.2026.131366>
2. Leonid A. Bunimovich, Emilio N.M. Cirillo, Matteo Colangeli, Lamberto
   Rondoni, "Dynamics of the Kac Ring Model with switching scatterers",
   *Physica A* 686 (2026), 131347.
   DOI: <https://doi.org/10.1016/j.physa.2026.131347>
3. R.A. Dumer, D.R. da Costa, M. Godoy, "Universality of self-organized phase
   transitions in driven three-dimensional magnetic systems with competing
   dynamics", *Physica A* 686 (2026), 131359.
   DOI: <https://doi.org/10.1016/j.physa.2026.131359>
4. Linda Albanese et al., "Serial vs parallel recall in the
   Blume-Every-Griffiths neural networks", *Physica A* 686 (2026), 131338.
   DOI: <https://doi.org/10.1016/j.physa.2026.131338>
5. Tal Halevi et al., "Self-attention vector output similarities reveal how
   machines pay attention", *Physica A* 686 (2026), 131363.
   DOI: <https://doi.org/10.1016/j.physa.2026.131363>
6. Phil Duxbury, Carlile Lavor, Luiz Leduino de Salles-Neto, "A continuous
   nonlinear optimization perspective on the Spin Glass Problem",
   *Physica A* 686 (2026), 131356.
   DOI: <https://doi.org/10.1016/j.physa.2026.131356>
7. P.F. Dias, F.M. Zimmer, N.G. Fytas, M. Schmidt, "Competing ferromagnetic and
   antiferromagnetic phases on the frustrated Ising honeycomb lattice",
   *Physica A* 686 (2026), 131321.
   DOI: <https://doi.org/10.1016/j.physa.2026.131321>
8. Daniel Borin, Matheus Rolim Sales, Edson Denis Leonel, Diego Fregolent Mendes
   de Oliveira, "On the dynamics of the q-Tsallis Gauss Iterated Map",
   *Physica A* 686 (2026), 131352.
   DOI: <https://doi.org/10.1016/j.physa.2026.131352>
9. Ronit D. Gross, Yanir Harel, Ido Kanter, "Translation entropy: A statistical
   framework for evaluating translation systems", *Physica A* 686 (2026),
   131320. DOI: <https://doi.org/10.1016/j.physa.2026.131320>

These papers are not asserted to be PETRA prior art. They are candidates for
method transfer: entropy-based observables, symmetry arguments, dynamical
regimes, phase-transition language, optimization views, representation
similarity, and statistical-mechanics framing may inspire bounded PETRA
experiments when a concrete research question justifies the transfer.

## Promotion rule

The maintained workflow is:

```text
discover -> classify -> inspect -> extract method/claim -> compare with PETRA
         -> run bounded experiment if justified -> verify -> promote only if earned
```

A source moves from methodological inspiration to direct related work only when
its substantive overlap with PETRA is documented. A method moves from
inspiration to PETRA research practice only after its assumptions are checked
against PETRA's data and semantics.

Nothing in this register modifies canonical PETRA behavior.