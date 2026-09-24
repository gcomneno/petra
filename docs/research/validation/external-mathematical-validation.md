# PETRA Phase 6 — external mathematical validation matrix

Status: **Phase 6 COMPLETE / provenance classification frozen** under programme #276.

This document classifies the mathematical results developed in Phases 1–5 against external literature. It is a provenance / novelty-boundary document, not a replacement for PETRA's internal proofs.

## Classification vocabulary

Each validation row uses exactly one status from this vocabulary:

- **KNOWN** — established mathematics directly matching the PETRA statement at the relevant level;
- **SPECIALIZED** — known mathematics specialized or reformulated in PETRA terminology / carrier;
- **PETRA-INTERNAL** — proved internally for PETRA, but external equivalence / novelty remains unresolved;
- **OPEN** — conjecture or unresolved theorem question;
- **BOUNDED** — computational evidence only;
- **TO-VERIFY** — literature comparison not yet strong enough to classify.

Qualifiers such as “elementary”, “likely standard”, or “not established” belong in the validation note, not in the status column.

No row labeled `PETRA-INTERNAL` is a novelty claim. No row labeled `TO-VERIFY` may be promoted merely because no contrary source was found.

---

## Validation matrix

| PETRA result family | Current classification | External basis | Validation note |
| --- | --- | --- | --- |
| Carrier as finite rooted unlabeled non-plane trees | **KNOWN** | Pólya-tree literature; Bartholdi–Diaconis 2026; standard rooted unordered tree references | PETRA's `Node(M_f(P))` describes the classical rooted unlabeled/non-plane tree class. |
| Root child collection as finite multiset; sibling order non-intrinsic | **KNOWN** | Pólya-tree recursive specification; rooted unordered tree references | This is standard structure of rooted unordered trees. |
| Enumeration `1,1,2,4,9,20,48,115,286,719,...` | **KNOWN** | Pólya/Otter tradition; Bartholdi–Diaconis 2026; OEIS A000081 | PETRA bounded enumeration agrees with the classical Pólya-tree sequence. |
| Root / parent / connectedness / finiteness / acyclicity facts | **KNOWN** | elementary rooted-tree theory | These are standard consequences of the tree carrier, not PETRA novelty. |
| One-constructor zero-child formulation | **SPECIALIZED** | standard recursive rooted-tree representation | PETRA's exact presentation is a reformulation of the standard recursive carrier. |
| Prime-factorization / natural-number rooted-tree correspondence | **KNOWN** | Matula 1968; Göbel 1980 | Clear prior art. Arithmetic correspondence is interpretation/encoding, not PETRA novelty. |
| Structural rooted-tree statistics such as size/depth/profile/degree | **KNOWN** | classical rooted-tree literature; Deutsch 2012; Bartholdi–Diaconis 2026 | The statistics themselves are standard. PETRA-specific edit bounds remain separate rows. |
| `Aut(P)` recursive decomposition by child types and symmetric permutations | **SPECIALIZED** | Colbourn–Booth 1981; Bartholdi–Diaconis 2026, Lemma 3.5 | The structural theorem is classical for rooted trees; PETRA notation specializes it. |
| Automorphism-count recurrence | **SPECIALIZED** | classical rooted-tree automorphism decomposition | Immediate cardinality consequence of the classical decomposition. |
| Recursive rigidity criterion | **SPECIALIZED** | consequence of classical automorphism decomposition | PETRA's criterion follows from the standard recursive automorphism structure. |
| Target orbit iff same witnessed edit class | **PETRA-INTERNAL** | PETRA witness definition; rooted-tree automorphism theory | Exact at witnessed-edge level by definition/proof in Phase 5. |
| Same target orbit implies same unpointed successor | **PETRA-INTERNAL** | consequence of PETRA witness quotient | Internally proved; no novelty claim. |
| Same unpointed ADD successor implies same target orbit | **SPECIALIZED** | Krasikov 1991 branch-interchange theorem + PETRA root-marker reduction | The classical pendant-attachment similarity theorem gives the unrooted result; a finite rigid marker attached at the distinguished root forces the resulting automorphism to be root-preserving. |
| Same unpointed REMOVE successor implies same target orbit | **SPECIALIZED** | Harary–Palmer / Kirkpatrick–Klawe–Corneil endvertex pseudosimilarity theorem + PETRA root-marker reduction | Removal-similar leaves of a tree are similar; the same marker reduction preserves PETRA's distinguished root. |
| `Z` unique degree-one vertex of PETRA edit graph | **PETRA-INTERNAL** | no exact external match recorded | Specific to PETRA leaf-edit graph as currently defined. |
| Global PETRA edit-graph automorphisms fix `Z` and preserve size layers | **SPECIALIZED** | generic graph automorphism distance invariance + PETRA rank theorem | Once `Z` is uniquely degree one, every graph automorphism fixes it and therefore preserves distance/rank. The PETRA-specific input is the rank formula `d(Z,P)=size(P)-1`. |
| Reconstruction from the set of lower neighbours | **PETRA-INTERNAL** | Kostochka–Nahvi–West–Zirlin 2022 clarifies the multiset/set distinction; explicit PETRA size-3 counterexample | False in general: the rooted 3-chain and the rooted 2-leaf star have the same singleton set of REMOVE predecessors, although their `rc1` multisets differ in multiplicity. |
| Global `Aut(E_P)` triviality | **OPEN** | lower-neighbour-set induction route is refuted by the size-3 collision | Global rigidity may still hold, but it cannot be proved by the proposed claim that every form is uniquely determined by its lower-neighbour set. |
| Generic unordered tree edit distance as a field | **KNOWN** | Zhang–Statman–Shasha 1992; Bille 2005 | Strong prior art exists, but unrestricted operation semantics differ from PETRA. |
| Leaf-restricted insertion/deletion as a tree-edit family | **KNOWN** | Selkow 1977; modern 1-degree edit-distance literature | Known as Selkow / top-down / degree-1 / 1-degree edit distance. |
| PETRA ADD/REMOVE operation family | **SPECIALIZED** | Selkow 1977; 1-degree literature | Unlabeled unordered unit-cost specialization with relabeling absent. |
| PETRA elementary operation system versus unrestricted classical TED | **KNOWN** | Zhang–Statman–Shasha 1992; Bille 2005; Selkow 1977 | The operation systems are not identical: unrestricted TED permits broader insertion/deletion semantics, whereas PETRA permits leaf ADD/REMOVE only. This row makes no claim about a closed-form relation between the resulting metrics. |
| PETRA edit graph connectedness and size bipartition | **PETRA-INTERNAL** | generic graph consequences of ±1 grading | Internally direct and elementary; external novelty is not assessed. |
| Exact PETRA distance `d(P,Q)=size(P)+size(Q)-2c(P,Q)` | **PETRA-INTERNAL** | Selkow/1-degree prior art; Kuboyama–Shin–Miyahara 2006 common-structure framework | Internal proof stands. Targeted comparison found broad known analogues but no operation-exact external theorem for PETRA's maximum common REMOVE reduct under all PETRA conventions. No novelty claim. |
| Existence of REMOVE*ADD* geodesic through a maximum common reduct | **PETRA-INTERNAL** | Selkow/1-degree leaf-edit family; general edit/common-structure duality | The theorem is internally proved for PETRA. No registered source states the exact normal form with PETRA's common-REMOVE-reduct and quotient conventions. No novelty claim. |
| REMOVE reachability is a partial order | **PETRA-INTERNAL** | generic consequences of strict size decrease and reachability | Standard style of argument; the exact poset is PETRA-specific. |
| REMOVE poset not a meet-semilattice | **PETRA-INTERNAL** | no exact external comparison yet | Explicit counterexample internally proved. No novelty claim. |
| Structural interpretation as recursive fold / homomorphism | **SPECIALIZED** | Adámek–Milius–Moss 2025, bag-functor initial algebra | The unique PETRA structural fold is the standard unique homomorphism out of the initial bag algebra, expressed in PETRA terminology. |
| `(P,Node)` initial algebra for finite-multiset functor on `Set` | **KNOWN** | Adámek–Milius–Moss 2025, Example 3.2.10 | The bag functor's initial algebra is explicitly all finite unordered trees with tree-tupling by finite bags; this matches PETRA's carrier. |
| Faithful structural interpretation iff injective | **SPECIALIZED** | direct definition-level consequence | Elementary specialization; no novelty claim. |
| Kernel of structural interpretation is structural congruence | **SPECIALIZED** | Burris–Sankappanavar, kernel-congruence theorem | Standard universal-algebra theorem after presenting the bag constructor as symmetric finitary operations. |
| Quotient algebra iff structural congruence | **SPECIALIZED** | Burris–Sankappanavar, quotient algebra theory | Standard quotient-congruence principle under the same presentation bridge. |
| First-isomorphism-style factorization through image | **SPECIALIZED** | Burris–Sankappanavar, Homomorphism Theorem | Standard `A/ker(h) ~= im(h)` factorization specialized to PETRA structural homomorphisms. |
| Arbitrary semantic kernel need not be structural | **PETRA-INTERNAL** | explicit PETRA counterexample | No external comparison yet. |
| Structural congruence does not imply REMOVE transition compatibility | **PETRA-INTERNAL** | explicit universal-congruence counterexample | Specific distinction in PETRA theory. |
| Witnessed edit paths form free category | **SPECIALIZED** | Sharifi free-category construction | PETRA's witnessed paths are the standard free category on the witnessed edit graph, specialized to PETRA edge semantics. |
| Quotient by inverse cancellation is a groupoid | **SPECIALIZED** | Brown, free groupoid on a graph | PETRA's inverse-cancellation quotient is the standard free-groupoid construction before adding any commutation relations. |
| Generic residual transport / permutation equivalence of rewriting steps | **KNOWN** | Melliès 2002; Bruggink 2003; Glauert–Khasidashvili 1996 | Residual theory explicitly studies how one step transforms the status of another and compares reductions modulo permutation equivalence. |
| PETRA witnessed residual transport as a full residual system | **PETRA-INTERNAL** | Bruggink 2003 residual-system axioms; PETRA axiom audit #303 | The audit gives a negative result for the current `W_P` witness quotient: residual transport is only defined on a restricted realization-level independence domain, and automorphism-quotiented edge classes can conflate self and distinct symmetric occurrences. A total well-defined projection on all coinitial witnessed edges is therefore not currently available. |
| Independent edits commute under PETRA's explicit criterion | **PETRA-INTERNAL** | residual theory and trace theory supply generic analogues | The exact PETRA structural criterion remains internally proved; no theorem has yet identified it with a standard residual-system independence condition. |
| Reduced path need not be geodesic | **PETRA-INTERNAL** | explicit PETRA counterexample | No novelty claim. |
| Completeness of cancellation + independent commutation | **OPEN** | none | Explicitly unresolved. |
| Depth / leaf / root-degree / width / max-degree 1-Lipschitz under PETRA edits | **PETRA-INTERNAL** | standard statistics, PETRA-specific edit bound | Internal proofs are direct; external novelty unresolved. |
| Degree-profile `L1 <= 3` one-step bound | **PETRA-INTERNAL** | no exact external match recorded | Sharp internally and bounded-corroborated. |
| Level-profile `L1 = 1` per edit | **PETRA-INTERNAL** | direct from PETRA leaf edit | No novelty claim. |
| Natural statistic tuple fails to classify forms | **PETRA-INTERNAL** | explicit PETRA witness | The witness is proved internally. A broader external “known phenomenon” classification is not asserted without a source. |

