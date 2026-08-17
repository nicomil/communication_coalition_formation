from otree.api import (  # type: ignore
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Page,
    WaitPage,
)

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
    pass


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





def _is_inactive_excluded(player):
    return bool(player.participant.vars.get('inactive_excluded', False))

def _is_group_dropped_inactive(player):
    return bool(player.participant.vars.get('group_dropped_inactive', False))

def _is_timeout_excluded(player):
    return bool(player.participant.vars.get('timeout_excluded', False))


def _is_excluded(player):
    """Il survey spetta solo a chi ha scelto deliberatamente su Signals,
    Decision e PostDecisionConfidence.

    Chi finisce in uno di questi tre stati ha avuto almeno una scelta assegnata
    d'ufficio, quindi vede solo SurveyTerminated:
      - inactive_excluded: timeout sulle control questions dell'intro
      - group_dropped_inactive: gruppo caduto per disconnessione
      - timeout_excluded: timeout su Signals, Decision o PostDecisionConfidence
    """
    return (
        _is_inactive_excluded(player)
        or _is_group_dropped_inactive(player)
        or _is_timeout_excluded(player)
    )


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

    # Birth year: YYYY (Q2)
    birth_year = models.IntegerField(
        min=1924,
        max=2008,
        label="In what year were you born?",
    )

    # Field of study: ISCED 2013 categories (Q3)
    field_of_study = models.IntegerField(
        choices=[
            [1, 'Education'],
            [2, 'Arts and humanities'],
            [3, 'Social sciences (i.e. economics, sociology, political science)'],
            [11, 'Journalism and information'],
            [4, 'Business, administration and law'],
            [5, 'Natural sciences, mathematics and statistics'],
            [6, 'Information and Communication Technologies (ICTs)'],
            [7, 'Engineering, manufacturing and construction'],
            [8, 'Agriculture, forestry, fisheries and veterinary'],
            [9, 'Health and welfare'],
            [10, 'Services'],
        ],
        widget=widgets.RadioSelect,
        label="What is or was the main field of study of your highest educational qualification?",
    )

    # University years: 0–20 full-time equivalents (Q4)
    university_years = models.IntegerField(
        min=0,
        max=20,
        label="About how many years of university (or tertiary) education have you completed in total (full-time equivalents)?",
    )

    # Q5: Main situation (Select one)
    main_situation = models.StringField(
        choices=[
            ['paid_work', 'In paid work (employee, employer, self-employed)'],
            ['education', 'In education / Student'],
            ['unemployed', 'Unemployed'],
            ['sick_disabled', 'Permanently sick or disabled'],
            ['retired', 'Retired'],
            ['housework', 'Doing housework, looking after children or other persons'],
        ],
        widget=widgets.RadioSelect,
        label="Which of these descriptions best describes your main situation? (Select one)",
    )

    # Q6: Job type (always shown; 'not_employed' for those not in paid work)
    job_type = models.StringField(
        choices=[
            ['employee', 'An employee'],
            ['self_employed', 'Self-employed (without employees)'],
            ['employer', 'An employer (self-employed with employees)'],
            ['not_employed', 'Not employed'],
        ],
        widget=widgets.RadioSelect,
        label="In your main job, are you...",
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
    time_survey_questions = models.FloatField(initial=0)
    time_survey_sd3_mach = models.FloatField(initial=0)
    time_survey_sd3_narc = models.FloatField(initial=0)
    time_survey_sd3_psych = models.FloatField(initial=0)
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

class SurveyQuestions(_SurveyTimedPage):
    """Demographic questions page."""
    form_model = 'player'
    form_fields = [
        'gender',
        'birth_year',
        'field_of_study',
        'university_years',
        'main_situation',
        'job_type',
        'time_on_page',
    ]

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_questions = player.time_on_page or 0


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


class SurveyPage1(_SurveyTimedPage):
    template_name = 'bargaining_tdl_survey/SurveyMatrix.html'
    form_model = 'player'
    form_fields = [
        *(field_name for field_name, _ in SD3_MACHIAVELLIANISM_ITEMS),
        'time_on_page',
    ]

    @staticmethod
    def vars_for_template(player):
        return {
            **_matrix_context(player, SD3_MACHIAVELLIANISM_ITEMS),
            'page_title': "Survey Page 3 of 5"
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_sd3_mach = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)


class SurveyPage2(_SurveyTimedPage):
    template_name = 'bargaining_tdl_survey/SurveyMatrix.html'
    form_model = 'player'
    form_fields = [
        *(field_name for field_name, _ in SD3_NARCISSISM_ITEMS),
        'time_on_page',
    ]

    @staticmethod
    def vars_for_template(player):
        return {
            **_matrix_context(player, SD3_NARCISSISM_ITEMS),
            'page_title': "Survey Page 4 of 5"
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_sd3_narc = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)


class SurveyPage3(_SurveyTimedPage):
    template_name = 'bargaining_tdl_survey/SurveyMatrix.html'
    form_model = 'player'
    form_fields = [
        *(field_name for field_name, _ in SD3_PSYCHOPATHY_ITEMS),
        'time_on_page',
    ]

    @staticmethod
    def vars_for_template(player):
        return {
            **_matrix_context(player, SD3_PSYCHOPATHY_ITEMS),
            'page_title': "Survey Page 5 of 5"
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_sd3_psych = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)


class SurveyPage4(_SurveyTimedPage):
    """Combined Survey Page (4-9)"""
    form_model = 'player'
    form_fields = [
        'willingness_future',
        'willingness_risk',
        'reciprocity_positive',
        'reciprocity_negative',
        'willingness_donate',
        'trust_general',
        'time_on_page'
    ]

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(11))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page4 = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)





