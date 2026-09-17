# PETRA Related Work

## Status

This document is the maintained related-work survey for PETRA research context.
It records how PETRA relates to prior mathematics and computer-science
literature and constrains novelty claims accordingly.

It is **not normative for PETRA semantics**. The sole normative semantic source
remains [`../reference/SPEC.md`](../reference/SPEC.md).

The survey is deliberately conservative: PETRA does not claim novelty for a
component merely because PETRA combines it with other components in a new
system.

## 1. Integer-to-tree encodings: Matula and Göbel

The closest historical predecessor to PETRA's arithmetic ancestry is the
Matula-Göbel correspondence between positive integers and rooted trees.

Matula's 1968 construction gives a recursive rooted-tree enumeration by prime
factorization. Göbel later obtained the same one-to-one correspondence
independently. Subsequent work studies tree invariants through Matula numbers
and develops the combinatorics of the correspondence.

This prior work means PETRA does **not** claim novelty for either of the
following ideas in isolation:

- recursively decomposing natural numbers through prime factorization; or
- associating that recursive decomposition with rooted trees.

The relevant distinction is PETRA's architectural direction. PETRA is
shape-first: prime identities, represented integer values, factorization
provenance, and persistent node identities are not part of canonical shape
identity. Numeric projection is optional and derived. Consequently PETRA is
not presented as another bijective integer encoding.

A useful way to state the boundary is:

```text
Matula-Göbel tradition:
integer -> recursive prime-factor structure -> rooted tree

PETRA:
canonical recursive shape -> optional numeric interpretation/projection
```

The distinction is material because the PETRA abstraction is intentionally
many-to-one when viewed from integers: distinct integers can induce the same
canonical shape once concrete prime identities are forgotten.

### Recent recursive-factorization work

Contucci, Giberti, Osabutey, and Vernia (2026) study a deterministic encoding
of the natural numbers obtained by recursively factorizing exponents, yielding
planar rooted trees / Dyck words and then measuring statistical properties of
the resulting corpus. This is especially close to the arithmetic motivation
behind PETRA and therefore must be treated as direct related work.

PETRA's current research question is different: rather than asking what
statistical structure is present in the integer-generated tree sequence,
PETRA asks what algebraic and geometric structure remains after arithmetic
labels are intentionally abstracted away and canonical shapes become the
primary objects.

## 2. Terms, trees, and rewriting

Term rewriting systems provide a mature formal setting for recursive
term-shaped objects, positional addressing, local replacement, normal forms,
termination, and confluence. Standard presentations model a position in a term
as a finite sequence of natural numbers and define rewriting by replacing the
subterm selected at a position.

Therefore PETRA does **not** claim novelty for:

- representing recursive syntax as trees;
- selecting a subobject by a positional path;
- replacing a selected subobject locally; or
- studying canonical or normal forms of recursively defined objects.

PETRA's narrower contribution candidate is a domain-specific canonical rewrite
system over prime-exponent-shaped structures. The canonical runtime defines a
fixed grammar together with the four structural operators `SPROUT`, `SHED`,
`GRAFT`, and `PRUNE`, deterministic target resolution, state-scoped addresses,
typed outcomes, witnesses, and stable failure reasons.

This should not be confused with a claim that PETRA constitutes a new general
term-rewriting theory. A useful future formalization task is instead to express
PETRA in standard rewriting language and determine which classical properties
hold: termination for selected subsystems, confluence, critical-pair behavior,
normal forms, reachability, and presentation by generators and relations.

## 3. Tree algebras and rooted-tree operators

Rooted trees already support substantial algebraic structures in the
literature. In particular, work around rooted-tree Hopf algebras uses growth,
grafting, and pruning operators. Hoffman defines growth and pruning operators
on the vector space spanned by rooted trees and studies their algebraic
relations; related rooted-tree Hopf-algebra constructions use grafting as a
fundamental operation.

Accordingly, PETRA does **not** claim novelty for the words or generic concepts
"grafting", "pruning", "growth", or algebraic operations on rooted trees.

PETRA's `GRAFT` and `PRUNE` are domain-specific canonical rewrite operators
with semantics fixed by the PETRA specification. They should not be identified
with grafting/pruning operators from rooted-tree Hopf algebras merely because
the terminology overlaps.

The term "algebra" in PETRA should therefore be strengthened by explicit
mathematics rather than by terminology alone. Natural formal questions are:

- What is the carrier of the PETRA algebra?
- Which PETRA operations are total and which are partial?
- Which pairs are partial inverses?
- Which invariants are preserved or changed monotonically?
- Is there a useful grading by node count, depth, or another structural
  quantity?
- Can the operator system be characterized by generators and relations?
- What are the automorphisms or symmetries of the resulting shape space?

## 4. Tree edit distance and Resolver

Classical tree-edit-distance literature studies the minimum-cost sequence of
insertions, deletions, and relabelings needed to transform one tree into
another. Zhang and Shasha (1989) give a foundational algorithm for ordered
labeled trees. Work on unordered labeled trees shows that the computational
picture changes substantially and includes NP-complete cases.

Therefore Resolver does **not** claim novelty merely for:

- searching for a shortest edit path between trees; or
- defining structural dissimilarity through edit operations.

The PETRA-specific question is narrower: what geometry is induced when the
allowed edges are exactly PETRA/Resolver structural operations over canonical
PETRA shapes?

That question leads to concrete mathematical obligations:

1. determine whether the induced distance is a metric, pseudometric, or only a
   directed shortest-path cost;
