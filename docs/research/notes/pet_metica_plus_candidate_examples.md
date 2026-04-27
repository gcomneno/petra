# PET-METICA `⊕` definition examples

## Scopo
Questa nota confronta definizioni preliminari di `⊕` su pochi casi-manifesto.
Non promuove ancora nessuna definizione. Serve a scartare presto le definizioni deboli o artificiali.

---

## Definizioni testate

### A. Composizione di trasporti
Idea:
- trattare `⊕` come composizione/concatenazione di trasporti compatibili

Domanda guida:
- il risultato è leggibile come dinamica naturale di rewrite?

### B. Operazione su stati via punto base
Idea:
- scegliere un punto base `g`
- leggere gli stati tramite i trasporti da `g`
- combinare tali trasporti

Domanda guida:
- il risultato dipende troppo dal riferimento scelto?

### C. Target comune / merge
Idea:
- cercare uno stato bersaglio che assorba o combini naturalmente due stati

Domanda guida:
- il target risultante è naturale oppure solo euristico?

---

## Caso 1 — 2, 4, 8

### A. Composizione di trasporti
Osservazione iniziale:
- questo è il caso più favorevole
- la torre dyadica sembra offrire una dinamica ordinata e leggibile

Giudizio preliminare:
- promettente

### B. Punto base
Osservazione iniziale:
- con un punto base dyadico il caso appare relativamente naturale
- resta però il sospetto che il buon comportamento dipenda dalla famiglia scelta

Giudizio preliminare:
- plausibile ma sospetto

### C. Target comune / merge
Osservazione iniziale:
- qui il target comune sembra quasi ovvio dentro la famiglia
- rischio: il caso è troppo favorevole e troppo speciale

Giudizio preliminare:
- utile come sanity check, non decisivo

---

## Caso 2 — 4, 12

### A. Composizione di trasporti
Osservazione iniziale:
- il passaggio tra stato puramente dyadico e stato misto è già più istruttivo
- qui si vede se la definizione regge oltre la sola torre del 2

Giudizio preliminare:
- da testare bene

### B. Punto base
Osservazione iniziale:
- la dipendenza dal punto base potrebbe iniziare a farsi sentire
- il risultato rischia di cambiare faccia a seconda del riferimento

Giudizio preliminare:
- sospetto medio

### C. Target comune / merge
Osservazione iniziale:
- `12` sembra un possibile target assorbente naturale rispetto a `4`
- ma non è ancora chiaro se questa lettura sia strutturale o solo comoda

Giudizio preliminare:
- interessante

---

## Caso 3 — 6, 30

### A. Composizione di trasporti
Osservazione iniziale:
- questo è il caso-manifesto più importante
- `6 -> 30` è già una freccia privilegiata via `NEW(x5)`

Giudizio preliminare:
- molto promettente

### B. Punto base
Osservazione iniziale:
- qui il punto base rischia di introdurre artificio più che chiarimento
- il caso sembra voler parlare direttamente in termini di trasporto, non di riferimento esterno

Giudizio preliminare:
- debole

### C. Target comune / merge
Osservazione iniziale:
- `30` sembra una scelta naturale come target comune/esteso rispetto a `6`
- ma attenzione: questo non basta a dire che il merge definisca una buona `⊕` in generale

Giudizio preliminare:
- promettente localmente, non ancora generale

---

## Tabella di lettura provvisoria

| Candidato | 2,4,8 | 4,12 | 6,30 | Giudizio provvisorio |
|---|---|---|---|---|
| Composizione di trasporti | buono | da testare | molto buono | miglior definizione iniziale |
| Punto base | plausibile | sospetto | debole | definizione fragile |
| Target comune / merge | plausibile | interessante | promettente | definizione locale da capire meglio |

---

## Lettura corrente

La lettura più promettente, allo stato attuale, è:

- `⊕` come operazione più vicina a una composizione/aggregazione di trasporti
- oppure, in alternativa, come costruzione di target comune in casi privilegiati

La definizione via punto base al momento appare più artificiale.

---

## Prossimo passo

Prima di definire `⊕`, conviene fare un altro passaggio piccolo:

- scegliere una semantica esplicita per la definizione A
- scegliere una semantica esplicita per la definizione C
- testarle sugli stessi casi manifesto
- vedere quale delle due resta leggibile senza introdurre convenzioni troppo arbitrarie
