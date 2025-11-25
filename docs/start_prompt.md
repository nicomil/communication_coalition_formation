# Prompt per Generazione Esperimento oTree

## Obiettivo
Genera un nuovo esperimento oTree basato sul paper generale (`DPPT_10_11_25_Paper.pdf`) e sulle istruzioni dettagliate (`DPPT__22_11_25_Instruction.pdf`).

## Regole Fondamentali

### Priorità delle Fonti
**LE ISTRUZIONI HANNO SEMPRE PRIORITÀ SUL PAPER**

Quando ci sono differenze tra il paper e le istruzioni, **usa SEMPRE le istruzioni**. Esempi specifici:

1. **Terminologia dei partecipanti:**
   - ❌ Paper: `b1`, `g1`, `b2`, `g2`, ecc.
   - ✅ Istruzioni: `player_on_the_left`, `player_on_the_right`
   - **Usa la terminologia delle istruzioni**

2. **Valuta:**
   - ❌ Paper: Euro (€)
   - ✅ Istruzioni: Sterline inglesi (£)
   - **Usa sempre le sterline nelle istruzioni e nel codice**

3. **Qualsiasi altra differenza:**
   - Se il paper dice X ma le istruzioni dicono Y, usa sempre Y

### Struttura del Codice oTree

Segui la struttura standard degli esperimenti oTree presenti nella codebase. Esamina gli esperimenti esistenti come riferimento:
- `prisoner/__init__.py`
- `trust/__init__.py`
- `dictator/__init__.py`
- `bargaining/__init__.py`
- `cournot/__init__.py`

#### Componenti Standard

1. **Import e Documentazione:**
```python
from otree.api import *

doc = """
Descrizione dell'esperimento basata sulle istruzioni.
"""
```

2. **Classe Constants (C):**
```python
class C(BaseConstants):
    NAME_IN_URL = 'nome_esperimento'  # nome della cartella
    PLAYERS_PER_GROUP = 2  # o il numero appropriato
    NUM_ROUNDS = 1  # o il numero appropriato
    # Aggiungi altre costanti necessarie
    # Usa cu() per valori monetari (sterline)
```

3. **Classe Subsession:**
```python
class Subsession(BaseSubsession):
    pass
    # Aggiungi metodi se necessario (es. creating_session)
```

4. **Classe Group:**
```python
class Group(BaseGroup):
    # Aggiungi campi a livello di gruppo se necessario
    pass
```

5. **Classe Player:**
```python
class Player(BasePlayer):
    # Aggiungi campi per le decisioni dei giocatori
    # Usa models.CurrencyField per valori monetari
    # Usa models.IntegerField per numeri interi
    # Usa models.BooleanField per scelte binarie
    # Usa models.StringField per testo
```

6. **Funzioni:**
```python
# FUNCTIONS
def set_payoffs(group: Group):
    # Calcola i payoff basandoti sulle istruzioni
    pass

def other_player(player: Player):
    # Helper per ottenere l'altro giocatore
    return player.get_others_in_group()[0]
```

7. **Pagine (Pages):**
```python
# PAGES
class Introduction(Page):
    pass
    # timeout_seconds se necessario

class Decision(Page):  # o nome appropriato
    form_model = 'player'  # o 'group'
    form_fields = ['campo1', 'campo2']  # campi del form

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    body_text = "Waiting for other participants..."  # opzionale

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Variabili da passare al template
        return dict(...)

page_sequence = [Introduction, Decision, ResultsWaitPage, Results]
```

### Template HTML

**IMPORTANTE:** Non usare un template fisso. Analizza attentamente il file delle istruzioni (`DPPT__22_11_25_Instruction.pdf`) per determinare:

1. **Quanti step/fasi ci sono nell'esperimento** - Identifica tutte le fasi distinte descritte nelle istruzioni
2. **Quali sono i nomi appropriati per ogni fase** - Usa la terminologia esatta delle istruzioni (es. se le istruzioni parlano di "Fase 1: Introduzione", "Fase 2: Decisione", "Fase 3: Risultati", usa quei nomi)
3. **Quanti template HTML servono** - Crea un template per ogni fase identificata

