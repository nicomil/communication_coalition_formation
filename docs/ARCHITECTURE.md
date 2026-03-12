# Architettura dell'Applicazione - Bargaining Game (TDL + Async)

## 📋 Overview

L'applicazione è un esperimento economico basato su oTree che implementa un gioco di bargaining a tre partecipanti. L'esperimento è strutturato in 4 parti sequenziali, con un modulo comune che fornisce funzionalità condivise.

**Framework**: oTree 5.11.4  
**Linguaggio**: Python 3.11+  
**Architettura**: Modulare con separazione delle responsabilità

---

## 🏗️ Struttura Modulare

L'applicazione è organizzata in 5 moduli principali:

```
comunication_coalition_formation/
├── bargaining_tdl_common/          # Modulo comune (funzionalità condivise)
│   ├── __init__.py
│   ├── helpers.py                  # Funzioni utility
│   ├── validators.py               # Validatori control questions
│   ├── utils.py                    # Funzioni cross-module
│   └── mixins.py                   # Base classes e mixins
│
├── bargaining_tdl_intro/           # Part 1: Individual Tasks
│   ├── __init__.py
│   └── [templates HTML]
│
├── bargaining_tdl_main/            # Part 1: Grouping & Decision
│   ├── __init__.py
│   └── [templates HTML]
│
├── bargaining_tdl_part2/           # Part 2: Matching Probability List (MPL)
│   ├── __init__.py
│   └── [templates HTML]
│
├── bargaining_tdl_part3/           # Part 3: Three-Person Dictator Game
│   ├── __init__.py
│   └── [templates HTML]
│
└── settings.py                     # Configurazione oTree
```

---

## 🔄 Flusso dell'Esperimento

L'esperimento segue una sequenza lineare definita in `settings.py`:

```
bargaining_tdl_intro → bargaining_tdl_main → bargaining_tdl_part2 → bargaining_tdl_part3
```

### Sequenza Completa

1. **bargaining_tdl_intro** (Individual Tasks)
   - Welcome
   - Instructions Part 1
   - Control Questions
   - Goodbye (se control questions fallite)
   - Chat and Signals (draft messages + intentions)

2. **bargaining_tdl_main** (Grouping & Decision)
   - GroupingWaitPage (raggruppamento dinamico)
   - ExperimentTerminated (se control questions fallite)
   - Decision (scelta finale)
   - ResultsWaitPage (calcolo payoff)
   - Results (visualizzazione risultati)

3. **bargaining_tdl_part2** (MPL Questions)
   - Instructions Part 2
   - Payment Instruction Part 2
   - Control Questions Part 2
   - Thank You Part 2 (se control questions fallite)
   - MPL Intro First Player
   - MPL Question 1-6
   - MPL Intro Second Player
   - MPL Question 7-12
   - Results Part 2

4. **bargaining_tdl_part3** (Dictator Game)
   - Instructions Part 3
   - Summary Part 3
   - Control Questions Part 3
   - Thank You Part 3 (se control questions fallite)
   - Decision Part 3
   - Results Part 3 (payoff finale)

---

## 📦 Modulo Comune: `bargaining_tdl_common`

Il modulo comune centralizza funzionalità condivise tra tutti i moduli dell'esperimento, riducendo duplicazione e garantendo consistenza.

### Struttura

#### `helpers.py`
Funzioni utility base:
- `save_time_value()`: Converte e valida valori di tempo per il tracking

#### `validators.py`
Validatori per control questions:
- `set_control_questions_failed()`: Imposta flag di fallimento
- `has_failed_control_questions()`: Verifica se control questions sono fallite
- `check_control_questions_intro()`: Validazione Part 1
- `check_control_questions_part2()`: Validazione Part 2
- `check_control_questions_part3()`: Validazione Part 3

#### `utils.py`
Funzioni cross-module:
- `get_main_group_player()`: Recupera player dal gruppo di main
- `get_participant_role_in_group()`: Determina ruolo (A, B, C) nel gruppo

#### `mixins.py`
Base classes per estensioni future:
- `TimeTrackedPage`: Base class per pagine con time tracking automatico

