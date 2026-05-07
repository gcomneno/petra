# PET Shadow Projection

## Shape scale spectrum

The first `pi`-scale experiments were useful, but the current evidence does not
support treating pi as a privileged projection scale.

On the tested decimal lengths, `digits / pi` often rounds to the same segment
length as `digits / 3`.  The scale comparison tool therefore reports an
`effective_scale_alias` field, so that apparent pi-scale observations are not
over-interpreted when they are operationally identical to another scale.

The current claim is weaker and more useful:

> PET-shadow projection should be studied as a scale spectrum, not as a single
> privileged scale.

The helper tool is:

    tools/research/pet_shape_scale_compare_study.py

It compares visible segment projections across relative scale rules such as
`pi`, `third`, `half`, `quarter`, `sqrt-digits`, and `log2-digits`.

The output is projection-only:

    scale comparison only; visible segment projection only; not PET(N)

### Early scale-spectrum observations

Small empirical sample:

| N | digits | lowest-noise scale | highest-dominant scale | pi alias | field class |
|---|---:|---|---|---|---|
| `100000000003900000091` | 21 | half | half | pi,third | has-strong-scale |
| `100000000000000000091` | 21 | half | half | pi,third | has-strong-scale |
| `1000000000000000000000091` | 25 | pi | pi | pi,third | has-weak-scale |
| `9999999999000000000119` | 22 | sqrt-digits | sqrt-digits | pi,third | has-strong-scale |
| `999999990000000119` | 18 | pi | pi | pi,third | has-strong-scale |
| `999999999999000000000119` | 24 | sqrt-digits | sqrt-digits | pi,third | has-strong-scale |
| `1234567891234567891234567` | 25 | half | half | pi,third | diffuse-all-scales |
| `3141592653589793238462643` | 25 | half | half | pi,third | diffuse-all-scales |
| `2718281828459045235360287` | 25 | half | pi | pi,third | diffuse-all-scales |

Early reading:

- sparse zero fields can expose a low-noise scale, but the winning scale appears
  length-sensitive;
- saturated 9/0 fields tend to produce a strong-scale resonance in this sample;
- digit-mixed opaque inputs remain diffuse across the tested scales.

These are empirical observations only.  They do not reconstruct `PET(N)`, do not
identify a true PET generator for `N`, and do not establish a mathematical
classification.

### Periodic decimal fields

A follow-up check suggests that periodic decimal fields should be tracked as a
separate empirical family instead of being merged into generic mixed opaque
inputs.

Small sample:

| N | digits | lowest-noise scale | highest-dominant scale | pi alias | field class |
|---|---:|---|---|---|---|
| `1212121212121212121212121` | 25 | sqrt-digits | sqrt-digits | pi,third | has-strong-scale |
| `9090909090909090909090909` | 25 | sqrt-digits | sqrt-digits | pi,third | has-single-generator-scale |

Early reading:

- periodic fields can expose scale-specific resonance;
- in the `909090...` sample, the visible matches collapse to a single generator
  at the `sqrt-digits` / `log2-digits` alias band;
- this is still projection-only evidence and does not identify `PET(N)`.

### Target-generator sensitivity

A small target-basis check suggests that the broad field-class separation is
more stable than the exact winning scale.

Across the tested target generator sets:

- sparse zero fields remained in `has-strong-scale` / `has-weak-scale`;
- saturated 9/0 fields remained in `has-strong-scale`;
- digit-mixed opaque inputs remained in `diffuse-all-scales`;
- periodic fields remained structured when their visible generator basis was
  included.

The important caveat is target sensitivity for single-generator resonance.
For example, `9090909090909090909090909` exposes a clean generator-12 resonance
at the `sqrt-digits` / `log2-digits` alias band when `12` is included in the
target generator set.  If `12` is excluded, the same input can become
`no-visible-target-shape`.

So the current empirical claim is:

> `field_class` appears useful for separating digit-mixed opaque inputs from
> structured decimal fields, but single-generator outcomes depend on the chosen
> target generator basis.

## Projection operators

The current PET-shadow line can be described with two projection operators.

These operators are research tools.  They do not reconstruct `PET(N)`, do not
identify the true PET generator of `N`, and do not prove a mathematical
classification.

### Π_shape: local visible segment projection

`Π_shape` is the local projection layer.

Given an opaque integer `N`, a visible base, a scale rule, and a target generator
basis, it:

1. writes `N` in the visible base, currently decimal;
2. extracts visible digit segments at the selected scale;
3. computes local PET signatures for those segments;
4. keeps the local generators that resonate with the target basis;
5. summarizes the resulting local shadow field.

The current helper tool is:

    tools/research/pet_shape_scale_compare_study.py

Its summary fields include:

