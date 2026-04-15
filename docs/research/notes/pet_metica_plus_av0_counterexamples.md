# PET-METICA `⊕` A-v0 counterexamples

## Scopo
Questa nota fissa i primi controesempi strutturali per A-v0, cioè per la definizione di `⊕` come pura concatenazione di trasporti compatibili.

---

## 1. Esito della scansione locale

Su una scansione con:
- `overscan = 120`
- `n_max = 40`

si osserva:

- `exact = 2062`
- `same_cost_diff_path = 765`
- `concat_worse = 11161`
- `direct_unreachable = 0`
- `bad_composition = 0`

---

## 2. Lettura dell'esito

### 2.1. Coerenza sintattica
Il fatto che `bad_composition = 0` mostra che la concatenazione di trasporti compatibili è ben definita come operazione sintattica.

### 2.2. Fallimento semantico di A-v0
Il fatto che:
- `same_cost_diff_path > 0`
- `concat_worse >> 0`

mostra che la pura concatenazione non coincide in generale con il trasporto minimo diretto.

Quindi A-v0 non può essere promosso come semantica finale di `⊕`.

---

## 3. Due casi-manifesto

### Caso buono: `(2 -> 6 -> 30)`
Qui:
- la concatenazione coincide esattamente con `T(2,30)`
- costo e path coincidono

Questo mostra che A-v0 può funzionare perfettamente su catene naturali favorevoli.

### Caso cattivo: `(2 -> 3 -> 4)`
Qui:
- `ab = 2`
- `bc = 3`
- `concat = 5`
- `ac = 1`

Quindi la concatenazione è molto peggiore del trasporto minimo diretto.

Questo è un controesempio netto contro A-v0 come semantica minimizzata.

---

## 4. Correzione naturale

La promozione naturale è:

- `A-v1 = composizione + reminimizzazione`

Lettura:
- la concatenazione resta l'operazione sintattica primaria
- ma il risultato semanticamente rilevante va richiuso sul trasporto minimo diretto

In forma schematica:

- `T(a,b) ⊕_A1 T(b,c) := minimize(T(a,b) ⋅ T(b,c))`

oppure, più onestamente:

- `T(a,b) ⊕_A1 T(b,c) := T(a,c)`

quando la composizione è testimoniata da una concatenazione compatibile.

---

## 5. Stato corrente

Dopo questa scansione:

- A-v0 resta utile come composizione sintattica di cammini
- A-v0 non basta come semantica finale di `⊕`
- A-v1 diventa il candidato serio sul lato dei trasporti

Questo sposta il confronto reale su:

- A-v1 come operazione sui trasporti
contro
- C-v0 come operazione su stati
