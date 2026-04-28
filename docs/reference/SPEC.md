# SPEC — Prime Exponent Tree (PET)

## Dominio

PET è definito sugli interi `N >= 2`.

## Definizione informale

Ogni intero `N >= 2` viene rappresentato tramite la sua
fattorizzazione prima ordinata. Ogni esponente viene poi
rappresentato ricorsivamente con lo stesso schema.

## Sintassi

Usiamo:

- `•` per rappresentare l'esponente `1`
- una lista di coppie `(p, E)` per rappresentare un albero PET
- `p` è sempre un numero primo
- `E` è o `•` oppure un altro PET

## Rappresentazione JSON canonica

La rappresentazione macchina canonica di un PET è un valore JSON composto da:

- una lista non vuota di nodi
- ogni nodo è un oggetto con esattamente le chiavi `p` ed `e`
- `p` è un intero primo
- `e` è `null` quando l'esponente è `1`
- `e` è un altro PET JSON canonico quando l'esponente è `>= 2`
- i nodi di ogni lista sono ordinati per `p` crescente
- ogni primo `p` compare al massimo una volta per livello

Esempi JSON canonici:

PET(2):

    [{"p": 2, "e": null}]

PET(12):

    [
      {"p": 2, "e": [{"p": 2, "e": null}]},
      {"p": 3, "e": null}
    ]

PET(72):

    [
      {"p": 2, "e": [{"p": 3, "e": null}]},
      {"p": 3, "e": [{"p": 2, "e": null}]}
    ]

Questa è la forma serializzata normativa usata da `pet encode --json`,
`pet decode`, `pet validate`, `pet render` e dai record JSONL prodotti da
`pet scan`.

## Forma canonica

Un PET è canonico se e solo se:

1. tutti i fattori al primo livello sono numeri primi
2. i primi sono ordinati strettamente in senso crescente
3. ogni primo compare una sola volta per livello
4. l'esponente `1` è rappresentato solo da `•`
5. ogni esponente `e >= 2` è rappresentato come `PET(e)`
6. non sono ammesse forme alternative equivalenti

## Semantica

Il valore di `•` è:

`value(•) = 1`

Il valore di un PET:

`value([(p1, E1), ..., (pk, Ek)]) = prod(p_i ^ value(E_i))`

## Proprietà richieste

### Completezza
Ogni intero `N >= 2` deve avere una rappresentazione PET.

### Esattezza
Se `T = PET(N)`, allora `value(T) = N`.

### Canonicità
Se `PET(N1) = PET(N2)`, allora `N1 = N2`.

### Unicità della forma normale
Se `N1 = N2`, allora `PET(N1) = PET(N2)`.

## Costruzione canonica

Dato `N >= 2`:

1. fattorizza `N` in primi:
   `N = prod(p_i ^ e_i)`
2. ordina i primi in senso crescente
3. per ogni esponente:
   - se `e_i = 1`, usa `•`
   - se `e_i >= 2`, usa `PET(e_i)`

## Esempi

### PET(2)

[(2, •)]

### PET(12)

[
  (2, [(2, •)]),
  (3, •)
]

### PET(72)

[
  (2, [(3, •)]),
  (3, [(2, •)])
]

## Invarianti strutturali

Gli invarianti seguenti sono proprietà della **forma dell'albero PET**, non del valore numerico.
Sono stati verificati empiricamente fino a N = 10000.

### Invariante 1 — Linearità

Le seguenti condizioni sono equivalenti:

- `is_linear(tree)` è vero
- `max_branching(tree) == 1`
- `leaf_count(tree) == 1`

Un PET lineare è una catena pura: ogni livello ha esattamente un nodo.

Esempi: `2, 3, 4, 8, 16, 32, 81, 256` — ma non `64 = 2^(2·3)`.

### Invariante 2 — Uniformità per livello

Le seguenti condizioni sono equivalenti:

- `is_level_uniform(tree)` è vero
- `structural_asymmetry(tree) == 0.0`
- tutti i valori di `branch_profile(tree)` sono uguali

Un PET uniforme ha lo stesso numero di nodi a ogni livello.
`is_linear` è il caso speciale con `max_branching == 1`.

Esempi uniformi non lineari: `36 = 2^2·3^2` con profilo `[2,2]`, `72 = 2^3·3^2` con profilo `[2,2]`.

