# PETRA Phase 6 — external mathematical validation matrix

Status: **working Phase 6 classification** for issue #293 under programme #276.

This document classifies the mathematical results developed in Phases 1–5 against external literature. It is a provenance / novelty-boundary document, not a replacement for PETRA's internal proofs.

## Classification vocabulary

- **KNOWN** — established mathematics directly matching the PETRA statement at the relevant level.
- **SPECIALIZED** — known mathematics specialized or reformulated in PETRA terminology / carrier.
- **PETRA-INTERNAL** — proved internally for PETRA, but external equivalence / novelty remains unresolved.
- **OPEN** — conjecture or unresolved theorem question.
- **BOUNDED** — computational evidence only.
- **TO-VERIFY** — literature comparison not yet strong enough to classify.

No row labeled `PETRA-INTERNAL` is a novelty claim.

---

## Validation matrix

| PETRA result family | Current classification | External basis | Validation note |
| --- | --- | --- | --- |
| Carrier as finite rooted unlabeled non-plane trees | **KNOWN** | Pólya-tree literature; Bartholdi–Diaconis 2026; standard rooted unordered tree references | PETRA's `Node(M_f(P))` describes the classical rooted unlabeled/non-plane tree class. |
| Root child collection as finite multiset; sibling order non-intrinsic | **KNOWN** | Pólya-tree recursive specification; rooted unordered tree references | This is standard structure of rooted unordered trees. |
| Enumeration `1,1,2,4,9,20,48,115,286,719,...` | **KNOWN** | Pólya/Otter tradition; modern Pólya-tree references; OEIS A000081 | PETRA bounded enumeration agrees with the classical Pólya-tree sequence. |
| Root / parent / connectedness / finiteness / acyclicity facts | **KNOWN** | elementary rooted-tree theory | These are standard consequences of the tree carrier, not PETRA novelty. |
| One-constructor zero-child formulation | **SPECIALIZED** | standard recursive rooted-tree representation | PETRA's exact presentation is a reformulation of the standard recursive carrier. |
| Prime-factorization / natural-number rooted-tree correspondence | **KNOWN** | Matula 1968; Göbel 1980 | Clear prior art. Arithmetic correspondence is interpretation/encoding, not PETRA novelty. |
| Structural rooted-tree statistics such as size/depth/profile/degree | **KNOWN** | classical rooted-tree literature; Matula-number statistics literature | The statistics themselves are standard. |
| `Aut(P)` recursive decomposition by child types and symmetric permutations | **KNOWN / SPECIALIZED** | Colbourn–Booth 1981; modern Pólya-tree automorphism statements | Same structural theorem is classical for rooted trees; PETRA notation specializes it. |
| Automorphism-count recurrence | **KNOWN / SPECIALIZED** | same automorphism decomposition | Immediate cardinality consequence of the classical decomposition. |
| Recursive rigidity criterion | **SPECIALIZED** | consequence of classical automorphism decomposition | PETRA proof is valid, but mathematical content follows from standard rooted-tree automorphism structure. |
| Target orbit iff same witnessed edit class | **PETRA-INTERNAL** | no exact external match recorded yet | Depends on PETRA's witnessed-edit definition; externally unclassified. |
| Same target orbit implies same unpointed successor | **PETRA-INTERNAL** | consequence of PETRA witness quotient | Internally proved; no novelty claim. |
| Converse: same successor implies same target orbit | **OPEN** | bounded search only | No counterexample through size 10; not a theorem. |
| `Z` unique degree-one vertex of PETRA edit graph | **PETRA-INTERNAL** | no exact external match recorded | Specific to PETRA leaf-edit graph as currently defined. |
| Global PETRA edit-graph automorphisms fix `Z` and preserve size layers | **PETRA-INTERNAL** | follows internally from graph theory + PETRA rank theorem | The generic graph-theory steps are standard; the characterization of this graph is PETRA-specific. |
| Global `Aut(E_P)` triviality | **OPEN** | none | Not proved and not externally validated. |
| Generic unordered tree edit distance as a field | **KNOWN** | Zhang–Statman–Shasha 1992; Bille 2005 | Strong prior art exists, but operation semantics differ from PETRA. |
| PETRA elementary ADD/REMOVE metric identical to classical TED | **NOT ESTABLISHED** | classical TED uses broader operations | Must not be claimed without an explicit equivalence theorem. |
| PETRA edit graph connectedness and size bipartition | **PETRA-INTERNAL / elementary** | generic graph consequences of ±1 grading | Internally direct; external novelty not assessed. |
| Exact PETRA distance `d(P,Q)=size(P)+size(Q)-2c(P,Q)` | **TO-VERIFY** | common-subtree / edit-distance literature relevant but not yet matched to PETRA's restricted edits | Internal proof stands; external equivalence and novelty remain unresolved. |
| Existence of REMOVE*ADD* geodesic through a maximum common reduct | **TO-VERIFY** | likely related to common-subtree/edit-script normal forms | Requires operation-exact comparison. |
| REMOVE reachability is a partial order | **PETRA-INTERNAL / elementary** | generic consequences of strict size decrease and reachability | Standard style of argument; exact poset is PETRA-specific. |
| REMOVE poset not a meet-semilattice | **PETRA-INTERNAL** | no exact external comparison yet | Explicit counterexample internally proved. No novelty claim. |
| Structural interpretation as recursive fold / homomorphism | **TO-VERIFY / likely SPECIALIZED** | generic initial-algebra literature | General idea is standard; exact finite-multiset-functor theorem needs stronger sourcing. |
| `(P,Node)` initial algebra for finite-multiset functor on `Set` | **TO-VERIFY** | generic initial-algebra references insufficiently specific so far | Keep internal theorem, but Phase 6 source not yet adequate. |
| Faithful structural interpretation iff injective | **SPECIALIZED / elementary** | direct definition-level consequence | No plausible novelty claim. |
| Kernel of structural interpretation is structural congruence | **TO-VERIFY / likely SPECIALIZED** | standard algebraic kernel-congruence pattern | Exact signature / functor formulation still needs source. |
| Quotient algebra iff structural congruence | **TO-VERIFY / likely SPECIALIZED** | standard universal-algebra quotient principle | Needs exact external reference. |
| First-isomorphism-style factorization through image | **TO-VERIFY / likely SPECIALIZED** | standard algebraic pattern | PETRA proof stands; external classification incomplete. |
| Arbitrary semantic kernel need not be structural | **PETRA-INTERNAL** | explicit PETRA counterexample | No external comparison yet. |
| Structural congruence does not imply REMOVE transition compatibility | **PETRA-INTERNAL** | explicit universal-congruence counterexample | Specific distinction in PETRA theory. |
| Witnessed edit paths form free category | **SPECIALIZED / standard construction** | generic free-category-on-a-graph mathematics | Exact PETRA witness graph is specific; categorical construction itself is standard. |
| Quotient by inverse cancellation is a groupoid | **SPECIALIZED / standard construction** | generic path groupoid / free groupoid pattern | Needs a primary/reference citation in later Phase 6 work. |
| Independent edits commute under PETRA's explicit criterion | **PETRA-INTERNAL** | trace/concurrency/rewriting analogues plausible | Exact comparison not yet sourced. |
| Reduced path need not be geodesic | **PETRA-INTERNAL** | explicit PETRA counterexample | No novelty claim. |
| Completeness of cancellation + independent commutation | **OPEN** | none | Explicitly unresolved. |
| Depth / leaf / root-degree / width / max-degree 1-Lipschitz under PETRA edits | **PETRA-INTERNAL** | standard statistics, PETRA-specific edit bound | Internal proofs direct; external novelty unresolved. |
| Degree-profile `L1 <= 3` one-step bound | **PETRA-INTERNAL** | no exact external match recorded | Sharp internally and bounded-corroborated. |
| Level-profile `L1 = 1` per edit | **PETRA-INTERNAL** | direct from PETRA leaf edit | No novelty claim. |
| Natural statistic tuple fails to classify forms | **KNOWN phenomenon / PETRA witness** | rooted-tree invariants generally non-complete | PETRA explicit witness is internal; non-completeness of coarse invariants is unsurprising and not candidate novelty. |

