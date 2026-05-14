# PET Syntax Tree exploratory model

This document explores whether PET can use a syntax-tree-like model to explain
how it sees numbers, residuals, routes, anchors, and structural descent.

This is a research/design document only.

It does not define new core runtime behavior.

## Goal

Explore a minimal "PET Syntax Tree" model.

The goal is to represent how PET sees a number or residual as a structured
object:

- the root is the current number or residual;
- nodes describe structural PET states, anchors, generators, factors, or
  unresolved residuals;
- edges describe PET moves, verified reductions, or explanatory relationships;
- the tree helps explain, visualize, and possibly guide residual-shape descent.

The main intended uses are:

- explain PET more intuitively;
- visualize residual descent;
- compare candidate residual shapes;
- make routing decisions easier to debug;
- document why one anchor was selected over another;
- support residual-shape-compression experiments.

## Non-goals

A PET Syntax Tree is not a new mathematical proof engine.

It must not replace:

- classic arithmetic verification;
- PET routing policies;
- candidate verification;
- shape-family support scans;
- residual descent validation.

It must also not become a nicer name for `shape_signature`.

If the model does not add explanatory or routing value beyond existing fields,
it should remain a metaphor and not become implementation.

## Existing PET structures that already look syntax-like

PET already has several concepts that are close to a syntax model.

### `shape_signature`

`shape_signature` is the closest existing object to a compact syntax form.

Examples:

```text
[[]]
[[], []]
[[], [[]]]
[[], [], [[]]]
[[[]], [[]]]
~~~
```

These are not factorization trees. They describe PET-visible structure.

Possible interpretation:

shape_signature = compact PET structural expression
generator

The generator can be seen as a canonical or minimal representative of a PET
shape.

Possible interpretation:

shape_signature = structure
generator        = minimal representative realizing that structure
Pathwise neighborhood

The pathwise neighborhood is not a tree.

It is closer to a graph of possible PET moves:

NEW
DROP
INC
DEC

Because multiple paths can reach related states, this model is naturally graph-
like. A PET Syntax Tree must not erase that distinction.

Pathwise DOT

The existing DOT-oriented pathwise output is useful for visualization, but it
mostly represents states and transitions.

This is closer to a graph of moves than to a single syntax tree.

Root anatomy and known_root_children

Root anatomy and known_root_children already resemble structural node data:

root state;
known children;
root generator information;
lower-bound information.

These can inform the shape of future PET Syntax Nodes.

Explain moves

Explain moves already expose PET transitions in human-readable form.

They can become edge labels in an explanatory tree or graph.

Residual descent

Residual descent already creates a recursive explanation path:

N
-> verified anchor
-> residual
-> PET-routing on residual
-> verified anchor
-> residual
-> ...

This is the best current candidate for a PET Syntax Tree view, because it is
already tree-like when represented as:

N
├── verified anchor
└── residual
    ├── verified anchor
    └── residual
Factorization tree vs PET vs pathwise graph vs PET Syntax Tree
Classic factorization tree

A classic factorization tree explains division into factors.

Example:

252
├── 2
└── 126
    ├── 2
    └── 63
        ├── 3
        └── 21
            ├── 3
            └── 7

Main question:

What divides this number?
Prime Exponent Tree

PET asks a different question.

Main question:

What PET-visible structure does this number have?

PET is interested in shape, generator behavior, candidate anchors, supported
families, and routing.

It is not just trial division with a different name.

Pathwise graph / neighborhood

The pathwise graph describes possible moves around a number or shape.

Main question:

What PET moves are possible from here?

This is naturally a graph because states and transformations can overlap.

PET Syntax Tree

A PET Syntax Tree should describe a selected structural explanation.

Main question:

How does PET explain this number or residual in this routing path?

It is a snapshot/explanation tree, not the entire move space.

A useful separation is:

shape_signature       = compact structural form
pathwise graph        = possible transformations
residual descent      = chosen verified recursive route
PET Syntax Tree       = explainable structured view of the chosen route/state
PET Syntax Forest     = competing explanation trees for candidate anchors
PET Syntax Node

A PET Syntax Node represents one PET-observable state.

Minimal fields:

id
role
value
shape_signature
shape_family_class
generator
route_policy
route_status
terminal_status
metadata

Possible roles:

root
residual
anchor
factor
generator
terminal_leaf
unresolved_residual
candidate

Example node:

{
  "id": "node_0",
  "role": "root",
  "value": 245,
  "shape_signature": "[[], [[]]]",
  "shape_family_class": "one-deep-tail",
  "route_policy": "shape-family-support-scan",
  "route_status": "partial-factorization-by-shape-family-scan",
  "terminal_status": "non-terminal",
  "metadata": {}
}
PET Syntax Edge

A PET Syntax Edge represents a structural relation or transformation.

Minimal fields:

source
target
edge_kind
move
verification_status
reason

Possible edge kinds:

has_anchor
has_residual
pet_move
residual_descent
classic_verified_factor
shape_projection
candidate_alternative

Possible moves:

NEW
DROP
INC
DEC
ANCHOR
RESIDUAL
VERIFY

