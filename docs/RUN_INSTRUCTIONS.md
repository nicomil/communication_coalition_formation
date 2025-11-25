# Istruzioni di Avvio: Bargaining Game (TDL + Async)

Questo documento spiega come avviare l'esperimento composto dalle due app sequenziali (`bargaining_tdl_intro` -> `bargaining_tdl_main`).

## 1. Configurazione Ambiente (Virtual Environment)

Prima di iniziare, è fondamentale lavorare in un ambiente isolato per evitare conflitti tra librerie.

### Mac/Linux
```bash
# 1. Crea il virtual environment (solo la prima volta)
python3 -m venv venv

# 2. Attiva l'ambiente (fallo ogni volta che apri un nuovo terminale)
source venv/bin/activate

# 3. Installa le dipendenze (solo la prima volta o se cambiano)
pip install -r requirements.txt
```

### Windows
```bash
# 1. Crea il virtual environment (solo la prima volta)
python -m venv venv

# 2. Attiva l'ambiente (fallo ogni volta che apri un nuovo terminale)
.\venv\Scripts\activate

# 3. Installa le dipendenze (solo la prima volta o se cambiano)
pip install -r requirements.txt
```

*Nota: Se non hai un file `requirements.txt`, puoi installare oTree direttamente con `pip install otree`.*

---

## 2. Avvio Rapido (Sviluppo Locale)

Per testare l'esperimento mentre sviluppi:

```bash
# 1. Resetta il database (cancella vecchi dati per evitare conflitti)
otree resetdb

# 2. Avvia il server di sviluppo
otree devserver
```

Apri il browser su: `http://localhost:8000`

---

## 2. Simulazione con Bot (Browser Bots)

Per verificare che la logica di gruppo, i payoff e il passaggio dati funzionino correttamente senza dover cliccare manualmente:

```bash
# 1. Assicurati di aver creato la sessione "Bargaining Game (TDL + Async)"
# nella config di settings.py (dovrebbe già esserci).

# 2. Lancia i bot (esempio con 6 partecipanti per formare 2 gruppi da 3)
otree browser_bots bargaining_tdl 6
```

*Nota: `bargaining_tdl` è il nome della configurazione sessione definita in `settings.py`, che include la sequenza delle due app.*

---

## 3. Configurazione Sessione (`settings.py`)

Assicurati che la configurazione in `settings.py` sia corretta. Deve includere entrambe le app in sequenza:

```python
SESSION_CONFIGS = [
    dict(
        name='bargaining_tdl',
        display_name="Bargaining Game (TDL + Async)",
        app_sequence=[
            'bargaining_tdl_intro',  # App 1: Individuale
            'bargaining_tdl_main'    # App 2: Gruppo (WaitPage + Decisione)
        ],
        num_demo_participants=3,
    ),
]
```

## 4. Risoluzione Problemi Comuni

*   **Errore:** *TemplateSyntaxError* o *KeyError* sui campi `received_...`
    *   **Causa:** Probabilmente stai cercando di accedere a dati che non sono stati passati correttamente dallo "zaino" (`participant.vars`).
    *   **Soluzione:** Controlla la `GroupingWaitPage` in `bargaining_tdl_main/__init__.py` e verifica che le chiavi corrispondano a quelle salvate in `bargaining_tdl_intro`.

*   **Attesa Infinita nella WaitPage:**
    *   **Causa:** Non sono arrivati abbastanza partecipanti per formare un gruppo da 3.
    *   **Soluzione:** In devserver, usa il link "Advance slowest users" dalla console o dalla pagina di monitoraggio, oppure apri più tab del browser.

---

## 5. Deploy in Produzione (Server)

Se devi caricare su Heroku o un server Ubuntu:

1.  Crea il file `requirements.txt` aggiornato:
    ```bash
    pip freeze > requirements.txt
    ```
2.  Assicurati che `otree` sia presente nel file.
3.  Sul server, imposta `OTREE_PRODUCTION=1` nelle variabili d'ambiente.
4.  Esegui `otree resetdb` sul server prima della prima sessione reale.