class SurveyPage10(_SurveyTimedPage):
    """11-20 game — guess a number between 110 and 200."""
    form_model = 'player'
    form_fields = ['beauty_contest_guess', 'time_on_page']

    @staticmethod
    def beauty_contest_guess_error_message(player, value):
        if value is not None:
            val_in_cents = round(value * 100)
            if val_in_cents % 10 != 0:
                return 'Please enter a number in steps of $ 0.10 (e.g., 1.10, 1.20, 1.30... 2.00).'

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_page10 = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)


class SurveyFeedback(_SurveyTimedPage):
    """Feedback page shown after survey page 10 and before final results."""
    form_model = 'player'
    form_fields = ['instructions_clarity', 'general_comment', 'time_on_page']

    @staticmethod
    def vars_for_template(player):
        return {'scale_values': list(range(1, 6))}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_survey_feedback = player.time_on_page or 0

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)


class SurveyTerminated(Page):
    template_name = 'bargaining_tdl_survey/SurveyTerminated.html'
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        return _is_excluded(player)

    @staticmethod
    def vars_for_template(player):
        is_cq_dropout = player.participant.vars.get('inactive_excluded_reason') == 'intro'
        return dict(is_cq_dropout=is_cq_dropout)

    @staticmethod
    def js_vars(player):
        is_cq_dropout = player.participant.vars.get('inactive_excluded_reason') == 'intro'
        link = player.session.config.get('dropoutlink_cq', '').strip() if is_cq_dropout else player.session.config.get('dropoutlink_inactive', '').strip()
        return dict(
            dropoutlink=link,
        )

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return []


class WaitForPart1Results(Page):
    """Attesa breve prima di FinalResults, mostrata solo se il gruppo non è
    ancora chiudibile.

    Caso tipico: un compagno ha chiuso il browser e non ha deciso. Il suo
    timer di pagina non scatta (vive nel client), quindi senza questa pagina
    chi ha finito arriverebbe su FinalResults con la decisione del compagno
    ancora NULL — che è l'origine dell'Application error 500.

    La pagina si auto-ricarica: appena il compagno decide, oppure appena
    scatta la finalizzazione d'ufficio, is_displayed diventa False e oTree
    manda avanti da solo. Chi trova il gruppo già pronto non la vede mai.
    """
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        if _is_excluded(player):
            return False
        from bargaining_tdl_common import get_main_group_player # type: ignore
        main_player = get_main_group_player(player)
        if not main_player:
            return False
        # Il tentativo di calcolo è idempotente: si ferma da solo se i payoff
        # del gruppo sono già stati scritti.
        return not _calculate_payoffs_if_needed(main_player.group)

    @staticmethod
    def get_timeout_seconds(player):
        """Rete di sicurezza per chi ha il JavaScript bloccato: allo scadere
        si finalizza comunque. Dura quanto manca al compagno più lento per
        essere considerato assente."""
        from bargaining_tdl_common import get_main_group_player # type: ignore
        from bargaining_tdl_main import seconds_until_absent # type: ignore
        main_player = get_main_group_player(player)
        if not main_player:
            return 5
        pending = [
            seconds_until_absent(p)
            for p in main_player.group.get_players()
            if not p.field_maybe_none('decision_choice')
        ]
        return max(5, min(pending) + 5) if pending else 5

    @staticmethod
    def vars_for_template(player):
        from bargaining_tdl_common import get_main_group_player # type: ignore
        from bargaining_tdl_main import seconds_until_absent # type: ignore
        main_player = get_main_group_player(player)
        wait_seconds = 0
        if main_player:
            pending = [
                seconds_until_absent(p)
                for p in main_player.group.get_players()
                if not p.field_maybe_none('decision_choice')
            ]
            wait_seconds = min(pending) if pending else 0
        return dict(wait_seconds=wait_seconds)

    @staticmethod
    def before_next_page(player, timeout_happened):
        if not timeout_happened:
            return
        # Timeout raggiunto: si chiude comunque, senza aspettare oltre.
        from bargaining_tdl_common import get_main_group_player # type: ignore
        main_player = get_main_group_player(player)
        if main_player:
            _calculate_payoffs_if_needed(main_player.group, force=True)


