"""Unit tests for dropout auto-advance helpers."""

import unittest
from unittest.mock import MagicMock, patch


class TestDropoutSyncHelpers(unittest.TestCase):
    def _make_group(self, interrupted_id=2):
        group = MagicMock()
        group.interrupted_player_id = interrupted_id
        group.session.code = 'sess-code'
        return group

    def _make_interrupted_player(self, index=10, code='P2'):
        participant = MagicMock()
        participant._index_in_pages = index
        participant.code = code
        player = MagicMock()
        player.participant = participant
        return player

    def _make_page(self, page_name='Signals', app_name='bargaining_tdl_main'):
        page_cls = type(page_name, (), {})
        page = page_cls()
        page._lookup = MagicMock()
        page._lookup.app_name = app_name
        return page

    def test_force_chat_to_signals_when_two_peers_ahead(self):
        from bargaining_tdl_main import _advance_interrupted_player_to_waitpage

        group = self._make_group(interrupted_id=2)
        interrupted = self._make_interrupted_player(index=10)
        p1 = MagicMock()
        p1.id_in_group = 1
        p1.participant._index_in_pages = 13
        p3 = MagicMock()
        p3.id_in_group = 3
        p3.participant._index_in_pages = 13
        group.get_players.return_value = [p1, interrupted, p3]
        group.get_player_by_id.return_value = interrupted

        chat_page = self._make_page(page_name='Chat')
        interrupted.participant._get_page_instance.side_effect = [chat_page, None]
        interrupted.participant._timeout_page_index = 10
        interrupted.participant._timeout_expiration_time = 9999999999

        def _submit():
            interrupted.participant._index_in_pages += 1

        interrupted.participant._submit_current_page.side_effect = _submit
        interrupted.participant._visit_current_page.side_effect = lambda: None

        _advance_interrupted_player_to_waitpage(group, 12)
        self.assertEqual(interrupted.participant._index_in_pages, 11)
        self.assertEqual(interrupted.participant._submit_current_page.call_count, 1)

    def test_advance_interrupted_player_stops_on_other_app(self):
        from bargaining_tdl_main import _advance_interrupted_player_to_waitpage

        group = self._make_group(interrupted_id=2)
        interrupted = self._make_interrupted_player(index=10)
        p1 = MagicMock()
        p1.id_in_group = 1
        p1.participant._index_in_pages = 13
        p3 = MagicMock()
        p3.id_in_group = 3
        p3.participant._index_in_pages = 13
        group.get_players.return_value = [p1, interrupted, p3]
        group.get_player_by_id.return_value = interrupted

        interrupted.participant._get_page_instance.return_value = self._make_page(
            app_name='bargaining_tdl_survey'
        )

        _advance_interrupted_player_to_waitpage(group, 12)
        interrupted.participant._submit_current_page.assert_not_called()

    def test_signals_waits_for_timeout_before_auto_submit(self):
        from bargaining_tdl_main import _advance_interrupted_player_to_waitpage

        group = self._make_group(interrupted_id=2)
        interrupted = self._make_interrupted_player(index=11)
        interrupted.participant_left_ts = 0
        p1 = MagicMock()
        p1.id_in_group = 1
        p1.participant._index_in_pages = 13
        p3 = MagicMock()
        p3.id_in_group = 3
        p3.participant._index_in_pages = 13
        group.get_players.return_value = [p1, interrupted, p3]
        group.get_player_by_id.return_value = interrupted

        interrupted.participant._get_page_instance.return_value = self._make_page(
            page_name='Signals'
        )
        interrupted.participant._timeout_page_index = 11
        interrupted.participant._timeout_expiration_time = 9999999999

        _advance_interrupted_player_to_waitpage(group, 13)
        interrupted.participant._submit_current_page.assert_not_called()

    def test_signals_submits_if_offline_elapsed_exceeds_timeout(self):
        from bargaining_tdl_main import _advance_interrupted_player_to_waitpage

        group = self._make_group(interrupted_id=2)
        interrupted = self._make_interrupted_player(index=11)
        interrupted.participant_left_ts = 1
        p1 = MagicMock()
        p1.id_in_group = 1
        p1.participant._index_in_pages = 13
        p3 = MagicMock()
        p3.id_in_group = 3
        p3.participant._index_in_pages = 13
        group.get_players.return_value = [p1, interrupted, p3]
        group.get_player_by_id.return_value = interrupted

        interrupted.participant._get_page_instance.return_value = self._make_page(
            page_name='Signals'
        )
        # Fresh timeout marker could still be in future; offline elapsed must win.
        interrupted.participant._timeout_page_index = 11
        interrupted.participant._timeout_expiration_time = 9999999999

        with patch('bargaining_tdl_main.time.time', return_value=1000):
            _advance_interrupted_player_to_waitpage(group, 13)

        interrupted.participant._submit_current_page.assert_called()

    def test_advance_interrupted_player_noop_without_interrupted_id(self):
        from bargaining_tdl_main import _advance_interrupted_player_to_waitpage

        group = self._make_group(interrupted_id=0)
        _advance_interrupted_player_to_waitpage(group, 12)
        group.get_player_by_id.assert_not_called()

    def test_mark_group_dropped_sets_random_signal_fallback(self):
        from bargaining_tdl_main import _mark_group_dropped

        group = self._make_group(interrupted_id=2)
        p1 = MagicMock()
        p1.id_in_group = 1
        p1.participant.vars = {}
        p2 = MagicMock()
        p2.id_in_group = 2
        p2.participant.vars = {}
        p3 = MagicMock()
        p3.id_in_group = 3
        p3.participant.vars = {}
        group.get_players.return_value = [p1, p2, p3]

        _mark_group_dropped(group)

        self.assertTrue(group.group_dropped)
        self.assertEqual(p2.signal_inactive, 99)
        self.assertIn(p2.signal_left, ['split_you', 'split_other', 'split_both'])
        self.assertIn(p2.signal_right, ['split_you', 'split_other', 'split_both'])
        self.assertFalse(p2.part1_payoff_eligible)
        self.assertEqual(p2.participant.vars.get('signal_inactive'), 99)
        self.assertEqual(p2.participant.vars.get('group_dropped'), True)
        self.assertTrue(p1.part1_payoff_eligible)
        self.assertTrue(p3.part1_payoff_eligible)


if __name__ == '__main__':
    unittest.main()
