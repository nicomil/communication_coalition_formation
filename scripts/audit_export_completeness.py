"""
Audit di completezza dell'export oTree.

Confronta ciò che l'esperimento *dichiara* di raccogliere (campi dei modelli
oTree, PARTICIPANT_FIELDS, SESSION_FIELDS, ExtraModel) con ciò che finisce
davvero nel CSV ``all_apps_wide``. Serve a garantire che nessuna variabile
raccolta resti fuori dal dataset di analisi.

I campi dei modelli vengono estratti con ``ast``, senza importare oTree: così
l'audit gira anche senza database e senza server attivo.

Uso:
    python scripts/audit_export_completeness.py --wide docs/all_apps_wide.csv
    python scripts/audit_export_completeness.py --wide <csv> --chat <ChatMessages.csv>
    python scripts/audit_export_completeness.py --wide <csv> --json report.json
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# App nella sequenza attiva dell'esperimento, nell'ordine di esecuzione.
APPS = ['bargaining_tdl_intro', 'bargaining_tdl_main', 'bargaining_tdl_survey']

# Colonne che oTree genera da sé per ogni app: non sono campi dichiarati nei
# modelli, ma devono comunque essere presenti nell'export.
OTREE_IMPLICIT_PLAYER_FIELDS = ['id_in_group', 'role', 'payoff']
OTREE_IMPLICIT_GROUP_FIELDS = ['id_in_subsession']
OTREE_IMPLICIT_SUBSESSION_FIELDS = ['round_number']

# Colonne participant/session che oTree emette sempre, indipendentemente da
# PARTICIPANT_FIELDS.
OTREE_BUILTIN_PARTICIPANT_COLS = [
    'participant.id_in_session', 'participant.code', 'participant.label',
    'participant._is_bot', 'participant._index_in_pages',
    'participant._max_page_index', 'participant._current_app_name',
    'participant._current_page_name', 'participant.time_started_utc',
    'participant.visited', 'participant.payoff',
]

# Colonne MTurk: presenti nell'export ma inutili per questo studio (nessuna
# raccolta su MTurk). Vengono segnalate come "da rimuovere", non come errore.
MTURK_COLS = [
    'participant.mturk_worker_id', 'participant.mturk_assignment_id',
    'session.mturk_HITId', 'session.mturk_HITGroupId',
]

# Campi partecipante deliberatamente esclusi dall'analisi, su indicazione dello
# sperimentatore. Non vanno segnalati come buchi.
INTENTIONALLY_IGNORED_VARS = {
    'intro_cq_errors',
    'failed_control_questions',
    'timeout_excluded',
    'chat_advanced_reason',
    # Ridondante: coincide con bargaining_tdl_main.1.player.payoff.
    'part1_payoff',
    # Copie di comodo di campi già esportati come colonne dedicate.
    'signal_left', 'signal_right', 'signal_inactive', 'time_welcome',
    'group_outcome', 'part1_group_id', 'group_dropped', 'part1_payoff_eligible',
    'inactive_excluded', 'inactive_excluded_reason', 'treatment',
    'prolific_id', 'prolific_study_id', 'prolific_session_id',
    'assignment_status', 'allocation_failure_reason', 'randomization_seed',
    'group_dropped_inactive',
}


def _module_ast(app: str) -> ast.Module:
    path = REPO_ROOT / app / '__init__.py'
    return ast.parse(path.read_text(encoding='utf-8'), filename=str(path))


def _is_models_field(node: ast.AST) -> bool:
    """True se il nodo è una chiamata del tipo ``models.QualcosaField(...)``."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == 'models'
        and func.attr.endswith('Field')
    )


def _class_fields(module: ast.Module, class_name: str) -> list[str]:
    """Nomi dei campi ``models.*Field`` dichiarati in una classe."""
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            fields = []
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and _is_models_field(stmt.value):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            fields.append(target.id)
            return fields
    return []


def _extra_model_classes(module: ast.Module) -> dict[str, list[str]]:
    """ExtraModel dichiarati nel modulo, con i rispettivi campi.

    Gli ExtraModel non finiscono mai in ``all_apps_wide``: si esportano solo
    tramite custom export. Vanno quindi elencati a parte.
    """
    out = {}
    for node in module.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
        if 'ExtraModel' not in bases:
            continue
        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and _is_models_field(stmt.value):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        fields.append(target.id)
        out[node.name] = fields
    return out


def _custom_export_functions(module: ast.Module) -> list[str]:
    return [
        node.name
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith('custom_export')
    ]


