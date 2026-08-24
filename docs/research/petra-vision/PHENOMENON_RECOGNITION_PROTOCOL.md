# PETRA VISION — Phenomenon Recognition and Serendipity Preservation Protocol

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Operational research-governance contract.

Issue: #201.

Decision authority: `gcomneno` / Giancarlo, explicit instruction to formalize the method on 2026-08-24.

Foundation: Gate 3 final decision commit `5eba66db487b21459567b578f64a2ef437d6962a`.

This protocol is cross-gate governance. It is **not Gate 4**, does not activate Gate 4, and does not authorize any mutation campaign, parameter search, corpus expansion, or scope jump by itself.

## Purpose

PETRA research must preserve unexpected observations long enough to determine whether they are noise, implementation artifacts, bounded regularities, or genuine candidate phenomena.

The primary risk addressed here is not failure to generate serendipity. It is failure to recognize it before the evidence disappears into terminal output, transient files, post-hoc explanation, or an unrelated experimental loop.

The protocol therefore treats recognition as a research capability with explicit capture, provenance, isolation, replay, falsification, replication, and re-discovery rules.

## Core principle

> **An unexpected result must not be classified as `IRRELEVANT` in the same observation event in which it first appears.**

At first observation it may be qualified as:

- unexplained;
- probably trivial;
- suspected artifact;
- source-boundary suspect;
- non-replicated;
- low-attention;
- candidate phenomenon.

But irreversible dismissal requires additional evidence.

This rule prevents premature loss without promoting surprise into truth.

## Epistemic separation

PETRA keeps the following ladder explicit:

`OBSERVATION`
→ `PATTERN`
→ `CANDIDATE_PHENOMENON`
→ `REPLICATED_PHENOMENON`
→ `CLAIM_CANDIDATE`

These states are not interchangeable.

### `OBSERVATION`

An exact result was obtained under an identifiable protocol, input, implementation, and environment.

An observation may be surprising but carries no implication that it is meaningful.

### `PATTERN`

A reproducible relationship occurs in more than one relevant case or under more than one matched observation, but its explanation remains open.

### `CANDIDATE_PHENOMENON`

The pattern survives the immediate controls needed to rule out at least the obvious implementation, identity-channel, ordering, probe, serialization, or arithmetic explanations relevant to the case.

### `REPLICATED_PHENOMENON`

The candidate survives a genuinely independent replication appropriate to the claim, for example an independent held-out family, independently implemented reproducer, or another predeclared orthogonal control.

Composition checks do not count as independent replication.

### `CLAIM_CANDIDATE`

A bounded proposition can be stated with an explicit scope, falsification boundary, provenance, and non-claims.

Claim promotion remains separate from phenomenon recognition.

## Attention level is not epistemic maturity

PETRA may use the existing rabbit shorthand as an attention signal:

- **Level 1** — interesting;
- **Level 2** — surprising;
- **Level 3** — material candidate requiring isolation and independent verification;
- **Level 4** — replicated bounded rabbit.

Rabbit level answers:

> How much attention should this receive?

Epistemic status answers:

> What is actually supported?

A high rabbit level does not override missing evidence. A low rabbit level does not authorize deletion.

## Four first-class preservation layers

### 1. Evidence Ledger

Records exact experimental evidence and provenance.

At minimum, when applicable:

- protocol identifier;
- frozen parameters;
- gate/subgate context;
- commit or source revision;
- source and runner digests;
- exact input/corpus identity;
- raw and normalized outputs;
- deterministic replay status;
- artifact digest;
- source-boundary and identity-channel audit.

The Evidence Ledger records what happened, not why it matters.

### 2. Rabbit Register

Records observations that warrant increased attention.

Each entry must state:

- stable phenomenon identifier;
- attention level;
- trigger for escalation;
- reason ordinary continuation was interrupted or not interrupted;
- current epistemic status;
- next verification gate.

A rabbit is not a claim.

### 3. Unresolved Phenomena Register

Preserves observations or patterns whose meaning is not yet understood.

`UNRESOLVED` is a valid durable outcome.

A record must not be deleted merely because:

- the first explanation failed;
- the current gate ended;
- no immediate application exists;
- the effect is difficult to interpret;
- the effect does not improve a headline score.

An unresolved record may remain dormant until later evidence makes it legible.

