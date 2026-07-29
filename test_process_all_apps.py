import csv
import os
import tempfile
import unittest

from process_all_apps import process_all_apps


class ProcessAllAppsTests(unittest.TestCase):
    def test_generates_core_full_and_dictionary(self):
        headers = [
            'participant.id_in_session',
            'participant.code',
            'participant.inactive_excluded',
            'participant.inactive_excluded_reason',
            'participant.group_dropped',
            'participant.part1_payoff_eligible',
            'participant.prolific_id',
            'participant.prolific_study_id',
            'participant.prolific_session_id',
            'participant.allocation_failure_reason',
            'bargaining_tdl_intro.1.player.assigned_treatment',
            'bargaining_tdl_intro.1.player.allocation_slot',
            'bargaining_tdl_intro.1.player.allocation_block',
            'bargaining_tdl_intro.1.player.allocation_attempt',
            'bargaining_tdl_intro.1.player.assignment_timestamp',
            'bargaining_tdl_intro.1.player.assignment_status',
            'bargaining_tdl_intro.1.player.is_replacement',
            'bargaining_tdl_main.1.group.id_in_subsession',
            'bargaining_tdl_main.1.player.id_player_on_the_left',
            'bargaining_tdl_main.1.player.id_player_on_the_right',
            'bargaining_tdl_main.1.player.signal_left',
            'bargaining_tdl_main.1.player.signal_right',
            'bargaining_tdl_main.1.player.signal_left_convincingness',
            'bargaining_tdl_main.1.player.signal_right_convincingness',
            'bargaining_tdl_main.1.player.decision_choice',
            'bargaining_tdl_main.1.player.part1_calculated_payoff',
            'bargaining_tdl_main.1.group.group_outcome',
            'bargaining_tdl_survey.1.player.instructions_clarity',
            'bargaining_tdl_survey.1.player.general_comment',
            'bargaining_tdl_survey.1.player.age',
            'bargaining_tdl_survey.1.player.sd3_mach_01',
            'unused.column',
        ]
        rows = [
            {
                'participant.id_in_session': '1',
                'participant.code': 'abc',
                'participant.inactive_excluded': '0',
                'participant.inactive_excluded_reason': '',
                'participant.group_dropped': '0',
                'participant.part1_payoff_eligible': '1',
                'participant.prolific_id': 'pid1',
                'participant.prolific_study_id': 'study1',
                'participant.prolific_session_id': 'sess1',
                'participant.allocation_failure_reason': '',
                'bargaining_tdl_intro.1.player.assigned_treatment': 'private_no_dwl',
                'bargaining_tdl_intro.1.player.allocation_slot': '4',
                'bargaining_tdl_intro.1.player.allocation_block': '1',
                'bargaining_tdl_intro.1.player.allocation_attempt': '2',
                'bargaining_tdl_intro.1.player.assignment_timestamp': '123.5',
                'bargaining_tdl_intro.1.player.assignment_status': 'passed',
                'bargaining_tdl_intro.1.player.is_replacement': '1',
                'bargaining_tdl_main.1.group.id_in_subsession': '10',
                'bargaining_tdl_main.1.player.id_player_on_the_left': 'L',
                'bargaining_tdl_main.1.player.id_player_on_the_right': 'R',
                'bargaining_tdl_main.1.player.signal_left': 'split_you',
                'bargaining_tdl_main.1.player.signal_right': 'support_none',
                'bargaining_tdl_main.1.player.signal_left_convincingness': '3',
                'bargaining_tdl_main.1.player.signal_right_convincingness': '5',
                'bargaining_tdl_main.1.player.decision_choice': 'Left',
                'bargaining_tdl_main.1.player.part1_calculated_payoff': '6',
                'bargaining_tdl_main.1.group.group_outcome': 'mutual_12',
                'bargaining_tdl_survey.1.player.instructions_clarity': '5',
                'bargaining_tdl_survey.1.player.general_comment': 'ok',
                'bargaining_tdl_survey.1.player.age': '25',
                'bargaining_tdl_survey.1.player.sd3_mach_01': '3',
                'unused.column': '',
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, 'input.csv')
            core_path = os.path.join(tmp, 'core.csv')
            full_path = os.path.join(tmp, 'full.csv')
            dictionary_path = os.path.join(tmp, 'dictionary.md')

            with open(input_path, 'w', encoding='utf-8', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            process_all_apps(input_path, core_path, full_path, dictionary_path)

            self.assertTrue(os.path.exists(core_path))
            self.assertTrue(os.path.exists(full_path))
            self.assertTrue(os.path.exists(dictionary_path))

            with open(core_path, 'r', encoding='utf-8-sig') as handle:
                core_reader = csv.DictReader(handle)
                core_rows = list(core_reader)
            self.assertEqual(len(core_rows), 1)
            self.assertEqual(core_rows[0]['playerid'], '1')
            self.assertEqual(core_rows[0]['treatment'], 'private_no_dwl')
            self.assertEqual(core_rows[0]['allocation_attempt'], '2')
            self.assertEqual(core_rows[0]['signal_right_convincingness'], '5')
            self.assertEqual(core_rows[0]['group_outcome'], 'mutual_12')
            self.assertEqual(core_rows[0]['survey_sd3_mach_01'], '3')
            self.assertEqual(core_rows[0]['survey_instructions_clarity'], '5')
            self.assertEqual(core_rows[0]['survey_general_comment'], 'ok')

            with open(dictionary_path, 'r', encoding='utf-8') as handle:
                dictionary_text = handle.read()
            self.assertIn('always_empty', dictionary_text)
            self.assertIn('`unused.column`', dictionary_text)


if __name__ == '__main__':
    unittest.main()
