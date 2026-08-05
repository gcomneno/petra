# Graph-Laplacian evidence

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

Created: 2026-08-05
Protocol: `petra-vision-graph-laplacian-v1`

## Status and purpose

Status: **bounded reproducible computational evidence**.

This document records the first canonical PETRA VISION graph-Laplacian
experiment over the complete Phase 1 bounded corpus.

The experiment is implemented as a repository research tool with focused
tests and machine-readable JSON output. It remains outside the static Phase 1
completion gate and does not modify the canonical geometry contract.

The result is deliberately retained as `109/110` under the primary
coordinate-free reader. The remaining collision is evidence about the selected
graph and observation convention, not a dataset defect to suppress.

## Research question

The investigated question is whether deterministic diffusion on the
four-neighbor occupied-cell graph yields a reproducible dynamic signature that
distinguishes bounded canonical PETRA VISION geometries.

For canonical geometry `C`, geometry-derived graph `G(C)`, declared probe `p`,
and declared observation procedure `O`, define:

```text
Sigma(C, p, O) =
    sampled trajectory of
    x[k + 1] = (I - (1 / q)L[C]) x[k]
```

where:

- `L[C] = D[C] - A[C]` is the combinatorial graph Laplacian;
- `q` is the declared Euler denominator;
- all graph vertices and edges derive only from occupied geometry cells;
- disconnected components remain disconnected;
- no PETRA serialization, address, label, object identity, or adapter metadata
  enters the dynamic core.

## Evidence boundary

All results are limited to:

- the 110 ordered Phase 1 shapes;
- maximum ordered-group width `3`;
- maximum structural depth `3`;
- maximum structural-node count `7`;
- the committed canonical occupied-cell geometry;
- four-neighbor orthogonal adjacency;
- the combinatorial graph Laplacian;
- the declared probes, integration rules, sample steps, and readers;
- exact integer numerator arithmetic.

The evidence does not establish equivalent behavior for larger domains,
different graph constructions, different boundary models, physical media, or
imperfect observation.

## Reproducibility artifacts

The experiment is represented by:

```text
tools/research/petra_vision_graph_laplacian.py
tests/test_tools_petra_vision_graph_laplacian.py
docs/research/petra-vision/GRAPH_LAPLACIAN_EVIDENCE.md
```

The tool provides:

- deterministic human-readable output;
- machine-readable JSON through `--json`;
- optional JSON persistence through `--write-json PATH`;
- exact collision retention;
- per-shape signature digests;
- probe, temporal, mutation, and elementary-statistics controls.

## Declared primary protocol

The primary protocol is frozen as follows:

| Parameter | Value |
| --- | --- |
| Graph vertices | canonical occupied cells |
| Graph edges | four-neighbor orthogonal adjacency |
| Laplacian | combinatorial `L = D - A` |
| Boundary condition | natural disconnected graph boundary |
| Integration | explicit Euler |
| Euler denominator | `8` |
| Arithmetic | exact integer numerators |
| Probe | unit impulse at the lexicographically minimum vertex of every component |
| Sample steps | `1, 2, 4, 8, 16, 32` |
| Primary reader | global multiset of sampled state values |

The common denominator is implicit in each sampled step. Since signatures are
compared at equal step counts under the same denominator, integer numerator
comparison is exact for this protocol.

No parameter was tuned to reproduce the earlier Galton-like `110/110` result.

## Geometry-induced graph structure

The canonical nested-frame geometry is mostly disconnected under occupied-cell
four-neighbor adjacency:

- connected graphs: `1/110`;
- disconnected graphs: `109/110`;
- connected components per geometry: `1` to `7`;
- maximum observed graph degree: `3`.

Three structural correspondences hold over the full corpus:

| Correspondence | Result |
| --- | ---: |
| connected components = structural nodes | `110/110` |
| isolated vertices = terminals | `110/110` |
| component cycle-rank multiset = local arity multiset | `110/110` |

The graph therefore preserves each node's local frame topology, but the empty
clearance regions prevent diffusion from directly traversing parent-child
containment.

This is a central limitation of the chosen graph construction.

## Primary reader results

| Reader | Distinct signatures | Collision groups |
| --- | ---: | --- |
| null probe, oriented cell order | `110/110` | none |
| diffusion, global value multiset | `109/110` | `[[23, 41]]` |
| diffusion, component-separated multisets | `109/110` | `[[23, 41]]` |
| diffusion, oriented cell order | `110/110` | none |

