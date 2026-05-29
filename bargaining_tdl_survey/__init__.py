from otree.api import (  # type: ignore
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Page,
)
from bargaining_tdl_common import (  # type: ignore
    get_page_timeout_seconds,
    timeout_submission_with_time,
)

_SURVEY_PAGE_TIMEOUT = 180
_SURVEY_PAGE10_TIMEOUT = 300


class _SurveyTimedPage(Page):
    @staticmethod
    def get_timeout_seconds(player):
        return get_page_timeout_seconds(player, _SURVEY_PAGE_TIMEOUT)


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


def _mark_inactive_exclusion(player, reason):
    player.participant.inactive_excluded = True
    player.participant.inactive_excluded_reason = reason
    player.participant.vars['inactive_excluded'] = True
    player.participant.vars['inactive_excluded_reason'] = reason


def _is_inactive_excluded(player):
    return bool(player.participant.vars.get('inactive_excluded', False))


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
        min=1,
        max=20,
        label="Please indicate how many years you studied at university?",
    )

    # Job status
    job_status = models.StringField(
        choices=[
            ['employee', 'Employee'],
            ['employer', 'Employer'],
            ['self_employed', 'Self-employed'],
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

    # 11-20 game — guess an amount 1.10-2.00 (steps of 0.10)
    beauty_contest_guess = models.FloatField(
        min=1.1,
        max=2.0,
        label="What amount of money would you request?",
    )

    instructions_clarity = models.IntegerField(
        min=1,
        max=5,
        label="How clear were the experiment instructions?",
    )

    general_comment = models.LongStringField(
        label="Please write any general comment about the experiment:",
        blank=False,
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
    time_survey_feedback = models.FloatField(initial=0)
    time_final_results = models.FloatField(initial=0)


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


class SurveyQuestions(_SurveyTimedPage):
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

    timeout_submission = timeout_submission_with_time(
        _SURVEY_PAGE_TIMEOUT,
        gender=0,
        age=18,
        field_of_study='N/A',
        university_years=1,
        job_status='employee',
    )

    @staticmethod
    def field_of_study_error_message(player, value):
        """Reject values that contain no alphabetic characters (e.g. pure numbers)."""
        if value and not any(c.isalpha() for c in value):
            return 'Please enter a valid field of study (text only, no numbers).'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_questions = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_questions_timeout')


class SurveyScaleIntro(Page):
    """Instructions page explaining the 0–10 willingness and self-assessment scales."""
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_scale_intro = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage4(_SurveyTimedPage):
    """Willingness to delay gratification — 0–10 scale."""
    form_model = 'player'
    form_fields = ['willingness_future', 'time_on_page']
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT, willingness_future=0)

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page4 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page4_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage5(_SurveyTimedPage):
    """General willingness to take risks — 0–10 scale."""
    form_model = 'player'
    form_fields = ['willingness_risk', 'time_on_page']
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT, willingness_risk=0)

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page5 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page5_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage6(_SurveyTimedPage):
    """Positive reciprocity self-assessment — 0–10 scale."""
    form_model = 'player'
    form_fields = ['reciprocity_positive', 'time_on_page']
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT, reciprocity_positive=0)

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page6 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page6_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage7(_SurveyTimedPage):
    """Negative reciprocity self-assessment — 0–10 scale."""
    form_model = 'player'
    form_fields = ['reciprocity_negative', 'time_on_page']
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT, reciprocity_negative=0)

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page7 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page7_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage8(_SurveyTimedPage):
    """Altruism — willingness to donate to good causes — 0–10 scale."""
    form_model = 'player'
    form_fields = ['willingness_donate', 'time_on_page']
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT, willingness_donate=0)

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page8 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page8_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage9(_SurveyTimedPage):
    """General trust self-assessment — 0–10 scale."""
    form_model = 'player'
    form_fields = ['trust_general', 'time_on_page']
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT, trust_general=0)

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page9 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page9_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyPage10(_SurveyTimedPage):
    """11-20 game — guess a number between 110 and 200."""
    form_model = 'player'
    form_fields = ['beauty_contest_guess', 'time_on_page']
    timeout_submission = timeout_submission_with_time(
        _SURVEY_PAGE10_TIMEOUT,
        beauty_contest_guess=1.1,
    )

    @staticmethod
    def get_timeout_seconds(player):
        return get_page_timeout_seconds(player, _SURVEY_PAGE10_TIMEOUT)

    @staticmethod
    def beauty_contest_guess_error_message(player, value):
        if value is not None:
            val_in_cents = round(value * 100)
            if val_in_cents % 10 != 0:
                return 'Please enter a number in steps of $ 0.10 (e.g., 1.10, 1.20, 1.30... 2.00).'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page10 = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_page10_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyFeedback(_SurveyTimedPage):
    """Feedback page shown after survey page 10 and before final results."""
    form_model = 'player'
    form_fields = ['instructions_clarity', 'general_comment', 'time_on_page']
    timeout_submission = timeout_submission_with_time(
        _SURVEY_PAGE_TIMEOUT,
        instructions_clarity=1,
        general_comment='No comment provided (timeout).',
    )

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(1, 6))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_feedback = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_feedback_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveyTerminated(Page):
    template_name = 'bargaining_tdl_survey/SurveyTerminated.html'
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        return _is_inactive_excluded(player)

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.session.config.get('completionlink', '').strip(),
        )

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return []


