# Piano Esecutivo: Implementazione Part 3

## 📋 Overview

Implementare la **Parte 3** dell'esperimento (Three-Person Dictator Game) seguendo fedelmente il documento `part3_prompt.md`. La Part 3 è un task individuale per l'utente; a posteriori lo sperimentatore creerà il gruppo con una nuova triade.

**Obiettivo**: Creare il flusso completo della Part 3 mantenendo piena coerenza con Part 1 e Part 2, preservando tutti i testi originali.

---

## ⚠️ PRINCIPI FONDAMENTALI

1. **NON MODIFICARE** testi originali (paper, istruzioni, control questions)
2. **NON ALTERARE** il flusso esistente di Part 1 e Part 2
3. **PRESERVARE** la struttura Summary + Control Questions come nelle parti precedenti
4. **MANTENERE** coerenza con il pattern implementativo già stabilito
5. **TASK INDIVIDUALE**: Non serve creare gruppi in oTree - ogni partecipante fa la scelta individualmente

---

## 🎯 Flusso della Part 3

Il flusso completo della Parte 3 deve essere:

1. **Instructions for Part 3** (NUOVA PAGINA)
2. **Summary** (NUOVA PAGINA)
3. **Control Questions for Part 3** (NUOVA PAGINA con validazione)
4. **Thank You Page** (NUOVA PAGINA - mostrata solo se validazione fallisce)
5. **Decision Screen** (NUOVA PAGINA)
6. **Payoff Page** (NUOVA PAGINA - finale, mostra payoff dell'esperimento)

---

## 📦 Task 1: Creare Struttura Base App

### 1.1 Creare Cartella `bargaining_tdl_part3/`
- Creare directory seguendo la convenzione di naming (`bargaining_tdl_*`)
- Creare file `__init__.py` con struttura base oTree

### 1.2 Configurare Classi Base
- `C(BaseConstants)`: NAME_IN_URL = 'bargaining_tdl_part3', PLAYERS_PER_GROUP = None, NUM_ROUNDS = 1
- `Subsession(BaseSubsession)`: vuota
- `Group(BaseGroup)`: vuota (non serve gruppo per task individuale)
- `Player(BasePlayer)`: campi per:
  - Scelta del partecipante (decision)
  - Risposte alle control questions
  - Flag per validazione control questions

### 1.3 Campi Player Necessari
```python
# Decision
decision = models.StringField(
    choices=[
        ['share_left', 'Share only with the player on the left'],
        ['share_right', 'Share only with the player on the right'],
        ['share_both', 'Share with both the player on the left and the player on the right']
    ],
    widget=widgets.RadioSelect,
    label="How would you like to divide $12?"
)

# Control Questions - Example 1
example1_earnings_you = models.StringField(...)
example1_earnings_left = models.StringField(...)
example1_earnings_right = models.StringField(...)

# Control Questions - Example 2
example2_earnings_you = models.StringField(...)
example2_earnings_left = models.StringField(...)
example2_earnings_right = models.StringField(...)

# Control Questions - Payoff Question
payoff_question = models.StringField(...)

# Flag validazione
all_control_questions_correct = models.BooleanField(initial=False)
```

---

## 📄 Task 2: Creare Pagina Instructions for Part 3

### 2.1 File: `InstructionsPart3.html`
- Usare testo integrale dalla sezione 1.2 del prompt
- Mantenere formato identico a `InstructionsPart1.html` e `InstructionsPart2.html`
- Usare valuta corretta ($ per Part 3, come da istruzioni originali)
- **Testo da usare** (da `part3_prompt.md` sezione 1.2):
  ```
  In this part of the experiment, you and the other participants will be matched in groups of three. You and the other two members of your group will choose how each of you would like to divide $ 12 between the three of you.
  Please note that in Part 3 of the experiment, each participant will be matched with other group members than those they were matched with in Part 1.
  Each player has three options: to share the money equally with the player on the left, with the player on the right, or with both players. For example:
  • Option 1: Share only with the player on the left. Both you and the player on the left earn $ 6, while the player on the right earns $ 0.
  • Option 2: Share only with the player on the right. Both you and the player on the right earn $ 6, while the player on the left earns $ 0.
  • Option 3: Share with both the player on the left and the player on the right. All three of you earn $ 4.
  If Part 3 is randomly selected to determine the payoff of the experiment, then the choice of one of the three group members would be randomly selected and implemented. In each group, each participant has an equal probability of being selected as the actual decision maker in Part 3.
  ```

### 2.2 Classe Page: `InstructionsPart3`
- Eredita da `Page`
- Nessuna logica particolare, solo visualizzazione

---

## 📄 Task 3: Creare Pagina Summary

### 3.1 File: `SummaryPart3.html`
- Usare testo integrale dalla sezione 1.3 del prompt
- **Testo da usare**:
  ```
  In summary, Part 3 will proceed as follows:
  1. Group members make their decisions.
  2. The decision maker is randomly determined.
  3. Payments are determined.
  ```

### 3.2 Classe Page: `SummaryPart3`
- Eredita da `Page`
- Nessuna logica particolare, solo visualizzazione

---

## 📄 Task 4: Creare Pagina Control Questions for Part 3

### 4.1 File: `ControlQuestionsPart3.html`
- Usare testo integrale dalla sezione 1.4 del prompt
- Struttura simile a `ControlQuestionsPart2.html`
- **Testo da usare** (da `part3_prompt.md` sezione 1.4):
  - Titolo: "Control questions for Part 3"
  - Introduzione: "You have been matched with the player on the left and the player on the right for Part 3, consider the following three examples:"
  - Example 1: 3 domande (earnings you, left, right) - risposta corretta: $4 per tutti
  - Example 2: 3 domande (earnings you, left, right) - risposte corrette: you=$0, left=$6, right=$6
  - Payoff question: 4 opzioni multiple choice - risposta corretta: "I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3."

### 4.2 Classe Page: `ControlQuestionsPart3`
- Eredita da `Page`
- Metodo `before_next_page()` per validare tutte le risposte
- Se tutte corrette: `player.all_control_questions_correct = True`
- Se almeno una sbagliata: `player.all_control_questions_correct = False`

### 4.3 Logica Validazione
```python
def before_next_page(player, timeout_happened):
    correct = True
    
    # Example 1: tutte le risposte devono essere '4'
    if (player.example1_earnings_you != '4' or 
        player.example1_earnings_left != '4' or 
        player.example1_earnings_right != '4'):
        correct = False
    
    # Example 2: you='0', left='6', right='6'
    if (player.example2_earnings_you != '0' or 
        player.example2_earnings_left != '6' or 
        player.example2_earnings_right != '6'):
        correct = False
    
    # Payoff question: risposta corretta specifica
    if player.payoff_question != 'correct_answer_value':
        correct = False
    
    player.all_control_questions_correct = correct
```

---

## 📄 Task 5: Creare Pagina Thank You (per Control Questions fallite)

### 5.1 File: `ThankYouPart3.html`
- Pagina di chiusura se le control questions sono sbagliate
- Testo standard di ringraziamento
- Nessun pulsante "Next" - fine esperimento

### 5.2 Classe Page: `ThankYouPart3`
- Eredita da `Page`
- Metodo `is_displayed()`: mostra solo se `player.all_control_questions_correct == False`

---

## 📄 Task 6: Creare Pagina Decision Screen

### 6.1 File: `DecisionPart3.html`
- Mostrare tre opzioni di scelta:
  - "Share only with the player on the left"
  - "Share only with the player on the right"
  - "Share with both the player on the left and the player on the right"
- Usare RadioSelect widget
- Mostrare chiaramente i payoff per ogni opzione:
  - Option 1: You=$6, Left=$6, Right=$0
  - Option 2: You=$6, Left=$0, Right=$6
  - Option 3: You=$4, Left=$4, Right=$4

### 6.2 Classe Page: `DecisionPart3`
- Eredita da `Page`
- Metodo `is_displayed()`: mostra solo se `player.all_control_questions_correct == True`
- Salvare la scelta in `player.decision`

---

## 📄 Task 7: Creare Pagina Payoff (Finale)

### 7.1 File: `ResultsPart3.html` o `PayoffPart3.html`
- Pagina finale che mostra i payoff ottenuti dall'esperimento
- Mostrata dopo la decisione
- **Nota importante**: In futuro qui andranno mostrati i payoff ottenuti dall'esperimento completo. La definizione di come calcolarli sarà obiettivo di un'implementazione futura. Per il momento mostra solo i payoff provenienti dalla Part 1 che già si sanno calcolare.

### 7.2 Classe Page: `ResultsPart3` o `PayoffPart3`
- Eredita da `Page`
- Metodo `is_displayed()`: mostra solo se `player.all_control_questions_correct == True` e `player.decision` è compilato
- Metodo `vars_for_template()`: recuperare payoff dalla Part 1
  - Accedere a `player.participant.vars` o ai dati della Part 1 per ottenere il payoff
  - Mostrare il payoff della Part 1 (già calcolato)
  - In futuro: aggiungere logica per calcolare payoff completo (Part 1 + Part 2 o Part 1 + Part 3)

### 7.3 Logica Payoff (Implementazione Iniziale)
```python
@staticmethod
def vars_for_template(player):
    # Per ora: recuperare solo payoff Part 1
    # Il payoff della Part 1 è già stato calcolato e salvato
    # Accedere ai dati dalla Part 1 tramite participant.vars o session
    
    # Esempio (da adattare alla struttura reale):
    part1_payoff = player.participant.vars.get('part1_payoff', cu(0))
    
    return dict(
        part1_payoff=part1_payoff,
        # In futuro: aggiungere part2_payoff, part3_payoff, total_payoff
    )
```

### 7.4 Template HTML
- Mostrare chiaramente il payoff della Part 1
- Struttura simile a `bargaining_tdl_main/Results.html`
- Includere nota che in futuro verranno mostrati tutti i payoff

---

## 🔧 Task 8: Configurare Page Sequence

### 8.1 Aggiungere page_sequence in `__init__.py`
```python
page_sequence = [
    InstructionsPart3,
    SummaryPart3,
    ControlQuestionsPart3,
    ThankYouPart3,  # Solo se control questions sbagliate
    DecisionPart3,  # Solo se control questions corrette
    ResultsPart3,  # Solo se control questions corrette - mostra payoff
]
```

### 8.2 Gestire Condizionalità
- Usare `is_displayed()` su ogni pagina per controllare il flusso
- `ThankYouPart3`: mostra solo se `all_control_questions_correct == False`
- `DecisionPart3` e `ResultsPart3`: mostrano solo se `all_control_questions_correct == True`

---

## ⚙️ Task 9: Aggiornare settings.py

### 9.1 Aggiungere App alla Sequenza
- Modificare `app_sequence` in `SESSION_CONFIGS` per `bargaining_tdl`:
  ```python
  app_sequence=['bargaining_tdl_intro', 'bargaining_tdl_main', 'bargaining_tdl_part2', 'bargaining_tdl_part3']
  ```

### 9.2 Verificare Compatibilità
- Assicurarsi che non ci siano conflitti con le altre app
- Verificare che i dati necessari siano disponibili (se servono dati da Part 1/2)

---

## 🧪 Task 10: Testing

### 10.1 Test Flusso Completo
- Testare flusso con control questions corrette
- Testare flusso con control questions sbagliate
- Verificare che i dati vengano salvati correttamente

### 10.2 Test Validazione
- Testare ogni control question individualmente
- Verificare che la validazione funzioni correttamente
- Verificare che il flusso si interrompa correttamente se sbagliate

### 10.3 Test Decision Screen
- Verificare che tutte e tre le opzioni siano selezionabili
- Verificare che la scelta venga salvata correttamente
- Verificare che i payoff siano visualizzati correttamente

---

## 📝 Task 11: Documentazione

### 11.1 Commenti nel Codice
- Aggiungere docstring alle classi principali
- Commentare la logica di validazione
- Documentare i campi del Player model

### 11.2 Verifica Coerenza
- Verificare che tutti i testi corrispondano esattamente al prompt
- Verificare che il flusso sia coerente con Part 1 e Part 2
- Verificare che la struttura segua il pattern esistente

---

## ✅ Checklist Finale

- [ ] Cartella `bargaining_tdl_part3/` creata
- [ ] File `__init__.py` con tutte le classi e pagine
- [ ] Pagina `InstructionsPart3.html` con testo originale
- [ ] Pagina `SummaryPart3.html` con testo originale
- [ ] Pagina `ControlQuestionsPart3.html` con testo originale e validazione
- [ ] Pagina `ThankYouPart3.html` per control questions fallite
- [ ] Pagina `DecisionPart3.html` con tre opzioni
- [ ] Pagina `ResultsPart3.html` o `PayoffPart3.html` finale (mostra payoff Part 1)
- [ ] Page sequence configurata correttamente
- [ ] `settings.py` aggiornato
- [ ] Test eseguiti e funzionanti
- [ ] Documentazione completa

---

## 🎯 Note Implementative

1. **Valuta**: Part 3 usa $ (dollari) nelle istruzioni originali, ma il progetto usa GBP. Verificare se mantenere $ o convertire a £ seguendo il pattern del progetto.

2. **Mapping Left/Right**: Per il task individuale, non serve creare gruppi reali. Le istruzioni parlano di "player on the left" e "player on the right" ma questo sarà gestito a posteriori dallo sperimentatore.

3. **Salvataggio Dati**: La scelta del partecipante deve essere salvata in `player.decision` per permettere il calcolo del payoff finale.

4. **Payoff Page**: La pagina finale è una **Payoff Page** (non Thank You Page) che mostra i payoff dell'esperimento. Per ora mostra solo i payoff della Part 1 (già calcolati). Il calcolo completo dei payoff (Part 1 + Part 2 o Part 1 + Part 3) sarà implementato in futuro.

5. **Coerenza**: Mantenere lo stesso stile HTML/CSS delle altre parti per coerenza visiva.

---

## 📚 Riferimenti

- `docs/part3_prompt.md` - Documento principale con tutti i testi originali
- `bargaining_tdl_intro/` - Riferimento per struttura Part 1
- `bargaining_tdl_part2/` - Riferimento per struttura Part 2 (soprattutto control questions)
- `bargaining_tdl_part2/ControlQuestionsPart2.html` - Riferimento per struttura control questions
- `bargaining_tdl_main/Results.html` - Riferimento per struttura payoff page (mostra payoff Part 1)