### Invariante 3 — Squarefreeness

Le seguenti condizioni sono equivalenti:

- `is_squarefree(tree)` è vero
- `recursive_mass(tree) == 0`
- tutti i nodi sono al livello radice (nessun sottoalbero esponenziale)

Un PET squarefree è un albero piatto: tutti gli esponenti della fattorizzazione sono `1`.

Esempi: `2, 3, 6, 30, 42` — ma non `4 = 2^2`, `12 = 2^2·3`.

### Invariante 4 — Espansione

Le seguenti condizioni sono equivalenti:

- `is_expanding(tree)` è vero
- `branch_profile(tree)[-1] > branch_profile(tree)[0]`
- almeno un esponente nella fattorizzazione è composto con due o più fattori primi distinti

Un PET espandente si allarga scendendo — proprietà rara (12 casi su 10000).

Esempi: `64 = 2^6` (esponente `6=2·3`), `576 = 2^6·3^2`, `729 = 3^6`.

### Relazioni tra invarianti

- `is_linear` implica `is_level_uniform` (ma non viceversa)
- `is_squarefree` e `is_linear` sono indipendenti (es. `6` è squarefree ma non lineare; `4` è lineare ma non squarefree)
- `is_expanding` è incompatibile con `is_linear` (un albero espandente non può essere una catena)
- `is_squarefree` è incompatibile con `is_expanding` (se tutti gli esponenti sono `1`, nessun sottoalbero può ramificarsi)

### Nota

Questi invarianti emergono dalla struttura ricorsiva di PET e non hanno
un corrispondente diretto nella fattorizzazione prima classica.

## Metriche analitiche (pet_metrics)

Le seguenti metriche sono definite in `src/pet_metrics.py` e operano su PET canonici validi.

### Admission rule for canonical metrics

A metric may be added to the canonical PET metric set only if all of the following hold:

1. **Deterministic on canonical PETs**  
   The metric must be a pure function of a valid canonical PET and must always return the same value for the same tree.

2. **Independent from incidental representation details**  
   The metric must not depend on serialization choices, implementation accidents, or traversal artifacts that do not carry structural meaning.

3. **Semantically explicit**  
   Its definition must be precise, compact, and understandable without relying on implementation-specific behavior.

4. **Non-redundant**  
   It must add structurally meaningful information that is not already captured well enough by the existing canonical metrics.

5. **Empirically justified**  
   It must help distinguish real observed PET families or notable cases, not only artificially constructed examples.

6. **Generally useful**  
   It must describe a recurring structural property of PETs, rather than a niche, ad hoc, or research-only curiosity.

7. **Canonical-output worthy**  
   Its value must be important enough to appear by default in the canonical metrics block, CLI metrics output, and scan JSONL records.

Metrics that are informative but fail one or more of these criteria should remain in extended, research, or reporting layers rather than in the canonical metric set.

### Metriche scalari

- `verticality_ratio(tree)` — rapporto `height / node_count`. Vale `1.0` per catene pure, tende a `0` per alberi piatti.
- `structural_asymmetry(tree)` — deviazione standard del `branch_profile`. Vale `0.0` per alberi uniformi per livello.
- `recursive_mass(tree)` — numero di nodi appartenenti a sottoalberi esponenziali (già in PET-Base).
- `leaf_ratio(tree)` — rapporto `leaf_count / node_count` come `Fraction` esatta. Appartiene a un insieme sparso e discreto di valori razionali.

### Classificatori booleani

- `is_linear(tree)` — `True` se il PET è una catena pura (`max_branching == 1`).
- `is_level_uniform(tree)` — `True` se tutti i livelli hanno lo stesso numero di nodi.
- `is_squarefree(tree)` — `True` se `recursive_mass == 0` (tutti gli esponenti sono `1`).
- `is_expanding(tree)` — `True` se l'ultimo livello ha più nodi del primo (proprietà rara).

### Classificatore morfologico

`profile_shape(tree)` restituisce una stringa che descrive la forma del profilo:
- `'point'` — albero di altezza 1 (numero squarefree o primo)
- `'linear'` — catena pura, tutti i livelli con un solo nodo
- `'normal'` — forma tipica, profilo non crescente
- `'expanding'` — ultimo livello più largo del primo (raro: ~12 casi su 10000)
- `'bell'` — picco interno al profilo, né al primo né all'ultimo livello (rarissimo: ~6 casi su 100000)

