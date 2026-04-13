# PET Shape Algebra v0

## Scopo

Questo modulo introduce un layer **shape-first** per PET.

Ordine concettuale:

1. manipolare la **shape**
2. solo dopo, se serve, materializzare un witness numerico compatibile

Questa v0 non prova a risolvere direttamente la ricostruzione esatta di `N` da un Partial-PET.
Il suo obiettivo è fornire una base autonoma e coerente per:

- algebra delle shape
- matching con partial shape
- minimal completion
- bounded completion frontier

---

## Oggetto base

Una `Shape` è rappresentata come struttura pura:

- `()` = leaf
- `tuple[Shape, ...]` = nodo con figli ordinati canonicamente

Nel layer shape non compaiono:

- primi
- valori numerici espliciti
- fattorizzazioni

La canonicalizzazione è fatta da `normalize_shape(...)`.

---

## Le 4 primitive core

La shape algebra v0 ha **quattro primitive**:

- `NEW`
- `DROP`
- `INC`
- `DEC`

### NEW

Aggiunge un nuovo figlio leaf al root.

```python
shape_new(shape)
```

### DROP

Rimuove un figlio leaf dal root.

```python
shape_drop(shape)
```

### INC

Applica il successore locale a un sotto-shape puntato da `path`.

```python
shape_inc(shape, path)
```

### DEC

Applica il predecessore locale a un sotto-shape puntato da `path`.

```python
shape_dec(shape, path)
```

### Dispatcher unico

Le quattro primitive sono esposte anche tramite:

```python
shape_apply(shape, op, path=())
shape_can_apply(shape, op, path=())
```

con:

- `NEW`, `DROP` validi solo su `path=()`
- `INC`, `DEC` validi solo su path non vuoti

---

## Successore / predecessore locali

`shape_succ(...)` e `shape_pred(...)` agiscono su exponent-shapes.

In questa versione non sono più hardcoded su pochi casi iniziali:
sono definiti da un **ordine canonico globale** sulle shape, basato su:

1. `shape_mass(shape)`
2. `_shape_key(shape)`

Questo rende `INC/DEC` generalizzabili senza rientrare direttamente nel layer numerico.

---

## Path e navigazione

Il targeting locale usa principalmente `PathT = tuple[int, ...]`.

Helper disponibili:

- `shape_at(shape, path)`
- `shape_paths(shape, include_root=False)`

Esistono anche helper per stable path canoniche, ma il core operativo resta sui path a indici.

---

## Bridge shape <-> PET / witness

### Proiezione PET -> shape

```python
pet_to_shape(tree)
```

Dimentica i primi e conserva solo la struttura.

### Materializzazione minima shape -> PET

```python
shape_to_pet(shape)
shape_gamma(shape)
```

- `shape_to_pet(shape)` costruisce un PET canonico minimale compatibile con la shape
- `shape_gamma(shape)` restituisce il witness numerico minimale

Questa è la regola chiave del progetto:

> prima shape, poi witness minimale compatibile

---

## Esplorazione shape-only

Helper già presenti:

- `shape_neighbors(shape)`
- `shape_closure(shape, depth)`
- `shape_frontier_levels(shape, depth)`
- `shape_shortest_path(start, target, max_depth=...)`
- `shape_distance(start, target, max_depth=...)`

Questi strumenti lavorano nel mondo puramente strutturale.

---

## Partial shape

### Rappresentazione

Una partial shape usa:

- `None` = sottostruttura ignota / hole
- `()` = leaf esatta
- `tuple[...]` = nodo parzialmente noto

Helper base:

- `normalize_partial_shape(...)`
- `partial_shape_hole_count(...)`
- `partial_shape_is_exact(...)`

### Matching

```python
shape_matches_partial(shape, partial)
pet_matches_partial_shape(tree, partial)
n_matches_partial_shape(n, partial)
```

Nota importante:
le shape sono canoniche e non ordinate semanticamente, quindi il matching partial deve essere
**shape-aware** e non un semplice `zip(...)`.

---

## Minimal completion

Questa v0 distingue chiaramente tra:

- **minimal completion**
- **completion frontier bounded**

### Minimal completion

```python
partial_shape_fill_min(partial)
partial_shape_gamma_min(partial)
partial_shape_shortest_completion_target(partial)
partial_shape_shortest_completion_gamma(partial)
partial_shape_shortest_completion_pet(partial)
```

