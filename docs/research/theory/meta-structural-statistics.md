# PETRA meta-theory — structural statistics and Lipschitz observables

Status: **research formalization** for issue #291 under Phase 5 of the complete-theory programme #276.

This note studies structural statistics of PETRA forms and how they change under one elementary ADD/REMOVE edit. It distinguishes structural invariance under PETRA equality from edit invariance: most quantities below are not constant under edits, but some are sharply Lipschitz on the edit graph.

No arithmetic interpretation is used.

## 1. Source data and terminology

Let `P` be the canonical PETRA carrier

```text
P ::= Node(M_f(P))
```

with zero-child form

```text
Z = Node(empty).
```

For a concrete realization `T` of `P`, levels are root distances in edges, the root has level `0`, and out-degree is the number of direct children of an occurrence.

All statistics defined below are invariant under rooted-tree isomorphism, so they descend from realizations to PETRA forms.

For adjacent forms we write

```text
P ~_E Q
```

when one elementary ADD/REMOVE separates them.

## 2. Observable taxonomy

A form-level statistic `f` is called:

- **structural** when it is invariant under PETRA equality / rooted-tree isomorphism;
- **ADD-monotone** when `P --ADD--> Q` implies `f(P) <= f(Q)`;
- **REMOVE-monotone decreasing** when `P --REMOVE--> Q` implies `f(Q) <= f(P)`;
- **k-Lipschitz on one edit** when `|f(P)-f(Q)| <= k` for every adjacent pair;
- **globally k-Lipschitz** when `|f(P)-f(Q)| <= k d(P,Q)` for all forms.

A structural statistic need not be edit-invariant.

### Lemma 1 — Local Lipschitz bounds globalize

If `f` is k-Lipschitz on every edit edge, then

```text
|f(P)-f(Q)| <= k d(P,Q)
```

for all `P,Q`.

#### Proof

Apply the one-edge bound along a geodesic and use the triangle inequality. QED.

Hence every k-Lipschitz observable gives the distance lower bound

```text
ceil(|f(P)-f(Q)| / k) <= d(P,Q).
```

## 3. Depth

Define

```text
depth(P) = maximum occurrence level.
```

### Theorem 1 — Exact ADD rule for depth

Let `Q` be obtained from `P` by ADD at an occurrence `u` of level `ell`. Then

```text
depth(Q) = max(depth(P), ell+1).
```

Therefore

```text
depth(Q)-depth(P) in {0,1}.
```

The increase is exactly one iff `u` lies at maximum level `depth(P)`.

#### Proof

ADD creates one fresh leaf at level `ell+1` and leaves all existing occurrence levels unchanged. QED.

### Corollary 1 — Depth is 1-Lipschitz

For adjacent forms,

```text
|depth(P)-depth(Q)| <= 1.
```

Hence

```text
|depth(P)-depth(Q)| <= d(P,Q)
```

for all forms.

The REMOVE statement is the converse of Theorem 1: deleting a leaf can decrease depth by at most one, and does so exactly when no other occurrence remains at the old maximum level.

## 4. Leaf count

Let

```text
leaf(P) = number of zero-child occurrences of P.
```

### Theorem 2 — Exact one-step leaf rule

Suppose ADD acts at an occurrence of out-degree `k`.

If `k=0`, the target stops being a leaf while the fresh child is a leaf, so

```text
leaf(Q)=leaf(P).
```

If `k>=1`, the target was not a leaf and the fresh child adds one leaf, so

```text
leaf(Q)=leaf(P)+1.
```

Dually, suppose REMOVE deletes a leaf whose parent has out-degree `k>=1` before deletion.

If `k=1`, the deleted leaf disappears but its parent becomes a leaf, so

```text
leaf(Q)=leaf(P).
```

If `k>=2`, the deleted leaf disappears and the parent remains non-leaf, so

```text
leaf(Q)=leaf(P)-1.
```

QED.

### Corollary 2 — Leaf count is 1-Lipschitz

For adjacent forms,

```text
|leaf(P)-leaf(Q)| <= 1,
```

hence globally

```text
|leaf(P)-leaf(Q)| <= d(P,Q).
```

Leaf count is nondecreasing under ADD and nonincreasing under REMOVE, but is not exactly graded because some edits leave it unchanged.

## 5. Root degree

Define

```text
rdeg(P) = out-degree of the root.
```

### Theorem 3 — Exact root-degree rule

An ADD changes root degree by `+1` iff its target is the root; otherwise root degree is unchanged.

A REMOVE changes root degree by `-1` iff the deleted leaf is a direct child of the root; otherwise root degree is unchanged.

Therefore

```text
|rdeg(P)-rdeg(Q)| <= 1
```

for adjacent forms, and root degree is globally 1-Lipschitz.

QED.

## 6. Degree profile

For `k>=0`, define

```text
D_k(P) = number of occurrences of out-degree k.
```

Let `e_k` denote the unit vector in coordinate `k`.

### Theorem 4 — Exact degree-profile update

If ADD acts at a target of out-degree `k`, then

```text
D(Q)-D(P) = e_0 - e_k + e_{k+1}.
```

When `k=0`, the `e_0-e_0` terms cancel, so the change is simply `e_1`.

If REMOVE deletes a leaf whose parent has out-degree `k>=1`, then

```text
D(Q)-D(P) = -e_0 - e_k + e_{k-1}.
```

When `k=1`, the `-e_0+e_0` terms cancel, so the change is simply `-e_1`.

#### Proof

ADD contributes one fresh degree-zero occurrence and changes exactly one existing target degree from `k` to `k+1`. REMOVE deletes one degree-zero occurrence and changes exactly one parent degree from `k` to `k-1`. QED.

