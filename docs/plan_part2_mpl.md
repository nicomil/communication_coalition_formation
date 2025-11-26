# Piano d'Azione: Implementazione Parte 2 - Matching Probability List (MPL)

## 📋 Overview
Implementare la **Parte 2** dell'esperimento che genera 12 MPL questions per ogni partecipante basandosi sui dati della Parte 1 (bargaining game).

## ⚠️ PRINCIPIO FONDAMENTALE: NON MODIFICARE INTRO E MAIN
**IMPORTANTE**: Questo piano implementa una nuova app `bargaining_tdl_part2` che:
- **LEGGE SOLO** i dati esistenti da `bargaining_tdl_intro` e `bargaining_tdl_main`
- **NON MODIFICA** in alcun modo i file di `bargaining_tdl_intro` o `bargaining_tdl_main`
- **NON SALVA** dati aggiuntivi nei modelli di intro/main
- **NON RICHIEDE** modifiche al codice esistente di intro/main

Se durante l'implementazione si ritiene necessario modificare qualcosa in `bargaining_tdl_intro` o `bargaining_tdl_main`, **CHIEDERE AUTORIZZAZIONE** prima di procedere.

---

# ⚠️ SEZIONE CRITICA: TESTI ORIGINALI OBBLIGATORI

**ATTENZIONE: I seguenti testi sono OBBLIGATORI e NON DEVONO ESSERE MODIFICATI in alcun modo durante l'implementazione.**

Tutti i testi devono essere inclusi esattamente come riportato di seguito. Il sistema di implementazione DEVE utilizzare questi testi come costanti o stringhe letterali nel codice.

---

## 📄 1. Testo del Paper (Sezione 3.2) - OBBLIGATORIO

**Fonte**: Paper DPPT_10_11_25_Paper.pdf, Sezione 3.2

```
3.2 Part Two: Matching Probability

This part of the experiment consists of eliciting individual ambiguity aversion, ambiguity-
generated insensitivity and ambiguity-neutral beliefs for natural events, through the use of

the matching probability procedure presented by Baillon et al. (2018). Each participant is
presented with 12 questions, 6 for each participant in the triad. Each question measures the
participant's preference between betting on given probabilities and betting on the choices of
other participants in part one (see Figure 2). The latter are referred to either single, and
composite events (see Table 1, and Figure 3). For example, suppose you are participant A1,
part of the triad with participants B1 and C1 in Part One; each question is presented with
two options:
• Option 1: You win e5 if Participant B1 chose "Share only with Participant C1" or
"Share with both Participant A1 and Participant C1" (and nothing otherwise).
• Option 2: You win e5 with p% probability (and nothing otherwise).
In all questions, each subject is offered the chance to win e5, the probabilities range of the
above options span from 0 to 100. These questions are presented in the form of multiple
price lists (MPLs) with ascending p values, and the participant is provided with an on-screen
reminder of the signals previously sent and received.
```

**Note per implementazione**:
- Il simbolo "e5" deve essere interpretato come "€5" (euro 5) o "£5" (sterline 5) in base alle istruzioni
- I riferimenti a "Participant A1", "Participant B1", "Participant C1" devono essere convertiti in "you", "player on the left", "player on the right" nell'interfaccia utente

---

## 📄 2. Istruzioni Ufficiali Parte 2 - OBBLIGATORIE

**Fonte**: Istruzioni ufficiali per i partecipanti

```
In Part 2, we will ask you to express your preference between bets on given probabilities and
bets on the choice in Part 1 of another participant (with whom you interacted in Part 1).
Suppose you are you, matched with the player on the left and the player on the right for
Part 1. In each question you will be presented with two options of the following type:

• Option 1: You win $ 5 if the player on the left chose "Share only with the player on the
right" or "Share with both you and the player on the right" (and nothing otherwise).
• Option 2: You win $ 5 with p% probability (and nothing otherwise).
In all questions, as in the above example, you will be offered the chance to win $ 5. You
will be asked to state which one of these two options you prefer for various values p, from 0
to 100. Let us illustrate it with the example given above for some values of p:
If p = 100, you will most likely prefer Option 2 because you are then guaranteed to win
$ 5.
If p = 0, then you will most likely prefer Option 1, as you might win something, as
opposed to Option 2, where there is no chance of you to win at all.
On the next screen you will see an example of the screens you will soon interact with.
As you have seen in the figure, on the left you will have a description of Option 1, along
with a reminder of what you and the other Participant (whose choice is the subject of the
bets) have declared to each other.
On the right hand side Option 2 will be presented with ascending p values. For each
value of p you are asked to state your preference between Option 1 and the given probability
option by clicking on the respective option button.
Note that if you prefer Option 1 when, for instance, the given probability option offers
you 75% chance of winning (that is, p = 75), then when the given probability option offers
an even lower chance of winning, say 60% (p = 60), then you should again choose Option
1 over the given probability option. Similarly, imagine that you like the given probability
option better than Option 1 when p = 93. Then, when the given probability option offers
an even better chance of winning, say p = 97, then it is expected that you still prefer the
given probability option to Option 1.
Accordingly, you will notice that in the figure above there is only a single switch from
80% to 85%. For every value of p from 0 until 80%, Option 1 is chosen, and for all values
of p from 85% up, Option 2 has been selected. To save you the trouble of clicking on the
option button for each value of p, the program has been designed to work with a single click.

You can click on Option 2 for the probability such that, for that probabil-
ity and all better (higher) probabilities, you prefer Option 2, and for all worse

(lower) probabilities you prefer Option 1. Similarly, you can also click on Op-
tion 1 for the probability such that, for that probability and all worse (lower)

probabilities, you prefer Option 1, and for all better (higher) probabilities you
prefer Option 2.
The computer will then automatically indicate all of your choices.
You can change your choices as many times as you want. However, once you have made
your final decision and clicked on the appropriate option box, you will need to click the
"OK" button to register your choices and move on to the next question. This button will
only appear after you've selected a preferred option for each line.
You will not be allowed to go back to a question once you have clicked on the "OK"
button.
```