- `field_class`;
- `lowest_noise_scale`;
- `highest_dominant_scale`;
- `highest_dominant_ratio`;
- `pi_effective_scale_alias`.

The main empirical lesson so far is:

> `Π_shape` can expose local PET-style resonances, but local resonance does not
> imply a coherent global shadow.

### Ω_shape: positional overlap projection

`Ω_shape` is the positional overlap layer.

It starts from the same visible segment projections as `Π_shape`, but instead of
only counting local generator matches, it overlays them across the digit
positions of `N`.

For each digit position, it records which local shadow generators cover that
position.  This gives a positional overlap field.

The current helper tool is:

    tools/research/pet_shape_overlap_projection_study.py

Its summary fields include:

- `best_overlap_scale`;
- `best_overlap_hint`;
- `best_position_coverage_ratio`;
- `best_position_agreement_ratio`;
- `best_dominant_position_generator`;
- `best_dominant_position_ratio`;
- `best_average_position_entropy`.

Observed overlap hints include:

- `coherent-single-generator-overlap`;
- `coherent-dominant-overlap`;
- `dominant-diffuse-overlap`;
- `diffuse-overlap-field`;
- `mixed-overlap-field`;
- `sparse-overlap-field`;
- `no-visible-overlap`.

The main empirical lesson so far is:

> `Ω_shape` separates local resonance from positional coherence.

For example:

| N | Π_shape reading | Ω_shape reading |
|---|---|---|
| `9090909090909090909090909` | `has-single-generator-scale` | `coherent-single-generator-overlap` |
| `1212121212121212121212121` | `has-strong-scale` | `dominant-diffuse-overlap` |
| `1234567891234567891234567` | `diffuse-all-scales` | `diffuse-overlap-field` |

This distinction matters because a number may show strong local resonance while
still producing a noisy positional overlap field.

### Route correlation layer

A third research helper compares PET-shadow observations against decimal
rigidity and full PET signature cost:

    tools/research/pet_shadow_route_correlation_study.py

The current empirical claim is limited:

> PET-shadow route correlation does not yet separate timeout from non-timeout,
> but it can distinguish decimal-rigid structured timeouts from diffuse opaque
> timeouts on the tested sample.

This is still triage evidence only.

### Ω_shape and route correlation

A follow-up correlation check included both the local projection summary
`Π_shape` and the positional overlap projection `Ω_shape`.

Small sample with a short full-signature timeout budget:

| N | Π_shape field class | Ω_shape overlap hint | route pressure hint |
|---|---|---|---|
| `100000000003900000091` | `has-strong-scale` | `diffuse-overlap-field` | `decimal-rigid-timeout` |
| `9999999999000000000119` | `has-strong-scale` | `mixed-overlap-field` | `decimal-rigid-timeout` |
| `1234567891234567891234567` | `diffuse-all-scales` | `diffuse-overlap-field` | `shadow-diffuse-timeout` |
| `3141592653589793238462643` | `diffuse-all-scales` | `diffuse-overlap-field` | `shadow-diffuse-timeout` |
| `1212121212121212121212121` | `has-strong-scale` | `dominant-diffuse-overlap` | `structured-shadow-timeout` |
| `9090909090909090909090909` | `has-single-generator-scale` | `coherent-single-generator-overlap` | `structured-shadow-timeout` |

Current reading:

- with the tested short timeout budget, `Ω_shape` does not yet separate timeout
  from non-timeout;
- `Ω_shape` does improve the structural diagnosis by separating diffuse overlap,
  mixed overlap, dominant noisy overlap, and coherent single-generator overlap;
- therefore `Ω_shape` currently behaves more like a diagnostic refinement than a
  cost predictor.

Current empirical claim:

> `Ω_shape` improves PET-shadow structural diagnosis, but it has not yet shown
> independent timeout-prediction power on the tested sample.

## Motivazione

La costruzione completa di `PET(N)` può diventare troppo costosa per input
grandi o opachi. In questi casi non è sempre ragionevole partire da
`shape_signature_dict(N)` o dalla race PET completa.

La linea `PET shadow projection` studia un'alternativa più prudente:

```text
non aprire subito tutta la patata;
osserva la sua ombra rappresentazionale;
cerca forme PET locali visibili;
costruisci una proiezione parziale dichiaratamente non esatta.
```

Questa linea nasce dai casi in cui:

- `decimal-rigid-border` viene riconosciuto rapidamente;
- `large non-rigid opaque inputs` possono comunque rendere costosa la firma PET;
- blocchi locali risultano economici anche quando la firma globale va in timeout.

## Non-claim fondamentali

`PET shadow projection` non è `PET(N)`.

Non afferma:

```text
PET_shadow(N) = PET(N)
```

