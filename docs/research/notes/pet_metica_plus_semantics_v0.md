# PET-METICA `⊕` semantics v0

## Scopo
Questa nota fissa una semantica v0 esplicita per due candidati di `⊕`:

- A-v0: composizione di trasporti
- C-v0: target comune / merge

Non è una definizione finale di `⊕`.
Serve a rendere i candidati abbastanza espliciti da poterli confrontare e, se necessario, scartare.

---

## 1. Contesto minimo

In PET-METICA, la lettura corrente di `⊖` è:

- differenza come cammino minimo
- oppure come trasporto minimo di rewrite tra due stati PET

Quindi il problema di `⊕` va posto in uno di questi due modi:

- come operazione su trasporti
- oppure come operazione su stati che nasce da una costruzione naturale di rewrite

I due candidati sotto corrispondono esattamente a queste due famiglie.

---

## 2. Candidato A-v0 — composizione di trasporti

### 2.1. Oggetto di partenza

Un trasporto PET minimo da `a` a `b` è un cammino minimo orientato:

- `T(a,b) := path(a,b)`

quando tale cammino è definito.

In A-v0, `⊕` non agisce primariamente su stati, ma su trasporti.

### 2.2. Compatibilità

Due trasporti minimi

- `T(a,b)`
- `T(b,c)`

sono **compatibili** se il target del primo coincide con la sorgente del secondo.

Questa è la compatibilità minima di concatenazione.

### 2.3. Definizione v0

Per trasporti compatibili, si definisce:

- `T(a,b) ⊕_A T(b,c) := T(a,b) ⋅ T(b,c)`

dove `⋅` indica la concatenazione dei due cammini.

### 2.4. Normalizzazione minima

In v0 non si introduce ancora una normalizzazione forte dei cammini.
Il risultato è semplicemente:

- il cammino concatenato
- con eventuale riduzione futura lasciata aperta

Quindi A-v0 restituisce:
- un trasporto composto
- non uno stato
- non uno scalare

### 2.5. Lettura

A-v0 è leggibile come:

- composizione dinamica di rewrite
- estensione naturale della lettura di `⊖` come trasporto

### 2.6. Limite strutturale

A-v0 non è ancora una “somma di numeri”.
È più vicino a:
- una composizione di frecce
- una path algebra elementare
- una semantica di trasporti

Questo non è un difetto, ma va dichiarato apertamente.

---

## 3. Candidato C-v0 — target comune / merge

### 3.1. Oggetto di partenza

Dati due stati PET `a` e `b`, si cerca uno stato `t` che possa fungere da bersaglio comune naturale.

### 3.2. Ammissibilità v0

Uno stato `t` è **ammissibile** per `(a,b)` se:

- `a -> t` è raggiungibile tramite rewrite
- `b -> t` è raggiungibile tramite rewrite

Questa è la condizione minima.

### 3.3. Criterio di scelta v0

Tra i target ammissibili, si privilegiano quelli che minimizzano:

- prima `max(distance(a,t), distance(b,t))`
- poi `distance(a,t) + distance(b,t)`
- poi tie-break canonico crescente sul valore numerico di `t`

Quindi C-v0 definisce un target scelto come miglior compromesso locale tra i due ingressi.

### 3.4. Definizione v0

Se esiste un target ammissibile selezionato da questo criterio, allora:

- `a ⊕_C b := t*`

dove `t*` è il miglior target comune secondo il ranking sopra.

### 3.5. Lettura

C-v0 restituisce:
- uno stato
- non un trasporto

Quindi è più vicino all’idea intuitiva di una “somma” o fusione su stati.

### 3.6. Limite strutturale

C-v0 rischia di dipendere troppo da:
- euristiche di selezione
- tie-break
- esistenza non robusta di target naturali

Quindi è leggibile, ma potenzialmente fragile.

---

## 4. Test manifesto

I candidati vanno letti su casi piccoli e ad alta leggibilità.

### 4.1. Caso dyadico: `2, 4, 8`
Serve per capire:
- se il candidato vive bene dentro una famiglia semplice
- se sta solo sfruttando un caso troppo favorevole

### 4.2. Caso misto: `4, 12`
Serve per capire:
- se il candidato regge oltre la sola torre del 2
- se un target comune è davvero strutturale o solo comodo

### 4.3. Caso manifesto: `6, 30`
Serve per capire:
- se il candidato riconosce una freccia privilegiata già emersa in PET-METICA
- se il risultato resta leggibile senza convenzioni artificiali

---

## 5. Verdetto provvisorio sui due candidati

### A-v0
Punti forti:
- è la prosecuzione più naturale della lettura di `⊖`
- evita il trucco del punto base
- parla direttamente in termini di trasporti

Punti deboli:
- non restituisce ancora una somma di stati
- rischia di essere più una composizione che una vera `⊕`

Giudizio provvisorio:
- candidato principale da sviluppare

### C-v0
Punti forti:
- restituisce uno stato
- è intuitivamente leggibile come fusione o target comune

Punti deboli:
- dipende da un criterio di selezione
- rischia di essere troppo euristico
- potrebbe funzionare bene solo in casi privilegiati

Giudizio provvisorio:
- candidato secondario, utile soprattutto come benchmark locale

---

## 6. Lettura corrente più onesta

La lettura più onesta, allo stato attuale, è:

- A-v0 è il candidato teoricamente più naturale
- C-v0 è il candidato più intuitivo come operazione su stati
- A-v0 sembra più profondo
- C-v0 sembra più fragile ma più “somma-like”

Quindi il vero confronto futuro è:

- profondità semantica di A
contro
- leggibilità operativa di C

---

## 7. Prossimo passo

Il prossimo passo utile non è definire `⊕` in generale.

È questo:

1. istanziare A-v0 su esempi concreti come composizione di cammini minimi
2. istanziare C-v0 su esempi concreti come scelta di target comune
3. vedere quale dei due candidati resta leggibile senza introdurre artifici eccessivi

Se uno dei due collassa subito in convenzioni arbitrarie, va scartato presto.
