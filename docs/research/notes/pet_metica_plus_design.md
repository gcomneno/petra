# PET-METICA `⊕` design note

## Scopo
Questa nota non definisce ancora `⊕` in modo definitivo.
Serve a fissare il problema di progetto in forma stretta, prima di promuovere una definizione operativa o teorica.

---

## 1. Problema

In PET-METICA, `⊖` ha già una faccia naturale:

- differenza come cammino minimo
- oppure come trasporto minimo di rewrite tra stati PET

Per `⊕`, invece, non esiste ancora una faccia altrettanto naturale.

Il problema è questo:

- in una geometria di rewrite direzionale, cosa dovrebbe significare “sommare” due oggetti?
- stiamo sommando stati?
- stiamo sommando trasporti?
- stiamo componendo cammini?
- stiamo costruendo un nuovo target?

Questa ambiguità va chiarita prima di fissare una notazione stabile.

---

## 2. Vincolo di contesto

PET-METICA non nasce come copia esotica di `+` e `-` classici.

La lettura corrente più onesta è:

- gli oggetti primitivi sono stati PET
- le trasformazioni primitive sono rewrite locali
- la distanza misura frizione di trasformazione
- `⊖` ha la faccia di un trasporto, non di uno scalare

Quindi `⊕` non va progettato partendo dall'idea
“troviamo una somma che assomigli a quella classica”.

Va progettato partendo dall'idea
“quale operazione è naturale dentro una geometria di rewrite direzionale?”.

---

## 3. Candidati di alto livello

### Candidato A — composizione di trasporti

Idea:
- se `⊖` è un trasporto/cammino, allora `⊕` potrebbe essere una composizione di trasporti compatibili

Schema:
- se `a ⊖ b` e `b ⊖ c` sono cammini compatibili,
  allora una forma di `⊕` potrebbe essere la loro concatenazione o composizione normalizzata

Vantaggi:
- è molto naturale se gli oggetti principali sono i cammini
- rispetta l'idea dinamica di PET-METICA

Problemi:
- questo `⊕` non è una somma di stati, ma di trasporti
- richiede una nozione di compatibilità/composizione
- rischia di vivere più vicino a una categoria/path algebra che a un'“aritmetica” sugli interi

Stato:
- candidato serio
- ma probabilmente è una composizione, non una somma sui numeri

### Candidato B — operazione su stati via punto base

Idea:
- scegliere uno stato base `g` e interpretare ogni stato tramite il trasporto da `g`
- poi definire `a ⊕ b` come combinazione dei due trasporti uscenti da `g`

Schema informale:
- `a ~ path(g, a)`
- `b ~ path(g, b)`
- `a ⊕ b` ottenuto combinando questi due trasporti e richiudendo su uno stato risultante

Vantaggi:
- restituisce un'operazione sui numeri/stati
- mantiene un legame con la lettura di `⊖`

Problemi:
- dipende dalla scelta del punto base
- il punto base potrebbe introdurre arbitrarietà strutturale
- non è chiaro se esista una combinazione naturale dei due trasporti

Stato:
- candidato interessante
- ma fortemente sospetto di dipendenza artificiale dal riferimento

### Candidato C — concatenazione normalizzata di rewrite

Idea:
- prendere due cammini di rewrite e concatenarli, poi normalizzare/collassare il risultato in un cammino o in uno stato canonico

Vantaggi:
- operazione direttamente costruttiva
- leggibile in termini computazionali

Problemi:
- la normalizzazione è il cuore del problema
- senza una nozione robusta di equivalenza tra cammini, la definizione rischia di essere arbitraria
- può dipendere troppo dall'ordine delle mosse

Stato:
- utile come candidato operativo sperimentale
- ancora troppo grezzo per essere promosso

### Candidato D — “somma” come costruzione di target comune

Idea:
- dati due stati `a` e `b`, definire `a ⊕ b` come uno stato bersaglio che assorbe o combina parte delle loro strutture di rewrite

Interpretazione:
- più che sommare trasporti, si cerca un target naturale comune

Vantaggi:
- tiene `⊕` come operazione su stati
- potrebbe essere vicino a nozioni di join, fusione o least common target

Problemi:
- non è affatto chiaro che il target naturale esista o sia unico
- rischia di produrre un'operazione troppo dipendente da euristiche
- può slittare verso una nozione di merge, non di somma

Stato:
- candidato utile da esplorare
- ma molto aperto

---

## 4. Proprietà desiderabili

Una futura definizione di `⊕` dovrebbe soddisfare, almeno idealmente, alcune proprietà.

### 4.1. Naturalità di rewrite
`⊕` deve nascere da mosse, cammini e stati PET.
Non deve essere una decorazione artificiale appoggiata dall'esterno.

### 4.2. Compatibilità concettuale con `⊖`
Se `⊖` è trasporto/differenza dinamica, `⊕` dovrebbe avere un significato coerente rispetto a questa lettura.
Non è necessario che sia l'inverso classico, ma non deve essere semanticamente scollegato.

### 4.3. Restituzione di un oggetto ben leggibile
Bisogna decidere cosa restituisce `⊕`:
- uno stato?
- un trasporto?
- una classe di cammini?
- un oggetto misto?

Questa scelta va resa esplicita.

### 4.4. Sensatezza computazionale
La definizione deve essere almeno sperimentabile.
Se `⊕` non produce niente di computabile o osservabile, rischia di restare puro fumo simbolico.

### 4.5. Non banalizzazione a `+` classico
Se `⊕` collassa banalmente sulla somma usuale, allora PET-METICA non sta aggiungendo niente di strutturale.

### 4.6. Controllo della dipendenza da convenzioni arbitrarie
Se la definizione dipende troppo da:
- punto base
- tie-break
- normalizzazioni ad hoc
- ordine artificiale delle mosse

allora va trattata con estrema cautela.

---

## 5. Cose da non promettere ora

Allo stato attuale non bisogna promettere:

- associatività forte
- commutatività
- esistenza di identità naturale
- inversi
- struttura di gruppo
- struttura di anello
- compatibilità forte con l'aritmetica classica
- forma canonica definitiva

Queste sarebbero, oggi, promesse premature.

---

## 6. Lettura attuale più onesta

La lettura più onesta oggi è:

- `⊖` ha già una faccia naturale come trasporto minimo di rewrite
- `⊕` non è ancora definito
- il candidato più naturale, ad oggi, sembra più vicino a una composizione/aggregazione di trasporti che a una somma classica di stati

Questa però è ancora una direzione di lavoro, non una definizione chiusa.

---

## 7. Strategia operativa consigliata

Ordine di lavoro consigliato:

1. non fissare ancora `⊕` come operatore definitivo
2. distinguere chiaramente:
   - `⊕` su stati
   - `⊕` su trasporti/cammini
3. testare candidati piccoli su esempi manifesto
4. scartare presto i candidati che dipendono troppo da scelte arbitrarie
5. promuovere solo una definizione che resti leggibile in termini di rewrite

---

## 8. Prossimo passo concreto

Il prossimo passo utile non è una teoria completa.
È una piccola batteria di esempi dove testare candidati di `⊕` su casi semplici, ad esempio:

- `2, 4, 8`
- `3, 9`
- `6, 30`
- `4, 12`
- `8, 24`

L'obiettivo è capire se qualche candidato produce una nozione stabile, leggibile e non artificiale.
