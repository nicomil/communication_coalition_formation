# Piano Esecutivo: Implementazione Payoff Function Part 2

## 📋 Overview

Implementare la funzione di payoff per la Part 2 che determina il pagamento basandosi su:
1. Selezione casuale di una delle 12 domande MPL
2. Estrazione di probabilità random e confronto con switching point
3. Verifica eventi Part 1 (per Option 1) o estrazione seconda probabilità (per Option 2)

**Obiettivo**: Creare una funzione che calcoli il payoff della Part 2 e lo salvi per il calcolo finale dell'esperimento.

---

## ⚠️ PRINCIPI FONDAMENTALI

1. **NON MODIFICARE** la struttura esistente della Part 2
2. **PRESERVARE** tutti i dati esistenti (switching points, scelte MPL)
3. **ACCEDERE CORRETTAMENTE** ai dati della Part 1 per verificare eventi
4. **SALVARE** il payoff calcolato in `participant.vars` per uso futuro
5. **ESECUZIONE**: La funzione deve essere eseguita alla fine della Part 3 (o quando necessario)

---

## 🎯 Flusso della Payoff Function

### Step 1: Selezione Casuale Domanda
- Scegliere casualmente una delle 12 domande MPL (1-12)
- Recuperare lo switching point per quella domanda
- Recuperare i metadati della domanda (tipo, event_codes, target_code)

### Step 2: Estrazione Probabilità Random (pr1)
- Estrarre un numero casuale tra 0 e 100 (inclusi)
- Questo è `pr1`

### Step 3: Decisione Option 1 vs Option 2
- Se `pr1 < switching_point`: **Scenario 2.1** (Option 1)
- Se `pr1 >= switching_point`: **Scenario 2.2** (Option 2)

### Step 4a: Scenario 2.1 - Verifica Evento Part 1
- Verificare se l'evento a cui si riferisce la domanda è realmente accaduto nella Part 1
- Se l'evento è accaduto: payoff = £5 (o cu(5))
- Se l'evento non è accaduto: payoff = £0 (o cu(0))

### Step 4b: Scenario 2.2 - Estrazione Seconda Probabilità
- Estrarre un secondo numero casuale tra 0 e 99 (inclusi): `pr2`
- Se `pr2 <= pr1`: payoff = £5 (o cu(5))
- Se `pr2 > pr1`: payoff = £0 (o cu(0))

---

## 📦 Task 1: Creare Funzione di Mapping Eventi → Scelte Part 1

### 1.1 Mapping Event Codes → Decision Choices

**File**: `bargaining_tdl_part2/__init__.py`

**Funzione**: `map_event_code_to_decision_choice(event_code: str) -> str`

Mappare i codici evento alle scelte effettive della Part 1:

```python
# Mapping Event Codes → Decision Choices
EVENT_TO_DECISION = {
    'EB1': 'Right',  # B divide with C only (Share only with the player on the right)
    'EB2': 'Left',   # B divide with A only (Share only with you = Left per A)
    'EB3': 'Both',   # B divide among all three
    'EC1': 'Left',   # C divide with B only (Share only with the player on the left)
    'EC2': 'Right',  # C divide with A only (Share only with you = Right per A)
    'EC3': 'Both',   # C divide among all three
    'EA1': 'Right',  # A divide with C only (Share only with the player on the right)
    'EA2': 'Left',   # A divide with B only (Share only with you = Left per B)
    'EA3': 'Both',   # A divide among all three
}
```

**Nota**: Il mapping dipende dalla prospettiva del giocatore. Deve essere verificato in base alla struttura reale delle domande.

### 1.2 Funzione Helper per Verificare Evento

**Funzione**: `check_event_occurred_in_part1(player: Player, target_code: str, event_codes: list[str]) -> bool`

**Logica**:
1. Recuperare il player target dalla Part 1 (usando `get_main_group_player` o simile)
2. Ottenere la `decision_choice` del target player
3. Per ogni `event_code` in `event_codes`:
   - Mappare `event_code` a `decision_choice` attesa
   - Verificare se la scelta del target corrisponde
4. Per Single Event: verificare un solo evento
5. Per Composite Event: verificare se ALMENO UNO degli eventi è accaduto (OR logico)

**Esempio**:
```python
def check_event_occurred_in_part1(player: Player, target_code: str, event_codes: list[str]) -> bool:
    """
    Verifica se l'evento (o almeno uno degli eventi per composite) è accaduto nella Part 1.
    
    Args:
        player: Player corrente (Part 2)
        target_code: 'A', 'B', o 'C' (chi ha fatto la scelta)
        event_codes: Lista di codici evento (es. ['EB1'] o ['EB2', 'EB3'])
    
    Returns:
        True se l'evento è accaduto, False altrimenti
    """
    # Recupera il target player dalla Part 1
    target_player = get_target_player_from_part1(player, target_code)
    if target_player is None:
        return False
    
    # Ottieni la scelta effettiva del target
    actual_choice = target_player.decision_choice  # 'Left', 'Right', o 'Both'
    
    # Per ogni evento, verifica se è accaduto
    for event_code in event_codes:
        expected_choice = EVENT_TO_DECISION.get(event_code)
        if expected_choice == actual_choice:
            return True  # Almeno un evento è accaduto (OR logico per composite)
    
    return False
```

