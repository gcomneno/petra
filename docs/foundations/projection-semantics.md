# PET Projection Semantics v0

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


# Introduzione

Questo documento esplora la relazione tra oggetti PET e proiezione numerica classica.

---

# 1. Proiezione Numerica

La proiezione numerica di un oggetto PET è il valore intero ottenuto dalla sua valutazione classica.

Esempio:

    {2^1,3^1,5^1}
    →
    30

---

# 2. Forgetful Projection

La proiezione numerica classica può essere vista come una forgetful projection.

Essa preserva:

- il valore finale

ma non necessariamente:

- support topology
- recursive refinement
- connectivity dynamics
- path-history

---

# 3. Livelli di Equivalenza

## Numeric Equality

Due oggetti PET sono numericamente equivalenti se producono lo stesso intero.

Analogia:

    ==

---

## Structural Equality

Due oggetti PET sono strutturalmente equivalenti se condividono:

- stesso support-set
- stessa recursive structure

---

## Historical Equality

Due oggetti PET sono storicamente equivalenti se condividono la stessa path-history operatoriale.

Analogia:

    ===

---

# 4. Structural Information

La rappresentazione PET mantiene informazioni strutturali non esplicitamente visibili nella sola proiezione numerica finale.

---

# 5. Conseguenze Concettuali

Possibili implicazioni:

- esistenza di classi strutturali equivalenti
- perdita informativa nella valutazione numerica
- dipendenza dalla path-history
- separazione tra valore e struttura

---

# 6. Research Questions

- Oggetti PET distinti possono condividere la stessa proiezione?
- Esistono classi canoniche di equivalenza strutturale?
- La history contribuisce all'identità PET?
- Quanta informazione viene persa nella proiezione numerica?
