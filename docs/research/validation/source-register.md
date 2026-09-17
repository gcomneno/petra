# PETRA Phase 6 — external mathematical validation source register

Status: **Phase 6 working source register** for issue #293 under programme #276.

This register records external sources used to classify the provenance of PETRA's research theory. Inclusion of a source does **not** by itself establish equivalence with a PETRA theorem; convention mismatches are recorded explicitly.

## Source quality labels

- **PRIMARY** — original research article establishing the cited result or construction.
- **SURVEY** — survey / tutorial synthesizing prior literature.
- **MODERN REFERENCE** — recent research/reference source useful for terminology and a current statement of known results.
- **REFERENCE / SOFTWARE MANUAL** — implementation/reference documentation; useful for terminology and representation, not novelty.
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

This is **not yet sufficient** to validate PETRA's exact claim that the finite-unordered-multiset carrier is the initial algebra for the finite-multiset endofunctor on `Set`.

A primary or textbook-quality source specific enough to the finite-multiset functor is still required.

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

# Sources still required

The following areas remain deliberately **TO VERIFY** before Phase 6 can close:

1. a primary / textbook-grade source for the exact finite-multiset functor initial-algebra statement;
2. universal-algebra references for congruence, quotient, kernel congruence and first-isomorphism-style factorization in the exact signature used;
3. term-rewriting / trace / concurrency literature close enough to PETRA's witnessed-edit commutation to support a precise comparison;
4. literature on leaf-add/delete or rooted-subtree-reduction metrics close enough to test whether PETRA's exact common-reduct distance formula is already known in equivalent form;
5. literature sufficient to assess the global PETRA edit-graph automorphism questions;
6. dedicated novelty review for any PETRA-specific theorem candidate.

No absence from this initial register is evidence of novelty.