### Pattern di Utilizzo

Tutti i moduli importano da `bargaining_tdl_common`:

```python
from bargaining_tdl_common import (
    save_time_value,
    check_control_questions_intro,
    set_control_questions_failed,
    has_failed_control_questions,
)
```

---

## 🎯 Dettagli Moduli

### 1. `bargaining_tdl_intro` - Part 1: Individual Tasks

**Scopo**: Fase iniziale individuale dove ogni partecipante:
- Legge le istruzioni
- Completa le control questions
- Scrive messaggi (draft) agli altri due partecipanti
- Seleziona le intenzioni (signals)

**Caratteristiche**:
- `PLAYERS_PER_GROUP = None` (task individuale)
- Salva dati in `participant.vars` per uso futuro
- Validazione control questions con redirect a Goodbye se fallite

**Dati salvati in `participant.vars`**:
- `draft_history_left`, `draft_history_right`
- `signal_left`, `signal_right`
- `failed_control_questions` (flag)

**Pagine chiavi**: `Chat` e `Signals`
- **Chat**: interfaccia a due colonne per i messaggi verso partner a sinistra e a destra
- **Signals**: selezione intenzioni per left e right player; tracking del primo intention selezionato

---

### 2. `bargaining_tdl_main` - Part 1: Grouping & Decision

**Scopo**: Raggruppamento dinamico e decisione finale

**Caratteristiche**:
- `PLAYERS_PER_GROUP = 3` (triadi)
- `group_by_arrival_time = True` (raggruppamento dinamico)
- Mapping dati tra player usando topology circolare

**Topology del Gruppo**:
```
P1 (id=1): Left=P3, Right=P2
P2 (id=2): Left=P1, Right=P3
P3 (id=3): Left=P2, Right=P1
```

**Funzione chiave**: `map_player_data_in_group()`
- Mappa dati da `participant.vars` ai campi `received_*` del player
- Implementa logica "Postman" (ogni player riceve ciò che gli altri hanno inviato a lui)

**Logica Payoff**:
1. Tutti scelgono "Both" → tutti ricevono £4
2. Match pairwise (P1-P2, P2-P3, P3-P1) → coppia riceve £6, terzo £0
3. Nessun match → tutti ricevono £0 (disagreement)

**Dati salvati**:
- `part1_payoff` in `participant.vars`

---

### 3. `bargaining_tdl_part2` - Part 2: MPL Questions

**Scopo**: Matching Probability List (MPL) per misurare credenze probabilistiche

**Caratteristiche**:
- `PLAYERS_PER_GROUP = None` (task individuale)
- 12 domande MPL generate dinamicamente
- Doppia randomizzazione: ordine player + ordine domande

**Struttura MPL Questions**:
- 6 domande per "player on the left"
- 6 domande per "player on the right"
- Ogni gruppo ha 3 single events + 3 composite events

**Factory Pattern**:
Le 12 classi `MPLQuestion1-12` sono generate dinamicamente usando `create_mpl_question_class()`:
- Riduce duplicazione da ~170 righe a ~40 righe
- Mantiene funzionalità identica

**Randomizzazione**:
1. Ordine player: left_first o right_first
2. Shuffle completo delle domande per ogni player
3. Ordine salvato in `mpl_question_order` (JSON)

**Calcolo Payoff Part 2**:
Funzione `calculate_part2_payoff()`:
1. Selezione casuale domanda (1-12)
2. Estrazione pr1 (0-100)
3. Se pr1 < switching_point → Option 1 (verifica evento Part 1)
4. Altrimenti → Option 2 (estrazione pr2, confronto con pr1)

---

### 4. `bargaining_tdl_part3` - Part 3: Dictator Game

**Scopo**: Three-Person Dictator Game individuale

**Caratteristiche**:
- `PLAYERS_PER_GROUP = None` (task individuale)
- Scelta individuale senza raggruppamento
- Gruppi creati a posteriori dallo sperimentatore

**Payoff Finale**:
- Part 2 + max(Part 1, Part 3)
- Calcolato in `ResultsPart3.vars_for_template()`

