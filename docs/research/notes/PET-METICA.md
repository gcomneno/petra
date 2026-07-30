# PET-aritmetica

> Note: this document contains historical and exploratory PET-METICA material.
> Its `NEW`, `DROP`, `INC`, and `DEC` material describes current executable
> legacy PET-METICA behavior and research evidence, not canonical or future
> PET semantics. The sole normative future operator contract is
> [`../../foundations/pet-peg-2.0-object-native-operators.md`](../../foundations/pet-peg-2.0-object-native-operators.md).
> The companion operational notes, CLI reference, and bounded reports are
> compatibility references for that legacy behavior; compositional/operator
> material is non-core unless explicitly promoted later.

## Storia completa dell'idea, della formalizzazione e dei primi risultati empirici

## 0. Scopo del documento

Questo file raccoglie in un unico posto tutta la traiettoria sviluppata fin qui sulla **PET-aritmetica**.

L'idea di partenza era semplice ma forte: la forma interessante non sembra essere una pseudo-sottrazione numerica del tipo

```text
PET(12) - PET(3)
```

come se PET dovesse imitare direttamente l'aritmetica classica.

La pista che si è rivelata più promettente è invece un'altra:

- una **PET-shape** come stato
- i **rewrite locali** come operazioni primitive
- la “somma/sottrazione” reinterpretata come **trasformazione canonica tra shape**
- la distanza come **costo minimo di trasformazione**
- l'oggetto interessante non è tanto il risultato numerico, ma il **cammino minimo canonico**

Da qui è nata l'idea di una **aritmetica di rewrite**, o meglio di una **geometria di trasporto e riscrittura sugli interi tramite PET**.

---

# 1. Idea iniziale

L'intuizione fondante è stata questa:

> `12 - 3 = 9` come identità numerica è una cosa.  
> Trasformare `Shape(12)` verso `Shape(9)` è un'altra.  
> La seconda potrebbe essere la vera PET-aritmetica interessante.

Questa intuizione porta a cambiare completamente punto di vista.

Non più:

- numeri come oggetti primitivi
- operazioni aritmetiche classiche da “simulare”

ma:

- shape PET come stati primitivi
- rewrite locali come algebra interna
- cammini di rewrite come vere operazioni

In questa prospettiva, PET non serve a “ricopiare” `+`, `-`, `*`, ma a introdurre una **geometria interna** sugli interi.

---

# 2. Cambio di paradigma

La formulazione concettuale che è emersa è questa:

## Non:
PET rappresenta l'aritmetica classica.

## Piuttosto:
PET induce una **geometria di trasformazione** sopra gli interi.

Questa geometria ha almeno quattro ingredienti:

1. **stati**: shape canoniche
2. **rewrite locali**: `NEW`, `DROP`, `INC`, `DEC`, ...
3. **cammini**: sequenze finite di rewrite
4. **costo**: misura del prezzo minimo per andare da una shape all'altra

In questo quadro, la “differenza” fra due numeri non è un numero, ma un **cammino minimo canonico**.

---

# 3. Mini-assiomatica concettuale (versione 0.1)

La prima mini-assiomatica formulata è stata questa.

## 3.1 Stati
Sia `S` l'insieme delle shape PET canoniche.

A ogni shape `σ ∈ S` associamo un numero tramite una mappa:

```text
N : S -> N_{>=1}
```

e, idealmente, una mappa inversa:

```text
Σ(n) = shape canonica di n
```

## 3.2 Rewrite locali
Esiste un insieme `R` di rewrite locali validi.

Esempi naturali:

- `NEW`
- `DROP`
- `INC`
- `DEC`

Ogni rewrite trasforma una shape in un'altra quando applicabile.

## 3.3 Grafo PET
Da shape e rewrite si costruisce un grafo orientato:

- nodi = shape
- archi = rewrite locali ammessi

## 3.4 Costo
All'inizio si è scelto il caso più semplice:

- ogni mossa ha costo `1`

## 3.5 Distanza PET
La distanza PET tra due shape è il costo minimo di un cammino che le collega.

Sui numeri:

```text
d_PET(m, n) := d_PET(Σ(m), Σ(n))
```

## 3.6 Differenza PET
La “sottrazione” PET interessante non restituisce un intero, ma:

- l'insieme dei cammini minimi
- oppure un cammino minimo canonico

Questa è stata la prima idea forte: **la vera differenza PET è un trasporto strutturale, non un numero.**

---

# 4. Traduzione computabile (versione 0.2)