class FinalResults(Page):
    """Final screen of the experiment summarizing payoffs."""
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)

    @staticmethod
    def vars_for_template(player):
        from otree.api import Currency as cu
        
        part1_group_id = player.participant.vars.get('part1_group_id')
        selected = player.participant.vars.get('selected_part_for_payment', 1)
        part1_payoff_eligible = bool(player.participant.vars.get('part1_payoff_eligible', True))
            
        base_fee = cu(3)
        beauty_contest_bonus = cu(player.beauty_contest_guess or 0)
        part1_payoff_val = player.participant.vars.get('part1_payoff', cu(0))
        if not part1_payoff_eligible:
            part1_payoff_val = cu(0)
        
        if selected == 1 and part1_payoff_eligible:
            subtotal = base_fee + part1_payoff_val + beauty_contest_bonus
        else:
            subtotal = base_fee + beauty_contest_bonus
            if selected != 1:
                part1_payoff_val = "TBD"

        from bargaining_tdl_common import get_main_group_player, TOPOLOGY, COLOR_MAPPING
        
        main_player = get_main_group_player(player)
        left_choice_display = ""
        right_choice_display = ""
        left_color = ""
        right_color = ""
        left_inactive = False
        right_inactive = False
        my_choice_display = ""
        my_color = ""
        
        if main_player:
            my_id = main_player.id_in_group
            partners = TOPOLOGY[my_id]
            left_id = partners['left']
            right_id = partners['right']
            
            left_partner = main_player.group.get_player_by_id(left_id)
            right_partner = main_player.group.get_player_by_id(right_id)
            
            left_color = COLOR_MAPPING[left_id]
            right_color = COLOR_MAPPING[right_id]
            my_color = COLOR_MAPPING[my_id]
            
            left_inactive = (left_partner.decision_inactive == 99)
            right_inactive = (right_partner.decision_inactive == 99)

            # Formatta la propria scelta
            my_c = main_player.decision_choice
            if my_c == 'Both':
                my_choice_display = "I would like to divide the $12 equally with the two participants"
            elif my_c == 'Left':
                my_left_id = TOPOLOGY[my_id]['left']
                my_choice_display = f"I would like to divide the $12 equally only with the {COLOR_MAPPING[my_left_id]} Participant"
            else:
                my_right_id = TOPOLOGY[my_id]['right']
                my_choice_display = f"I would like to divide the $12 equally only with the {COLOR_MAPPING[my_right_id]} Participant"
            
            # Formatta la scelta del left partner
            left_c = left_partner.decision_choice
            if left_c == 'Both':
                left_choice_display = "I would like to divide the $12 equally with the two participants"
            elif left_c == 'Left':
                left_partner_left_id = TOPOLOGY[left_id]['left']
                left_choice_display = f"I would like to divide the $12 equally with the {COLOR_MAPPING[left_partner_left_id]} Participant"
            else:
                left_partner_right_id = TOPOLOGY[left_id]['right']
                left_choice_display = f"I would like to divide the $12 equally with the {COLOR_MAPPING[left_partner_right_id]} Participant"

            # Formatta la scelta del right partner
            right_c = right_partner.decision_choice
            if right_c == 'Both':
                right_choice_display = "I would like to divide the $12 equally with the two participants"
            elif right_c == 'Left':
                right_partner_left_id = TOPOLOGY[right_id]['left']
                right_choice_display = f"I would like to divide the $12 equally only with the {COLOR_MAPPING[right_partner_left_id]} Participant"
            else:
                right_partner_right_id = TOPOLOGY[right_id]['right']
                right_choice_display = f"I would like to divide the $12 equally only with the {COLOR_MAPPING[right_partner_right_id]} Participant"

        return {
            'part1_group_id': part1_group_id,
            'selected': selected,
            'part1_payoff_eligible': part1_payoff_eligible,
            'part1_payoff': part1_payoff_val,
            'subtotal': subtotal,
            'base_fee': base_fee,
            'beauty_contest_bonus': beauty_contest_bonus,
            'left_color': left_color,
            'right_color': right_color,
            'left_choice_display': left_choice_display,
            'right_choice_display': right_choice_display,
            'my_choice_display': my_choice_display,
            'my_color': my_color,
            'left_inactive': left_inactive,
            'right_inactive': right_inactive,
        }

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.session.config.get('completionlink', '').strip(),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_final_results = player.time_on_page or 0


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
    SurveyFeedback,
    SurveyTerminated,
    FinalResults,
]
