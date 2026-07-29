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

AGREEMENT_SCALE = [
    (1, 'Disagree strongly'),
    (2, 'Disagree'),
    (3, 'Neither agree nor disagree'),
    (4, 'Agree'),
    (5, 'Agree strongly'),
]

SD3_MACHIAVELLIANISM_ITEMS = [
    ('sd3_mach_01', "It’s not wise to tell your secrets."),
    ('sd3_mach_02', 'I like to use clever manipulation to get my way.'),
    ('sd3_mach_03', 'Whatever it takes, you must get the important people on your side.'),
    ('sd3_mach_04', 'Avoid direct conflict with others because they may be useful in the future.'),
    ('sd3_mach_05', 'It’s wise to keep track of information that you can use against people later.'),
    ('sd3_mach_06', 'You should wait for the right time to get back at people.'),
    ('sd3_mach_07', 'There are things you should hide from other people to preserve your reputation.'),
    ('sd3_mach_08', 'Make sure your plans benefit yourself, not others.'),
    ('sd3_mach_09', 'Most people can be manipulated.'),
]

SD3_NARCISSISM_ITEMS = [
    ('sd3_narc_01', 'People see me as a natural leader.'),
    ('sd3_narc_02', 'I hate being the center of attention.'),
    ('sd3_narc_03', 'Many group activities tend to be dull without me.'),
    ('sd3_narc_04', 'I know that I am special because everyone keeps telling me so.'),
    ('sd3_narc_05', 'I like to get acquainted with important people.'),
    ('sd3_narc_06', 'I feel embarrassed if someone compliments me.'),
    ('sd3_narc_07', 'I have been compared to famous people.'),
    ('sd3_narc_08', 'I am an average person.'),
    ('sd3_narc_09', 'I insist on getting the respect I deserve.'),
]

SD3_PSYCHOPATHY_ITEMS = [
    ('sd3_psych_01', 'I like to get revenge on authorities.'),
    ('sd3_psych_02', 'I avoid dangerous situations.'),
    ('sd3_psych_03', 'Payback needs to be quick and nasty.'),
    ('sd3_psych_04', 'People often say I’m out of control.'),
    ('sd3_psych_05', 'It’s true that I can be mean to others.'),
    ('sd3_psych_06', 'People who mess with me always regret it.'),
    ('sd3_psych_07', 'I have never gotten into trouble with the law.'),
    ('sd3_psych_08', 'I enjoy having sex with people I hardly know.'),
    ('sd3_psych_09', 'I’ll say anything to get what I want.'),
]


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

    # Short Dark Triad: tre matrici da nove item, scala 1-5.
    sd3_mach_01 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[0][1])
    sd3_mach_02 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[1][1])
    sd3_mach_03 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[2][1])
    sd3_mach_04 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[3][1])
    sd3_mach_05 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[4][1])
    sd3_mach_06 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[5][1])
    sd3_mach_07 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[6][1])
    sd3_mach_08 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[7][1])
    sd3_mach_09 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_MACHIAVELLIANISM_ITEMS[8][1])

    sd3_narc_01 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[0][1])
    sd3_narc_02 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[1][1])
    sd3_narc_03 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[2][1])
    sd3_narc_04 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[3][1])
    sd3_narc_05 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[4][1])
    sd3_narc_06 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[5][1])
    sd3_narc_07 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[6][1])
    sd3_narc_08 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[7][1])
    sd3_narc_09 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_NARCISSISM_ITEMS[8][1])

    sd3_psych_01 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[0][1])
    sd3_psych_02 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[1][1])
    sd3_psych_03 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[2][1])
    sd3_psych_04 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[3][1])
    sd3_psych_05 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[4][1])
    sd3_psych_06 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[5][1])
    sd3_psych_07 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[6][1])
    sd3_psych_08 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[7][1])
    sd3_psych_09 = models.IntegerField(choices=AGREEMENT_SCALE, label=SD3_PSYCHOPATHY_ITEMS[8][1])

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
    time_survey_sd3_mach = models.FloatField(initial=0)
    time_survey_sd3_narc = models.FloatField(initial=0)
    time_survey_sd3_psych = models.FloatField(initial=0)
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
    def vars_for_template(player):
        from otree.api import Currency as cu
        return {
            'participation_fee': cu(
                player.session.config.get('participation_fee', 3)
            )
        }

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