### Osservazioni sui valori di leaf_ratio

Il rapporto `leaf_count / node_count` appartiene a un insieme sparso e discreto.
Famiglie identificate fino a N = 500000:

- `1/k` — catene di altezza `k` (profilo `[1,1,...,1]`)
- `k/(k+1)` — profilo `[k,1]`, converge a `1`
- `k/(2k+1)` — profilo `[k,k,1]`, converge a `1/2`

## Famiglie di leaf_ratio

Il rapporto `leaf_count / node_count` appartiene a un insieme sparso e discreto di frazioni razionali.
Le famiglie identificate seguono la forma generale `k / (p·k + 1)` dove `p >= 0`.

### Famiglie accessibili (primi esempi raggiungibili)

| p | formula | esempi di ratio | primo esempio | profilo tipico |
|---|---|---|---|---|
| 0 | `k/1` = `1` | `1` | N=2 | `[k]` |
| 1 | `k/(k+1)` | `1/2, 2/3, 3/4, ...` | N=4 | `[k, 1]` |
| 2 | `k/(2k+1)` | `1/3, 2/5, 3/7, ...` | N=16 | `[k, k, 1]` |
| 3 | `k/(3k+1)` | `1/4, 2/7, ...` | N=65536 | `[k, k, k, 1]` |

### Famiglie inaccessibili (primi esempi astronomici)

Per `p >= 4`, le famiglie `k/(pk+1)` esistono teoricamente ma i loro primi esempi
richiedono numeri della forma `2^(2^(2^...))` con profondità crescente —
irraggiungibili per esplorazione diretta.

Il primo esempio per `p=3, k=1` è già `N = 65536 = 2^16`.
Il primo esempio per `p=4, k=1` richiederebbe `2^(2^(2^(2^(2^2)))) = 2^(2^65536)`,
un numero con decine di migliaia di cifre.

### Famiglie ibride

Oltre alla serie principale, esistono ratio che non seguono la forma `k/(pk+1)`:

| ratio | profilo | primo esempio |
|---|---|---|
| `3/8` | `[3, 3, 2]` | N=32400 |
| `5/9` | `[5, 3, 1]` | N=277200 |
| `4/7` | `[4, 2, 1]` | N=5040 |
| `3/5` | `[3, 2]` | N=180 |
| `5/8` | `[5, 2, 1]` | N=55440 |
| `5/7` | `[5, 2]` | N=13860 |

Questi ratio emergono da strutture miste in cui i livelli non sono uniformi.
La loro classificazione completa è ancora aperta.

### Nota
La scarsità dei ratio accessibili è una conseguenza diretta della struttura ricorsiva di PET: ogni nuovo livello di profondità richiede esponenti che sono a loro volta numeri strutturalmente complessi, il cui primo esempio cresce in modo superesponenziale.

## Confronto con famiglie aritmetiche note

Le metriche PET sono state calcolate su quattro famiglie aritmetiche classiche per valutare il potere discriminante di PET rispetto alla teoria dei numeri tradizionale.

### Primorials (2, 6, 30, 210, 2310, ...)

Firma PET perfettamente uniforme:
- `shape = point` per tutti
- `height = 1`, `asym = 0.0`, `ratio = 1`

Questo riflette il fatto che i primorials sono squarefree per costruzione (prodotto di primi distinti con esponente 1).
PET li identifica istantaneamente, ma questo è equivalente al già noto criterio squarefree.

### Numeri di Hamming (5-smooth)

Nessuna firma PET coerente — mescola `point`, `linear`, `normal`.
PET non li separa come famiglia distinta.

### Numeri altamente composti

Quasi tutti `shape = normal`, con `asym` e `ratio` crescenti all'aumentare di N.
PET cattura la complessità strutturale crescente ma non li discrimina nettamente.

### Numeri perfetti

Troppo pochi per concludere (solo 4 noti e calcolabili).
Nessuna firma PET comune identificata.

### Conclusione

PET separa nettamente solo i Primorials — ma questo coincide con la proprietà squarefree già nota. Per le altre famiglie, PET descrive la morfologia ma non offre discriminazione aggiuntiva rispetto alla fattorizzazione classica.

Il valore di PET resta negli invarianti strutturali scoperti e nella rappresentazione ricorsiva canonica. PET-Algebra potrebbe essere il livello dove emerge potere classificatorio genuinamente nuovo.