**Note per implementazione**:
- Il simbolo "$ 5" deve essere interpretato come "€5" o "£5" in base alle istruzioni
- Il testo deve essere incluso ESATTAMENTE come sopra, senza modifiche

---

## 📄 3. Testo Reminder Parte 1 - OBBLIGATORIO

**Testo da mostrare in ogni MPL question**:

```
We remind you of the following information regarding what you and Participant X have declared to each other:
You said: [...]
Participant X said: [...]
```

**Dove**:
- `Participant X` deve essere sostituito con "the player on the left" o "the player on the right" in base al mapping
- `You said: [...]` deve contenere l'intenzione dichiarata dal partecipante corrente al target participant
- `Participant X said: [...]` deve contenere l'intenzione dichiarata dal target participant al partecipante corrente

**Esempio concreto** (da screenshot):
```
We remind you of the following information regarding what you and Participant A1 have declared to each other:
You said: I want to share only with Participant B1.
Participant A1 said: I want to share with both Participant B1 and Participant C1
```

**Nota**: Nell'interfaccia, "Participant A1" deve essere sostituito con "the player on the left" o "the player on the right" in base al mapping.

---

## 📄 4. Testi delle Opzioni di Scelta Parte 1 - OBBLIGATORI

**Mapping Eventi → Testi (da usare in Option 1)**:

### Per il "player on the left" (B nel gruppo):
- **EB1**: "Share only with the player on the right"
- **EB2**: "Share only with you"
- **EB3**: "Share with both you and the player on the right"

### Per il "player on the right" (C nel gruppo):
- **EC1**: "Share only with the player on the left"
- **EC2**: "Share only with you"
- **EC3**: "Share with both you and the player on the left"

**IMPORTANTE**: Questi testi devono essere usati ESATTAMENTE come riportati sopra, senza modifiche.

---

## 📄 5. Struttura Testo Option 1 - OBBLIGATORIA

### Per Single Event:
```
You win €5 if the player on the left chose "[TESTO_EVENTO]" (and nothing otherwise).
```

o

```
You win €5 if the player on the right chose "[TESTO_EVENTO]" (and nothing otherwise).
```

### Per Composite Event:
```
You win €5 if the player on the left chose "[TESTO_EVENTO_1]" or "[TESTO_EVENTO_2]" (and nothing otherwise).
```

o

```
You win €5 if the player on the right chose "[TESTO_EVENTO_1]" or "[TESTO_EVENTO_2]" (and nothing otherwise).
```

**Dove**:
- `[TESTO_EVENTO]` deve essere sostituito con uno dei testi della sezione 4
- `€5` può essere `£5` se richiesto dalle istruzioni
- La struttura con "(and nothing otherwise)" è OBBLIGATORIA

---

## 📄 6. Struttura Testo Option 2 - OBBLIGATORIA

```
You win €5 with the following probability (and nothing otherwise).
```

**Dove**:
- `€5` può essere `£5` se richiesto dalle istruzioni
- Il testo deve essere ESATTAMENTE come sopra

---

## 📄 7. Liste Probabilità - OBBLIGATORIE

### Single Event:
```
0%, 1%, 2%, 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50%, 55%, 60%, 65%, 70%, 75%, 85%, 100%
```

**Nota**: Notare il salto da 75% a 85% (mancano 76%-84%).

### Composite Event:
```
0%, 20%, 35%, 40%, 45%, 50%, 55%, 60%, 65%, 70%, 75%, 80%, 85%, 90%, 93%, 95%, 97%, 98%, 99%, 100%
```

**Nota**: La lista per Composite Event è diversa da Single Event, con valori più sparsi all'inizio (0%, 20%, 35%) e più densi verso la fine (93%, 95%, 97%, 98%, 99%, 100%).

---

## 📄 8. Le 12 Domande MPL - DA SPECIFICARE

**STATO**: ⚠️ **PENDING** - Le specifiche esatte delle 12 domande per ogni partecipante (A, B, C) devono essere fornite.

### Struttura Attesa:

Per ogni partecipante (A, B, C), devono essere specificate **12 domande**, così suddivise:
- **6 Single Event**
- **6 Composite Event**

### Formato Atteso per Ogni Domanda:

```python
{
    'question_num': int,  # 1-12
    'type': 'single' | 'composite',
    'target_code': 'A' | 'B' | 'C',  # Chi ha fatto la scelta
    'event_codes': list[str],  # Es. ['EB1'] per single, ['EB2', 'EB3'] per composite
    'description': str  # Descrizione testuale (opzionale)
}
```

### Domande da inserire:

Participant A
EB1 You win $ 5 if Participant B divide equally with Participant A only (single event)


EC1 You win $ 5 if Participant C divide equally with Participant A only (single event)


EB2 You win $ 5 if Participant B divide equally with Participant C only (single event)


EC2 You win $ 5 if Participant C divide equally with Participant B only (single event)


EB3 You win $ 5 if Participant B divide equally among all three participants (single event)


EC3 You win $ 5 if Participant C divide equally among all three participants (single event)


EB12 You win $ 5 if Participant B divide equally with Participant A only or Participant B divide equally with Participant C only (composite event)


EC12 You win $ 5 if Participant C divide equally with Participant A only or Participant C divide equally with Participant B only (composite event)


EB23 You win $ 5 if Participant B divide equally with Participant C only or Participant B divide equally among all three participants (composite event)


EC23 You win $ 5 if Participant C divide equally with Participant B only or Participant C divide equally among all three participants (composite event)


EB31 You win $ 5 if Participant B divide equally among all three participants or Participant B divide equally with Participant A only (composite event)


EC31 You win $ 5 if Participant C divide equally among all three participants or Participant C divide equally with Participant A only (composite event)



Participant B
EA1 You win $ 5 if Participant A divide equally with Participant B only (single event)


EC1 You win $ 5 if Participant C divide equally with Participant B only (single event)


EA2 You win $ 5 if Participant A divide equally with Participant C only (single event)


EC2 You win $ 5 if Participant C divide equally with Participant A only (single event)


EA3 You win $ 5 if Participant A divide equally among all three participants (single event)


EC3 You win $ 5 if Participant C divide equally among all three participants (single event)


EA12 You win $ 5 if Participant A divide equally with Participant B only or Participant A divide equally with Participant C only (composite event)


EC12 You win $ 5 if Participant C divide equally with Participant B only or Participant C divide equally with Participant A only (composite event)


EA23 You win $ 5 if Participant A divide equally with Participant C only or Participant A divide equally among all three participants (composite event)


EC23 You win $ 5 if Participant C divide equally with Participant A only or Participant C divide equally among all three participants (composite event)


EA31 You win $ 5 if Participant A divide equally among all three participants or Participant A divide equally with Participant B only (composite event)


EC31 You win $ 5 if Participant C divide equally among all three participants or Participant C divide equally with Participant B only (composite event)



Participant C
EA1 You win $ 5 if Participant A divide equally with Participant C only (single event)


EB1 You win $ 5 if Participant B divide equally with Participant C only (single event)


EA2 You win $ 5 if Participant A divide equally with Participant B only (single event)


EB2 You win $ 5 if Participant B divide equally with Participant A only (single event)


EA3 You win $ 5 if Participant A divide equally among all three participants (single event)


EB3 You win $ 5 if Participant B divide equally among all three participants (single event)


EA12 You win $ 5 if Participant A divide equally with Participant C only or Participant A divide equally with Participant B only (composite event)


EB12 You win $ 5 if Participant B divide equally with Participant C only or Participant B divide equally with Participant A only (composite event)


EA23 You win $ 5 if Participant A divide equally with Participant B only or Participant A divide equally among all three participants (composite event)


EB23 You win $ 5 if Participant B divide equally with Participant A only or Participant B divide equally among all three participants (composite event)


EA31 You win $ 5 if Participant A divide equally among all three participants or Participant A divide equally with Participant C only (composite event)


EB31 You win $ 5 if Participant B divide equally among all three participants or Participant B divide equally with Participant C only (composite event)
Le domande dovranno essere rappresentate come da immagini fornite, differendo a seconda del tipo di domanda (composite event o single event) tendendo conto dei differenti scaglioni di probabilita’ come vedi dalle immagini.


**AZIONE RICHIESTA**: Fornire le specifiche complete delle 12 domande per A, B, C prima di procedere con l'implementazione.

---

## 📄 9. Testi UI - OBBLIGATORI

### Headers:
- **OPTION 1**: Deve apparire esattamente come "OPTION 1" (tutto maiuscolo)
- **OPTION 2**: Deve apparire esattamente come "OPTION 2" (tutto maiuscolo)

### Colonne:
- **Colonna 1**: Etichetta "1" (per Option 1)
- **Colonna 2**: Etichetta "2" (per Option 2)

### Button:
- **OK Button**: Testo "OK" (tutto maiuscolo), colore rosso

---

## 🔒 REGOLE DI IMPLEMENTAZIONE

1. **TUTTI i testi sopra riportati sono OBBLIGATORI e NON MODIFICABILI**
2. **Nessun testo deve essere tradotto o modificato**
3. **I testi devono essere inclusi come costanti nel codice Python o come stringhe letterali**
4. **Qualsiasi sostituzione dinamica (es. "player on the left") deve rispettare il mapping ma mantenere la struttura del testo originale**
5. **Se un testo non è specificato qui, NON inventarlo - richiedere specifiche**

---

## 🎯 Task 1: Analisi e Documentazione delle 12 Domande MPL

### Obiettivo
Recuperare e documentare le esatte 12 domande per ogni partecipante (A, B, C) con la loro struttura (Single Event vs Composite Event).

### Azioni
1. **Recuperare le 12 domande specifiche** dai documenti originali o dalle specifiche fornite
2. **Classificare ogni domanda** come:
   - Single Event (es. EB1, EC1)
   - Composite Event (es. EB23, EC12)
