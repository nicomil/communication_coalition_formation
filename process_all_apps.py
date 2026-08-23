"""Normalizza export ``all_apps_wide`` per analisi e audit."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


CORE_MAPPING = {
    'playerid': 'participant.id_in_session',
    'participant_code': 'participant.code',
    # Identificano la raccolta: con i pilot lanciati un trattamento alla volta
    # servono per unire i file e per sapere da quale sessione viene ogni riga.
    'session_code': 'session.code',
    'session_config': 'session.config.name',
    'groupid': 'bargaining_tdl_main.1.group.id_in_subsession',
    'treatment': 'bargaining_tdl_intro.1.player.assigned_treatment',
    'treatment_main': 'bargaining_tdl_main.1.player.treatment',
    'allocation_slot': 'bargaining_tdl_intro.1.player.allocation_slot',
    'allocation_block': 'bargaining_tdl_intro.1.player.allocation_block',
    'allocation_attempt': 'bargaining_tdl_intro.1.player.allocation_attempt',
    'assignment_timestamp': 'bargaining_tdl_intro.1.player.assignment_timestamp',
    'assignment_status': 'bargaining_tdl_intro.1.player.assignment_status',
    'is_replacement': 'bargaining_tdl_intro.1.player.is_replacement',
    'allocation_failure_reason': 'participant.allocation_failure_reason',
    'inactive': 'participant.inactive_excluded',
    'inactive_reason': 'participant.inactive_excluded_reason',
    'group_dropped': 'participant.group_dropped',
    'part1_payoff_eligible': 'participant.part1_payoff_eligible',
    'left_player': 'bargaining_tdl_main.1.player.id_player_on_the_left',
    'right_player': 'bargaining_tdl_main.1.player.id_player_on_the_right',
    'visualized_player_on_the_left': 'bargaining_tdl_main.1.player.id_player_visualized_on_the_left',
    'visualized_player_on_the_right': 'bargaining_tdl_main.1.player.id_player_visualized_on_the_right',
    'part1_signal_left': 'bargaining_tdl_main.1.player.signal_left',
    'part1_signal_right': 'bargaining_tdl_main.1.player.signal_right',
    # Belief elicitation su PostDecisionConfidence. Sostituiscono
    # signal_left/right_convincingness, rimossi dai modelli.
    'guess_left_choice': 'bargaining_tdl_main.1.player.guess_left_choice',
    'guess_right_choice': 'bargaining_tdl_main.1.player.guess_right_choice',
    'guess_left_confidence': 'bargaining_tdl_main.1.player.guess_left_confidence',
    'guess_right_confidence': 'bargaining_tdl_main.1.player.guess_right_confidence',
    'part1_finaldecision': 'bargaining_tdl_main.1.player.decision_choice',
    'decision_inactive': 'bargaining_tdl_main.1.player.decision_inactive',
    'signal_inactive': 'bargaining_tdl_main.1.player.signal_inactive',
    'part1_payoff': 'bargaining_tdl_main.1.player.part1_calculated_payoff',
    'group_outcome': 'bargaining_tdl_main.1.group.group_outcome',
    'prolific_id': 'participant.prolific_id',
    'prolific_study_id': 'participant.prolific_study_id',
    'prolific_session_id': 'participant.prolific_session_id',
}

SURVEY_PREFIX = 'bargaining_tdl_survey.1.player.'


def _read_export(input_path):
    with input_path.open('r', encoding='utf-8-sig', newline='') as handle:
        first_line = handle.readline()
        handle.seek(0)
        delimiter = ';' if ';' in first_line else ','
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def _write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_dictionary(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(rows)
    lines = [
        '# Export Data Dictionary',
        '',
        f'Rows inspected: **{total}**.',
        '',
        '| Column | Non-empty | Fill ratio | Category |',
        '|---|---:|---:|---|',
    ]
    for header in headers:
        non_empty = sum(
            1 for row in rows if str(row.get(header, '')).strip() != ''
        )
        ratio = (non_empty / total) if total else 0
        if non_empty == 0:
            category = 'always_empty'
        elif non_empty == total:
            category = 'populated'
        else:
            category = 'sparse'
        lines.append(
            f'| `{header}` | {non_empty}/{total} | {ratio:.4f} | {category} |'
        )
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def process_all_apps(
    input_file,
    core_output_file,
    full_output_file=None,
    dictionary_output_file=None,
):
    """
    Produce dataset core; opzionalmente copia audit completa e dizionario.

    Firma a due argomenti resta supportata per script legacy.
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f'Input file not found: {input_path}')

    headers, rows = _read_export(input_path)
    survey_columns = [
        header for header in headers if header.startswith(SURVEY_PREFIX)
    ]
    survey_mapping = {
        header: f"survey_{header.removeprefix(SURVEY_PREFIX)}"
        for header in survey_columns
    }

    core_fieldnames = list(CORE_MAPPING) + list(survey_mapping.values())
    core_rows = []
    for row in rows:
        core_row = {
            target: row.get(source, '')
            for target, source in CORE_MAPPING.items()
        }
        core_row.update({
            target: row.get(source, '')
            for source, target in survey_mapping.items()
        })
        core_rows.append(core_row)

    _write_csv(Path(core_output_file), core_fieldnames, core_rows)
    if full_output_file:
        _write_csv(Path(full_output_file), headers, rows)
    if dictionary_output_file:
        _write_dictionary(Path(dictionary_output_file), headers, rows)

    return {
        'rows': len(rows),
        'core_columns': len(core_fieldnames),
        'full_columns': len(headers),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    input_path = Path(argv[0]) if len(argv) >= 1 else Path(
        'docs/all_apps_wide_2026-05-14 (1).csv'
    )
    core_path = Path(argv[1]) if len(argv) >= 2 else Path(
        'docs/processed_all_apps_dataset_core.csv'
    )
    full_path = Path(argv[2]) if len(argv) >= 3 else Path(
        'docs/processed_all_apps_dataset_full.csv'
    )
    dictionary_path = Path(argv[3]) if len(argv) >= 4 else Path(
        'docs/EXPORT_DATA_DICTIONARY.md'
    )

    result = process_all_apps(
        input_path,
        core_path,
        full_path,
        dictionary_path,
    )
    print(
        'Dataset processed: '
        f"{result['rows']} rows, {result['core_columns']} core columns."
    )


if __name__ == '__main__':
    main()