---

## High-confidence prior-art boundaries

### Carrier

PETRA's abstract carrier is not a new combinatorial species. A rooted unlabeled/non-plane tree is classically described recursively by a root carrying an unordered collection / multiset of rooted trees. Modern Pólya-tree literature uses precisely this class.

Therefore PETRA should say, at most:

```text
PETRA adopts the classical Pólya-tree carrier as its canonical shape domain.
```

It should **not** say:

```text
PETRA introduces a new class of recursive trees.
```

### Arithmetic correspondence

Matula (1968) and Göbel (1980) establish rooted-tree / natural-number correspondences based on prime factorization. Consequently the historical idea of reading recursive prime structure as a rooted tree is prior art.

PETRA's potentially distinctive contribution, if any, must lie elsewhere: for example in its shape-first abstraction boundary, intrinsic edit algebra, interpretation architecture, or specific meta-theory. Those possibilities remain unvalidated novelty candidates, not claims.

### Automorphisms

The recursive structure of rooted-tree automorphism groups — internal automorphisms of child subtrees together with permutations among isomorphic child copies — is classical. PETRA's Phase-5 group decomposition and cardinality recurrence should be cited as specialization/rederivation, not novelty.

### Tree edit distance

Tree edit distance is a mature literature. However, operation semantics matter critically. Classical insertion/deletion may reattach children and may include labels/relabeling, whereas PETRA's elementary operation inserts or removes only a leaf occurrence.

