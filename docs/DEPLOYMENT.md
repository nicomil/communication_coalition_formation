# Deployment Essenziale (Heroku)

Guida minima per deploy sicuro oTree senza perdere dati.

## Primo setup (una sola volta)

1. Crea app e DB Postgres:

```bash
heroku create <nome-app>
heroku addons:create heroku-postgresql:essential-0 --app <nome-app>
```

1. Configura variabili:

```bash
heroku config:set OTREE_PRODUCTION=1 --app <nome-app>
heroku config:set OTREE_AUTH_LEVEL=STUDY --app <nome-app>
heroku config:set OTREE_ADMIN_PASSWORD=<password-forte> --app <nome-app>
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') --app <nome-app>
heroku config:set PROLIFIC_COMPLETION_URL="https://app.prolific.com/submissions/complete?cc=C1HQEIID" --app <nome-app>
```

1. Verifica DB persistente collegato:

```bash
heroku config:get DATABASE_URL --app <nome-app>
```

Se vuoto ma esiste `HEROKU_POSTGRESQL_<COLOR>_URL`:

```bash
heroku addons:attach <nome-addon-postgres> --app <nome-app> --as DATABASE
```

1. Primo deploy:

```bash
git push heroku main
```

## Deploy successivi (produzione)

1. Backup prima del push:

```bash
heroku pg:backups:capture --app <nome-app>
```

1. Deploy:

```bash
git push heroku main
```

1. Verifica rapida:

```bash
heroku logs --tail --app <nome-app>
```

## Backup DB (dove sta e come usarlo)

- Il backup viene salvato su Heroku Postgres (non nel repository locale).
- Elenco backup:

```bash
heroku pg:backups --app <nome-app>
```

- Download locale ultimo backup:

```bash
heroku pg:backups:download --app <nome-app>
```

- Ripristino da backup specifico (operazione distruttiva sul DB target):

```bash
heroku pg:backups:restore b001 DATABASE_URL --app <nome-app> --confirm <nome-app>
```

## Regole critiche

- Non usare `heroku run otree resetdb` in produzione: cancella tutti i dati.
- Usa `otree resetdb` solo su ambiente nuovo/staging, mai su app con dati reali.
- Ruota periodicamente `OTREE_ADMIN_PASSWORD` e `SECRET_KEY`.
- `OTREE_AUTH_LEVEL=STUDY` per raccolta dati reale su Prolific (`DEMO` solo per test pubblici).

## Prolific: un solo entry point RCT

1. Da admin oTree crea una sessione `bargaining_tdl` associata alla room
   `prolific`.
2. Pubblica in Prolific una sola URL room-wide:

```text
https://<app>.herokuapp.com/room/prolific?participant_label={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}
```

3. In Prolific passa:
   - `PROLIFIC_PID` (mappato su `participant_label`)
   - `STUDY_ID`
   - `SESSION_ID`
4. L'app assegna internamente uno dei tre trattamenti con blocchi permutati
   3:3:3. Non creare URL o studi separati per trattamento.
5. Imposta `PROLIFIC_COMPLETION_URL` e prova il redirect finale.

## Setup Prolific consigliato (pilota)

- Tipo studio: `External study`
- Routing trattamenti: interno a oTree; **una sola URL**
- Link: `/room/prolific` con parametri Prolific
- Quote pilota: multiplo di 9 consigliato
- Review: `Manual review`
- Device: `Desktop only` (mobile off, tablet off)
- Lingua filtro: `Primary language = English`
- Durata stimata iniziale: `40 min` (aggiustare dopo pilot)

## Session sizing oTree (anti saturazione quote)

- Non creare sessioni da N esatto quando la quota Prolific è N.
- Creare una sola sessione RCT con buffer (es. 2× quota) per CQ failure e
  dropout; fermare il reclutamento quando la quota di CQ passate è raggiunta.
- Gli slot CQ falliti vengono offerti prima dei nuovi slot e mantengono lo
  stesso trattamento.

## Capacity e addon check pre-go-live

- Verifica processi attivi:

```bash
heroku ps --app <nome-app>
```

- Mantieni `web=1` (oTree non beneficia da scaling orizzontale standard per singola sessione).
- Verifica Redis se usi chat/live pages/waiting ad alta concorrenza:

```bash
heroku config:get REDIS_URL --app <nome-app>
```

- Monitora metriche dyno durante pilot (CPU/load/response time) e scala piano dyno se load rimane alto.
- Mantieni backup DB recente prima di ogni deploy in produzione.
- Postgres:
  - pilota: minimo `Essential 1` consigliato se chat + concorrenza
  - studio completo: target `Standard 0`
- Dyno Eco: valido per test, ma con picchi/chat va verificato sotto carico reale.

## Checklist go-live Prolific

- [ ] `OTREE_PRODUCTION=1`
- [ ] `OTREE_AUTH_LEVEL=STUDY`
- [ ] `OTREE_ADMIN_PASSWORD` impostata e testata
- [ ] `SECRET_KEY` impostata
- [ ] `DATABASE_URL` presente
- [ ] `PROLIFIC_COMPLETION_URL` valorizzata con completion code reale
- [ ] URL unico `/room/prolific` include `participant_label`, `STUDY_ID`, `SESSION_ID`
- [ ] Prolific configurato come singolo `External study`
- [ ] Prolific `Desktop only`, mobile/tablet disabilitati
- [ ] Prolific in `Manual review`
- [ ] Sessione RCT unica, associata alla room `prolific`, con buffer
- [ ] Istruzioni No-DWL definitive approvate (la copia Private TDL è temporanea)
- [ ] Smoke test completo: ingresso Prolific -> sessione oTree -> redirect completion
- [ ] Backup DB eseguito (`heroku pg:backups:capture`)

## Smoke test Prolific consigliato (step by step)

1. Apri URL Prolific con parametri:
   - `participant_label={{%PROLIFIC_PID%}}`
   - `STUDY_ID={{%STUDY_ID%}}`
   - `SESSION_ID={{%SESSION_ID%}}`
2. Completa flusso fino a `FinalResults`.
3. Verifica presenza bottone manuale "Complete on Prolific now".
4. Attendi redirect automatico e conferma arrivo su completion URL.
5. Verifica su export che siano valorizzati:
   - `participant.prolific_id`
   - `participant.prolific_study_id`
   - `participant.prolific_session_id`

## Stato attuale Heroku (`ccf`)

Ultimo check: 2026-05-05 14:13 (UTC+2)

- App: `ccf`
- URL: `https://ccf-70e9cba78a52.herokuapp.com/`
- Owner: `nicombk@gmail.com`
- Stack: `heroku-24`
- Dynos: `web: 1`
- Addon DB: `heroku-postgresql:essential-0` (`postgresql-rugged-25313`)
- DB alias attivi: `DATABASE_URL`, `HEROKU_POSTGRESQL_AQUA_URL`
- Postgres: `17.9`
- DB size: `7.69 MB`
- Tabelle: `0`
- Backup disponibile: `b001` (Completed, 2026-05-05 12:11:17 +0000)
- Database: `d6qm0ppaqrupal` (host e credenziali mascherati)

### Credenziali correnti (sensibili)

- `OTREE_PRODUCTION=1`
- `OTREE_AUTH_LEVEL` da verificare (target: `STUDY`)
- `OTREE_ADMIN_PASSWORD=********`
- `SECRET_KEY=********`
- `PROLIFIC_COMPLETION_URL` da impostare/verificare
