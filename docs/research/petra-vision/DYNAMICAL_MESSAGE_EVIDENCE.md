# Dynamical message evidence

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

Created: 2026-08-05
Evidence revision: `6020fa8d91616175cc3043ac62bc8afa28a58fdf`

## Status and purpose

Status: **bounded exploratory computational evidence**.

This document records a sequence of transient, read-only computational
experiments over the complete PETRA VISION Phase 1 bounded corpus.

It is an evidence record for one declared Galton-like propagation model. It
does not modify the static PETRA VISION technical contract, the Phase 1
completion decision, or the planned graph-Laplacian experiment.

The experiments were executed as transient Python programs from the repository
root. They did not modify production code, tests, generated evidence, or the
working tree. Their implementations are not yet committed reproducibility
artifacts.

## Research question

The investigated question is whether canonical geometry, together with a
declared propagation law, initial condition, and observation convention, can
determine an observable terminal message.

For a canonical geometry `C`, declared dynamics `D`, initial condition `I`,
and observation procedure `O`, define:

```text
Phi[D,I,O](C) = terminal probability distribution
```

For a sampled experiment with random realization `omega`:

```text
Y = F(C, D, I, O, omega)
```

The individual realization depends on `omega`. The theoretical terminal
distribution does not:

```text
pi[C] = P(Y | C, D, I, O)
```

The conservative interpretation is therefore:

> Geometry and declared dynamics determine the probability law of the
> terminal observation. Randomness selects an individual realization of that
> law.

## Evidence boundary

All results in this document are limited to:

- the 110 ordered Phase 1 shapes;
- maximum ordered-group width `3`;
- maximum structural depth `3`;
- maximum structural-node count `7`;
- the committed canonical Phase 1 geometry;
- the declared Galton-like `v0` dynamics;
- the declared initial state and terminal reader;
- numerical computation under the recorded protocols.

The evidence does not establish the same properties for larger shapes, other
propagation laws, other boundary conditions, physical media, or imperfect
sensors.

## Corpus

The independently enumerated bounded corpus contains exactly 110 shapes, with
the following node-count distribution:

```text
nodes:   1  2  3  4   5   6   7
shapes:  1  1  2  5  12  28  61
```

Every experiment reconfirmed exact static geometry roundtrip before dynamic
analysis. The 110 canonical geometries had 110 distinct static digests.

## Declared Galton-like rule

The experimental rule family used these principles:

1. remove the outer canonical frame from the active obstacle field;
2. treat internal occupied cells in each geometry row as geometric pegs;
3. begin each event at the horizontal center;
4. traverse active rows in a fixed direction;
5. move one horizontal unit per row;
6. derive left and right pressure from inverse-square distance to row pegs;
7. map net pressure through a bounded hyperbolic-tangent response;
8. use reduced sensitivity on direct peg alignment;
9. clamp rightward probability to the interval `[0.05, 0.95]`;
10. clamp terminal motion to the declared interior boundary;
11. observe the resulting terminal horizontal position.

The degenerate one-cell `Leaf` geometry places all terminal mass in the
central observation bin.

The rule receives occupied geometry and declared numeric parameters. It does
not receive serialized PETRA, native addresses, labels, node identifiers,
object identity, historical PET values, or adapter-side identity channels.

A committed geometry-only audit remains pending.

## Experiment 1: controlled paired probe

Two seven-node, depth-three geometries were compared:

```text
original: [L,[L,[L,L]]]
mutated:  [L,[[L,L],L]]
```

They had equal node count, depth, occupied-cell count, and extent:

```text
nodes:    7
depth:    3
cells:    169
extent:   25 x 13
```

Their static geometry digests were:

```text
original:
0987c56a28004eb7646c6b7a089c2e2e701347f28ba90fb53e981375325ba706

mutated:
74303fde71a95e426e5fb9b4dc45003f854ca78aaf887ccd6163d7afdff06612
```

