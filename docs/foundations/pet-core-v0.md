# PET Core v0 — Ontologia Strutturale e Dinamica

## Introduzione

PET (Prime Exponent Tree) esplora rappresentazioni strutturali ricorsive degli interi, preservando informazioni non esplicitamente visibili nella sola proiezione numerica finale.

L'obiettivo non è sostituire la matematica classica, ma introdurre una lente strutturale alternativa capace di mantenere visibili:

- support topology
- recursive refinement
- connectivity dynamics
- path-history

prima del collasso implicito nella valutazione numerica finale.

---

# 1. Oggetto PET

## Definizione minimale

Un oggetto PET è una baseline finita di primal roots.

Ogni primal root è una coppia:

    p^E

dove:

- `p` è una primal root della baseline
- `E` è un oggetto PET

L'oggetto PET minimale è:

    1

detto leaf PET object.

Ogni exponent-object è quindi ricorsivamente un oggetto PET.

---

# 2. Baseline PET

La baseline di un oggetto PET è l'insieme finito delle primal roots presenti al livello corrente della struttura.

---

# 3. Support-set

Il support-set di un oggetto PET è l'insieme delle primal roots della sua baseline corrente.

Esempio:

    {2^1, 3^1, 5^1}

ha support-set:

    {2,3,5}

---

# 4. Assi Ontologici Fondamentali

| Asse | Significato |
|---|---|
| X | support topology |
| Y | recursive refinement |
| Z | connectivity dynamics |

---

# 5. Operatori Fondamentali

## Operatori X — Support Topology

Gli operatori X modificano il support-set baseline.

### NEW(q)

NEW(q) aggiunge una nuova primal root `q` alla baseline corrente dell'oggetto PET.

Effetto:

    Support(P) → Support(P) ∪ {q}

Interpretazione:

    support-expanding operator

---

### DROP(q)

DROP(q) rimuove la primal root `q` dalla baseline corrente dell'oggetto PET.

Effetto:

    Support(P) → Support(P) \ {q}

Interpretazione:

    support-contracting operator

---

## Operatori Y — Recursive Refinement

Gli operatori Y modificano la struttura ricorsiva degli exponent-objects senza alterare il support-set baseline.

### INC(p)

INC(p) modifica ricorsivamente l'exponent-object associato alla primal root `p`.

Vincolo fondamentale:

    INC(p) preserva il support-set baseline.

Interpretazione:

    support-preserving refinement operator

---

### DEC(p)

DEC(p) riduce o semplifica la struttura ricorsiva dell'exponent-object associato a `p`.

Vincolo fondamentale:

    DEC(p) preserva il support-set baseline.

Interpretazione:

    support-preserving reduction operator

---

## Operatori Z — Connectivity Dynamics

Gli operatori Z modificano la navigazione dinamica tra stati PET senza modificare direttamente support-set o recursive refinement.

### REDIRECT

REDIRECT introduce una route alternativa tra stati PET.

Interpretazione:

    connectivity-transforming operator

---

### SHADOW_SELECT

SHADOW_SELECT privilegia una route alternativa che preserva maggiore continuità strutturale.

Interpretazione:

    shadow-connectivity operator

---

# 6. Prima Separazione Ontologica

Gli operatori X modificano il support-set.

Gli operatori Y preservano il support-set.

Conseguenza preliminare:

    Nessuna composizione finita
    di operatori Y
    può simulare un operatore X.

---

# 7. PEG Dynamics

## Stato PET

Uno stato PET è una configurazione strutturale identificata da:

- support topology
- recursive refinement
- operator context

---

## Route PET

Una route PET è una sequenza di trasformazioni operatoriali tra stati PET.

---

## Connectivity

Due stati PET sono connessi se esiste almeno una route PET che li collega.

---

## Local Neighborhood

Il neighborhood di uno stato PET è l'insieme degli stati raggiungibili tramite una singola trasformazione operatoriale.

---

## Continuità

Una route PET è continua se preserva proprietà strutturali considerate attive o navigabili.

---

## Recoverability

Uno stato PET è recoverable se esiste almeno una route verso una regione strutturalmente attiva.

---

## Collapse

Uno stato PET è collapsed quando nessuna route nota preserva continuità strutturale attiva.

---

# 8. Path-History

## Definizione preliminare

La path-history di un oggetto PET è la traiettoria operatoriale che conduce allo stato corrente.

La path-history rappresenta memoria trasformazionale strutturale.

---

# 9. Livelli di Equivalenza

## Numeric Equality

Due oggetti PET sono numericamente equivalenti se producono la stessa proiezione intera.

---

## Structural Equality

Due oggetti PET sono strutturalmente equivalenti se condividono:

- stesso support-set
- stessa recursive structure

---

## Historical Equality

Due oggetti PET sono storicamente equivalenti se condividono la stessa path-history operatoriale.

---

# 10. Projection Layer

La proiezione numerica classica può essere vista come una forgetful projection che preserva il valore finale ma non necessariamente:

- struttura
- dinamica
- storia trasformazionale

---

# 11. Prime Research Questions

## Q-A1

Gli assi X/Y/Z sono realmente indipendenti?

---

## Q-B1

INC/DEC preservano sempre il support-set baseline?

---

## Q-C1

NEW è simulabile tramite composizioni finite di INC?

---

## Q-D1

La composizione operatoriale è commutativa?

---

## Q-E1

Le classi PEG (healthy / recoverable / collapsed) corrispondono a regioni XYZ?

---

## Q-PH1

La path-history è parte integrante dell'identità PET?

---

# 12. Stato del Framework

Questo documento rappresenta una formalizzazione preliminare del core ontologico PET/PEG.

Le definizioni e le proposizioni qui presentate sono da considerarsi esplorative e incrementali.
