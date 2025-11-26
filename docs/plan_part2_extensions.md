# Piano d'Azione: Estensione Part 2 - Payment Instructions e Control Questions

## 📋 Overview

Estendere il flusso della **Parte 2** dell'esperimento inserendo nuove schermate e nuove regole di validazione, **senza alterare alcun testo originale** del paper, delle istruzioni, delle domande o delle control questions esistenti.

**Obiettivo**: Aggiornare la logica e il flusso della Parte 2, inserendo nuove schermate e nuove regole, mantenendo intatto il sistema attuale.

---

## ⚠️ PRINCIPI FONDAMENTALI

1. **NON MODIFICARE** testi inglesi, domande, istruzioni generate finora
2. **NON ALTERARE** l'ordine esistente delle MPL
3. **NON TOCCARE** la logica dello "switch unico"
4. **NON MODIFICARE** mapping left/right
5. **NON ALTERARE** persistenza dei risultati
6. **NON INTERPRETARE, NON RIFORMULARE, NON SEMPLIFICARE** testi originali

L'unica modifica è inserire correttamente le nuove pagine nel flusso esistente.

---

## 🎯 Flusso Finale della Part 2

Il flusso corretto della Parte 2 deve essere:

1. **Instructions for Part 2** (già presente → NON MODIFICARE)
2. **Payment Instruction for Part Two** (NUOVA PAGINA)
3. **Control Questions for Part 2** (NUOVA PAGINA con validazione)
4. **Thank You Page** (NUOVA PAGINA - mostrata solo se validazione fallisce)
5. **MPL Question 1** (già presente → NON MODIFICARE)
6. **MPL Question 2** (già presente → NON MODIFICARE)
7. ...
8. **MPL Question 12** (già presente → NON MODIFICARE)
9. **Results Part 2** (già presente → NON MODIFICARE)

---

## 📄 Testi Originali OBBLIGATORI

### 1. Payment Instruction for Part Two

**Testo integrale** (NON MODIFICARE):

```
Payment instructions for Part 2

In Part 2 of the experiment, you will face 12 screens where you will have to express your
preference between Option 1 and Option 2 for different levels of p. In 6 of these screens,
Option 1 will refer to the choice of a participant you interacted with in Part 1(i.e., the player
on the left), while in the other 6, Option 1 will refer to the choice of the other participant
you interacted with in Part 1(i.e., the player on the right).

Once the experiment is over, one of your choices will be played out for real.

The computer will randomly pick with equal probability one question out of the 12 and
one line and check which option you chose in the experiment.

If you preferred the bet on Option 1, then the computer will check the choice made by the
other relevant participant, show it to you, and pay you accordingly. If, on the other hand,
you preferred Option 2, then we will play out your choice with the help of the computer.

The computer will randomly draw an integer between 1 and 100 inclusive; each number
has an equal probability of being drawn. Probability p% is equivalent to the probability of
drawing a number less than or equal to p out of 1,2...,100. Thus, if the bet is "You win $ 5
with 74% probability and nothing otherwise", then if the number drawn is less than or equal
to the value of 74 you will win the bet.

On the next screen, we will present you with an example and two related questions to
ensure you understood the payment mechanism for Part 2.
```

**Nota**: Il testo usa `$ 5` ma il sistema usa `£5` (GBP). Verificare se mantenere `$ 5` o convertire in `£5` per coerenza.

---

### 2. Control Questions for Part 2

**Testo integrale** (NON MODIFICARE):

```
Control questions for Part 2

Example: Imagine that the question where Option 1 is "You win $ 5 if the player on the
left chose "Share only with the player on the right" or "Share with both you and
the player on the right" (and nothing otherwise)" is selected. Imagine that you preferred
Option 1 for p% less than or equal to 80% and Option 2 for p% greater than or equal to
85%.

Question 1: Imagine that, at the end of the experiment, the question in the example is
played for real money for p = 45%. The example indicates that, for p = 45%, Option 1 is
preferred. You would therefore win $ 5 if the player on the left chose "Share only with the
player on the right" or "Share with both you and the player on the right". Let assume that
at the end of the experiment we found out that the player on the left chose "Share with both
you and the player on the right". What would be the payment for Part 2? Please select an
answer.

• I don't win anything.
• $ 5. (Correct answer)
• I don't know.

Question 2: Imagine that, at the end of the experiment, the question in the example is
played for real money for p = 93%. The example indicates that, for p = 93%, Option 2 is
preferred. The computer randomly draws the number 57. What would be the payment for
Part 2? Please select an answer.

• I don't win anything.
• $ 5. (Correct answer)
• I don't know.
```

**Nota**: Anche qui il testo usa `$ 5`. Verificare coerenza con `£5`.

---

## 🔧 Task di Implementazione

### Fase 1: Creazione Nuove Pagine HTML

