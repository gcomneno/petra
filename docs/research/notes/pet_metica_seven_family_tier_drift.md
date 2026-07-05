# PET-METICA: famiglia `7 × {2^k, 3^k}` e tier drift

## Scopo

Questa nota fissa i risultati empirici di una ladder di scan PET-METICA mirati
sulla famiglia

```text
F_dyad(k) = 7 · 2^k
F_tri(k)  = 7 · 3^k
```

con focus sulle **coppie seed canonicali** `(2^k, 7·2^k)` e `(3^k, 7·3^k)`.

La nota documenta anche una correzione di rotta importante: le asimmetrie
osservate **non sono invarianti** rispetto a `(n_max, overscan)`. Estendere il
range non “conferma” semplicemente un pattern: può **abbassare** l’asimmetria
misurata per lo stesso `k`.

Non contiene teoremi.

---

## Strumenti e artefatti

### Probe mirato

```bash
python tools/research/pet_metica_seven_family_probe.py \
  --n-max N --overscan O \
  --output-json docs/reports/data/metica-seven-family-N.json \
  --output-md docs/reports/generated/metica-seven-family-N.md
```

Implementazione: `tools/research/pet_metica_seven_family_probe.py`

### Sweep multi-tier globale (contesto hub / frizione)

```bash
python tools/research/pet_metica_range_sweep.py \
  --output-json docs/reports/data/metica-range-sweep.json \
  --output-md docs/reports/generated/metica-range-sweep.md
```

Implementazione: `tools/research/pet_metica_range_sweep.py`

### Report generati in questa pass

| Tier | n_max | overscan | Report |
|------|-------|----------|--------|
| 300 | 300 | 900 | `docs/reports/generated/metica-seven-family-300.md` |
| 500 | 500 | 1500 | `docs/reports/generated/metica-seven-family-500.md` |
| 800 | 800 | 2400 | `docs/reports/generated/metica-seven-family-800.md` |
| 900 | 900 | 2700 | `docs/reports/generated/metica-seven-family-900.md` |
| 1200 | 1200 | 3600 | `docs/reports/generated/metica-seven-family-1200.md` |

Convenzione overscan usata: circa `3 · n_max`.

---

## Definizioni operative

### Membri di famiglia in `1..n_max`

- **Dyadic:** tutti i `7·2^k` con `7·2^k ≤ n_max`
- **Triadic:** tutti i `7·3^k` con `7·3^k ≤ n_max`

Esempi:

| n_max | dyadic fino a | triadic fino a |
|-------|---------------|----------------|
| 300 | 224 (k=5) | 189 (k=3) |
| 500 | 448 (k=6) | 189 (k=3) |
| 900 | 896 (k=7) | 567 (k=4) |
| 1200 | 896 (k=7) | 567 (k=4) |

Attenzione numerica:

- `7·2^7 = 896` entra solo per `n_max ≥ 896`
- `7·2^8 = 1792` richiede `n_max ≥ 1792` (non coperto da tier 800/900/1200)

### Coppia seed canonical dyadic

Per ogni `k` con `7·2^k ≤ n_max`:

```text
base   = 2^k
target = 7 · 2^k
```

Si misurano:

- `d(base → target)` — costo rewrite minimo forward
- `d(target → base)` — costo rewrite minimo reverse
- `asymmetry = d(base → target) − d(target → base)` quando entrambe le direzioni sono raggiungibili nel grafo bounded

### Coppia seed canonical triadic

Stessa logica con `base = 3^k`, `target = 7·3^k`.

---

## Claim robusti (in questa pass)

### 1. Il ritorno dalla potenza pura al multiplo di 7 è cheap

Nei tier 300–1200, per ogni seed canonical dyadic/triadic **raggiungibile in
entrambe le direzioni**:

```text
d(7·2^k → 2^k) = 1
d(7·3^k → 3^k) = 1
```

Questo è il pattern più stabile della ladder. Regge attraverso il drift sul
forward cost.

### 2. La famiglia dyadic produce poli asimmetrici forti

Membri come `56`, `112`, `224`, `448`, `896`:

- compaiono spesso nelle coppie con `|asymmetry| ≥ 6`
- possono avere **hub_score = 0** nel tier corrente pur essendo poli asimmetrici

Interpretazione prudente:

- “hub di transito” e “polo asimmetrico” sono ruoli distinti nel grafo bounded
- un nodo può essere direzionalmente importante senza comparire spesso come nodo
  interno di shortest path globali

### 3. Esiste una struttura ricorrente attorno ai multipli di 7

Nei tier grandi, le coppie forti ripetono schemi del tipo:

```text
2^k  ↔ 7·2^k   con asymmetry positiva grande
7·2^k ↔ 2·7·2^k  con asymmetry negativa speculare (quando il partner entra in range)
```

Esempi osservati:

- tier 500: `64↔448(+10)`, `128↔448(+10)`, `256↔448(+10)`
- tier 900: `128↔896(+10)`, `256↔896(+10)`, `512↔896(+10)`
- tier 1200: `128↔896(+8)`, `256↔896(+8)`, `512↔896(+8)`

Il **polo dominante sale** con il range (`56 → 112 → 224 → 448 → 896`), ma
resta nella famiglia dyadic.

### 4. Il ramo triadic esiste ma è più sottile

A tier 900/1200 compare `567 = 7·3^4` con seed `81 → 567`, asymmetry `+6`.

Il ramo triadic entra più tardi e con segnali più deboli rispetto al dyadic.

### 5. Hub globali restano stabili (sweep multi-tier)

