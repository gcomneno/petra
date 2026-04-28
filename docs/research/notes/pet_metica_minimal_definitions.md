# PET-METICA minimal definitions

## Scopo
Questa nota fissa il vocabolario minimo operativo di PET-METICA.
Non introduce ancora una teoria completa di `⊕`.
Serve a stabilizzare i concetti minimi usati nei report empirici e nei futuri strumenti CLI.

---

## 1. Stato PET

Uno **stato PET** è la forma canonica PET associata a un intero `n >= 2`.

Lettura corrente:
- un intero è trattato come nodo di uno spazio strutturale di rewrite
- la sua shape PET canonica è lo stato da cui partono e a cui arrivano le mosse PET

---

## 2. Number-level and shape-level PET-METICA

PET-METICA currently has two related but distinct operational levels.

### Number-level PET-METICA

At the number level, states are represented by concrete integers `n >= 2`.
The CLI commands operate primarily at this level:

    pet rewrite pair A B
    pet rewrite explain A B
    pet rewrite friction
    pet rewrite scan

This level is useful for reproducible bounded experiments, reports, demos, and
operator-facing analysis.

### Shape-level PET-METICA

At the shape level, states are canonical PET shapes with prime labels ignored.
Shape-level tools study abstract rewrite behavior independently from specific
integer labels.

This level is useful for understanding the structural grammar behind PET-METICA,
but it should not be confused with the concrete number-level CLI behavior.

### Current convention

Number-level PET-METICA is the operational CLI surface.

Shape-level PET-METICA is the supporting structural layer used for algebraic and
research analysis.

Both levels are useful, but claims should say explicitly which level they refer
to.

---

## 3. Mossa PET

Una **mossa PET** è una trasformazione locale primitiva tra stati PET canonici.

Le mosse primitive attualmente usate sono:
- `NEW`
- `DROP`
- `INC`
- `DEC`

Lettura corrente:
- `NEW` introduce un nuovo primo nel supporto
- `DROP` rimuove un primo dal supporto
- `INC` aumenta localmente una struttura esponente
- `DEC` la riduce

Una mossa PET va trattata come operazione locale di rewrite strutturale, non come semplice variazione numerica.

---

## 4. Cammino PET

Un **cammino PET** è una sequenza finita di mosse PET che trasforma uno stato in un altro.

Lettura corrente:
- il cammino descrive come si passa da un intero a un altro nello spazio di rewrite
- la nozione centrale non è la differenza numerica classica, ma la trasformazione strutturale

---

## 5. Distanza PET

La **distanza PET** tra due stati è il costo minimo di trasformazione tra essi, misurato nello spazio dei cammini PET ammessi.

Lettura corrente:
- in generale non coincide con `|m-n|`
- può essere asimmetrica
- misura frizione di trasformazione, non differenza aritmetica classica

Stato teorico:
- nozione ben supportata computazionalmente
- non ancora chiusa in una teoria assiomatica completa

---

## 6. Differenza PET (`⊖`)

La faccia attualmente più naturale di una **differenza PET** non è uno scalare.

Lettura corrente:
- `a ⊖ b` come **cammino minimo** da `a` a `b`
- oppure come **trasporto minimo di rewrite** che porta `a` in `b`

Stato teorico:
- la scelta di una forma pienamente canonica del cammino è ancora aperta
- quindi `⊖` non va ancora trattato come operatore completamente stabilizzato

---

## 7. Stato teorico corrente

La formulazione più onesta, allo stato attuale, è:

- PET-METICA non replica l’aritmetica classica in forma esotica
- PET-METICA descrive una geometria di rewrite sugli interi
- gli oggetti primitivi rilevanti sono stati, mosse, cammini, costi e frizioni
- la domanda centrale non è “quanto fa?”, ma “come ci arrivi?”

---

## 8. Cose non ancora fissate

Questa nota non fissa ancora:
- eventuali operatori compositivi oltre il trasporto di rewrite
- una caratterizzazione teorica definitiva dei cammini minimi
- una teoria assiomatica completa della distanza PET
- lo status della single free tower policy

Questi restano fronti aperti.
