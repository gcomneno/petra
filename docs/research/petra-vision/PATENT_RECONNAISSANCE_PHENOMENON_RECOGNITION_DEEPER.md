# PETRA VISION — Deeper Patent Search: Phenomenon Recognition

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Second-pass patent and non-patent prior-art search following the initial reconnaissance in `PATENT_RECONNAISSANCE_PHENOMENON_RECOGNITION.md`.

Issue: #201.

Search date: 2026-08-24.

This is research reconnaissance only. It is not a legal opinion and does not establish novelty, inventive step/non-obviousness, patent eligibility, FTO, validity, infringement, or claim scope.

## Question tested

The first reconnaissance left six possible differentiation hypotheses:

1. provenance-bound **epistemic capsule** containing prior expectation plus unexpected observation;
2. independent **attention** and **epistemic-maturity** state dimensions;
3. a **gate-local preservation barrier** that protects the declaring context before tuning or scope expansion;
4. durable **UNRESOLVED** retention with an anti-dismissal invariant;
5. later **re-discovery** of related unresolved events through a fingerprint;
6. a machine-enforced **verification-transition path** from capture through replay, controls, falsification, replication, and bounded claim freeze.

The deeper search tests whether these survive once expected-outcome modeling, probationary hypothesis stores, historical anomaly matching, and research automation are included.

## Additional material prior art

### DP-01 — US20090138415A1 — Automated research systems and methods for researching systems

**FACT**

- Google Patents reports a 2007-11-02 priority for the application and an `Abandoned` application status; related later applications are listed and must be treated separately from that status.
- The disclosure is explicitly directed to automated research, including biological research.
- It models an `Experiment` with a system state, modification specification, and **Expected Outcome**.
- It models an `Experiment Outcome Object` with the actual experiment result.
- It defines an **Expected Outcome Set**, including possible results, estimated probabilities, and value-of-information measures.
- Execution produces an outcome and updates a knowledge base.
- Claim 6 broadly includes an automated research system with experiment objects, an experiment director, result analysis, a knowledge model, comparison of results to the knowledge model, and update of that model.

**OBSERVATION**

The broad idea of explicitly representing expected experimental outcomes before execution, then preserving actual outcomes and updating research knowledge, is old automated-research prior art.

**IMPACT ON H-01**

The candidate distinction cannot be `store expectation + actual observation` alone.

What remains potentially different is the narrower historical-evidence rule that the **pre-observation expectation is frozen as a provenance object and cannot be overwritten by the later explanatory model**, together with the surprise-triggered maturation lifecycle.

That narrower combination remains unverified, not established novel.

### DP-02 — US12093311B2 / related AIEconomy family — probationary hypothesis storage and later promotion

**FACT**

- Google Patents reports priority 2020-02-21 and an active US grant for `US12093311B2`.
- Independent claim 1 includes a context-aware AI database, a **probationary database**, generation of a hypothesis object with metadata, training/testing producing experimental results, storage of lower-performing hypothesis/results in the probationary database, and storage of successful results in the main context-aware database.
- The claim further recites later transfer from probationary storage when a subsequent result meets the performance criterion.
- The description states that probationary hypotheses may be retained, trended over time, retested as new data/variables become available, and recalled/refined for further testing.
- Google Patents lists related continuation/CIP activity extending the architecture to other domains, including medical/genetic analytics and industrial systems.

**OBSERVATION**

This is a strong collision against any broad claim that PETRA is distinctive because it gives uncertain/unsuccessful hypotheses a durable non-final state and later promotes them after further evidence.

**IMPACT ON H-04 AND H-06**

- `UNRESOLVED/probationary retention` alone is not a credible differentiator.
- threshold/state-based later promotion of a hypothesis after further experiments is also occupied territory.

A PETRA distinction would need to be more specific than `keep weak results for later retesting`.

### DP-03 — Historical anomaly matching and anomaly case bases

**FACT**

Retrieved anomaly-management disclosures in monitoring/security/industrial contexts store historical anomaly records, derive fingerprints or feature vectors, and compare later anomalies with historical cases using similarity measures.

Examples retrieved in the deeper search include current anomaly case libraries with stored characteristics/context and similarity matching against new events.

**OBSERVATION**

The generic concept `create fingerprint for anomaly -> later compare a new anomaly with historical anomalies` is crowded outside scientific research.

**IMPACT ON H-05**

Re-discovery by similarity/fingerprint alone is not a strong differentiator.

What remains potentially different is a technical coupling in which a fingerprint match is attached to an immutable scientific expectation/observation provenance record and affects permissible **epistemic-state transitions**, while explicitly not asserting common cause.

That combination still faces obviousness/inventive-step pressure.

