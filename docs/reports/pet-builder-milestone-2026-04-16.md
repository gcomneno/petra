# PET Builder milestone — 2026-04-16

## Stato
PET Builder **completo** raggiunto in senso **operativo / research-grade**.

Questo significa che il progetto dispone ora di un builder end-to-end reale, con entrypoint unico, capace di partire da un intero `N` e arrivare fino a un `built_pet_object` tramite pipeline completa e testata.

## Cosa esiste ora

### Entrypoint unico
- Tool dedicato: `tools/pet_builder_from_int.py`
- Modulo core: `src/pet/builder_from_int.py`
- Comando CLI ufficiale/sperimentale:
  - `pet builder-from-int N --json`

### Pipeline completa
Flusso ora disponibile e verificato:

1. input `N`
2. costruzione payload CLI (`canonical` oppure `partial`)
3. `pet_support_realization.py`
4. `pet_builder_plan.py`
5. `pet_builder_execute.py`
6. emissione di:
   - artifact materializzati
   - `final_build_output`
   - `built_pet_object`

## Casi reali coperti

### Canonical real CLI cases
Verificati come `built`:
- `12`
- `24`
- `30`
- `36`
- `60`
- `120`
- `210`
- `420`
- `840`
- `2310`
- `30030`

### Partial real CLI cases
Verificati come `built`:
- `18`
- `20`
- `1234567890`
- `1234567890123`

## Milestone tecniche chiuse

### 1. Support realization utile al builder
- peeling di `known_divisors`
- metriche di peeling e readiness
- distinzione tra blocchi:
  - pre-known
  - peeled
  - fully peeled
  - partial
  - blocked
  - not attempted

### 2. Builder plan
- readiness esplicita
- action chiara
- manifest
- script steps
- build result simulato

### 3. Builder execute
- materializzazione artifact su disco
- `final_build_output`
- `built_pet_object`
- assembly trace
- finalization metadata

### 4. CLI integration
- `build-from-int --allow-non-canonical-support` gestisce anche casi overshoot come `18`
- `builder-from-int` è disponibile come porta CLI unica del builder

### 5. Core integration
- il motore del builder vive ora anche nel package:
  - `src/pet/builder_from_int.py`

## Stato test al raggiungimento milestone
Smoke builder-oriented verde con:

- `72 passed`

Include copertura su:
- `tests/test_pet_builder_from_int.py`
- `tests/test_pet_builder_e2e.py`
- `tests/test_pet_builder_execute.py`
- `tests/test_pet_builder_plan.py`
- `tests/test_pet_support_realization.py`
- `tests/test_cli_build_from_int.py`

## Significato della milestone
Il progetto non ha più soltanto:
- tool sparsi
- pipeline manuali
- skeleton separati

Ha ora un **PET Builder vero**, con front door esplicito, output built finale e copertura reale su casi canonical e partial.

## Limite noto residuo
La support realization non è ancora una chiusura teoricamente universale per ogni caso immaginabile.

Tuttavia questo non impedisce di considerare la milestone raggiunta: il builder è ora completo in senso operativo, integrato e testato sul perimetro reale rilevante per il progetto.

## Formula finale
**PET Builder completo raggiunto (operativo / research-grade).**
