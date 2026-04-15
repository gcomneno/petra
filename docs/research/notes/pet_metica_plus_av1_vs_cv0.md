# PET-METICA `⊕`: A-v1 vs C-v0

## Scopo
Questa nota chiarisce il rapporto tra A-v1 e C-v0 dopo i controesempi di A-v0.

L'obiettivo non è scegliere subito un vincitore.
L'obiettivo è chiarire se A-v1 e C-v0 siano davvero candidati alternativi per la stessa operazione.

---

## 1. Punto di partenza

Dopo i controesempi ad A-v0, il quadro corrente è:

- A-v0 non basta come semantica finale
- A-v1 emerge come correzione naturale sul lato dei trasporti
- C-v0 resta un candidato forte sul lato degli stati

Questo però rivela una differenza più profonda:
- A-v1 e C-v0 non agiscono sullo stesso tipo di oggetti

---

## 2. Tipo semantico di A-v1

A-v1 nasce da:

- trasporti minimi orientati `T(a,b)`
- composizione compatibile
- richiusura semantica sul trasporto minimo risultante

Lettura corrente:
- A-v1 è un operatore su trasporti
- il suo risultato naturale è ancora un trasporto
- non restituisce primariamente uno stato

Quindi A-v1 risponde alla domanda:

- come si compongono due dinamiche di rewrite compatibili?

Non risponde direttamente alla domanda:

- quale stato ottengo sommando due stati?

---

## 3. Tipo semantico di C-v0

C-v0 nasce da:

- due stati `a`, `b`
- ricerca di un target comune ammissibile
- scelta del miglior target secondo un criterio locale

Lettura corrente:
- C-v0 è un operatore su stati
- il suo risultato naturale è uno stato
- non restituisce primariamente un trasporto

Quindi C-v0 risponde alla domanda:

- quale stato comune o fusione locale emerge naturalmente da due stati?

Non risponde direttamente alla domanda:

- come si compongono due trasporti orientati?

---

## 4. Conseguenza

A-v1 e C-v0 non sono, in senso stretto, due definizioni concorrenti dello stesso operatore.

Sono piuttosto due candidati per due nozioni diverse:

- `⊕_A` come composizione semantica di trasporti
- `⊕_C` come fusione o target comune di stati

Questa distinzione è cruciale.

Se la si ignora, si rischia di confrontare:
- una composizione di frecce
con
- un merge di nodi

come se fossero lo stesso problema.

Non lo sono.

---

## 5. Caso-manifesto: `(6,30)`

Il caso `(6,30)` ha mostrato:

- `6 -> 30` è una freccia privilegiata
- `30` emerge come miglior target comune per C-v0

Quindi:
- `(6,30)` è un ottimo test per C-v0
- `(6,30)` da solo non basta a testare A-v1

Per A-v1 serve invece una vera catena composabile, ad esempio:
- `(2,6,30)`

Questo conferma ancora una volta che i due candidati lavorano su oggetti diversi.

---

## 6. Caso-manifesto: `(2,6,30)`

Il caso `(2,6,30)` ha mostrato:

- `T(2,6)` e `T(6,30)` sono compatibili
- la loro composizione coincide con `T(2,30)`

Quindi:
- `(2,6,30)` è un ottimo test per A-v1
- non è invece il test più naturale per C-v0, che resta più leggibile come operatore binario su stati

Anche questo rafforza la separazione dei ruoli.

---

## 7. Lettura corrente più onesta

La lettura più onesta oggi è:

- A-v1 è il candidato serio per una nozione di `⊕` sui trasporti
- C-v0 è il candidato serio per una nozione di `⊕` sugli stati
- non è ancora chiaro se PET-METICA abbia bisogno di uno solo dei due
- non è escluso che servano due operazioni diverse, con nomi o livelli distinti

In altre parole:
- il problema potrebbe non essere “scegliere il vincitore”
- ma “smettere di costringere due nozioni diverse dentro lo stesso simbolo”

---

## 8. Bivio progettuale

A questo punto ci sono due strade pulite.

### Strada 1
Promuovere `⊕` come operazione primaria sui trasporti.
In questo caso:
- A-v1 diventa il candidato principale
- C-v0 resta una costruzione secondaria su stati

### Strada 2
Promuovere `⊕` come operazione primaria sugli stati.
In questo caso:
- C-v0 diventa il candidato principale
- A-v1 resta una composizione di trasporti con altra notazione o altro rango concettuale

### Strada 3
Accettare che esistano due operazioni diverse:
- una per stati
- una per trasporti

Questa, al momento, è la strada più onesta da non escludere.

---

## 9. Prossimo passo

Il prossimo passo utile non è scegliere subito un simbolo finale.

È decidere esplicitamente quale dei due livelli si vuole trattare come primario:

- livello degli stati
oppure
- livello dei trasporti

Solo dopo questa scelta ha senso stabilizzare davvero la semantica di `⊕`.