The primary supported dynamic result is therefore:

> Under the declared asymmetric component probe and coordinate-free global
> multiset reader, graph-Laplacian diffusion distinguishes 109 of the 110
> bounded canonical geometries.

The oriented `110/110` result is not attributed to diffusion because the
oriented null control already distinguishes `110/110`.

## Observation convention

The experiment separates two sources of information:

1. graph dynamics within each connected component;
2. canonical spatial ordering of occupied cells.

An oriented reader receives sampled values in canonical cell order. That order
already identifies all 110 static geometries, including without propagation.

A coordinate-free multiset reader removes spatial order. Under that reader,
the reflected pair `#23/#41` collides.

The observation convention is therefore part of the message and must be
reported with every distinguishability result.

## Probe sensitivity

The coordinate-free global reader produced:

| Probe | Distinct signatures | Collision groups | Shapes involved |
| --- | ---: | ---: | ---: |
| zero | `29/110` | `22` | `103` |
| minimum component vertex | `109/110` | `1` | `2` |
| maximum component vertex | `109/110` | `1` | `2` |
| both component endpoints | `62/110` | `38` | `86` |
| constant state | `29/110` | `22` | `103` |

The minimum and maximum asymmetric probes reproduce the same unique collision.

The endpoint probe is symmetric and loses substantial information. The zero
and constant probes provide null controls; a constant state remains in the
kernel of the graph Laplacian.

The primary probe is therefore explicitly asymmetric. This is a protocol
choice, not a universal property of graph-Laplacian diffusion.

## Temporal sensitivity

For both minimum and maximum probes, and for Euler denominators `4`, `8`, and
`16`:

| Sampling schedule | Distinct signatures |
| --- | ---: |
| steps `1, 2, 4, 8` | `71/110` |
| final step `32` only | `109/110` |
| steps `1, 4, 16, 32` | `109/110` |
| primary schedule | `109/110` |
| primary schedule plus step `64` | `109/110` |

The dynamic separation is insensitive to the tested Euler denominators but
depends on allowing sufficient propagation time.

The pair `#23/#41` persists under every tested nontrivial schedule.

## Translation, replay, and geometry-only audit

Every declared reader is invariant under a fixed positive translation of every
occupied cell:

| Reader | Translation matches |
| --- | ---: |
| null oriented | `110/110` |
| global multiset | `110/110` |
| component multiset | `110/110` |
| oriented | `110/110` |

The dynamic core was audited at the Python AST level. Graph construction,
probe construction, Euler propagation, and signature derivation contain no
references to:

- `VisionShape`;
- `Terminal` or `OrderedGroup`;
- geometry encoding or decoding;
- native PETRA adapters;
- structural addresses;
- corpus enumeration;
- structural metadata helpers.

Two fresh-process JSON executions were byte-for-byte equivalent when audited,
with empty standard error. Deterministic replay is also tested inside the
repository suite.

## Bounded local-mutation sensitivity

The declared local mutation replaces exactly one terminal occurrence:

```text
Terminal()
->
OrderedGroup(children=(Terminal(),))
```

Only mutations whose result remains inside the bounded Phase 1 corpus are
included.

Results:

| Measurement | Value |
| --- | ---: |
| valid bounded mutation pairs | `99` |
| dynamically distinguished pairs | `99` |
| undetected pairs | `0` |
| mutable source shapes | `45` |
| reached target shapes | `74` |

The primary coordinate-free signature detects every valid mutation of this
declared type.

This does not establish sensitivity to every possible local mutation.

## Elementary-statistics control

Shapes were grouped when they shared all of:

- occupied-cell count;
- graph edge count;
- connected-component count;
- isolated-vertex count;
- geometry extent.

Results:

| Measurement | Value |
| --- | ---: |
| shared-statistics groups | `28` |
| shapes involved | `96` |
| comparable pairs | `165` |
| dynamically distinguished pairs | `164` |
| undetected pairs | `1` |

The only undetected pair is `#23/#41`.

The primary signature therefore carries more information than the selected
elementary graph and occupancy statistics.

## Primary collision

The two colliding shapes are:

```text
#23:
OrderedGroup(
    OrderedGroup(
        OrderedGroup(Terminal)
    ),
    OrderedGroup(Terminal, Terminal)
)

#41:
OrderedGroup(
    OrderedGroup(Terminal, Terminal),
    OrderedGroup(
        OrderedGroup(Terminal)
    )
)
```