3. **Documentare la struttura** di ogni domanda:
   - Target participant (A/B/C)
   - Eventi coinvolti
   - Testo esatto di Option 1

### Output Atteso
- File `docs/part2_questions_specification.md` con le 12 domande per A, B, C
- Mapping chiaro tra codici interni (EB1, EC23) e descrizioni

### Note
- Se le domande non sono disponibili nei documenti, richiedere all'utente le specifiche complete

---

## 🎯 Task 2: Creare Struttura App oTree per Parte 2

### Obiettivo
Creare la nuova app `bargaining_tdl_part2` seguendo la convenzione di naming del progetto.

### Azioni
1. **Creare directory**: `bargaining_tdl_part2/`
2. **Creare `__init__.py`** con struttura base:
   - Constants class
   - Subsession class
   - Group class (se necessario)
   - Player class con campi per le 12 risposte MPL
3. **Definire costanti**:
   - `PROBABILITIES_SINGLE_EVENT`: lista probabilità per Single Event (da screenshot)
   - `PROBABILITIES_COMPOSITE_EVENT`: lista probabilità per Composite Event (da screenshot)
   - `PRIZE_AMOUNT`: €5 (o £5 se richiesto dalle istruzioni)
   - `NUM_QUESTIONS_PER_PARTICIPANT`: 12

---

## 🎯 Task 2.1: Definire Costanti Testi Obbligatori

### Obiettivo
Definire tutte le costanti con i testi obbligatori all'inizio del file `__init__.py` per garantire che non vengano modificati.

### ⚠️ VINCOLI OBBLIGATORI
- **TUTTI i testi** devono essere copiati ESATTAMENTE dalla sezione "⚠️ SEZIONE CRITICA: TESTI ORIGINALI OBBLIGATORI"
- **NON MODIFICARE** neanche una virgola
- **USARE commenti** per indicare la fonte di ogni testo

### Costanti da Definire

```python
# ============================================================================
# TESTI OBBLIGATORI - NON MODIFICARE
# Fonte: Sezione "⚠️ SEZIONE CRITICA: TESTI ORIGINALI OBBLIGATORI"
# ============================================================================

# Testi delle Opzioni di Scelta Parte 1 (Sezione 📄 4)
EVENT_TEXT_EB1 = "Share only with the player on the right"
EVENT_TEXT_EB2 = "Share only with you"
EVENT_TEXT_EB3 = "Share with both you and the player on the right"
EVENT_TEXT_EC1 = "Share only with the player on the left"
EVENT_TEXT_EC2 = "Share only with you"
EVENT_TEXT_EC3 = "Share with both you and the player on the left"

# Mapping Eventi → Testi
EVENT_TO_TEXT = {
    'EB1': EVENT_TEXT_EB1,
    'EB2': EVENT_TEXT_EB2,
    'EB3': EVENT_TEXT_EB3,
    'EC1': EVENT_TEXT_EC1,
    'EC2': EVENT_TEXT_EC2,
    'EC3': EVENT_TEXT_EC3,
}

# Struttura Testo Option 1 (Sezione 📄 5)
OPTION1_SINGLE_TEMPLATE_LEFT = "You win €5 if the player on the left chose \"{event_text}\" (and nothing otherwise)."
OPTION1_SINGLE_TEMPLATE_RIGHT = "You win €5 if the player on the right chose \"{event_text}\" (and nothing otherwise)."
OPTION1_COMPOSITE_TEMPLATE_LEFT = "You win €5 if the player on the left chose \"{event_text_1}\" or \"{event_text_2}\" (and nothing otherwise)."
OPTION1_COMPOSITE_TEMPLATE_RIGHT = "You win €5 if the player on the right chose \"{event_text_1}\" or \"{event_text_2}\" (and nothing otherwise)."

# Struttura Testo Option 2 (Sezione 📄 6)
OPTION2_TEXT = "You win €5 with the following probability (and nothing otherwise)."

# Testo Reminder Parte 1 (Sezione 📄 3)
REMINDER_TEMPLATE = """We remind you of the following information regarding what you and {target_label} have declared to each other:
You said: {you_said}
{target_label} said: {target_said}"""

# Testi UI (Sezione 📄 9)
UI_OPTION1_HEADER = "OPTION 1"
UI_OPTION2_HEADER = "OPTION 2"
UI_COLUMN1_LABEL = "1"
UI_COLUMN2_LABEL = "2"
UI_OK_BUTTON_TEXT = "OK"

# Liste Probabilità (Sezione 📄 7)
PROBABILITIES_SINGLE_EVENT = [0, 1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 85, 100]
# PROBABILITIES_COMPOSITE_EVENT = [DA VERIFICARE DALL'SCREENSHOT]

# Istruzioni Parte 2 (Sezione 📄 2) - Da includere nel template HTML
# Il testo completo è troppo lungo per essere una costante, va incluso direttamente nel template
```

### Output Atteso
- File `__init__.py` con tutte le costanti definite all'inizio
- Commenti che indicano la fonte di ogni testo
- Testi identici a quelli della sezione obbligatoria

### File da Creare
```
bargaining_tdl_part2/
├── __init__.py
├── InstructionsPart2.html
├── MPLQuestion.html
└── ResultsPart2.html
```

