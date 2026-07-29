# Runbook pilot Prolific — RCT a tre bracci

## 1. Gate

Configurare:

```bash
heroku config:set OTREE_PRODUCTION=1 --app ccf
heroku config:set OTREE_AUTH_LEVEL=STUDY --app ccf
heroku config:set OTREE_ADMIN_PASSWORD='<password-forte>' --app ccf
heroku config:set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" --app ccf
heroku config:set PROLIFIC_COMPLETION_URL='https://app.prolific.com/submissions/complete?cc=<CODE>' --app ccf
```

Verificare:

```bash
python scripts/verify_production_gates.py
python scripts/verify_production_gates.py --url https://<app>.herokuapp.com
```

Non usare `otree resetdb` su produzione.

## 2. Creare la sessione unica

1. Admin oTree → **Rooms** → **Prolific participants**.
2. Crea/associa una sessione `bargaining_tdl`.
3. Dimensione: almeno quota Prolific + buffer CQ/dropout; per il pilot è
   prudente 2× quota.
4. Usa multipli di 9 quando possibile.

La sessione crea una schedule casuale in blocchi permutati. Ogni blocco
completo contiene:

- 3 `private`;
- 3 `public`;
- 3 `private_no_dwl`.

Il partecipante riceve il trattamento dopo aver inviato un Welcome valido.
Una CQ failure restituisce lo slot; il primo nuovo partecipante prende quello
slot e quindi lo stesso trattamento.

## 3. URL Prolific unico

Tipo studio: **External study**. Pubblicare solo:

```text
https://<app>.herokuapp.com/room/prolific?participant_label={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}
```

Non usare Taskflow, più studi, più condizioni Prolific o più URL. La
randomizzazione viene eseguita e registrata da oTree.

Impostazioni consigliate:

- Desktop only;
- Manual review;
- lingua primaria English;
- completion code uguale a `PROLIFIC_COMPLETION_URL`.

## 4. Smoke locale

Avvia:

```bash
otree devserver
```

Da admin crea una sessione nella room `prolific`, poi apri in anonimo:

```text
http://localhost:8000/room/prolific?participant_label=TEST_PID_001&STUDY_ID=TEST_STUDY&SESSION_ID=TEST_SESSION
```

Verificare:

1. Welcome riceve il PID.
2. Dopo Welcome compaiono le istruzioni del trattamento assegnato.
3. CQ Example 2 richiede `12,0,0` solo nel braccio No-DWL.
4. Dopo le CQ si formano solo triadi omogenee.
5. Decisione mostra solo Left, Right, No one.
6. Ogni messaggio finale richiede rating 1–5.
7. Le tre pagine SD3 compaiono subito dopo le demografiche.
8. Final Results include fee + Part 1 + domanda 11–20.
9. Redirect Prolific funziona.

## 5. Test automatici pre-pilot

Eseguire tutta `docs/TESTING.md`. Minimo:

```bash
otree test bargaining_tdl 18
OTREE_IN_MEMORY=1 python -m unittest test_rct_allocator.py
```

Scaricare e controllare:

- `all_apps_wide`;
- `RCT Assignments`;
- `RCT Slots`.

## 6. Audit RCT

Prima di aprire il reclutamento:

- `randomization_seed` presente;
- ogni blocco completo è 3:3:3;
- tutti gli assegnati hanno `assignment_status`;
- CQ failure ha `status=failed` e `resolution_reason`;
- il rimpiazzo usa stesso `slot_number`, trattamento e
  `attempt_number > 1`.

Conservare anche i soggetti CQ-failed: servono all'audit ITT.

## 7. Monitoraggio

Controllare a quote regolari:

| Segnale | Azione |
|---|---|
| errori 5xx ripetuti | pausa Prolific, controlla log |
| PID vuoti | verifica URL e `participant_label` |
| triade ferma >10 min | controlla waiting room/dropout |
| sessione vicina alla capacità | crea nuova sessione prima della saturazione |
| quota CQ-passed raggiunta | ferma reclutamento |

L'allocatore può reintegrare solo se restano partecipanti oTree non ancora
entrati. Da qui il buffer della sessione.

## 8. Blocco editoriale No-DWL

Le istruzioni `private_no_dwl` sono intenzionalmente una copia temporanea
delle Private TDL. Prima del go-live lo sperimentatore deve inserire e
approvare il wording che spiega il payoff 12/0/0. Fino ad allora il software è
testabile, ma quel braccio non è pronto per raccolta reale.

## 9. Sicurezza

Con `OTREE_AUTH_LEVEL=STUDY`:

- `/demo` non deve essere pubblico;
- root/admin richiedono login;
- il partecipante entra solo da `/room/prolific`.

Password e chiavi restano in variabili ambiente, mai nel repository.

## Riferimenti

- [Prolific: random assignment to conditions](https://researcher-help.prolific.com/en/articles/445173-can-i-randomly-assign-participants-to-conditions-on-prolific)
- [Prolific Taskflow/multiple conditions](https://researcher-help.prolific.com/en/articles/445142-taskflow-academic-multiple-conditions)
- `docs/DEPLOYMENT.md`
- `docs/EXPORT_DATA_DICTIONARY.md`
- `docs/DATA_VALIDITY_PROLIFIC.md`