### DP-04 — Diagnosis systems with priority/confidence/hypothesis ranking

**FACT**

Long-standing diagnostic prior art separately represents hypotheses, confidence values, preference/priority functions, observations, and repeated hypothesis selection/evaluation.

Representative retrieved material includes `WO2012052281A1` / `US20130268809A1`, where diagnoses/hypotheses are prioritized using confidence and preference functions, then updated using observed system information.

**OBSERVATION**

Maintaining more than one metadata dimension around a hypothesis—e.g. confidence and priority—is not new in itself.

**IMPACT ON H-02**

The PETRA distinction cannot simply be `two scores instead of one`.

The narrower hypothesis is that **attention priority and evidentiary maturity have independent transition semantics**, including states that cannot be skipped merely because attention is high.

No close scientific-research disclosure of that exact lifecycle was identified in this pass, but the structural idea is likely vulnerable to combination/obviousness arguments.

### DP-05 — Workflow error/interruption pause and replay

**FACT**

Previously retrieved workflow patent families implement event/error/interruption detection followed by pausing, preserving workflow state, user intervention, correction, replay, and resumption.

**OBSERVATION**

A `stop-the-line` control is not patentably distinctive merely because it pauses an automated process.

**IMPACT ON H-03**

The narrower PETRA distinction is the reason and invariant enforced by the barrier: preserving the **declaring scientific causal context** from post-surprise parameter/protocol mutation before evidence capture/replay is complete.

The deeper search did not locate an exact anticipation of that rule, but it may be viewed as an obvious application of workflow locking/checkpointing unless tied to a concrete system effect.

### DP-06 — Deviation from prior expectation as an “interesting” event

**FACT**

Other computer systems already treat a large deviation from prior expectation as a signal of interest or importance and use such deviations to select/report content.

**OBSERVATION**

`surprise = deviation from expectation` and `high surprise deserves attention` cannot carry the inventive concept.

This reinforces the need to separate the candidate mechanism from generic surprise scoring.

## Non-patent pressure after deeper search

### D-NPL-01 — “Patterns for paying attention”

The 2023 R&D literature explicitly frames serendipity as requiring organizations prepared to notice and realize value already present in ordinary research outputs, rather than deterministic engineering of serendipity.

This is conceptually very close to the PETRA motivation.

### D-NPL-02 — Scientific provenance for unexpected results

Bowers et al. (2006) expressly presents workflow provenance as a mechanism for reproducing earlier results and explaining unexpected results.

### D-NPL-03 — Surprise and scientific impact

Contemporary science-of-science literature treats surprise as disruption of expectations and studies its relation to scientific impact and new claims.

**OBSERVATION**

The philosophical and organizational framing is clearly prior art/non-patent knowledge. Any protectable subject, if one exists, must therefore lie in a concrete computer-system architecture rather than the insight that serendipity requires recognition.

## Differentiation hypotheses after deeper search

### H-01 — Epistemic capsule

**STATUS: WEAKENED BUT NOT ELIMINATED**

Prior art covers expected outcomes, actual outcomes, knowledge-base update, scientific provenance, and anomaly-triggered snapshot retention.

Residual candidate:

> atomically bind a **historical pre-observation expectation version** to the unexpected result and its executable provenance, with the expectation object made non-overwritable by subsequent explanatory hypotheses.

Risk: likely combination/obviousness and software-eligibility pressure.

### H-02 — Independent attention and epistemic maturity

**STATUS: WEAKENED**

Priority and confidence are separately known metadata dimensions.

Residual candidate:

> two orthogonal machine state variables with distinct transition guards, where an attention escalation cannot advance evidentiary maturity and evidentiary maturity cannot erase attention history.

Risk: may be treated as abstract information classification unless tied to concrete orchestration behavior.

### H-03 — Gate-local preservation barrier

**STATUS: SURVIVES AS NARROW CANDIDATE**

Pause/recovery/checkpointing are known.

Residual candidate:

> a surprise-triggered barrier that locks mutation of the declaring experimental protocol/input/parameter set until a content-addressed evidence capsule and exact replay checkpoint have been committed, while leaving the wider research system operable and without activating later-scope capabilities.

Potential technical contribution: preserving reproducibility/causal auditability in an adaptive experiment-orchestration system.

Risk: obviousness relative to checkpoint/transaction/immutability systems.

### H-04 — Durable unresolved state

**STATUS: SUBSTANTIALLY COLLIDED**

The AIEconomy probationary-database claims and description are strong art for storing weak hypotheses/results and later promoting them after new evidence.

Residual anti-dismissal wording is governance, not yet a convincing technical distinction.

### H-05 — Re-discovery fingerprint

**STATUS: SUBSTANTIALLY COLLIDED IN ISOLATION**