Using 25,000 events and common random numbers:

- identical geometry and seed reproduced exactly;
- `13,210` terminal trajectories differed;
- the paired divergence fraction was `52.8400%`;
- original seed variation had TV distance `0.008400`;
- mutated seed variation had TV distance `0.010920`;
- cross-geometry TV distances were `0.086400` and `0.089160`;
- the minimum observed geometry signal exceeded the maximum observed
  seed variation by approximately `7.91`.

This establishes a geometry-dependent response for the declared pair and
rule. It is not a general injectivity result.

## Experiment 2: sampled corpus atlas

The Galton-like rule was applied to all 110 shapes using:

```text
terminal bins:       25
seeds:               4
events per seed:     6,000
events per shape:    24,000
total events:        2,640,000
```

Observed results:

```text
sampled signatures:                     110/110 distinct
exact sampled-signature collision sets: 0
maximum same-shape seed distance:        0.032667
minimum cross-shape distance:            0.004208
shapes separated from own seed noise:    55/110
```

The sampled atlas showed no exact collision, but it did not provide global
statistical separation because the closest cross-shape distance was smaller
than the largest observed seed variation.

## Experiment 3: direct probability propagation

Monte Carlo sampling was then removed. Unit probability mass was propagated
directly through every row transition.

This produced:

```text
canonical geometries:             110
distinct dynamic kernels:         110
distinct terminal distributions:  110
exact kernel collisions:          0
exact distribution collisions:    0
minimum terminal TV distance:
0.0041008494986721801
```

For the controlled pair:

```text
deterministic TV distance:
0.0889003732917105632

original mean:
11.698214452431

mutated mean:
12.064501899158

original variance:
13.001908864013

mutated variance:
12.011260585737
```

Within this finite corpus and numeric implementation, the map

```text
canonical geometry -> exact terminal distribution
```

was numerically injective.

## Experiment 4: inverse dynamic decoder

Nearest-distribution decoding recovered all exact signatures:

```text
exact distributions decoded correctly: 110/110
ambiguities:                             0
```

The global minimum-distance decoding radius was:

```text
minimum TV distance:
0.0041008494986721801

global unique-decoding radius:
0.00205042474933609005
```

Sampled observations produced the following nearest-TV results over three
test seeds:

```text
events       correct       accuracy
1,000        272/330       82.4242%
6,000        308/330       93.3333%
24,000       329/330       99.6970%
```

The global radius is an adversarial uniform guarantee. Many shapes have
substantially larger local margins and can be decoded correctly outside that
global radius.

## Experiment 5: maximum-likelihood decoding

A maximum-likelihood decoder was compared with nearest-TV decoding using 12
test seeds and 1,320 observations per checkpoint.

```text
events    nearest TV            maximum likelihood
1,000     1004/1320  76.0606%   1106/1320  83.7879%
6,000     1250/1320  94.6970%   1295/1320  98.1061%
24,000    1310/1320  99.2424%   1319/1320  99.9242%
```

At 24,000 events:

- maximum likelihood corrected nine nearest-TV errors;
- nearest TV corrected no maximum-likelihood error;
- both decoders failed on one observation;
- that failure occurred on the theoretically hardest pair.

This supports maximum likelihood as the appropriate finite-sample decoder for
the declared multinomial observation model.

## Experiment 6: information distance

All `5,995` unordered pairs were evaluated.

The minimum Chernoff information was:

```text
8.08668884870945739e-05
```

The minimum class contained a reflected pair orbit:

```text
[[L],[L,L,L]] <-> [[L],[L,L],L]

[L,[L,L],[L]] <-> [[L,L,L],[L]]
```

The two representatives agree within numerical tolerance and have opposite
optimal Chernoff parameters under reflection.

For the worst binary pair, the conservative Chernoff event budgets were:

```text
target binary error    sufficient events
1%                     48,377
0.1%                   76,850
0.01%                 105,324
0.0001%               162,272
```