def _vars_owner(node: ast.AST) -> str | None:
    """Nome dell'oggetto a cui appartiene un ``.vars``: participant o session."""
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def _participant_vars_written(module: ast.Module) -> set[str]:
    """Chiavi scritte in ``participant.vars['...']`` dentro il modulo.

    Individua le variabili di stato che l'esperimento crea a runtime: se non
    sono in PARTICIPANT_FIELDS non compaiono nell'export. Le ``session.vars``
    sono escluse: hanno un elenco dedicato (SESSION_FIELDS).
    """
    keys = set()
    for node in ast.walk(module):
        if not isinstance(node, ast.Subscript):
            continue
        value = node.value
        if not (isinstance(value, ast.Attribute) and value.attr == 'vars'):
            continue
        if _vars_owner(value.value) != 'participant':
            continue
        idx = node.slice
        if isinstance(idx, ast.Constant) and isinstance(idx.value, str):
            keys.add(idx.value)
    return keys


def _settings_list(name: str) -> list[str]:
    """Legge una lista di stringhe da settings.py senza importarlo."""
    module = ast.parse((REPO_ROOT / 'settings.py').read_text(encoding='utf-8'))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    if isinstance(node.value, ast.List):
                        return [
                            el.value
                            for el in node.value.elts
                            if isinstance(el, ast.Constant)
                        ]
    return []


def collect_expected() -> dict:
    """Costruisce l'inventario di tutto ciò che l'esperimento raccoglie."""
    expected_cols = []
    per_app = {}
    extra_models = {}
    custom_exports = {}
    vars_written = set()

    for app in APPS:
        module = _module_ast(app)
        player = OTREE_IMPLICIT_PLAYER_FIELDS + _class_fields(module, 'Player')
        group = OTREE_IMPLICIT_GROUP_FIELDS + _class_fields(module, 'Group')
        subsession = OTREE_IMPLICIT_SUBSESSION_FIELDS + _class_fields(
            module, 'Subsession'
        )
        per_app[app] = dict(player=player, group=group, subsession=subsession)

        for field in player:
            expected_cols.append(f'{app}.1.player.{field}')
        for field in group:
            expected_cols.append(f'{app}.1.group.{field}')
        for field in subsession:
            expected_cols.append(f'{app}.1.subsession.{field}')

        extra = _extra_model_classes(module)
        if extra:
            extra_models[app] = extra
        exports = _custom_export_functions(module)
        if exports:
            custom_exports[app] = exports
        vars_written |= _participant_vars_written(module)

    participant_fields = _settings_list('PARTICIPANT_FIELDS')
    session_fields = _settings_list('SESSION_FIELDS')

    expected_cols += OTREE_BUILTIN_PARTICIPANT_COLS
    expected_cols += [f'participant.{f}' for f in participant_fields]
    expected_cols += [f'session.{f}' for f in session_fields]

    return dict(
        expected_cols=expected_cols,
        per_app=per_app,
        extra_models=extra_models,
        custom_exports=custom_exports,
        participant_fields=participant_fields,
        session_fields=session_fields,
        participant_vars_written=sorted(vars_written),
    )


def audit(wide_path: Path, chat_path: Path | None) -> dict:
    with wide_path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.reader(handle)
        actual_cols = next(reader)
        rows = list(reader)

    expected = collect_expected()
    actual_set = set(actual_cols)

    missing = [c for c in expected['expected_cols'] if c not in actual_set]

    # Variabili di stato scritte a runtime ma non esportabili perché assenti da
    # PARTICIPANT_FIELDS; escluse quelle deliberatamente ignorate.
    declared = set(expected['participant_fields'])
    orphan_vars = sorted(
        v
        for v in expected['participant_vars_written']
        if v not in declared and v not in INTENTIONALLY_IGNORED_VARS
    )

    mturk_present = [c for c in MTURK_COLS if c in actual_set]

    # Colonne interamente vuote: presenti ma senza alcun dato raccolto.
    empty_cols = []
    if rows:
        index = {c: i for i, c in enumerate(actual_cols)}
        for col in actual_cols:
            i = index[col]
            if all(not (r[i] if i < len(r) else '').strip() for r in rows):
                empty_cols.append(col)

    chat_report = None
    if chat_path is not None:
        chat_report = _audit_chat(chat_path, wide_path)

    return dict(
        wide_file=str(wide_path),
        n_rows=len(rows),
        n_cols=len(actual_cols),
        missing_columns=missing,
        orphan_participant_vars=orphan_vars,
        mturk_columns_present=mturk_present,
        empty_columns=empty_cols,
        extra_models=expected['extra_models'],
        custom_exports=expected['custom_exports'],
        chat=chat_report,
    )


