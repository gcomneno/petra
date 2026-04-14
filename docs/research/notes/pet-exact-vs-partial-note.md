# PET senza fattorizzazione completa: Exact-PET vs Partial-PET

## Idea

L’esperienza pratica con `pet explain` / `pet dismantle` suggerisce un limite netto:

- per numeri moderati, PET è calcolabile e lo smontaggio funziona bene;
- per numeri ostici, il collo di bottiglia non è PET in sé;
- il collo di bottiglia è la **fattorizzazione iniziale**.

Questo porta a una domanda naturale:

> si può ricavare informazione PET direttamente da `N`, senza passare dalla fattorizzazione completa?

La risposta va separata in due problemi molto diversi.

---

## 1. Problema forte: `Exact-PET(N)`

### Definizione informale

Dato un intero `N`, calcolare in modo canonico e completo:

- firma PET,
- generatore,
- mosse immediate `NEW / DROP / INC / DEC`,
- eventuale smontaggio canonico o greedy,
- vicinato/pathwise esatto.

### Osservazione

Nel formalismo attuale, questi oggetti dipendono profondamente dalla struttura moltiplicativa di `N`:

- supporto primo,
- esponenti,
- collisioni di esponenti,
- aggiornamenti locali del multinsieme degli esponenti.

Quindi un algoritmo che producesse `Exact-PET(N)` senza fattorizzare `N` dovrebbe comunque recuperare una quantità di informazione aritmetica molto vicina a quella richiesta dalla fattorizzazione.

### Congettura di lavoro

`Exact-PET(N)` è plausibilmente **factoring-hard**, o comunque non sembra realisticamente più facile della fattorizzazione completa.

Questa non è una dimostrazione.  
È una posizione di lavoro motivata da due fatti:

1. PET oggi è definita a partire dalla struttura prima di `N`;
2. le mosse fondamentali (`DEC`, `DROP`, `INC`, `NEW`) sono ombre dirette di trasformazioni sugli esponenti primi.

### Conseguenza pratica

La prospettiva:

> “calcolare PET esatta evitando del tutto la fattorizzazione”

va trattata come **programma teorico forte**, non come prossimo miglioramento implementativo.

---

## 2. Problema debole ma promettente: `Partial-PET(N)`

### Definizione informale

Dato un intero `N`, calcolare informazione PET **sound ma incompleta**, senza richiedere la fattorizzazione completa.

L’output può essere parziale, ma non deve mentire.

### Esempi di output possibili

- lower bound sul generatore PET;
- upper bound su certe quantità strutturali;
- witness di non-minimalità;
- witness locali di profondità 1 o 2;
- esclusione certificata di alcune mosse;
- decomposizione PET parziale;
- classi candidate compatibili con vincoli osservabili;
- residuo ignoto ma con anatomia parziale nota.

### Filosofia

Non chiedere:

> “qual è la PET completa di `N`?”

ma chiedere:

> “quanta PET corretta posso estrarre da `N` prima della fattorizzazione completa?”

Questa versione è molto più credibile e allineata con quanto già emerso nel lavoro sui probe parziali.

---

## 3. Analogia utile

La differenza è questa:

- `Exact-PET` sta a PET come la fattorizzazione completa sta all’aritmetica moltiplicativa;
- `Partial-PET` sta a PET come un certificato parziale, un witness o un bound stanno alla soluzione completa.

Non serve avere tutto per avere informazione utile.

---

## 4. Ipotesi strutturale

L’ipotesi guida è:

> PET potrebbe avere una teoria “osservabile” parziale, accessibile senza fattorizzazione completa, anche se la PET esatta resta factoring-hard.

In altre parole:

- la **PET completa** può essere difficile;
- ma gli **osservabili PET** possono essere accessibili.

Questa è la direzione di ricerca sensata.

---

## 5. Programma minimo di ricerca

### Obiettivo A — separazione concettuale
Formalizzare bene la distinzione tra:

- `Exact-PET(N)`
- `Partial-PET(N)`

### Obiettivo B — soundness
Per ogni output parziale, chiarire:

- cosa è garantito,
- cosa è solo ignoto,
- cosa non si sta affermando.

### Obiettivo C — nuovi osservabili factor-free
Cercare quantità PET estraibili senza fattorizzazione completa, ad esempio:

- bound sul generatore,
- pattern compatibili/incompatibili,
- witness locali,
- criteri di arresto parziale,
- frammenti di smontaggio certificati.

### Obiettivo D — algebra autonoma PET
Solo in una fase molto più ambiziosa, chiedersi se esista un vero analogo della “decomposizione in primi” sul lato delle forme PET.

Questa è la versione più forte e più lontana.

---

## 6. Conclusione operativa

La domanda giusta non è:

> si può saltare completamente la fattorizzazione?

La domanda giusta è:

> quali quantità PET utili, canoniche e certificate si possono ricavare da `N` senza fattorizzarlo tutto?

Questa riformulazione evita una falsa promessa e apre un programma realistico.

---

## Tesi di lavoro

- `Exact-PET` sembra troppo vicino al factoring per aspettarsi un salto facile;
- `Partial-PET` sembra invece una frontiera reale e fertile;
- il progresso vero non è “nascondere” la fattorizzazione;
- il progresso vero è **vedere PET prima della fattorizzazione completa**.
