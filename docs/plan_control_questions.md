# Piano di Implementazione: Control Questions

## Obiettivo
Aggiungere una sezione di control questions tra `InstructionsPart1` e `ChatAndSignals` per verificare che l'utente abbia compreso le istruzioni. L'utente deve rispondere correttamente a tutte le domande per procedere, altrimenti viene reindirizzato a una pagina di saluti che termina l'esperimento.

---

## Task 1: Definire la struttura dati nel modello Player

### File: `bargaining_tdl_intro/__init__.py`

**Azione**: Aggiungere campi nel modello `Player` per memorizzare le risposte alle control questions.

**Campi da aggiungere**:
- `example1_earnings_you`: StringField - guadagni del giocatore nell'Example 1 (con choices)
- `example1_earnings_left`: StringField - guadagni del giocatore a sinistra nell'Example 1 (con choices)
- `example1_earnings_right`: StringField - guadagni del giocatore a destra nell'Example 1 (con choices)
- `example2_earnings_you`: StringField - guadagni del giocatore nell'Example 2 (con choices)
- `example2_earnings_left`: StringField - guadagni del giocatore a sinistra nell'Example 2 (con choices)
- `example2_earnings_right`: StringField - guadagni del giocatore a destra nell'Example 2 (con choices)
- `example3_earnings_you`: StringField - guadagni del giocatore nell'Example 3 (con choices)
- `example3_earnings_left`: StringField - guadagni del giocatore a sinistra nell'Example 3 (con choices)
- `example3_earnings_right`: StringField - guadagni del giocatore a destra nell'Example 3 (con choices)
- `payoff_determination`: StringField - risposta alla domanda sul payoff totale (con choices)

**Note**:
- Per tutte le domande numeriche, usare `StringField` con `widget=widgets.RadioSelect` e choices predefinite (1 corretta + 2 sbagliate)
- Per la domanda finale, usare `StringField` con `widget=widgets.RadioSelect` e choices che includono la risposta corretta + 3 risposte sbagliate
- Le risposte sbagliate sono specificate nella sezione "Risposte Sbagliate Predefinite" più sotto

---

## Task 2: Creare la pagina ControlQuestions

### File: `bargaining_tdl_intro/__init__.py`

**Azione**: Creare una nuova classe `ControlQuestions` che estende `Page`.

**Caratteristiche**:
- `form_model = 'player'`
- `form_fields` deve includere tutti i campi definiti nel Task 1
- Implementare `vars_for_template()` per passare:
  - Gli scenari degli esempi (testo descrittivo)
  - Le opzioni per le domande a scelta multipla (per la domanda finale)
- Implementare `before_next_page()` per:
  - Validare tutte le risposte
  - Se tutte corrette: permettere di procedere
  - Se almeno una sbagliata: impostare un flag per reindirizzare alla pagina di saluti

**Logica di validazione**:
```python
def check_all_answers_correct(player):
    correct = (
        player.example1_earnings_you == "6" and
        player.example1_earnings_left == "0" and
        player.example1_earnings_right == "6" and
        player.example2_earnings_you == "4" and
        player.example2_earnings_left == "4" and
        player.example2_earnings_right == "4" and
        player.example3_earnings_you == "0" and
        player.example3_earnings_left == "0" and
        player.example3_earnings_right == "0" and
        player.payoff_determination == "I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3."
    )
    return correct
```

**Note**: I valori sono stringhe perché i campi sono `StringField` con choices.

**⚠️ IMPORTANTE**: 
- **NON** usare `app_after_this_page()` su `ControlQuestions` (vedi Problema 2 nella sezione "Problemi Comuni")
- Usare solo `before_next_page()` per salvare il flag in `participant.vars`
- La logica di reindirizzamento viene gestita con `is_displayed()` nelle pagine successive (vedi Task 7)

---

## Task 3: Creare il template HTML per ControlQuestions

### File: `bargaining_tdl_intro/ControlQuestions.html`

**Azione**: Creare il template HTML per visualizzare le control questions.

**Struttura**:
1. **Titolo**: "Control Questions"
2. **Introduzione**: Breve testo che spiega che devono rispondere correttamente a tutte le domande per procedere
3. **Example 1**:
   - Testo dello scenario
   - 3 campi radio (Your earnings, Left player earnings, Right player earnings)
   - Ogni campo ha 3 opzioni (1 corretta + 2 sbagliate predefinite)
4. **Example 2**: Stessa struttura
5. **Example 3**: Stessa struttura (solo TDL)
6. **Domanda finale sul payoff**:
   - Testo della domanda
   - Radio buttons con 4 opzioni (1 corretta + 3 sbagliate predefinite)