class FinalResults(Page):
    """Final screen of the experiment summarizing payoffs."""
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)

    @staticmethod
    def vars_for_template(player):
        from otree.api import Currency as cu
        from bargaining_tdl_common import get_main_group_player, TOPOLOGY, COLOR_MAPPING
        
        main_player = get_main_group_player(player)

        if main_player:
            # force=True: siamo all'ultima pagina, oltre non si aspetta più.
            _calculate_payoffs_if_needed(main_player.group, force=True)
        
        part1_group_id = player.participant.vars.get('part1_group_id')
        part1_payoff_eligible = bool(player.participant.vars.get('part1_payoff_eligible', True))
            
        base_fee = cu(player.session.config.get('participation_fee', 1.50))
        beauty_contest_bonus = cu(player.beauty_contest_guess or 0)
        part1_payoff_val = player.participant.vars.get('part1_payoff', cu(0))
        if not part1_payoff_eligible:
            part1_payoff_val = cu(0)
        subtotal = base_fee + part1_payoff_val + beauty_contest_bonus
        
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
                return f"I will support {COLOR_MAPPING[actor_left_id]}"
            if choice == 'Right':
                return f"I will support {COLOR_MAPPING[actor_right_id]}"
            return "I will support no one"
        
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

            # field_maybe_none: se un partner non ha mai deciso il campo è NULL
            # e la lettura diretta solleverebbe TypeError, mandando in 500 la
            # pagina finale di chi invece ha completato.
            my_choice_display = format_choice(
                main_player.field_maybe_none('decision_choice'), my_id
            )
            left_choice_display = format_choice(
                left_partner.field_maybe_none('decision_choice'), left_id
            )
            right_choice_display = format_choice(
                right_partner.field_maybe_none('decision_choice'), right_id
            )

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
            'beauty_contest_can_win_bonus': (player.beauty_contest_guess or 0) < 2.0,
        }

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.session.config.get('completionlink', '').strip(),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_final_results = player.time_on_page or 0




def _calculate_payoffs_if_needed(main_group, force=False):
    """Calcola i payoff di Part 1 se il gruppo è pronto.

    Ritorna True se i payoff sono disponibili, False se manca ancora la
    decisione di qualcuno che potrebbe tornare.
    """
    p1 = main_group.get_player_by_id(1)

    # Calcola i payoff solo una volta per il gruppo
    if 'part1_payoff' in p1.participant.vars:
        return True

    from bargaining_tdl_common import treatment_flag, custom_calculate_payoff_vector, VALID_DECISIONS # type: ignore
    from bargaining_tdl_main import finalize_absent_players # type: ignore
    from otree.api import Currency as cu # type: ignore
    import logging
    logger = logging.getLogger(__name__)

    p1 = main_group.get_player_by_id(1)
    p2 = main_group.get_player_by_id(2)
    p3 = main_group.get_player_by_id(3)
    players = [p1, p2, p3]

    # Chi è sparito senza decidere riceve ora una scelta casuale, così gli
    # altri due non restano appesi. Con force=True non si aspetta oltre.
    if not finalize_absent_players(main_group, force=force):
        logger.info(
            f"Gruppo {main_group.id}: decisione mancante, payoff rimandati."
        )
        return False

    c1 = p1.field_maybe_none('decision_choice')
    c2 = p2.field_maybe_none('decision_choice')
    c3 = p3.field_maybe_none('decision_choice')

    if any(c not in VALID_DECISIONS for c in [c1, c2, c3]):
        logger.debug(f"Skipping group {main_group.id} (invalid decisions).")
        return False

    payoff_values, outcome = custom_calculate_payoff_vector(
        (c1, c2, c3),
        no_deadweight_loss=bool(treatment_flag(p1, 'no_deadweight_loss', False)),
    )

    for p, payoff_value in zip(players, payoff_values):
        p.payoff = cu(payoff_value)

    main_group.group_outcome = outcome
    main_group.grp_coordinate = int(any(value > 0 for value in payoff_values))
    
    for p in players:
        p.part1_calculated_payoff = p.payoff
        if not getattr(p, 'part1_payoff_eligible', True):
            p.payoff = cu(0)

        p.participant.vars['part1_payoff'] = p.payoff
        p.participant.vars['part1_group_id'] = main_group.id
        p.participant.vars['group_outcome'] = outcome

    return True




class SurveyIntro(Page):
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        return not _is_excluded(player)


page_sequence = [
    SurveyPage10,
    SurveyIntro,
    SurveyQuestions,
    SurveyPage4,
    SurveyPage1,
    SurveyPage2,
    SurveyPage3,
    SurveyFeedback,
    SurveyTerminated,
    WaitForPart1Results,
    FinalResults,
]
