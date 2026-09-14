# Changelog

Tutte le modifiche rilevanti di questo progetto saranno documentate qui.

Il formato si ispira a Keep a Changelog.
Versioning corrente: `1.y.z`.

## [1.0.3] — 2026-09-14

### Fixed
- `tests/test_petra_distribution_boundary.py::test_distribution_source_boundary_keeps_legacy_out_of_package_discovery`: stesso trattamento del test gemello già sistemato in 1.0.2. Ora skippa esplicitamente quando `src/pet/` è assente, così distribuzioni self-contained (es. archivio Zenodo) restano autoconsistenti.

## [1.0.2] — 2026-09-14

### Fixed
- `tests/test_petra_distribution_boundary.py`: il test che verifica la presenza di `src/pet/` ora skippa esplicitamente quando il runtime storico è assente, invece di fallire. Necessario per distribuzioni self-contained che omettono volontariamente `src/pet/` (es. archivio Zenodo della superficie pubblica). Il test diventerà no-op automaticamente quando Phase 10 rimuoverà il runtime storico.

## [1.0.1] — 2026-09-14

### Fixed
- `tests/conftest.py`: il pattern `startswith("test_pet")` marcava erroneamente come `legacy` anche i test `test_petra_*`, escludendoli dal gate CI canonical. Il marker ora richiede `test_pet.py`, `test_pet_*` o `test_tools_pet_*` espliciti.
  - Prima: 198 canonical / 1078 legacy
  - Dopo: 719 canonical (655 non-slow) / 557 legacy

## [1.0.0] — 2026-09-14

Prima release PETRA. La linea di versione riparte da `1.0.0` per scelta:
PETRA non è un successore compatibile di PET, quindi ereditare il numero di
versione PET sarebbe fuorviante. L'ultima release PET resta il tag `v0.3.0`.

### Added
- Architettura PETRA come unica superficie mantenuta (runtime, distribuzione, CLI).
- Address posizionali canonici, record tipizzati result/witness e serializzazione canonica sotto `src/petra/`.
- Operatori canonici: `SPROUT`, `SHED`, `GRAFT`, `PRUNE`.
- CLI canonica minimale `petra <shape> <invocation-json>`.
- Flag `petra --version` che stampa la versione installata del pacchetto.
- SPEC normativa in `docs/reference/SPEC.md`.
- Dipendenze di test dichiarate in `[project.optional-dependencies]` (`pip install -e ".[test]"`).

### Changed
- Versione del progetto portata da `0.1.4` a `1.0.0`.
- `pytest` e `sympy` non vengono più installati ad-hoc: sono dichiarati e pinnati.

### Deprecated
- `src/pet/` e `tools/pet_*` restano nel working tree come residuo di migrazione durante Phase 10. Non fanno parte della superficie PETRA mantenuta e saranno rimossi in una release 1.x successiva.

### Removed
- La compatibilità permanente con PET non è un requisito e non è fornita.


## [Unreleased]

### Added
- `SECURITY.md` con policy di segnalazione e scope del progetto.
- Badge DOI Zenodo nel README e campo `doi:` in `CITATION.cff` (`10.5281/zenodo.22741778`, concept DOI che punta sempre all'ultima versione).
- Prima release pubblica su Zenodo: `PETRA — Prime Exponent Tower Recursive Algebra v1.0.3`, DOI versione `10.5281/zenodo.22741779`.
- Gate di qualità in CI: `ruff check` (E, F, I, UP, B, SIM, RUF) e `mypy` (strict-ish) eseguiti su `src/petra/` e sui test canonical. Configurazione in `pyproject.toml` sotto `[tool.ruff]` e `[tool.mypy]`.
- Tool research PET-METICA: `pet_metica_range_sweep.py` (scan multi-tier) e `pet_metica_seven_family_probe.py` (probe mirato su `7×{2^k,3^k}`), con test e report generated associati.
- Research note `docs/research/notes/pet_metica_seven_family_tier_drift.md` e scorecard di chiusura pass in `docs/research/experiments/pet-metica-seven-family-ladder-pass.md`.
- Passaggio di fondazione first-principles: esempi, semantica `collapse(P)`, audit implementativo, classificazione moduli, audit metriche e boundary per API aliases.
- `scripts/check_docs_consistency.py` per controllare link Markdown locali e riferimenti Python sorgente non più esistenti.
- Target `make docs-check` per eseguire il controllo documentale leggero.
- Pipeline canonica `tools/pet_triage_pipeline.sh` per il workflow PET triage.
- Flusso PET race diagnostic -> classic handoff policy -> classic verification.
- Namespace operativi per i tool: `tools/core/`, `tools/classic/`, `tools/legacy/`, `tools/research/`.
- Wrapper compatibili root-level per preservare i vecchi percorsi `tools/*.py` e `tools/*.sh`.
- `.pet-cache/` come area locale per cache, stati e artefatti generati non tracciati.

### Changed
- Introdotto il marker `legacy` (applicato automaticamente da `tests/conftest.py`) sui test che esercitano il runtime PET storico (`src/pet/`) e i tool PET (`tools/pet_*`). Il gate CI canonical (`-m "not slow and not legacy"`) copre 719 test; il gate legacy (557 test) gira solo su `main` come informativo.
- CI: il job legacy PET è condizionato a `push` su `main`, non blocca le PR e non fallisce il workflow (`continue-on-error: true`).
- `src/petra/results.py`: fallback `StrEnum` basato su `sys.version_info` invece di `try/except ImportError`. Stesso comportamento runtime, ma mypy ora inferisce correttamente `Operator` come enum e non più come `str`.
- `src/petra/serialization.py`: `_malformed` annotato `NoReturn`.
- `src/petra/model.py`: `_is_shape` annotato `TypeGuard[PetraShape]`.
- `src/petra/cli.py`: variabile dell'eccezione rinominata per evitare shadowing.
- Fix ruff minori (import sorting, f-string, iterable unpacking, `zip(strict=False)`, raw string, noqa mirati per cifre unicode intenzionali nei test).
- Documentazione pubblica: chiarita la separazione tra PET-Base, First-principles PET, PET-Metrics, PET/PEG 2.0 e PET-METICA.
- Allineati README, SPEC/STATUS e foundation docs intorno ai confini tra contratto stabile, layer object-native, metriche estese e tooling research.
- Corretto il riferimento storico `src/pet_algebra.py` verso il percorso reale `src/pet/algebra.py`.

### Fixed
- `tests/test_petra_shape_model_stack_safety.py`: alza localmente `sys.setrecursionlimit` così i test di stack-safety a profondità 2048 passano anche su CPython 3.10 e 3.11, dove il consumo di C stack per frame è maggiore rispetto a 3.12.
- `tests/test_report_contracts.py`: corretti i path dei report a `docs/reports/generated/`; il contract test era silenziosamente skippato prima.
- CI: installazione degli extras di test nel job `docs` (`pip install -e ".[test]"`), che mancava e causava exit 127.
- `petra --version` ora stampa la versione installata del pacchetto.

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
