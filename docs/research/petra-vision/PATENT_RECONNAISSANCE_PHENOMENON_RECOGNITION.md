# PETRA VISION — Patent Reconnaissance: Phenomenon Recognition and Serendipity Preservation

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

Patent landscape / prior-art reconnaissance under the experimental `$brevetta` workflow.

Issue: #201.

Research date: 2026-08-24.

Related technical formalization:

- `PHENOMENON_RECOGNITION_PROTOCOL.md`;
- `PHENOMENA_REGISTER.md`.

This document is **not a legal opinion** and does not establish patentability, freedom to operate, validity, infringement, or absence of third-party rights.

Patent-status statements below are discovery observations from the cited databases as viewed on the research date unless an official register is explicitly identified. Google Patents itself warns that its legal-status and priority fields are assumptions rather than legal conclusions.

## Idea under reconnaissance

The idea is not a generic system for anomaly detection and not a generic electronic laboratory notebook.

The candidate technical concept is a computer-implemented research-governance mechanism that, upon a material unexpected observation:

1. preserves the observation together with the pre-existing expectation that it falsified or contradicted;
2. binds the record to protocol/input/source/revision/artifact provenance;
3. prevents premature loss or reinterpretation before deterministic replay and relevant controls;
4. manages attention priority separately from epistemic maturity;
5. preserves `UNRESOLVED` observations as durable first-class records;
6. later re-identifies potentially related observations through a non-causal retrieval fingerprint;
7. controls promotion from observation to pattern, phenomenon, replicated phenomenon, and bounded claim through explicit verification transitions;
8. respects research-gate boundaries so that an exciting anomaly cannot silently authorize a later experimental capability.

The originating PETRA use-case is scientific/computational research, but this reconnaissance tests the broader technical space rather than assuming PETRA-specific vocabulary creates novelty.

## Epistemic categories

This report uses:

- `FACT` — source-supported bibliographic or technical statement;
- `OBSERVATION` — relationship seen in the retrieved prior art;
- `HYPOTHESIS` — possible distinction requiring deeper search;
- `LEGAL CONCLUSION` — deliberately not produced here.

## Patent prior-art candidates

### PA-01 — WO2010086862A1 — Comprehensive electronic laboratory notebook

**FACT**

- Publication: `WO2010086862A1`.
- Applicant/assignee shown by Google Patents: SPARKLIX Ltd.
- Reported prior-art date: 2009-02-01.
- Google Patents reports the PCT application as `Ceased` and shows one WO family application; this status has not been independently converted into an FTO conclusion.
- Claim 16 expressly covers a processor configured to identify experimental results deemed abnormal relative to previously obtained experimental results.
- The disclosure concerns permanent experimental record-keeping, reproducibility, protocols, controls, experimental results, metadata, and analysis.

**OBSERVATION**

A broad claim that a research system should preserve experiments and automatically recognize abnormal experimental results is old and directly crowded.

**COLLISION AREA**

- abnormal-result recognition;
- ELN preservation;
- protocol/result storage;
- reproducibility context.

### PA-02 — US11593300B2 / US20220066986A1 — Anomaly-based retention policies for snapshot-based data protection systems

**FACT**

- Google Patents reports priority 2019-10-16 and an active US grant, `US11593300B2`.
- Claim 1 includes monitoring a runtime element, detecting an anomaly, and in response automatically marking a snapshot so that the marking overrides the ordinary retention policy.
- Dependent claims include longer retention and prevention of deletion while marked.
- The description supports automatic or prompted marking, anomaly thresholds, user feedback, and later changing a retention decision.

**OBSERVATION**

The technical chain `anomaly -> preserve snapshot beyond default retention` is explicitly patented in a non-scientific computing context.

**COLLISION AREA**

- event-triggered preservation;
- anomaly-dependent retention;
- automatic protection from deletion;
- importance marking.

### PA-03 — CN103745319B — Data provenance traceability based on multi-state scientific workflow

**FACT**

- Publication/grant: `CN103745319B`.
- The disclosure describes a multi-state scientific-workflow model with data lineage, versions, node relationships, process/data unified management, and traceability during scientific research and simulation workflows.

**OBSERVATION**

Scientific-workflow provenance plus explicit multiple states is established prior art. A broad claim to a stateful scientific workflow with lineage is unlikely to distinguish the PETRA concept.

**COLLISION AREA**

- multi-state scientific workflow;
- provenance/lineage;
- data version traceability;
- lifecycle monitoring.

### PA-04 — US10909503B1 — Snapshots to train prediction models and improve workflow execution

**FACT**

- Disclosure covers scientific/business/operating-system workflow hierarchy, workflow snapshots, parameters, inputs, obtained results, quality metrics, and provenance gathered during execution.
- It uses snapshots as workflow-execution representations for later prediction/optimization.

