# PETRA VISION Gate 3 — Explicit spectral controls contract

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Gate 3 protocol freeze.

Issue: #200.

Foundation:

`f366e4e84eb61fe0bd85f176da2e7766be74faca`

## Research question

Which reproducible distinctions in the frozen PETRA VISION dynamic constructions
can be attributed to static structure, spectral structure, probe choice,
impulse response, temporal observation, or orientation?

Gate 3 is an attribution gate. It does not optimize a new classifier for
perfect corpus separation.

## Frozen dependencies

Gate 3 inherits without modification:

- Gate 0 frozen corpora and baseline contracts;
- Gate 1A coordinate-free quotient interpretation;
- Gate 1B native FGS as a bounded geometry-derived research object;
- Gate 2 construction protocols and recorded results.

No Gate 0, Gate 1, or Gate 2 protocol may be silently changed to improve a
Gate 3 result.

## Frozen corpus order

Every primary result is reported separately for:

1. Phase 1 bounded corpus: 110 forms;
2. held-out width-4 corpus: 27 forms;
3. complete frozen extended domain: 137 forms.

The held-out 27-form result remains independently visible.

## Primary substrates

### G3-B0 — frozen occupied-cell baseline

Use the frozen graph-Laplacian v1 occupied-cell construction unchanged.

Purpose: baseline spectral and probe attribution.

### G3-D1 — distance-2 clearance coupling

Use the frozen Gate 2 D1 operator unchanged.

Purpose: resolve the Gate 2 probe qualification and distinguish operator
information from excitation-rule information.

### G3-F1 — FGS factor-proximity coupling

Use the frozen Gate 2 F1 construction unchanged.

Purpose: attribute the clean bounded F1 gain to static factor information,
spectral information, coupling response, or observation protocol.

### G3-L1 — uniform full-lattice propagation

Use the frozen Gate 2 L1 construction unchanged.

Purpose: attribute the clean FGS-independent L1 gain to lattice structure,
operator spectrum, propagation response, or temporal observation.

C0, F0, and E1 remain reference controls when required. Gate 3 must not
reinterpret them as new positive constructions without a separately frozen
protocol.

## Attribution families

The families below are evaluated separately before joint interpretation.

### G3-S0 — static controls

Record only coordinate-free static graph or material information available
before propagation.

Purpose: establish the no-dynamics information floor.

### G3-S1 — Laplacian spectrum

Observe only the eigenvalue multiset of the declared operator.

The primary reader must not receive:

- eigenvector ordering;
- vertex ordering;
- coordinates;
- component or factor ordinal;
- structural address;
- decoded AST identity;
- corpus index;
- serialization or shape code;
- object identity.

Purpose: determine what discrimination exists in the operator spectrum alone.

### G3-S2 — component and factor spectra

For representations with native disconnected components or Gate 1B FGS
factors, compute spectra independently and expose only an unordered,
multiplicity-preserving multiset of local spectral signatures.

Purpose: separate local spectral content from globally coupled information.

### G3-H1 — heat-trace control

Use a predeclared deterministic coordinate-free compression derived from the
same frozen spectrum.

Purpose: measure which distinctions survive spectral compression.

No heat-trace sampling schedule may be selected after corpus discrimination is
inspected.

### G3-P1 — probe ablation

Replay identical frozen dynamics while changing only the initial probe.

The initial frozen probe family is:

- frozen lexicographic minimum probe where defined;
- lexicographic maximum/reflected endpoint counterpart where defined;
- intrinsic local-degree-derived probe;
- constant field;
- zero field negative control.

Additional probes require a protocol amendment before their corpus results are
inspected.

Purpose: identify probe-dependent versus operator-dependent distinctions.

### G3-I1 — impulse-response attribution

Compare matched impulse responses under the frozen probe family while keeping
the operator, integration rule, sample schedule, and reader fixed.

Purpose: determine whether dynamic discrimination survives an intrinsic or
reflection-equivariant excitation rule.

### G3-T1 — temporal observation

The frozen propagation sample index is discrete algorithmic time.

Compare matched observations of the same frozen dynamics under predeclared
temporal reductions. Initial families may include:

- complete ordered sampled trajectory;
- order-discarding multiset of sampled states;
- endpoint-only observation;
- declared prefix observations;
- first-divergence and persistence diagnostics when defined independently of
  corpus identity.

Temporal observation may add evidence only when the underlying dynamics are
identical across the matched comparison.

No claim of physical time, spacetime, or cosmological equivalence is allowed.

### G3-O1 — orientation control

Oriented observations remain explicitly labelled diagnostics only.

They are never evidence for coordinate-free recovery.

Purpose: detect orientation leakage and separate it from intrinsic
spectral/dynamic information.

## Frozen G3-S0/S1 subprotocol

The initial static/spectral attribution protocol is frozen separately in
`EXPLICIT_SPECTRAL_CONTROLS_S0_S1_PROTOCOL.md`.

It uses exact characteristic-polynomial signatures with no floating-point
spectral tolerance.

The frozen computational routes are:

- B0: exact combinatorial-Laplacian charpoly;
- D1: exact weighted-Laplacian charpoly;
- F1: exact rational frozen propagation-operator charpoly;
- L1: exact rectangular-grid Laplacian charpoly through a Cartesian-product
  path-polynomial resultant.

