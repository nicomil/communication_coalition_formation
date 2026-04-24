from otree.api import (  # type: ignore
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Page,
)

doc = """
Post-experiment survey.
Collects demographic information and one question about other participants' choices.
"""


class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Gender: 0=Male, 1=Female, 2=Other
    gender = models.IntegerField(
        choices=[
            [0, 'Male'],
            [1, 'Female'],
            [2, 'Other'],
        ],
        widget=widgets.RadioSelect,
        label="Please indicate your gender:",
    )

    # Age: numeric 18–99
    age = models.IntegerField(
        min=18,
        max=99,
        label="Please indicate your age:",
    )

    # Field of study: free text
    field_of_study = models.StringField(
        label="Please indicate your field of study:",
        blank=False,
    )

    # University years: free numeric input
    university_years = models.IntegerField(
        min=0,
        label="Please indicate how many years you studied at university?",
    )

    # Job status
    job_status = models.StringField(
        choices=[
            ['employee', 'Employee'],
            ['employer', 'Employer'],
            ['not_in_labour_force', 'Not in the labour force'],
        ],
        widget=widgets.RadioSelect,
        label="Please indicate your job status:",
    )

    # ── Scale questions ──────────────────────────────────────────────────────
    # Willingness to delay gratification (0–10)
    willingness_future = models.IntegerField(
        min=0,
        max=10,
        label="How willing are you to give up something that is beneficial for you today "
              "in order to benefit more from that in the future?",
    )

    # General willingness to take risks (0–10)
    willingness_risk = models.IntegerField(
        min=0,
        max=10,
        label="Please tell me, in general, how willing or unwilling you are to take risks.",
    )

    # Positive reciprocity — self-assessment (0–10)
    reciprocity_positive = models.IntegerField(
        min=0,
        max=10,
        label="When someone does me a favor I am willing to return it.",
    )

    # Negative reciprocity — self-assessment (0–10)
    reciprocity_negative = models.IntegerField(
        min=0,
        max=10,
        label="If I am treated very unjustly, I will take revenge at the first occasion, "
              "even if there is a cost to do so.",
    )

    # Altruism — willingness to donate (0–10)
    willingness_donate = models.IntegerField(
        min=0,
        max=10,
        label="How willing are you to give to good causes without expecting anything in return?",
    )

    # General trust — self-assessment (0–10)
    trust_general = models.IntegerField(
        min=0,
        max=10,
        label="I assume that people have only the best intentions.",
    )

    # Beauty contest — guess a number 0–100 (decimals allowed)
    beauty_contest_guess = models.FloatField(
        min=0,
        max=100,
        label="Please select a number between 0 and 100:",
    )

    # Time tracking
    time_on_page = models.FloatField(initial=0, blank=True)
    time_survey_intro = models.FloatField(initial=0)
    time_survey_questions = models.FloatField(initial=0)
    time_survey_scale_intro = models.FloatField(initial=0)
    time_survey_page4 = models.FloatField(initial=0)
    time_survey_page5 = models.FloatField(initial=0)
    time_survey_page6 = models.FloatField(initial=0)
    time_survey_page7 = models.FloatField(initial=0)
    time_survey_page8 = models.FloatField(initial=0)
    time_survey_page9 = models.FloatField(initial=0)
    time_survey_page10 = models.FloatField(initial=0)


# ──────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────

class SurveyIntro(Page):
    """Introductory page with thank-you text and survey description."""
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_intro = player.time_on_page or 0


class SurveyQuestions(Page):
    """Demographic questions page."""
    form_model = 'player'
    form_fields = [
        'gender',
        'age',
        'field_of_study',
        'university_years',
        'job_status',
        'time_on_page',
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_questions = player.time_on_page or 0


class SurveyScaleIntro(Page):
    """Instructions page explaining the 0–10 willingness and self-assessment scales."""
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_scale_intro = player.time_on_page or 0


class SurveyPage4(Page):
    """Willingness to delay gratification — 0–10 scale."""
    form_model = 'player'
    form_fields = ['willingness_future', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page4 = player.time_on_page or 0


class SurveyPage5(Page):
    """General willingness to take risks — 0–10 scale."""
    form_model = 'player'
    form_fields = ['willingness_risk', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page5 = player.time_on_page or 0


class SurveyPage6(Page):
    """Positive reciprocity self-assessment — 0–10 scale."""
    form_model = 'player'
    form_fields = ['reciprocity_positive', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page6 = player.time_on_page or 0


class SurveyPage7(Page):
    """Negative reciprocity self-assessment — 0–10 scale."""
    form_model = 'player'
    form_fields = ['reciprocity_negative', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page7 = player.time_on_page or 0


class SurveyPage8(Page):
    """Altruism — willingness to donate to good causes — 0–10 scale."""
    form_model = 'player'
    form_fields = ['willingness_donate', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page8 = player.time_on_page or 0


class SurveyPage9(Page):
    """General trust self-assessment — 0–10 scale."""
    form_model = 'player'
    form_fields = ['trust_general', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page9 = player.time_on_page or 0


class SurveyPage10(Page):
    """Beauty contest — guess a number between 0 and 100."""
    form_model = 'player'
    form_fields = ['beauty_contest_guess', 'time_on_page']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page10 = player.time_on_page or 0


page_sequence = [
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
]