**OBSERVATION**

Capturing workflow state plus provenance around execution is not a distinguishing concept by itself.

**COLLISION AREA**

- workflow snapshot;
- before/after execution state;
- result/provenance capture;
- later model use.

### PA-05 — US20240311727A1 — Method for automatically documenting a laboratory workflow

**FACT**

- Applicant shown by Google Patents: LabTwin GmbH.
- Reported priority: 2023-03-15.
- Google Patents reports the US application as `Abandoned`; this does not establish that related rights are absent elsewhere.
- Claim 1 covers AI classification of unstructured laboratory workflow data into a predefined template with classification-certainty values.
- When certainty is below a threshold, the system prompts another user to classify the information.
- The description also allows information belonging to classes outside the template to be appended or escalated for action.

**OBSERVATION**

Automated laboratory capture plus uncertainty-triggered human escalation is crowded prior art.

**COLLISION AREA**

- laboratory workflow documentation;
- confidence threshold;
- human review/escalation;
- out-of-template observations.

### PA-06 — US20250259042A1 and related QOMPLX application network

**FACT**

- Publication: `US20250259042A1`.
- Google Patents reports priority 2024-02-08, filing 2025-02-18, publication 2025-08-14, and status `Pending`.
- Google Patents lists related priority applications/publications including `US20250259041A1`, `US20250259043A1`, `US20250259044A1`, `US20250259085A1`, and `US20250390352A1` around the same 2024-02-08 priority lineage.
- The disclosure describes context-sensitive surprise metrics, novelty detection, continuous surprise computation, and stochastic memory retention.
- A scientific-discovery example assigns higher retention probability to unexpected experimental results that deviate from theoretical predictions and considers possible future value.
- The currently displayed independent claim 1 of `US20250259042A1` is directed primarily to orchestration of collaborative AI agents rather than expressly claiming the scientific surprise-retention example as the independent-claim core.

**OBSERVATION**

This is the closest retrieved disclosure to the high-level proposition `unexpected scientific result -> increased probability of preserving it because it may later be valuable`.

The fact that this appears in the specification even where the displayed independent claim focuses on a broader agent platform still makes it material prior-art territory for novelty/inventive-step reconnaissance.

**COLLISION AREA**

- surprise/novelty metric;
- unexpected experimental result;
- adaptive memory retention;
- avoiding premature discard;
- possible future utility;
- context-dependent surprise.

### PA-07 — US9038172B2 — Robust anomaly detection with scientific-experiment examples

**FACT**

The background expressly recognizes anomalous measurements in scientific experiments as potentially indicating either equipment glitches or interesting phenomena.

**OBSERVATION**

The epistemic ambiguity `artifact versus interesting phenomenon` is not itself new. Generic anomaly detection applied to scientific measurements is well established.

**COLLISION AREA**

- anomalous scientific measurement;
- glitch versus phenomenon;
- statistical anomaly detection.

### PA-08 — Workflow pause/interruption families

Representative retrieved publications include:

- `US20240192985A1` — workflow error detection with pause, correction, replay/resume; continuation lineage tracing back to a 2019 provisional;
- `US12619458B2` — interruption detection during automated workflow, score/threshold-driven pause and user resolution;
- `US20240177082A1` — automated laboratory workflow recovery after a detected stoppage.

**OBSERVATION**

The generic control flow `detect event/error -> pause workflow -> preserve/inspect state -> user intervention -> resume` is crowded.

**COLLISION AREA**

- stop-the-line mechanics;
- event-triggered pause;
- workflow-state preservation;
- human intervention and resume.

### PA-09 — CN119105317A — Scientific-research automation comparing expected and actual results

**FACT**

The retrieved disclosure describes an automated scientific-research system in which an agent compares an expected result with an actual experimental result. If the experiment does not meet expectation, another model adjusts design parameters and generates a new trial plan, iterating until requirements are met.

**OBSERVATION**

The relation `expected experimental result -> actual result comparison -> workflow action` is also occupied territory.

The PETRA method therefore cannot rely on mere expected-versus-actual comparison as its differentiator.

**COLLISION AREA**

- explicit expected/actual experimental comparison;
- automated feedback;
- parameter adjustment;
- iterative re-execution.

## Non-patent prior art

### NPL-01 — Bowers et al., 2006 — User-oriented data provenance in pipelined scientific workflows

**FACT**

`A Model for User-Oriented Data Provenance in Pipelined Scientific Workflows`, IPAW 2006, DOI `10.1007/11890850_15`, explicitly motivates scientific-workflow provenance as useful to reproduce earlier results and explain unexpected results.

**OBSERVATION**

Provenance specifically for explaining unexpected scientific results predates the PETRA concept by approximately two decades.