Their canonical geometries are distinct and are horizontal reflections of one
another.

They contain the same multiset of normalized connected components, placed in
opposite spatial order. Because the coordinate-free graph dynamics evolves
those disconnected components independently, it cannot recover which
substructure occupied the left or right bay.

This collision is therefore structural for the declared coordinate-free
observation, not a floating-point or sample-resolution accident.

## Strongest supported statements

The evidence supports the following bounded statements:

1. occupied-cell four-neighbor graph construction is deterministic and
   translation invariant;
2. the graph has one connected component for every structural-node occurrence;
3. isolated graph vertices correspond exactly to terminals;
4. component cycle ranks reproduce the multiset of local structural arities;
5. exact Euler propagation is deterministically replayable;
6. the primary coordinate-free signature distinguishes `109/110` bounded
   geometries;
7. the sole collision is the reflected pair `#23/#41`;
8. minimum and maximum asymmetric component probes reproduce that result;
9. early-only sampling is insufficient, while the tested mature schedules
   reproduce `109/110`;
10. all 99 declared bounded local mutations are detected;
11. 164 of 165 pairs sharing selected elementary statistics are distinguished;
12. oriented observation distinguishes `110/110`, but the same is already true
    without propagation.

A conservative summary is:

> On the Phase 1 bounded corpus, deterministic graph-Laplacian diffusion on the
> occupied-cell graph yields 109 coordinate-free dynamic signatures. The
> remaining reflected pair has identical disconnected component content and
> differs only in canonical spatial arrangement.

## Matters not established

This evidence does not establish:

- injectivity over all 110 forms under a coordinate-free reader;
- a theorem over unbounded PETRA VISION shapes;
- usefulness of every probe or observation convention;
- independence from graph construction or boundary condition;
- equivalence between occupied-cell adjacency and a physical propagation
  medium;
- a dynamic decoder with error guarantees;
- robustness to noise, damage, quantization, sensor bias, or occlusion;
- spectral uniqueness or absence of isospectral non-identical graphs;
- held-out or newly generated shape validation;
- independent implementation or external reproduction;
- superiority over the Galton-like propagation family;
- cryptographic security;
- novelty, patentability, inventive step, or freedom to operate;
- production readiness;
- any modification of the static Phase 1 contract.

## Methodological risks

The evidence must be interpreted with these risks:

- the same bounded corpus is used to define and evaluate the protocol;
- no held-out corpus has yet been tested;
- only one graph construction is used;
- only the natural disconnected boundary condition is used;
- no spectral decomposition or eigenvalue control is yet recorded;
- probe asymmetry contributes materially to distinguishability;
- canonical coordinate ordering is itself an injective static channel;
- the local-mutation family covers one declared mutation type only;
- exact computational arithmetic does not model physical noise;
- no independent implementation has reproduced the result.

All collisions, negative controls, and degraded probe results are retained.

## Relationship to the Galton-like evidence

The Galton-like precursor and graph-Laplacian experiment use materially
different propagation families.

The Galton-like rule produced `110/110` distinct terminal distributions under
its declared oriented observation convention.

The graph-Laplacian experiment produces:

- `109/110` under its primary coordinate-free reader;
- `110/110` under oriented observation;
- a demonstrated warning that oriented observation already identifies all
  forms without propagation;
- an explicit reflected collision caused by disconnected component
  reordering.

The experiments therefore agree that canonical geometry can support rich
declared dynamics, but they do not establish a law-independent dynamic
identity theorem.

## Reproducibility status

Current repository status represented by this evidence revision:

```text
research tool:                present
focused tests:                present
machine-readable JSON:        available on demand
exact collision retention:    present
translation audit:            present
identity-channel audit:       present
probe controls:               present
temporal controls:            present
local-mutation control:       present
elementary-statistics control: present
held-out corpus:              absent
spectral controls:            absent
alternate boundary model:     absent
independent reproduction:     absent
```

## Next research gates

The appropriate next gates are:

1. retain the `109/110` result and reflected collision unchanged;
2. add held-out bounded shapes before interpreting generality;
3. compare at least one alternate graph or boundary construction;
4. add explicit spectral and isospectral controls;
5. compare invariants and collisions with the Galton-like family;
6. reconstruct the Galton-like calculation as committed auditable code;
7. seek an independent implementation of both propagation families;
8. evaluate observation noise and damage only in a separate later phase;
9. retain confidentiality and professional IP-review gates.