def _audit_chat(chat_path: Path, wide_path: Path) -> dict:
    """Verifica che ogni messaggio di chat sia riconducibile a un partecipante."""
    with chat_path.open(encoding='utf-8-sig', newline='') as handle:
        messages = list(csv.DictReader(handle))
    with wide_path.open(encoding='utf-8-sig', newline='') as handle:
        wide = list(csv.DictReader(handle))

    codes = {r['participant.code'] for r in wide}
    unmatched = [m for m in messages if m.get('participant_code') not in codes]

    malformed = []
    channels = set()
    for message in messages:
        channel = message.get('channel', '')
        suffix = channel.rpartition('-')[2]
        parts = suffix.split('_')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            malformed.append(channel)
        else:
            channels.add((message['session_code'], parts[0]))

    empty_bodies = [m for m in messages if not (m.get('body') or '').strip()]

    return dict(
        chat_file=str(chat_path),
        n_messages=len(messages),
        n_chat_groups=len(channels),
        messages_without_matching_participant=len(unmatched),
        malformed_channels=sorted(set(malformed)),
        empty_message_bodies=len(empty_bodies),
    )


def render(report: dict) -> str:
    lines = []
    add = lines.append

    add('=' * 78)
    add('AUDIT DI COMPLETEZZA EXPORT')
    add('=' * 78)
    add(f"File          : {report['wide_file']}")
    add(f"Righe         : {report['n_rows']}")
    add(f"Colonne       : {report['n_cols']}")
    add('')

    add('-- Campi dichiarati nei modelli e assenti dal CSV ' + '-' * 27)
    if report['missing_columns']:
        for col in report['missing_columns']:
            add(f'  MANCANTE  {col}')
    else:
        add('  Nessuno: ogni campo dichiarato ha la sua colonna.')
    add('')

    add('-- participant.vars scritti ma non esportabili ' + '-' * 31)
    if report['orphan_participant_vars']:
        add('  (non sono in PARTICIPANT_FIELDS, quindi non finiscono nel CSV)')
        for var in report['orphan_participant_vars']:
            add(f'  ORFANO    {var}')
    else:
        add('  Nessuno.')
    add('')

    add('-- ExtraModel (mai in all_apps_wide, solo via custom export) ' + '-' * 17)
    if report['extra_models']:
        for app, models_ in report['extra_models'].items():
            for name, fields in models_.items():
                add(f'  {app}.{name}: {len(fields)} campi')
                add(f'    {", ".join(fields)}')
    else:
        add('  Nessuno.')
    add('')

    add('-- Custom export da scaricare a parte ' + '-' * 40)
    if report['custom_exports']:
        for app, funcs in report['custom_exports'].items():
            for func in funcs:
                add(f'  {app}.{func}')
    else:
        add('  Nessuno.')
    add('')

    add('-- Colonne MTurk da rimuovere dal dataset di analisi ' + '-' * 25)
    for col in report['mturk_columns_present'] or ['  Nessuna.']:
        add(f'  {col}' if report['mturk_columns_present'] else col)
    add('')

    add('-- Colonne presenti ma completamente vuote ' + '-' * 35)
    if report['empty_columns']:
        add(f"  {len(report['empty_columns'])} colonne senza alcun valore:")
        for col in report['empty_columns']:
            add(f'  VUOTA     {col}')
    else:
        add('  Nessuna.')
    add('')

    if report['chat']:
        chat = report['chat']
        add('-- Chat ' + '-' * 69)
        add(f"  File                          : {chat['chat_file']}")
        add(f"  Messaggi                      : {chat['n_messages']}")
        add(f"  Gruppi con almeno un messaggio: {chat['n_chat_groups']}")
        add(f"  Messaggi senza partecipante   : {chat['messages_without_matching_participant']}")
        add(f"  Canali malformati             : {len(chat['malformed_channels'])}")
        add(f"  Messaggi vuoti                : {chat['empty_message_bodies']}")
        add('')

    blocking = bool(report['missing_columns'] or report['orphan_participant_vars'])
    if report['chat']:
        blocking = blocking or report['chat']['messages_without_matching_participant'] > 0
    add('=' * 78)
    add('ESITO: ' + ('PROBLEMI DA SANARE' if blocking else 'NESSUN BUCO RILEVATO'))
    add('=' * 78)
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wide', required=True, type=Path,
                        help='CSV all_apps_wide da verificare')
    parser.add_argument('--chat', type=Path, default=None,
                        help='CSV ChatMessages (opzionale)')
    parser.add_argument('--json', type=Path, default=None,
                        help='Scrive il report anche in JSON')
    args = parser.parse_args(argv)

    report = audit(args.wide, args.chat)
    print(render(report))
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                             encoding='utf-8')
        print(f'\nReport JSON: {args.json}')

    blocking = bool(report['missing_columns'] or report['orphan_participant_vars'])
    return 1 if blocking else 0


if __name__ == '__main__':
    sys.exit(main())