## PET-Algebra

PET-Algebra studia le operazioni strutturali sui PET canonici.
Tutte le operazioni producono PET canonici che rappresentano interi.
Il codice vive in `src/pet_algebra.py`.

### Operazione: graft

`graft(tree, scion)` sostituisce ogni foglia (`None`) di `tree` con `scion`.

Ogni nodo di `tree` il cui esponente è `None` (esponente = 1) riceve
`scion` come nuovo sottoalbero esponenziale.

**Esempio:**
```
PET(6)  = [(2,•),(3,•)]
PET(2)  = [(2,•)]
graft(PET(6), PET(2)) = [(2,[(2,•)]),(3,[(2,•)])] = PET(36)
```

### Proprietà algebriche di graft

| Proprietà | Risultato |
|---|---|
| Commutatività | ✗ |
| Associatività | ✓ |
| Elemento identità | ✗ |
| Elemento assorbente | ✗ |
| Idempotenza | ✗ |

`graft` è un'operazione **non commutativa ma associativa**.

### Teorema 1 — graft su squarefree

Per ogni intero `n` squarefree e ogni intero `k >= 2`:

> `decode(graft(PET(n), PET(k))) = n^k`

Innestare `PET(k)` su un PET squarefree equivale a elevare `n` alla potenza `k`.

### Teorema 2 — autoinnesto su squarefree

Per ogni intero `n` squarefree:

> `decode(graft(PET(n), PET(n))) = n^n`

L'autoinnesto di un PET squarefree produce `n^n`.

### Corollario del Teorema 2 — graft iterato

Definiamo il graft iterato `g^k(n)` come:
- `g^0(n) = n`
- `g^k(n) = graft(g^(k-1)(n), PET(n))`

Per ogni `n` squarefree:

> `decode(g^k(n)) = n^(n^(n^...))` — torre di potenze di altezza `k+1`

Esempi per `n=2`:
- `g^0(2) = 2`
- `g^1(2) = 4 = 2^2`
- `g^2(2) = 16 = 2^(2^2)`

### Teorema 3 — graft ricorsivo (caso generale)

Per ogni `n >= 2` e `k >= 2`:

> `decode(graft(PET(n), PET(k))) = prod(p_i ^ f(e_i, k))`

dove `f(e, k) = k` se `e = 1`, altrimenti `f(e, k) = decode(graft(PET(e), PET(k)))`.

In altre parole: `graft(PET(n), PET(k))` eleva ricorsivamente ogni esponente
nella fattorizzazione di `n` alla potenza `k`.

I Teoremi 1 e 2 sono casi speciali:
- quando `n` è squarefree, tutti gli esponenti sono `1` → `f(1,k) = k` → `decode = n^k`
- quando `k = n` squarefree → `decode = n^n`

### Nota

Per `n` non squarefree il risultato di `graft` è sempre un intero valido, ma la corrispondenza con `n^k` o `n^n` non vale in generale.
La struttura algebrica per i non-squarefree è ancora aperta.

### Operazione: distance

`distance(a, b)` misura la distanza strutturale tra due PET in termini di **coincidenza di primi**.

- primi presenti in un solo albero contribuiscono con il loro intero node count
- primi presenti in entrambi contribuiscono con la distanza ricorsiva tra i sottoalberi esponenziali
- due foglie (`None`) hanno distanza `0`
- `distance(a, a) = 0` per ogni PET

### Operazione: structural_distance

`structural_distance(a, b)` misura la distanza tra due PET ignorando i valori dei primi — confronta solo la **forma** dell'albero.

- due PET hanno `structural_distance = 0` se e solo se sono isomorfi come alberi ordinati
- `PET(4) = [(2,[(2,•)])]` e `PET(9) = [(3,[(2,•)])]` hanno `structural_distance = 0`

### Relazione tra le due distanze

Le due metriche sono complementari — nessuna sussume l'altra:

| caso | distance | structural_distance |
|---|---|---|
| PET(2) vs PET(3) | 2 | 0 |
| PET(4) vs PET(9) | 4 | 0 |
| PET(12) vs PET(18) | 2 | 0 |
| PET(2) vs PET(30) | 2 | 2 |
| PET(4) vs PET(12) | 1 | 3 |

