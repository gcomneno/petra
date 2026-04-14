# PET grammar note (bounded empirical)

## Scope

This note records a bounded empirical PET rewriting grammar observed from
generator-family transition experiments.

It does **not** claim a theorem or a complete global theory.
It records reproducible bounded behavior in the tested range.

## Checked setup

- source values: `2..100000` for transition-law extraction
- tested local primes: `2, 3, 5, 7, 11, 13, 17, 19, 23, 29`
- guarded normal-form stress test:
  - start values: `2..1000`
  - test primes: `2, 3, 5`
  - word length: `4`
  - valid tested words: `413070`

## Primitive moves

We use four elementary PET moves on a number `n` and track only the target
generator family.

- `NEW`: multiply by a prime not already present in the support
- `DROP`: remove a prime of exponent `1`
- `INC`: multiply by a prime already present
- `DEC`: divide by a prime already present

## Bounded empirical transition laws

The currently strongest bounded formulations reached so far are:

- `T_new ~ g`
- `T_drop ~ g`
- `T_inc ~ (g, gen(e), gen(e+1))`
- `T_dec ~ (g, gen(e), gen(e-1))`

where:
- `g` is the PET generator family of the current number
- `e` is the exponent of the moved prime
- `gen(e)` is the PET generator of the exponent viewed as an integer

These laws were deterministic in the tested bounded range.

An equivalent coordinate reformulation using
`h = gen(n / p^e)` was also verified, but it did not yield a stronger law;
it is only a change of coordinates.

## External support grammar

Under `NEW`, observed generator families form a bounded rooted forest.

Observed bounded properties:
- no `NEW` cycles
- no multi-predecessor nodes under `NEW`
- `DROP` acts as the partial inverse of `NEW`

This gives an external support axis:
- `NEW` grows support
- `DROP` shrinks support

## Internal exponent grammar

Within the bounded source domain, `INC` and `DEC` induce deterministic
root-level transitions when labeled by the refined exponent-generator pairs.

This gives an internal exponent axis:
- `INC` increases local exponent mass
- `DEC` decreases local exponent mass

Up to bounded range truncation, these moves behave as inverse rewrites with
reversed local labels.

## Commutation

The following bounded commutation checks all passed with zero observed failures:

- `NEW` with `INC`
- `NEW` with `DEC`
- `DROP` with `INC`
- `DROP` with `DEC`

So the support axis and exponent axis empirically commute in the tested range.

## Guarded normal form

A naive normal form of the shape

`DEC* ; DROP* ; NEW* ; INC*`

fails because one cannot delete the last remaining support prime before a new
support prime has been introduced.

The bounded empirical normal form that passed the stress test is:

`DEC* ; guarded(DROP/NEW) ; INC*`

where the guarded middle phase obeys:

- reduce exponents first
- when support must change, do not remove the last live support prime unless a
  replacement prime has already been introduced
- use `NEW` as a bridge when necessary
- finish remaining exponent growth with `INC*`

Observed guarded normal-form test result:
- tested valid words: `413070`
- canonicalization failures: `0`
- law-prediction failures on canonical paths: `0`

So, in the tested bounded regime, the four transition laws are sufficient to
predict the generator-family path of the guarded canonical rewrite.

## Interpretation

This suggests that PET already supports a small bounded empirical arithmetic /
grammar:

- support is controlled by `NEW/DROP`
- local exponent motion is controlled by `INC/DEC`
- the two axes commute
- canonical rewriting requires a guarded bridge when support is replaced

This is enough to treat PET as a bounded rewriting system, not just as a static
catalog of families.

## Limits

Everything in this note is bounded empirical.

It does not claim:
- a theorem beyond the tested range
- global confluence
- a complete presentation of all PET rewrites
- a final algebraic formalism

It is a compact research note for the currently verified bounded core.