---

## 📦 Task 2: Creare Funzione Helper per Recuperare Target Player

### 2.1 Funzione `get_target_player_from_part1`

**File**: `bargaining_tdl_part2/__init__.py`

**Funzione**: `get_target_player_from_part1(player: Player, target_code: str) -> Player`

**Logica**:
1. Recuperare il gruppo della Part 1 (usando `get_main_group_player` come riferimento)
2. Trovare il player con il ruolo corrispondente a `target_code`:
   - 'A' → id_in_group = 1
   - 'B' → id_in_group = 2
   - 'C' → id_in_group = 3
3. Restituire il player target

**Esempio**:
```python
def get_target_player_from_part1(player: Player, target_code: str):
    """
    Recupera il target player dalla Part 1.
    
    Args:
        player: Player corrente (Part 2)
        target_code: 'A', 'B', o 'C'
    
    Returns:
        Player della Part 1 corrispondente al target_code, o None se non trovato
    """
    from importlib import import_module
    main_app = import_module('bargaining_tdl_main')
    MainPlayer = main_app.Player
    MainSubsession = main_app.Subsession
    
    # Recupera il gruppo della Part 1
    main_player = get_main_group_player(player)
    if main_player is None:
        return None
    
    group = main_player.group
    
    # Mapping target_code → id_in_group
    target_id_map = {'A': 1, 'B': 2, 'C': 3}
    target_id = target_id_map.get(target_code)
    if target_id is None:
        return None
    
    # Trova il player con quell'id
    target_player = group.get_player_by_id(target_id)
    return target_player
```

---

## 📦 Task 3: Creare Funzione Principale Payoff Part 2

### 3.1 Funzione `calculate_part2_payoff`

**File**: `bargaining_tdl_part2/__init__.py`

**Funzione**: `calculate_part2_payoff(player: Player) -> dict`

**Logica Completa**:

```python
def calculate_part2_payoff(player: Player) -> dict:
    """
    Calcola il payoff della Part 2 seguendo la logica specificata.
    
    Returns:
        Dict con:
        - 'payoff': Currency (cu(5) o cu(0))
        - 'selected_question': int (1-12)
        - 'switching_point': int
        - 'pr1': int (0-100)
        - 'pr2': int (0-99) o None
        - 'option_selected': str ('Option 1' o 'Option 2')
        - 'event_occurred': bool (solo per Option 1)
        - 'payoff_amount': int (5 o 0)
    """
    import random
    
    # Step 1: Selezione casuale domanda (1-12)
    selected_question_num = random.randint(1, 12)
    
    # Recupera switching point
    switch_field_name = f'mpl_question_{selected_question_num}_switch_value'
    switching_point = getattr(player, switch_field_name, None)
    
    if switching_point is None:
        # Se non c'è switching point, payoff = 0
        return {
            'payoff': cu(0),
            'selected_question': selected_question_num,
            'switching_point': None,
            'pr1': None,
            'pr2': None,
            'option_selected': None,
            'event_occurred': None,
            'payoff_amount': 0
        }
    
    # Step 2: Estrai pr1 (0-100)
    pr1 = random.randint(0, 100)
    
    # Step 3: Decisione Option 1 vs Option 2
    if pr1 < switching_point:
        # Scenario 2.1: Option 1 - Verifica evento Part 1
        # Recupera metadati della domanda
        questions = generate_mpl_questions(player)
        selected_question = questions[selected_question_num - 1]  # -1 perché lista è 0-indexed
        
        target_code = selected_question['target_code']
        event_codes = selected_question['event_codes']
        
        # Verifica se evento è accaduto
        event_occurred = check_event_occurred_in_part1(player, target_code, event_codes)
        
        payoff_amount = 5 if event_occurred else 0
        
        return {
            'payoff': cu(payoff_amount),
            'selected_question': selected_question_num,
            'switching_point': switching_point,
            'pr1': pr1,
            'pr2': None,
            'option_selected': 'Option 1',
            'event_occurred': event_occurred,
            'payoff_amount': payoff_amount
        }
    else:
        # Scenario 2.2: Option 2 - Estrai pr2
        pr2 = random.randint(0, 99)
        
        # Se pr2 <= pr1, vinci £5
        payoff_amount = 5 if pr2 <= pr1 else 0
        
        return {
            'payoff': cu(payoff_amount),
            'selected_question': selected_question_num,
            'switching_point': switching_point,
            'pr1': pr1,
            'pr2': pr2,
            'option_selected': 'Option 2',
            'event_occurred': None,
            'payoff_amount': payoff_amount
        }
```