`distance` cattura la somiglianza aritmetica (quali primi condividono),
`structural_distance` cattura la somiglianza morfologica (che forma hanno).

### Proprietà metriche

Entrambe le distanze soddisfano le proprietà di una metrica:
- `d(a,a) = 0`
- `d(a,b) = d(b,a)` — simmetria
- `d(a,c) <= d(a,b) + d(b,c)` — disuguaglianza triangolare

### Relazione tra le due distanze

`dist >= sdist` nella quasi totalità dei casi. Le eccezioni si verificano quando un PET è **sottostruttura ricorsiva** dell'altro — al primo livello (un PET ha più primi) o in profondità (un esponente è esteso ricorsivamente).

In questi casi `dist` è piccola (condividono quasi tutti i primi) ma `sdist` è grande (le forme sono molto diverse).

### Indipendenza dalle metriche scalari

Sia `dh(a,b) = |height(a) - height(b)|` e `dn(a,b) = |node_count(a) - node_count(b)|`.

Esistono coppie con `dh=0` e `dn=0` ma `distance>0` o `structural_distance>0`:

| A | B | dist | sdist | dh | dn |
|---|---|---|---|---|---|
| 2 | 3 | 2 | 0 | 0 | 0 |
| 4 | 9 | 4 | 0 | 0 | 0 |
| 12 | 18 | 2 | 0 | 0 | 0 |
| 36 | 60 | 4 | 4 | 0 | 0 |
| 36 | 72 | 2 | 0 | 0 | 0 |

`distance` e `structural_distance` sono quindi metriche genuinamente nuove —
non riducibili a combinazioni di metriche scalari preesistenti come `height` e `node_count`.

## Enumerazione shape-first (proposta operativa)

Per i workflow operativi orientati alla shape, il criterio numerico
"generatore minimo" non basta sempre.
In particolare, quando si vuole esplorare o materializzare shape con priorità
strutturale, serve una corsia dedicata che non ordini i casi solo per valore
numerico del witness.

### Obiettivo

Introdurre un comando CLI dedicato all'enumerazione shape-first:

```bash
pet shape-enumerate --max-mass N
```

Questo comando non ridefinisce PET-Base e non sostituisce `pet encode`.
Lavora invece nel layer operativo/algebrico, dove interessa enumerare
shape esatte canoniche e materializzarne un witness minimo compatibile.

### Ordinamento canonico proposto

Le shape enumerate entro il bound scelto devono essere ordinate con priorità
lessicografica:

1. `height` decrescente
2. `root_width` crescente
3. ordine canonico stabile della shape (`shape_key` o equivalente)

Interpretazione operativa:

- prima si privilegia la verticalità
- solo dopo si minimizza la larghezza della root
- solo infine si usa un tie-break strutturale stabile

### Parametri minimi

MVP proposto:

```bash
pet shape-enumerate --max-mass N [--json] [--limit K] [--with-pet]
```

Dove:

- `--max-mass N` limita l'enumerazione alle shape con massa strutturale `<= N`
- `--json` emette record machine-friendly
- `--limit K` tronca il numero di shape restituite
- `--with-pet` include anche il witness PET materializzato oltre a `gamma`

### Campi di output minimi

Ogni record dovrebbe esporre almeno:

- `shape`
- `mass`
- `height`
- `root_width`
- `gamma`

Facoltativamente:

- `pet`

### Esempio di output testuale

```text
shape 1
mass: 3
height: 3
root_width: 1
gamma: 16
shape: (((),),)

shape 2
mass: 3
height: 2
root_width: 2
gamma: 12
shape: (((),), ())
```

### Esempio di output JSON

```json
{
  "mass": 3,
  "height": 3,
  "root_width": 1,
  "gamma": 16,
  "shape": [[[]]]
}
```

### Nota di ambito

Questa proposta riguarda l'interfaccia operativa shape-first.
Non modifica:

- la definizione canonica di PET
- la serializzazione JSON canonica di PET
- l'uso di `pet encode/decode` per gli interi

Serve solo a rendere esplicita una corsia CLI coerente con la policy:

- prima altezza
- poi larghezza della root
- poi ordine canonico stabile

## Clustering delle famiglie aritmetiche con PET-Algebra

Le distanze `distance` e `structural_distance` sono state applicate a quattro famiglie
aritmetiche classiche per misurare il potere discriminante di PET-Algebra.
L'analisi è in due fasi: famiglie sovrapposte (come definite classicamente) e famiglie
disgiunte (ogni elemento assegnato alla famiglia più specifica).

