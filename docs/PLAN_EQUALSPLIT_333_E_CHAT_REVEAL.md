# Piano d'azione — `3,3,3` globale + Framework multi-trattamento (chat privata/pubblica)

**Data:** 2026-06-24
**Autore:** Claude Code (per validazione del professore)
**Stato:** ✅ Decisioni del professore confermate (vedi Parte E) — pronto per l'implementazione. NESSUNA modifica al codice ancora applicata.
**Sostituisce:** la prima bozza (singola variante) — qui l'architettura è a **flussi alternativi randomizzati**.

---

## 0. Obiettivo (come concordato)

1. **`3,3,3` è un cambiamento GLOBALE.** La divisione "equa tra tutti e tre" passa da
   `$4/$4/$4` a `$3/$3/$3` **ovunque**, anche nella versione attuale (Part 1, intro,
   control questions, e Part 3). Non è una differenza tra trattamenti.
2. **L'unica differenza tra trattamenti è la CHAT:**
   - **`private`** (attuale): nella scelta finale vedi solo le conversazioni di cui hai
     fatto parte.
   - **`public`** (novità): nella scelta finale vedi **anche** la chat tra gli altri due
     partecipanti (es. Green legge la chat Red↔Blue).
3. **Meccanismo interno generico** per ospitare con semplicità **N esperimenti futuri**,
   non solo questi due.
4. **Randomizzazione interna a oTree** su **un solo link Prolific**: assegnazione casuale
   e bilanciata, con grouping che accoppia **solo partecipanti dello stesso trattamento e
   che hanno superato le control questions**.
5. **Testabilità isolata:** devo poter attivare **un solo trattamento** in una sessione
   (es. solo `public`) per testarlo **indipendentemente** dall'altro.

Flusso (invariato come app_sequence):
```
bargaining_tdl_intro → bargaining_tdl_main → bargaining_tdl_part3 → bargaining_tdl_survey
```

---

## PARTE A — Cambiamento globale `4,4,4 → 3,3,3`

> ⚠️ **Implicazione di design da confermare:** con `3,3,3` il totale distribuito diventa
> **$9** (restano $3 non assegnati). Le altre divisioni restano invariate: "con un solo
> partner" = `$6/$6/$0`; "disaccordo" = `$0/$0/$0`. Questo rende lo split equo meno
> efficiente. Confermare che è l'intenzione.

### A.1 Calcolo payoff (Part 1)

| File | Riga | Attuale | Nuovo |
|------|------|---------|-------|
| `bargaining_tdl_main/__init__.py` | 60 | `PAYOFF_SPLIT = cu(4)` | `PAYOFF_SPLIT = cu(3)` |

La logica payoff (`ResultsWaitPage.after_all_players_arrive`) usa già la costante → si
aggiorna da sola. `grp_coordinate`/`grp_triadicsplit` restano corretti.

### A.2 Testi visibili ($4 → $3)

- `bargaining_tdl_main/__init__.py:842` — dettaglio opzione "Both" su Decision.
- `bargaining_tdl_main/Signals.html:186-187, 225-227` — testo segnale "split with both".
- `bargaining_tdl_intro/_instructions_content.html:25, 59, 64` — "$4" / "earns $4".
- `bargaining_tdl_intro/__init__.py:411, 415, 417, 420` — scenari control questions.

### A.3 Control questions Intro (campi, opzioni, validatore, test)

- **Opzioni** `bargaining_tdl_intro/__init__.py:175-263`: il distrattore `['4','$4']`
  diventa `['3','$3']` in tutte e 9 le domande (opzioni → `$6 / $3 / $0`), perché `$4`
  non è più un payoff possibile.
- **Validatore** `bargaining_tdl_common/validators.py:154-156`:
  `example2_earnings_* == "4"` → `"3"`.
- **Bot test** `bargaining_tdl_intro/tests.py:48-50`: `'4'` → `'3'`.

### A.4 Part 3 (è parte della versione attuale → in scope)

- `bargaining_tdl_part3/__init__.py:196` e `InstructionsPart3.html:108` — label
  "share_both" `($4 …)` → `$3`.
