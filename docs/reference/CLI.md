# PET CLI Guide

Questa guida raccoglie l'uso pratico del command-line interface di PET.

Il CLI è pensato come punto di accesso operativo per:

- encoding e decoding di interi in formato PET
- ispezione della struttura di un intero
- confronto tra strutture PET
- generazione di dataset JSONL
- interrogazione di dataset PET per metriche
- analisi bounded su dataset PET

Per la visione generale del progetto, vedere `../VISION.md`.
Per lo stato epistemico del progetto, vedere `../reports/STATUS.md`.
Per il formato e i contratti del dataset, vedere `SPEC.md`.

## Installazione rapida

Installazione locale in editable mode:

```bash
pip install -e .
```

Verifica rapida:

```bash
pet --help
```

## Comandi disponibili

| Comando | Scopo |
|---|---|
| `pet encode N` | codifica un intero `N` nel formato PET |
| `pet decode FILE.json` | decodifica un PET JSON e ricostruisce l'intero |
| `pet render FILE.json` | stampa una vista ad albero leggibile del PET |
| `pet validate FILE.json` | valida un PET JSON canonico |
| `pet generator N` | stampa il più piccolo intero con la stessa shape PET di `N` |
| `pet signature N` | mostra la signature canonica della shape PET di `N` |
| `pet compare N1 N2` | confronta due interi tramite distanza PET e distanza strutturale |
| `pet classify N` | classifica un intero con predicati strutturali derivati dal PET |
| `pet metrics N` | stampa le metriche strutturali canoniche |
| `pet xmetrics N` | stampa metriche estese / research |
| `pet scan START END --jsonl OUT.jsonl` | genera un dataset PET JSONL |
| `pet query ...` | filtra o raggruppa un dataset PET JSONL per campi strutturali e metriche |
| `pet atlas DATASET.jsonl` | produce statistiche atlas-style su un dataset |
| `pet shape-generators DATASET.jsonl` | mostra i primi generatori delle shape strutturali |
| `pet branch-neighbors N` | mostra le mosse PET locali in ordine canonico e deterministico |
| `pet rewrite ...` | calcola distanze, scan e matrici di rewrite PET-METICA |

## Primo percorso consigliato

Se vuoi capire PET senza perderti nei report, fai questo ordine:

1. `encode`
2. `metrics`
3. `classify`
4. `generator`
5. `signature`
6. `compare`
7. `scan`
8. `query`
9. `atlas`

È il percorso più corto tra “ho capito il comando” e “sto già osservando struttura”.

## Esempi pratici

### 1. Codificare un intero

```bash
pet encode 72
```

Versione solo JSON:

```bash
pet encode 72 --json
```

Uso tipico:

- vedere la forma PET di un intero
- ottenere una rappresentazione serializzabile

### 2. Misurare le metriche canoniche

```bash
pet metrics 72
```

Versione JSON:

```bash
pet metrics 72 --json
```

Le metriche canoniche includono:

- `node_count`
- `leaf_count`
- `height`
- `max_branching`
- `branch_profile`
- `recursive_mass`
- `average_leaf_depth`
- `leaf_depth_variance`

### 3. Esporre metriche estese / research

```bash
pet xmetrics 72
```

Versione JSON:

```bash
pet xmetrics 72 --json
```

Questo comando aggiunge, oltre alle metriche canoniche, misure esplorative come:

- `verticality_ratio`
- `structural_asymmetry`
- `subtree_mixing_score`
- `has_root_mixed_simple_pattern`

Nota: `xmetrics` è utile per ricerca esplorativa, non solo per uso operativo minimale.

### 4. Classificare un intero

```bash
pet classify 72
```

Versione JSON:

```bash
pet classify 72 --json
```

Questo comando espone predicati strutturali già derivati dal PET, per esempio:

- `is_linear`
- `is_level_uniform`
- `is_expanding`
- `is_squarefree`
- `leaf_ratio`
- `profile_shape`

È il comando più leggibile quando vuoi una sintesi qualitativa della struttura.

### 5. Trovare il generatore minimo di una shape

```bash
pet generator 7776
pet generator 1024
pet generator 4620
```

Questo comando restituisce il più piccolo intero che ha la stessa
shape strutturale PET di `N`.

Esempi tipici:

- `7776 -> 36`
- `1024 -> 64`
- `4620 -> 4620`

È utile quando vuoi separare la taglia numerica dalla forma strutturale.

### Structural factorization

PET espone la structural factorization come comando CLI ufficiale:

```bash
pet structural-factorization 24680 --max-depth 4
```

Output:

```text
PET STRUCTURAL FACTORIZATION

N = 24680
status = complete
residual_reduction_chain = 20 * 2 * 617
terminal_residual = 1
claim = PET performs structural factorization of the PET shape; classic verification confirms arithmetic factors
```

Secondo esempio:

```bash
pet structural-factorization 1224180 --max-depth 4
```

Output:

```text
PET STRUCTURAL FACTORIZATION

N = 1224180
status = complete
residual_reduction_chain = 180 * 3 * 2267
terminal_residual = 1
claim = PET performs structural factorization of the PET shape; classic verification confirms arithmetic factors
```

La structural factorization scompone la forma PET visibile del numero; la
verifica classica conferma i fattori aritmetici reali.

Per produrre anche un artifact PEST esplicativo:

```bash
pet structural-factorization 24680 --max-depth 4 --pest-json out.json
```

`--pest-json` produce un JSON `pet.syntax_tree.v0` opzionale e non decisionale.



Experimental guarded redirect mode:

    pet structural-factorization 357357 --max-depth 4 --guarded-redirect

Output:

    PET STRUCTURAL FACTORIZATION

    N = 357357
    status = complete
    residual_reduction_chain = 3 * 7 * 7 * 17 * 11 * 13
    terminal_residual = 1
    guarded_redirect = applied
    guarded_redirect_mode = flat-k
    guarded_redirect_current_anchor = 231
    guarded_redirect_redirect_anchor = 3
    guarded_redirect_structural_prefix = 77
    guarded_redirect_execution_delta = redirect-completes-with-flat-k
    claim = PET performs structural factorization of the PET shape; classic verification confirms arithmetic factors

`--guarded-redirect` is explicit opt-in. The default structural-factorization
route is unchanged.

The guarded mode only reports an applied redirect when the structural-prefix
guard triggers and the redirected route completes under an expanded scan mode.
If the guard does not trigger, PET keeps the normal structural-factorization
summary and reports `guarded_redirect = not-applied`.

This mode is experimental and does not change default PET routing.

#### Signature canonica della shape

```bash
pet signature 7776
pet signature 192
pet signature 3600 --json
```

Questo comando mostra la signature strutturale canonica della shape PET di `N`,
calcolata sul generatore minimo della classe strutturale.

Output tipico:

- `generator`: il rappresentante minimo canonico della shape
- `already_minimal`: dice se `N` è già quel rappresentante
- `child_generators`: i generatori canonici dei figli del root
- `signature`: la signature strutturale canonica serializzata
- `shape`: una vista ad albero della shape canonica (in output testuale)

È utile quando `metrics` e `classify` non bastano a distinguere collisioni
strutturali con stesso `branch_profile`.

### 6. Confrontare due interi

```bash
pet compare 12 18
```

Versione JSON:

```bash
pet compare 12 18 --json
```

Output concettuale:

- `distance` misura la distanza PET completa
- `structural_distance` ignora i valori primi e confronta solo la shape
- `same_shape = true` significa shape strutturale identica

Questo è spesso il comando più utile per rispondere alla domanda:
“questi due interi sono strutturalmente uguali o solo numericamente diversi?”

### Distanze PET vs rewrite cost

PET espone tre concetti distinti:

- `distance`: distanza PET completa tra due alberi, sensibile anche ai valori dei primi.
- `structural_distance`: distanza morfologica tra due alberi, ignorando i valori dei primi.
- `rewrite cost`: costo minimo nel grafo di riscrittura value-level usato
  dall'attuale tooling PET-METICA.

In pratica:

- usa `pet compare A B` per confrontare due PET come oggetti statici;
- usa `pet rewrite pair A B` per studiare il trasporto dinamico da `A` a `B`;
- usa `pet rewrite explain A B` quando vuoi anche una spiegazione delle mosse.

Nota: `distance` e `structural_distance` sono confronti tra strutture. Il
rewrite cost è invece una distanza di cammino nel grafo orientato esposto
dall'attuale CLI. Le sue etichette legacy non sono semantica PET canonica: il
solo contratto normativo PET/PEG 2.0 per operatori futuri è
[`../foundations/pet-peg-2.0-object-native-operators.md`](../foundations/pet-peg-2.0-object-native-operators.md).

### 7. Validare e renderizzare un PET JSON

Partendo da un file JSON:

```bash
pet validate sample.json
pet render sample.json
pet decode sample.json
```

Output atteso di `pet validate` su un file valido:

    OK

Uso tipico:

- verificare che un file PET sia canonico
- visualizzarne la struttura
- ricostruire l'intero rappresentato

### 8. Generare una scan bounded

```bash
pet scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl
```