Interpretazione:

- ogni hole interno `None` viene riempito col minimo locale `()`
- un hole al root viene riempito col minimo root-valido `((),)`

Questa parte produce:

- shape esatta minima compatibile
- witness minimo compatibile
- path minimo di completion

---

## Completion frontier bounded

Qui sta la vera completion algebra “non minima”.

Dato che con `None = sottostruttura arbitraria` le exact completions sono in generale **infinite**,
non ha senso parlare di “tutte le completions” senza bound.

La v0 usa una frontiera bounded per `max_mass`.

Helper disponibili:

- `partial_shape_completion_frontier(partial, max_mass)`
- `partial_shape_completion_gamma_frontier(partial, max_mass)`
- `partial_shape_completion_count(partial, max_mass)`
- `partial_shape_completion_levels(partial, max_mass)`
- `partial_shape_completion_gamma_levels(partial, max_mass)`
- `partial_shape_completion_profile(partial, max_mass)`
- `partial_shape_completion_gamma_profile(partial, max_mass)`
- `partial_shape_completion_report(partial, max_mass, preview=...)`

### Guardrail di reporting introdotti dopo gli stress test

I report shape/partial espongono ora due segnali operativi importanti:

- `reported_in_canonical_coordinates = yes`
- `warning = weak-stabilization`

Interpretazione pratica:

- i core e i path residui sono riportati in coordinate canoniche
- se `stable_window < 2`, il report va letto con prudenza
- un caso con `stable_window = 1` può cambiare ancora a `N+1`
- un caso con `stable_window = 0` non va trattato come conclusione strutturale robusta

### Significato di `max_mass`

`max_mass` limita la ricerca alle shape esatte con massa strutturale bounded.

Questo permette di quantificare:

- quanto resta libero nel partial
- quante completions esatte esistono fino a un certo bound
- quali witness minimi compaiono per ogni livello di massa

---

## Distinzione importante: “minimal” vs “all bounded”

Questa distinzione è fondamentale.

### Minimal completion
Risponde alla domanda:

> qual è la shape esatta minima compatibile col partial?

### Bounded completion frontier
Risponde alla domanda:

> quali shape esatte compatibili esistono fino a massa `M`?

Confondere queste due cose porterebbe dritto a risultati ambigui o falsi.

---

## Report disponibili

### Report minimale sul partial

```python
partial_shape_report(partial)
```

Restituisce:

- partial normalizzato
- exact / non exact
- hole count
- fill minimo
- target minimo
- witness minimo
- completion distance minima

### Report bounded sulla completion frontier

```python
partial_shape_completion_report(partial, max_mass, preview=...)
```

Restituisce tra l'altro:

- `hole_count`
- `completion_count`
- `per_mass_count`
- `cumulative_count`
- `per_mass_min_gamma`
- `preview_exact_shapes`
- `preview_exact_gammas`

---

## Cosa è deciso

Ad oggi sono fissati:

- `Shape` come struttura pura a tuple
- le 4 primitive core: `NEW`, `DROP`, `INC`, `DEC`
- `shape_apply(...)` come dispatcher unico
- bridge PET -> shape
- materializzazione minima via `shape_to_pet(...)` / `shape_gamma(...)`
- partial shape con `None` come hole
- minimal completion
- bounded completion frontier per `max_mass`

---

## Cosa resta aperto

I fronti aperti seri sono questi:

### 1. Addressing locale più robusto
I path a indici funzionano, ma non sono il paradiso.
Una nozione più stabile di indirizzamento locale potrebbe diventare utile.

### 2. Rewrite sul partial
Oggi il partial ha matching, completion e report.
Manca ancora una vera algebra di rewrite direttamente sul partial.

### 3. Ranking / guida della frontier
La frontier bounded c'è, ma non è ancora guidata da euristiche o priorità di ricerca.

### 4. Integrazione operativa
La shape algebra vive già bene nel modulo Python.
Manca ancora, se desiderata, una piccola interfaccia operativa dedicata.

---

## Stato attuale

La `PET shape algebra v0` è ormai una base di ricerca usabile:

- autonoma dal solver numerico come obiettivo principale
- capace di manipolare shape
- capace di produrre witness minimi
- capace di trattare partial shape
- capace di quantificare completions bounded

Quindi il progetto ha già superato la fase di “idea vaga” ed è entrato in una fase
di strumento concreto.