- Control questions `__init__.py:76-127` — distrattore `['4','$4']` → `['3','$3']`.
- Scenari `ControlQuestionsPart3.html:37-39, 61-62` — verificare/aggiornare importi.
- Validatore `bargaining_tdl_common/validators.py:194-196` — `'4'` → `'3'`.
- Bot test `bargaining_tdl_part3/__init__.py:245-250` — `'4'` → `'3'`.
- **Payoff Part 3:** individuare dove "share_both" diventa importo monetario (calcolo
  finale, indicato in `bargaining_tdl_survey/FinalResults`) e portare 4→3.

### A.5 Test che usano la costante

`bargaining_tdl_main/tests.py:148` usa `C.PAYOFF_SPLIT` → resta valido (aggiornare solo
il commento `# 4` → `# 3`).

---

## PARTE B — Framework multi-trattamento

### B.1 Registry dei trattamenti (nuovo)

Nuovo modulo `bargaining_tdl_common/treatments.py`:

```python
TREATMENTS = {
    'private': {
        'label': 'Private communication (baseline)',
        'reveal_third_party_chat': False,
    },
    'public': {
        'label': 'Public communication',
        'reveal_third_party_chat': True,
    },
    # Esperimenti futuri: basta aggiungere una voce + il comportamento che essa controlla.
}

DEFAULT_ACTIVE_TREATMENTS = ['private', 'public']

def get_active_treatments(session):
    return session.config.get('active_treatments', DEFAULT_ACTIVE_TREATMENTS)

def get_treatment(player):
    return player.participant.vars.get('treatment', 'private')

def treatment_flag(player, key, default=None):
    return TREATMENTS.get(get_treatment(player), {}).get(key, default)
```

Aggiungere `'treatment'` a `PARTICIPANT_FIELDS` in `settings.py` (persistenza + export).

### B.2 Attivazione per sessione + test in isolamento

In `settings.py`, ogni session config può dichiarare quali trattamenti sono attivi.
Proposta di config:

```python
SESSION_CONFIGS = [
    # Produzione A/B: entrambi i trattamenti, randomizzati internamente
    dict(name='bargaining_tdl', ..., active_treatments=['private', 'public']),

    # Solo nuovo trattamento, per test ISOLATO indipendente dall'altro
    dict(name='bargaining_tdl_public', ..., active_treatments=['public']),

    # Solo baseline (se serve testarlo da solo)
    dict(name='bargaining_tdl_private', ..., active_treatments=['private']),
]
```

➡️ Per testare la comunicazione pubblica da sola: si lancia `bargaining_tdl_public`.
Nessuna dipendenza dall'altro trattamento. (`active_treatments` di default = entrambi.)

### B.3 Assegnazione bilanciata — BLOCCHI DI 3 per ORDINE DI ARRIVO

**Logica scelta (conferma prof.: blocchi di 3).** Poiché le istruzioni differiscono per
trattamento, l'assegnazione avviene **al primo accesso** (pagina `Welcome` dell'intro).
Un contatore a livello di sessione assegna i trattamenti **a blocchi di
`PLAYERS_PER_GROUP` (=3) per ordine di arrivo**: i primi 3 partecipanti che iniziano
vanno al Trattamento 1, i successivi 3 al Trattamento 2, i successivi 3 di nuovo al
Trattamento 1, e così via.

```python
# bargaining_tdl_intro: assegnazione sulla prima pagina (Welcome)
PLAYERS_PER_BLOCK = 3  # = bargaining_tdl_main.C.PLAYERS_PER_GROUP

def assign_treatment(player):
    p = player.participant
    if p.vars.get('treatment'):
        return p.vars['treatment']                       # idempotente
    active = get_active_treatments(player.session)
    counter = player.session.vars.get('treatment_counter', 0)
    block = counter // PLAYERS_PER_BLOCK                  # blocco corrente
    t = active[block % len(active)]                       # alterna i trattamenti per blocco
    player.session.vars['treatment_counter'] = counter + 1
    p.vars['treatment'] = t
    return t
```

- **Blocchi di 3 per arrivo**: ogni trattamento riceve i partecipanti a gruppi della
  dimensione esatta di una triade → la **prima triade di ciascun trattamento si chiude
  appena arrivano i suoi 3**, minimizzando l'attesa in sala.
- **Bilanciamento**: lo scarto fra i trattamenti resta entro un blocco (±3); su lotti
  multipli di 6 il bilanciamento è esatto.
- **Test isolato**: se `active` ha un solo elemento, tutti ricevono quel trattamento.
- **Idempotente**: l'assegnazione non cambia se il partecipante ricarica la pagina.
- **Nota operativa (gioco a 3):** dimensionare comunque i lotti Prolific come **multipli
  di 6** per chiudere le triadi senza "orfani" in sala d'attesa.
