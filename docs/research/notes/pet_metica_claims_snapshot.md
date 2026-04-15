# PET-METICA claims snapshot

## Scopo
Questa nota fissa lo stato attuale dei claim PET-METICA dopo una robustness pass empirica su range piccoli/medi.
Non contiene teoremi. Distingue esplicitamente tra pattern robusti, pattern empirici ancora aperti e metriche considerate sporche.

## Setup minimo usato
Scan eseguiti con:
- `n_max=40`, `overscan=160`
- `n_max=80`, `overscan=320`
- `n_max=120`, `overscan=480`

Metriche considerate affidabili in questa pass:
- `family_report`
- `one_step_return_costs.by_prime`
- `one_step_return_costs.hardest_returns`
- `matrix` per misure aggregate di asimmetria

Metriche non usate come base teorica:
- `top_attractors`

---

## Claim robusti

### 1. Gerarchia locale di frizione per primo
Il pattern più stabile osservato è:

`2 < 3 < 5 < 7`

Misurato tramite `one_step_return_costs.by_prime`.

Valori osservati:
- `n=40`: `1.000 < 2.000 < 2.600`
- `n=80`: `1.000 < 1.857 < 3.000 < 5.800`
- `n=120`: `1.000 < 1.836 < 3.250 < 4.714`

Lettura corrente:
- forte legge empirica locale
- i primi più alti introducono maggiore frizione di ritorno

### 2. Famiglie globali favorite e repulsive
Per `n=80` e `n=120` il quadro è stabile:

- `2^k` = famiglia attrattiva stabile
- `3^k` = quasi neutra alla base, debolmente attrattiva sulle potenze superiori
- `5^k` = repulsiva
- `7^k` = fortemente repulsiva

Lettura corrente:
- il ramo dyadico è il più chiaramente favorito
- il ramo ternario è molto più debole e più sottile
- i rami `5` e `7` sono sfavoriti, con `7` molto più duro

### 3. Asimmetria reale e non rara
La distanza PET è direzionale in modo sostanziale.

Tassi osservati:
- `n=40`: `asymmetry_rate = 0.294`
- `n=80`: `asymmetry_rate = 0.451`
- `n=120`: `asymmetry_rate = 0.412`

Casi forti osservati:
- `(6,30)`: gap `4`
- `(8,56)`: gap `10` a `n=80`
- `(16,112)`: gap `8` a `n=120`

Lettura corrente:
- l’asimmetria non è occasionale
- va trattata come tratto strutturale della geometria di rewrite

### 4. I hardest returns sono dominati da primi costosi
I ritorni più costosi sono stabilmente concentrati attorno a mosse con primo alto, soprattutto `7`.

Casi-manifesto osservati:
- `56 --DROP(p=7)--> 8`
- `28 --DROP(p=7)--> 4`
- `63 --DROP(p=7)--> 9`
- `112 --DROP(p=7)--> 16`
- `6 --NEW(x5)--> 30`

Lettura corrente:
- `DROP(p=7)` è una fonte sistematica di ritorni duri
- `NEW(x5)` ha almeno un caso-manifesto molto stabile (`6 -> 30`)

---

## Claim empirici plausibili ma non ancora stabilizzati

### 1. Plateau dyadico positivo
Nel `family_report`, le potenze di `2` mostrano:
- picco forte su `4`
- poi un plateau positivo ancora alto su `8,16,32,64`

Questo pattern è robusto nei range medi testati, ma non è ancora dimostrato né calibrato asintoticamente.

### 2. Struttura più fine del ramo `3^k`
Il ramo `3^k` sembra:
- quasi neutro su `3`
- positivo su `9,27,81`

È plausibile che esista una distinzione tra base del ramo e potenze più profonde, ma la lettura è ancora empirica.

### 3. Intensità dell’asimmetria al crescere del range
L’asimmetria resta evidente, ma:
- cresce da `0.294` a `0.451`
- poi si assesta a `0.412`

Quindi la presenza dell’asimmetria è robusta, mentre la sua legge di crescita non è ancora stabilizzata.

---

## Correzioni di rotta già acquisite

### 1. `30` non è un attrattore globale semplice
La lettura più onesta è:
- `30` è un hub composto importante
- ha asimmetrie selettive forti
- non va trattato come attrattore globale semplice

### 2. `top_attractors` è una metrica sporca
Questa metrica si è rivelata poco affidabile a range più grandi.
Non va usata come base teorica primaria.

### 3. `n=40` non è sufficiente per claim globali sulle famiglie
Esempio:
- `7` risulta positivo a `n=40`
- ma fortemente negativo a `n=80` e `n=120`

Lettura corrente:
- `n=40` è utile per esplorazione locale
- non basta per fissare claim globali di famiglia

---

## Fronti aperti

### 1. Nessuna asimmetria di ampiezza 1 nei range testati
Nei range `40, 80, 120` si osserva:

- `asymmetry_rate == strong_asymmetry_rate(>=2)`

Quindi, empiricamente, tutte le asimmetrie osservate hanno modulo almeno `2`.

Questo è interessante, ma va trattato come pattern aperto, non come legge.

### 2. Ranking preciso dei hardest returns
Il fatto che i casi duri coinvolgano spesso `7` è robusto.
Il ranking preciso e il massimo assoluto, invece, cambiano col range.

### 3. Formalizzazione concettuale della differenza PET
La faccia attuale più naturale di `⊖` resta:
- cammino minimo canonico / trasporto di rewrite

Ma la formalizzazione definitiva è ancora da rifinire.

### 4. Formalizzazione di `⊕`
Ancora aperta.

### 5. Single free tower policy
Ancora aperta:
- possibile euristica locale forte
- non ancora promossa a congettura seria

---

## Formula sintetica corrente
La PET-aritmetica interessante non restituisce “quanto fa”, ma “come ci arrivi”.

Più precisamente:
- gli interi formano uno spazio di rewrite
- le mosse primitive hanno frizioni diverse
- esistono hub strutturali
- esistono famiglie favorite e repulsive
- la distanza è direzionale
- la differenza naturale ha la faccia di un trasporto, non di uno scalare
