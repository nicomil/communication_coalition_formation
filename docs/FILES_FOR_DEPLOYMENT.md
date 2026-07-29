# File necessari al deployment

## Root

- `requirements.txt`
- `Procfile`
- `settings.py`
- `runtime.txt` o `.python-version`
- `process_all_apps.py`

## App attive

- `bargaining_tdl_common/`
- `bargaining_tdl_intro/`
- `bargaining_tdl_main/`
- `bargaining_tdl_survey/`
- `_templates/`
- `_welcome_pages/`
- `_static/`

Non esiste più un'app Dictator/Part 3 nel flusso.

## Verifica

```bash
git ls-files requirements.txt Procfile settings.py
git ls-files bargaining_tdl_common/
git ls-files bargaining_tdl_intro/
git ls-files bargaining_tdl_main/
git ls-files bargaining_tdl_survey/
git status
```

La room `prolific` non richiede un file label: è dichiarata in `settings.py`.

## Non tracciare

- `.env`;
- virtual environment;
- database SQLite;
- `__pycache__`, bytecode e statici generati;
- password, `DATABASE_URL`, `SECRET_KEY`.

## Gate

- PostgreSQL collegato;
- `OTREE_PRODUCTION=1`;
- `OTREE_AUTH_LEVEL=STUDY`;
- password admin e secret configurati;
- `PROLIFIC_COMPLETION_URL` reale;
- sessione `bargaining_tdl` associata alla room `prolific`;
- backup DB prima del deploy;
- suite `docs/TESTING.md` verde.
