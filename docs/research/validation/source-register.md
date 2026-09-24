# PETRA Phase 6 — external mathematical validation source register

Status: **Phase 6 working source register** for issue #293 under programme #276.

This register records external sources used to classify the provenance of PETRA's research theory. Inclusion of a source does **not** by itself establish equivalence with a PETRA theorem; convention mismatches are recorded explicitly.

## Source quality labels

- **PRIMARY** — original research article establishing the cited result or construction.
- **SURVEY** — survey / tutorial synthesizing prior literature.
- **MODERN REFERENCE** — recent research/reference source useful for terminology and a current statement of known results.
- **REFERENCE / SOFTWARE MANUAL** — implementation/reference documentation; useful for terminology and representation, not novelty.
- **TEXTBOOK / MONOGRAPH** — book-length reference establishing standard theory at textbook/reference level.
- **SECONDARY INDEX** — bibliographic/index source used only to locate or cross-check primary literature.

---

## S1 — Bartholdi & Diaconis, Pólya trees

**Bibliographic identity**

Laurent Bartholdi and Persi Diaconis, *An algorithm for uniform generation of unlabeled (Pólya) trees*, Forum of Mathematics, Sigma (2026).

Stable URL / DOI:

- https://doi.org/10.1017/fms.2026.10218

Type: **PRIMARY**.

This recent primary research article also serves as a useful modern reference for current Pólya-tree terminology and statements.

### Supports / limits

The paper explicitly treats **Pólya trees as rooted unlabeled trees** and gives the standard enumeration

```text
1, 1, 2, 4, 9, 20, 48, 115, 286, 719, ...
```

for sizes 1 through 10. It also gives the recursive root-subtree viewpoint and a rooted-tree automorphism decomposition.

For PETRA this supports the classification:

```text
P ::= Node(M_f(P))
```

as the standard rooted unlabeled / non-plane tree carrier rather than a novel carrier class.

The paper also states a recursive automorphism-group decomposition in terms of automorphisms of root subtrees and permutations of isomorphic copies, matching the structural form used in PETRA Phase 5.

### Convention mismatch

The paper studies the classical combinatorial class and probabilistic generation. It does **not** establish PETRA's edit algebra, common-reduct distance theorem, witnessed path presentation, or PETRA-specific global edit graph.

---

## S2 — Sage rooted unordered trees reference

**Bibliographic identity**

SageMath reference manual, *Rooted (unordered) trees*.

Stable URL:

- https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/rooted_tree.html

Type: **REFERENCE / SOFTWARE MANUAL**.

### Supports / limits

The reference describes an unordered rooted tree inductively as a **multiset of unordered rooted trees** and explicitly notes that sibling order is not significant.

This is useful corroboration for PETRA's carrier language:

```text
node = finite multiset of child trees
```

and for the distinction between unordered and ordered rooted trees.

### Convention mismatch

This is documentation rather than primary mathematical literature and is therefore not sufficient for novelty or priority claims.

---

## S3 — Matula 1968

**Bibliographic identity**

D. W. Matula, *A natural rooted tree enumeration by prime factorization*, SIAM Review 10 (1968), p. 273.

Stable bibliographic URL:

- https://www.jstor.org/stable/2027327

Type: **PRIMARY**.

### Supports / limits

Matula gives a rooted-tree enumeration based on prime factorization. This is direct prior art for recursive prime/factorization encodings of rooted trees.

For PETRA, the historical arithmetic reading must therefore be treated as an **interpretation / encoding tradition with clear prior art**, not as a novel identification of rooted-tree structure with prime factorization.

### Convention mismatch

PETRA's current research carrier is shape-first and does not define forms by arithmetic. The source validates an external encoding relationship, not PETRA's intrinsic edit algebra.

---

## S4 — Göbel 1980

**Bibliographic identity**

F. Göbel, *On a 1-1-correspondence between rooted trees and natural numbers*, Journal of Combinatorial Theory, Series B 29(1) (1980), 141–143.

DOI:

- https://doi.org/10.1016/0095-8956(80)90049-0

Type: **PRIMARY**.

### Supports / limits

Göbel explicitly establishes a one-to-one correspondence between rooted trees and natural numbers.

This reinforces the Phase-6 boundary:

```text
rooted tree <-> natural-number / prime-factorization correspondence
```

is known mathematics predating PETRA.

### Convention mismatch