### Output Atteso
- Struttura base dell'app funzionante
- Modelli dati definiti

---

## 🎯 Task 3: Definire Modello Dati Player per Parte 2

### Obiettivo
Creare i campi nel modello `Player` per salvare tutte le risposte MPL e i dati necessari.

### Campi da Aggiungere

#### Campi per le 12 Risposte MPL
```python
# Per ogni domanda (1-12), salvare:
mpl_question_1_switch_value = models.IntegerField()  # Valore di switch (0-100)
mpl_question_2_switch_value = models.IntegerField()
# ... fino a question_12

# Opzionale: salvare anche le scelte complete per validazione
mpl_question_1_choices = models.LongStringField()  # JSON con tutte le scelte
# ... per tutte le 12 domande
```

#### Campi per Dati Parte 1 (per riferimento)
```python
# Questi dati vengono letti da participant.vars o group, non salvati qui
# Ma potrebbero essere utili per debug/analisi
part1_decision_choice = models.StringField()  # Left/Right/Both
part1_signal_to_left = models.StringField()
part1_signal_to_right = models.StringField()
part1_signal_from_left = models.StringField()
part1_signal_from_right = models.StringField()
```

### Output Atteso
- Modello Player completo con tutti i campi necessari
- Documentazione dei campi

---

## 🎯 Task 4: Implementare Funzione di Mapping Left/Right

### Obiettivo
Creare funzioni helper per convertire i codici interni (A/B/C) in "player on the left" / "player on the right" basandosi sul ruolo del partecipante.

### Mapping da Implementare
```python
# Se subject = A (P1 nel gruppo):
#   B (P2) → player on the left
#   C (P3) → player on the right

# Se subject = B (P2 nel gruppo):
#   A (P1) → player on the left
#   C (P3) → player on the right

# Se subject = C (P3 nel gruppo):
#   A (P1) → player on the left
#   B (P2) → player on the right
```

### Funzioni da Creare
```python
def get_target_player_label(player: Player, target_code: str) -> str:
    """
    Converte un codice target (A/B/C) in "player on the left" o "player on the right"
    basandosi sul ruolo del player corrente nel gruppo.
    
    Args:
        player: Il player corrente
        target_code: 'A', 'B', o 'C' (codice interno)
    
    Returns:
        'player on the left' o 'player on the right'
    """
    pass

def get_participant_role_in_group(player: Player) -> str:
    """
    Determina il ruolo del player nel gruppo (A, B, o C).
    Basato sulla posizione nel gruppo (id 1, 2, o 3).
    """
    pass
```

### Output Atteso
- Funzioni helper testate e documentate
- Test unitari per verificare il mapping corretto

---

## 🎯 Task 5: Implementare Generazione Testi Option 1

### Obiettivo
Creare funzioni che generano il testo esatto di Option 1 per ogni domanda MPL, usando i dati della Parte 1 e il mapping left/right.

### ⚠️ VINCOLI OBBLIGATORI
- **USARE ESCLUSIVAMENTE** i testi della sezione "📄 4. Testi delle Opzioni di Scelta Parte 1 - OBBLIGATORI"
- **SEGUIRE ESATTAMENTE** la struttura della sezione "📄 5. Struttura Testo Option 1 - OBBLIGATORIA"
- **NON MODIFICARE** i testi in alcun modo

### Funzioni da Creare

#### Per Single Event
```python
def generate_option1_single_event(
    player: Player,
    target_code: str,
    event_code: str
) -> str:
    """
    Genera il testo di Option 1 per un Single Event.
    
    Esempio output:
    "You win €5 if the player on the left chose 'Share only with the player on the right' 
    (and nothing otherwise)."
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C' (chi ha fatto la scelta)
        event_code: Codice evento (es. 'EB1', 'EC1')
    
    Returns:
        Stringa con il testo completo di Option 1
    """
    pass
```

#### Per Composite Event
```python
def generate_option1_composite_event(
    player: Player,
    target_code: str,
    event_codes: list[str]
) -> str:
    """
    Genera il testo di Option 1 per un Composite Event (OR logico).
    
    Esempio output:
    "You win €5 if the player on the left chose 'Share only with the player on the right' 
    or 'Share with both you and the player on the right' (and nothing otherwise)."
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C'
        event_codes: Lista di codici evento (es. ['EB2', 'EB3'])
    
    Returns:
        Stringa con il testo completo di Option 1
    """
    pass
```

#### Mapping Eventi → Testi
**OBBLIGATORIO**: Usare ESATTAMENTE i testi della sezione "📄 4. Testi delle Opzioni di Scelta Parte 1 - OBBLIGATORI"

```python
# Questi testi sono OBBLIGATORI e NON MODIFICABILI
EVENT_TO_TEXT = {
    'EB1': "Share only with the player on the right",  # DA SEZIONE 📄 4
    'EB2': "Share only with you",  # DA SEZIONE 📄 4
    'EB3': "Share with both you and the player on the right",  # DA SEZIONE 📄 4
    'EC1': "Share only with the player on the left",  # DA SEZIONE 📄 4
    'EC2': "Share only with you",  # DA SEZIONE 📄 4
    'EC3': "Share with both you and the player on the left",  # DA SEZIONE 📄 4
}
```

