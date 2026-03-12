# Guida per il supervisore – Bargaining Game (TDL + Async)

Questo documento descrive le **app** dell’esperimento, come sono **collegate**, le **pagine** che i partecipanti incontrano e i **punti in cui il flusso può cambiare** (es. control questions fallite). È pensato per chi supervisiona la sessione e deve capire il percorso completo senza entrare nei dettagli tecnici.

---

## 1. Panoramica del flusso

L’esperimento è un **unico session** con **4 app in sequenza**:

```
bargaining_tdl_intro  →  bargaining_tdl_main  →  bargaining_tdl_part2  →  bargaining_tdl_part3
```

- **Intro**: istruzioni e control questions; chi non le passa viene **escluso** (vede Goodbye e non prosegue).
- **Main**: formazione dei gruppi da 3, chat/signals, decisione di Part 1 e risultati.
- **Part 2**: istruzioni, control questions, domande MPL (Matching Probability List).
- **Part 3**: istruzioni, control questions, decisione del dictator game e payoff finale.

Il numero di partecipanti per sessione è configurato in `settings.py` (es. 9 per la demo). I partecipanti che **falliscono le control questions in intro** vedono solo **intro + Goodbye** e l’esperimento per loro termina lì. Chi **fallisce le control questions in Part 2** vede **ThankYouPart2** e termina (nessuna Part 3). Chi **fallisce le control questions in Part 3** vede **ThankYouPart3** e termina senza vedere la decisione né il payoff finale.

---

## 2. App 1: `bargaining_tdl_intro`

**Ruolo:** Fase iniziale **individuale**. Ogni partecipante legge le istruzioni e risponde alle control questions. **Non ci sono ancora gruppi.**

| # | Pagina | Descrizione |
|---|--------|-------------|
| 1 | **Welcome** | Benvenuto e istruzioni generali. |
| 2 | **InstructionsPart1** | Istruzioni dettagliate della Part 1 (bargaining a tre). |
| 3–7 | **ControlQuestionsAttempt1 … Attempt5** | Domande di comprensione (esempi di payoff, come si viene pagati). Fino a 5 tentativi (numero massimo configurabile in sessione). Solo **un** tentativo per volta è visibile (Attempt1, poi eventualmente Attempt2, ecc.). |
| 8 | **Goodbye** | Mostrata **solo** a chi ha **fallito** le control questions dopo tutti i tentativi consentiti. Dopo Goodbye l’esperimento per quel partecipante **termina** (non passa a main). |

**Collegamento con le altre app:**

- Chi **passa** le control questions: dopo l’ultima pagina vista (un tentativo di control questions) **non** vede Goodbye e, cliccando “Next”, arriva alla **wait page** della app successiva (**bargaining_tdl_main**), dove verranno formati i gruppi.
- Chi **fallisce** le control questions: vede **Goodbye** e l’app sequence per lui si interrompe (`app_after_this_page` restituisce lista vuota).

---

## 3. App 2: `bargaining_tdl_main`

**Ruolo:** Formare **gruppi da 3** (triadi), far compilare **chat e segnali** (intenzioni), poi **decisione** della Part 1 e **risultati**. Chi aveva fallito le control questions in intro **non** vede le pagine operative (vede solo ExperimentTerminated e poi esce).