Therefore the safe Phase-6 statement is:

```text
PETRA defines a restricted rooted-unordered-tree edit metric related to,
but not yet identified with, classical tree edit distance.
```

---

## Candidate PETRA-specific theorem families requiring deeper search

The following currently deserve dedicated literature review because they are internally nontrivial but not externally classified:

1. exact distance via maximum common REMOVE reduct;
2. non-meet property of the REMOVE poset under the PETRA reduction relation;
3. exact relationship between edit-target automorphism orbits and unpointed successors;
4. automorphism group of the global PETRA edit graph;
5. completeness or incompleteness of the local witnessed-path presentation;
6. PETRA-specific Lipschitz/profile bounds under leaf-only edits;
7. structural-congruence versus edit-compatibility separation in this exact algebra;
8. exact universal-property formulation for the finite-multiset carrier.

No item in this list is called novel.

---

## Evidence already available internally

Bounded probes remain classified separately from literature:

- canonical rooted-tree enumeration through size 10;
- exact edit-geometry corroboration on bounded corpora;
- automorphism recurrence independently brute-force checked through size 8;
- target-orbit converse search with no counterexample through size 10;
- structural-statistic local formulas exhaustively checked through size 10.

These results support implementation/proof confidence but **do not establish external novelty or priority**.

---

## Phase-6 next research slices

The next source-driven work should proceed narrowly rather than attempting novelty review all at once:

1. **exact edit metric comparison** — PETRA leaf-only metric vs common-subtree / rooted-tree edit metrics;
2. **algebraic semantics validation** — finite-multiset initial algebra, congruences, quotients, kernels;
3. **rewrite/path comparison** — free groupoid, traces, commuting independent rewrites;
4. **global edit-graph literature** — reconstruction / automorphism questions;
5. only then, a dedicated **novelty candidate audit**.

Phase 7 remains blocked until this validation work is complete enough to support a normative decision.