### NPL-02 — Yaqub, 2018 — Serendipity: Towards a taxonomy and a theory

**FACT**

Research Policy 47(1), DOI `10.1016/j.respol.2017.10.007`, classifies multiple types and mechanisms of serendipity, including observer-led, error-borne, theory-led, and network-emergent mechanisms.

**OBSERVATION**

Scientific serendipity and mechanisms for recognizing unexpected beneficial discoveries are a mature conceptual research area.

### NPL-03 — Thompson & Copeland, 2023 — Patterns for paying attention

**FACT**

`Serendipity in research and development: The promise of putting into place patterns for paying attention`, Drug Discovery Today 28(8), article 103648, DOI `10.1016/j.drudis.2023.103648`.

The paper explicitly argues that R&D organizations can structure themselves to acknowledge and realize accidental discoveries and distinguishes this from deterministic `engineering serendipity`.

**OBSERVATION**

The broad organizational thesis that the problem is paying attention to accidental value rather than manufacturing serendipity is directly represented in non-patent literature.

## Crowded concepts

The reconnaissance finds strong prior art for each of the following in isolation, and in several partial combinations:

- recording complete experiments and provenance;
- recognizing abnormal or anomalous experimental results;
- comparing expected and actual results;
- using anomaly/surprise metrics;
- increasing retention in response to anomaly or surprise;
- preserving workflow snapshots;
- multi-state scientific workflows;
- pausing workflows when an interruption/error is detected;
- escalating uncertain classifications to a human;
- using provenance to reproduce/explain unexpected scientific results;
- organizational patterns for noticing accidental discoveries.

A patent position framed at any of those levels would face substantial prior-art pressure.

## Candidate differentiation hypothesis

### HYPOTHESIS H-01 — Epistemic preservation capsule

A potentially narrower differentiator is the atomic preservation of an **epistemic capsule**, not merely a computational snapshot.

The capsule would bind at first material surprise:

- the prior expectation in its pre-explanation form;
- the unexpected observation;
- declaring protocol and frozen parameters;
- input/corpus identity;
- source/revision identity;
- source and artifact digests;
- raw/derived outputs;
- current attention level;
- current epistemic maturity;
- permissible next transitions.

The prior expectation is historical evidence and cannot be rewritten by a later explanation.

### HYPOTHESIS H-02 — Orthogonal state machines

Use two independent state dimensions:

1. an attention/escalation state such as rabbit level;
2. an epistemic-maturity state such as `OBSERVATION -> PATTERN -> CANDIDATE_PHENOMENON -> REPLICATED_PHENOMENON -> CLAIM_CANDIDATE`.

This prevents urgency/interestingness from being treated as evidential maturity.

The reconnaissance has not yet found a document combining these two explicit dimensions for scientific-surprise governance.

### HYPOTHESIS H-03 — Gate-local preservation barrier

When a surprise crosses a predeclared threshold, the system creates the capsule and applies a gate-local barrier preventing protocol/input/parameter changes that would destroy the declaring context until required capture/replay fields are satisfied.

This differs from pausing a workflow merely because execution cannot continue: the purpose is preservation of causal interpretability rather than operational recovery.

### HYPOTHESIS H-04 — Durable unresolved state with anti-dismissal invariant

The system makes `UNRESOLVED` a durable first-class disposition and prohibits `IRRELEVANT` as a same-event first classification for a material surprise.

The purpose is to prevent later reinterpretation from erasing the original anomaly without simultaneously promoting it to a scientific claim.

### HYPOTHESIS H-05 — Re-discovery before explanation

Each unresolved/candidate phenomenon receives a retrieval fingerprint describing its relation class, substrate, controls, and bounded scope without asserting common cause.

A later experimental observation that matches the fingerprint must surface the historical record before accepting a fresh explanation.

This is different from ordinary similarity search if it is technically coupled to the epistemic lifecycle and provenance bundle.

### HYPOTHESIS H-06 — Verification-transition machine

Promotion is conditioned on explicit transitions such as:

`capture -> exact replay -> minimal positive/negative isolation -> one-variable controls -> leakage audit -> synthetic necessity falsification -> independent replication -> bounded claim freeze`.

The novelty hypothesis is not any individual transition. It is their use as a machine-enforced provenance-preserving maturation path for unexpected scientific observations.

## Candidate invention nucleus

The strongest candidate nucleus found in this reconnaissance is:

> A computer-implemented mechanism that responds to a scientifically material expectation violation by atomically preserving a provenance-bound expectation/observation capsule, enforcing a local immutability/pause boundary on the declaring experiment until reproducibility capture is complete, tracking attention and epistemic maturity as independent state dimensions, retaining unresolved observations without dismissal, and re-surfacing earlier unresolved records upon later fingerprint matches before permitting claim promotion.