### Output Atteso
- Funzioni che generano testi corretti per tutte le combinazioni
- Test per verificare la correttezza dei testi generati

---

## 🎯 Task 6: Implementare Caricamento Dati Parte 1

### Obiettivo
Creare funzioni che caricano e preparano i dati della Parte 1 per essere mostrati nelle MPL questions.

### ⚠️ VINCOLO CRITICO: SOLO LETTURA
**IMPORTANTE**: Questo task richiede SOLO la lettura dei dati esistenti da `bargaining_tdl_intro` e `bargaining_tdl_main`. 
**NON MODIFICARE** in alcun modo i file `bargaining_tdl_intro` o `bargaining_tdl_main`.
**NON SALVARE** dati aggiuntivi in `participant.vars` o nei modelli di intro/main.

### Dati da Caricare
Per ogni partecipante, recuperare (SOLO LETTURA):
- **Intenzione dichiarata** (signal_left, signal_right) - da `participant.vars` (salvati da intro)
- **Messaggi scambiati** (draft_history_left, draft_history_right) - da `participant.vars` (salvati da intro)
- **Scelte finali** (decision_choice) - dai campi Player del gruppo di main
- **Messaggi e segnali ricevuti** (received_history_left, received_signal_left, etc.) - dai campi Player del gruppo di main

### Note di Implementazione
- I dati di intro sono accessibili tramite `player.participant.vars`
- I dati di main sono accessibili tramite il gruppo di main (es. `player.in_round(1)` o tramite il gruppo della sessione)
- Per accedere ai dati degli altri player nel gruppo di main, usare `group.get_player_by_id(id)` per ottenere i player target

### Funzioni da Creare
```python
def load_part1_data_for_mpl(player: Player, target_code: str) -> dict:
    """
    Carica i dati della Parte 1 relativi a un target participant specifico.
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C' (il participant di cui si sta chiedendo la scelta)
    
    Returns:
        Dict con:
        - 'you_said': str (intenzione dichiarata al target)
        - 'target_said': str (intenzione dichiarata dal target)
        - 'target_decision': str (scelta finale del target: Left/Right/Both)
    """
    pass
```

### Output Atteso
- Funzioni di caricamento dati testate
- Gestione errori per dati mancanti

---

## 🎯 Task 7: Creare Pagina Istruzioni Parte 2

### Obiettivo
Creare la pagina HTML con le istruzioni complete della Parte 2, usando i testi originali forniti.

### ⚠️ VINCOLI OBBLIGATORI
- **USARE ESCLUSIVAMENTE** il testo della sezione "📄 2. Istruzioni Ufficiali Parte 2 - OBBLIGATORIE"
- **INCLUDERE TUTTO** il testo senza omissioni
- **NON MODIFICARE** neanche una virgola del testo originale

### Contenuti da Includere
1. **Testo introduttivo** (dalle istruzioni ufficiali - sezione 📄 2)
2. **Esempio di MPL** (con screenshot o descrizione)
3. **Spiegazione dello switch unico** (già inclusa nelle istruzioni)
4. **Istruzioni su come procedere** (già incluse nelle istruzioni)

### File
- `bargaining_tdl_part2/InstructionsPart2.html`

### Requisiti
- **NON modificare** i testi originali in inglese
- Includere tutti i contenuti dalle istruzioni ufficiali
- Formattazione chiara e leggibile

### Output Atteso
- Pagina HTML completa con tutte le istruzioni
- Testo identico alle istruzioni originali

---

## 🎯 Task 8: Implementare UI MPL Question (Single Event)

### Obiettivo
Creare il template HTML per una MPL question di tipo Single Event, replicando esattamente lo screenshot `single_event.png`.

### Requisiti UI

#### Layout
- **Left Panel**: Option 1 con:
  - Descrizione della scommessa
  - Reminder dei messaggi/scelte della Parte 1
- **Right Panel**: Option 2 con:
  - Lista probabilità (esatta sequenza dallo screenshot)
- **Center Columns**: Due colonne "1" e "2" con checkbox per ogni probabilità
- **OK Button**: In basso a destra (rosso)

#### Lista Probabilità Single Event
**OBBLIGATORIO**: Usare ESATTAMENTE la lista della sezione "📄 7. Liste Probabilità - OBBLIGATORIE"

Dallo screenshot: `0%, 1%, 2%, 5%, 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50%, 55%, 60%, 65%, 70%, 75%, 85%, 100%`

#### Funzionalità JavaScript
- **Single Switch Logic**: Click su una probabilità seleziona automaticamente:
  - Option 1 per tutte le probabilità < switch point
  - Option 2 per tutte le probabilità >= switch point
- **OK Button**: Appare solo dopo che tutte le righe hanno una selezione
- **Validazione**: Non permettere di procedere senza selezione completa

### File
- `bargaining_tdl_part2/MPLQuestion.html` (template riutilizzabile)

### Output Atteso
- UI identica allo screenshot
- Logica di switch funzionante
- Validazione completa

---

## 🎯 Task 9: Implementare UI MPL Question (Composite Event)

### Obiettivo
Creare il template HTML per una MPL question di tipo Composite Event, replicando esattamente lo screenshot `Composite_event.png`.

### Differenze rispetto a Single Event
- **Lista probabilità diversa**: Verificare dallo screenshot esatto
- **Testo Option 1**: Include "OR" tra due eventi
- **Layout**: Stesso ma con testo diverso