---

## 🔗 Relazioni tra Moduli

### Flusso Dati

```
bargaining_tdl_intro
  ↓ (participant.vars)
bargaining_tdl_main
  ↓ (participant.vars: part1_payoff)
bargaining_tdl_part2
  ↓ (calcolo payoff Part 2)
bargaining_tdl_part3
  ↓ (payoff finale)
```

### Accesso Cross-Module

**Part 2 → Main**:
- `get_main_group_player()`: Recupera player dal gruppo di main
- `get_participant_role_in_group()`: Determina ruolo (A/B/C)

**Part 3 → Part 2**:
- `calculate_part2_payoff()`: Calcola payoff Part 2 se non già calcolato

**Part 3 → Main**:
- Accesso a `part1_payoff` da `participant.vars`

### Pattern di Comunicazione

1. **participant.vars**: Dati persistenti tra moduli
2. **Import dinamico**: `import_module()` per accesso cross-module
3. **Session.get_subsessions()**: Ricerca subsession di altri moduli

---

## 🎨 Pattern e Convenzioni

### Time Tracking

Ogni pagina include:
- Campo `time_on_page` (hidden field)
- JavaScript tracking automatico (in `_templates/global/Page.html`)
- Salvataggio in `before_next_page()` usando `save_time_value()`

Pattern:
```python
@staticmethod
def before_next_page(player, timeout_happened):
    player.time_page_name = save_time_value(player.time_on_page)
```

### Control Questions

Pattern standardizzato:
1. Validazione in `before_next_page()`
2. Salvataggio flag con `set_control_questions_failed()`
3. Redirect con `is_displayed()` usando `has_failed_control_questions()`

### Naming Conventions

- **Campi time**: `time_<page_name>`
- **Campi received**: `received_<type>_<direction>` (es. `received_history_left`)
- **Flag control questions**: `failed_control_questions_<part>`
- **Campi MPL**: `E<L|R><number>_switch_value` (es. `EL1_switch_value`)

### Error Handling

- Funzioni cross-module ritornano `None` in caso di errore
- Logging con `print()` per debug
- Fallback values per dati mancanti

---

## 🔧 Configurazione

### `settings.py`

```python
SESSION_CONFIGS = [
    dict(
        name='bargaining_tdl',
        display_name="Bargaining Game (TDL + Async)",
        app_sequence=[
            'bargaining_tdl_intro',
            'bargaining_tdl_main',
            'bargaining_tdl_part2',
            'bargaining_tdl_part3'
        ],
        num_demo_participants=6,
    ),
]
```

### Costanti Globali

- `REAL_WORLD_CURRENCY_CODE = 'GBP'`
- `LANGUAGE_CODE = 'en'`
- `USE_POINTS = False`

---

## 📊 Struttura Dati

### Player Model Fields

**bargaining_tdl_intro**:
- `draft_history_left`, `draft_history_right`
- `signal_left`, `signal_right`
- `first_intention_selected`
- Control questions (example1/2/3, payoff_determination)
- Time tracking fields

**bargaining_tdl_main**:
- `decision_choice` (Left/Right/Both)
- `received_history_left/right`
- `received_signal_left/right`
- Time tracking fields

**bargaining_tdl_part2**:
- 12 campi `E<L|R><number>_switch_value`
- 12 campi `E<L|R><number>_choices` (JSON)
- `mpl_player_order`, `mpl_question_order`
- Control questions Part 2
- Time tracking fields (1 per ogni MPL question)

**bargaining_tdl_part3**:
- `decision` (share_left/right/both)
- Control questions Part 3
- `all_control_questions_correct` (flag)
- Time tracking fields

### participant.vars

Dati persistenti tra moduli:
- `draft_history_left/right`
- `signal_left/right`
- `failed_control_questions` (intro/part2/part3)
- `part1_payoff`
- `part2_payoff_data`
- `part2_payoff`
- `current_display_order` (MPL)
- `current_question_num_original` (MPL)

---

## 🧪 Testing

### Struttura Test