Questo produce un dataset JSONL con:

- `n`
- `pet`
- `generator`
- `signature`
- `metrics`
- metadata di schema / formato

Per i contratti del dataset, vedere `SPEC.md`.

> [!WARNING]
> Some committed example datasets under `docs/reports/data/` still use legacy
> layouts even when their filenames suggest newer scan generations.
>
> If you need `generator` / `signature` fields or commands such as
> `same-signature`, `signature-family`, and `generator-family`, regenerate the
> dataset with the current `pet scan` command instead of trusting the filename
> alone.

### 9. Interrogare una scan con query

Dopo aver generato un dataset JSONL, puoi filtrarlo o raggrupparlo
direttamente da terminale.

Filtrare per predicati semplici:

```bash
pet query filter docs/reports/data/scan-2-10000.jsonl --where "height=2" --where "max_branching>=2" --limit 10
pet query filter docs/reports/data/scan-2-10000.jsonl --where "signature=[[[]],[[]]]"
```

Raggruppare per un campo:

```bash
pet query group-count docs/reports/data/scan-2-10000.jsonl --field branch_profile
pet query group-count docs/reports/data/scan-2-10000.jsonl --field signature
```

Campi attualmente supportati:

- `height`
- `max_branching`
- `node_count`
- `recursive_mass`
- `branch_profile`
- `average_leaf_depth`
- `leaf_depth_variance`

Operatori supportati in `--where`:

- `=`
- `>=`
- `<=`

Nota pratica:

- `branch_profile` supporta solo `=`
- esempio valido: `--where "branch_profile=[2,1]"`
- `signature` supporta solo `=`
- esempio valido: `--where "signature=[[[]],[[]]]"`

Trovare gli interi con la stessa shape strutturale di un dato `N`:

```bash
pet query same-shape docs/reports/data/scan-2-10000.jsonl 72
pet query same-shape docs/reports/data/scan-2-10000.jsonl 72 --limit 10
```

Questo comando confronta la shape PET ignorando i valori primi
e restituisce i record del dataset che hanno la stessa struttura di `N`.

Trovare o riassumere la famiglia con la stessa signature canonica di un dato `N`:

```bash
pet query same-signature docs/reports/data/scan-2-10000.jsonl 72
pet query same-signature docs/reports/data/scan-2-10000.jsonl 72 --limit 10
pet query signature-family docs/reports/data/scan-2-10000.jsonl 72
pet query signature-family docs/reports/data/scan-2-10000.jsonl 72 --preview 5
```

- `same-signature` restituisce i record con la stessa signature canonica di `N`
- `signature-family` restituisce un riepilogo della famiglia strutturale:
  - `target_n`
  - `signature`
  - `generator`
  - `count`
  - `min_n`
  - `max_n`
  - `first_values`

Trovare o riassumere la famiglia con lo stesso generatore canonico di un dato `N`:

```bash
pet query generator-family docs/reports/data/scan-2-10000.jsonl 72
pet query generator-family docs/reports/data/scan-2-10000.jsonl 72 --preview 5
```

- `generator-family` restituisce un riepilogo della famiglia con lo stesso
  generatore canonico di `N`:
  - `target_n`
  - `generator`
  - `count`
  - `min_n`
  - `max_n`
  - `first_values`
  - `distinct_signatures` (quando disponibile)

Nota pratica:
- `same-signature`, `signature-family`, `generator-family` e i filtri su
  `signature`/`generator` richiedono un dataset generato con lo schema corrente
  (`schema_version = 2`)

### 10. Analizzare una scan con atlas

```bash
pet atlas docs/reports/data/scan-2-10000.jsonl
```

Questo comando serve per osservare:

- numero di shape distinte
- distribuzioni aggregate
- segnali strutturali bounded sul dataset

### 11. Ispezionare i generatori di shape

```bash
pet shape-generators docs/reports/data/scan-2-10000.jsonl --metrics
```

Questo comando stampa i primi interi che generano nuove shape strutturali
e, opzionalmente, alcune metriche associate.


## Workflow minimo da terminale

Un workflow corto ma utile può essere questo:

```bash
pet encode 72 --json
pet metrics 72
pet classify 72
pet generator 7776
pet signature 7776
pet compare 12 18
pet branch-neighbors 12
pet scan 2 10000 --jsonl docs/reports/data/scan-2-10000.jsonl
pet query filter docs/reports/data/scan-2-10000.jsonl --where "height=2" --limit 5
pet atlas docs/reports/data/scan-2-10000.jsonl
```

## Quando usare cosa

