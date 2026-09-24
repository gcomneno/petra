# PETRA Phase 6 — leaf-edit metric comparison

Status: **Phase 6 external-validation note** for issue #295 under programme #276.

This note compares PETRA's elementary leaf ADD/REMOVE system with established tree-edit literature. It does not modify PETRA's internal theory and makes no novelty claim.

## 1. PETRA edit semantics

PETRA works on finite rooted unlabeled unordered/non-plane trees. Elementary edits attach one fresh zero-child node or delete one non-root zero-child node, each at unit cost. There is no relabel operation.

## 2. Selkow / 1-degree prior art

Selkow's 1977 *The Tree-to-Tree Editing Problem* is direct prior art for edit systems where insertion and deletion are restricted to leaves. Modern literature explicitly calls this **1-degree edit distance** and lists node relabel, leaf insert, and leaf delete as its elementary operations.

Therefore leaf-restricted insertion/deletion is not a PETRA novelty candidate.

## 3. Convention matrix

| Feature | Selkow / 1-degree family | PETRA |
| --- | --- | --- |
| rooted trees | yes | yes |
| labels | yes in classical formulations | no |
| sibling order | ordered in Selkow's original formulation | intrinsic order absent |
| relabel | yes | absent |
| insertion | leaf-restricted | attach one fresh leaf |
| deletion | leaf-restricted | delete one non-root leaf |
| root preservation | standard mapping formulations preserve root | yes |
| cost | general and unit-cost variants | unit |
| equality level | concrete/tree-mapping formulation | rooted-tree isomorphism classes |

## 4. Phase-6 classification

The operation family is **SPECIALIZED**: PETRA removes labels/relabeling and sibling order from a known leaf-edit family.

Literal equality with Selkow's original metric is not asserted because the carrier and quotient conventions differ. By contrast, non-identity with **unrestricted** classical TED at the operation-system level is already established by the definitions: unrestricted TED permits internal-node insertion/deletion semantics that PETRA does not.

## 5. Common reduct is not generic common subtree

PETRA's `c(P,Q)` is the maximum size of a tree obtainable from both forms by repeated PETRA REMOVE operations. Literature uses several non-equivalent notions of common subtree, embedded subtree, tree inclusion, and deletion-with-reattachment. These terms must not be substituted for PETRA common REMOVE-reduct without an operation-exact equivalence result.

## 6. Exact distance formula

PETRA internally proves:

```text
d(P,Q) = size(P) + size(Q) - 2*c(P,Q)
```

The literature search confirms strong connections among tree edit distance, restricted edit distance, and maximum-common-structure formulations, but the currently registered sources do not establish this exact formula under all PETRA conventions simultaneously: unlabeled, unordered, rooted, root-preserving, unit-cost, leaf-only, modulo rooted-tree isomorphism, with `c` defined by common leaf-pruning reducts.

Therefore the exact formula remains **TO-VERIFY externally**. Its internal proof is unaffected.

## 7. REMOVE* ADD* geodesic

PETRA's existence theorem for a geodesic of the form `REMOVE* ADD*` through a maximum common reduct remains **TO-VERIFY externally**. The current literature makes the comparison substantially narrower, but no source-exact theorem has yet been registered.

## 8. REMOVE reachability

PETRA REMOVE reachability is related to pruning / tree-inclusion ideas, but generic tree inclusion often uses more general deletion semantics preserving ancestry by reconnecting descendants. Exact equivalence is therefore not asserted.

## 9. Result

Phase 6 can now strengthen one boundary safely: PETRA's elementary leaf ADD/REMOVE operation family is a specialization of established 1-degree / Selkow edit operations. The exact PETRA metric formula, geodesic normal form, and pruning-order equivalence remain narrower `TO-VERIFY` questions.