**Processo di identificazione:**
- Leggi le istruzioni sezione per sezione
- Identifica ogni fase distinta (introduzione, istruzioni, decisioni, comunicazioni, risultati, ecc.)
- Nota se ci sono fasi diverse per ruoli diversi (es. player_on_the_left fa una cosa, player_on_the_right ne fa un'altra)
- Determina se servono WaitPage tra le fasi
- Assegna un nome appropriato a ogni fase basandoti sulla terminologia delle istruzioni

**Esempi di possibili fasi (da dedurre dalle istruzioni):**
- Introduzione iniziale
- Istruzioni dettagliate
- Fase di comunicazione (se presente)
- Fase di decisione (potrebbero esserci più fasi di decisione)
- Fase di attesa
- Risultati finali
- Ecc.

**Struttura Bootstrap standard per i template:**
```html
<div class="card bg-light m-3">
    <div class="card-body">
        <!-- Contenuto specifico della fase -->
    </div>
</div>
```

**Nota:** Il numero e i nomi dei template devono riflettere esattamente la struttura descritta nelle istruzioni, non un template generico.

### Convenzioni di Codice

1. **Valute:**
   - Usa sempre `cu()` per valori monetari (es. `cu(100)` per 100 sterline)
   - Nei template, usa `{{ C.NOME_COSTANTE }}` per mostrare valori

2. **Nomi dei giocatori:**
   - Usa `player_on_the_left` e `player_on_the_right` invece di `b1`, `g1`, ecc.
   - Se necessario, crea helper functions per identificare i giocatori

3. **Ruoli:**
   - Se ci sono ruoli diversi, usa `id_in_group` o crea campi specifici
   - Esempio: `player.id_in_group == 1` per identificare il primo giocatore

4. **Payoff:**
   - Calcola sempre i payoff nella funzione `set_payoffs`
   - Assegna a `player.payoff` per ogni giocatore

### Checklist di Generazione

- [ ] Leggi attentamente le istruzioni (`DPPT__22_11_25_Instruction.pdf`)
- [ ] Identifica tutte le differenze con il paper e usa sempre le istruzioni
- [ ] **Analizza le istruzioni per identificare tutte le fasi/step dell'esperimento**
- [ ] **Determina il numero e i nomi dei template HTML necessari basandoti sulle fasi identificate**
- [ ] Determina il numero di giocatori per gruppo
- [ ] Determina il numero di round
- [ ] Identifica tutte le decisioni che i giocatori devono prendere
- [ ] Identifica la struttura dei payoff
- [ ] Crea la struttura base del codice seguendo gli esempi esistenti
- [ ] **Crea i template HTML con nomi appropriati basati sulle fasi identificate nelle istruzioni**
- [ ] Usa sterline (£) invece di euro (€)
- [ ] Usa `player_on_the_left`/`player_on_the_right` invece di `b1`/`g1`
- [ ] Testa la logica dei payoff
- [ ] Verifica che tutte le pagine siano nella `page_sequence` e corrispondano alle fasi identificate

### Note Importanti

1. **Non inventare dettagli:** Se qualcosa non è specificato nelle istruzioni, fai riferimento al paper, ma mantieni la terminologia delle istruzioni.

2. **Coerenza:** Mantieni coerenza con gli altri esperimenti nella codebase per quanto riguarda stile e struttura.

3. **Validazione:** Aggiungi validazione appropriata ai campi (min, max, choices, ecc.)

4. **WaitPages:** Usa `WaitPage` quando i giocatori devono aspettare gli altri prima di procedere.

5. **Display condizionale:** Usa `is_displayed()` se alcune pagine devono essere mostrate solo a certi giocatori.

### Esempio di Mapping Terminologia

| Paper | Istruzioni | Codice oTree |
|-------|------------|--------------|
| b1, g1 | player_on_the_left, player_on_the_right | `player.id_in_group == 1` per left, `== 2` per right |
| Euro (€) | Sterline (£) | `cu()` con valori in sterline |
| Participant A/B | player_on_the_left/right | Usa la terminologia delle istruzioni |

## Processo di Generazione

1. **Analisi:** Leggi entrambi i documenti e identifica:
   - Struttura dell'esperimento
   - **Tutte le fasi/step descritte nelle istruzioni (introduzione, istruzioni, decisioni, comunicazioni, risultati, ecc.)**
   - **Numero e nomi appropriati per ogni fase**
   - Decisioni da prendere
   - Regole dei payoff
   - Differenze tra paper e istruzioni

2. **Progettazione:** 
   - Definisci la struttura delle classi
   - Identifica i campi necessari
   - **Pianifica la sequenza delle pagine basandoti sulle fasi identificate nelle istruzioni**
   - **Determina quali template HTML creare e con quali nomi**

3. **Implementazione:**
   - Crea `__init__.py` con tutte le classi e funzioni
   - **Crea i template HTML con nomi che riflettono le fasi identificate nelle istruzioni**
   - Implementa la logica dei payoff

4. **Verifica:**
   - Controlla che tutte le differenze paper/istruzioni siano risolte
   - Verifica che la terminologia sia corretta
   - Testa la logica

## Output Atteso

Un nuovo esperimento oTree completo con:
- File `__init__.py` nella cartella dell'esperimento
- Template HTML necessari
- Logica dei payoff corretta
- Terminologia basata sulle istruzioni
- Valute in sterline
- Struttura coerente con gli altri esperimenti

