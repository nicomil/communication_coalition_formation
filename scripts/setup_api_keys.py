"""
Configura le chiavi API della pipeline NLP.

Un solo comando, identico su macOS, Windows e Linux:

    python scripts/setup_api_keys.py

Chiede le chiavi (l'input resta nascosto), le salva in `.secrets.env` nella
cartella del progetto, verifica che git le ignori davvero e — se lo si chiede —
prova a contattare i servizi per confermare che funzionino.

    python scripts/setup_api_keys.py --check    verifica quelle già presenti
    python scripts/setup_api_keys.py --status   dice solo cosa è configurato

Il file non va mai messo sotto controllo di versione: il repository è pubblico.
Lo script si rifiuta di scrivere se git non lo sta ignorando.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.nlp import secrets  # noqa: E402

# Chiavi proposte durante la configurazione, in ordine di importanza.
PROMPTS = [
    ('OPENAI_API_KEY', 'OpenAI — serve a TopicGPT', 'sk-...'),
    ('ANTHROPIC_API_KEY', 'Anthropic — serve alla rubrica di validazione', 'sk-ant-...'),
]

GITIGNORE_LINE = secrets.SECRETS_FILENAME


def ensure_gitignored(path: Path) -> bool:
    """Verifica che git ignori il file; se manca, propone di aggiungere la riga."""
    ignored = secrets.is_git_ignored(path)
    if ignored:
        return True
    if ignored is None:
        print('  git non disponibile: non posso verificare che il file sia ignorato.')
        return True

    gitignore = secrets.REPO_ROOT / '.gitignore'
    print(f'\n  {path.name} non è ignorato da git, e il repository è pubblico.')
    answer = input(f'  Aggiungo "{GITIGNORE_LINE}" a .gitignore? [S/n] ').strip().lower()
    if answer in ('n', 'no'):
        print('  Interrotto: senza la riga in .gitignore le chiavi rischiano di finire online.')
        return False

    existing = gitignore.read_text(encoding='utf-8') if gitignore.is_file() else ''
    separator = '' if existing.endswith('\n') or not existing else '\n'
    gitignore.write_text(f'{existing}{separator}{GITIGNORE_LINE}\n', encoding='utf-8')
    print(f'  Aggiunta a {gitignore}')
    return bool(secrets.is_git_ignored(path))


def write_secrets(path: Path, values: dict) -> None:
    lines = [
        '# Chiavi API della pipeline NLP.',
        '# File locale: non va mai messo sotto controllo di versione.',
        '# Rigenerabile con: python scripts/setup_api_keys.py',
        '',
    ]
    lines += [f'{key}={value}' for key, value in sorted(values.items()) if value]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if os.name == 'posix':
        path.chmod(0o600)


def _masked(value: str) -> str:
    if len(value) <= 10:
        return '*' * len(value)
    return f'{value[:6]}…{value[-4:]} ({len(value)} caratteri)'


def check_openai(key: str) -> tuple[bool, str]:
    request = urllib.request.Request(
        'https://api.openai.com/v1/models',
        headers={'Authorization': f'Bearer {key}'},
    )
    return _probe(request, 'OpenAI')


def check_anthropic(key: str) -> tuple[bool, str]:
    request = urllib.request.Request(
        'https://api.anthropic.com/v1/models',
        headers={'x-api-key': key, 'anthropic-version': '2023-06-01'},
    )
    return _probe(request, 'Anthropic')


def _probe(request, label: str) -> tuple[bool, str]:
    """Chiamata di sola lettura per confermare che la chiave sia valida."""
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
        models = payload.get('data') or []
        return True, f'{label}: chiave valida, {len(models)} modelli disponibili'
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return False, f'{label}: chiave rifiutata (HTTP {exc.code})'
        return False, f'{label}: risposta inattesa (HTTP {exc.code})'
    except urllib.error.URLError as exc:
        return False, f'{label}: nessuna connessione ({exc.reason})'
    except (TimeoutError, OSError, ValueError) as exc:
        return False, f'{label}: verifica non riuscita ({exc})'


CHECKERS = {
    'OPENAI_API_KEY': check_openai,
    'ANTHROPIC_API_KEY': check_anthropic,
}


def run_checks(values: dict) -> bool:
    print('\nVerifica delle chiavi:')
    all_ok = True
    for name, checker in CHECKERS.items():
        key = values.get(name) or os.environ.get(name, '')
        if not key.strip():
            print(f'  {name}: non configurata, salto')
            continue
        ok, message = checker(key.strip())
        print(f'  {"OK  " if ok else "FAIL"} {message}')
        all_ok = all_ok and ok
    return all_ok


def print_status() -> None:
    path = secrets.secrets_path()
    secrets.load_secrets(path)
    ignored = secrets.is_git_ignored(path)
    ignored_label = {
        True: 'sì',
        False: 'NO — da sistemare, il repository è pubblico',
        None: 'non verificabile',
    }[ignored]
    print(f'File chiavi : {path}')
    print(f'  esiste    : {"sì" if path.is_file() else "no"}')
    print(f'  git ignora: {ignored_label}')
    print()
    for name, purpose, present in secrets.status():
        print(f'  {"presente" if present else "assente ":9s} {name:22s} {purpose}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='verifica le chiavi già configurate, senza modificarle')
    parser.add_argument('--status', action='store_true',
                        help='mostra cosa è configurato ed esce')
    args = parser.parse_args(argv)

    path = secrets.secrets_path()
    existing = (
        secrets.parse_secrets(path.read_text(encoding='utf-8'))
        if path.is_file() else {}
    )

    if args.status:
        print_status()
        return 0

    if args.check:
        secrets.load_secrets(path)
        return 0 if run_checks(existing) else 1

    print('Configurazione delle chiavi API')
    print(f'File: {path}\n')
    print('Incolla la chiave e premi invio. Il testo non compare a schermo.')
    print('Premi invio a vuoto per lasciare invariata quella già presente.\n')

    values = dict(existing)
    for name, description, hint in PROMPTS:
        current = existing.get(name, '')
        state = f'attuale: {_masked(current)}' if current else 'non configurata'
        print(f'{description}\n  {state}')
        entered = getpass.getpass(f'  {name} ({hint}): ').strip()
        if entered:
            values[name] = entered
        print()

    if not any(values.get(name) for name, _, _ in PROMPTS):
        print('Nessuna chiave inserita: non scrivo nulla.')
        return 1

    if not ensure_gitignored(path):
        return 1

    write_secrets(path, values)
    print(f'Salvato in {path}')
    if os.name == 'posix':
        print('Permessi ristretti al solo proprietario (600).')

    ok = run_checks(values)
    print()
    if ok:
        print('Tutto pronto. La pipeline caricherà le chiavi da sola:')
        print('    python scripts/run_nlp_pipeline.py --merged-dir docs/merged \\')
        print('        --stem <nome> --topics --llm')
    else:
        print('Qualche verifica non è andata a buon fine: controlla i messaggi sopra.')
        print('Le chiavi sono comunque salvate; rilancia con --check dopo averle corrette.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
