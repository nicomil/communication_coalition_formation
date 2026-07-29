"""Integration tests for the database-backed RCT treatment allocator."""

import unittest
from collections import Counter

from otree.main import setup

setup()

from otree.export import get_custom_export_functions
from otree.session import create_session
from bargaining_tdl_intro import (
    TreatmentAssignment,
    TreatmentSlot,
    assign_treatment_slot,
    confirm_treatment_slot,
    release_treatment_slot,
    custom_export_rct_assignments,
    custom_export_rct_slots,
)


class RCTAllocatorIntegrationTests(unittest.TestCase):
    def _new_players(self, count=18):
        session = create_session(
            'bargaining_tdl',
            num_participants=count,
        )
        subsession = session.get_subsessions()[0]
        return session, subsession.get_players()

    def test_permuted_blocks_are_balanced_and_auditable(self):
        session, players = self._new_players()
        treatments = [assign_treatment_slot(player) for player in players]

        self.assertEqual(len(set(treatments)), 3)
        for block_start in range(0, 18, 9):
            self.assertEqual(
                Counter(treatments[block_start:block_start + 9]),
                Counter({'private': 3, 'public': 3, 'private_no_dwl': 3}),
            )

        self.assertEqual(len(TreatmentSlot.filter(subsession=players[0].subsession)), 18)
        self.assertEqual(
            sum(len(TreatmentAssignment.filter(player=player)) for player in players),
            18,
        )
        self.assertIsInstance(session.vars['randomization_seed'], int)

    def test_failed_cq_slot_is_first_replacement_and_keeps_arm(self):
        _, players = self._new_players(9)
        failed_player, replacement_player, next_player = players[:3]

        original_treatment = assign_treatment_slot(failed_player)
        original_slot = failed_player.allocation_slot
        release_treatment_slot(failed_player, 'control_questions_failed')

        replacement_treatment = assign_treatment_slot(replacement_player)
        self.assertEqual(replacement_treatment, original_treatment)
        self.assertEqual(replacement_player.allocation_slot, original_slot)
        self.assertTrue(replacement_player.is_replacement)
        self.assertEqual(replacement_player.allocation_attempt, 2)

        confirm_treatment_slot(replacement_player)
        self.assertEqual(replacement_player.assignment_status, 'passed')

        assign_treatment_slot(next_player)
        self.assertNotEqual(next_player.allocation_slot, original_slot)

        attempts = [
            *TreatmentAssignment.filter(player=failed_player),
            *TreatmentAssignment.filter(player=replacement_player),
        ]
        self.assertEqual([row.status for row in attempts], ['failed', 'passed'])

    def test_both_rct_exports_are_registered_and_session_scoped(self):
        _, players = self._new_players(9)
        for player in players[:3]:
            assign_treatment_slot(player)

        exports = get_custom_export_functions('bargaining_tdl_intro')
        self.assertIn('custom_export_rct_assignments', exports)
        self.assertIn('custom_export_rct_slots', exports)

        assignment_rows = list(custom_export_rct_assignments(players))
        slot_rows = list(custom_export_rct_slots(players))
        self.assertEqual(len(assignment_rows), 4)
        self.assertEqual(len(slot_rows), 10)
        self.assertEqual(assignment_rows[0][0], 'session_code')
        self.assertEqual(slot_rows[0][1], 'randomization_seed')


if __name__ == '__main__':
    unittest.main()