### Lista Probabilità Composite Event
Da verificare dallo screenshot fornito (potrebbe essere diversa da Single Event)

### File
- Stesso template `MPLQuestion.html` con logica condizionale per tipo evento

### Output Atteso
- UI identica allo screenshot Composite Event
- Gestione corretta del testo con "OR"

---

## 🎯 Task 10: Implementare Logica Single Switch (Backend)

### Obiettivo
Implementare la logica lato server per gestire lo switch unico e salvare il valore di switch.

### Funzionalità

#### Salvataggio Switch Value
```python
def save_mpl_response(player: Player, question_num: int, switch_value: int):
    """
    Salva il valore di switch per una domanda MPL.
    
    Args:
        player: Player corrente
        question_num: Numero domanda (1-12)
        switch_value: Valore probabilità a partire dal quale si passa a Option 2 (0-100)
    """
    # Esempio: se switch_value = 85, significa che:
    # - Option 1 è preferita per probabilità < 85%
    # - Option 2 è preferita per probabilità >= 85%
    pass
```

#### Validazione
- Verificare che switch_value sia un valore valido (0-100)
- Verificare che corrisponda a una probabilità nella lista

### Output Atteso
- Funzioni di salvataggio testate
- Validazione robusta

---

## 🎯 Task 11: Implementare Logica Single Switch (Frontend JavaScript)

### Obiettivo
Implementare la logica JavaScript per gestire lo switch unico nell'interfaccia utente.

### Funzionalità JavaScript

```javascript
// Pseudocodice
function handleProbabilityClick(probability, option) {
    // Se click su Option 2 a probabilità p:
    //   - Seleziona Option 2 per tutte le probabilità >= p
    //   - Seleziona Option 1 per tutte le probabilità < p
    
    // Se click su Option 1 a probabilità p:
    //   - Seleziona Option 1 per tutte le probabilità <= p
    //   - Seleziona Option 2 per tutte le probabilità > p
    
    // Aggiorna visualizzazione
    // Abilita OK button se tutte le righe hanno selezione
}
```

### Requisiti
- **Single Switch**: Solo un punto di switch possibile
- **Visual Feedback**: Checkbox selezionati/non selezionati
- **OK Button**: Abilitato solo quando tutte le righe hanno selezione
- **Reset**: Possibilità di cambiare selezione prima di OK

### Output Atteso
- JavaScript funzionante e testato
- UX fluida e intuitiva

---

## 🎯 Task 12: Generare Sequenza delle 12 Domande

### Obiettivo
Creare la logica che genera la sequenza corretta delle 12 domande MPL per ogni partecipante.

### Funzionalità

#### Determinazione Ruolo
```python
def get_participant_role(player: Player) -> str:
    """
    Determina se il player è A, B, o C nel gruppo.
    Basato su player.id_in_group (1, 2, o 3).
    """
    pass
```

#### Generazione Domande
```python
def generate_mpl_questions(player: Player) -> list[dict]:
    """
    Genera la lista delle 12 domande MPL per il player.
    
    Returns:
        Lista di dict, ognuno con:
        - 'question_num': int (1-12)
        - 'type': 'single' o 'composite'
        - 'target_code': str ('A', 'B', o 'C')
        - 'event_codes': list[str] (es. ['EB1'] o ['EB2', 'EB3'])
        - 'option1_text': str (testo completo)
        - 'reminder_text': str (reminder Parte 1)
        - 'probabilities': list[int] (lista probabilità)
    """
    pass
```

#### Definizione Domande per Ruolo
```python
# Esempio struttura (da completare con le 12 domande reali)
QUESTIONS_FOR_A = [
    {'type': 'single', 'target': 'B', 'event': 'EB1', ...},
    {'type': 'single', 'target': 'B', 'event': 'EB2', ...},
    {'type': 'composite', 'target': 'B', 'events': ['EB2', 'EB3'], ...},
    # ... 12 domande totali
]

QUESTIONS_FOR_B = [...]
QUESTIONS_FOR_C = [...]
```

### Output Atteso
- Funzione che genera correttamente le 12 domande
- Test per verificare la correttezza della sequenza

---

## 🎯 Task 13: Creare Page Sequence e Routing

### Obiettivo
Implementare il flusso completo delle pagine della Parte 2.

### Page Sequence
```python
page_sequence = [
    InstructionsPart2,
    MPLQuestion1,
    MPLQuestion2,
    # ... fino a MPLQuestion12
    ResultsPart2
]
```

### Implementazione Dinamica
- Creare una classe `MPLQuestion` generica che accetta `question_num` come parametro
- Usare `vars_for_template` per passare i dati specifici di ogni domanda

### Output Atteso
- Page sequence funzionante
- Navigazione corretta tra le 12 domande
- Possibilità di tornare indietro (se richiesto) o blocco dopo OK

---

## 🎯 Task 14: Implementare Pagina Results Part 2

### Obiettivo
Creare la pagina di riepilogo finale della Parte 2.

### Contenuti
- Riepilogo delle 12 risposte (switch values)
- Eventuale calcolo di metriche (se richiesto)
- Messaggio di completamento

### File
- `bargaining_tdl_part2/ResultsPart2.html`

### Output Atteso
- Pagina di risultati completa
- Dati salvati correttamente nel database