#### Task 1: PaymentInstructionPart2.html
- **File**: `bargaining_tdl_part2/PaymentInstructionPart2.html`
- **Tipo**: Pagina informativa (solo testo, nessun form)
- **Contenuto**: Testo integrale fornito sopra
- **Note**: 
  - Usare template standard oTree con `{{ block title }}` e `{{ block content }}`
  - Includere `{{ next_button }}`
  - Verificare se convertire `$ 5` in `£5` per coerenza

#### Task 2: ControlQuestionsPart2.html
- **File**: `bargaining_tdl_part2/ControlQuestionsPart2.html`
- **Tipo**: Pagina con form (due domande a scelta multipla)
- **Contenuto**: 
  - Testo dell'Example
  - Question 1 con 3 opzioni (radio buttons)
  - Question 2 con 3 opzioni (radio buttons)
- **Note**:
  - Usare `{{ formfield }}` per ogni domanda
  - Stile coerente con `ControlQuestions.html` della Part 1
  - Messaggio di avvertimento: "You must answer all questions correctly to continue. If you answer incorrectly, the experiment will end."

#### Task 3: ThankYouPart2.html
- **File**: `bargaining_tdl_part2/ThankYouPart2.html`
- **Tipo**: Pagina finale (equivalente a `Goodbye.html` della Part 1)
- **Contenuto**: 
  - Messaggio di ringraziamento
  - Spiegazione che l'esperimento è terminato per risposte sbagliate
- **Note**:
  - Includere JavaScript per disabilitare navigazione (come in `Goodbye.html`)
  - Rimuovere il pulsante Next dal DOM
  - Prevenire qualsiasi submit del form

---

### Fase 2: Logica Backend

#### Task 4: Aggiungere Campi Player
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Aggiungere al modello `Player`:
  ```python
  control_question_1 = models.StringField(
      choices=[
          ["nothing", "I don't win anything."],
          ["5", "$ 5."],  # o "£5." se convertiamo
          ["dont_know", "I don't know."]
      ],
      label="Question 1: What would be the payment for Part 2?"
  )
  
  control_question_2 = models.StringField(
      choices=[
          ["nothing", "I don't win anything."],
          ["5", "$ 5."],  # o "£5." se convertiamo
          ["dont_know", "I don't know."]
      ],
      label="Question 2: What would be the payment for Part 2?"
  )
  ```

#### Task 5: Funzione di Validazione
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Creare funzione `check_control_questions_part2_correct(player)`:
  ```python
  def check_control_questions_part2_correct(player: Player) -> bool:
      """Verifica se entrambe le risposte alle control questions sono corrette."""
      if not player.control_question_1 or not player.control_question_2:
          return False
      
      # Entrambe le risposte corrette devono essere "5" (o "£5" se convertiamo)
      correct = (
          player.control_question_1 == "5" and
          player.control_question_2 == "5"
      )
      return correct
  ```

#### Task 6: Classe PaymentInstructionPart2
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Creare classe Page semplice (solo visualizzazione):
  ```python
  class PaymentInstructionPart2(Page):
      pass
  ```

#### Task 7: Classe ControlQuestionsPart2
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Creare classe Page con form e validazione:
  ```python
  class ControlQuestionsPart2(Page):
      form_model = 'player'
      form_fields = ['control_question_1', 'control_question_2']
      
      @staticmethod
      def before_next_page(player, timeout_happened):
          """Salva un flag se le risposte sono sbagliate."""
          is_correct = check_control_questions_part2_correct(player)
          player.participant.vars['failed_control_questions_part2'] = not is_correct
  ```

#### Task 8: Classe ThankYouPart2
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Creare classe Page con logica condizionale:
  ```python
  class ThankYouPart2(Page):
      """Pagina di saluto che termina l'esperimento per il partecipante."""
      
      @staticmethod
      def is_displayed(player):
          """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
          failed = player.participant.vars.get('failed_control_questions_part2')
          if failed is None:
              return False
          return failed
      
      @staticmethod
      def app_after_this_page(player, upcoming_apps):
          """Termina l'esperimento dopo questa pagina."""
          return []
  ```

---

### Fase 3: Integrazione nel Flusso

#### Task 9: Aggiornare page_sequence
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Modificare `page_sequence` per includere le nuove pagine:
  ```python
  page_sequence = [
      InstructionsPart2,           # Già presente
      PaymentInstructionPart2,     # NUOVA
      ControlQuestionsPart2,       # NUOVA
      ThankYouPart2,                # NUOVA (condizionale)
      MPLQuestion1,                 # Già presente
      MPLQuestion2,                 # Già presente
      # ... altre MPL questions
      MPLQuestion12,                # Già presente
      ResultsPart2                  # Già presente
  ]
  ```