Per non restare nella filosofia, si è passati subito a una versione computabile.

Sono state fissate tre definizioni operative.

## 4.1 Vicinato di rewrite
Per ogni numero `n`, si definisce il vicinato PET a un passo:

```text
Γ_PET(n) = insieme delle mosse locali valide da n
```

Ogni vicino è rappresentato da:

- target numerico
- etichetta della mossa
- costo

## 4.2 Distanza di rewrite
Si definisce la distanza diretta come shortest path nel grafo dei rewrite.

Con costi unitari, basta BFS.

## 4.3 Differenza PET canonica
La differenza PET canonica tra `m` e `n` è il **cammino minimo canonico**:

- costo minimo
- lista delle mosse
- tie-break deterministico tra cammini minimi

---

# 5. Il tool costruito nel repo

Per testare l'idea è stato costruito un tool dedicato nel repo:

```text
pet rewrite
```

Il tool è nato con tre comandi principali:

## 5.1 `pair`
Per analizzare una coppia:

```bash
pet rewrite pair 12 9
```

Restituisce:

- raggiungibilità
- costo minimo
- path canonico

## 5.2 `scan`
Per scansione globale su `1..N` con un overscan più ampio:

```bash
pet rewrite scan --n-max 20 --overscan 60
```

Restituisce:

- statistiche globali del grafo
- hub
- anomalie rispetto a `|m-n|`
- asimmetrie
- metriche di ritorno per le mosse a un passo
- report per famiglie

## 5.3 `matrix`
Per esportare la matrice delle distanze.

---

# 6. Cablaggio tecnico nel repo PET

Il punto di aggancio reale è stato trovato qui:

```text
src/pet/cli.py
```

Funzione concreta usata:

```python
_pathwise_edges_for_number(n)
```

L'output osservato, per esempio su `12`, è stato:

```python
[
    {'label': 'NEW(x5)', 'target_generator': None, 'target_n': 60},
    {'label': 'DROP(p=3)', 'target_generator': None, 'target_n': 4},
    {'label': 'INC(p=3,e=1)', 'target_generator': None, 'target_n': 36},
    {'label': 'INC(p=2,e=2)', 'target_generator': None, 'target_n': 24},
    {'label': 'DEC(p=2,e=2)', 'target_generator': None, 'target_n': 6},
]
```

Da lì il tool è stato collegato al repo reale.

Sono emersi anche due aggiustamenti pratici:

- il target era in `target_n`
- `1` andava trattato come nodo senza vicini, perché il core accetta solo `n >= 2`

---

# 7. Primo test-manifesto: `12 -> 9`

Il primo caso davvero parlante è stato:

```bash
pet rewrite pair 12 9 --overscan 120
```

Output osservato:

```text
src = 12
dst = 9
reachable = True
cost = 3
path:
  12 --DEC(p=2,e=2)--> 6
  6 --DROP(p=2)--> 3
  3 --INC(p=3,e=1)--> 9
```

Questo caso ha confermato l'idea iniziale:

- non “`12 - 3 = 9`”
- ma **trasporto di rewrite** da `12` a `9`

Il risultato importante è stato:

> la differenza PET interessante è il **cammino**, non il numero finale.

---

# 8. Prima scansione globale: `n_max=20`, `overscan=60`

La prima scansione globale ha mostrato immediatamente che la distanza PET non collassa sulla distanza numerica.

## 8.1 Esempi di non banalità

### Numericamente vicini ma PET-lontani
- `7 -> 5`: PET `8`, numerica `2`
- `11 -> 10`: PET `7`, numerica `1`

### Numericamente lontani ma PET-vicini
- `20 -> 4`: PET `1`, numerica `16`

Questo è stato il primo risultato forte:

> **distanza PET ≠ distanza numerica**

---

# 9. Emergenza degli hub

Già nei primi scan sono emersi hub veri.

## Top hub iniziali osservati
- `4`
- `6`
- `12`
- `2`
- `20`

Con l'ampliamento del range sono poi emersi anche:
- `30`
- `8`
- `9`
- `35`
- `14`

L'interpretazione iniziale è stata:

- alcuni nodi fungono da **snodi naturali**
- i shortest path passano spesso da lì
- non siamo davanti a un grafo casuale

---

# 10. Analisi di cammini anomali

Per capire la geometria interna, sono stati letti alcuni path particolarmente istruttivi.

## 10.1 `20 -> 4`
```text
20 --DROP(p=5)--> 4
```

