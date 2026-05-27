# Load Test Automatico (Heroku + oTree)

Questo test usa `locust` e i link unici `InitializeParticipant` generati da oTree.

## 1) Prerequisiti locali

Niente install manuale nella `.venv` del progetto.
Usa launcher `scripts/run_otree_loadtest.py`: crea/usa `.loadtest_venv` isolata.

## 2) Crea sessione test su Heroku

- In admin oTree, crea sessione con `num_participants = N` (es. 15 / 30 / 45).
- Imposta config test consigliata:
  - `use_test_timers=True`
  - `skip_intro_control_questions=True`
- Apri pagina `SessionStartLinks` e scarica/copi la tabella link.

## 3) Estrai link in file test

Salva export come CSV, poi:

```bash
python scripts/extract_otree_start_links.py /path/to/session_start_links.csv -o /tmp/start_links.txt
```

Output: un file con 1 link per riga.

## 4) Esegui load test (launcher consigliato)

```bash
python scripts/run_otree_loadtest.py \
  --links-file /tmp/start_links.txt \
  --host https://ccf-70e9cba78a52.herokuapp.com \
  --users 45 \
  --spawn-rate 12 \
  --run-time 8m \
  --label run_45
```

Output CSV in:

- `scripts/loadtest_results/run_45_stats.csv`
- `scripts/loadtest_results/run_45_failures.csv`
- `scripts/loadtest_results/run_45_exceptions.csv`

## 5) Monitoraggio Heroku durante test

```bash
heroku logs --tail --app ccf
heroku pg:info --app ccf
```

## 6) Riassunto automatico risultato

```bash
python scripts/summarize_locust_stats.py \
  scripts/loadtest_results/run_45_stats.csv \
  scripts/loadtest_results/run_45_failures.csv
```

## 7) Checklist critica per run 45 valido

- Usa **sessione nuova** con almeno 45 start links freschi (single-use).
- Non interrompere il run prima del `--run-time`.
- Usa config sessione test:
  - `use_test_timers=True`
  - `skip_intro_control_questions=True`
- Dopo run, controlla anche `SessionMonitor`/`SessionData` per stalli su wait/chat.

## 8) Limiti noti

- Questo test automatizza submit form HTML server-side.
- Pagine fortemente JS/websocket (chat/wait) possono risultare meno fedeli rispetto a browser reali.
- Per validazione end-to-end completa, aggiungi un test Playwright con pochi utenti (es. 5-10).
