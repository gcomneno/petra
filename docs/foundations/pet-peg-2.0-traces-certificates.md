# PET/PEG 2.0 Traces, Certificates, and Exploration Boundary

This note defines the PET/PEG 2.0 trace and certificate layer.

The trace/certificate layer records and checks what happened.

It does not decide why a route was selected.

That separation is intentional:

- trace/certificate layer: what happened
- exploration-policy layer: why this path was tried first

> **Implementation-compatibility boundary.** The `NEW`, `DROP`, `INC`, and
> `DEC` trace examples below record current retained value-level behavior. The
> sole normative future operator contract is
> [`pet-peg-2.0-object-native-operators.md`](pet-peg-2.0-object-native-operators.md).

## Trace semantics

A PET/PEG 2.0 trace records one concrete graph path.

Current implementation:

- `PETTrace`
- `PETTraceStep`
- `trace_from_path(path)`

A trace records:

- root value
- target value
- depth
- value sequence
- operator-label sequence
- concrete path identity
- ordered steps

Each trace step records:

- step index
- source value
- target value
- operator
- structural address
- optional operator argument
- deterministic operator label
- application reason

Example:

    60 -- NEW(parent_address=[],q=7) --> 420

Trace summary:

    root_value = 60
    target_value = 420
    depth = 1
    values = [60, 420]
    labels = ["NEW(parent_address=[],q=7)"]

This records what happened.

It does not claim this route was optimal, preferred, useful, or selected by any
routing policy.

## Certificate semantics

A PET/PEG 2.0 trace certificate verifies that a trace can be replayed.

Current implementation:

- `PETTraceCheckStep`
- `PETTraceCertificate`
- `check_trace(trace)`
- `certificate_from_path(path)`

A certificate checks:

- recorded label matches the operator/address/argument tuple
- recorded source value matches the current replay value
- recorded operator can be applied
- replayed target value matches the recorded target value
- final replay value matches the trace target value

A valid certificate proves only this:

    the recorded trace is replayable under current PET/PEG 2.0 operator semantics

It does not prove:

- route quality
- route optimality
- factorization usefulness
- routing priority
- exploration completeness

## Replay/check procedure

Given a trace:

1. Start from `trace.root_value`.
2. Rebuild the corresponding PET object.
3. For each recorded step:
   - reconstruct the expected operator label
   - verify the label
   - verify the current source value
   - apply the recorded operator by value
   - verify the actual target value
4. After all steps, verify the final value equals `trace.target_value`.

If every check passes:

    valid = true
    reason = trace-replayed

## Replay/check failure reasons

Current failure reasons include:

- `label-mismatch`
- `source-value-mismatch`
- operator target/application failure reason
- `target-value-mismatch`
- `trace-target-mismatch`

These are certificate validity failures.

They are not route-quality judgments.

## Trace validity vs route quality

Trace validity and route quality are separate concepts.

A trace may be valid but strategically useless.

A trace may replay perfectly while being a terrible exploration choice.

Conversely, exploration policy may prefer a path, but that preference is not part
of the trace certificate.

Core rule:

    certificates validate replayability, not wisdom

## Exploration boundary

Exploration policy is outside this core layer.

The trace/certificate layer must not silently promote:

- routing heuristics
- anchor selection
- preferred path choice
- factorization-performance claims
- graph search strategy
- pruning strategy
- completeness claims

Those belong to a future explicit exploration-policy layer.

## Current implementation

Current implementation:

- `src/pet/traces.py`
- `PETTraceStep`
- `PETTrace`
- `PETTraceCheckStep`
- `PETTraceCertificate`
- `trace_from_path`
- `check_trace`
- `certificate_from_path`

Trace/certificate tests:

- `tests/test_traces.py`

Related graph/path layer:

- `src/pet/graph.py`
- `PETGraphPath`
- `PETGraphTraversal`
- `traverse_operator_graph_by_value`

## Boundary

This semantics does not claim:

- routing policy promotion
- anchor-selection change
- factorization performance
- stable CLI behavior changes
- exploration completeness
- PEG algebra completeness
