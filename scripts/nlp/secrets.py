"""
Caricamento delle chiavi API per la pipeline NLP.

Le chiavi si mettono in un file `.secrets.env` nella cartella del progetto,
che `.gitignore` esclude. È l'unico posto da ricordare, funziona uguale su
macOS, Windows e Linux, e non richiede di toccare il profilo della shell.

Ordine di precedenza: una variabile d'ambiente già impostata vince sempre sul
file, così chi preferisce gestirle a modo suo non viene scavalcato.

Il file non deve mai finire sotto controllo di versione: il repository è
pubblico. Per questo `load_secrets` chiede a git se il file è davvero ignorato
e avvisa in modo rumoroso quando non lo è, invece di fidarsi del fatto che una
riga di `.gitignore` sia stata scritta correttamente.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

SECRETS_FILENAME = '.secrets.env'

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Chiavi note, con la spiegazione di cosa serve a cosa: la usano sia il
# messaggio d'errore sia lo script di configurazione.
KNOWN_KEYS = {
    'OPENAI_API_KEY': 'TopicGPT (backend usato dal paper)',
    'ANTHROPIC_API_KEY': 'rubrica di validazione delle misure testuali',
    'OPENAI_BASE_URL': 'endpoint alternativo compatibile OpenAI (facoltativo)',
}


def secrets_path() -> Path:
    return REPO_ROOT / SECRETS_FILENAME


def parse_secrets(text: str) -> dict:
    """Legge un file in forma ``CHIAVE=valore``.

    Tollera il prefisso ``export``, le virgolette e i commenti, così un file
    copiato da istruzioni trovate altrove funziona comunque.
    """
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[len('export '):].strip()
        if '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def is_git_ignored(path: Path) -> bool | None:
    """True se git ignora il file, None se git non è disponibile."""
    try:
        result = subprocess.run(
            ['git', 'check-ignore', '-q', str(path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    # 0 = ignorato, 1 = non ignorato, altro = git non utilizzabile qui.
    if result.returncode in (0, 1):
        return result.returncode == 0
    return None


def _warn_if_exposed(path: Path) -> None:
    if is_git_ignored(path) is False:
        print(
            f'\nATTENZIONE: {path.name} NON è ignorato da git.\n'
            f'  Il repository è pubblico: aggiungi "{SECRETS_FILENAME}" a '
            f'.gitignore prima di fare qualunque commit.\n',
            file=sys.stderr,
        )
    if os.name == 'posix' and path.exists():
        mode = path.stat().st_mode
        if mode & (stat.S_IRGRP | stat.S_IROTH):
            print(
                f'ATTENZIONE: {path.name} è leggibile da altri utenti. '
                f'Correggi con: chmod 600 {path}',
                file=sys.stderr,
            )


def load_secrets(path: Path | None = None) -> list[str]:
    """Carica le chiavi nell'ambiente. Restituisce i nomi caricati dal file."""
    path = path or secrets_path()
    if not path.is_file():
        return []

    _warn_if_exposed(path)

    loaded = []
    for key, value in parse_secrets(path.read_text(encoding='utf-8')).items():
        if not value:
            continue
        # setdefault: una variabile d'ambiente già presente ha la precedenza.
        if key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def has_key(name: str) -> bool:
    return bool(os.environ.get(name, '').strip())


def require_key(name: str) -> str:
    """Restituisce la chiave o esce con istruzioni utilizzabili."""
    value = os.environ.get(name, '').strip()
    if value:
        return value

    purpose = KNOWN_KEYS.get(name, 'questo stadio della pipeline')
    raise SystemExit(
        f"\nManca la chiave {name}, necessaria per {purpose}.\n\n"
        f"Per configurarla:\n"
        f"    python scripts/setup_api_keys.py\n\n"
        f"Lo script la salva in {SECRETS_FILENAME}, che git ignora.\n"
        f"In alternativa, impostala come variabile d'ambiente.\n"
    )


def status() -> list[tuple[str, str, bool]]:
    """Riepilogo per la diagnostica: nome, a cosa serve, se è presente."""
    return [(name, purpose, has_key(name)) for name, purpose in KNOWN_KEYS.items()]