- Usa `metrics` quando vuoi misure canoniche e stabili.
- Usa `xmetrics` quando vuoi anche misure research-facing.
- Usa `classify` quando vuoi una lettura qualitativa rapida.
- Usa `generator` quando vuoi ridurre un intero al rappresentante minimo della sua shape.
- Usa `signature` quando vuoi vedere la signature canonica della shape e distinguere collisioni che le metriche aggregate non separano.
- Usa `compare` quando vuoi confrontare due interi come struttura.
- Usa `branch-neighbors` quando vuoi vedere il branching locale canonico e deterministico.

- Usa `scan` per generare un dataset osservabile.
- Usa `query` per cercare casi strutturali specifici dentro una scan, incluse signature e generatori canonici.
- Usa `atlas` quando vuoi una vista aggregata del dataset.

### 15. PET-METICA rewrite

I comandi `pet rewrite` espongono il layer operativo PET-METICA per lavorare
su distanze, cammini minimi, scan bounded e matrici di rewrite.

Coppia:

    pet rewrite pair 12 9 --overscan 120
    pet rewrite pair 12 9 --overscan 120 --explain
    pet rewrite pair 12 9 --overscan 120 --json
    pet rewrite explain 12 9 --overscan 120
    pet rewrite explain 12 9 --overscan 120 --json
    pet rewrite explain 2 10 --overscan 120 --target-aware
    pet rewrite explain 2 10 --overscan 120 --target-aware --json
    pet rewrite friction --n-max 10 --overscan 40 --limit 3
    pet rewrite friction --n-max 10 --overscan 40 --limit 3 --json

Scan bounded:

    pet rewrite scan --n-max 20 --overscan 60
    pet rewrite scan --n-max 20 --overscan 60 --json

Matrice distanze:

    pet rewrite matrix --n-max 10 --overscan 60 --json

Uso tipico:

- calcolare un cammino minimo di rewrite tra due interi
- spiegare il significato locale delle mosse con `--explain`
- leggere il delta strutturale di `rewrite explain`
- osservare hub, asimmetrie e gap tra distanza PET-METICA e distanza numerica
- misurare la frizione di ritorno delle mosse locali con `friction`
- produrre dati bounded per analisi research-facing

`pet rewrite explain` espone anche `structural_delta`, una sintesi bounded
del cammino in quattro classi operative:

- `removed_primes`: rami primi rimossi dal supporto
- `introduced_primes`: nuovi rami primi introdotti nel supporto
- `strengthened_branches`: rami primo-esponente incrementati
- `weakened_branches`: rami primo-esponente decrementati

Questa sintesi descrive il delta strutturale del cammino trovato. Non è una
nuova prova matematica e non sostituisce la fattorizzazione: rende più leggibile
come cambia l'anatomia PET lungo un rewrite bounded.

`pet rewrite explain A B --target-aware` attiva una modalità esplicita
target-aware. Questa modalità usa la struttura del target quando disponibile per
produrre una spiegazione strutturale ottimizzata. Il comportamento predefinito
resta il rewrite canonico locale.

La modalità target-aware:

- espone `mode = target-aware`
- mantiene `canonical_cost` separato da `target_aware_cost`
- espone `optimization_gap` quando il costo canonico è disponibile
- dichiara esplicitamente `target_used = True`
- dichiara esplicitamente `factorization_used = True`
- ottimizza i cambiamenti di supporto, ma mantiene unitari gli step sugli
  esponenti

Esempio:

    pet rewrite explain 2 10 --overscan 120 --target-aware

Output essenziale:

    mode = target-aware
    canonical_cost = 3
    target_aware_cost = 1
    optimization_gap = 2
    target_used = True
    factorization_used = True
    NEW_TARGET(p=5): 2 -> 10

Questa modalità non sostituisce la distanza canonica PET-METICA: fornisce una
spiegazione strutturale diretta, utile quando il cammino canonico è più lungo o
non disponibile nel grafo bounded.

Nota: `pet rewrite` è operativo, ma resta parte del layer PET-METICA
sperimentale. I risultati di scan vanno letti come osservazioni bounded, non
come teoremi generali.

## Cosa aspettarsi dal CLI

Il CLI di PET non è pensato come shell “magica”.
È un'interfaccia operativa piccola, leggibile e composabile.

Le affermazioni forti del progetto non devono vivere nel CLI:

- la parte epistemica sta in `../reports/STATUS.md`
- la parte formale sta in `SPEC.md`
- la parte empirica bounded sta nei report sotto `docs/reports/`

## Documenti collegati

- `README.md`
- `VISION.md`
- `../reports/STATUS.md`
- `SPEC.md`
- `CHANGELOG.md`
- `docs/reports/README.md`