These are conservative binary bounds under the declared model. They are not
universal multiclass, physical-device, or adversarial guarantees.

## Reflection equivariance

Let `M` reverse child order recursively and reflect horizontal geometry.

The complete corpus verified:

```text
Phi(M(C)) = M(Phi(C))
```

Observed structure:

```text
self-reflecting shapes: 24
reflected shape pairs:  43
reflection orbits:      67
```

The count closes the corpus:

```text
24 + 2 * 43 = 110
```

Maximum numerical TV error between a reflected distribution and the
distribution of the reflected shape was:

```text
1.31405303305243137e-16
```

The most difficult Chernoff class is therefore an orbit under reflection,
rather than a unique literal pair.

## Observation convention

An oriented 25-bin reader recovered all 110 exact forms.

A reader that folds each left-right bin pair together discards orientation.
It recovered exactly the 67 reflection orbits:

```text
oriented forms:                     110
oriented messages:                  110
reflection orbits:                   67
unoriented messages:                 67
extra collisions beyond reflection:  0
```

The minimum TV distance between distinct folded orbits was:

```text
0.00357095061230023811
```

Therefore, within this corpus:

- an oriented reader identifies the oriented form;
- a reflection-symmetric reader identifies the reflection orbit;
- the observation convention is part of the message contract.

## Spatial reader resolution

The 25-bin terminal distribution was coarsened to each odd uniform
resolution from 1 through 25.

Results:

```text
oriented bins   oriented messages   folded sensors   orbit messages
1               1/110               1                1/67
3               110/110             2                67/67
5               110/110             3                67/67
7 through 25    110/110             4 through 13     67/67
```

Three oriented bins were the first complete resolution in the tested uniform
odd scale.

The corresponding exact margins were:

```text
three-bin oriented minimum TV:
0.0000013156656655532805236661997213765940945650820159713120500326598171800999434123308134505

two-sensor folded minimum gap:
0.000182808564392944494605438803898472864625587128652200639307807810316064378763174022221353
```

This is a minimum only within the tested uniform odd reader family, not among
all possible sensor placements or observation functions.

## High-precision verification

The three-bin calculation was independently repeated using decimal arithmetic
at 60 and 90 digits.

All 110 signatures agreed over the first 40 decimal digits.

Observed scalar properties:

```text
left terminal mass:       110/110 oriented forms distinct
center terminal mass:      67/110 values, one per reflection orbit
right terminal mass:      110/110 oriented forms distinct
left-right imbalance:      87/110 distinct values
```

Consequently, for this corpus and rule:

```text
left mass   -> oriented form
center mass -> reflection orbit
```

The maximum center-mass discrepancy within reflected pairs at 90-digit
precision was `4E-90`.

## Quantization

Uniform scalar quantization produced these empirical thresholds:

```text
left mass, 110 oriented forms:
19 bits

center mass, 67 reflection orbits:
12 bits
```

Conservative thresholds derived from the observed minimum gaps were:

```text
left mass:
20 bits

center mass:
13 bits
```

These values describe uniform quantization of the selected analog
observables. They are not minimal arbitrary binary code lengths.

The information-theoretic label lower bound is seven bits for both 110 forms
and 67 orbits:

```text
ceil(log2(110)) = 7
ceil(log2(67))  = 7
```

The larger observed precision requirement arises because the decoder reads a
dynamically generated scalar on a uniform numeric grid rather than an
arbitrarily assigned discrete codeword.

## Strongest supported statements

The following statements are supported for the declared finite protocol:

1. canonical geometry and the Galton-like `v0` law deterministically define a
   terminal probability distribution;
2. all 110 bounded canonical geometries have distinct exact terminal
   distributions;
3. the exact distributions decode to the correct form with no ambiguity;
4. sampled observations converge toward reliable decoding as event count
   increases;
5. maximum likelihood outperforms nearest-TV decoding in the tested finite
   samples;
