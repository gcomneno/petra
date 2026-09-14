# Security Policy

## Scope

PETRA is a pure-computation library. It does not:

- accept network input;
- read or write files as part of its public API;
- deserialize untrusted data (the CLI parses JSON with the standard library,
  but only as canonical operator-invocation transport defined by the
  specification);
- execute code on behalf of the caller;
- spawn subprocesses.

The canonical runtime under `src/petra/` is the only maintained surface. Any
code under `src/pet/` or `tools/` is historical Phase 10 migration residue and
is not supported.

## Reporting a vulnerability

If you believe you have found a security issue in the canonical PETRA runtime,
please report it privately to:

<https://github.com/gcomneno/petra/security/advisories/new>

Alternatively, contact the maintainer by email:

**giancarlo.cicellyn@gmail.com**

Please include:

- a description of the issue;
- a minimal reproducer;
- the exact PETRA version (`petra --version`);
- the Python version.

Please do not open a public issue for security-sensitive reports.

## Response

Reports are acknowledged within a reasonable time. Because PETRA has no
external dependencies in its runtime and no I/O in its public API, the
expected attack surface is limited; reports will be triaged accordingly.

## Supported versions

Only the latest 1.x release is supported. Version line `0.1.x` through
`0.3.x` belong to the historical PET runtime and are not maintained.
