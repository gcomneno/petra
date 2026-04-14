# Partial-PET preimage search note

## Idea

Filone operativo: **preimage search from Partial-PET**.

Obiettivo pratico:
- partire da un `Partial-PET` / seed compatibile
- esplorare preimmagini plausibili con mosse forward
- distinguere chiaramente:
  - informazione **certificata** dal probe
  - ipotesi del **synth**
  - ricerca di stati/numeri compatibili

Questa search **non** ricostruisce in generale `N` esatto.  
Nello stato attuale, produce ed esplora una frontier di numeri compatibili con un seed PET e con alcuni vincoli estratti dal `Partial-PET`.

---

## Stato implementativo raggiunto

Tooling aggiunto in `tools/pet_preimage_seed.py`:

- costruzione seed da `partial-explain`
- espansione forward con `NEW` / `INC`
- mini-BFS con:
  - dedup per `current_n`
  - materializzazione multi-parent
  - pruning su `current_n`
- filtri aggiuntivi:
  - `max_new_in_path`
  - `require_known_children_covered`
- helper di profilo:
  - `recommended_search_profile(...)`
  - `run_profiled_search(...)`
  - `build_profiled_search_report(...)`
- helper di analisi vincoli:
  - `constraint_report_for_n(...)`

---

## Osservazioni empiriche principali

### 1. Seed-only search era troppo cieca

Con seed uguale, la frontier risultava uguale anche per casi concettualmente diversi.

Caso dimostrativo:
- `4452484` (exact, seed `420`)
- `84739348317483740132` (open, seed `420`)

Prima dei filtri constraint-aware:
- stessa frontier numerica
- stessa crescita
- differenze del probe non usate davvero dalla search

Conclusione:
- la search iniziale era ancora troppo **seed-driven**

### 2. Il pruning giusto era su `current_n`

Il problema grosso non era solo il branching, ma la ridondanza da path multipli verso lo stesso `current_n`.

Il pruning con dedup per `current_n` ha:
- abbattuto il `dup_factor`
- mantenuto gli stati distinti
- reso la frontier leggibile e gestibile

### 3. `max_new_in_path=2` è un buon budget

Sui casi studiati:
- `max_new_in_path=1` era troppo aggressivo
- `max_new_in_path=2` teneva quasi tutto il nocciolo utile
- `max_new_in_path=3` aggiungeva soprattutto coda

Conclusione:
- `max_new_in_path=2` è una buona baseline

### 4. `require_known_children_covered` è utile sui casi open, troppo duro sugli exact

Risultato qualitativo:
- **open / partial**: il filtro migliora la frontier
- **exact**: come default può tagliare troppo

Quindi la policy giusta non è universale:
- `exact_root_anatomy = False` -> filtro attivo
- `exact_root_anatomy = True` -> filtro spento

---

## Profilo operativo raccomandato

Helper:
- `recommended_search_profile(seed, mode="quick" | "deep")`

Policy codificata:

- `rank = 1`
- `max_new_in_path = 2`
- `require_known_children_covered = not exact_root_anatomy`

Modalità:
- `quick` -> `max_target_n = 5_000_000`
- `deep` -> `max_target_n = 15_000_000`

---

## Batch empirico di riferimento (depth = 6)

| case | probe_exact | probe_status | seed_n | quick_count | quick_max | deep_count | deep_max |
|---|---:|---|---:|---:|---:|---:|---:|
| `exact-180` (`16562`) | yes | `unit` | 180 | 27 | 2,910,600 | 28 | 10,672,200 |
| `exact-420` (`4452484`) | yes | `unit` | 420 | 24 | 3,603,600 | 27 | 12,612,600 |
| `open-420` (`84739348317483740132`) | no | `composite-non-prime-power` | 420 | 17 | 3,603,600 | 19 | 12,612,600 |
| `exact-13860` (`40072356`) | yes | `unit` | 13860 | 7 | 4,989,600 | 15 | 14,414,400 |
| `open-60060` (`54841245428`) | no | `composite-non-prime-power` | 60 | 19 | 970,200 | 20 | 5,336,100 |

### Lettura del batch

- casi con stesso seed possono divergere dopo l'introduzione dei filtri constraint-aware
- `open-420` vs `exact-420` è il caso guida:
  - stesso seed
  - comportamento diverso
  - la search non è più puramente seed-driven
- il profilo `quick` cattura già gran parte del nocciolo utile
- `deep` serve soprattutto a raccogliere la coda

---

## Punto concettuale acquisito

Lo stato corrente non è ancora una ricerca “fully constraint-driven”.

È però una prima forma operativa di:

- search **profilata**
- **pruned**
- con un minimo di uso reale dei vincoli certificati dal `Partial-PET`

In altre parole:
- non più solo “search dal seed”
- non ancora “reconstruction guided by full Partial-PET semantics”
- ma una baseline seria e ripetibile

---

## Prossimi passi sensati

1. usare questa baseline per batch più ampi su casi open reali
2. studiare filtri/score più fini oltre a `known_children_covered`
3. misurare quanto la frontier resta stabile al crescere di depth/cap
4. chiarire se serve una ranking function constraint-aware, non solo pruning hard