7. **Pulsante Next**: Standard oTree next button

**Styling**:
- Usare stile coerente con le altre pagine
- Evidenziare chiaramente ogni scenario
- Formattare i radio buttons in modo chiaro e leggibile

**Note**: Tutte le opzioni sono già definite nei campi del modello con le choices, quindi il template userà semplicemente `{{ formfield }}` per ogni campo.

---

## Task 4: Creare la pagina Goodbye

### File: `bargaining_tdl_intro/__init__.py`

**Azione**: Creare una classe `Goodbye` che estende `Page`.

**Caratteristiche**:
- Non ha form fields
- Mostra un messaggio di saluto
- Termina l'esperimento per il partecipante

**Note**: Usare `app_after_this_page` per terminare la sequenza dell'app.

---

## Task 5: Creare il template HTML per Goodbye

### File: `bargaining_tdl_intro/Goodbye.html`

**Azione**: Creare un template semplice con messaggio di saluto.

**Contenuto**:
- Messaggio che ringrazia per la partecipazione
- Spiegazione che l'esperimento è terminato
- Eventuali istruzioni per il pagamento (se necessario)

---

## Task 6: Aggiornare page_sequence

### File: `bargaining_tdl_intro/__init__.py`

**Azione**: Modificare `page_sequence` per includere le nuove pagine nell'ordine corretto.

**Nuova sequenza**:
```python
page_sequence = [
    Welcome,
    InstructionsPart1,
    ControlQuestions,  # NUOVA PAGINA
    Goodbye,           # NUOVA PAGINA - mostrata solo se risposte sbagliate
    ChatAndSignals     # Mostrata solo se risposte corrette
]
```

**Logica condizionale**:
- `Goodbye` viene mostrata solo se `failed_control_questions == True` (gestito con `is_displayed()`)
- `ChatAndSignals` viene mostrata solo se `failed_control_questions == False` (gestito con `is_displayed()`)
- **NON** usare `app_after_this_page()` su `ControlQuestions` (vedi Problema 2 nella sezione "Problemi Comuni")

---

## Task 7: Implementare la logica di reindirizzamento

### File: `bargaining_tdl_intro/__init__.py`

**Azione**: Implementare la logica per reindirizzare a `Goodbye` se le risposte sono sbagliate.

**Approccio CORRETTO** (basato su problemi riscontrati):
- **NON** usare `app_after_this_page()` su `ControlQuestions` (pagina intermedia)
- Salvare un flag in `participant.vars` in `before_next_page()` di `ControlQuestions`
- Usare `is_displayed()` su `Goodbye` e `ChatAndSignals` per controllare il flag
- Usare `app_after_this_page()` solo su `Goodbye` per terminare l'esperimento

**Implementazione**:
```python
# In ControlQuestions
@staticmethod
def before_next_page(player, timeout_happened):
    is_correct = check_all_answers_correct(player)
    player.participant.vars['failed_control_questions'] = not is_correct
    # NON implementare app_after_this_page() qui

# In Goodbye
@staticmethod
def is_displayed(player):
    failed = player.participant.vars.get('failed_control_questions')
    if failed is None:
        return False
    return failed

@staticmethod
def app_after_this_page(player, upcoming_apps):
    return []  # Termina l'esperimento

# In ChatAndSignals
@staticmethod
def is_displayed(player):
    failed = player.participant.vars.get('failed_control_questions')
    if failed is None:
        return True  # Retrocompatibilità
    return not failed
    # NON implementare app_after_this_page() qui
```

**⚠️ IMPORTANTE**: 
- `app_after_this_page()` su pagine intermedie può causare `InvalidAppError`
- `is_displayed()` viene chiamato PRIMA di `before_next_page()`, quindi NON chiamare `check_all_answers_correct()` direttamente in `is_displayed()`
- Usare sempre un flag in `participant.vars` per comunicare tra pagine

---

## Task 8: Testare l'implementazione

### File: Test manuale e/o `bargaining_tdl_intro/tests.py` (se esiste)

**Azioni**:
1. Testare che tutte le risposte corrette permettano di procedere
2. Testare che almeno una risposta sbagliata reindirizzi a Goodbye
3. Testare che la pagina Goodbye termini correttamente l'esperimento
4. Verificare che tutte le opzioni siano visualizzate correttamente
5. Testare la visualizzazione su diversi browser

**Casi di test**:
- Tutte le risposte corrette → procede a ChatAndSignals
- Una risposta sbagliata → va a Goodbye
- Tutte le risposte sbagliate → va a Goodbye
- Risposte parziali → validazione corretta

