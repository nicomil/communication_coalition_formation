from otree.api import Bot, expect, Submission  # type: ignore
from bargaining_tdl_common import get_page_timeout_seconds  # type: ignore
from . import _SURVEY_PAGE10_TIMEOUT  # type: ignore
from . import (  # type: ignore
    SurveyIntro,
    SurveyQuestions,
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
        yield Submission(FinalResults, dict(time_on_page=1.0), check_html=False)

        expect(self.player.age, 30)
        expect(self.player.beauty_contest_guess, 1.5)