- L'assegnazione avviene **prima** delle istruzioni, così queste possono già differire.

### B.4 Grouping per trattamento + solo "passers" (Part 1)

Oggi `GroupingAfterControlQuestions(WaitPage)` usa `group_by_arrival_time = True`.
Chi fallisce le CQ termina già nell'intro (`Goodbye` → `app_after_this_page=[]`) e **non
arriva** al grouping. Aggiungiamo il matching per trattamento definendo, nella
`Subsession` di `bargaining_tdl_main`:

```python
def group_by_arrival_time_method(subsession, waiting_players):
    from collections import defaultdict
    from bargaining_tdl_common import has_failed_control_questions, get_treatment
    pools = defaultdict(list)
    for p in waiting_players:
        if has_failed_control_questions(p, 'intro'):   # difensivo
            continue
        pools[get_treatment(p)].append(p)
    for _t, players in pools.items():
        if len(players) >= C.PLAYERS_PER_GROUP:
            return players[:C.PLAYERS_PER_GROUP]
    return None
```

Così una triade è **sempre omogenea** per trattamento (requisito del gioco a 3) e
composta solo da chi ha superato le CQ. Conviene anche salvare il trattamento sul
`Player` (campo `treatment`) in `after_all_players_arrive` per chiarezza nei CSV.

### B.5 Istruzioni per trattamento (intro)

**Conferma prof.: il testo delle istruzioni lo scriverà direttamente lui in un secondo
momento.** Io predispongo solo l'**infrastruttura condizionale** (il "gancio"), lasciando
un **segnaposto** vuoto che il prof. compilerà.

- `bargaining_tdl_intro` pagine (`InstructionsPart1`, `_instructions_content.html`,
  ed eventualmente `ChatAndSignals` / `SimulatedChat`): passo in `vars_for_template`
  `treatment` e `reveal_third_party_chat`, e inserisco i blocchi condizionali
  ```django
  {% if reveal_third_party_chat %}
    {# === TESTO RAMO PUBLIC — da compilare a cura del prof. === #}
  {% else %}
    {# === eventuale testo specifico RAMO PRIVATE (di norma = attuale) === #}
  {% endif %}
  ```
- Nel ramo `private` il testo resta **identico all'attuale**. Nel ramo `public` il blocco
  è pronto ma vuoto, in attesa del testo del prof.
- Le control questions restano identiche tra trattamenti (la meccanica payoff non cambia
  tra `private`/`public`).

### B.6 La rivelazione — pagina `Decision` (solo ramo `public`)

**Conferma prof.: rivelare SIA la chat SIA i "Final Message" della coppia di terzi,
impaginati allo stesso modo di adesso.** Cioè la terza card replica la struttura delle due
esistenti: un box "Final Message" per ciascuno dei due + il log chat tra loro.

**B.6.a — Chat del terzo canale.**
Problema nickname: i messaggi sono salvati con nickname relativi
"LeftPartner"/"RightPartner" (`Chat.html:107,118`), illeggibili per un terzo. Quindi per
il terzo canale **non** si usa il widget live `{{ chat }}`, ma si leggono le righe dal DB
etichettando ogni messaggio col **colore reale** del mittente (HTML statico, sola lettura).

1. Nuovo helper in `bargaining_tdl_main/__init__.py` (sul modello di
   `_chat_rows_for_decision`, riga 438), es. `_third_party_chat_rows(player, channel)`:
   costruisce la mappa `participant.id → COLOR_MAPPING[id_in_group]` dai 3 player, legge i
   `ChatMessage` del canale ordinati per timestamp, e restituisce
   `{speaker: "<Color> Participant", body: …}`.
2. `Decision.vars_for_template`: calcolare il terzo canale
   ```python
   third_a, third_b = sorted((left_id, right_id))
   channel_third = f"{group_id}_{third_a}_{third_b}"
   ```

