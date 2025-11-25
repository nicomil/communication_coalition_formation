# Prompt per Generazione Fase 1: Bargaining Game

## Contesto e Obiettivo
Sei un esperto di oTree. Il tuo compito è creare **SOLO la Fase 1** (Bargaining Game) dell'esperimento, basandoti sui seguenti documenti:
1.  `docs/DPPT__22_11_25_Instruction.pdf` (Istruzioni Fase 1 - **Fonte Primaria per terminologia e regole**)
2.  `docs/DPPT_10_11_25_Paper.pdf` (Sezione 3.1 e Pagina 5/6 - **Fonte per dettagli tecnici su segnali e chat**)
3.  `docs/start_prompt.md` (Linee guida generali di coding e struttura)
4. `docs/istruzioni.md` (suggerimenti dello sperimentatore )

**ATTENZIONE:** Ignora le Fasi 2 e 3 per ora. Concentrati esclusivamente sulla corretta implementazione della Fase 1.

## Specifiche Funzionali

### 1. Configurazione Gruppo e Ruoli
- **Partecipanti:** 3 giocatori per gruppo (Fixed matching per questa fase).
- **Terminologia (Obbligatoria):**
    - Usa sempre "Sterline (£)" (`cu()`) per la valuta.
    - Mappatura ruoli (dal Paper alle Istruzioni/UI):
        - `Participant A1` (Paper) -> **You**
        - `Participant B1` (Paper) -> **The player on the left**
        - `Participant C1` (Paper) -> **The player on the right**
- **Identificazione Relativa:** Ogni giocatore deve avere un riferimento dinamico a chi è "Left" e chi è "Right" (es. in un gruppo [1, 2, 3], per P1: Left=P3, Right=P2; o logica circolare equivalente).

### 2. Meccanismo di Gioco (Bargaining)
- **Surplus:** £12.
- **Opzioni di Scelta:** Ogni giocatore sceglie una delle 3 opzioni:
    1.  Dividere con Left (Tu: £6, Left: £6, Right: £0).
    2.  Dividere con Right (Tu: £6, Left: £0, Right: £6).
    3.  Dividere con Entrambi (Tu: £4, Left: £4, Right: £4).
- **Regola di Maggioranza:**
    - L'allocazione viene implementata SOLO se almeno 2 giocatori selezionano la **stessa distribuzione vettoriale** (coordinamento).
    - *Nota di implementazione:* "Tu scegli Left" (6,6,0) coincide con "Left sceglie Right" (6,6,0). Il codice deve verificare la corrispondenza dei vettori di payoff risultanti.
- **Disaccordo (TDL):** Se non c'è maggioranza (3 vettori diversi), il payoff è £0 per tutti (Total Deadweight Loss).

### 3. Interfaccia Chat (Pagina 5 Paper)
- **Layout:** La pagina di chat deve mostrare **due chatbox separate** affiancate (split verticale 50/50):
    - Sinistra: Chat con "The player on the left".
    - Destra: Chat con "The player on the right".
- **Funzionamento:** Comunicazione bilaterale privata. A parla con B (privato) e con C (privato).
- **Timer:** 3 minuti (180 secondi).
- **Implementazione Tecnica:** Usa `otree.chat` con canali specifici (es. `channel=group.id + "-1-2"`).

### 4. Segnali (Post-Chat)
Subito dopo la chat e prima della decisione, ogni giocatore DEVE inviare un segnale pre-definito a ciascuno degli altri due.
- **Input:** Due form field (uno per Left, uno per Right).
- **Opzioni (adattate dal Paper pag. 5):**
    1.  "I wish to split the payoff equally with YOU only."
    2.  "I wish to split the payoff equally with THE OTHER PLAYER only."
    3.  "I wish to split the payoff equally with both of the other participants."
    4.  "I do not wish to communicate my intentions."
- **Flusso:**
    1.  Page `Chat` (con timer).
    2.  Page `SendSignals` (Input segnali).
    3.  Page `ReadSignals` (Visualizzazione segnali ricevuti).
    4.  Page `Decision` (Scelta distribuzione).

## Struttura Codice Richiesta
Segui lo standard definito in `start_prompt.md`:
- `C` constants (PLAYERS_PER_GROUP=3, NUM_ROUNDS=1).
- `Group` model con funzioni per calcolo payoff e verifica maggioranza.
- `Player` model con campi per segnali (`signal_left`, `signal_right`) e decisione.
- **Template HTML:** Crea template distinti per `Chat.html`, `SendSignals.html`, `ReadSignals.html`, `Decision.html`, `Results.html`.
- **Stile:** Usa Bootstrap. Layout pulito. Mostra chiaramente i ruoli "Left" e "Right" nell'header delle card.

## Checklist Controllo
- [ ] La chat è divisa in due box distinti?
- [ ] I segnali vengono inviati DOPO la chat e PRIMA della decisione?
- [ ] La logica di maggioranza riconosce correttamente l'accordo tra (Tu->Left) e (Left->Right)?
- [ ] La valuta è in Sterline?