Nei tier globali 30–200 del range sweep, i top hub baseline `{2, 3, 4, 6, 30}`
restano nel top-10 fino a `n_max = 200`.

Questo è ortogonale alla famiglia seven: descrive la spina dorsale globale del
grafo bounded, non i poli asimmetrici locali.

---

## Scoperta centrale: tier drift

### Enunciato empirico

Per lo **stesso** `k`, l’asimmetria canonical **non è costante** al crescere di
`n_max` (con overscan proporzionale).

Estendere la finestra può **abbassare** `|asymmetry|` per la stessa coppia seed.

### Tabella dyadic: `(2^k, 7·2^k)`

Valori di `asymmetry` osservati (solo tier dove `7·2^k ≤ n_max`):

| k | base → target | tier 300 | tier 500 | tier 800 | tier 900 | tier 1200 |
|---|---------------|----------|----------|----------|----------|-----------|
| 1 | 2 → 14 | 4 | 4 | 4 | 4 | 4 |
| 2 | 4 → 28 | 4 | 4 | 4 | 4 | 4 |
| 3 | 8 → 56 | 4 | 4 | 4 | 4 | 4 |
| 4 | 16 → 112 | 6 | 6 | 4 | 4 | 4 |
| 5 | 32 → 224 | 8 | 8 | 6 | 6 | 4 |
| 6 | 64 → 448 | — | **10** | 8 | 8 | 6 |
| 7 | 128 → 896 | — | — | — | **10** | **8** |

Legenda: `—` = target fuori range.

### Tabella triadic: `(3^k, 7·3^k)`

| k | base → target | tier 300 | tier 900 | tier 1200 |
|---|---------------|----------|----------|-----------|
| 1 | 3 → 21 | 4 | 4 | 4 |
| 2 | 9 → 63 | 4 | 4 | 4 |
| 3 | 27 → 189 | 6 | 4 | 4 |
| 4 | 81 → 567 | — | 6 | 6 |

### Forward cost drift (stesso k, tier crescenti)

Esempio `(64, 448)`:

| tier | d(64→448) | d(448→64) | asymmetry |
|------|-----------|-----------|-----------|
| 500 | 11 | 1 | 10 |
| 800 | 9 | 1 | 8 |
| 900 | 9 | 1 | 8 |
| 1200 | 7 | 1 | 6 |

Il reverse resta a `1`; si muove il forward cost.

---

## Correzioni di rotta acquisite

### 1. L’extrapolazione `asymmetry ≈ 2·(k−1)` non regge

A tier 500, la sequenza dyadic `4,4,4,6,8,10` per k=1..6 ha suggerito una legge
lineare crescente.

A tier 900/1200 la stessa legge **sovrastima** l’asimmetria osservata:

- predizione naive per k=7 a tier 900: `+12`
- osservato: `+10`
- osservato a tier 1200: `+8`

Conclusione: ogni formula chiusa sui soli tier piccoli va trattata come
**ipotesi locale**, non come legge.

### 2. Il nome del tier conta esplicitamente

“Tier 800” non implica automaticamente la presenza di `7·2^7 = 896`:

```text
896 > 800
```

Prima di ogni run, verificare quali membri `7·2^k` e `7·3^k` cadono in
`1..n_max`.

### 3. Overscan insufficiente maschera la forward direction

Con overscan troppo basso, `d(base → target)` può risultare unreachable anche
quando `d(target → base)` è definito.

Per analisi seed canonical, usare overscan generoso (qui: ~`3·n_max`).

---

## Cosa NON claimare

Questa pass **non** stabilisce:

- una legge asintotica `asymmetry(2^k, 7·2^k) = f(k)` indipendente dal tier
- che `896`, `448`, `112`, ecc. siano hub globali
- che ogni multiplo di 7 si comporti come la famiglia seed
- che i valori del tier 500 si propaghino ai tier 900/1200 senza ricalibrazione

Ogni numero della tabella è **valido solo** nel quadrupletto
`(n_max, overscan, grafo rewrite locale, costo unitario)`.

---

## Fronti aperti

1. **Modello esplicito del drift** — esiste una funzione
   `asymmetry(k, n_max, overscan)` empiricamente stabile?
2. **Tier ≥ 1792** — comportamento di `7·2^8 = 1792` non ancora misurato
3. **Ruolo di 567 / ramo triadic** — pattern più debole, da seguire separatamente
4. **Connessione con frizione per primo** — i poli seven interagiscono con la
   gerarchia `2 < 3 < 5 < 7` già documentata in `pet_metica_claims_snapshot.md`?
5. **Promotion policy** — nessun claim di questa nota va promosso a PET-Base o
   STATUS senza nuova pass di stabilizzazione

---

## Formula sintetica corrente

La famiglia `7 × {2^k, 3^k}` è una **linea di ricerca empirica promettente**
per PET-METICA:

- produce asimmetria direzionale forte e ricorrente
- scala i poli con `k` e con `n_max`
- separa ruoli “hub di transito” e “polo asimmetrico”

Ma la grandezza misurata dell’asimmetria è una proprietà del **grafo bounded
osservato**, non ancora un invariante matematico.

La lezione operativa della ladder:

> prima di extrapolare, fissare sempre `(n_max, overscan)` e riportare il tier
> nel claim.

---

## Riferimenti

- `pet_metica_minimal_definitions.md` — vocabolario number-level PET-METICA
- `pet_metica_claims_snapshot.md` — claim globali su frizione e famiglie
- `PET-METICA.md` — storia e motivazione rewrite-geometrica
- `../../reports/STATUS.md` — confini stable / empirical / exploratory