---

## Dettagli delle Domande e Risposte

### Example 1
**Scenario**: "Imagine that you chose 'Share only with the player on the right', that the player on the left chose 'Share with both you and the player on the right', and that the player on the right chose 'Share only with you'."

**Domanda 1**: What would your earnings be for Part 1 in this case?
- ✅ **Risposta corretta**: £6
- ❌ Risposta sbagliata 1: £4
- ❌ Risposta sbagliata 2: £0

**Domanda 2**: What would the earnings for the player on the left be for Part 1 in this case?
- ✅ **Risposta corretta**: £0
- ❌ Risposta sbagliata 1: £4
- ❌ Risposta sbagliata 2: £6

**Domanda 3**: What would the earnings for the player on the right be for Part 1 in this case?
- ✅ **Risposta corretta**: £6
- ❌ Risposta sbagliata 1: £4
- ❌ Risposta sbagliata 2: £0

### Example 2
**Scenario**: "Imagine that you chose 'Share with both the player on the left and the player on the right', that the player on the left chose 'Share only with the player on the right', and that the player on the right chose 'Share with both you and the player on the left'."

**Domanda 1**: What would your earnings be for Part 1 in this case?
- ✅ **Risposta corretta**: £4
- ❌ Risposta sbagliata 1: £6
- ❌ Risposta sbagliata 2: £0

**Domanda 2**: What would the earnings for the player on the left be for Part 1 in this case?
- ✅ **Risposta corretta**: £4
- ❌ Risposta sbagliata 1: £6
- ❌ Risposta sbagliata 2: £0

**Domanda 3**: What would the earnings for the player on the right be for Part 1 in this case?
- ✅ **Risposta corretta**: £4
- ❌ Risposta sbagliata 1: £6
- ❌ Risposta sbagliata 2: £0

### Example 3 (solo TDL)
**Scenario**: "Imagine that you chose 'Share with both the player on the left and the player on the right', that the player on the left chose 'Share only with you', and that the player on the right chose 'Share only with the player on the left'."

**Domanda 1**: What would your earnings be for Part 1 in this case?
- ✅ **Risposta corretta**: £0
- ❌ Risposta sbagliata 1: £4
- ❌ Risposta sbagliata 2: £6

**Domanda 2**: What would the earnings for the player on the left be for Part 1 in this case?
- ✅ **Risposta corretta**: £0
- ❌ Risposta sbagliata 1: £4
- ❌ Risposta sbagliata 2: £6

**Domanda 3**: What would the earnings for the player on the right be for Part 1 in this case?
- ✅ **Risposta corretta**: £0
- ❌ Risposta sbagliata 1: £4
- ❌ Risposta sbagliata 2: £6

### Domanda Finale
**Testo**: "Excluding the participation fee of £2, how will your total payoff be determined in this experiment?"

**Risposta corretta**: ✅ "I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3."

**Risposte sbagliate**:
- ❌ "I will only get paid for one of the following parts: Part 1, Part 2, or Part 3."
- ❌ "I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment."
- ❌ "I don't know."

---

## Risposte Sbagliate Predefinite - Definizione Choices

### Per i campi nel modello Player:

**Example 1 - Your earnings** (`example1_earnings_you`):
```python
choices=[
    ['6', '£6'],  # Corretta
    ['4', '£4'],  # Sbagliata 1
    ['0', '£0'],  # Sbagliata 2
]
```

**Example 1 - Left player earnings** (`example1_earnings_left`):
```python
choices=[
    ['0', '£0'],  # Corretta
    ['4', '£4'],  # Sbagliata 1
    ['6', '£6'],  # Sbagliata 2
]
```

**Example 1 - Right player earnings** (`example1_earnings_right`):
```python
choices=[
    ['6', '£6'],  # Corretta
    ['4', '£4'],  # Sbagliata 1
    ['0', '£0'],  # Sbagliata 2
]
```

**Example 2 - Your earnings** (`example2_earnings_you`):
```python
choices=[
    ['4', '£4'],  # Corretta
    ['6', '£6'],  # Sbagliata 1
    ['0', '£0'],  # Sbagliata 2
]
```

**Example 2 - Left player earnings** (`example2_earnings_left`):
```python
choices=[
    ['4', '£4'],  # Corretta
    ['6', '£6'],  # Sbagliata 1
    ['0', '£0'],  # Sbagliata 2
]
```

**Example 2 - Right player earnings** (`example2_earnings_right`):
```python
choices=[
    ['4', '£4'],  # Corretta
    ['6', '£6'],  # Sbagliata 1
    ['0', '£0'],  # Sbagliata 2
]
```

