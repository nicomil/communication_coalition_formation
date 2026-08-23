"""I codici Prolific in settings.py devono coincidere con il calendario.

I codici sono specifici per giorno e fascia oraria, e un codice sbagliato non
si vede finche' il partecipante non arriva su Prolific e la submission non
combacia. Questo test rilegge le due fonti — la tabella in
``docs/PROLIFIC_CODES_COLLECTION_SCHEDULE.md`` e il foglio
``docs/Schedule sessions - Sheet2.csv`` — e confronta ogni codice con quello
che finisce nella session config.

    python -m unittest bargaining_tdl_common.test_prolific_codes
"""

import csv
import re
import unittest
from pathlib import Path

import settings

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE_MD = ROOT / 'docs' / 'PROLIFIC_CODES_COLLECTION_SCHEDULE.md'
SCHEDULE_CSV = ROOT / 'docs' / 'Schedule sessions - Sheet2.csv'

# Nel calendario i trattamenti hanno il nome operativo; nel codice quello
# storico, che gli export gia' raccolti usano.
TREATMENT_BY_LABEL = {
    'Baseline': 'private',
    'Public': 'public',
    'Slacker': 'private_no_dwl',
}


def slots_from_markdown():
    """Le nove righe della tabella, una per slot, nell'ordine del calendario."""
    day = None
    slots = []
    for line in SCHEDULE_MD.read_text(encoding='utf-8').splitlines():
        header = re.match(r'### Day (\d) — (\w+)', line)
        if header:
            day = int(header.group(1))
            continue
        if not (line.startswith('| ') and day):
            continue
        cells = [c.strip().strip('`') for c in line.strip('|').split('|')]
        if len(cells) == 9 and cells[2] in TREATMENT_BY_LABEL:
            slots.append(dict(
                day=day,
                slot=cells[0],
                treatment=TREATMENT_BY_LABEL[cells[2]],
                completion=cells[3],
                dropout_cq=cells[5],
                dropout_timeout=cells[7],
            ))
    return slots


def slots_from_csv():
    """Lo stesso calendario nel foglio, con il numero di partecipanti."""
    with SCHEDULE_CSV.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))

    def code(cell):
        # Il foglio scrive "CODICE - https://...": serve solo il codice.
        return cell.split(' - ')[0].strip()

    return [
        dict(
            slot=row['Time Slot (Italian Time)'].strip(),
            study=row['Study to Launch'].strip(),
            participants=int(row['No. of Participants']),
            completion=code(row['completion code']),
            dropout_cq=code(row['DropoutCQs code']),
            dropout_timeout=code(row['DropoutTimeout code']),
        )
        for row in rows
    ]


def collection_configs():
    names = {f"bargaining_tdl_{s['key']}" for s in settings.COLLECTION_SLOTS}
    return [c for c in settings.SESSION_CONFIGS if c['name'] in names]


class ScheduleSourcesAgreeTests(unittest.TestCase):
    """Le due fonti devono raccontare lo stesso calendario."""

    def test_same_number_of_slots(self):
        self.assertEqual(len(slots_from_markdown()), 9)
        self.assertEqual(len(slots_from_csv()), 9)

    def test_same_codes_in_the_same_order(self):
        for md, sheet in zip(slots_from_markdown(), slots_from_csv()):
            for field in ('completion', 'dropout_cq', 'dropout_timeout'):
                self.assertEqual(md[field], sheet[field], msg=f"{md['slot']} {field}")


class SettingsMatchTheScheduleTests(unittest.TestCase):

    def test_one_config_per_slot(self):
        self.assertEqual(len(settings.COLLECTION_SLOTS), 9)
        self.assertEqual(len(collection_configs()), 9)

    def test_every_code_comes_from_the_schedule(self):
        for slot, md, sheet in zip(settings.COLLECTION_SLOTS,
                                   slots_from_markdown(), slots_from_csv()):
            self.assertEqual(slot['day'], md['day'], msg=slot['key'])
            self.assertEqual(slot['treatment'], md['treatment'], msg=slot['key'])
            self.assertEqual(slot['study'], sheet['study'], msg=slot['key'])
            self.assertEqual(slot['participants'], sheet['participants'],
                             msg=slot['key'])
            for field in ('completion', 'dropout_cq', 'dropout_timeout'):
                self.assertEqual(slot[field], md[field],
                                 msg=f"{slot['key']} {field}")

    def test_links_carry_the_slot_codes(self):
        """Il link e' quello che il partecipante apre: deve avere il suo codice."""
        for slot in settings.COLLECTION_SLOTS:
            config = next(c for c in settings.SESSION_CONFIGS
                          if c['name'] == f"bargaining_tdl_{slot['key']}")
            pairs = (
                ('completionlink', slot['completion']),
                ('dropoutlink_cq', slot['dropout_cq']),
                ('dropoutlink_inactive', slot['dropout_timeout']),
            )
            for key, code in pairs:
                self.assertEqual(
                    config[key],
                    f'https://app.prolific.com/submissions/complete?cc={code}',
                    msg=f"{slot['key']} {key}",
                )

    def test_no_collection_config_is_missing_an_outcome(self):
        """Tre esiti, tre link: un link vuoto lascia il partecipante fermo."""
        for config in collection_configs():
            for key in ('completionlink', 'dropoutlink_cq', 'dropoutlink_inactive'):
                self.assertTrue(config.get(key, '').strip(),
                                msg=f"{config['name']} senza {key}")

    def test_codes_are_never_reused_across_slots(self):
        """Il calendario lo vieta: un codice riusato confonde due studi."""
        codes = [
            slot[field]
            for slot in settings.COLLECTION_SLOTS
            for field in ('completion', 'dropout_cq', 'dropout_timeout')
        ]
        self.assertEqual(len(codes), 27)
        self.assertEqual(len(set(codes)), 27)

    def test_each_slot_runs_one_treatment(self):
        """Sessioni mono-trattamento: i codici sono per studio, non per arm."""
        for config in collection_configs():
            self.assertEqual(len(config['active_treatments']), 1,
                             msg=config['name'])

    def test_each_day_covers_the_three_treatments(self):
        for day in (1, 2, 3):
            treatments = {s['treatment'] for s in settings.COLLECTION_SLOTS
                          if s['day'] == day}
            self.assertEqual(treatments,
                             {'private', 'public', 'private_no_dwl'},
                             msg=f'day {day}')

    def test_pilot_codes_stay_out_of_the_collection_configs(self):
        """I codici del pilot restano solo nelle config di collaudo."""
        pilot = {
            settings.PUBLIC_COMPLETION, settings.PUBLIC_DROPOUT_CQ,
            settings.PUBLIC_DROPOUT_INE, settings.PRIVATE_COMPLETION,
            settings.PRIVATE_DROPOUT_CQ, settings.PRIVATE_DROPOUT_INE,
            settings.NO_DWL_COMPLETION, settings.NO_DWL_DROPOUT_CQ,
            settings.NO_DWL_DROPOUT_INE,
        }
        for config in collection_configs():
            for key in ('completionlink', 'dropoutlink_cq', 'dropoutlink_inactive'):
                self.assertNotIn(config[key], pilot, msg=config['name'])

    def test_test_configs_are_marked_as_such(self):
        """Chi apre l'elenco deve vedere subito quali non sono da usare."""
        collection = {c['name'] for c in collection_configs()}
        for config in settings.SESSION_CONFIGS:
            if config['name'] not in collection:
                self.assertTrue(config['display_name'].startswith('[TEST]'),
                                msg=config['name'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
