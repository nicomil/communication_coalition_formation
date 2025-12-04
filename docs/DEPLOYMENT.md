# Guida al Deployment Online

Questa guida spiega come deployare l'esperimento oTree online per fornire il link alla piattaforma di testing.

## Opzioni di Deployment

### 1. Heroku (Raccomandato - già configurato)

Heroku è la piattaforma più semplice per oTree, e il progetto è già configurato con il `Procfile`.

#### Prerequisiti
- Account Heroku (gratuito per test)
- Heroku CLI installato: https://devcenter.heroku.com/articles/heroku-cli

#### Passaggi

1. **Installa Heroku CLI** (se non l'hai già fatto):
   ```bash
   # Mac
   brew tap heroku/brew && brew install heroku
   
   # Linux/Windows: scarica da https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login su Heroku**:
   ```bash
   heroku login
   ```

3. **Crea una nuova app Heroku**:
   ```bash
   heroku create nome-tua-app
   # Esempio: heroku create bargaining-experiment
   ```

4. **Aggiungi PostgreSQL** (database gratuito):
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Configura le variabili d'ambiente**:
   ```bash
   # Password admin (IMPORTANTE: scegli una password sicura!)
   heroku config:set OTREE_ADMIN_PASSWORD=la_tua_password_sicura
   
   # Modalità produzione
   heroku config:set OTREE_PRODUCTION=1
   
   # Secret key (genera una chiave casuale)
   heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
   ```

6. **Deploy del codice**:
   ```bash
   git push heroku main
   # oppure se usi master: git push heroku master
   ```

7. **Inizializza il database**:
   ```bash
   heroku run otree resetdb
   ```

8. **Apri l'applicazione**:
   ```bash
   heroku open
   ```

9. **Ottieni il link**:
   ```bash
   heroku info
   # Il link sarà: https://nome-tua-app.herokuapp.com
   ```

#### Aggiornamenti Futuri
Per aggiornare l'app dopo modifiche:
```bash
git add .
git commit -m "Aggiornamento esperimento"
git push heroku main
heroku run otree resetdb  # Solo se hai cambiato modelli o struttura
```

#### Monitoraggio
- **Logs**: `heroku logs --tail`
- **Console**: `heroku run bash`
- **Database**: `heroku pg:psql`

---

### 2. Railway

Railway è un'alternativa moderna a Heroku con piano gratuito generoso.

#### Passaggi

1. **Crea account su Railway**: https://railway.app

2. **Connetti il repository GitHub**:
   - Vai su Railway Dashboard
   - Clicca "New Project" → "Deploy from GitHub repo"
   - Seleziona il tuo repository

3. **Configura il servizio**:
   - Railway rileva automaticamente il `Procfile`
   - Aggiungi un servizio PostgreSQL dal marketplace

4. **Configura le variabili d'ambiente**:
   Nella sezione "Variables" del progetto, aggiungi:
   ```
   OTREE_ADMIN_PASSWORD=la_tua_password_sicura
   OTREE_PRODUCTION=1
   SECRET_KEY=genera_una_chiave_casuale_lunga
   DATABASE_URL=railway_lo_configura_automaticamente
   ```

5. **Deploy automatico**:
   - Railway deploya automaticamente ad ogni push su GitHub
   - Il link sarà: `https://tuo-progetto.up.railway.app`

6. **Inizializza il database**:
   - Vai su "Deployments" → "View Logs"
   - Apri la console e esegui: `otree resetdb`

---

### 3. Render

Render offre hosting gratuito con PostgreSQL incluso.

#### Passaggi

1. **Crea account su Render**: https://render.com

2. **Crea un nuovo Web Service**:
   - Connetti il repository GitHub
   - Render rileva automaticamente il `Procfile`

3. **Configura**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `otree prodserver1of2` (per il web)
   - **Environment**: `Python 3`

4. **Aggiungi PostgreSQL**:
   - Crea un nuovo "PostgreSQL" database
   - Render configura automaticamente `DATABASE_URL`

5. **Configura le variabili d'ambiente**:
   ```
   OTREE_ADMIN_PASSWORD=la_tua_password_sicura
   OTREE_PRODUCTION=1
   SECRET_KEY=genera_una_chiave_casuale_lunga
   ```

6. **Crea un Background Worker** (per il worker):
   - Nuovo "Background Worker"
   - Start Command: `otree prodserver2of2`
   - Stesse variabili d'ambiente del web service

7. **Deploy**:
   - Render deploya automaticamente
   - Il link sarà: `https://tuo-servizio.onrender.com`

---

## Configurazione Post-Deployment

### 1. Accesso Admin

Dopo il deployment, accedi all'interfaccia admin:
- URL: `https://tuo-link.com/admin/`
- Username: `admin`
- Password: quella che hai impostato in `OTREE_ADMIN_PASSWORD`

### 2. Creare una Sessione

1. Vai su `/admin/`
2. Clicca su "Sessions"
3. Crea una nuova sessione con:
   - **Session config name**: `bargaining_tdl`
   - **Number of participants**: il numero desiderato
   - **Room**: seleziona una room o lascia vuoto

### 3. Link per i Partecipanti

Dopo aver creato la sessione, otterrai un link unico per i partecipanti:
- URL tipo: `https://tuo-link.com/join/xxxxx/`
- Condividi questo link con i partecipanti

### 4. Monitoraggio Sessione

- Vai su `/admin/` → "Sessions" → seleziona la tua sessione
- Puoi vedere lo stato di tutti i partecipanti
- Puoi avanzare manualmente i partecipanti se necessario

---

## Variabili d'Ambiente Richieste

| Variabile | Descrizione | Esempio |
|-----------|-------------|---------|
| `OTREE_ADMIN_PASSWORD` | Password per l'accesso admin | `mia_password_sicura_123` |
| `OTREE_PRODUCTION` | Modalità produzione (sempre `1` in produzione) | `1` |
| `SECRET_KEY` | Chiave segreta per Django/oTree | Genera con: `python -c 'import secrets; print(secrets.token_urlsafe(50))'` |
| `DATABASE_URL` | URL del database PostgreSQL | Configurato automaticamente da Heroku/Railway/Render |

---

## Troubleshooting

### Errore: "Database connection failed"
- Verifica che PostgreSQL sia attivo e configurato
- Controlla che `DATABASE_URL` sia impostata correttamente

### Errore: "SECRET_KEY not set"
- Assicurati di aver impostato `SECRET_KEY` nelle variabili d'ambiente
- In produzione, non usare il placeholder `{{ secret_key }}` da `settings.py`

### App non si avvia
- Controlla i logs: `heroku logs --tail` (Heroku) o nella dashboard (Railway/Render)
- Verifica che tutte le dipendenze siano in `requirements.txt`

### Partecipanti non si connettono
- Verifica che la sessione sia stata creata correttamente
- Controlla che il link condiviso sia corretto
- Assicurati che il numero di partecipanti corrisponda alla configurazione

---

## Sicurezza

⚠️ **IMPORTANTE**: Prima di andare in produzione:

1. ✅ Cambia `SECRET_KEY` con una chiave casuale sicura
2. ✅ Imposta una password admin forte (`OTREE_ADMIN_PASSWORD`)
3. ✅ Verifica che `OTREE_PRODUCTION=1` sia impostato
4. ✅ Non committare mai password o chiavi nel repository
5. ✅ Usa HTTPS (tutte le piattaforme sopra lo forniscono automaticamente)

---

## Costi

- **Heroku**: Piano gratuito disponibile (con limitazioni), poi $7/mese per hobby
- **Railway**: $5 crediti gratuiti/mese, poi pay-as-you-go
- **Render**: Piano gratuito disponibile (con limitazioni), poi $7/mese

Per esperimenti di testing, il piano gratuito è generalmente sufficiente.



