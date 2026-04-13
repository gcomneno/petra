# Partial Shape Target

## Risultato ufficiale attuale

Il risultato operativo ufficiale del layer shape-first è una:

**Observed Compatible Decomposition**

cioè una decomposizione osservata del Partial-PET in:

- `observed_core`
- `observed_core_kind`
- `residual_free_paths`
- `residual_local_profiles`
- `evidence`

Questa decomposizione è esposta dalla CLI ufficiale tramite:

```bash
pet partial-shape-target '<partial>' ...
```

---

## Significato dei campi

### `observed_core`

È la parte di struttura che risulta **robusta nel bound osservato**.

Non va interpretata come prova assoluta della massima struttura compatibile.
Va interpretata come il miglior **core compatibile osservato e stabilizzato** entro il bound ispezionato.

### `observed_core_kind`

Classifica il tipo di core osservato:

- `empty`
- `root-arity-only`
- `partially-structured`
- `exact`

### `residual_free_paths`

Sono i path in cui resta libertà strutturale residua.

Nota importante:
questi path vanno letti in **coordinate canoniche** della partial/shape normalizzata,
non come coordinate “geometriche originali” del ramo scritto in input.

Quando la CLI stampa:

- `reported_in_canonical_coordinates = yes`

significa esattamente questo:
`observed_core` e `residual_free_paths` descrivono un rappresentante canonico della classe osservata.

### `residual_local_profiles`

Per ogni free path descrive:

- `local_forced_core`
- `local_forced_core_kind`
- `observed_local_count`
- `observed_local_shapes`
- `observed_local_gammas`

### `evidence`

Raccoglie il contesto osservativo:

- `max_mass`
- `stable_window`
- `stabilization_mass`
- `forced_hole_count`
- `fast_preview`

Lettura pratica di `stable_window`:

- `stable_window >= 2` → risultato abbastanza leggibile operativamente
- `stable_window = 1` → risultato provvisorio; a `N+1` può ancora cambiare faccia
- `stable_window = 0` → risultato non affidabile come lettura strutturale

Quando la CLI stampa:

- `warning = weak-stabilization`

significa che il caso è ancora in questa zona debole e non va letto troppo forte.

---

## Cosa garantiamo

Con `partial-shape-target` il progetto oggi garantisce una separazione pratica tra:

- parte **osservata come forzata**
- parte **osservata come libera**

entro un bound strutturale finito.

---

## Cosa NON garantiamo ancora

Non garantiamo ancora che `observed_core` coincida sempre con una:

**massima struttura compatibile dimostrata in assoluto**

Inoltre, nei casi simmetrici, `observed_core` può essere esposto tramite
un rappresentante canonico della classe osservata: per questo la direzione
apparente dei rami non va sempre interpretata come informazione intrinseca.

Questa resta una frontiera aperta del progetto.

Quindi la lettura corretta è:

- sì: risultato strutturale utile, stabile, operativo
- no: non ancora teorema finale di massimalità assoluta

---

## Lettura pratica

### Caso 1

```bash
pet partial-shape-target '((), None)' --max-mass 5
```

Lettura tipica:

- è robustamente forzato un leaf al root
- l'altro ramo resta libero

### Caso 2

```bash
pet partial-shape-target '(None, (None,))' --max-mass 6
```

Lettura tipica:

- sopravvive solo l'arità 2 del root
- non sopravvive la distinzione iniziale tra ramo semplice e ramo strutturato

### Caso 3

```bash
pet partial-shape-target '((None,), (None,))' --max-mass 8
```

Lettura tipica:

- la shell esterna a due rami con un figlio interno ciascuno regge
- i due buchi interni restano liberi

---

## Comando ufficiale da usare

Il comando di riferimento, da qui in poi, è:

```bash
pet partial-shape-target '<partial>' [--max-mass N | --auto-window W --max-mass-cap C] [--fast-preview]
```

Gli altri comandi restano utili come supporto tecnico, ma questo è il punto di arrivo semantico principale.