---

## 🎯 Task 15: Integrare Parte 2 in settings.py

### Obiettivo
Aggiungere la nuova app alla sequenza dell'esperimento.

### ⚠️ NOTA: Solo Aggiunta, Non Modifica
Questa modifica aggiunge solo `bargaining_tdl_part2` alla sequenza esistente. 
**NON modifica** la configurazione di `bargaining_tdl_intro` o `bargaining_tdl_main`.

### Modifiche a `settings.py`
```python
SESSION_CONFIGS = [
    dict(
        name='bargaining_tdl',
        display_name="Bargaining Game (TDL + Async)",
        app_sequence=[
            'bargaining_tdl_intro', 
            'bargaining_tdl_main',
            'bargaining_tdl_part2'  # AGGIUNTO
        ],
        num_demo_participants=6,
    ),
]
```

### Output Atteso
- Settings aggiornati
- Sequenza completa funzionante

---

## 🎯 Task 16: Testing e Validazione

### Obiettivo
Testare l'intera implementazione della Parte 2.

### Test da Eseguire

#### Test Funzionali
1. **Caricamento Dati Parte 1**: Verificare che i dati vengano caricati correttamente
2. **Mapping Left/Right**: Verificare che il mapping sia corretto per tutti i ruoli
3. **Generazione Testi**: Verificare che i testi Option 1 siano corretti
4. **Single Switch**: Verificare che lo switch funzioni correttamente
5. **Salvataggio**: Verificare che i switch values vengano salvati correttamente

#### Test UI
1. **Layout Single Event**: Confrontare con screenshot
2. **Layout Composite Event**: Confrontare con screenshot
3. **Liste Probabilità**: Verificare che siano identiche agli screenshot
4. **OK Button**: Verificare che appaia solo dopo selezione completa

#### Test End-to-End
1. **Flusso Completo**: Da Parte 1 a Parte 2
2. **12 Domande**: Verificare che tutte le 12 domande vengano mostrate
3. **Dati Persistenza**: Verificare che i dati vengano salvati nel database

### Output Atteso
- Suite di test completa
- Tutti i test passano
- Documentazione dei test

---

## 🎯 Task 17: Documentazione e Cleanup

### Obiettivo
Completare la documentazione e fare cleanup del codice.

### Azioni
1. **Documentare funzioni complesse** con docstring
2. **Aggiungere commenti** dove necessario
3. **Verificare conformità** con le regole del progetto
4. **Rimuovere codice di debug** o commentato
5. **Aggiornare README** se presente

### Output Atteso
- Codice pulito e documentato
- Pronto per produzione

---

## 📊 Riepilogo Task

| # | Task | Priorità | Dipendenze |
|---|------|----------|------------|
| 1 | Analisi 12 Domande MPL | 🔴 Alta | - |
| 2 | Creare Struttura App | 🔴 Alta | - |
| 2.1 | Definire Costanti Testi Obbligatori | 🔴 Alta | 2 |
| 3 | Modello Dati Player | 🔴 Alta | 2, 2.1 |
| 4 | Mapping Left/Right | 🔴 Alta | 2 |
| 5 | Generazione Testi Option 1 | 🔴 Alta | 4 |
| 6 | Caricamento Dati Parte 1 | 🔴 Alta | 2 |
| 7 | Pagina Istruzioni | 🟡 Media | 2 |
| 8 | UI Single Event | 🔴 Alta | 2, 5, 6 |
| 9 | UI Composite Event | 🔴 Alta | 8 |
| 10 | Logica Switch Backend | 🔴 Alta | 3 |
| 11 | Logica Switch Frontend | 🔴 Alta | 8, 9 |
| 12 | Generazione 12 Domande | 🔴 Alta | 1, 4, 5 |
| 13 | Page Sequence | 🔴 Alta | 12 |
| 14 | Pagina Results | 🟡 Media | 3 |
| 15 | Integrazione settings.py | 🟡 Media | 13 |
| 16 | Testing | 🔴 Alta | 15 |
| 17 | Documentazione | 🟢 Bassa | 16 |

---

## ⚠️ Note Importanti

1. **Testi Originali**: NON modificare mai i testi originali in inglese - RIFERIRSI ALLA SEZIONE "⚠️ SEZIONE CRITICA: TESTI ORIGINALI OBBLIGATORI"
2. **Screenshot**: La UI deve essere identica agli screenshot forniti
3. **Switch Value**: Salvare sempre il valore esatto della probabilità di switch
4. **Mapping**: Usare sempre "player on the left" / "player on the right" nell'UI
5. **Dati Parte 1**: Tutti i dati devono essere disponibili e mostrati correttamente
6. **Costanti nel Codice**: Tutti i testi obbligatori devono essere definiti come costanti Python all'inizio del file `__init__.py` per garantire che non vengano modificati accidentalmente

---

## 🚀 Ordine di Implementazione Consigliato

1. **Fase 1 - Fondamenta** (Task 1-6): Preparare struttura e dati
2. **Fase 2 - UI Base** (Task 7-9): Creare interfacce
3. **Fase 3 - Logica** (Task 10-12): Implementare funzionalità core
4. **Fase 4 - Integrazione** (Task 13-15): Collegare tutto insieme
5. **Fase 5 - Quality** (Task 16-17): Test e documentazione