---

## High-confidence prior-art boundaries

### Carrier

PETRA's abstract carrier is not a new combinatorial species. A rooted unlabeled/non-plane tree is classically described recursively by a root carrying an unordered collection / multiset of rooted trees. Modern Pólya-tree literature uses this class and gives the same enumeration sequence.

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

The recursive structure of rooted-tree automorphism groups — internal automorphisms of child subtrees together with permutations among isomorphic child copies — is classical. Bartholdi–Diaconis 2026 states this explicitly in Lemma 3.5 and attributes the orbit machinery to Colbourn–Booth. PETRA's Phase-5 group decomposition and cardinality recurrence should therefore be cited as specialization/rederivation, not novelty.

### Tree edit distance

Tree edit distance is a mature literature. However, operation semantics matter critically. Classical insertion/deletion may reattach children and may include labels/relabeling, whereas PETRA's elementary operation inserts or removes only a leaf occurrence.

Phase-6 research now identifies a closer prior-art family than generic TED: Selkow's leaf-restricted edit distance, commonly called 1-degree / degree-1 / top-down edit distance. PETRA's ADD/REMOVE operation family is therefore classified as a specialization of known leaf-edit operations to unlabeled unordered rooted trees with unit costs and no relabel operation.

This does **not** yet identify PETRA's quotient metric or its maximum-common-reduct formula with a published theorem under the same full convention set.

