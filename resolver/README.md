# Resolver

A bounded A* search over PETRA canonical shapes.

Given two canonical PETRA shapes, the Resolver finds the shortest sequence
of SPROUT, SHED, GRAFT, and PRUNE invocations that transforms the source
shape into the target shape.

The Resolver is a derived layer. It imports from the canonical `petra`
package and never the other way around. It does not extend PETRA semantics
and does not modify the PETRA runtime.

## Requirements

- Python 3.10 or later
- The `petra` package must be installed. The Resolver does not declare
  `petra` as a dependency to avoid pulling an unrelated distribution from
  PyPI. Install PETRA first, then install the Resolver.

## Installation

From the repository root:

~~~bash
pip install -e .
pip install -e ./resolver
~~~

This installs both `petra` and `resolver` as editable packages.

## Command line

~~~bash
resolver SOURCE TARGET [options]
~~~

Example:

~~~bash
resolver "1" "C(r0^C(r0^C(r0^1)))"
~~~

Options:

- `--max-depth N` -- maximum number of steps (default: 10)
- `--max-nodes N` -- maximum node count per shape (default: 20)
- `--max-visited N` -- maximum distinct shapes explored (default: 1000)
- `--key-json STR` -- optional JSON object mapping positional addresses to
  primes, e.g. `{"@/0":2,"@/1":3}`
- `--json` -- emit a single compact JSON document

When `--key-json` is supplied, the Resolver also computes the numeric
projection of the source, the target, and each step. Projection is
optional and external; it never influences the search.

## Python API

~~~python
from resolver import PrimeKey, resolve, project

path = resolve("1", "C(r0^C(r0^1))")
for step in path.steps:
    print(step.operator.value, step.after_shape)

key = PrimeKey({(0,): 2, (0, 0): 3})
value = project(path.target, key)
~~~

## Algorithm

The Resolver uses A* with an admissible heuristic based on three structural
lower bounds:

- node-count distance divided by 2
- maximum-depth distance
- leaf-count distance

Each canonical operator changes node count by exactly plus or minus 2, and
changes maximum depth and leaf count by at most 1. The maximum of these
three distances is therefore a lower bound on the number of remaining
steps, and A* is optimal whenever it finds a path.

## Performance

On tower and flat shapes of size N, the Resolver explores exactly N + 1
shapes before reaching the target. This is the optimal exploration
signature: every step makes progress.

Empirical measurements:

| Depth or width | Time | Shapes explored |
| ---: | ---: | ---: |
| 10 | 0.015s | 11 |
| 50 | 0.7s | 51 |
| 100 | 5.7s | 101 |
| 200 | 42s | 201 |
| 500 | more than 120s | -- |

The cost grows as O(N squared): each step rebuilds the entire shape
(PETRA shapes are immutable), and there are N steps. This is a property
of the PETRA runtime, not of the search.

## Bounds

All searches are bounded by `max_depth`, `max_nodes`, and `max_visited`.
A search that cannot find a path within the bounds raises
`ResolverError`.

## Projection

The projection layer converts a shape into a numeric value given an
explicit `PrimeKey`. It does not derive the key; the caller supplies it.
Projection refuses to materialize values beyond a fixed bit bound, so a
path can be found even when the numeric value of its endpoints cannot be
computed. In that case, the CLI shows a question mark for the missing
values.

## Boundary

The Resolver:

- does not modify PETRA
- does not introduce new PETRA operators
- does not claim to factorize integers
- does not claim to compress values
- does not influence PETRA canonical semantics

It is a structural search over the graph induced by PETRA canonical
operators, with an optional numeric projection layer.