Historical anomaly fingerprint/similarity matching is common.

Residual candidate only exists as part of the larger epistemic/provenance transition architecture.

### H-06 — Verification-transition machine

**STATUS: SURVIVES ONLY AS INTEGRATED COMBINATION**

Individual components—replay, matched controls, human review, confidence thresholds, probationary state, provenance—are known.

The deeper search did not find an exact single reference implementing the PETRA sequence:

`surprise capture -> expectation-preserving provenance freeze -> exact replay -> isolation/matched controls -> leakage qualification -> synthetic necessity falsification -> independent replication -> bounded claim freeze`

However, absence of one matching keyword result is **not evidence of novelty**, and an examiner could combine references.

## Revised candidate nucleus

After the deeper search, the candidate nucleus is narrower:

> **A transactional scientific-observation preservation mechanism for adaptive computational experimentation that, upon an expectation-violation event, atomically commits a non-overwritable pre-observation expectation together with executable experiment provenance and the unexpected result; activates a local mutation barrier until an exact replay checkpoint is committed; and thereafter controls independent attention and epistemic-maturity state transitions while preserving the original expectation/history across later reinterpretation and cross-experiment retrieval.**

The following are explicitly removed from the nucleus because prior art is too strong:

- generic anomaly detection;
- generic scientific provenance;
- generic ELN capture;
- generic expected-versus-actual comparison;
- generic anomaly-triggered retention;
- generic workflow pause;
- generic human escalation;
- generic unresolved/probationary storage;
- generic hypothesis promotion after later success;
- generic anomaly fingerprint similarity search;
- generic surprise-based memory retention.

## Technical-effect question

The critical patent question is now not “is the method philosophically new?”

It is:

> Does the transactional expectation/provenance freeze plus mutation barrier solve a concrete technical problem in adaptive scientific workflow execution—such as loss of reproducibility or causal auditability caused by post-anomaly mutation of executable experiment state—in a manner not taught or obvious from the combined prior art?

This question cannot be answered by the current documentary protocol alone.

It requires a concrete implementation architecture and a claim-oriented search around transactions, content-addressed scientific experiment state, immutable provenance, event-sourced experiment orchestration, and experiment checkpoint locking.

## Revised risk assessment

| Area | Risk after deeper search |
| --- | --- |
| broad serendipity-recognition concept | extreme |
| anomaly-triggered preservation | extreme |
| expected/actual scientific outcome representation | extreme |
| durable unresolved/probationary hypothesis state | extreme |
| later promotion after new evidence | extreme |
| historical anomaly fingerprint matching | very high |
| attention/confidence metadata | very high |
| scientific provenance | extreme |
| workflow pause/replay | extreme |
| immutable historical expectation bound to executable provenance | medium/unknown |
| surprise-triggered local mutation barrier for causal auditability | medium/unknown |
| full integrated transactional epistemic lifecycle | high obviousness risk / unknown novelty |

## Filing-readiness assessment

### FACT

The broad idea is heavily pre-populated by patent and non-patent art.

### OBSERVATION

After two search passes, the only potentially interesting IP territory is a narrow technical implementation of **historical expectation preservation + executable provenance transaction + adaptive-workflow mutation barrier**, possibly combined with guarded epistemic-state transitions.

### HYPOTHESIS

If PETRA later implements this as an actual orchestration mechanism with measurable reproducibility/auditability behavior, there may be enough concrete structure to justify a professional claim-oriented search.

### LEGAL CONCLUSION

`UNRESOLVED`.

No patentability or FTO conclusion is supported.

## `$brevetta` triage gate

**STUDY**

Rationale:

- `STOP` would be too strong because a narrow technical nucleus remains insufficiently tested;
- immediate filing is not justified because the broad concept and many constituent mechanisms are crowded;
- another generic keyword search is unlikely to resolve the central question without a concrete technical architecture;
- the next useful evidence is an implementation-level design showing exactly what state is atomically frozen, what mutations are blocked, what is content-addressed, how replay is verified, and what computer-system failure mode is prevented.

If that technical design produces a distinctive mechanism, the patent path should move to:

`PROFESSIONAL IP REVIEW`

with a claim chart against at least the strongest families identified in the two reconnaissance documents.

## Protection posture meanwhile

Until the technical nucleus is resolved:

- retain the protocol and patent reconnaissance as confidential/private research;
- do not market the broad “recognize serendipity” framing as a patentable invention;
- preserve implementation dates, commits, digests, and authorship/provenance;
- avoid assuming that abandoned/ceased publications imply freedom to use;
- keep the patent question separate from the scientific value of the protocol.

The research-governance protocol remains valuable even if no patentable technical invention ultimately exists.