The correspondence is an encoding/bijection. It does not imply that arithmetic is intrinsic to the rooted-tree carrier, and it does not establish PETRA's ADD/REMOVE theory.

---

## S5 — Deutsch 2012, rooted-tree statistics from Matula numbers

**Bibliographic identity**

Emeric Deutsch, *Rooted tree statistics from Matula numbers*, Discrete Applied Mathematics 160(15) (2012), 2314–2322.

DOI:

- https://doi.org/10.1016/j.dam.2012.05.012

Type: **PRIMARY**.

### Supports / limits

The paper studies standard rooted-tree statistics obtained from Matula numbers. It is relevant prior literature for statistics such as size/depth and related rooted-tree observables.

### Convention mismatch

PETRA Phase 5's specific Lipschitz results are statements about **PETRA's restricted leaf ADD/REMOVE edit metric**. The existence of classical rooted-tree statistics does not by itself establish those metric bounds.

---

## S6 — Colbourn & Booth 1981, automorphisms

**Bibliographic identity**

Charles J. Colbourn and Kellogg S. Booth, *Linear Time Automorphism Algorithms for Trees, Interval Graphs, and Planar Graphs*, SIAM Journal on Computing 10(1) (1981), 203–225.

DOI:

- https://doi.org/10.1137/0210015

Type: **PRIMARY**.

### Supports / limits

The paper develops tree automorphism algorithms, including automorphism partitions / orbits and generators. Modern sources citing it state the rooted-tree orbit criterion and recursive decomposition into subtree automorphisms and permutations of isomorphic child subtrees.

For PETRA this means the following are **classical rooted-tree automorphism mathematics**, not candidate novelty:

- occurrence orbits under a rooted-tree automorphism group;
- recursive decomposition by isomorphic child classes;
- automorphism counting from subtree automorphisms and symmetric permutations.

### Convention mismatch

PETRA-specific consequences such as the relationship between these orbits and witnessed ADD/REMOVE edit classes, and constraints on automorphisms of the **global PETRA edit graph**, require separate analysis.

---

## S7 — Zhang, Statman & Shasha 1992, unordered tree edit distance

**Bibliographic identity**

Kaizhong Zhang, Rick Statman and Dennis Shasha, *On the editing distance between unordered labeled trees*, Information Processing Letters 42(3) (1992), 133–139.

DOI:

- https://doi.org/10.1016/0020-0190(92)90136-J

Type: **PRIMARY**.

### Supports / limits

This is established prior literature for edit distance on **unordered labeled trees**.

It establishes that unordered tree edit distance is a classical problem family and studies computational complexity under its edit-operation definitions.

### Critical convention mismatch

PETRA elementary edits are deliberately narrower:

```text
ADD  = attach one fresh zero-child node
REMOVE = delete one non-root zero-child node
```

Classical tree edit distance commonly includes more general insert/delete semantics and labels. Therefore PETRA's metric must **not** be identified with classical TED merely because both act on rooted trees.

Any equivalence or specialization claim requires an explicit operation-by-operation theorem.

---

## S8 — Bille 2005 tree-edit-distance survey

**Bibliographic identity**

Philip Bille, *A survey on tree edit distance and related problems*, Theoretical Computer Science 337 (2005), 217–239.

DOI:

- https://doi.org/10.1016/j.tcs.2004.12.030

Type: **SURVEY**.

### Supports / limits

The survey confirms the broad classical tree-edit-distance framework based on local deletion, insertion and relabeling operations and reviews related distance/inclusion/alignment problems.

Use it primarily to map terminology and locate primary sources.

### Convention mismatch

As with S7, PETRA's leaf-only edits form a restricted system. Results about generic TED cannot be imported without checking hypotheses.

---

## S9 — modern rooted-tree automorphism statement in Bartholdi & Diaconis

Same paper as S1; highlighted separately because it explicitly states a recursive decomposition of the rooted-tree automorphism group:

```text
Aut(T)
= (product_i Aut(T_i)) semidirect (product_C S_C)
```

where equal-isomorphism root-subtree classes may be permuted.

This is essentially the structural decomposition proved internally in PETRA Phase 5, so PETRA should classify that decomposition as **known mathematics specialized to the PETRA carrier**.

---

## S10 — generic initial-algebra orientation source

**Bibliographic identity**

nLab, *initial algebra of an endofunctor*.

Stable URL:

- https://ncatlab.org/nlab/show/initial%2Balgebra%2Bof%2Ban%2Bendofunctor