---

## 📦 Task 4: Integrare Payoff Function nella Part 3

### 4.1 Eseguire Payoff Function alla Fine Part 3

**File**: `bargaining_tdl_part3/__init__.py`

**Classe**: `ResultsPart3` (o nuova pagina `PayoffCalculation`)

**Metodo**: `before_next_page()` o `vars_for_template()`

**Logica**:
1. Importare la funzione `calculate_part2_payoff` da `bargaining_tdl_part2`
2. Eseguire la funzione per calcolare il payoff Part 2
3. Salvare il risultato in `player.participant.vars['part2_payoff_data']`
4. Salvare anche il payoff come `player.participant.vars['part2_payoff']` (Currency)

**Esempio**:
```python
@staticmethod
def before_next_page(player, timeout_happened):
    """Calcola e salva il payoff della Part 2."""
    from bargaining_tdl_part2 import calculate_part2_payoff
    
    # Calcola payoff Part 2
    part2_payoff_data = calculate_part2_payoff(player)
    
    # Salva in participant.vars
    player.participant.vars['part2_payoff_data'] = part2_payoff_data
    player.participant.vars['part2_payoff'] = part2_payoff_data['payoff']
```

---

## 📦 Task 5: Aggiungere Campi Player per Salvare Dati Payoff (Opzionale)

### 5.1 Campi Opzionali in Player Model

**File**: `bargaining_tdl_part2/__init__.py`

**Campi** (opzionali, se si vuole salvare nel database):
```python
# Payoff calculation results (opzionale)
part2_selected_question = models.IntegerField(blank=True)
part2_pr1 = models.IntegerField(blank=True)
part2_pr2 = models.IntegerField(blank=True)
part2_option_selected = models.StringField(blank=True)
part2_payoff = models.CurrencyField(blank=True)
```

**Nota**: Questi campi sono opzionali se si preferisce salvare solo in `participant.vars`.

---

## 📦 Task 6: Verificare Mapping Eventi → Decision Choices

### 6.1 Test Mapping

**File**: `bargaining_tdl_part2/tests.py` (o nuovo file di test)

**Test da eseguire**:
1. Verificare che ogni `event_code` mappi correttamente a una `decision_choice`
2. Verificare che la logica di verifica eventi funzioni per Single Event
3. Verificare che la logica di verifica eventi funzioni per Composite Event (OR logico)
4. Testare la funzione `calculate_part2_payoff` con diversi scenari

---

## 📦 Task 7: Gestire Edge Cases

### 7.1 Casi Particolari

1. **Switching point mancante**: Se un partecipante non ha risposto a una domanda, payoff = 0
2. **Dati Part 1 mancanti**: Se non si riesce a recuperare i dati della Part 1, payoff = 0
3. **Target player non trovato**: Se il target player non esiste, payoff = 0
4. **Random seed**: Considerare se usare un seed deterministico per riproducibilità (opzionale)

---

## 📦 Task 8: Documentazione e Commenti

### 8.1 Aggiungere Docstring

- Documentare ogni funzione con descrizione, parametri e return
- Spiegare la logica di mapping eventi
- Commentare i casi edge

---

## ✅ Checklist Finale

- [ ] Funzione `map_event_code_to_decision_choice` implementata e testata
- [ ] Funzione `check_event_occurred_in_part1` implementata e testata
- [ ] Funzione `get_target_player_from_part1` implementata e testata
- [ ] Funzione `calculate_part2_payoff` implementata e testata
- [ ] Integrazione nella Part 3 completata
- [ ] Payoff salvato in `participant.vars`
- [ ] Test per tutti gli scenari (Option 1, Option 2, edge cases)
- [ ] Documentazione completa

---

## 🎯 Note Implementative

1. **Random Seed**: Considerare se usare un seed basato su session/participant per riproducibilità
2. **Valuta**: Usare `cu(5)` e `cu(0)` invece di valori hardcoded
3. **Accesso Dati Part 1**: Verificare che l'accesso ai dati della Part 1 funzioni correttamente tra app diverse
4. **Performance**: La funzione `generate_mpl_questions` potrebbe essere costosa - considerare caching se necessario
5. **Logging**: Considerare di loggare i risultati del calcolo per debugging

---

## 📚 Riferimenti

- `bargaining_tdl_part2/__init__.py` - Struttura esistente Part 2
- `bargaining_tdl_main/__init__.py` - Dati Part 1 (decision_choice)
- `bargaining_tdl_part3/__init__.py` - Integrazione payoff function