Non afferma che i blocchi visibili siano fattori di `N`.

Non usa divisibilità classica, moduli piccoli primi o trial division come nucleo
della proiezione.

Il claim corretto è:

```text
projection only; this does not reconstruct PET(N)
```

La proiezione può produrre hint, non verità canoniche.

## Occhiali PET-mode

La regola metodologica è:

```text
partire solo da ciò che è visibile o budgetabile
e interpretarlo con forme PET note.
```

Segnali ammessi nel nucleo PET-style:

- base e lunghezza della rappresentazione;
- profili di blocchi e transizioni;
- empty/unit/saturated edges;
- firme PET locali di masse visibili budgetabili;
- stabilità multi-scala;
- risonanza con generatori PET noti;
- stato budgeted della firma globale.

Segnali esclusi dal nucleo:

- ricerca di divisori;
- piccoli moduli primi;
- fattorizzazione classica;
- interpretazioni che fingono di ricostruire `PET(N)`.

## Block projection

La block projection taglia la rappresentazione decimale di `N` in blocchi
posizionali e osserva la PET locale dei blocchi informativi.

Esempio:

```text
100000000003900000091
block_width = 4
blocks = 1 | 0000 | 0000 | 0039 | 0000 | 0091
```

I blocchi `0000` e `0001` sono trattati come unit/empty shadow.
I blocchi informativi possono avere una firma PET locale, ad esempio:

```text
0039 -> generator 6, signature [[], []]
0091 -> generator 6, signature [[], []]
```

Questo non significa che `39` o `91` siano componenti fattoriali di `N`.
Significa solo che alcune masse visibili locali proiettano la stessa forma PET.

Tool:

```bash
tools/research/pet_block_projection_study.py
```

## Packed shadow summary

Il packed shadow summary sintetizza le ombre locali:

- `informative_block_count`
- `unit_or_empty_block_count`
- `local_generator_set`
- `dominant_local_generator`
- `full_generator_in_local_set`
- `transition_kinds`
- `shadow_coupling_hint`
- `candidate_shadow_generator`

Il campo `candidate_shadow_generator` è un generatore locale candidato, non il
generatore vero di `PET(N)`.

Claim corretto:

```text
candidate_shadow_claim = local projection only; not PET(N)
```

Osservazione importante:

```text
il generatore globale può essere assente da tutti i generatori locali.
```

Quindi la ricomposizione non può essere un semplice merge delle PET locali.

## Multiscale shadow

Il taglio a blocchi fissi è sensibile alla scala scelta.
Per questo è stata introdotta una lettura multi-scala.

Tool:

```bash
tools/research/pet_multiscale_shadow_study.py
```

Esempio di campi:

- `candidate_shadow_generators`
- `candidate_generator_stability`
- `non_identity_candidate_stability`
- `dominant_shadow_coupling_hint`
- `local_generator_hit_count`
- `identity_scale_count`
- `scale_sensitivity`

Risultato osservato:

```text
un singolo candidate_shadow_generator è fragile;
la stabilità multi-scala e il coupling hint sono più informativi.
```

Esempio significativo:

```text
100000000003900000091
candidate_shadow_generators = 6,6,6
scale_sensitivity = low
```

Questo suggerisce una possibile ombra strutturale stabile, pur senza costruire
`PET(N)` completo.

## Shape-aware projection

La shape-aware projection non taglia solo per blocchi fissi.
Cerca segmenti visibili che risuonano con generatori PET noti.

Tool:

```bash
tools/research/pet_shape_aware_projection_study.py
```

Generatori target iniziali:

```text
2,4,6,12,30,36,60,210
```

Questi rappresentano famiglie PET locali note e ricorrenti.

Output rilevanti:

- `matched_segment_count`
- `matched_position_coverage`
- `matched_generator_counts`
- `matched_generator_unique_count`
- `dominant_matched_generator`
- `dominant_matched_generator_ratio`
- `shape_aware_projection_hint`

La prima versione `up-to-max` cercava troppi segmenti piccoli e produceva rumore.
È utile come baseline, ma troppo permissiva.

## Pi-scale lens

La lente `pi-scale` nasce dall'idea che la massa inscritta non debba avere una
dimensione fissa.

Invece di usare un massimo arbitrario di cifre, si usa una scala proporzionale
alla lunghezza visibile di `N`:

```text
pi_scale_digits = round(N_digits / pi)
```

Il tool cerca segmenti nella zona:

```text
pi_scale - radius
pi_scale
pi_scale + radius
```

Esempi:

```text
N_digits = 21 -> pi_scale_digits = 7
N_digits = 25 -> pi_scale_digits = 8
N_digits = 35 -> pi_scale_digits = 11
```