Ogni modulo ha un file `tests.py` con:
- `PlayerBot` per simulare partecipanti
- Test cases per scenari specifici
- Verifica payoff e logica di gruppo

### Test Manuale

1. Avviare server: `otree devserver 8000`
2. Navigare a `http://localhost:8000/demo`
3. Creare sessione demo
4. Testare flusso completo con 6 partecipanti

---

## 🔄 Refactoring Recente

### Miglioramenti Implementati

1. **Modulo Comune**: Centralizzazione codice duplicato
2. **Factory Pattern**: Generazione dinamica classi MPLQuestion
3. **Standardizzazione**: Pattern consistenti per control questions
4. **Helper Functions**: Mapping logica semplificata

### Riduzione Codice

- **Duplicazione ridotta**: ~40%
- **Righe rimosse**: ~66 nette (commit 1)
- **Manutenibilità**: Significativamente migliorata

---

## 📝 Note Tecniche

### oTree Specifics

- **WaitPages**: Usate per sincronizzazione (GroupingWaitPage, ResultsWaitPage)
- **group_by_arrival_time**: Raggruppamento dinamico in main
- **app_after_this_page()**: Controllo flusso tra app
- **is_displayed()**: Controllo condizionale pagine

### Performance

- Import lazy per evitare import circolari
- Caching di dati calcolati in `participant.vars`
- Generazione MPL questions una sola volta per partecipante

### Sicurezza

- Validazione control questions prima di procedere
- Sanitizzazione input con `save_time_value()`
- Fallback values per dati mancanti

---

## 🚀 Estensioni Future

### Miglioramenti Implementati ✅

1. **TimeTrackedPage Mixin**: ✅ Implementato mixin base per automatizzare time tracking
   - Classe base `TimeTrackedPage` in `bargaining_tdl_common/mixins.py`
   - Richiede `time_field_name` esplicito nella sottoclasse
   - Logging automatico di warning se `time_field_name` non è definito

2. **Caching**: ✅ Cache per `get_main_group_player()` implementata
   - Usa `@lru_cache(maxsize=128)` per memorizzare risultati
   - Riduce lookup multipli nel database
   - Cache trasparente: nessun cambio API necessario

3. **Logging**: ✅ Sistema di logging strutturato implementato
   - Modulo `bargaining_tdl_common/logger.py`
   - Sostituisce tutti i `print()` con logger strutturato
   - Formatter con timestamp e livello
   - Funzioni di convenienza: `info()`, `warning()`, `error()`, `debug()`

4. **Documentazione**: ✅ Docstring migliorate per funzioni complesse
   - `map_player_data_in_group()`: Documentazione completa della topology
   - `generate_mpl_questions()`: Documentazione dettagliata della randomizzazione
   - `calculate_part2_payoff()`: Documentazione dell'algoritmo di calcolo
   - `load_part1_data_for_mpl()`: Documentazione della logica di mapping
   - `generate_option1_single_event()` e `generate_option1_composite_event()`: Esempi d'uso

5. **Testing**: ✅ Test suite base creata
   - `bargaining_tdl_common/tests.py`: Test per helpers, validators, logger
   - Test esistenti migliorati con docstring
   - Struttura pronta per test di integrazione

### Possibili Miglioramenti Futuri

1. **TimeTrackedPage Mixin**: Migliorare per inferire automaticamente `time_field_name` dal nome classe
2. **Test Coverage**: Aumentare coverage dei test automatizzati
3. **Performance Monitoring**: Aggiungere metriche di performance per operazioni critiche
4. **Error Handling**: Standardizzare gestione errori con custom exceptions

---

## 📚 Riferimenti

- **oTree Documentation**: https://www.otree.org/
- **Paper**: `docs/DPPT_10_11_25_Paper.pdf`
- **Istruzioni**: `docs/DPPT__22_11_25_Instruction.pdf`
- **Testing Guide**: `docs/TESTING.md`

---

**Ultimo aggiornamento**: Dopo refactoring alta/media priorità  
**Versione oTree**: 5.11.4  
**Python**: 3.11+