Possible verification statuses:

pet-structural
classic-verified
suggested-only
blocked

Example edge:

{
  "source": "node_0",
  "target": "node_1",
  "edge_kind": "has_anchor",
  "move": "ANCHOR",
  "verification_status": "classic-verified",
  "reason": "anchor selected by best-pet-residual-shape-descent"
}
PET Syntax Tree

A PET Syntax Tree is rooted at a single number or residual.

Minimal fields:

schema
root
nodes
edges
claim

Example claim:

PET syntax tree is explanatory only; arithmetic verification remains classic-bounded.

The tree can explain a selected PET route, but it does not prove arithmetic
correctness by itself.

PET Syntax Forest

A PET Syntax Forest is useful when PET compares several candidate anchors or
routes.

Example:

anchor 2  -> residual tree A
anchor 10 -> residual tree B
anchor 20 -> residual tree C
selected  -> anchor 20
reason    -> best supported residual shape

Minimal fields:

schema
target
candidate_trees
selected_tree
selection_policy
reason

This can be useful for explaining:

best-pet-residual-shape-descent

The forest represents alternatives. The selected tree represents the route PET
actually follows.

Example: 245

Classic factorization:

245 = 5 * 7 * 7

PET-style route:

245
shape_signature = [[], [[]]]
shape_family_class = one-deep-tail
route = shape-family-support-scan
anchor = 5
residual = 49
residual route = prime-power-local-check
49 = 7 * 7

Possible PET Syntax Tree:

245 [one-deep-tail]
├── anchor 5 [classic-verified]
└── residual 49 [narrow-deep-chain]
    ├── factor 7 [classic-verified]
    └── factor 7 [classic-verified]

This is not a classic factorization tree. It shows the PET routing explanation:
first a shape-family anchor, then a prime-power residual.

Example: 252

Classic factorization:

252 = 2 * 2 * 3 * 3 * 7

PET may see a mixed-depth structure:

target_signature = [[], [[]], [[]]]
shape_family_class = mixed-depth

A PET Syntax Tree would emphasize the route:

252 [mixed-depth]
├── anchor selected by shape-family support scan
└── residual
    └── PET-routing continues

The exact tree should record verified anchors in the order PET selected them,
not force canonical prime factorization.

This preserves the residual descent story.

Example: 24680

Observed residual descent:

24680
-> anchor 20
-> residual 1234
-> anchor 2
-> residual 617
-> prime leaf

Possible PET Syntax Tree:

24680
├── anchor 20 [classic-verified]
└── residual 1234
    ├── anchor 2 [classic-verified]
    └── residual 617
        └── prime leaf 617 [classic-verified]

This tree explains recursive PET-routing over verified residuals.

It should not be normalized into canonical prime factorization by default,
because the residual reduction chain records the anchors PET actually selected.

Example: 1001

One possible residual descent:

1001
-> anchor 13
-> residual 77
-> 7 * 11

Possible PET Syntax Tree:

1001
├── anchor 13 [classic-verified]
└── residual 77 [semiprime-flat]
    ├── factor 7 [classic-verified]
    └── factor 11 [classic-verified]

This example shows why the syntax tree can be useful: it explains how a flat-k
or support-scan result can lead into a simpler residual family.

Potential uses

A PET Syntax Tree could help with:

explaining PET to humans;
visualizing residual descent;
debugging route choices;
comparing residual shapes after candidate anchors;
showing why one candidate produced a simpler supported residual;
building future residual-shape-compression metrics;
generating DOT/JSON artifacts for research reports.
Risks
Confusing graph and tree

The pathwise neighborhood is a graph of possible moves.

A PET Syntax Tree is a selected explanation path or structural snapshot.

They must remain separate.

Duplicating shape_signature

If the syntax tree only wraps shape_signature in a more elegant name, it is
not useful.

It must add explanatory relationships, route information, verification status,
and residual descent structure.

Beautiful but useless metaphor

The tree must support practical tasks:

explain;
visualize;
compare;
debug;
guide routing.

If it does not help at least some of these, it should remain a metaphor.

Losing verification boundaries

A visual tree can look convincing even when it is only suggestive.

Every edge should preserve the boundary:

pet-structural
classic-verified
suggested-only
blocked

The tree must never imply that PET visual structure alone proves arithmetic
correctness.

Possible future exploratory probe

A future research-only tool could be added later, after explicit approval:

tools/research/pet_syntax_tree_probe.py

Possible behavior:

python tools/research/pet_syntax_tree_probe.py 245 --json
python tools/research/pet_syntax_tree_probe.py 245 --dot

Possible output schema:

pet.syntax_tree.v0

Constraints for any future probe:

research-only;
no PET core refactor;
no runtime behavior change;
JSON/DOT export only;
preserve verification boundaries;
do not replace pathwise graph output.
Current recommendation

Start with documentation only.

The model is promising as an explanatory and visualization layer, especially for
residual descent and best-pet-residual-shape-descent.

It should not be promoted to core behavior until it proves practical value beyond
naming existing concepts differently.
