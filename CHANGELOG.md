# Changelog

Tutte le modifiche rilevanti di questo progetto saranno documentate qui.

Il formato si ispira a Keep a Changelog.
Versioning corrente: `0.y.z`.

## [Unreleased]

### Added
- Aggiunti tool research PET-METICA: `pet_metica_range_sweep.py` (scan multi-tier) e `pet_metica_seven_family_probe.py` (probe mirato su `7×{2^k,3^k}`), con test e report generated associati.
- Aggiunta research note `docs/research/notes/pet_metica_seven_family_tier_drift.md` e scorecard di chiusura pass in `docs/research/experiments/pet-metica-seven-family-ladder-pass.md`.
- Aggiunto il passaggio di fondazione first-principles: esempi, semantica `collapse(P)`, audit implementativo, classificazione moduli, audit metriche e boundary per API aliases.
- Aggiunto `scripts/check_docs_consistency.py` per controllare link Markdown locali e riferimenti Python sorgente non più esistenti.
- Aggiunto il target `make docs-check` per eseguire il controllo documentale leggero.
- Aggiunta la pipeline canonica `tools/pet_triage_pipeline.sh` per il workflow PET triage.
- Aggiunto il flusso PET race diagnostic -> classic handoff policy -> classic verification.
- Aggiunti namespace operativi per i tool:
  - `tools/core/`
  - `tools/classic/`
  - `tools/legacy/`
  - `tools/research/`
- Aggiunti wrapper compatibili root-level per preservare i vecchi percorsi `tools/*.py` e `tools/*.sh`.
- Aggiunta `.pet-cache/` come area locale per cache, stati e artefatti generati non tracciati.

### Changed
- Chiarita nella documentazione pubblica la separazione tra PET-Base, First-principles PET, PET-Metrics, PET/PEG 2.0 e PET-METICA.
- Allineati README, SPEC/STATUS e foundation docs intorno ai confini tra contratto stabile, layer object-native, metriche estese e tooling research.
- Corretto il riferimento storico `src/pet_algebra.py` verso il percorso reale `src/pet/algebra.py`.
- `tools/peelator.sh` ora è un wrapper compatibile verso `tools/pet_triage_pipeline.sh`.
- I tool PET triage core sono stati spostati sotto `tools/core/`.
- I tool di scansione classic sono stati spostati sotto `tools/classic/`.
- I vecchi lens diagnostics sono stati spostati sotto `tools/legacy/`.
- I tool report/research/PET-METICA sono stati spostati sotto `tools/research/`.
- Aggiornata la documentazione operativa per riflettere la tassonomia namespaced dei tool.

### Removed
- Rimossi dal tracking Git artefatti PET generati precedentemente presenti sotto `artifacts/`.
- Rimossi esperimenti falliti di builder, support-realization, dismantle, bytes-to-build e pet-friendliness.
- Rimossi i comandi di planning target-directed `plan`, `branch-plan`, `plan-best` e `branch-plan-best`.

## [0.1.4] - 2026-04-14

### Added
- Nuovo comando pubblico `pet generator` per calcolare il più piccolo intero con la stessa shape PET di un dato `N`.
- Nuovo test end-to-end per il CLI pubblico `generator`.
- Nuovo sottocomando `pet query same-shape` per trovare nei dataset scan gli interi con la stessa shape strutturale PET di un dato `N`.

### Changed
- Aggiornata la guida pratica del CLI con esempi per `pet generator` e `pet query same-shape`.

## [0.1.3] - 2026-03-27

### Added
- Nuovo comando pubblico `pet query` per interrogare dataset PET JSONL generati con `scan`.
- Sottocomandi `pet query filter` e `pet query group-count` per filtrare o raggruppare record tramite metriche PET.
- Nuovi test end-to-end per il CLI pubblico `query`.

### Changed
- `tools/scan_query.py` ora riusa la logica del modulo package `pet.query` invece di duplicarla.
- Aggiornata la documentazione pratica del CLI per includere la nuova capacità di query sui dataset scan.

## [0.1.2] - 2026-03-27

### Added
- Nuovo comando `pet xmetrics` per esporre metriche estese / research dal CLI.
- Nuovo comando `pet compare` per confrontare due interi tramite distanza PET e distanza strutturale.
- Nuovo comando `pet classify` per classificare un intero con predicati strutturali derivati dal PET.
- Nuovi test end-to-end per `xmetrics`, `compare` e `classify`.
- Nuovo test negativo per `tools/scan_query.py` sul vincolo `branch_profile only supports '='`.

### Changed
- Il CLI pubblico espone ora una parte più ampia delle capacità già mature del progetto.

## [0.1.1] - 2026-03-27

### Added
- GitHub Actions CI con esecuzione automatica della test suite su Python 3.10, 3.11 e 3.12.
- Licenza MIT.
- Badge nel README per CI, release, licenza e supporto Python.
- Nuovo modulo `pet.io` per serializzazione JSON, parsing e rendering PET.

### Changed
- Metadata packaging modernizzati in `pyproject.toml`.
- Gli script esplorativi ora usano per default il dataset canonico `docs/reports/data/scan-2-1000000.jsonl`, con override da riga di comando.
- La CLI è stata spostata fuori da `core.py` nel modulo dedicato `pet.cli`.
- `core.py` è stato alleggerito separando meglio logica PET, I/O e interfaccia CLI.

### Removed
- Rimosso dal CLI il comando `shapes-growth`, esposto ma non realmente implementato nel package.

## [0.1.0] - 2026-03-27

### Added
- Prima release pubblica del progetto PET.
- CLI iniziale per encode, decode, render, validate, metrics, scan, atlas e shape-generators.
- Test suite automatizzata per core, metriche, scan, report contracts e tooling essenziale.
- Documentazione iniziale del progetto, incluse `VISION.md`, `STATUS.md`, `SPEC.md` e report bounded sotto `docs/reports/`.

### Notes
- `v0.1.0` rappresenta la prima baseline pubblica del repository prima del successivo hardening di packaging, CI e modularizzazione.