### Famiglie analizzate

- **Primorials**: 2, 6, 30, 210, 2310, 30030, 510510
- **Hamming** (5-smooth): elementi con fattori solo in {2,3,5}, fino a 256
- **HighlyComposite**: numeri con più divisori di qualsiasi intero precedente, fino a 720720
- **Perfect**: 6, 28, 496, 8128

### Famiglie disgiunte

Per l'analisi pulita ogni elemento è assegnato alla famiglia più specifica che lo contiene,
con priorità: Perfect > Primorials > Hamming > HighlyComposite.

Elementi rimossi per disgiunzione:

| Famiglia | orig | kept | removed |
|---|---|---|---|
| Perfect | 4 | 4 | — |
| Primorials | 7 | 6 | 6 |
| Hamming | 30 | 28 | 2, 6 |
| HighlyComposite | 37 | 26 | 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240 |

### Risultati intra-famiglia

| Famiglia | dist diam | dist mean | sdist diam | sdist mean |
|---|---|---|---|---|
| Perfect | 4.00 | 3.50 | 2.00 | 1.33 |
| Primorials | 6.00 | 2.67 | 6.00 | 2.67 |
| Hamming | 7.00 | 3.60 | 6.00 | 2.49 |
| HighlyComposite | 7.00 | 3.78 | 9.00 | 3.33 |

Osservazioni:

- **Perfect**: le due metriche divergono nettamente (dist diam=4, sdist diam=2). I numeri
  perfetti hanno strutture morfologicamente simili — forma 2^(p-1)·(2^p-1) — ma usano
  primi diversi. `structural_distance` cattura questa somiglianza, `distance` no.
- **Primorials**: le due metriche coincidono esattamente. I primorials sono squarefree,
  quindi i loro PET sono piatti — non c'è struttura ricorsiva da distinguere. Le due
  metriche collassano sulla stessa cosa: contare le differenze tra insiemi di primi.
- **HighlyComposite**: `sdist diam=9` è il più alto del dataset. La famiglia è
  strutturalmente eterogenea — contiene sia alberi piatti che alberi profondi.

### Outlier strutturale: 720720

720720 = 2⁴·3²·5·7·11·13 è l'elemento più isolato morfologicamente dell'intero dataset
HC (sdist min=4.00, mean=6.40 rispetto agli altri HC).

```
PET(720720):
  node_count=9, leaf_count=6, height=3
  max_branching=6, branch_profile=[6,2,1], recursive_mass=3
```

Combina la massima larghezza radice (6 rami) con la massima profondità (height=3)
tra tutti gli HC. Nessun altro elemento HC ha questa combinazione.

### Risultati inter-famiglia (famiglie disgiunte)

#### distance

| Famiglia A | Famiglia B | min | mean | max |
|---|---|---|---|---|
| Perfect | Primorials | 1.00 | 4.83 | 9.00 |
| Perfect | Hamming | 1.00 | 3.75 | 8.00 |
| Perfect | HighlyComposite | **3.00** | 6.15 | 10.00 |
| Primorials | Hamming | 1.00 | 4.31 | 8.00 |
| Primorials | HighlyComposite | 1.00 | 4.40 | 8.00 |
| Hamming | HighlyComposite | 1.00 | 5.59 | 9.00 |

#### structural_distance

| Famiglia A | Famiglia B | min | mean | max |
|---|---|---|---|---|
| Perfect | Primorials | 1.00 | 3.67 | 7.00 |
| Perfect | Hamming | 0.00 | 2.31 | 5.00 |
| Perfect | HighlyComposite | **2.00** | 5.81 | 9.00 |
| Primorials | Hamming | 1.00 | 4.21 | 8.00 |
| Primorials | HighlyComposite | 1.00 | 4.28 | 8.00 |
| Hamming | HighlyComposite | 0.00 | 6.26 | 10.00 |

### Separabilità

Nessuna coppia di famiglie risulta separata nel senso metrico forte
(`gap_inter_min > max_intra_diam`). Il gap migliore è Perfect vs HighlyComposite
con `distance` (gap=3.00, max_intra=7.00).

La non-separazione riflette il fatto che queste famiglie si sovrappongono
strutturalmente. PET le distingue **in media** (le mean inter sono sistematicamente
più alte delle mean intra) ma non ai bordi.

