# PET-METICA `⊕` case study: (2, 6, 30)

> **Legacy research case study.** Any `NEW`, `DROP`, `INC`, or `DEC` path
> below is retained PET-METICA evidence, not canonical or future PET semantics.
> The sole normative future operator contract is
> [`../../reference/SPEC.md`](../../reference/SPEC.md).

## Scopo
Questa nota fissa il caso composabile `(2,6,30)` come primo banco di prova reale per il candidato A-v0.

---

## 1. Dati di partenza

Trasporto minimo:
- `T(2,6)`:
  - costo `1`
  - path:
    - `2 --NEW(x3)--> 6`

Trasporto minimo:
- `T(6,30)`:
  - costo `1`
  - path:
    - `6 --NEW(x5)--> 30`

Trasporto minimo diretto:
- `T(2,30)`:
  - costo `2`
  - path:
    - `2 --NEW(x3)--> 6`
    - `6 --NEW(x5)--> 30`

---

## 2. Composizione A-v0

Per A-v0:
- `T(2,6)` e `T(6,30)` sono compatibili
- quindi si può definire la composizione per concatenazione

Concatenazione osservata:
- `T(2,6) ⋅ T(6,30)`:
  - costo `2`
  - path:
    - `2 --NEW(x3)--> 6`
    - `6 --NEW(x5)--> 30`

---

## 3. Confronto con il trasporto diretto

Confronto osservato:
- `concat(T(2,6), T(6,30)) == T(2,30)` come path
- `cost(concat) == cost(T(2,30))`

Quindi, in questo caso:
- la composizione coincide esattamente con il trasporto minimo diretto
- non è necessaria alcuna reminimizzazione
- non emerge alcuna ambiguità di cammino

---

## 4. Verdetto locale

Questo è il miglior esito possibile per A-v0 su un primo caso composabile.

Lettura:
- A-v0 non solo compone trasporti compatibili
- in questo caso la composizione è già minimizzata e canonica
- la semantica di composizione segue la dinamica naturale delle mosse `NEW`

Quindi A-v0 è promosso localmente su `(2,6,30)`.

---

## 5. Limite della conclusione

Questa conclusione è locale e non generale.

Non segue ancora che:
- ogni concatenazione di trasporti minimi sia minima
- ogni concatenazione coincida con il trasporto diretto
- A-v0 sia già una definizione completa e stabile di `⊕`

Segue però che:
- A-v0 ha almeno un caso-manifesto reale in cui funziona perfettamente

---

## 6. Lettura corrente più onesta

Dopo i casi `(6,30)` e `(2,6,30)` il quadro provvisorio è:

- C-v0 è molto forte come merge locale su stati
- A-v0 è molto forte come composizione naturale di trasporti

Quindi i due candidati restano vivi, ma su funzioni concettualmente diverse.

---

## 7. Prossimo passo

Il prossimo passo utile è cercare un caso composabile in cui A-v0 non sia così perfetto, ad esempio una catena dove:

- la concatenazione resti valida
- ma non coincida esattamente col trasporto diretto
- oppure richieda una normalizzazione successiva

Quel tipo di caso decide se A-v0 resta puro o se ha bisogno di una forma di composizione + reminimizzazione.