---

## Candidate PETRA-specific theorem families requiring deeper search

The following remain legitimate future research questions, but **do not block Phase 6 closure** because their current provenance status is explicit:

1. non-meet property of the REMOVE poset under the PETRA reduction relation;
2. automorphism group of the global PETRA edit graph;
3. stronger graph-theoretic neighbourhood signatures for global rigidity, if pursued;
4. completeness or incompleteness of the local witnessed-path presentation;
5. PETRA-specific Lipschitz/profile bounds under leaf-only edits;
6. structural-congruence versus edit-compatibility separation in this exact algebra.

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

## Phase-6 closure state

The closure audit for #311 confirms:

- every major Phase 1–5 theorem family represented here has an explicit provenance status;
- the validation table contains **no `TO-VERIFY` rows**;
- unresolved mathematical questions are explicitly classified `OPEN` or `PETRA-INTERNAL` rather than treated as hidden blockers;
- `PETRA-INTERNAL` means internally proved / externally unmatched at the audited level, **not novel**;
- negative results and failed comparison routes remain part of the record rather than being erased.

Therefore Phase 6 is **COMPLETE**.

Future work on global rigidity, stronger residual semantics, path-completeness, or candidate-specific novelty review may be undertaken if needed, but none is a prerequisite for closing Phase 6.

Phase 7 may now begin as a separate normative-promotion phase. This document itself makes no SPEC, runtime, API, CLI, serialization, or Resolver change.