Interpretazione:
- PET vede `20` e `4` come molto vicini
- togliere il fattore `5` è una mossa locale semplice

## 10.2 `7 -> 5`
```text
7 --NEW(x2)--> 14
14 --INC(p=2,e=1)--> 28
28 --DROP(p=7)--> 4
4 --DEC(p=2,e=2)--> 2
2 --NEW(x3)--> 6
6 --NEW(x5)--> 30
30 --DROP(p=2)--> 15
15 --DROP(p=3)--> 5
```

Interpretazione:
- i primi isolati sono periferici
- per passare da uno all'altro PET usa corridoi composti e nodi altamente manovrabili

## 10.3 `11 -> 10`
```text
11 --NEW(x2)--> 22
22 --INC(p=2,e=1)--> 44
44 --DROP(p=11)--> 4
4 --NEW(x3)--> 12
12 --NEW(x5)--> 60
60 --DROP(p=3)--> 20
20 --DEC(p=2,e=2)--> 10
```

Interpretazione:
- ancora una volta il sistema entra in una zona composta ricca e poi ridiscende

---

# 11. Prima legge locale: compressione preferenziale

Dai primi esempi è emersa una legge locale grezza:

> Le trasformazioni semplificanti (`DROP`, certi `DEC`) sono spesso economiche e locali, mentre il ritorno non coincide necessariamente con un contro-rewrite elementare, ma richiede una ricostruzione mediata.

Questa prima versione era giusta nella direzione, ma troppo rozza.

In seguito è stata raffinata.

---

# 12. Report di asimmetria

È stato poi aggiunto un report dedicato all'asimmetria:

```text
d(a,b) - d(b,a)
```

Scopo:
- capire se PET fosse simmetrica o direzionale

### Primo risultato
L'asimmetria c'era, ma inizialmente sembrava moderata.

Casi tipici:
- `4 <-> 20`
- `5 <-> 15`
- `6 <-> 18`

Esempio:

```text
4 -> 20 = 3
20 -> 4 = 1
```

Interpretazione:
- scendere verso una forma più semplice costa meno che risalire

---

# 13. Analisi dei ritorni a un passo

Per non fermarsi all'intuizione, è stato aggiunto un report automatico sui **costi di ritorno** per ogni arco diretto di costo `1`.

Questo report è diventato uno dei pezzi più preziosi di tutto il lavoro.

## Osservazione chiave
Non tutte le mosse hanno lo stesso costo di ritorno.

### Quasi perfettamente reversibili
Le mosse legate al `2` risultano quasi sempre invertibili in `1`.

### Più costose da invertire
Le mosse che coinvolgono:
- `3`
- `5`
- e poi `7`

diventano progressivamente più attritive e costose in senso inverso.

---

# 14. Gerarchia di frizione per primo

Questa è probabilmente la legge empirica più forte emersa finora.

## Risultato osservato
Con range crescenti, il costo medio di ritorno per primo coinvolto si dispone così:

- `p=2`: `1.0`
- `p=3`: circa `1.8-2.0`
- `p=5`: circa `2.5-3.0`
- `p=7`: circa `5.8`

Questa gerarchia si è stabilizzata e rafforzata con l'estensione del range.

## Formula empirica
> La reversibilità locale dei rewrite PET mostra una gerarchia crescente di frizione per primo coinvolto: `2 < 3 < 5 < 7`.

Questa legge è supportata sia dai dati medi sia dai casi peggiori.

---

# 15. Casi-manifesto di frizione forte

I casi più duri osservati finora sono:

- `56 --DROP(p=7)--> 8` con ritorno `11`
- `28 --DROP(p=7)--> 4` con ritorno `9`
- `63 --DROP(p=7)--> 9` con ritorno `7`
- `6 --NEW(x5)--> 30` con ritorno `5`

Questi casi mostrano che:

- togliere `7` può essere locale ed economico
- ma ricostruire quella struttura è molto costoso

Il `7` è emerso come primo **particolarmente duro** in senso PET.

---

# 16. Caso speciale: `30`

A un certo punto si è ipotizzato che `30` fosse un attrattore globale.

### Casi osservati
- `6 -> 30 = 1`, ma `30 -> 6 = 5`
- `10 -> 30 = 1`, ma `30 -> 10 = 3`

Questo ha suggerito inizialmente che `30` fosse facile da raggiungere e difficile da lasciare.

## Correzione successiva
Con metriche più ampie si è visto che `30` **non** è un attrattore globale semplice.