| # | Pagina | Tipo | Descrizione |
|---|--------|------|-------------|
| 1 | **GroupingAfterControlQuestions** | Wait page | “Aspettate gli altri per formare il gruppo.” I partecipanti vengono raggruppati **per ordine di arrivo** (chi passa per primo le control questions forma il primo gruppo, ecc.). |
| 2 | **ChatAndSignals** | Pagina | Chat (testi) verso il giocatore a sinistra e a destra + scelta delle **intenzioni** (signal) verso sinistra e verso destra. Dati salvati e poi usati per la Part 2. |
| 3 | **ExperimentTerminated** | Pagina | Mostrata **solo** a chi ha fallito le control questions in intro. Dopo questa pagina l’esperimento per quel partecipante **termina**. |
| 4 | **DataMappingWaitPage** | Wait page | Sincronizzazione e mappatura dei dati di chat/signals tra i tre membri del gruppo (chi riceve cosa da chi). Non mostrata a chi ha fallito le control questions. |
| 5 | **Decision** | Pagina | Scelta: dividere con il giocatore a sinistra, a destra, o con entrambi (tutti e tre). Non mostrata a chi ha fallito le control questions. |
| 6 | **ResultsWaitPage** | Wait page | Attesa che tutti e tre abbiano scelto; calcolo dei payoff della Part 1. Non mostrata a chi ha fallito le control questions. |
| 7 | **Results** | Pagina | Visualizzazione del risultato e del payoff Part 1. Il payoff viene salvato in `participant.vars` per Part 2 e Part 3. Non mostrata a chi ha fallito le control questions. |

**Collegamento:** Dopo Results tutti i partecipanti che sono ancora in gioco passano automaticamente a **bargaining_tdl_part2**.

---

## 4. App 3: `bargaining_tdl_part2`

**Ruolo:** **Part 2** – Istruzioni, control questions e **12 domande MPL** (Matching Probability List) per misurare le credenze probabilistiche sugli eventi della Part 1. **Nessun gruppo:** ogni partecipante risponde da solo.

| # | Pagina | Descrizione |
|---|--------|-------------|
| 1 | **InstructionsPart2** | Istruzioni della Part 2. |
| 2 | **PaymentInstructionPart2** | Istruzioni su come si viene pagati nella Part 2. |
| 3–7 | **ControlQuestionsPart2Attempt1 … Attempt5** | Control questions della Part 2 (fino a 5 tentativi). |
| 8 | **ThankYouPart2** | Se le control questions Part 2 sono **fallite** dopo tutti i tentativi, il partecipante vede questa pagina e l’esperimento per lui **termina** (non passa a Part 3). |
| 9 | **MPLIntroFirstPlayer** | Introduzione alla prima serie di domande MPL (giocatore a sinistra / a destra – ordine randomizzato). |
| 10–15 | **MPLQuestion1 … MPLQuestion6** | Prime 6 domande MPL. |
| 16 | **MPLIntroSecondPlayer** | Introduzione alla seconda serie (l’altro “lato”). |
| 17–22 | **MPLQuestion7 … MPLQuestion12** | Ultime 6 domande MPL. |
| 23 | **ResultsPart2** | Riepilogo / risultati Part 2 (payoff Part 2 calcolato in seguito per la Part 3). |

**Collegamento:** Dopo Part 2 i partecipanti passano a **bargaining_tdl_part3**.

---

## 5. App 4: `bargaining_tdl_part3`

**Ruolo:** **Part 3** – Istruzioni, control questions e **Three-Person Dictator Game**: scelta individuale che determina, insieme a Part 1 e Part 2, il **payoff finale**.

| # | Pagina | Descrizione |
|---|--------|-------------|
| 1 | **InstructionsPart3** | Istruzioni della Part 3. |
| 2 | **SummaryPart3** | Riepilogo (payoff Part 1 e Part 2, come si compone il pagamento finale). |
| 3–7 | **ControlQuestionsPart3Attempt1 … Attempt5** | Control questions della Part 3 (fino a 5 tentativi). |
| 8 | **ThankYouPart3** | Mostrata **solo** a chi ha **fallito** le control questions della Part 3. Dopo questa pagina l’esperimento per quel partecipante **termina** (nessuna decisione Part 3 né Results Part 3). |
| 9 | **DecisionPart3** | Scelta del dictator (condivisione con sinistra, destra o entrambi). Mostrata **solo** a chi ha **passato** le control questions Part 3. |
| 10 | **ResultsPart3** | Payoff finale (Part 2 + max(Part 1, Part 3)). Mostrata **solo** a chi ha passato le control questions e ha completato DecisionPart3. |