Type: **SECONDARY / ORIENTATION REFERENCE**.

### Supports / limits

This source gives the standard conceptual relation between recursively generated datatypes and initial algebras, with finite-tree examples for polynomial functors.

### Validation status

This source by itself is **not sufficient** to validate PETRA's exact finite-multiset initial-algebra claim. That gap is now resolved separately by S14, which gives a textbook-grade bag-functor statement matching the PETRA carrier.

---

## S11 — Otter 1948, enumeration of rooted trees

**Bibliographic identity**

Richard Otter, *The Number of Trees*, Annals of Mathematics, Second Series 49(3) (1948), 583–599.

Stable DOI:

- https://doi.org/10.2307/1969046

Type: **PRIMARY**.

### Supports / limits

Otter is a classical primary source for enumeration of finite trees and rooted trees. It supplies a direct historical anchor for the rooted-tree enumeration tradition cited in the validation matrix, rather than relying only on modern references or sequence indexes.

For PETRA it supports the prior-art boundary that enumeration of the classical rooted-tree carrier is established mathematics and predates PETRA.

### Convention mismatch

Otter's enumeration theory does not establish PETRA's leaf-only edit algebra, interpretation theory, witnessed-path presentation, or PETRA-specific metric results.

---

## S12 — Selkow 1977, leaf-restricted tree editing

**Bibliographic identity**

Stanley M. Selkow, *The Tree-to-Tree Editing Problem*, Information Processing Letters 6(6) (1977), 184–186.

DOI:

- https://doi.org/10.1016/0020-0190(77)90064-3

Type: **PRIMARY**.

### Supports / limits

Selkow's original problem is formulated for labeled ordered rooted trees. Its edit system is an early direct source for the restriction that insertion and deletion operate at leaves. Later literature refers to this family as Selkow distance / top-down edit distance / degree-1 or 1-degree edit distance.

This establishes clear prior art for the elementary operation shape:

```text
leaf insertion
leaf deletion
```

PETRA specializes this family by using an unlabeled unordered carrier, omitting relabeling, and assigning unit cost to elementary ADD/REMOVE.

### Convention mismatch

Selkow's original carrier is ordered and labeled. PETRA forms are unlabeled rooted non-plane trees modulo rooted-tree isomorphism. The source supports the operation-family prior-art classification but does not by itself establish equality of the resulting quotient metrics or PETRA's maximum-common-reduct formula.

---

## S13 — Šestáková, Guth & Janoušek, modern 1-degree terminology

**Bibliographic identity**

Eliška Šestáková, Ondřej Guth and Jan Janoušek, *Inexact tree pattern matching with 1-degree edit distance using finite automata*, Discrete Applied Mathematics (2023).

Stable publisher page:

- https://www.sciencedirect.com/science/article/abs/pii/S0166218X23000057

Type: **PRIMARY**.

### Supports / limits

The paper explicitly describes 1-degree edit distance using three elementary operations:

```text
node relabel
leaf insert
leaf delete
```

and cites Selkow 1977 as the originating reference. This provides a modern confirmation that leaf-only insertion/deletion is an established named edit-distance family.

### Convention mismatch

The paper works with labeled ordered trees and pattern matching. PETRA removes labels, relabeling, and intrinsic sibling order. It supports specialization/provenance, not literal metric identity.

---


## S14 — Adámek, Milius & Moss 2025, bag functor initial algebra

**Bibliographic identity**

Jiří Adámek, Stefan Milius and Lawrence S. Moss, *Initial Algebras and Terminal Coalgebras: The Theory of Fixed Points of Functors*, Cambridge University Press, 2025.

Stable publisher page:

- https://www.cambridge.org/core/books/initial-algebras-and-terminal-coalgebras/5D35C77FF1C940558D6D09B0E8BBB9A6

Relevant material:

- Chapter 3, finitary iteration;
- Example 3.2.10, bag functor.

Type: **TEXTBOOK / MONOGRAPH**.

### Supports / limits

The book defines the bag functor

```text
B : Set -> Set
```

where `B(X)` is the set of finite bags / finite multisets over `X`, and maps are pushed forward by summing multiplicities along fibres.

It then identifies the initial algebra of `B` with **all finite unordered trees**, with algebra structure given by joining the trees in a finite bag under a fresh common root, preserving multiplicities.

This is an operation-exact external match for PETRA's research carrier:

```text
P ::= Node(M_f(P))
```

when `M_f` is read as the finite-multiset / bag functor.

The empty bag gives the one-node tree, matching PETRA's zero-child form.

### Phase-6 consequence

The claim that PETRA's canonical carrier is the initial algebra of the finite-multiset functor is established mathematics, not a PETRA novelty candidate.

PETRA's notation and surrounding interpretation/edit theory remain project-specific.

---

## S15 — Burris & Sankappanavar, universal-algebra homomorphism theory

**Bibliographic identity**

Stanley Burris and H. P. Sankappanavar, *A Course in Universal Algebra*, Graduate Texts in Mathematics 78, Springer-Verlag, 1981; Millennium Edition available from the University of Waterloo.

Stable references:

- https://link.springer.com/book/9781461381327
- https://www.math.uwaterloo.ca/~snburris/htdocs/UALG/univ-algebra.pdf

Type: **TEXTBOOK / MONOGRAPH**.

### Supports / limits

The text gives the standard universal-algebra results needed for PETRA's quotient comparison, including:

- kernel of a homomorphism is a congruence (Theorem 6.8 in the Millennium Edition);
- quotient algebras by congruences;
- natural quotient maps as homomorphisms;
- Homomorphism Theorem / first-isomorphism form `A / ker(h) ~= B` for a surjective homomorphism `h : A -> B` (Theorem 6.12).

Applied to the image of a general homomorphism, this yields the usual factorization:

```text
A / ker(h) ~= im(h).
```

### Convention bridge

PETRA's bag-algebra presentation is not literally a one-operation fixed-arity universal algebra. To use these theorems transparently, one may present the bag constructor by a finitary signature with one `n`-ary constructor for each `n >= 0`, quotienting by equations expressing invariance under permutations.

Under that presentation, PETRA structural congruence is ordinary compatibility with the constructor operations, so the standard quotient/kernel/homomorphism theorems apply.

These results do **not** imply any compatibility with PETRA's ADD/REMOVE transition system.

---

## S16 — Sharifi, free category on a directed graph

**Bibliographic identity**

Romyar Sharifi, *Homological Algebra — Chapter 1: Category Theory*, Definition 1.1.8.

Stable reference:

- https://www.math.ucla.edu/~sharifi/notes/homalg-ch01.html

Type: **REFERENCE / LECTURE NOTES**.

### Supports / limits

The notes define the category freely generated by a directed graph with vertices as objects, finite composable edge words as morphisms, the empty word as identity, and concatenation as composition.

This is exactly the generic construction used by PETRA witnessed edit paths over the witnessed edit graph.

### Phase-6 consequence

The statement that witnessed edit paths form the free category on `W_P` is established category theory specialized to PETRA's witnessed graph.

---

## S17 — Brown, free groupoid on a graph

**Bibliographic identity**

Ronald Brown, *Topology and Groupoids*, section on free groupoids.

Stable reference:

- https://groupoids.org.uk/pdffiles/rbrsbookb-e231109.pdf

Type: **TEXTBOOK / MONOGRAPH**.

### Supports / limits

Brown defines the free groupoid on a graph by the usual universal property. Its morphisms are represented by paths in graph edges together with formal inverse edges, modulo elementary reductions cancelling an edge immediately followed by its inverse, or conversely.

This matches PETRA's generic inverse-cancellation construction once the witnessed edit graph is regarded together with its reverse-edge involution.

### Convention boundary

The free-groupoid construction validates inverse cancellation only. It does **not** supply PETRA's additional commutation relations for independent edits.

---

## S18 — Aalbersberg & Rozenberg 1988, trace theory

**Bibliographic identity**

IJsbrand Jan Aalbersberg and Grzegorz Rozenberg, *Theory of traces*, Theoretical Computer Science 60(1) (1988), 1–82.

Stable DOI:

- https://doi.org/10.1016/0304-3975(88)90051-5

Type: **PRIMARY**.

### Supports / limits

The paper presents trace theory as a theory of partial commutativity for concurrent systems and explicitly notes that the theory originated with A. Mazurkiewicz in 1977. In the standard trace setting, one fixes an alphabet and an independence / partial-commutation relation, and words are identified by commuting independent letters.

Thus the generic pattern `... a b ... ~= ... b a ...` for independent actions is established prior art.

### Critical mismatch with PETRA

PETRA witnessed edits are not obviously letters of one fixed global alphabet with one fixed state-independent independence relation. Witnesses are typed by source state and occurrence, and after one edit the residual witness for the other edit may change.