La lettura più corretta è:

> `30` è un **hub composto con asimmetrie selettive forti**, non una calamita universale.

Questa è stata una correzione importante e sana.

---

# 17. Il problema della metrica “top_attractors”

È stata introdotta una metrica di attrazione globale:

```text
score(v) = avg_out(v) - avg_in(v)
```

dove:

- `avg_in(v)` = costo medio per arrivare a `v`
- `avg_out(v)` = costo medio per partire da `v`

### Problema emerso
Senza filtri, questa metrica premiava nodi con:
- pochissimi ingressi
- tantissime uscite costose

come `11`, `13`, ecc.

Quindi la metrica iniziale mescolava:
- veri attrattori
- nodi periferici “sticky”

## Correzione
È stato applicato un filtro minimo su:
- `incoming_count >= 5`
- `outgoing_count >= 5`

Con questo filtro, la lettura è diventata più sensata, anche se il report è rimasto meno affidabile del `family_report` ai range più grandi.

---

# 18. Prime famiglie moltiplicative

Per capire se certi effetti fossero specifici o generali, è stato aggiunto un `family_report` per famiglie di potenze pure:

- `2^k`
- `3^k`
- `5^k`
- poi anche `7^k`

Questo è diventato il secondo grande pilastro dell'analisi, insieme ai costi di ritorno per primo.

---

# 19. La storia della “torre del 2”

## Fase iniziale
Su range piccoli sembrava che:

- `4`
- `8`
- `16`

fossero attrattori deboli positivi

e che l'effetto forse decadessse verso `0`.

## Fase successiva
Con `n_max=40`, `overscan=160` il trend era:

- `2`: negativo o poco speciale a seconda del range
- `4`: positivo
- `8`: positivo
- `16`: positivo
- `32`: ancora positivo ma piccolo

Sembrava ancora possibile un decadimento verso zero.

## Fase estesa
Con `n_max=80`, `overscan=320`, il quadro è cambiato nettamente:

```text
2   -> score 0.654
4   -> score 1.720
8   -> score 1.543
16  -> score 1.421
32  -> score 1.380
64  -> score 1.367
```

### Conclusione
La vecchia idea “torre del 2 che tende a zero” non regge.

La lettura aggiornata è:

> Le potenze di `2` formano una famiglia **globalmente attrattiva stabile**, con un picco forte a `4` e poi un plateau positivo alto.

Questa è una scoperta importante.

---

# 20. Famiglia di `3`

Con l'ampliamento del range, anche la famiglia `3^k` ha cambiato faccia.

## Risultati osservati
- `3`: quasi neutro
- `9`: positivo
- `27`: positivo

### Lettura aggiornata
> Le potenze di `3` formano una famiglia **debolmente attrattiva o quasi neutra**, molto meno forte della torre del `2`.

---

# 21. Famiglia di `5`

Per `5` il quadro è rimasto stabile.

## Risultati osservati
- `5`: negativo
- `25`: negativo

### Lettura
> Le potenze di `5` risultano globalmente repulsive.

---

# 22. Famiglia di `7`

Questa è la scoperta più netta dell'ultima fase.

## Risultati osservati
- `7`: score molto negativo
- `49`: score molto negativo

### Lettura
> Le potenze di `7` risultano **globalmente fortemente repulsive**.

Questa osservazione si incastra perfettamente con:
- l'elevata frizione locale del `7`
- i peggiori costi di ritorno osservati

---

# 23. Quadro comparativo finale delle famiglie

## `2^k`
Famiglia attrattiva forte e stabile.

## `3^k`
Famiglia debolmente attrattiva / quasi neutra.

## `5^k`
Famiglia repulsiva.

## `7^k`
Famiglia fortemente repulsiva.

Questa tassonomia è una delle conclusioni empiriche più pulite emerse finora.

---

# 24. Due livelli strutturali distinti

A questo punto l'analisi mostra chiaramente due livelli diversi.

## 24.1 Livello locale
Misurato con:
- costo di ritorno per mossa a un passo
- aggregazione per primo

Qui emerge la legge di frizione crescente:

```text
2 < 3 < 5 < 7
```

## 24.2 Livello globale
Misurato con:
- `family_report`
- hub
- attrazione/repulsione delle famiglie

Qui emerge la tassonomia:

- `2^k` favorite
- `3^k` debolmente favorite
- `5^k` sfavorite
- `7^k` molto sfavorite

