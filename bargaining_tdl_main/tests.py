import itertools
import unittest

from otree.api import Bot, Currency as cu, expect, Submission  # type: ignore

from bargaining_tdl_common import TREATMENTS
from . import (
    C,
    Chat,
    Decision,
    InactivityGoodbyeMain,
    Results,
    Signals,
    VALID_DECISIONS,
    calculate_payoff_vector,
)


BOT_CASES = ['mutual_12', 'disagreement', 'no_dwl_star', 'signals_timeout']


def decisions_for_case(case, player_id):
    profiles = {
        'mutual_12': ('Right', 'Left', 'NoOne'),
        'disagreement': ('Left', 'Left', 'Left'),
        'no_dwl_star': ('NoOne', 'Left', 'Right'),
        'signals_timeout': ('Right', 'Left', 'NoOne'),
    }
    return profiles[case][player_id - 1]


class PlayerBot(Bot):
    """Bot completo per chat, messaggi, decisione e payoff Part 1."""

    cases = BOT_CASES

    def play_round(self):
        yield Chat, dict(time_on_page=1.0)

        player_id = self.player.id_in_group
        signals = {
            1: ('split_you', 'split_other'),
            2: ('split_other', 'support_none'),
            3: ('support_none', 'split_you'),
        }
        signal_left, signal_right = signals[player_id]
        if self.case == 'signals_timeout':
            yield Submission(Signals, {}, timeout_happened=True)
            expect(
                self.player.field_maybe_none('signal_left_convincingness'),
                None,
            )
            expect(
                self.player.field_maybe_none('signal_right_convincingness'),
                None,
            )
        else:
            yield Signals, dict(
                signal_left=signal_left,
                signal_right=signal_right,
                signal_left_convincingness=3,
                signal_right_convincingness=4,
                first_intention_selected='left',
                time_on_page=1.0,
            )

        decision = decisions_for_case(self.case, player_id)
        yield Decision, dict(decision_choice=decision, time_on_page=1.5)
        yield Results, dict(time_on_page=2.0)

        no_dwl = self.player.treatment == 'private_no_dwl'
        expected_vector, expected_outcome = calculate_payoff_vector(
            tuple(decisions_for_case(self.case, pid) for pid in (1, 2, 3)),
            no_deadweight_loss=no_dwl,
        )
        expect(
            self.player.part1_calculated_payoff,
            cu(expected_vector[player_id - 1]),
        )
        expect(self.group.group_outcome, expected_outcome)
        if self.case == 'signals_timeout':
            expect(self.player.payoff, cu(0))
            yield Submission(
                InactivityGoodbyeMain,
                dict(time_on_page=1.0),
                check_html=False,
            )
            return

        expect(self.player.signal_left_convincingness, 3)
        expect(self.player.signal_right_convincingness, 4)
        expect(
            self.player.participant.vars.get('part1_payoff'),
            self.player.part1_calculated_payoff,
        )


class PayoffLogicTests(unittest.TestCase):
    """Oracle indipendente per 27 profili × 3 trattamenti."""

    @staticmethod
    def expected(profile, no_dwl):
        c1, c2, c3 = profile
        if c1 == 'Right' and c2 == 'Left':
            return (6, 6, 0)
        if c2 == 'Right' and c3 == 'Left':
            return (0, 6, 6)
        if c3 == 'Right' and c1 == 'Left':
            return (6, 0, 6)
        if no_dwl:
            if c1 == 'NoOne' and c2 == 'Left' and c3 == 'Right':
                return (12, 0, 0)
            if c2 == 'NoOne' and c1 == 'Right' and c3 == 'Left':
                return (0, 12, 0)
            if c3 == 'NoOne' and c1 == 'Left' and c2 == 'Right':
                return (0, 0, 12)
        return (0, 0, 0)

    def test_all_profiles_in_all_treatments(self):
        for treatment, config in TREATMENTS.items():
            for profile in itertools.product(VALID_DECISIONS, repeat=3):
                with self.subTest(treatment=treatment, profile=profile):
                    actual, _ = calculate_payoff_vector(
                        profile,
                        no_deadweight_loss=config['no_deadweight_loss'],
                    )
                    self.assertEqual(
                        actual,
                        self.expected(profile, config['no_deadweight_loss']),
                    )

    def test_control_question_profiles(self):
        # Example 1: Green/Blue support each other.
        self.assertEqual(
            calculate_payoff_vector(('Right', 'Left', 'NoOne'))[0],
            (6, 6, 0),
        )
        # Example 2: both partners support Green, who supports no one.
        profile = ('NoOne', 'Left', 'Right')
        self.assertEqual(calculate_payoff_vector(profile, False)[0], (0, 0, 0))
        self.assertEqual(calculate_payoff_vector(profile, True)[0], (12, 0, 0))
        # Example 3: directed cycle.
        self.assertEqual(
            calculate_payoff_vector(('Right', 'Right', 'NoOne'))[0],
            (0, 0, 0),
        )