Therefore PETRA's local commuting-square relation is related to trace theory but is not currently identified with a trace monoid.

---

## S19 — Diekert & Muscholl, modern trace-theory reference

**Bibliographic identity**

Volker Diekert and Anca Muscholl, *Trace Theory*, Encyclopedia of Parallel Computing.

Stable reference:

- https://doi.org/10.1007/978-0-387-09766-4_491

Type: **MODERN REFERENCE**.

### Supports / limits

The reference characterizes traces as elements of a free partially commutative monoid: sequences of actions modulo equations `ab = ba` for pairs in a prescribed independence relation.

It is useful for fixing modern terminology around independence and partial commutation.

### Convention mismatch

As with S18, the standard trace-monoid setup assumes a fixed action alphabet and fixed independence relation. PETRA's state-dependent witnessed system requires a more general categorical / rewriting comparison before any trace-monoid identification.

---

## S20 — Melliès 2002, axiomatic residual theory

**Bibliographic identity**

Paul-André Melliès, *Axiomatic Rewriting Theory VI: Residual Theory Revisited*, in RTA 2002, Lecture Notes in Computer Science 2378, pp. 24–50.

DOI:

- https://doi.org/10.1007/3-540-45610-4_4

Type: **PRIMARY**.

### Supports / limits

Melliès describes residual theory as the algebraic theory of confluence for the lambda calculus and, more generally, conflict-free rewriting systems. The paper explicitly discusses Lévy-style **permutation equivalence between rewriting paths** and residual-theoretic confluence diagrams.

This is a substantially closer external framework for PETRA's source-dependent witnessed edits than fixed-alphabet trace monoids.

### Convention boundary

The source does not establish that PETRA satisfies the axioms of Melliès' residual structures. PETRA's exact witness transport, multiplicity handling, independence criterion, and completeness claim must therefore be checked separately.

---

## S21 — Bruggink 2003, residuals in higher-order rewriting

**Bibliographic identity**

H. J. Sander Bruggink, *Residuals in Higher-Order Rewriting*, in RTA 2003, Lecture Notes in Computer Science 2706, pp. 123–137.

Stable proceedings reference:

- https://link.springer.com/book/10.1007/3-540-44881-0

Type: **PRIMARY**.

### Supports / limits

The work studies residuals in an explicit rewriting formalism, defines reductions by proof terms that witness rewriting steps, and constructs a residual operator. It also connects the resulting residual system with confluence and permutation equivalence of reductions.

The use of witnessed reductions and a residual operator makes this source structurally relevant to PETRA's residualized second edit after one witnessed edit has occurred.

### Convention boundary

The formalism is higher-order pattern rewriting, not PETRA's unordered rooted-tree leaf editing. The existence of residual machinery in that setting does not by itself prove that PETRA forms a residual system.

---

## S22 — Glauert & Khasidashvili 1996, deterministic residual structures

**Bibliographic identity**

John R. W. Glauert and Zurab Khasidashvili, *Relative Normalization in Deterministic Residual Structures*, CAAP '96, Lecture Notes in Computer Science 1059, pp. 180–195.

DOI:

- https://doi.org/10.1007/3-540-61064-2_37

Type: **PRIMARY**.

### Supports / limits

The paper defines Stable Deterministic Residual Structures as abstract reduction systems equipped with axiomatized residual relations, intended to model orthogonal / conflict-free rewriting behaviour.

For PETRA this supplies a useful validation target: if a residual operator on witnessed edits is defined, its axioms should be checked explicitly rather than inferred from the existence of commuting squares.

### Convention boundary

No current PETRA Phase-6 result verifies the full SDRS axiom set. PETRA must therefore not yet be called a Stable Deterministic Residual Structure.

---

# Sources still required

The following areas remain deliberately **TO VERIFY** before Phase 6 can close:

1. an axiom-by-axiom determination of whether PETRA witnessed edits form a residual structure in the Melliès / Glauert–Khasidashvili sense;
2. a source-exact comparison for PETRA's common-REMOVE-reduct distance formula and REMOVE*ADD* geodesic normal form inside the Selkow / 1-degree leaf-edit family;
3. literature sufficient to assess the global PETRA edit-graph automorphism questions;
4. dedicated novelty review for any PETRA-specific theorem candidate.

No absence from this initial register is evidence of novelty.