S0 operator statistics and intrinsic initial-state controls remain separate.
B0/D1 probes are explicitly deferred to G3-P1/I1.

No G3-T1 experiment is activated by this subprotocol.

## G3-S0/S1 completed checkpoint

G3-S0/S1 is complete on the frozen Phase 1, held-out, and extended corpus
partitions.

The bounded decision is mixed:

- B0: positive exact spectral attribution;
- D1: positive exact spectral attribution, insufficient to explain its frozen
  dynamic discrimination;
- F1: valid negative spectral attribution;
- L1: valid negative spectral attribution.

All three evidence artifacts have byte-identical deterministic replays.

See `EXPLICIT_SPECTRAL_CONTROLS_S0_S1_EVIDENCE.md`.

The next ordered Gate 3 step is G3-S2 component/factor spectral controls,
followed by G3-H1. Probe and temporal experiments remain inactive.

## Primary causal comparisons

Gate 3 must prefer one-variable-at-a-time comparisons.

Examples:

- static versus spectrum on the same substrate;
- full spectrum versus heat-trace compression of the same operator;
- minimum probe versus intrinsic probe on identical dynamics;
- ordered temporal observation versus order-discarding observation of the
  identical trajectory;
- coordinate-free reader versus oriented diagnostic on identical state.

A result is not attributable when multiple operator, probe, propagation, or
reader changes are made simultaneously.

## Required measurements

For every declared primary comparison record:

- protocol identifier;
- frozen parameters;
- static distinct-signature count;
- spectral or dynamic distinct-signature count;
- exact collision groups;
- collision pairs split relative to the matched control;
- newly introduced collision pairs;
- explicit behavior of the retained Gate 1A #23/#41 reflected/reordered pair
  where applicable;
- deterministic replay;
- translation control;
- reflection/equivariance control where applicable;
- source-boundary and identity-channel audit;
- implementation source SHA256;
- evidence-runner SHA256;
- deterministic evidence digest;
- Phase 1, held-out, and extended results separately.

## Numerical discipline

Spectral calculations must use a representation whose determinism and numerical
tolerance are explicitly frozen before corpus interpretation.

If floating-point eigensolvers are used, the contract must declare:

- solver/library;
- sorting convention;
- rounding or tolerance policy;
- multiplicity handling;
- deterministic replay expectations.

Prefer exact arithmetic or exact characteristic/spectral invariants when
computationally practical.

Numerical coincidence must not be promoted to theorem-level spectral equality.

## Probe discipline

Coordinate-derived probes and intrinsic probes are different causal objects.

A distinction produced only by a coordinate-derived asymmetric probe must be
reported as probe-dependent even when the final reader is coordinate-free.

Reflection-equivariant operator behavior must be tested with transported or
intrinsic probes before claiming intrinsic reflection discrimination.

## Temporal discipline

Temporal evidence is evidence about ordered responses of a frozen algorithmic
dynamical system.

It does not establish a physical temporal dimension.

Temporal readers must not receive corpus identity, shape serialization,
coordinates, or structural labels.

## Deferred temporal hypothesis document

A separately stashed `TEMPORAL_DYNAMICS_HYPOTHESIS.md` may be introduced only
after this contract is committed.

Its contents remain hypothesis/protocol material for G3-T1 and do not become
evidence merely by being restored.

## Success criteria

Gate 3 succeeds when bounded reproducible attribution can be made, including
negative attribution.

Valid outcomes include:

- distinction already present in spectrum;
- distinction absent from spectrum but present in matched impulse response;
- distinction dependent on a particular probe;
- distinction lost under an intrinsic/equivariant probe;
- heat-trace compression retaining only a subset of full-spectrum
  discrimination;
- temporal ordering adding no information;
- temporal ordering adding reproducible information under matched dynamics.

## Failure and falsification criteria

A claim is rejected, qualified, or marked inconclusive when:

- gain disappears under the matched control;
- identity, coordinates, orientation, factor order, serialization, or corpus
  index leak into a primary reader;
- numerical spectral signatures are unstable under deterministic replay;
- probe and operator effects cannot be separated;
- temporal and static protocols are not matched;
- parameters are selected after observing discrimination without a prior
  tuning protocol;
- negative or colliding cases are suppressed.

## Gate boundary

Gate 4 adversarial collision generation is out of scope.

Gate 3 may replay the already known #23/#41 collision and declared reflection
controls, but it must not begin a new adversarial mutation campaign.

## Non-claims

Gate 3 does not establish:

- universal injectivity;
- spectral uniqueness over arbitrary graphs or geometries;
- intrinsic orientation or reflection breaking;
- physical propagation;
- physical time or spacetime;
- robustness to noise, damage, quantization, or occlusion;
- complete dynamic decoding;
- theorem-level reconstruction;
- production API readiness.

## Completion condition

Gate 3 is complete when the declared attribution matrix has been evaluated
sufficiently to separate static, spectral, probe, impulse-response,
temporal-observation, and orientation contributions on the frozen bounded
substrates, while retaining all positive, negative, confounded, inconclusive,
and collision results.