#### Task 10: Aggiungere is_displayed() alle MPL Questions
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Aggiungere `is_displayed()` a tutte le classi `MPLQuestion1` - `MPLQuestion12`:
  ```python
  @staticmethod
  def is_displayed(player):
      """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
      failed = player.participant.vars.get('failed_control_questions_part2', False)
      return not failed
  ```

#### Task 11: Aggiungere is_displayed() a ResultsPart2
- **File**: `bargaining_tdl_part2/__init__.py`
- **Azione**: Aggiungere `is_displayed()` alla classe `ResultsPart2`:
  ```python
  @staticmethod
  def is_displayed(player):
      """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
      failed = player.participant.vars.get('failed_control_questions_part2', False)
      return not failed
  ```

---

### Fase 4: Coerenza e Test

#### Task 12: Verificare Coerenza Valuta
- **Azione**: Decidere se convertire `$ 5` in `£5` nei testi
- **Opzioni**:
  1. Mantenere `$ 5` come nel testo originale (più fedele al paper)
  2. Convertire in `£5` per coerenza con `REAL_WORLD_CURRENCY_CODE = 'GBP'`
- **Raccomandazione**: Chiedere conferma all'utente o mantenere `$ 5` se il paper usa dollari

#### Task 13: Test Flusso Corretto
- **Scenario**: Partecipante risponde correttamente alle control questions
- **Flusso atteso**:
  1. Instructions for Part 2 ✓
  2. Payment Instruction for Part Two ✓
  3. Control Questions for Part 2 ✓ (risposte corrette)
  4. Thank You Page ✗ (non mostrata)
  5. MPL Question 1-12 ✓
  6. Results Part 2 ✓

#### Task 14: Test Flusso con Risposte Sbagliate
- **Scenario**: Partecipante risponde sbagliato a una o entrambe le control questions
- **Flusso atteso**:
  1. Instructions for Part 2 ✓
  2. Payment Instruction for Part Two ✓
  3. Control Questions for Part 2 ✓ (risposte sbagliate)
  4. Thank You Page ✓ (mostrata, esperimento termina)
  5. MPL Question 1-12 ✗ (non mostrate)
  6. Results Part 2 ✗ (non mostrata)

---

## 🔍 Pattern di Validazione (da Part 1)

Il pattern di validazione segue esattamente quello implementato nella Part 1:

1. **ControlQuestionsPart2**:
   - Ha `form_fields` per le risposte
   - In `before_next_page()` valida le risposte e salva flag `failed_control_questions_part2` in `participant.vars`
   - **NON** implementa `app_after_this_page()` (oTree gestisce automaticamente il flusso)

2. **ThankYouPart2**:
   - Usa `is_displayed()` per controllare il flag
   - Implementa `app_after_this_page()` che ritorna `[]` per terminare l'esperimento
   - Include JavaScript per prevenire navigazione

3. **Pagine successive (MPL Questions, Results)**:
   - Usano `is_displayed()` per non essere mostrate se `failed_control_questions_part2 == True`
   - Questo garantisce che il partecipante non possa procedere se ha fallito

---

## ⚠️ Note Importanti

1. **NON modificare** la logica esistente delle MPL Questions
2. **NON modificare** il sistema di switch unico
3. **NON modificare** il mapping left/right
4. **NON modificare** la persistenza dei risultati
5. **NON modificare** testi esistenti
6. **NON interpretare** i testi originali - usarli esattamente come forniti

---

## 📝 Checklist Finale

- [ ] PaymentInstructionPart2.html creato con testo integrale
- [ ] ControlQuestionsPart2.html creato con form e testo integrale
- [ ] ThankYouPart2.html creato con JavaScript per prevenire navigazione
- [ ] Campi Player aggiunti per control_question_1 e control_question_2
- [ ] Funzione check_control_questions_part2_correct() implementata
- [ ] Classe PaymentInstructionPart2 creata
- [ ] Classe ControlQuestionsPart2 creata con validazione
- [ ] Classe ThankYouPart2 creata con terminazione esperimento
- [ ] page_sequence aggiornata con nuove pagine nell'ordine corretto
- [ ] is_displayed() aggiunto a tutte le MPL Questions
- [ ] is_displayed() aggiunto a ResultsPart2
- [ ] Coerenza valuta verificata ($5 vs £5)
- [ ] Test flusso con risposte corrette completato
- [ ] Test flusso con risposte sbagliate completato

---

## 🎯 Risultato Atteso

Al completamento di tutte le task, il flusso della Part 2 sarà:

```
Instructions for Part 2
    ↓
Payment Instruction for Part Two (NUOVA)
    ↓
Control Questions for Part 2 (NUOVA)
    ↓
    ├─ Risposte corrette → MPL Question 1-12 → Results Part 2
    └─ Risposte sbagliate → Thank You Page → Fine Esperimento
```

Tutto questo **senza alterare** alcun testo originale o logica esistente delle MPL Questions.
