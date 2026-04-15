# PET-METICA operational semantics

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

## 4. Diff

Nel v0 operativo:

`lhs ⊖ rhs := path(rhs, lhs)`

Quindi `diff(lhs, rhs)` non produce ancora un nuovo oggetto algebrico autonomo.
Produce invece:
- un cammino minimo
- e quindi implicitamente un costo minimo associato

Stato teorico:
- questa è una convenzione operativa utile
- non è ancora una formalizzazione definitiva di `⊖`

---

## 5. Esempio minimo

Se `rhs` e `lhs` differiscono per una sola mossa locale, allora:
- `distance(rhs, lhs) = 1`
- `path(rhs, lhs)` contiene una sola mossa
- `lhs ⊖ rhs` è quel singolo rewrite

Questo è il caso-base della lettura di `⊖` come trasporto minimo di rewrite.
