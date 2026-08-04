from otree.api import Bot, Currency as cu, expect, Submission  # type: ignore
from bargaining_tdl_common import get_page_timeout_seconds  # type: ignore
from . import _SURVEY_PAGE10_TIMEOUT  # type: ignore
from . import (  # type: ignore
    SurveyIntro,
    SurveyQuestions,
    SurveyPage1,
    SurveyPage2,
    SurveyPage3,
    SurveyScaleIntro,
    SurveyPage4,
    SurveyPage5,
    SurveyPage6,
    SurveyPage7,
    SurveyPage8,
    SurveyPage9,
    SurveyPage10,
    SurveyFeedback,
    FinalResults,
)


class PlayerBot(Bot):
    cases = ['mutual_12', 'disagreement', 'no_dwl_star', 'signals_timeout']

    def play_round(self):
        yield SurveyIntro, dict(time_on_page=1.0)
        yield SurveyPage1, {
            **{f'sd3_mach_{index:02d}': 3 for index in range(1, 10)},
            'time_on_page': 2.0,
        }
        yield SurveyPage2, {
            **{f'sd3_narc_{index:02d}': 3 for index in range(1, 10)},
            'time_on_page': 2.0,
        }
        yield SurveyPage3, {
            **{f'sd3_psych_{index:02d}': 3 for index in range(1, 10)},
            'time_on_page': 2.0,
        }
        yield SurveyScaleIntro, dict(time_on_page=1.0)
        yield SurveyPage4, dict(willingness_future=5, time_on_page=1.0)
        yield SurveyPage5, dict(willingness_risk=5, time_on_page=1.0)
        yield SurveyPage6, dict(reciprocity_positive=5, time_on_page=1.0)
        yield SurveyPage7, dict(reciprocity_negative=5, time_on_page=1.0)
        yield SurveyPage8, dict(willingness_donate=5, time_on_page=1.0)
        yield SurveyPage9, dict(trust_general=5, time_on_page=1.0)
        expect(
            SurveyPage10.get_timeout_seconds(self.player),
            get_page_timeout_seconds(self.player, _SURVEY_PAGE10_TIMEOUT),
        )
        yield SurveyPage10, dict(beauty_contest_guess=1.5, time_on_page=1.0)
        yield SurveyQuestions, dict(
            gender=0,
            birth_year=1990,
            field_of_study=1,
            university_years=5,
            main_situation='paid_work',
            job_type='employee',
            time_on_page=2.0,
        )
        yield SurveyFeedback, dict(
            instructions_clarity=4,
            general_comment='Instructions were mostly clear.',
            time_on_page=1.0,
        )

        payment = FinalResults.vars_for_template(self.player)
        expected_fee = cu(self.player.session.config.get('participation_fee', 1.50))
        expected_part1 = self.player.participant.vars.get('part1_payoff', cu(0))
        if not self.player.participant.vars.get('part1_payoff_eligible', True):
            expected_part1 = cu(0)
        expected_guess_bonus = cu(
            self.player.participant.vars.get('guess_bonus_cents', 0) / 100
        )
        expect(payment['base_fee'], expected_fee)
        expect(payment['part1_payoff'], expected_part1)
        expect(payment['beauty_contest_bonus'], cu(1.5))
        expect(payment['guess_bonus'], expected_guess_bonus)
        expect(
            payment['subtotal'],
            expected_fee + expected_part1 + cu(1.5) + expected_guess_bonus,
        )

        yield Submission(FinalResults, dict(time_on_page=1.0), check_html=False)

        expect(self.player.birth_year, 1990)
        expect(self.player.sd3_mach_01, 3)
        expect(self.player.sd3_narc_09, 3)
        expect(self.player.sd3_psych_08, 3)
        expect(self.player.beauty_contest_guess, 1.5)
