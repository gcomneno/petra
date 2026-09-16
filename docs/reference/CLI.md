# PETRA CLI Reference

The maintained command-line interface is:

```text
petra SHAPE_TEXT INVOCATION_JSON
```

This document describes only the canonical minimal PETRA CLI implemented by
`petra.cli:main`. It does not preserve the historical PET command surface.

The normative semantics remain in [`SPEC.md`](SPEC.md).

## Inputs

The CLI accepts exactly two positional arguments:

1. `SHAPE_TEXT` — one canonical PETRA shape in the textual grammar;
2. `INVOCATION_JSON` — one strict PETRA operator invocation JSON document.

Extra or missing CLI arguments are rejected by the command-line parser.

### Shape text

Canonical examples include:

```text
1
C(r0^1)
C(r0^1,r1^C(r0^1))
```

The accepted grammar and resource limits are defined by the canonical PETRA
serialization contract and specification.

Malformed shape text is a transport error:

```text
petra: shape-text-malformed
```

and exits with status `2`.

## Invocation JSON

The invocation schema is:

```json
{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}
```

The JSON document must contain exactly:

- `schema`;
- `operator`;
- `target`.

The supported canonical operators are exactly:

- `SPROUT`;
- `SHED`;
- `GRAFT`;
- `PRUNE`.

Historical PET operator names such as `NEW`, `DROP`, and `INC` are not PETRA
compatibility aliases and are rejected as invalid invocations.

### Default target

A default invocation uses exactly:

```json
{"mode":"default"}
```

Example:

```bash
petra '1' '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}'
```

### Explicit target

An explicit invocation uses exactly:

```json
{"mode":"explicit","address":"@/0/^"}
```

Example:

```bash
petra 'C(r0^1)' '{"schema":"petra.operator-invocation.v1","operator":"GRAFT","target":{"mode":"explicit","address":"@/0/^"}}'
```

Addresses use the canonical positional PETRA address syntax defined by the
specification.

## Output

The CLI writes exactly one canonical compact JSON result document to standard
output, followed by one transport newline.

The result schema is:

```text
petra.operator-result.v1
```

Successful results include the normalized operator invocation, resolved target,
before/after shapes, and canonical address effects. Failed results include the
available normalized state and one stable failure reason as defined by the
runtime contract.

The serializer determines key ordering and compact JSON formatting; callers
should consume the JSON structure rather than depend on visual field order.

## Exit status

The maintained transport behavior is:

- `0` — operator result status is `ok`;
- `1` — invocation parsing or operator execution produced a canonical failed
  PETRA result;
- `2` — command-line argument parsing or shape transport parsing failed.

Canonical failed operator results are written to standard output as JSON.
Transport-level shape errors are written to standard error.

## Installation boundary

A maintained installation exposes the console entry point:

```text
petra = petra.cli:main
```

The historical `pet` console command is not part of the maintained PETRA
distribution.

The repository may temporarily retain historical `src/pet/` source during
Phase 10 migration, but that package is not a maintained installed surface.

## Non-features

The minimal PETRA CLI does not expose the former PET utilities for:

- integer encode/decode;
- prime factorization;
- PET metrics;
- graph/path exploration;
- scans, atlases, or dataset queries;
- historical rewrite/operator compatibility.

Such historical functionality does not become PETRA behavior merely because it
existed in the former runtime.