### 4. Falsified Expectations Register

Records the expectation that made an observation surprising.

The expectation must be preserved in its pre-explanation form whenever it existed before the observation.

A record distinguishes:

- prior expectation;
- basis for that expectation;
- exact observation that contradicted it;
- whether the expectation itself was frozen, informal, inferred, or merely heuristic;
- replacement hypothesis, if any.

A post-hoc explanation must not overwrite the historical expectation.

## Phenomenon record contract

Every material unexpected observation receives a stable identifier:

`PETRA-PHEN-####`

The first implementation uses a versioned Markdown registry. Storage format is not a scientific primitive and may later be replaced without changing this protocol.

A phenomenon record should contain, when known:

- `id`;
- `title`;
- `detected_at`;
- `gate_context`;
- `epistemic_status`;
- `attention_level`;
- `disposition`;
- `protocol_id`;
- `commit`;
- `source_digests`;
- `artifact_digests`;
- `input_identity`;
- `prior_expectation`;
- `observed_behavior`;
- `surprise_basis`;
- `immediate_replay`;
- `minimal_positive_cases`;
- `minimal_negative_cases`;
- `matched_controls`;
- `synthetic_falsification`;
- `independent_replication`;
- `source_boundary`;
- `related_records`;
- `fingerprint`;
- `supported_claim`;
- `non_claims`;
- `next_decision`.

Unknown fields remain explicitly `UNKNOWN`, `UNRESOLVED`, or `NOT_APPLICABLE`.

## Stop-the-line trigger

Normal experimental progression must pause before further interpretation or tuning when any of the following occurs:

1. a Level 3 or higher rabbit candidate is identified;
2. a frozen invariant or control unexpectedly fails;
3. a deterministic replay unexpectedly diverges;
4. a matched control produces a distinction that contradicts the active causal attribution;
5. two materially different constructions unexpectedly induce the same nontrivial partition or invariant;
6. a supposedly necessary mechanism is falsified by a counterexample;
7. a bounded regularity survives in a way that is not explained by the current protocol;
8. an identity, orientation, serialization, probe, or source-boundary leak is suspected in a positive result.

The pause is local to the active research loop. It must not silently activate another gate.

## Immediate capture bundle

Before changing parameters, corpus, implementation, reader, or interpretation, preserve:

- the exact command or runner invocation;
- input/corpus identity;
- protocol ID;
- frozen parameters;
- current commit;
- relevant source digests;
- exact output artifact;
- artifact digest;
- observed result;
- prior expectation, if one existed;
- reason the result is surprising;
- current rabbit level;
- current epistemic status.

If preservation cannot be completed, the gap must be recorded explicitly.

## Isolation sequence

A material candidate proceeds through the smallest applicable sequence below.

### I0 — deterministic replay

Repeat the exact observation without changing protocol or inputs.

Failure to replay downgrades the phenomenon claim and redirects investigation toward nondeterminism or environment effects.

### I1 — minimal case isolation

Find, when possible, the smallest positive case and a closely matched negative case without tuning the original declaring protocol.

Minimization is diagnostic. It must not rewrite the historical observation.

### I2 — one-variable-at-a-time controls

Change one causal factor at a time wherever the substrate permits it.

Examples include matched nulls, probe ablations, reflection transport, order removal, static/dynamic separation, exact normalization checks, and source-boundary controls.

### I3 — leakage audit

Test whether the effect depends on undeclared:

- coordinates;
- orientation;
- corpus index;
- serialization;
- factor or component order;
- AST identity;
- object identity;
- filenames;
- output labels;
- asymmetric probes.

A leakage explanation is scientifically useful and remains recorded.

### I4 — synthetic necessity falsification

When the working interpretation suggests that property `A` forces property `B`, construct a synthetic counterexample if practical.

If a counterexample exists, the bounded PETRA regularity may remain interesting but must not be presented as algebraic or generic necessity.

### I5 — independent replication

Use an independent held-out family, independent implementation, or another genuinely independent predeclared source of evidence appropriate to the claim.

Extended/composed corpora are stability checks unless they add independent data.

### I6 — bounded claim freeze

Only after the relevant controls may the record state a bounded claim and its explicit non-claims.

## Disposition

A record may have one of these dispositions independently from its epistemic status:

