from otree.api import Bot, Currency as cu, expect, Submission  # type: ignore
from bargaining_tdl_common import get_page_timeout_seconds  # type: ignore
from . import _SURVEY_PAGE10_TIMEOUT  # type: ignore
from . import (  # type: ignore
    SurveyIntro,
    SurveyQuestions,
    SurveySD3Machiavellianism,
    SurveySD3Narcissism,
    SurveySD3Psychopathy,
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
        yield SurveyQuestions, dict(
            gender=0,
            age=30,
            field_of_study='Economics',
            university_years=5,
            job_status='employee',
            time_on_page=2.0,
        )
        yield SurveySD3Machiavellianism, {
            **{f'sd3_mach_{index:02d}': 3 for index in range(1, 10)},
            'time_on_page': 2.0,
        }
        yield SurveySD3Narcissism, {
            **{f'sd3_narc_{index:02d}': 3 for index in range(1, 10)},
            'time_on_page': 2.0,
        }
        yield SurveySD3Psychopathy, {
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
        yield SurveyFeedback, dict(
            instructions_clarity=4,
            general_comment='Instructions were mostly clear.',
            time_on_page=1.0,
        )

        payment = FinalResults.vars_for_template(self.player)
        expected_part1 = self.player.participant.vars.get('part1_payoff', cu(0))
        expect(payment['base_fee'], cu(3))
        expect(payment['part1_payoff'], expected_part1)
        expect(payment['beauty_contest_bonus'], cu(1.5))
        expect(payment['subtotal'], cu(3) + expected_part1 + cu(1.5))

        yield Submission(FinalResults, dict(time_on_page=1.0), check_html=False)

        expect(self.player.age, 30)
        expect(self.player.sd3_mach_01, 3)
        expect(self.player.sd3_narc_09, 3)
        expect(self.player.sd3_psych_08, 3)
        expect(self.player.beauty_contest_guess, 1.5)