This formulation is a **HYPOTHESIS OF DIFFERENTIATION**, not a patentability conclusion and not a draft claim asserted to be novel.

## Collision / risk matrix

| Candidate element | Prior-art pressure | Initial assessment |
| --- | --- | --- |
| anomaly recognition | very high | crowded |
| abnormal experimental-result recognition | very high | directly disclosed/claimed |
| anomaly-triggered retention | very high | directly claimed outside science |
| scientific provenance | very high | mature prior art |
| expected vs actual comparison | high | disclosed in scientific automation |
| workflow pause | very high | mature workflow art |
| human escalation under uncertainty | high | laboratory workflow art |
| surprise-based long-term retention | very high | QOMPLX disclosure is especially close |
| preserve prior expectation immutably with surprise | medium/unknown | deeper search required |
| separate attention from epistemic maturity | medium/unknown | no close match yet found |
| durable unresolved anti-dismissal state | medium/unknown | deeper search required |
| gate-local barrier protecting declaring scientific context | medium/unknown | deeper search required |
| fingerprint-driven re-discovery before reinterpretation | medium/unknown | deeper search required |
| integrated verification-transition machine | medium/unknown | likely obviousness/inventive-step pressure |

## Patentability / eligibility caution

### OBSERVATION

The broad concept can easily look like research administration, scientific method, or information organization implemented in software.

### HYPOTHESIS

Any future filing strategy would likely need to articulate a concrete computer-system mechanism and technical effect beyond a rule for human reasoning or scientific judgment.

Examples requiring professional analysis include atomic provenance capture, immutable/content-addressed state, enforcement barriers in an experiment orchestration system, machine state transitions, and retrieval behavior tied to later event fingerprints.

### LEGAL CONCLUSION

`UNRESOLVED`.

Questions of patent eligibility, inventive step/non-obviousness, novelty, claim scope, and FTO require deeper patent search and professional IP review if filing becomes material.

## Expired / abandoned material

Two discovery examples in this reconnaissance are reported by Google Patents as ceased/abandoned:

- `WO2010086862A1` — reported ceased;
- `US20240311727A1` — reported abandoned.

This does **not** mean `free to copy`.

The reconnaissance has not established absence of other jurisdictional members, continuations, later patents, or overlapping third-party claims covering related technical combinations.

## Search gaps

The following searches remain necessary before any filing-oriented conclusion:

1. claim-by-claim family search around QOMPLX surprise/retention disclosures;
2. CPC/IPC search for anomaly-triggered scientific-data retention and ELN/LIMS exception workflows;
3. patent search for immutable expectation/hypothesis versioning bound to experimental results;
4. patent search for dual-axis confidence/importance versus evidence-maturity state machines;
5. patent search for unresolved-observation registries and delayed re-discovery/cross-experiment similarity matching;
6. patent search for machine-enforced experiment immutability following anomaly capture;
7. family/status validation in official registers for any document material to a filing or FTO decision;
8. non-patent search across scientific workflow, open-science provenance, anomaly triage, lab informatics, incident-management, MLOps, and knowledge-management literature;
9. targeted obviousness/inventive-step combination analysis rather than novelty-only keyword matching.

## Triage decision

`DEEPER PATENT SEARCH`

Rationale:

- broad serendipity-preservation and anomaly-retention ideas are strongly crowded;
- several individual mechanisms are directly disclosed or claimed;
- nevertheless, the integrated epistemic lifecycle has a narrower technical nucleus not yet matched closely enough by this first reconnaissance to justify `STOP`;
- the same evidence is insufficient to justify a patentability conclusion or filing recommendation.

Technical research under issue #201 may continue. `DEEPER PATENT SEARCH` does not mean FTO clearance and does not authorize a patent filing.

If filing becomes a real objective, the next legal gate is `PROFESSIONAL IP REVIEW` after a deeper search package exists.

## Current conclusion boundary

### FACT

There is substantial prior art around abnormal-result detection, scientific provenance, workflow snapshots, anomaly-triggered retention, workflow pause/recovery, surprise-based memory retention, expected-versus-actual comparison, and organizational serendipity recognition.

### OBSERVATION

PETRA's strongest apparent distinction is not preservation alone but **preservation of epistemic history and controlled maturation** around an unexpected observation.

### HYPOTHESIS

A sufficiently concrete implementation of expectation-preserving, provenance-bound, gate-local phenomenon maturation and re-discovery may contain a protectable technical combination.

### LEGAL CONCLUSION

`UNRESOLVED`.

No statement in this report should be read as `PATENTABLE`, `FREE_TO_USE`, `FTO_CLEAR`, `NON_INFRINGING`, or equivalent.