Questa lente non afferma che `pi` sia una legge aritmetica.
È una scala sperimentale di proiezione proporzionata alla massa rappresentazionale.

Uso:

```bash
tools/research/pet_shape_aware_projection_study.py --scale-rule pi --scale-radius 1 N
```

Osservazioni iniziali:

```text
100000000003900000091 -> dominant_matched_generator = 6
123456789123456789... -> dominant_matched_generator = 210
9999999999000000000119 -> dominant_matched_generator = 60
```

La lente `pi-scale` riduce il rumore delle micro-finestre e sposta la risonanza
verso masse locali più proporzionate.

## Relazione con la metafora

La metafora operativa è:

```text
pi = operatore/lente di proiezione
sole = N enorme opaco
masse inscritte = segmenti o blocchi visibili
campo tra masse = coupling posizionale
radiografia finale = PET shadow globale
```

La domanda non è:

```text
posso ricostruire PET(N) dai blocchi?
```

La domanda più prudente è:

```text
posso ottenere una base strutturale candidata
o un hint stabile osservando ombre locali?
```

## PACK_shadow come fronte aperto

Il futuro operatore `PACK_shadow` non deve essere definito come merge esatto
delle PET locali.

Una formulazione più sana è:

```text
PACK_shadow(local_projections, positional_edges) -> global_shadow
```

Output possibile:

- `packed_shadow_status`
- `pet_exact_claim = none`
- `candidate_shadow_generator`
- `shadow_basis_hint`
- `coupling_hint`
- `scale_sensitivity`
- `projection_confidence`

Fronte aperto:

```text
capire quali proprietà della PET globale
sono predicibili o vincolabili dalle ombre locali.
```

Non si assume che la ricostruzione PET esatta sia possibile.

## Stato attuale

Questa linea è research-only.

Tool disponibili:

```text
tools/research/pet_block_projection_study.py
tools/research/pet_multiscale_shadow_study.py
tools/research/pet_shape_aware_projection_study.py
```

Le evidenze attuali suggeriscono:

- block projection a scala singola è fragile;
- multi-scale shadow è più informativo;
- shape-aware projection riduce l'arbitrarietà del taglio;
- pi-scale è una lente promettente per evitare micro-segmenti rumorosi;
- il candidate generator va trattato come shadow generator, non come generatore di `PET(N)`.

## Regola finale

```text
Le patatone motivano l'operatore.
Le patatine lo insegnano.
```


## Recursive PET shape chunk study

`tools/research/pet_recursive_shape_chunk_study.py` is a diagnostic study for
small digit-mixed numbers where the real PET signature is still computable.

The goal is not to reconstruct `PET(N)` for opaque inputs. The goal is to test
whether the real PET generator is locally preserved in decimal subsegments.

The study recursively searches decimal split points and compares:

- the parent segment PET generator;
- the left/right child segment PET generators;
- product, gcd, and lcm merge candidates over the local PET generators;
- whether the parent generator is preserved locally;
- whether the lcm-style merge is stable;
- whether the generator appears to be globally emergent.

Important diagnostic statuses:

- `local-preservation-success`: the parent PET generator is visible in a child
  segment or through the lcm-style local generator merge.
- `parent-preserved-locally`: the parent generator appears directly in one side
  of the split.
- `parent-preserved-and-lcm-stable`: the parent generator appears locally and
  the lcm-style generator merge agrees with it.
- `emergent-global-generator`: the parent generator is not visible locally and
  is larger than the local/lcm support seen by the split.
- `no-local-support`: the chosen split does not preserve the parent generator.

Current empirical result on small digit-mixed samples:

- `Σ_backbone` often collapses to low generic support such as `6`.
- `Λ_chunk` can distinguish local-preservation cases from globally emergent
  generator cases.
- This is diagnostic only; it does not reconstruct `PET(N)` for opaque inputs.

Interpretation:

`Σ_backbone` remains a global shadow/support sensor. `Λ_chunk` acts as a local
PET-shape microscope for digit-mixed fields.


## PET shadow monster router

`tools/research/pet_shadow_monster_router.py` combines the global `Σ_backbone`
signal with optional local `Λ_chunk` diagnostics and routes each input into a
diagnostic monster class.

It does not factor `N` and does not reconstruct `PET(N)`.

Current route classes include:

- `saturated-shadow-coherent`
- `sigma-coherent-large-field`
- `weak-or-unstable-shadow-field`
- `fragile-shadow-field`
- `local-preserved-shadow-coherent`
- `local-preserved-sigma-floor-risk`
- `deceptive-stable-sigma`
- `diffuse-field`

Large inputs skip recursive chunk diagnosis by default through
`--max-chunk-digits 8`, avoiding expensive local segmentation on opaque numbers.

Use `--progress` to print per-number progress messages to stderr.

