# Shape Rewrite Arithmetic v0

## Idea generale

Invece di trattare i numeri solo come valori aritmetici, qui lavoriamo sulle **shape PET esatte** come stati di un sistema di rewrite.

L'idea non è:

- `12 - 3 = 9`

ma piuttosto:

- `Shape(PET(12)) ⊖ Shape(PET(3))`

dove `⊖` non è una sottrazione numerica classica: è il **cammino minimo di rewrite** che trasforma una shape nell'altra.

---

## Oggetti

Gli oggetti di lavoro sono **shape esatte**.

Esempi:

- `[[]]`
- `[[], []]`
- `[[], [[]]]`

Ogni shape è trattata in forma canonica normalizzata.

---

## Primitive di rewrite

Le mosse primitive sono quattro:

- `NEW` — aggiunge una foglia alla root
- `DROP` — rimuove una foglia dalla root
- `INC` — incrementa localmente una sotto-shape lungo un path
- `DEC` — decrementa localmente una sotto-shape lungo un path

Queste primitive sono già implementate nella shape algebra del repo e costituiscono il generatore locale del grafo di rewrite.

---

## Semantica operativa

### `neighbors(shape)`

Restituisce tutte le shape raggiungibili con **una sola mossa locale**.

Serve come nozione di vicinato nel grafo di rewrite.

### `distance(a, b)`

È il **costo minimo** per trasformare `a` in `b` tramite rewrite locali.

Formalmente:

- `distance(a, b) = lunghezza del shortest rewrite path da a a b`

### `path(a, b)`

Restituisce un **cammino minimo esplicito** da `a` a `b`, come sequenza di mosse locali.

### `diff(lhs, rhs)`

Nel v0 definiamo:

- `lhs ⊖ rhs := shortest rewrite path from rhs to lhs`

Quindi `diff` non produce ancora una nuova shape “differenza” come oggetto algebrico autonomo.
Produce invece:

- un **costo**
- una **sequenza minima di rewrite**

---

## Esempio minimo

Tra:

- `rhs = [[], []]`
- `lhs = [[], [[]]]`

si ha:

- `distance = 1`
- rewrite:
  - `INC path=[0]`

Quindi:

- `[[], [[]]] ⊖ [[], []]`

significa:

- “serve una sola mossa locale per trasformare `rhs` in `lhs`”

---

## Interpretazione

Questo v0 realizza una prima forma di **aritmetica strutturale**:

- gli stati sono shape
- le operazioni elementari sono rewrite locali
- la nozione di differenza è un cammino minimo
- la nozione di costo è una distanza di rewrite

---

## Cosa è già definito nel v0

- `neighbors`
- `distance`
- `path`
- `diff`

---

## Cosa non è ancora definito

Nel v0 **non** sono ancora definite in modo serio:

- una “somma” strutturale `⊕`
- un “prodotto” strutturale
- una forma normale di composizione tra cammini
- una teoria completa delle identità algebriche

Questa è una base operativa, non ancora una teoria completa.

---

## Stato del fronte

Questo v0 è utile perché:

- rende esplicita la PET-aritmetica come sistema di rewrite
- separa la differenza strutturale dalla sottrazione numerica classica
- fornisce già strumenti concreti per esplorare vicinato, distanza e trasformazioni minime