### Corollary 3 — Degree-profile L1 bound

For one edit,

```text
||D(P)-D(Q)||_1 <= 3.
```

The bound is sharp whenever ADD targets a non-leaf or REMOVE deletes a child of a parent of degree at least two.

Therefore

```text
ceil(||D(P)-D(Q)||_1 / 3) <= d(P,Q).
```

## 7. Level profile

For `j>=0`, define

```text
L_j(P) = number of occurrences at level j.
```

### Theorem 5 — Exact level-profile update

If ADD acts at an occurrence of level `ell`, then

```text
L(Q)-L(P) = e_{ell+1}.
```

If REMOVE deletes a leaf of level `ell`, then

```text
L(Q)-L(P) = -e_ell.
```

#### Proof

Elementary edits create or delete exactly one leaf and never relocate any surviving occurrence. QED.

### Corollary 4 — Level profile is L1-1-Lipschitz

For adjacent forms,

```text
||L(P)-L(Q)||_1 = 1.
```

Hence for all forms

```text
||L(P)-L(Q)||_1 <= d(P,Q).
```

This gives a profile-level distance lower bound stronger than any one coordinate alone.

## 8. Width

Define

```text
width(P) = max_j L_j(P).
```

### Theorem 6 — Width is 1-Lipschitz

A single edit changes exactly one level-profile coordinate by one in absolute value. Therefore

```text
|width(P)-width(Q)| <= 1
```

for adjacent forms.

The bound is sharp, for example when ADD increases a uniquely maximal level count or creates a new tied/exceeding maximum as appropriate.

Hence

```text
|width(P)-width(Q)| <= d(P,Q).
```

QED.

## 9. Maximum out-degree

Define

```text
Delta(P) = maximum occurrence out-degree.
```

### Theorem 7 — Maximum out-degree is 1-Lipschitz

ADD increases the degree of exactly one occurrence by one and changes no other existing degree. REMOVE decreases the degree of exactly one surviving occurrence by one. Therefore

```text
|Delta(P)-Delta(Q)| <= 1
```

for adjacent forms, hence globally

```text
|Delta(P)-Delta(Q)| <= d(P,Q).
```

QED.

## 10. Distance lower bounds collected

The established observables yield, for all `P,Q`,

```text
|size(P)-size(Q)|                  <= d(P,Q)
|depth(P)-depth(Q)|                <= d(P,Q)
|leaf(P)-leaf(Q)|                  <= d(P,Q)
|rdeg(P)-rdeg(Q)|                  <= d(P,Q)
|width(P)-width(Q)|                <= d(P,Q)
|Delta(P)-Delta(Q)|                <= d(P,Q)
||L(P)-L(Q)||_1                    <= d(P,Q)
ceil(||D(P)-D(Q)||_1 / 3)          <= d(P,Q).
```

These are lower bounds only. The exact distance remains the common-reduct formula established in the edit-geometry layer.

## 11. Natural statistics do not classify forms

Even fairly rich tuples of natural statistics do not determine the PETRA form.

### Proposition 1 — Equal basic statistics can hide different forms

Let

```text
P = Node({ Node({ Z, Node({Z}) }) })
```

and

```text
Q = Node({ Node({ Node({Z,Z}) }) }).
```

Then `P` and `Q` are distinct PETRA forms, but both have

```text
size       = 5
depth      = 3
leaf       = 2
root degree= 1
width      = 2
max degree = 2.
```

#### Proof

The statistics follow by direct inspection. The forms are not isomorphic because in `P` the unique root child has out-degree two, while in `Q` the unique root child has out-degree one. QED.

Thus the tuple

```text
(size, depth, leaf, rdeg, width, Delta)
```

is not a complete invariant for PETRA equality.

## 12. Interaction with automorphisms

All form-level statistics above are invariant under every realization automorphism because automorphisms preserve root, incidence, levels, child counts, and leaf status.

Occurrence-local quantities such as level and out-degree are constant on automorphism orbits of occurrences. Consequently automorphism-equivalent edit targets have equal local statistic signatures.

The converse need not hold: equal level and out-degree do not by themselves imply two occurrences lie in the same automorphism orbit.

This note therefore keeps form statistics distinct from target-orbit data developed in the automorphism layer.

## 13. What is established

This note proves internally:

- depth is 1-Lipschitz;
- leaf count has an exact one-step rule and is 1-Lipschitz;
- root degree is 1-Lipschitz;
- the exact degree-profile update formula and a sharp L1 bound of three per edit;
- the exact level-profile update formula and an L1 change of exactly one per edit;
- width is 1-Lipschitz;
- maximum out-degree is 1-Lipschitz;
- each Lipschitz observable yields an edit-distance lower bound;
- a six-statistic tuple still fails to classify PETRA forms;
- form statistics are automorphism-invariant but do not replace target-orbit theory.

## 14. What remains open

This note does not establish:

- an optimal finite family of statistics that classifies PETRA forms;
- whether any useful smaller complete signature exists short of canonical tree form;
- optimal combined lower bounds obtained from several correlated observables;
- spectral or generating-function statistics;
- probabilistic distributional statements;
- novelty relative to established rooted-tree metric/statistical literature;
- any normative runtime or SPEC consequence.

These belong to later Phase-5 work or Phase-6 external validation.

## 15. Evidence discipline

The statements above are direct consequences of the canonical rooted-tree carrier and elementary leaf ADD/REMOVE semantics.

A bounded executable probe may independently enumerate small forms and validate all local change formulas, sharpness examples, and non-classification witnesses. Such computation is corroboration, not a substitute for the proofs above.