**Collegamento:** Dopo ResultsPart3 (o dopo ThankYouPart3 per chi ha fallito) l’esperimento è concluso per tutti.

---

## 6. Riepilogo collegamenti tra app

| Da | A | Condizione |
|----|---|------------|
| **intro** | **main** | Solo se le control questions intro sono **passate** (altrimenti Goodbye → fine). |
| **main** | **part2** | Tutti coloro che sono ancora in sessione dopo main (chi ha fallito intro vede solo ExperimentTerminated e poi esce). |
| **part2** | **part3** | Solo chi ha **passato** le control questions Part 2 (chi le fallisce vede ThankYouPart2 e termina l’esperimento). |
| **part3** | — | Fine esperimento. Chi ha fallito le control questions Part 3 vede ThankYouPart3 e termina; gli altri vedono DecisionPart3 e ResultsPart3. |

---

## 7. Punti critici per la supervisione

1. **Control questions intro**  
   Se un partecipante non passa dopo il numero massimo di tentativi, vede **Goodbye** e non entra mai in main (nessun gruppo, nessuna decisione Part 1). Controllare che il numero di tentativi sia quello desiderato in `settings.py` (`control_questions_max_attempts`).

2. **Formazione dei gruppi (main)**  
   I gruppi da 3 si formano **per ordine di arrivo** alla prima wait page di main. Quindi l’ordine in cui i partecipanti **superano le control questions in intro** determina chi finisce nello stesso gruppo. Utile spiegarlo in sala se si fa riferimento ai “gruppi”.

3. **Part 2 e Part 3**  
   In Part 2, chi fallisce le control questions vede **ThankYouPart2** e l’esperimento **termina** (nessuna Part 3). In Part 3, chi fallisce le control questions non vede DecisionPart3 né ResultsPart3 (solo ThankYouPart3 e fine). Il payoff finale (Part 2 + max(Part 1, Part 3)) si applica solo a chi completa Part 3 con successo.

4. **Numero di partecipanti**  
   Per avere solo gruppi da 3 senza “avanzi”, il numero di partecipanti per sessione deve essere **multiplo di 3** (es. 6, 9, 12). Configurazione in `settings.py` (es. `num_demo_participants` per la demo).

5. **Perché il “numero di gruppo” cambia passando da un’app all’altra**  
   Se in fase di debug o in export compaiono Group ID / numero di gruppo diversi tra intro, main, part2 e part3, **non è un errore**. Ogni app ha la **propria** matrice di gruppi in oTree: in **intro** non ci sono gruppi da 3 (i partecipanti sono singoli o in gruppi “virtuali” solo per la struttura dell’app); in **main** i gruppi da 3 vengono creati e sono quelli rilevanti per la Part 1. In **part2** e **part3** non si usano gruppi per la logica di gioco, ma oTree assegna comunque un gruppo di default per ogni app. Quindi il numero o l’ID di gruppo che si vede **dipende dall’app corrente** e può cambiare al passaggio da un’app alla successiva. **La composizione reale della triade** (chi è con chi nella Part 1) è fissata in main e resta invariata nei dati; a cambiare è solo il “label” di gruppo mostrato in ciascun modulo. Se un partecipante o un revisore solleva l’obiezione “il mio gruppo è cambiato”, si può spiegare che si tratta di questo comportamento del software, non di una riassegnazione dei compagni di gruppo.

---

## 8. Riferimenti rapidi

- **Configurazione sessione:** `settings.py` → `SESSION_CONFIGS` → `app_sequence`, `num_demo_participants`, `control_questions_max_attempts`.
- **Documentazione tecnica (sviluppatori):** `docs/ARCHITECTURE.md`.
- **Testing:** `docs/TESTING.md`, `docs/HOW_TESTS_WORK.md`.

---

*Documento per il supervisore dell’esperimento – Bargaining Game (TDL + Async).*
