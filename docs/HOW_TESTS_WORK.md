# Come Funzionano i Test Automatici

Questo documento spiega in dettaglio come funzionano i test automatici dell'esperimento Bargaining TDL, come i bot interagiscono, e come vengono verificate le logiche dell'esperimento.

---

## 📚 Indice

1. [Architettura dei Test](#architettura-dei-test)
2. [Come Funzionano i Bot](#come-funzionano-i-bot)
3. [Raggruppamento nei Test](#raggruppamento-nei-test)
4. [Criteri di Decisione dei Bot](#criteri-decisione-dei-bot)
5. [Verifiche Automatiche](#verifiche-automatiche)
6. [Flusso Completo di un Test](#flusso-completo-di-un-test)
7. [Limitazioni e Considerazioni](#limitazioni-e-considerazioni)

---

## 🏗️ Architettura dei Test

### Struttura Base

Ogni app ha un file `tests.py` che contiene:

```python
from otree.api import Currency as c, currency_range, expect, Bot
from . import *

class PlayerBot(Bot):
    cases = ['case1', 'case2', ...]
    
    def play_round(self):
        # Simula il comportamento del partecipante
        yield Page1
        yield Page2, dict(field1='value1', field2='value2')
        # Verifiche con expect()
```

### Componenti Chiave

- **`Bot`**: Classe base di oTree per creare bot automatici
- **`cases`**: Lista di scenari che il bot può simulare
- **`play_round()`**: Metodo che simula il comportamento del partecipante
- **`yield`**: Simula la navigazione tra pagine
- **`expect()`**: Verifica che le condizioni siano soddisfatte

---

## 🤖 Come Funzionano i Bot

### 1. Simulazione del Flusso Completo

I bot **non saltano** pagine o logiche. Passano attraverso **tutte le pagine** dell'esperimento esattamente come farebbe un partecipante reale:

```python
def play_round(self):
    # Welcome page (no form)
    yield Welcome
    
    # Instructions page (no form)
    yield InstructionsPart1
    
    # Control Questions - compila il form
    yield ControlQuestions, dict(
        example1_earnings_you='6',
        example1_earnings_left='0',
        # ... altre risposte
    )
    
    # Chat - compila i messaggi
    yield Chat, dict(
        draft_history_left="Hi...",
        draft_history_right="Hello...",
        time_on_page=1.0,
    )
    # Signals - compila le intenzioni
    yield Signals, dict(
        signal_left="I wish to split...",
        signal_right="I wish to split...",
        time_on_page=1.0,
    )
```

**Ogni `yield` simula:**
- L'apertura della pagina
- L'attesa del caricamento
- La compilazione dei form (se presente)
- Il click su "Next"
- La navigazione alla pagina successiva

### 2. Rispetto delle Logiche dell'Esperimento

I bot **rispettano completamente** le logiche implementate:

#### ✅ Logica di Raggruppamento

Quando i bot arrivano alla `GroupingWaitPage` con `group_by_arrival_time=True`:

1. **I primi 3 bot** che arrivano → formano il **Gruppo 1**
2. **I successivi 3 bot** che arrivano → formano il **Gruppo 2**
3. E così via...

```python
# In bargaining_tdl_main/__init__.py
class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        map_player_data_in_group(group)  # Eseguita quando gruppo completo
```

**Nei test:**
- I bot vengono automaticamente raggruppati da oTree
- `after_all_players_arrive()` viene chiamata quando il gruppo è completo (3 bot)
- Il mapping dei dati viene eseguito correttamente

#### ✅ Logica dei Payoff

I bot **verificano** che i payoff siano calcolati correttamente:

```python
# Dopo aver completato Decision e ResultsWaitPage
yield Results

# Verifica che il payoff sia stato calcolato
expect(self.player.payoff, '!=', None)

# Verifica payoff specifici in base allo scenario
if case == 'all_both':
    expect(self.player.payoff, C.PAYOFF_SPLIT)  # Deve essere 4
elif case == 'match_12':
    if id_in_group in [1, 2]:
        expect(self.player.payoff, C.PAYOFF_MAX)  # Deve essere 6
    else:
        expect(self.player.payoff, C.PAYOFF_DISAGREEMENT)  # Deve essere 0
```

#### ✅ Persistenza dei Dati

I bot verificano che i dati siano salvati correttamente:

```python
# Verifica che i dati siano stati salvati in participant.vars
expect(self.player.participant.vars.get('signal_left'), signal_left)
expect(self.player.participant.vars.get('signal_right'), signal_right)
expect(self.player.participant.vars.get('part1_payoff'), self.player.payoff)
```

---

## 👥 Raggruppamento nei Test

### Come oTree Raggruppa i Bot

Quando esegui `otree test bargaining_tdl 90`:

1. **90 bot** vengono creati simultaneamente
2. Tutti i bot iniziano l'esperimento in parallelo (approssimativamente)
3. Quando arrivano alla `GroupingWaitPage`:
   - I bot procedono a velocità simile (non perfettamente sincronizzati)
   - oTree li raggruppa **nell'ordine di arrivo**
   - Primi 3 arrivati → **Gruppo 1**
   - Successivi 3 arrivati → **Gruppo 2**
   - ... e così via fino a **30 gruppi**

### Esempio Pratico

```python
# Test con 9 partecipanti (3 gruppi)

Bot 1, 2, 3 → Gruppo 1
  - P1 (id_in_group=1)
  - P2 (id_in_group=2)
  - P3 (id_in_group=3)

Bot 4, 5, 6 → Gruppo 2
  - P4 (id_in_group=1)
  - P5 (id_in_group=2)
  - P6 (id_in_group=3)

Bot 7, 8, 9 → Gruppo 3
  - P7 (id_in_group=1)
  - P8 (id_in_group=2)
  - P9 (id_in_group=3)
```

### Mapping dei Dati tra Player

Quando un gruppo è completo, viene eseguita la funzione `map_player_data_in_group()`:

```python
# Topology circolare del gruppo
# P1 (id=1): Left=P3, Right=P2
# P2 (id=2): Left=P1, Right=P3
# P3 (id=3): Left=P2, Right=P1

# P1 riceve:
# - Da Left (P3): quello che P3 ha inviato a Right (P1)
# - Da Right (P2): quello che P2 ha inviato a Left (P1)

# I dati vengono letti da participant.vars (salvati in intro)
# e mappati nei campi received_* del Player
```

**Nei test:**
- I bot della fase intro salvano dati in `participant.vars`
- Quando si raggruppano in main, i dati vengono mappati correttamente
- Ogni bot riceve i dati che gli altri hanno inviato a lui

---

## 🎲 Criteri di Decisione dei Bot

I bot **non decidono casualmente**. Usano **casi predefiniti** ("cases") che simulano comportamenti specifici.

### Part 1 (Intro): Tipi di Partecipanti

```python
cases = [
    'cooperative',      # Sempre Both
    'competitive',      # Strategia Left/Right
    'mixed',            # Strategia mista
    'altruistic',       # Sempre Both
]

if case == 'cooperative':
    signal_left = "I wish to split... with both you and player on the right"
    signal_right = "I wish to split... with both you and player on the left"
elif case == 'competitive':
    signal_left = "I wish to split... with you only, player on the left."
    signal_right = "I wish to split... with the other player only..."
```

### Part 1 Main (Decision): Scenari di Test

```python
cases = [
    'all_both',        # Tutti scelgono Both → payoff 4 per tutti
    'match_12',        # P1→Right, P2→Left → P1 e P2 vincono (6), P3 perde (0)
    'match_23',        # P2→Right, P3→Left → P2 e P3 vincono (6), P1 perde (0)
    'match_31',        # P3→Right, P1→Left → P3 e P1 vincono (6), P2 perde (0)
    'disagreement',    # Nessun match → tutti 0
    'mixed_strategy',  # Strategia variabile
    'experiment_terminated',  # Testa terminazione quando failed_control_questions=True
]

# Il bot decide in base al suo id_in_group
if case == 'match_12':
    if id_in_group == 1:
        decision = 'Right'  # P1 cerca match con P2
    elif id_in_group == 2:
        decision = 'Left'   # P2 cerca match con P1
    else:  # id_in_group == 3
        decision = 'Both'   # P3 non partecipa al match
```

### Part 2 (MPL): Profili di Rischio

```python
cases = [
    'risk_averse',     # Switching points bassi (0-30) → preferisce Option 1
    'risk_neutral',    # Switching points medi (40-60)
    'risk_loving',     # Switching points alti (70-100) → preferisce Option 2
    'mixed',           # Switching points variabili
]

if case == 'risk_averse':
    base_switch = random.randint(0, 30)
elif case == 'risk_neutral':
    base_switch = random.randint(40, 60)
# ...
```

### Part 3: Strategie di Condivisione

```python
cases = [
    'share_left',      # Condivide solo con left
    'share_right',     # Condivide solo con right
    'share_both',      # Condivide con entrambi
    'selfish',         # Strategia egoista
    'cooperative',     # Strategia cooperativa (share_both)
]
```

---

## ✅ Verifiche Automatiche

I bot **non solo eseguono** l'esperimento, ma **verificano** che tutto funzioni correttamente:

### 1. Verifica Dati Salvati

```python
# Verifica che i dati siano stati salvati in participant.vars
expect(self.player.participant.vars.get('signal_left'), signal_left)
expect(self.player.participant.vars.get('signal_right'), signal_right)
expect(self.player.participant.vars.get('failed_control_questions'), False)
```

### 2. Verifica Mapping dei Dati

```python
# Verifica che i campi received_* siano stati popolati dopo il mapping
expect(self.player.received_history_left, '!=', None)
expect(self.player.received_history_right, '!=', None)
expect(self.player.received_signal_left, '!=', None)
expect(self.player.received_signal_right, '!=', None)
```

### 3. Verifica Payoff Calcolati

```python
# Verifica che il payoff sia stato calcolato
expect(self.player.payoff, '!=', None)

# Verifica payoff specifici in base allo scenario
if case == 'all_both':
    expect(self.player.payoff, C.PAYOFF_SPLIT)  # Deve essere 4
elif case == 'match_12':
    if id_in_group in [1, 2]:
        expect(self.player.payoff, C.PAYOFF_MAX)  # Deve essere 6
```

### 4. Verifica Time Tracking

```python
# Verifica che i time tracking fields siano stati salvati
expect(self.player.time_decision, '>=', 0)
expect(self.player.time_results, '>=', 0)
expect(self.player.time_experiment_terminated, '>=', 0)
```

### 5. Verifica Terminazione Esperimento

```python
# Quando failed_control_questions=True
if case == 'experiment_terminated':
    set_control_questions_failed(self.player, 'intro', failed=True)
    yield ExperimentTerminated, dict(time_on_page=1.0)
    expect(self.player.time_experiment_terminated, '>=', 0)
    # L'esperimento dovrebbe terminare qui
```

---

## 🔄 Flusso Completo di un Test

### Esempio: Test con 9 Partecipanti

```bash
otree test bargaining_tdl 9
```

### Fase 1: Intro (bargaining_tdl_intro)

**9 bot** eseguono simultaneamente:

1. **Welcome** (no form)
2. **InstructionsPart1** (no form)
3. **ControlQuestions** (form)
   - Bot risponde correttamente (per permettere test completo)
   - `participant.vars['failed_control_questions'] = False`
4. **Chat** (form) – messaggi verso left e right  
5. **Signals** (form) – intenzioni verso left e right
   - Bot genera messaggi e segnali in base al suo `case`
   - Dati salvati in `participant.vars`:
     - `signal_left`, `signal_right`
     - `draft_history_left`, `draft_history_right`

**Risultato**: 9 partecipanti con dati salvati in `participant.vars`

### Fase 2: Main (bargaining_tdl_main)

**9 bot** arrivano alla `GroupingWaitPage`:

1. **Raggruppamento**:
   - Bot 1, 2, 3 → **Gruppo 1**
   - Bot 4, 5, 6 → **Gruppo 2**
   - Bot 7, 8, 9 → **Gruppo 3**

2. **Quando ogni gruppo è completo**:
   - `after_all_players_arrive()` viene chiamata
   - `map_player_data_in_group()` mappa i dati
   - Ogni bot riceve `received_history_*` e `received_signal_*`

3. **Decision**:
   - Ogni bot decide in base al suo `case` e `id_in_group`
   - Form include `decision_choice` e `time_on_page`

4. **ResultsWaitPage**:
   - Bot aspetta che tutti nel gruppo decidano
   - Quando completo, `after_all_players_arrive()` calcola i payoff

5. **Results**:
   - Bot vede i risultati
   - Payoff salvato in `participant.vars['part1_payoff']`
   - Time tracking salvato in `time_results`

### Fase 3: Part 2 (bargaining_tdl_part2)

**9 bot** completano le MPL questions:

1. **InstructionsPart2** (no form)
2. **PaymentInstructionPart2** (no form)
3. **ControlQuestionsPart2** (form)
4. **12 MPL Questions** (form per ognuna)
   - Bot risponde in base al suo `case` (risk_averse, risk_neutral, etc.)
5. **ResultsPart2** (no form)
   - Payoff calcolato e salvato

### Fase 4: Part 3 (bargaining_tdl_part3)

**9 bot** completano il Three-Person Dictator Game:

1. **InstructionsPart3** (no form)
2. **SummaryPart3** (no form)
3. **ControlQuestionsPart3** (form)
4. **DecisionPart3** (form)
   - Bot decide in base al suo `case`
5. **ResultsPart3** (no form)
   - Payoff finale calcolato

### Verifiche Finali

Ogni bot verifica automaticamente:
- ✅ Dati salvati correttamente
- ✅ Payoff calcolati correttamente
- ✅ Time tracking salvato
- ✅ Mapping dei dati funzionante

---

## ⚠️ Limitazioni e Considerazioni

### Cosa i Bot NON Fanno

1. **Non Leggono i Dati degli Altri prima di Decidere**
   - I bot decidono **solo** in base al loro `case`
   - Non simulano reazioni ai segnali ricevuti
   - Non cambiano strategia in base al comportamento degli altri

2. **Tempi Istantanei**
   - I bot non simulano pause di lettura
   - Non simulano tempi di riflessione
   - Navigano istantaneamente tra le pagine

3. **Sempre Risposte Corrette alle Control Questions**
   - I bot passano sempre le control questions (risposte corrette hardcoded)
   - Per testare il fallimento, usare il caso `'experiment_terminated'`

4. **Strategie Predefinite**
   - I bot non adattano le loro strategie
   - Usano sempre lo stesso comportamento per ogni `case`

### Come i Bot Simulano il Comportamento Umano

✅ **Coprono scenari vari**: Diversi `cases` simulano comportamenti diversi

✅ **Rispettano le logiche**: Tutte le regole dell'esperimento vengono rispettate

✅ **Verificano i risultati**: Assicurano che tutto funzioni correttamente

✅ **Testano scale**: Possono testare con molti partecipanti (90, 900, etc.)

---

## 📊 Esempio di Output di un Test

Quando esegui un test, vedrai output tipo:

```
Running tests for bargaining_tdl with 9 participants...

✓ bargaining_tdl_intro: 9 participants tested successfully
  - Cases: cooperative, competitive, mixed, altruistic
  
✓ bargaining_tdl_main: 9 participants tested successfully (3 groups)
  - Cases: all_both, match_12, match_23, match_31, disagreement, mixed_strategy
  
✓ bargaining_tdl_part2: 9 participants tested successfully
  - Cases: risk_averse, risk_neutral, risk_loving, mixed
  
✓ bargaining_tdl_part3: 9 participants tested successfully
  - Cases: share_left, share_right, share_both, selfish, cooperative

All tests passed! ✅
```

---

## 🎯 Quando Usare i Test

### ✅ Usa i Test per:

- **Verificare la logica**: Assicurarsi che i payoff siano calcolati correttamente
- **Testare scale**: Verificare che l'esperimento funzioni con molti partecipanti
- **Regression testing**: Assicurarsi che nuove modifiche non rompano funzionalità esistenti
- **Validare il mapping**: Verificare che i dati vengano mappati correttamente tra i player

### ❌ Non Usare i Test per:

- **Simulare comportamenti umani reali**: I bot hanno strategie fisse
- **Prevedere risultati reali**: I partecipanti reali si comportano diversamente
- **Testare l'UI**: I test non aprono browser (usa `otree browser_bots` per questo)

---

## 🔧 Personalizzazione dei Test

### Aggiungere un Nuovo Caso

```python
# In tests.py
cases = [
    'existing_case',
    'new_case',  # Aggiungi qui
]

def play_round(self):
    case = self.case
    
    if case == 'new_case':
        # Implementa il comportamento
        decision = 'Both'
    # ...
```

### Modificare un Comportamento Esistente

```python
def play_round(self):
    case = self.case
    
    if case == 'cooperative':
        # Modifica qui il comportamento cooperativo
        decision = 'Both'
    # ...
```

### Aggiungere Nuove Verifiche

```python
# Dopo yield Results
yield Results

# Aggiungi nuove verifiche
expect(self.player.custom_field, expected_value)
expect(self.player.participant.vars.get('custom_var'), '!=', None)
```

---

## 📚 Riferimenti

- [Documentazione oTree - Bots](https://otree.readthedocs.io/en/latest/bots.html)
- [Documentazione oTree - Test Avanzati](https://otree.readthedocs.io/en/latest/misc/bots_advanced.html)
- [TESTING.md](./TESTING.md) - Guida pratica ai test
- File di test: `bargaining_tdl_*/tests.py`

---

**Nota**: I test sono progettati per essere **deterministici** e **riproducibili**. Ogni esecuzione con gli stessi parametri dovrebbe produrre gli stessi risultati.