2. determine connectivity of the canonical shape graph;
3. characterize operator inverses and edge symmetry;
4. establish or refute the triangle inequality for each proposed distance;
5. analyze shortest-path complexity under the PETRA operator set;
6. compare PETRA-induced distance empirically and theoretically with classical
   tree-edit distances.

Until these properties are proved, Resolver results should be described as
computational results over the implemented PETRA shape graph, not as a new
universal tree metric.

## 5. The abstraction boundary that may be distinctive

The individual ingredients above all have substantial precedent. PETRA's
possible distinctive contribution therefore lies in the particular abstraction
boundary and the system built on top of it, not in any one ingredient alone.

### 5.1 Shape-first quotient abstraction

PETRA intentionally removes concrete prime identity, numeric magnitude,
factorization provenance, rewrite history, and persistent node identity from
canonical structure. Viewed from an external integer projection this naturally
suggests an equivalence relation

```text
n ~ m  iff  shape(n) = shape(m)
```

whenever a projection from integers to PETRA shapes is defined. This quotient
view is a research interpretation, not part of canonical runtime semantics.
It provides a precise place to investigate what arithmetic information survives
and what is intentionally forgotten.

### 5.2 State-scoped positional coordinates

PETRA root ranks and addresses are coordinates in one canonical shape state,
not persistent labels attached to enduring nodes. Successful rewrites can
renumber or retarget those coordinates. This design makes structural identity
depend on the current canonical state rather than object allocation or numeric
labels.

### 5.3 A fixed canonical operator system

`SPROUT`, `SHED`, `GRAFT`, and `PRUNE` define a small, explicit structural
vocabulary. A substantive originality claim would require showing that this
operator set generates or characterizes a mathematically interesting class of
transformations, not merely observing that four named operations exist.

### 5.4 Witnessed deterministic rewriting

A successful PETRA operation returns more than an after-shape: the runtime
records typed result information, resolved targets, a witness, and address
effects. This combination may be relevant from a software-verifiability
perspective, but it should be compared with provenance, proof-object, and
certified-rewriting literature before any broad novelty claim is made.

## 6. Claims PETRA does not make

PETRA does not currently claim to have invented:

- recursive prime-factor encodings of natural numbers;
- bijections or correspondences between natural numbers and rooted trees;
- recursively defined tree terms;
- positional addressing of tree nodes or subterms;
- local term/tree rewriting;
- canonical or normal forms in general;
- grafting or pruning as generic tree operations;
- algebraic structures on rooted trees;
- tree edit distance;
- shortest-path search over edit graphs; or
- structural metrics on trees in general.

Any future publication should formulate novelty at a more specific level and
should distinguish implemented engineering properties, experimental evidence,
proved mathematical results, and conjectures.

## 7. Current research position

The strongest defensible description at this stage is:

> PETRA is a shape-first canonical structural system for recursive
> prime-exponent forms. It deliberately quotients away concrete arithmetic
> identities and defines deterministic, witnessed structural rewrites over the
> resulting canonical shapes. Its relationship to classical rooted-tree
> encodings, term rewriting, rooted-tree algebras, and tree-edit geometry is an
> explicit part of the research program rather than a claim that those fields
> are new.

The next theoretical milestone is to define the PETRA shape space and operator
system in standard mathematical language, then prove structural properties of
that system that distinguish it from the surrounding literature.

## References

1. D. W. Matula, "A Natural Rooted Tree Enumeration by Prime Factorization",
   *SIAM Review* 10 (1968), p. 273.
   <https://www.jstor.org/stable/2027327>
2. F. Göbel, "On a 1-1-correspondence between rooted trees and natural
   numbers", *Journal of Combinatorial Theory, Series B* 29 (1980), 141-143.
   DOI: <https://doi.org/10.1016/0095-8956(80)90049-0>
3. I. Gutman and A. Ivić, "On Matula numbers", *Discrete Mathematics* 150
   (1996), 131-142. DOI: <https://doi.org/10.1016/0012-365X(95)00182-V>
4. E. Deutsch, "Rooted tree statistics from Matula numbers", *Discrete Applied
   Mathematics* 160 (2012), 2314-2322.
   DOI: <https://doi.org/10.1016/j.dam.2012.05.012>
5. P. Contucci, C. Giberti, G. Osabutey, and C. Vernia, "Statistical
   properties of the rooted-tree encoding of N", *Physica A* 686 (2026),
   131361. DOI: <https://doi.org/10.1016/j.physa.2026.131361>
6. F. Baader and T. Nipkow, *Term Rewriting and All That*, Cambridge University
   Press, 1998. <https://www.cambridge.org/core/books/term-rewriting-and-all-that/71768055278D0D698A9A91D0577E8CCF>
7. M. E. Hoffman, "Combinatorics of Rooted Trees and Hopf Algebras",
   *Transactions of the American Mathematical Society* 355 (2003), 3795-3811.
   Preprint: <https://arxiv.org/abs/math/0201253>
8. K. Zhang and D. Shasha, "Simple Fast Algorithms for the Editing Distance
   between Trees and Related Problems", *SIAM Journal on Computing* 18 (1989),
   1245-1262. DOI: <https://doi.org/10.1137/0218082>
9. K. Zhang, R. Statman, and D. Shasha, "On the editing distance between
   unordered labeled trees", *Information Processing Letters* 42 (1992),
   133-139. DOI: <https://doi.org/10.1016/0020-0190(92)90136-J>

## Maintenance rule

Add literature when it materially changes PETRA's novelty boundary, formal
positioning, or terminology. Prefer primary sources and stable DOI links.
Never convert a related-work observation into canonical PETRA semantics merely
by documenting it here; promotion requires the separate process defined by
`AGENTS.md` and the normative specification.