6. reflection of structure induces reflection of the terminal distribution;
7. removing reader orientation identifies exactly the 67 reflection orbits;
8. three uniform oriented bins preserve all 110 exact messages;
9. one scalar left-mass observable numerically identifies the 110 oriented
   forms;
10. one scalar center-mass observable numerically identifies the 67 reflection
    orbits;
11. the observed scalar injectivity is stable between 60-digit and 90-digit
    decimal calculations.

A conservative summary is:

> On the Phase 1 bounded corpus, canonical PETRA VISION geometry, the declared
> Galton-like dynamics, initial condition, and observation convention
> determine a numerically unique terminal message.

## Matters not established

This evidence does not establish:

- a theorem over unbounded PETRA VISION shapes;
- injectivity for every possible propagation law;
- optimality or naturalness of the Galton-like rule;
- independence from all choices of initial state or boundary condition;
- symbolic exactness of all pairwise inequalities;
- a physical propagation mechanism;
- transfer to printed, optical, acoustic, electrical, mechanical, fluid, or
  other material systems;
- robustness to systematic sensor bias, damage, occlusion, calibration error,
  or adversarial perturbation;
- error-correcting capability;
- cryptographic security;
- novelty, patentability, inventive step, or freedom to operate;
- production readiness;
- completion of the planned graph-Laplacian experiment;
- completion of a committed geometry-only audit;
- completion of held-out or larger-domain validation.

## Methodological risks

The present evidence must be interpreted with these risks:

- the law was explored on the same 110-shape corpus used for evaluation;
- the experiments were not preregistered;
- no held-out shape family was used;
- no independent implementation has yet reproduced the result;
- the dynamic scripts were transient rather than committed;
- the rule may emphasize features specific to the Phase 1 nested-frame
  grammar;
- high-precision numerical separation is not a symbolic proof;
- scalar injectivity may fail as the shape domain grows;
- physical noise may be qualitatively different from multinomial sampling
  noise.

No negative result or future collision should be suppressed.

## Relationship to the planned experiment

`DYNAMICAL_GEOMETRY_HYPOTHESIS.md` and `EXPERIMENT_PLAN.md` specify a
geometry-only graph-Laplacian diffusion experiment as the first canonical
reproducible dynamic probe.

The Galton-like evidence recorded here is an exploratory precursor. It does
not replace, complete, or prejudge that planned experiment.

The graph-Laplacian experiment remains valuable because it supplies:

- a different propagation family;
- an independent test of geometry-derived dynamics;
- explicit graph and spectral controls;
- null and permuted probes;
- boundary-condition sensitivity;
- a stronger committed geometry-only audit;
- an opportunity to test whether the observed distinguishability survives a
  materially different law.

## Reproducibility status

Current status:

```text
execution logs:              retained in private research conversation
repository modifications:   none
committed experiment code:   absent
committed generated data:    absent
independent reproduction:    absent
```

Before promotion beyond exploratory evidence, the experiment should be
reconstructed as a small geometry-only research tool with:

- frozen rule parameters;
- deterministic direct propagation;
- an independently enumerated corpus;
- exact protocol metadata;
- machine-readable results;
- focused tests;
- collision retention;
- high-precision checks;
- no native identity channel;
- a documented distinction between exact and sampled evidence.

## Next research gates

The appropriate next gates are:

1. preserve this record without promoting it to the static Phase 1 contract;
2. implement an independently auditable geometry-only version of the
   Galton-like direct calculation;
3. reproduce the 110-signature result from committed code;
4. add held-out shapes beyond the tuning corpus;
5. run the planned graph-Laplacian experiment without tuning it to reproduce
   the Galton result;
6. compare invariants and collisions across the two propagation families;
7. seek symbolic or interval-arithmetic certification of the closest
   inequalities;
8. evaluate observational and physical claims only in a separate later phase;
9. retain the existing confidentiality and professional IP-review gates.
