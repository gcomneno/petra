# PET-METICA `⊕` A-v1 semantics

## Scopo
Questa nota fissa una semantica più pulita per `A-v1`, dopo i controesempi ad `A-v0`.

L'idea guida è distinguere esplicitamente:

- composizione sintattica dei trasporti
- risultato semantico della composizione

---

## 1. Contesto

In `A-v0`, la composizione di due trasporti compatibili era definita come pura concatenazione:

- `T(a,b) ⊕_A0 T(b,c) := T(a,b) ⋅ T(b,c)`

Questa definizione è risultata troppo grezza:
- in alcuni casi la concatenazione coincide col trasporto minimo diretto
- in molti altri no
- quindi la concatenazione non può essere il risultato semantico finale

---

## 2. Oggetti di partenza

Un trasporto PET minimo orientato da `a` a `b` è indicato con:

- `T(a,b)`

ed è letto come:
- cammino minimo di rewrite da `a` a `b`

Due trasporti:
- `T(a,b)`
- `T(b,c)`

sono compatibili se:
- il target del primo coincide con la sorgente del secondo

Questa compatibilità consente la loro composizione sintattica.

---

## 3. Livello sintattico

La composizione sintattica è la semplice concatenazione dei cammini:

- `T(a,b) ⋅ T(b,c)`

Questa concatenazione ha valore come:
- witness di composabilità
- oggetto osservabile
- traccia esplicita della composizione locale

Ma non va più trattata come risultato semantico definitivo.

---

## 4. Livello semantico

La composizione semanticamente rilevante è:

- `T(a,b) ⊕_A1 T(b,c) := T(a,c)`

cioè:
- il trasporto minimo diretto da `a` a `c`

quando la composizione è testimoniata da una concatenazione compatibile.

---

## 5. Interpretazione

In `A-v1`:

- la concatenazione resta il witness sintattico della composizione
- il trasporto minimo diretto fornisce il risultato semantico finale

Quindi `A-v1` non dice:
- “la composizione è la concatenazione”

ma dice:
- “la concatenazione testimonia una composizione, la cui chiusura semantica è il trasporto minimo risultante”

---

## 6. Formula sintetica

La forma compatta da ricordare è:

- `T(a,b) ⊕ T(b,c) := T(a,c)`

con l'intesa che:
- la compatibilità è testimoniata da una concatenazione sintattica ben definita
- la concatenazione non coincide necessariamente col risultato finale

---

## 7. Caso favorevole

Nel caso `(2,6,30)` si osserva:

- `T(2,6) ⋅ T(6,30) = T(2,30)`

Quindi lì:
- witness sintattico
- e risultato semantico

coincidono perfettamente.

Questo è un caso favorevole, non una legge generale.

---

## 8. Caso sfavorevole

Nel caso `(2,3,4)` si osserva:

- concatenazione con costo `5`
- trasporto minimo diretto con costo `1`

Quindi lì:
- la concatenazione testimonia la composizione
- ma non può essere il risultato semantico buono

Questo è il motivo per cui `A-v1` sostituisce `A-v0`.

---

## 9. Vantaggi di A-v1

`A-v1` conserva le parti buone di `A-v0`:

- lavora sul livello dei trasporti
- mantiene la lettura dinamica di PET-METICA
- evita il trucco del punto base
- non perde la witness chain concreta

Ma evita il difetto principale di `A-v0`:
- non identifica ingenuamente concatenazione e trasporto minimo risultante

---

## 10. Limiti aperti

`A-v1` non chiude ancora tutto.

Restano aperti almeno questi punti:

- quando esattamente una concatenazione compatibile debba essere considerata semanticamente significativa
- se serva una nozione più forte di witness oltre alla sola compatibilità terminale
- quanto questa composizione si comporti bene su catene più lunghe
- quali proprietà strutturali sopravvivano oltre i casi locali favorevoli

---

## 11. Stato corrente

La lettura più onesta, allo stato attuale, è:

- `A-v1` è il candidato principale per una semantica transport-primary di `⊕`
- la concatenazione è parte della semantica, ma non è il risultato finale
- il risultato finale vive nel trasporto minimo diretto risultante

Questa è, finora, la formulazione più pulita emersa.
