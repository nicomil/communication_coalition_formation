"""Test della finalizzazione d'ufficio dei partecipanti spariti.

I bot non possono coprire questo caso: un bot invia sempre la pagina, mentre
qui il punto è proprio il partecipante che chiude il browser e non invia mai
nulla. Le funzioni sotto test non toccano il database, quindi si verificano
con stub leggeri.
"""

import time
import unittest

from . import (
    ABSENT_FINALIZE_SECONDS,
    finalize_absent_players,
    is_participant_absent,
    seconds_until_absent,
)


class _StubParticipant:
    def __init__(self, last_request_ago=0.0, timeout_in=None):
        now = time.time()
        self._last_request_timestamp = now - last_request_ago
        self._timeout_expiration_time = None if timeout_in is None else now + timeout_in
        self.part1_payoff_eligible = True
        self.vars = {}


class _StubPlayer:
    def __init__(self, id_in_group, decision=None, last_request_ago=0.0, timeout_in=None):
        self.id_in_group = id_in_group
        self.decision_choice = decision
        self.decision_inactive = 0
        self.part1_payoff_eligible = True
        self.participant = _StubParticipant(last_request_ago, timeout_in)

    def field_maybe_none(self, name):
        return getattr(self, name)


class _StubGroup:
    id = 7

    def __init__(self, players):
        self._players = players

    def get_players(self):
        return self._players


class AbsenceDetectionTests(unittest.TestCase):
    def test_recent_request_is_not_absent(self):
        player = _StubPlayer(1, last_request_ago=10, timeout_in=290)
        self.assertFalse(is_participant_absent(player))

    def test_silence_beyond_threshold_is_absent(self):
        player = _StubPlayer(1, last_request_ago=ABSENT_FINALIZE_SECONDS + 1)
        self.assertTrue(is_participant_absent(player))

    def test_expired_page_timeout_is_absent(self):
        # Browser chiuso: il timeout di pagina è scaduto lato server ma
        # nessun client lo ha mai inviato.
        player = _StubPlayer(1, last_request_ago=10, timeout_in=-1)
        self.assertTrue(is_participant_absent(player))

    def test_seconds_until_absent_counts_down(self):
        player = _StubPlayer(1, last_request_ago=ABSENT_FINALIZE_SECONDS - 30)
        self.assertGreater(seconds_until_absent(player), 0)
        self.assertLessEqual(seconds_until_absent(player), 30)

    def test_seconds_until_absent_is_zero_when_gone(self):
        player = _StubPlayer(1, last_request_ago=ABSENT_FINALIZE_SECONDS + 5)
        self.assertEqual(seconds_until_absent(player), 0)


class FinalizeAbsentPlayersTests(unittest.TestCase):
    def test_absent_player_gets_random_choice_and_loses_eligibility(self):
        gone = _StubPlayer(3, last_request_ago=ABSENT_FINALIZE_SECONDS + 60)
        group = _StubGroup([
            _StubPlayer(1, decision='Left'),
            _StubPlayer(2, decision='Right'),
            gone,
        ])

        self.assertTrue(finalize_absent_players(group))
        self.assertIn(gone.decision_choice, ('Left', 'Right', 'NoOne'))
        self.assertEqual(gone.decision_inactive, 99)
        self.assertFalse(gone.part1_payoff_eligible)
        self.assertFalse(gone.participant.vars['part1_payoff_eligible'])

    def test_player_still_online_is_left_alone(self):
        thinking = _StubPlayer(3, last_request_ago=20, timeout_in=280)
        group = _StubGroup([
            _StubPlayer(1, decision='Left'),
            _StubPlayer(2, decision='Right'),
            thinking,
        ])

        # Non è pronto: chi ha finito deve aspettare, non rubargli la scelta.
        self.assertFalse(finalize_absent_players(group))
        self.assertIsNone(thinking.decision_choice)
        self.assertTrue(thinking.part1_payoff_eligible)

    def test_force_finalizes_even_someone_online(self):
        thinking = _StubPlayer(3, last_request_ago=20, timeout_in=280)
        group = _StubGroup([
            _StubPlayer(1, decision='Left'),
            _StubPlayer(2, decision='Right'),
            thinking,
        ])

        self.assertTrue(finalize_absent_players(group, force=True))
        self.assertIn(thinking.decision_choice, ('Left', 'Right', 'NoOne'))
        self.assertFalse(thinking.part1_payoff_eligible)

    def test_existing_decisions_are_never_overwritten(self):
        decided = _StubPlayer(3, decision='NoOne', last_request_ago=9999)
        group = _StubGroup([
            _StubPlayer(1, decision='Left'),
            _StubPlayer(2, decision='Right'),
            decided,
        ])

        self.assertTrue(finalize_absent_players(group, force=True))
        self.assertEqual(decided.decision_choice, 'NoOne')
        self.assertTrue(decided.part1_payoff_eligible)