Questa distinzione è importante perché evita di confondere:
- proprietà delle singole mosse
- proprietà della geografia globale del grafo

---

# 25. Stato teorico attuale

La formulazione più onesta raggiunta finora è questa:

> PET non induce una semplice versione esotica dell'aritmetica classica, ma una **geometria di rewrite e trasporto** sugli interi, con:
> - hub strutturali
> - famiglie favorite e sfavorite
> - cammini minimi canonici
> - asimmetrie reali
> - frizione crescente legata ai primi

La “PET-aritmetica” interessante, in questo quadro, non è:

- un nuovo modo di fare `+` e `-`

ma:

- lo studio di **come una shape diventa un'altra**
- quanto costa
- quali vie canoniche usa
- quali nodi fungono da officine, corridoi, attrattori o zone repulsive

---

# 26. Risultati empirici consolidati

Questi sono i risultati che, allo stato attuale, sembrano più solidi.

## 26.1 Distanza PET non numerica
Confermato.

## 26.2 Hub reali
Confermato. Esempi forti:
- `4`
- `6`
- `12`
- `30`

## 26.3 Frizione locale crescente per primo
Confermato:
- `2`
- `3`
- `5`
- `7`

## 26.4 Famiglie moltiplicative distinte
Confermato:
- `2^k` attrattive
- `3^k` debolmente attrattive
- `5^k` repulsive
- `7^k` fortemente repulsive

## 26.5 Asimmetria reale
Confermato. Alcune coppie hanno differenze molto forti fra andata e ritorno.

---

# 27. Cose da non dire troppo in fretta

Per onestà, ci sono anche limiti e cautele.

## 27.1 Il nodo `1`
È stato trattato come nodo senza vicini per motivi tecnici.
Quindi non va interpretato matematicamente in profondità.

## 27.2 La metrica `top_attractors`
Non è ancora affidabile come strumento generale a range grandi.
Oggi i report più affidabili sono:
- `family_report`
- `one_step_return_costs.by_prime`
- `hardest_returns`

## 27.3 Nessun teorema ancora
Tutto ciò che è stato ottenuto è **empirico/computazionale**.
Le formulazioni tipo “legge empirica” vanno lette come:
- ipotesi forti supportate dai dati
- non ancora risultati dimostrati

---

# 28. Sintesi finale

La traiettoria completa è stata questa:

1. idea iniziale: la vera PET-aritmetica non è aritmetica classica travestita
2. formalizzazione: shape + rewrite + costo + cammini
3. prototipo computabile nel repo
4. primi test su coppie concrete
5. scoperta che la distanza PET non coincide con `|m-n|`
6. emersione di hub strutturali
7. analisi di asimmetrie
8. scoperta della frizione locale crescente per primo
9. analisi delle famiglie di potenze pure
10. tassonomia globale finale: `2^k`, `3^k`, `5^k`, `7^k`

La conclusione più forte, oggi, è questa:

> PET-aritmetica sembra essere, in primo luogo, una **geometria di rewrite** sugli interi.  
> Il suo contenuto non sta nel rifare l'aritmetica classica, ma nel descrivere:
> - vie minime di trasformazione
> - asimmetrie strutturali
> - hub
> - famiglie favorite
> - attriti locali legati ai primi

---

# 29. Formula finale compatta

Se si vuole condensare tutto in una riga:

> **La PET-aritmetica interessante non restituisce “quanto fa”, ma “come ci arrivi”.**

E quello che conta, in questa geometria, è:

- il cammino
- il costo
- la canonicità
- la frizione
- la struttura del grafo

---

# 30. Appendice: stato operativo del tool

Il file di lavoro costruito per questi esperimenti è:

```text
pet rewrite
```

Comandi usati ricorrentemente:

```bash
pet rewrite pair A B
pet rewrite scan --n-max N --overscan M
pet rewrite matrix --n-max N --overscan M --json
```

Le analisi più utili emerse finora sono state:

- `pair`
- `one_step_return_costs.by_prime`
- `one_step_return_costs.hardest_returns`
- `family_report`
- `dyadic_trend`

---

# 31. Stato finale, in tre frasi

1. **PET non replica l'aritmetica classica; costruisce una geometria di riscrittura sugli interi.**
2. **La reversibilità locale dei rewrite dipende fortemente dal primo coinvolto.**
3. **Le famiglie moltiplicative hanno ruoli globali diversi: `2^k` favorite, `3^k` quasi favorite, `5^k` e `7^k` sfavorite.**
