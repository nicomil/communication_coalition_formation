import unittest

from otree.api import Bot, expect  # type: ignore

from . import (
    ControlQuestionsAttempt1,
    InstructionsPart1,
    Welcome,
    build_randomized_schedule,
)


BOT_CASES = ['mutual_12', 'disagreement', 'no_dwl_star', 'signals_timeout']


class PlayerBot(Bot):
    """Attraversa onboarding e risponde alla CQ specifica del trattamento."""

    cases = BOT_CASES

    def play_round(self):
        yield Welcome, dict(
            time_on_page=1.0,
            prolific_pid_url=f'test-{self.participant.code}',
            prolific_study_id='test-study-id',
            prolific_session_id='test-session-id',
        )

        expect(self.player.assigned_treatment, '!=', '')
        expect(
            self.player.participant.vars.get('treatment'),
            self.player.assigned_treatment,
        )

        yield InstructionsPart1, dict(time_on_page=1.0)

        example2_you = (
            '6' if self.player.assigned_treatment == 'private_no_dwl' else '0'
        )
        yield ControlQuestionsAttempt1, dict(
            example1_earnings_you='0',
            example1_earnings_left='0',
            example1_earnings_right='0',
            example2_earnings_you=example2_you,
            example2_earnings_left='0',
            example2_earnings_right='0',
            example3_earnings_you='0',
            example3_earnings_left='3',
            example3_earnings_right='3',
            time_on_page=1.0,
        )

        expect(self.player.assignment_status, 'passed')
        expect(self.player.participant.vars.get('assignment_status'), 'passed')
        expect(self.player.time_welcome, '>=', 0)
        expect(self.player.participant.prolific_study_id, 'test-study-id')


class RandomizedScheduleTests(unittest.TestCase):
    def test_each_full_block_has_three_slots_per_arm(self):
        treatments = ['private', 'public', 'private_no_dwl']
        schedule = build_randomized_schedule(treatments, 18, seed=123)
        self.assertEqual(len(schedule), 18)
        for start in range(0, 18, 9):
            block = schedule[start:start + 9]
            self.assertEqual(
                {treatment: block.count(treatment) for treatment in treatments},
                {treatment: 3 for treatment in treatments},
            )

    def test_seed_is_reproducible(self):
        treatments = ['private', 'public', 'private_no_dwl']
        self.assertEqual(
            build_randomized_schedule(treatments, 18, seed=77),
            build_randomized_schedule(treatments, 18, seed=77),
        )

    def test_isolated_treatment_fills_every_slot(self):
        self.assertEqual(
            build_randomized_schedule(['public'], 7, seed=11),
            ['public'] * 7,
        )
