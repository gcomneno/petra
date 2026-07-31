# PET-METICA operational semantics

> **Legacy implementation-compatibility semantics.** `NEW`, `DROP`, `INC`,
> and `DEC` describe current executable PET-METICA behavior, not canonical or
> future PET semantics. The sole normative future operator contract is
> [`../../reference/SPEC.md`](../../reference/SPEC.md).

## Scopo
Questa nota fissa una semantica operativa minima per PET-METICA.
Integra le definizioni minime con convenzioni utili per strumenti e API sperimentali.

---

## 1. Neighbors

`neighbors(s)` restituisce gli stati PET raggiungibili da `s` con una sola mossa locale.

Lettura corrente:
- realizza il vicinato locale del grafo di rewrite
- usa come primitive `NEW`, `DROP`, `INC`, `DEC`

---

## 2. Distance

`distance(a, b)` è il costo minimo per trasformare lo stato `a` nello stato `b` tramite rewrite locali ammessi.

Lettura corrente:
- coincide con la lunghezza minima di un cammino di rewrite da `a` a `b`
- in generale non coincide con la distanza numerica classica
- può essere asimmetrica

---

## 3. Path

`path(a, b)` restituisce un cammino minimo esplicito da `a` a `b`, come sequenza di mosse locali.

Lettura corrente:
- rende osservabile non solo il costo, ma anche la trasformazione
- è la faccia concreta del trasporto di rewrite tra due stati

---

## 4. Operational observables

PET-METICA currently exposes several bounded operational observables.

### Rewrite cost

The rewrite cost from `a` to `b` is the minimum number of local rewrite moves
needed to transform `a` into `b`.

It is the value reported as `cost` by:

    pet rewrite pair A B
    pet rewrite explain A B

This cost is directional: in general, `cost(a, b)` may differ from `cost(b, a)`.

### Rewrite friction

The rewrite friction of a one-step move `a -> b` is the minimum rewrite cost
needed to return from `b` to `a`.

It is used to measure local reversibility.

Example:

    6 --NEW(x5)--> 30

may be a one-step forward move, while the return path from `30` to `6` can
require multiple moves.

This is the quantity summarized by:

    pet rewrite friction

### Hub score

A hub score counts how often a node appears as an internal node of canonical
shortest rewrite paths in a bounded scan.

High hub score means that a state frequently acts as a transit point in the
observed rewrite geometry.

Hub score is bounded by the scan range and overscan parameters.

### Rewrite asymmetry

Rewrite asymmetry compares the two directed costs between a pair:

    cost(a, b) - cost(b, a)

A non-zero value means the transport from `a` to `b` is not equally difficult
in the reverse direction.

### Attractor score

The attractor score compares average incoming and outgoing rewrite distances
for a node in a bounded pair scan.

Operationally, it is a bounded heuristic for detecting whether a node is easier
to reach than to leave, or vice versa.

It should be read as an empirical scan statistic, not as a global invariant.

---

## 5. Diff

Nel v0 operativo:

`diff(lhs, rhs) := path(rhs, lhs)`

Quindi `diff(lhs, rhs)` non produce ancora un nuovo oggetto algebrico autonomo.
Produce invece:
- un cammino minimo
- e quindi implicitamente un costo minimo associato

Stato teorico:
- questa è una convenzione operativa utile
- non è ancora una formalizzazione definitiva di un operatore algebrico di differenza

---

## 6. Esempio minimo

Se `rhs` e `lhs` differiscono per una sola mossa locale, allora:
- `distance(rhs, lhs) = 1`
- `path(rhs, lhs)` contiene una sola mossa
- `diff(lhs, rhs)` è quel singolo rewrite

Questo è il caso-base della lettura della differenza PET come trasporto minimo di rewrite.