**B.6.b — Final Message tra i due partner (NUOVO, da conferma #3).**
Oggi `map_player_data_in_group` mappa solo i segnali **ricevuti dal viewer**. Per la coppia
di terzi servono i due segnali che i partner si sono inviati **a vicenda**:
- il segnale che il partner *left* ha inviato al partner *right*;
- il segnale che il partner *right* ha inviato al partner *left*.

Sono già disponibili: ogni player salva `signal_left`/`signal_right` (e in
`participant.vars`). Tramite la topologia si seleziona, dei due segnali di ciascun partner,
quello **diretto all'altro partner** (non quello diretto al viewer). Si riusa
`_signal_display_text(...)` per il testo, passando i colori corretti.

**B.6.c — Template `Decision.html`.**
Sotto le due card esistenti, dentro `{% if reveal_third_party_chat %}`, una terza card
"Conversation between the {{left_partner_color}} and {{right_partner_color}} Participants"
con: i due box "Final Message" (uno per partner, etichettati col colore) + il log
`third_chat_rows` (sola lettura, riuso stili `.read-only-chat`/`.message-box`).
Nel ramo `private` la sezione non compare → **comportamento attuale identico**.
Passare al template anche `reveal_third_party_chat = treatment_flag(player, 'reveal_third_party_chat')`.

---

## PARTE C — Export dati

- Aggiungere `treatment` a `PARTICIPANT_FIELDS` (B.1) e/o come campo `Player`, così i
  dataset distinguono gli arm.
- Verificare in `process_all_apps.py` che i payoff a `$3` e la colonna `treatment` siano
  riportati nei dataset core/full (`docs/EXPORT_DATA_DICTIONARY.md` da aggiornare).

---

## PARTE D — File impattati (riepilogo)

| Area | File | Modifica |
|------|------|----------|
| Registry trattamenti | `bargaining_tdl_common/treatments.py` (NUOVO) | TREATMENTS, helper, active_treatments |
| Common export | `bargaining_tdl_common/__init__.py` | esportare i nuovi helper |
| Settings | `settings.py` | `active_treatments` nelle session config + `'treatment'` in PARTICIPANT_FIELDS + nuove config per test isolato |
| Assegnazione | `bargaining_tdl_intro/__init__.py` (Welcome) | blocchi di 3 per ordine di arrivo (bilanciato) |
| Istruzioni | `bargaining_tdl_intro/*` | **gancio condizionale + segnaposto** (testo a cura del prof.) |
| Grouping | `bargaining_tdl_main/__init__.py` (Subsession) | `group_by_arrival_time_method` per trattamento + salvataggio `treatment` su Player |
| Reveal chat+segnali | `bargaining_tdl_main/__init__.py` + `Decision.html` | helper terzo canale + Final Message coppia di terzi + sezione condizionale |
| `3,3,3` globale | main / intro / part3 / common/validators / survey | vedi Parte A |
| Test | intro/part3/main `tests.py` | risposte 4→3; aggiungere smoke test per arm `public` |

---

## PARTE E — Decisioni del professore (CONFERMATE)

1. ✅ **Totale `3,3,3`:** confermato — $9 distribuiti ($3 non assegnati); altre divisioni
   invariate (6/6/0, 0/0/0).
2. ✅ **Part 3 in scope:** confermato — Part 1 e Part 3 allineate sulle distribuzioni.
3. ✅ **Reveal:** confermato — rivelare **sia la chat sia i "Final Message"** della coppia
   di terzi, **con la stessa impaginazione attuale** (vedi B.6).
4. ✅ **Istruzioni ramo `public`:** il **testo lo scriverà il prof.**; io predispongo solo
   il gancio condizionale + segnaposto (vedi B.5).
5. ✅ **Bilanciamento:** **a blocchi di 3 per ordine di arrivo** (vedi B.3). Nota
   operativa: dimensionare le sessioni come multipli di 6 per triadi pulite.

> Tutte le decisioni sono chiuse: il piano è pronto per l'implementazione.

---

## PARTE F — Verifica post-implementazione (dopo l'OK)

- **Test isolato nuovo trattamento:** lanciare `otree test bargaining_tdl_public 9` e su
  devserver verificare: payoff "Both" = $3, e sulla Decision compare la chat del terzo
  canale con i colori corretti.
- **Test baseline invariato:** `otree test bargaining_tdl_private 9` → nessuna terza
  sezione chat; comportamento attuale identico (i bot test esistenti restano la garanzia
  di non-regressione).
- **Test A/B:** `otree test bargaining_tdl 9/12` → triadi omogenee per trattamento,
  assegnazione bilanciata.
- **Export:** `python process_all_apps.py` → colonna `treatment` presente e payoff a $3.