**Example 3 - Your earnings** (`example3_earnings_you`):
```python
choices=[
    ['0', '£0'],  # Corretta
    ['4', '£4'],  # Sbagliata 1
    ['6', '£6'],  # Sbagliata 2
]
```

**Example 3 - Left player earnings** (`example3_earnings_left`):
```python
choices=[
    ['0', '£0'],  # Corretta
    ['4', '£4'],  # Sbagliata 1
    ['6', '£6'],  # Sbagliata 2
]
```

**Example 3 - Right player earnings** (`example3_earnings_right`):
```python
choices=[
    ['0', '£0'],  # Corretta
    ['4', '£4'],  # Sbagliata 1
    ['6', '£6'],  # Sbagliata 2
]
```

**Payoff determination** (`payoff_determination`):
```python
choices=[
    ['I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.', 
     'I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.'],  # Corretta
    ['I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.', 
     'I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.'],  # Sbagliata 1
    ['I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment.', 
     'I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment.'],  # Sbagliata 2
    ["I don't know.", "I don't know."],  # Sbagliata 3
]
```

---

## Note Implementative

1. **Importante**: Tutte le risposte sbagliate sono già definite e hardcoded nel modello
2. **Valuta**: Randomizzare l'ordine delle opzioni nelle domande a scelta multipla per evitare bias (usare `random.shuffle()` sulle choices prima di passarle al campo)
3. **Valuta**: Mostrare feedback immediato se possibile (ma non obbligatorio)
4. **Importante**: Per Example 3, considerare solo TDL come specificato
5. **Nota**: I valori sono salvati come stringhe nei campi `StringField`, quindi la validazione confronta stringhe (es. `"6"` invece di `6`)

---

## Problemi Comuni e Soluzioni (Basati su Implementazione Reale)

### ⚠️ Problema 1: `is_displayed()` viene chiamato prima che i dati siano salvati

**Sintomo**: Anche rispondendo correttamente, l'utente viene reindirizzato a `Goodbye`.

**Causa**: `is_displayed()` viene chiamato PRIMA di `before_next_page()`, quindi quando `Goodbye.is_displayed()` chiama `check_all_answers_correct(player)`, i dati del form non sono ancora stati salvati nel database.

**Soluzione**: 
- **NON** chiamare `check_all_answers_correct()` direttamente in `is_displayed()`
- Salvare un flag in `participant.vars` in `before_next_page()` di `ControlQuestions`
- Usare il flag in `is_displayed()` invece della funzione di validazione

**Implementazione corretta**:
```python
# In ControlQuestions.before_next_page()
@staticmethod
def before_next_page(player, timeout_happened):
    is_correct = check_all_answers_correct(player)
    player.participant.vars['failed_control_questions'] = not is_correct

# In Goodbye.is_displayed()
@staticmethod
def is_displayed(player):
    failed = player.participant.vars.get('failed_control_questions')
    if failed is None:
        return False  # Flag non ancora impostato
    return failed

# In ChatAndSignals.is_displayed()
@staticmethod
def is_displayed(player):
    failed = player.participant.vars.get('failed_control_questions')
    if failed is None:
        return True  # Retrocompatibilità
    return not failed
```

---

### ⚠️ Problema 2: `InvalidAppError` quando le risposte sono corrette

**Sintomo**: Errore `InvalidAppError: "['bargaining_tdl_main']" is not in the upcoming_apps list` quando si risponde correttamente.