- `ACTIVE_ISOLATION`;
- `UNRESOLVED`;
- `RETAINED`;
- `EXPLAINED_AS_ARTIFACT`;
- `EXPLAINED_AS_LEAKAGE`;
- `EXPLAINED_AS_TRIVIAL_CONTROL_EFFECT`;
- `FALSIFIED`;
- `SUPERSEDED`.

No disposition deletes historical evidence.

`EXPLAINED_AS_ARTIFACT` is not equivalent to `never happened`; it preserves the diagnostic path that found the artifact.

## Re-discovery fingerprint

Each durable record should include a compact fingerprint intended to support later matching.

The fingerprint may contain only declared reporting metadata, for example:

- substrate/family;
- relation type such as equality, split, stasis, monotonicity, recollision, equivariance failure, or partition coincidence;
- observation class;
- control relation;
- bounded corpus scope;
- minimal-case identifiers where allowed.

The fingerprint is a retrieval aid, not evidence that two phenomena share a cause.

When a later experiment matches an older fingerprint, the older record must be surfaced before a new explanation is accepted.

## Anti-loss invariants

PETRA research must not:

- leave a material surprise only in transient terminal output;
- erase an unresolved observation because the active gate closes;
- discard a finding solely because it does not improve discrimination;
- require an immediate application/domain before preservation;
- overwrite the original expectation with a later explanation;
- treat failed explanations as grounds for deleting the underlying observation;
- merge independent replication and composition into one headline score.

## Anti-overclaim invariants

PETRA research must not:

- promote surprise directly to phenomenon;
- promote phenomenon directly to theorem;
- reinterpret an oriented or identity-bearing control as coordinate-free evidence;
- tune a frozen protocol after seeing the candidate in order to strengthen it;
- begin a later gate because a rabbit is exciting;
- use a rabbit level as a substitute for matched controls;
- convert unexplained persistence into a physical, semantic, temporal, or cosmological interpretation without a separately frozen contract.

## Gate separation

This protocol overlays the research pipeline but does not change gate ordering.

A phenomenon discovered inside Gate `N` may be isolated using controls that remain inside the declared semantics of Gate `N`.

If proper isolation requires a capability belonging to Gate `N+1` or later, the record remains `UNRESOLVED` or `CANDIDATE_PHENOMENON` until that gate is legitimately activated.

The phenomenon record may reference the future test, but may not smuggle it into the current gate.

## Relationship to Gate 3

Gate 3 provides originating evidence for this protocol because several important bounded findings emerged as secondary observations during attribution work and were preserved only because the normal loop was interrupted for focused verification.

Examples include:

- S1/P1/I1 common B0/D1 discrimination quotient;
- T1 terminal-sufficiency / no-recollision behavior;
- F1 native-order partition stasis under O1.

These examples motivate the method. They do not retroactively change Gate 3 protocols or results.

## Relationship to Gate 4

Gate 4 remains the next operational research gate after Gate 3.

This protocol does not activate Gate 4 and does not define its adversarial generator.

When Gate 4 is separately activated, this protocol may govern how unexpected mutation/collision behavior is captured and escalated.

## Completion criterion for recognition

The objective is not to explain every surprise immediately.

Recognition succeeds when PETRA can say, with durable provenance:

1. what unexpected thing was observed;
2. what was expected instead;
3. under exactly which protocol and source state it occurred;
4. whether it replayed;
5. which obvious explanations were tested;
6. what remains unresolved;
7. where the evidence can be recovered later;
8. what claim is and is not currently supported.

## Non-claims

This protocol does not establish that:

- every anomaly is valuable;
- serendipity can be guaranteed;
- surprise score equals scientific importance;
- rabbit level measures truth;
- automated anomaly detection can replace scientific judgment;
- preserved observations are patentable inventions;
- a replicated PETRA phenomenon generalizes outside its declared bounds.

## Formalized decision

PETRA adopts the following operating principle for exploratory research:

> **Serendipity is not merely the generation of an unexpected observation; it requires a research process capable of preserving, recognizing, isolating, and later re-identifying that observation without prematurely discarding or overclaiming it.**

This principle is operationalized by the Evidence Ledger, Rabbit Register, Unresolved Phenomena Register, Falsified Expectations Register, stop-the-line capture bundle, isolation sequence, stable phenomenon identifiers, and re-discovery fingerprints defined above.
