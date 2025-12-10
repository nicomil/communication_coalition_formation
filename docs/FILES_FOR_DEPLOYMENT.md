# File e Cartelle Necessari per il Deployment su Heroku

Questo documento elenca tutti i file e le cartelle che devono essere tracciati da Git per deployare correttamente l'esperimento oTree su Heroku.

## File Obbligatori (Root del Progetto)

### 1. **requirements.txt** ⚠️ OBBLIGATORIO
- **Perché**: Heroku usa questo file per installare le dipendenze Python
- **Contenuto minimo**:
  ```
  otree>=5.4.0
  psycopg2>=2.8.4
  sentry-sdk==0.7.9
  ```
- **Verifica**: `git ls-files requirements.txt` deve restituire il file

### 2. **Procfile** ⚠️ OBBLIGATORIO
- **Perché**: Definisce i process types (web e worker) per Heroku
- **Contenuto**:
  ```
  web: otree prodserver1of2
  worker: otree prodserver2of2
  ```
- **Verifica**: `git ls-files Procfile` deve restituire il file

### 3. **settings.py** ⚠️ OBBLIGATORIO
- **Perché**: Configurazione principale di oTree con le sessioni
- **Deve contenere**: `SESSION_CONFIGS` con le app da deployare
- **Verifica**: `git ls-files settings.py` deve restituire il file

### 4. **runtime.txt** (Opzionale ma Consigliato)
- **Perché**: Specifica la versione Python per Heroku
- **Contenuto**: `python-3.11.9` (o versione desiderata)
- **Nota**: Heroku raccomanda di usare `.python-version` invece (contenuto: `3.11`)

## Cartelle delle App oTree

### 5. **Cartelle `bargaining_tdl_*`** ⚠️ OBBLIGATORIO
Tutte le cartelle delle app che sono incluse in `SESSION_CONFIGS` devono essere tracciate:

- `bargaining_tdl_intro/` - App introduttiva
- `bargaining_tdl_main/` - App principale
- `bargaining_tdl_part2/` - Parte 2
- `bargaining_tdl_part3/` - Parte 3

**Ogni cartella app deve contenere**:
- `__init__.py` - Logica dell'app
- `*.html` - Template HTML delle pagine
- `tests.py` - Test (opzionale ma consigliato)

**Verifica**:
```bash
git ls-files bargaining_tdl_intro/
git ls-files bargaining_tdl_main/
git ls-files bargaining_tdl_part2/
git ls-files bargaining_tdl_part3/
```

## File Statici e Template

### 6. **`_static/`** ⚠️ OBBLIGATORIO
- **Perché**: oTree richiede questa directory per i file statici (CSS, JS, immagini)
- **Deve contenere almeno**: 
  - `_static/.gitkeep` (o almeno un file) per assicurarsi che la directory esista
  - `_static/global/` (opzionale ma consigliato per file globali)
- **Verifica**: `git ls-files _static/` deve restituire almeno un file

### 7. **`_templates/`** (Opzionale ma Consigliato)
- **Perché**: Template HTML globali personalizzati
- **Contenuto tipico**:
  - `_templates/global/Page.html`
  - `_templates/global/_time_tracking_field.html`
- **Verifica**: `git ls-files _templates/` deve restituire i file

## File di Configurazione Opzionali

### 8. **`.env.example`** (Opzionale)
- **Perché**: Documenta le variabili d'ambiente necessarie
- **Non viene usato in produzione**, ma è utile per la documentazione

### 9. **`_rooms/`** (Opzionale)
- **Perché**: File di etichette per i partecipanti (se usi le Rooms)
- **Esempio**: `_rooms/econ101.txt`
- **Verifica**: `git ls-files _rooms/` se usi le rooms

## File da NON Tracciare (già in .gitignore)

Questi file NON devono essere tracciati:
- `venv/` - Virtual environment (locale)
- `*.sqlite3` - Database locale
- `__pycache__/` - Cache Python
- `*.pyc`, `*.pyo` - Bytecode Python
- `.DS_Store` - File sistema macOS
- `_static_root/` - Generato automaticamente
- `staticfiles/` - Generato automaticamente