**Causa**: `app_after_this_page()` su una pagina intermedia (non ultima dell'app) che restituisce `upcoming_apps` può causare errori.

**Soluzione**: 
- **NON** usare `app_after_this_page()` su `ControlQuestions` (pagina intermedia)
- Usare `app_after_this_page()` solo su `Goodbye` (per terminare l'esperimento)
- Lasciare che oTree gestisca automaticamente il passaggio all'app successiva quando finisce l'app corrente

**Implementazione corretta**:
```python
# ControlQuestions - NON implementare app_after_this_page()
# Solo before_next_page() per salvare il flag

# Goodbye - implementare app_after_this_page() per terminare
@staticmethod
def app_after_this_page(player, upcoming_apps):
    return []  # Termina l'esperimento

# ChatAndSignals - NON implementare app_after_this_page()
# oTree gestirà automaticamente il passaggio all'app successiva
```

---

### ⚠️ Problema 3: L'utente riesce a bypassare i controlli rimuovendo `disabled` dal pulsante

**Sintomo**: L'utente rimuove `disabled` dal pulsante Next in `Goodbye` e riesce a procedere alla waiting room.

**Causa**: I controlli JavaScript possono essere bypassati modificando il DOM.

**Soluzione**: Implementare controlli a più livelli:
1. **Livello 1**: `app_after_this_page()` in `Goodbye` termina l'esperimento
2. **Livello 2**: JavaScript previene la navigazione
3. **Livello 3**: Aggiungere pagina `ExperimentTerminated` nell'app successiva come fallback
4. **Livello 4**: Tutte le pagine dell'app successiva controllano il flag

**Implementazione corretta**:
```python
# In bargaining_tdl_main/__init__.py
class ExperimentTerminated(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('failed_control_questions', False)
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return []  # Termina l'esperimento

# Aggiungere all'inizio di page_sequence
page_sequence = [
    ExperimentTerminated,  # Prima pagina - controlla il flag
    GroupingWaitPage,
    # ... altre pagine
]

# In tutte le altre pagine
@staticmethod
def is_displayed(player):
    return not player.participant.vars.get('failed_control_questions', False)
```

**JavaScript in Goodbye.html**:
```javascript
// Rimuovi il pulsante dal DOM
setTimeout(function() {
    if (nextButton && nextButton.parentNode) {
        nextButton.parentNode.removeChild(nextButton);
    }
}, 100);

// Previeni submit del form
form.addEventListener('submit', function(e) {
    e.preventDefault();
    return false;
}, true);
```

---

### ⚠️ Problema 4: Validazione non gestisce campi vuoti/None

**Sintomo**: La validazione fallisce anche se l'utente ha risposto correttamente.

**Causa**: Se un campo non è stato compilato, il valore è `None` o stringa vuota, e il confronto fallisce.

**Soluzione**: Verificare che tutti i campi siano compilati prima di validare i valori.

**Implementazione corretta**:
```python
def check_all_answers_correct(player):
    # Verifica che tutti i campi siano stati compilati
    if (not player.example1_earnings_you or 
        not player.example1_earnings_left or 
        not player.example1_earnings_right or
        # ... altri campi
        not player.payoff_determination):
        return False
    
    # Poi valida i valori
    correct = (
        player.example1_earnings_you == "6" and
        # ... resto della validazione
    )
    return correct
```

---

### ✅ Best Practices Implementate

1. **Flag in participant.vars**: Usare sempre un flag in `participant.vars` invece di chiamare direttamente la funzione di validazione in `is_displayed()`

2. **app_after_this_page() solo su pagine finali**: Usare `app_after_this_page()` solo su pagine che terminano l'esperimento, non su pagine intermedie

3. **Controlli multipli**: Implementare controlli a più livelli per prevenire il bypass:
   - JavaScript per prevenire la navigazione
   - `app_after_this_page()` per terminare l'esperimento
   - Pagina di fallback nell'app successiva
   - `is_displayed()` su tutte le pagine successive

4. **Validazione robusta**: Verificare sempre che i campi siano compilati prima di validare i valori

5. **Gestione del flag None**: Controllare sempre se il flag è `None` prima di usarlo in `is_displayed()`

---

## Ordine di Implementazione Consigliato

1. Task 1: Definire struttura dati con tutte le choices predefinite
2. Task 2: Creare classe ControlQuestions con validazione (⚠️ NON usare `app_after_this_page()` qui)
3. Task 3: Creare template ControlQuestions.html
4. Task 4: Creare classe Goodbye
5. Task 5: Creare template Goodbye.html (con JavaScript per prevenire bypass)
6. Task 6: Aggiornare page_sequence (includere Goodbye)
7. Task 7: Implementare logica reindirizzamento (usare flag in `participant.vars` e `is_displayed()`)
8. **Task 8.5**: Aggiungere pagina `ExperimentTerminated` nell'app successiva (`bargaining_tdl_main`) come fallback
9. **Task 8.6**: Aggiungere controlli `is_displayed()` su tutte le pagine dell'app successiva
10. Task 8: Testare (includere test per bypass JavaScript)

---

## File da Modificare/Creare

### File Esistenti da Modificare:
- `bargaining_tdl_intro/__init__.py`

### File Nuovi da Creare:
- `bargaining_tdl_intro/ControlQuestions.html`
- `bargaining_tdl_intro/Goodbye.html`
- `bargaining_tdl_main/ExperimentTerminated.html` (pagina di fallback nell'app successiva)

### File da Modificare (App Successiva):
- `bargaining_tdl_main/__init__.py` (aggiungere `ExperimentTerminated` e controlli `is_displayed()` su tutte le pagine)
