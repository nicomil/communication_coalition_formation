import itertools
import unittest

from otree.api import Bot, Currency as cu, expect, Submission  # type: ignore

from bargaining_tdl_common import TREATMENTS, VALID_DECISIONS, custom_calculate_payoff_vector
from . import (
    C,
    Chat,
    Decision,
    ExperimentTerminated,
    InactivityGoodbyeMain,
    PostDecisionConfidence,
    Results,
    Signals,
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
            # Il timeout su Signals ora fa cadere il gruppo: _mark_group_dropped
            # assegna d'ufficio segnali, decisione e guess all'interrotto, e
            # participant.vars['timeout_excluded'] lo manda su
            # ExperimentTerminated invece che a Decision.
            expect(self.player.participant.vars.get('timeout_excluded'), True)
            yield Submission(
                ExperimentTerminated,
                dict(time_on_page=1.0),
                check_html=False,
            )
        else:
            yield Signals, dict(
                signal_left=signal_left,
                signal_right=signal_right,
                first_intention_selected='left',
                time_on_page=1.0,
            )

        # Da qui in poi le pagine dipendono da come è finito il gruppo, non dal
        # nome del caso: si segue is_displayed, che è la stessa condizione che
        # usa oTree per servirle.
        decision = decisions_for_case(self.case, player_id)
        if Decision.is_displayed(self.player):
            yield Decision, dict(decision_choice=decision, time_on_page=1.5)
        # Le scale di convincingness e le guess sui partner sono state
        # spostate su PostDecisionConfidence (dopo Decision).
        if PostDecisionConfidence.is_displayed(self.player):
            yield Submission(
                PostDecisionConfidence,
                dict(
                    guess_left_confidence=5,
                    guess_right_confidence=2,
                    guess_left_choice='Left',
                    guess_right_choice='NoOne',
                    time_on_page=1.0,
                ),
                check_html=False,
            )
        if Results.is_displayed(self.player):
            yield Results, dict(time_on_page=2.0)
        if InactivityGoodbyeMain.is_displayed(self.player):
            yield Submission(
                InactivityGoodbyeMain,
                dict(time_on_page=1.0),
                check_html=False,
            )
            return

        expect(self.player.guess_left_confidence, 5)
        expect(self.player.guess_right_confidence, 2)



class PayoffLogicTests(unittest.TestCase):
    """Oracle indipendente per 27 profili × 3 trattamenti."""

    # Importi dimezzati rispetto al disegno originale (6/12) dopo
    # l'eliminazione della vecchia strategia (2,2,2): coalizione reciproca
    # $3 a testa, star no-DWL $6 al sostenuto. Coerente con le istruzioni e
    # con le control questions, che offrono solo $6/$3/$0.
    @staticmethod
    def expected(profile, no_dwl):
        c1, c2, c3 = profile
        if c1 == 'Right' and c2 == 'Left':
            return (3, 3, 0)
        if c2 == 'Right' and c3 == 'Left':
            return (0, 3, 3)
        if c3 == 'Right' and c1 == 'Left':
            return (3, 0, 3)
        if no_dwl:
            if c1 == 'NoOne' and c2 == 'Left' and c3 == 'Right':
                return (6, 0, 0)
            if c2 == 'NoOne' and c1 == 'Right' and c3 == 'Left':
                return (0, 6, 0)
            if c3 == 'NoOne' and c1 == 'Left' and c2 == 'Right':
                return (0, 0, 6)
        return (0, 0, 0)

    def test_all_profiles_in_all_treatments(self):
        for treatment, config in TREATMENTS.items():
            for profile in itertools.product(VALID_DECISIONS, repeat=3):
                with self.subTest(treatment=treatment, profile=profile):
                    actual, _ = custom_calculate_payoff_vector(
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
            custom_calculate_payoff_vector(('Right', 'Left', 'NoOne'))[0],
            (3, 3, 0),
        )
        # Example 2: both partners support Green, who supports no one.
        profile = ('NoOne', 'Left', 'Right')
        self.assertEqual(custom_calculate_payoff_vector(profile, False)[0], (0, 0, 0))
        self.assertEqual(custom_calculate_payoff_vector(profile, True)[0], (6, 0, 0))
        # Example 3: directed cycle.
        self.assertEqual(
            custom_calculate_payoff_vector(('Right', 'Right', 'NoOne'))[0],
            (0, 0, 0),
        )