## Checklist Pre-Deployment

Prima di fare `git push heroku main`, verifica:

```bash
# 1. File obbligatori esistono e sono tracciati
git ls-files requirements.txt
git ls-files Procfile
git ls-files settings.py
git ls-files runtime.txt  # opzionale

# 2. Cartelle app sono tracciate
git ls-files bargaining_tdl_intro/__init__.py
git ls-files bargaining_tdl_main/__init__.py
git ls-files bargaining_tdl_part2/__init__.py
git ls-files bargaining_tdl_part3/__init__.py

# 3. Directory _static esiste
git ls-files _static/

# 4. Template globali (se presenti)
git ls-files _templates/

# 5. Verifica che non ci siano file non tracciati importanti
git status
```

## Comandi Utili

### Verificare cosa manca
```bash
# Mostra tutti i file tracciati
git ls-files

# Mostra file non tracciati (potenzialmente importanti)
git status

# Verifica se un file specifico è tracciato
git ls-files nome_file
```

### Aggiungere file mancanti
```bash
# Aggiungi un file specifico
git add requirements.txt

# Aggiungi una cartella intera
git add _static/

# Aggiungi tutti i file di una app
git add bargaining_tdl_intro/

# Commit e push
git commit -m "Aggiungi file per deployment"
git push heroku main
```

## Struttura Minima Richiesta

```
progetto/
├── Procfile                    ⚠️ OBBLIGATORIO
├── requirements.txt            ⚠️ OBBLIGATORIO
├── runtime.txt                 (consigliato)
├── settings.py                 ⚠️ OBBLIGATORIO
├── .env.example                (opzionale)
├── _static/                    ⚠️ OBBLIGATORIO
│   ├── .gitkeep
│   └── global/
│       └── empty.css
├── _templates/                 (opzionale)
│   └── global/
│       └── Page.html
├── _rooms/                     (opzionale)
│   └── econ101.txt
└── bargaining_tdl_intro/       ⚠️ OBBLIGATORIO (se in SESSION_CONFIGS)
    ├── __init__.py
    ├── *.html
    └── tests.py
└── bargaining_tdl_main/         ⚠️ OBBLIGATORIO (se in SESSION_CONFIGS)
    ├── __init__.py
    ├── *.html
    └── tests.py
└── bargaining_tdl_part2/        ⚠️ OBBLIGATORIO (se in SESSION_CONFIGS)
    ├── __init__.py
    ├── *.html
    └── tests.py
└── bargaining_tdl_part3/        ⚠️ OBBLIGATORIO (se in SESSION_CONFIGS)
    ├── __init__.py
    ├── *.html
    └── tests.py
```

## Note Importanti

1. **Solo le app in `SESSION_CONFIGS`**: Non è necessario tracciare app che non sono incluse nella configurazione delle sessioni (es. `guess_two_thirds`, `survey`, ecc.)

2. **File generati automaticamente**: Non tracciare file generati automaticamente da oTree (come `_static_root/`)

3. **Database**: Il database PostgreSQL viene creato automaticamente su Heroku, non serve tracciare file di database locali

4. **Variabili d'ambiente**: Le variabili d'ambiente (`OTREE_ADMIN_PASSWORD`, `SECRET_KEY`, ecc.) vanno configurate su Heroku, non nel repository

## Troubleshooting

### Errore: "No default language could be detected"
- **Causa**: `requirements.txt` non è tracciato
- **Soluzione**: `git add requirements.txt && git commit -m "Aggiungi requirements.txt"`

### Errore: "Procfile declares types -> (none)"
- **Causa**: `Procfile` non è tracciato
- **Soluzione**: `git add Procfile && git commit -m "Aggiungi Procfile"`

### Errore: "ModuleNotFoundError: No module named 'bargaining_tdl_intro'"
- **Causa**: Le cartelle delle app non sono tracciate
- **Soluzione**: `git add bargaining_tdl_intro/ bargaining_tdl_main/ ... && git commit`

### Errore: "Directory '_static' does not exist"
- **Causa**: La directory `_static/` non è tracciata
- **Soluzione**: `git add _static/ && git commit`