### Coppia più distinguibile

**Perfect vs HighlyComposite** è la coppia meglio separata da PET:
- `distance` gap=3.00 — i numeri perfetti e gli HC esclusivi condividono pochissimi primi
- `structural_distance` gap=2.00 — sono anche morfologicamente distanti

Ha senso strutturalmente: i numeri perfetti hanno forma rigida 2^(p-1)·(2^p-1),
gli HC grandi sono alberi larghi e complessi senza schema fisso.

### Conclusione

PET-Algebra non separa nettamente le quattro famiglie nel senso metrico forte,
ma cattura differenze reali e misurabili. Il potere discriminante è presente
**in media** ma non abbastanza concentrato da produrre separazione netta ai bordi.

Gli strumenti di analisi sono in `tools/cluster_families.py` (famiglie originali)
e in `pet families benchmark-disjoint` (famiglie disgiunte, con wrapper compatibile
in `tools/cluster_families_disjoint.py`).

## JSONL scan record schema (v2)

The `pet scan` command produces one JSON object per line (JSONL).
Each line represents one integer `n >= 2` together with its canonical PET
encoding and structural analysis data.

### Record model

A scan record in schema v2 has the following top-level structure:

```json
{
  "schema_version": 2,
  "n": 72,
  "pet": [
    {"p": 2, "e": [{"p": 3, "e": null}]},
    {"p": 3, "e": [{"p": 2, "e": null}]}
  ],
  "metrics": {
    "node_count": 4,
    "leaf_count": 2,
    "height": 2,
    "max_branching": 2,
    "branch_profile": [2, 2],
    "recursive_mass": 2,
    "average_leaf_depth": 2.0,
    "leaf_depth_variance": 0.0
  },
  "meta": {
    "pet_format": "canonical-json"
  }
}
```

### Required top-level fields

- `schema_version`: integer schema version for compatibility tracking
- `n`: represented integer, with `n >= 2`
- `pet`: canonical PET JSON representation
- `metrics`: required structural metrics object

### Optional top-level fields

- `labels`: derived structural classifiers
- `meta`: descriptive non-structural metadata

### PET field

`pet` stores the canonical machine-facing PET JSON representation.

A PET JSON value is:

- a non-empty list
- of objects with exactly the keys `p` and `e`
- where `p` is a prime integer
- and `e` is either `null` (for exponent `1`) or another PET JSON value

This is the only normative structural representation in JSONL scan output.
Human-oriented renderings are out of scope for the dataset schema.

### Metrics field

The `metrics` object contains these required fields in schema v2:

- `node_count`: total number of PET nodes
- `leaf_count`: number of leaves (`e = null`)
- `height`: PET height in levels
- `max_branching`: maximum width at any local node set
- `branch_profile`: number of nodes per depth level
- `recursive_mass`: number of non-root nodes
- `average_leaf_depth`: arithmetic mean of leaf depths, with root depth = 1
- `leaf_depth_variance`: population variance of leaf depths

All metric fields above are mandatory in schema v2.

### Labels field

If present, `labels` contains derived structural classifiers.

Schema v2 reserves the following label names:

- `is_linear`
- `is_level_uniform`
- `is_squarefree`
- `is_expanding`
- `profile_shape`

These fields are derived convenience values, not the source of truth for PET structure.

### Meta field

If present, `meta` contains descriptive metadata about record encoding.

Schema v2 defines:

- `pet_format`: currently `"canonical-json"`

Arithmetic metadata may be added later, but it is not part of the required base schema.

### Stability and future evolution

Schema v2 guarantees the naming and meaning of all required fields above.

Compatibility rules:

- new optional fields may be added without changing `schema_version`
- removing or renaming required fields requires a new schema version
- changing the meaning of a required field requires a new schema version
- downstream consumers should ignore unknown optional fields

### Example JSONL line

```json
{"schema_version":2,"n":72,"pet":[{"p":2,"e":[{"p":3,"e":null}]},{"p":3,"e":[{"p":2,"e":null}]}],"metrics":{"node_count":4,"leaf_count":2,"height":2,"max_branching":2,"branch_profile":[2,2],"recursive_mass":2,"average_leaf_depth":2.0,"leaf_depth_variance":0.0},"meta":{"pet_format":"canonical-json"}}
```

