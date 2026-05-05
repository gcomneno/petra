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