def _matrix_context(player, items):
    return {
        'matrix_items': [
            {
                'number': index,
                'field_name': field_name,
                'text': text,
                'current_value': player.field_maybe_none(field_name),
            }
            for index, (field_name, text) in enumerate(items, start=1)
        ],
        'agreement_scale': AGREEMENT_SCALE,
    }


class SurveySD3Machiavellianism(_SurveyTimedPage):
    template_name = 'bargaining_tdl_survey/SurveyMatrix.html'
    form_model = 'player'
    form_fields = [
        *(field_name for field_name, _ in SD3_MACHIAVELLIANISM_ITEMS),
        'time_on_page',
    ]
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT)

    @staticmethod
    def vars_for_template(player):
        return _matrix_context(player, SD3_MACHIAVELLIANISM_ITEMS)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_sd3_mach = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_sd3_mach_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveySD3Narcissism(_SurveyTimedPage):
    template_name = 'bargaining_tdl_survey/SurveyMatrix.html'
    form_model = 'player'
    form_fields = [
        *(field_name for field_name, _ in SD3_NARCISSISM_ITEMS),
        'time_on_page',
    ]
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT)

    @staticmethod
    def vars_for_template(player):
        return _matrix_context(player, SD3_NARCISSISM_ITEMS)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_sd3_narc = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_sd3_narc_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


class SurveySD3Psychopathy(_SurveyTimedPage):
    template_name = 'bargaining_tdl_survey/SurveyMatrix.html'
    form_model = 'player'
    form_fields = [
        *(field_name for field_name, _ in SD3_PSYCHOPATHY_ITEMS),
        'time_on_page',
    ]
    timeout_submission = timeout_submission_with_time(_SURVEY_PAGE_TIMEOUT)

    @staticmethod
    def vars_for_template(player):
        return _matrix_context(player, SD3_PSYCHOPATHY_ITEMS)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_sd3_psych = player.time_on_page or 0
        if timeout_happened:
            _mark_inactive_exclusion(player, 'survey_sd3_psych_timeout')

    @staticmethod
    def is_displayed(player):
        return not _is_inactive_excluded(player)


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
        part1_payoff_eligible = bool(player.participant.vars.get('part1_payoff_eligible', True))
            
        base_fee = cu(player.session.config.get('participation_fee', 3))
        beauty_contest_bonus = cu(player.beauty_contest_guess or 0)
        part1_payoff_val = player.participant.vars.get('part1_payoff', cu(0))
        if not part1_payoff_eligible:
            part1_payoff_val = cu(0)
        subtotal = base_fee + part1_payoff_val + beauty_contest_bonus

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

        def format_choice(choice, actor_id):
            actor_left_id = TOPOLOGY[actor_id]['left']
            actor_right_id = TOPOLOGY[actor_id]['right']
            if choice == 'Left':
                return (
                    "I intend to vote for 'I get $6, the "
                    f"{COLOR_MAPPING[actor_left_id]} Participant gets $6, "
                    "and the other Participant gets $0'"
                )
            if choice == 'Right':
                return (
                    "I intend to vote for 'I get $6, the "
                    f"{COLOR_MAPPING[actor_right_id]} Participant gets $6, "
                    "and the other Participant gets $0'"
                )
            return "I intend to vote for 'Support no one'"
        
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

            my_choice_display = format_choice(main_player.decision_choice, my_id)
            left_choice_display = format_choice(left_partner.decision_choice, left_id)
            right_choice_display = format_choice(right_partner.decision_choice, right_id)

        return {
            'part1_group_id': part1_group_id,
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
    SurveyTerminated,
    FinalResults,
]
