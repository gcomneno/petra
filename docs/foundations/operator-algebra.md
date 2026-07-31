# PET Operator Algebra v0

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


> **Legacy/research operator algebra.** The `NEW`, `DROP`, `INC`, and `DEC`
> rules below describe the retained prime-label/value-level model, not canonical
> PET semantics. The sole normative future contract is
> [`../reference/SPEC.md`](../reference/SPEC.md).

# Introduzione

Questo documento formalizza gli operatori fondamentali del framework PET/PEG e la loro classificazione assiale.

---

# 1. Assi Ontologici

| Asse | Significato |
|---|---|
| X | support topology |
| Y | recursive refinement |
| Z | connectivity dynamics |

---

# 2. Operatori X — Support Topology

Gli operatori X modificano il support-set baseline.

## NEW(q)

Aggiunge una nuova primal root `q` alla baseline corrente.

Effetto:

    Support(P) → Support(P) ∪ {q}

Classe:

    support-expanding operator

---

## DROP(q)

Rimuove la primal root `q` dalla baseline corrente.

Effetto:

    Support(P) → Support(P) \ {q}

Classe:

    support-contracting operator

---

# 3. Operatori Y — Recursive Refinement

Gli operatori Y modificano la struttura ricorsiva senza alterare il support-set baseline.

## INC(p)

Modifica ricorsivamente l'exponent-object associato a `p`.

Vincolo:

    Support(P) invariato

Classe:

    support-preserving refinement operator

---

## DEC(p)

Riduce o semplifica l'exponent-object associato a `p`.

Vincolo:

    Support(P) invariato

Classe:

    support-preserving reduction operator

---

# 4. Operatori Z — Connectivity Dynamics

Gli operatori Z modificano la navigazione tra stati PET.

## REDIRECT

Introduce una route alternativa.

Classe:

    connectivity-transforming operator

---

## SHADOW_SELECT

Privilegia una route alternativa che preserva maggiore continuità strutturale.

Classe:

    shadow-connectivity operator

---

# 5. Separazione Ontologica

## Assi X

Gli operatori X modificano il support-set.

## Assi Y

Gli operatori Y preservano il support-set.

## Assi Z

Gli operatori Z modificano le relazioni dinamiche tra stati.

---

# 6. Conseguenze Preliminari

## Non-riducibilità

Nessuna composizione finita di operatori Y può simulare un operatore X.

---

## Possibile non-commutatività

Domanda aperta:

    NEW ∘ INC
    =
    INC ∘ NEW ?

---

# 7. Research Questions

- Esistono operatori puramente mono-assiali?
- Esistono operatori intrinsecamente multi-assiali?
- Esistono invarianti Z?
- La composizione operatoriale è commutativa?
