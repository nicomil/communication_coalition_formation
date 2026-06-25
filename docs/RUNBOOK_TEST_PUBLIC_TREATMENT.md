# Runbook — Test del nuovo trattamento "Public communication"

Guida per provare in locale le nuove modifiche del branch
`feat/treatment-public-communication`.

## Cosa c'è di nuovo (in breve)

1. **Divisione equa 3,3,3** (globale): dividere il $12 "tra tutti e tre" ora paga
   **$3/$3/$3** invece di $4/$4/$4. Le altre divisioni restano 6/6/0 e 0/0/0.
2. **Trattamento "public"**: nella scelta finale (pagina *Decision*) il partecipante
   vede **anche la conversazione e i messaggi finali tra gli altri due** (es. il Green
   legge la chat Red↔Blue). Nel trattamento "private" (baseline) questo non accade.

L'assegnazione al trattamento è automatica e bilanciata (a blocchi di 3 per ordine di
arrivo). Per i test puoi usare le **session config isolate** così provi un solo
trattamento alla volta.

---

## 1. Setup (una tantum)

Servono Python 3.11 e git.

```bash
git clone git@github.com:nicomil/communication_coalition_formation.git
cd communication_coalition_formation
git checkout feat/treatment-public-communication

python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # config locale di default
```

---

## 2. Avvia il server

```bash
otree devserver
```

Apri http://localhost:8000 .

> La compatibilità con Starlette recente è gestita automaticamente in `settings.py`,
> quindi `otree devserver` funziona nativamente. (Resta disponibile `python
> run_devserver.py` come fallback, ma non è più necessario.)

---

## 3. Prova il NUOVO trattamento da solo (consigliato)

È un gioco **a 3 giocatori**: serve far avanzare **3 partecipanti insieme**.

1. Nell'admin oTree (http://localhost:8000), crea una sessione con la config
   **`bargaining_tdl_public`** e **3 partecipanti**.
2. Apri i **3 link partecipante** in 3 schede/finestre separate (meglio se una in
   incognito) e procedi in parallelo con tutte e tre.
3. Supera le **domande di controllo** (vedi sotto le risposte corrette), poi nella
   fase **Chat** scrivi qualche messaggio in ciascuna conversazione, invia i
   **messaggi finali** e arriva alla pagina **Decision**.

> Questa config attiva **solo** il trattamento "public": non serve tenere attivo il
> baseline. Per il baseline esiste `bargaining_tdl_private`.

### Risposte corrette alle domande di controllo (intro)
- Example 1: **$6 / $0 / $6**
- Example 2 (tutti dividono con tutti): **$3 / $3 / $3**  ← qui si vede il nuovo 3,3,3
- Example 3: **$0 / $0 / $0**

---

## 4. Cosa verificare (checklist)

- [ ] **3,3,3**: nelle istruzioni, nei messaggi finali e nell'opzione "dividi con
      entrambi" l'importo è **$3** (non più $4).
- [ ] **Reveal (solo public)**: sulla pagina *Decision* compare una terza sezione
      *"Conversation between the … and … Participants"* con la chat tra gli altri due
      e i loro **due messaggi finali**, etichettati col colore corretto.
- [ ] I messaggi della chat di terzi mostrano il **colore reale** di chi ha scritto
      (Red/Green/Blue), non "you" o "LeftPartner".
- [ ] Nel trattamento **private** (`bargaining_tdl_private`) quella terza sezione
      **non** compare (comportamento attuale invariato).

> Nota: i tre partecipanti hanno colori diversi, quindi ognuno vede come "terza
> coppia" gli altri due rispetto a sé.

---

## 5. (Opzionale) Altre config

- `bargaining_tdl_private` — solo baseline (chat privata).
- `bargaining_tdl` — produzione A/B: con 12 partecipanti assegna **6 private + 6
  public** in triadi omogenee (i due trattamenti non si mischiano mai nello stesso
  gruppo).

---

## 6. (Opzionale) Sanity check automatico veloce

Senza aprire schede, i bot fanno girare un'intera sessione:

```bash
otree test bargaining_tdl_public 9     # nuovo trattamento
otree test bargaining_tdl_private 9    # baseline
otree test bargaining_tdl 12           # A/B (6/6)
```

Deve comparire `Bots completed session` per ciascuno.

---

## Note

- Il **testo specifico delle istruzioni del ramo public** è ancora un segnaposto vuoto
  in `bargaining_tdl_intro/InstructionsPart1.html` (lo scriverà il responsabile): la
  meccanica funziona già, manca solo il testo informativo.
- I timer di pagina sono quelli reali; per i test manuali non serve attenderli, basta
  cliccare **Next**. Se preferisci timer brevi (60s), imposta `use_test_timers=True`
  in `settings.py` (solo per i test, NON in produzione).
