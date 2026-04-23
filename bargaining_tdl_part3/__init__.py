from otree.api import (  # type: ignore
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as cu,
    Page,
    WaitPage,
)
from bargaining_tdl_common import (  # type: ignore
    save_time_value,
    check_control_questions_part3,
    set_control_questions_failed,
    has_failed_control_questions,
    get_max_attempts,
    get_control_questions_attempts,
    increment_control_questions_attempts,
    has_passed_control_questions,
    set_control_questions_passed,
    get_logger,
    get_partner_colors,
)

logger = get_logger('part3')

doc = """
Bargaining Game (Part 3: Three-Person Dictator Game)
Individual task - each participant makes a decision independently.
The experimenter will create groups with new triads a posteriori.
"""


def get_part2_payoff_data(player):
    """
    Restituisce dati payoff Part 2 se disponibili.
    Se app Part 2 non è in sessione, ritorna payoff zero.
    """
    def _normalize_part2_payoff_data(data):
        defaults = {
            'payoff': cu(0),
            'selected_question': None,
            'switching_point': None,
            'pr1': None,
            'pr2': None,
            'option_selected': None,
            'event_occurred': None,
            'payoff_amount': 0,
            'question_text': '',
            'reminder_text': '',
            'target_code': '',
            'event_codes': [],
            'question_type': '',
            'error': None,
        }
        normalized = dict(defaults)
        if isinstance(data, dict):
            normalized.update(data)
        return normalized

    if 'part2_payoff_data' in player.participant.vars:
        normalized = _normalize_part2_payoff_data(player.participant.vars['part2_payoff_data'])
        player.participant.vars['part2_payoff_data'] = normalized
        player.participant.vars['part2_payoff'] = normalized.get('payoff', cu(0))
        return normalized

    try:
        from bargaining_tdl_part2 import calculate_part2_payoff, get_part2_player  # type: ignore
    except Exception:
        part2_payoff_data = _normalize_part2_payoff_data({'error': 'Part 2 app not available'})
        player.participant.vars['part2_payoff_data'] = part2_payoff_data
        player.participant.vars['part2_payoff'] = cu(0)
        return part2_payoff_data

    part2_payoff_data = _normalize_part2_payoff_data(calculate_part2_payoff(player))
    player.participant.vars['part2_payoff_data'] = part2_payoff_data
    player.participant.vars['part2_payoff'] = part2_payoff_data.get('payoff', cu(0))

    # Se player Part2 esiste, sincronizza payoff per export
    part2_player = get_part2_player(player)
    if part2_player is not None:
        part2_player.payoff = player.participant.vars['part2_payoff']

    return part2_payoff_data

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_part3'
    PLAYERS_PER_GROUP = None  # Individual task
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Decision — internal values share_left/share_right/share_both; display labels in template
    decision = models.StringField(
        choices=[
            ['share_left', 'share_left'],
            ['share_right', 'share_right'],
            ['share_both', 'share_both'],
        ],
        widget=widgets.RadioSelect,
        label="How would you like to divide $12?"
    )
    
    # Control Questions - Example 1 (scenario uses fixed color names from vars_for_template)
    example1_earnings_you = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the SENDER ?"
    )
    example1_earnings_left = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the first of the two RECEIVERS ?"
    )
    example1_earnings_right = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the second of the two RECEIVERS ?"
    )
    
    # Control Questions - Example 2
    example2_earnings_you = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the SENDER ?"
    )
    example2_earnings_left = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the first of the two RECEIVERS ?"
    )
    example2_earnings_right = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would be the earnings for the second of the two RECEIVERS ?"
    )
    

    
    # Flag validazione
    all_control_questions_correct = models.BooleanField(initial=False)
    
    # Time tracking fields (in seconds)
    time_instructions_part3 = models.FloatField(initial=0)
    time_summary_part3 = models.FloatField(initial=0)
    time_control_questions_part3 = models.FloatField(initial=0)
    time_thank_you_part3 = models.FloatField(initial=0)
    time_decision_part3 = models.FloatField(initial=0)
    time_results_part3 = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)
    
    # Selezione casuale Part 1 vs Part 3 per il pagamento finale
    # 1 = viene pagato per Part 1, 0 = viene pagato per Part 3 (calcolato a posteriori dal ricercatore)
    selected_part_for_payment = models.IntegerField(
        initial=-1,
        doc="Estrazione casuale: 1=Part1 paga, 0=Part3 paga (gruppi Part3 formati a posteriori dal ricercatore)"
    )

# HELPER FUNCTIONS
# Le funzioni di validazione sono ora importate da bargaining_tdl_common

# PAGES

def _part3_color_context(player):
    """Build color context for Part 3 pages, falling back to generic names."""
    colors = get_partner_colors(player)
    return colors


def _decision_display_text(decision_code, colors):
    """
    Convert internal decision code (share_left/right/both) to participant-facing text.
    """
    if decision_code == 'share_left':
        return f"Share only with the {colors['left_partner_color']} player"
    if decision_code == 'share_right':
        return f"Share only with the {colors['right_partner_color']} player"
    if decision_code == 'share_both':
        return (
            f"Share with both the {colors['left_partner_color']} player "
            f"and the {colors['right_partner_color']} player"
        )
    return ""


class InstructionsPart3(Page):
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def vars_for_template(player):
        return _part3_color_context(player)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part3 = save_time_value(player.time_on_page)

class SummaryPart3(Page):
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def vars_for_template(player):
        return _part3_color_context(player)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_summary_part3 = save_time_value(player.time_on_page)

def create_control_questions_part3_class(attempt_number):
    """
    Factory function che crea dinamicamente una classe ControlQuestionsPart3 per un tentativo specifico.
    
    Args:
        attempt_number: Numero del tentativo (1-based)
    
    Returns:
        Classe Page per oTree
    """
    class_name = f'ControlQuestionsPart3Attempt{attempt_number}'
    
    class ControlQuestionsPart3Page(Page):
        template_name = 'bargaining_tdl_part3/ControlQuestionsPart3.html'
        form_model = 'player'
        preserve_unsubmitted_inputs = True
        form_fields = [
            'example1_earnings_you',
            'example1_earnings_left',
            'example1_earnings_right',
            'example2_earnings_you',
            'example2_earnings_left',
            'example2_earnings_right',
            'time_on_page'
        ]
        
        @staticmethod
        def is_displayed(player):
            """
            Mostra questa pagina solo se:
            - Non ha ancora passato le control questions E
            - Non ha ancora fallito definitivamente E
            - È il tentativo corretto (current_attempts == attempt_number - 1)
            """
            if has_passed_control_questions(player, 'part3'):
                return False
            
            if has_failed_control_questions(player, 'part3'):
                return False
            
            current_attempts = get_control_questions_attempts(player, 'part3')
            # Mostra solo quando è il turno di questo tentativo
            return current_attempts == (attempt_number - 1)

        @staticmethod
        def vars_for_template(player):
            max_attempts = get_max_attempts(player.session)
            colors = _part3_color_context(player)
            
            return {
                'max_attempts': max_attempts,
                'current_attempt': attempt_number,
                'attempts_remaining': max_attempts - attempt_number,
                'is_first_attempt': attempt_number == 1,
                **colors,
            }
        
        @staticmethod
        def before_next_page(player, timeout_happened):
            """Gestisce la logica di retry per le control questions."""
            player.time_control_questions_part3 = save_time_value(player.time_on_page)
            logger.debug(f"ControlQuestionsPart3 Attempt {attempt_number} - time_control_questions_part3 saved: {player.time_control_questions_part3}")
            
            # Verifica le risposte
            is_correct = check_control_questions_part3(player)
            max_attempts = get_max_attempts(player.session)
            current_attempts = increment_control_questions_attempts(player, 'part3')
            
            # Manteniamo la compatibilità con il campo esistente
            player.all_control_questions_correct = is_correct
            
            if is_correct:
                # Risposte corrette: imposta passed e resetta attempts
                set_control_questions_passed(player, 'part3', passed=True)
                set_control_questions_failed(player, 'part3', failed=False)
                logger.debug(f"ControlQuestionsPart3 Attempt {attempt_number} - All answers correct on attempt {current_attempts}")
            else:
                # Risposte sbagliate
                logger.debug(f"ControlQuestionsPart3 Attempt {attempt_number} - Incorrect answers on attempt {current_attempts}/{max_attempts}")
                
                if current_attempts >= max_attempts:
                    # Raggiunto il massimo numero di tentativi: imposta failed
                    set_control_questions_failed(player, 'part3', failed=True)
                    logger.debug(f"ControlQuestionsPart3 Attempt {attempt_number} - Max attempts reached, setting failed flag")
    
    # Imposta il nome della classe per il debug
    ControlQuestionsPart3Page.__name__ = class_name
    ControlQuestionsPart3Page.__qualname__ = class_name
    
    return ControlQuestionsPart3Page


# Crea fino a 5 istanze di ControlQuestionsPart3 (supporta fino a 5 tentativi)
ControlQuestionsPart3Attempt1 = create_control_questions_part3_class(1)
ControlQuestionsPart3Attempt2 = create_control_questions_part3_class(2)
ControlQuestionsPart3Attempt3 = create_control_questions_part3_class(3)
ControlQuestionsPart3Attempt4 = create_control_questions_part3_class(4)
ControlQuestionsPart3Attempt5 = create_control_questions_part3_class(5)

class ThankYouPart3(Page):
    """Pagina mostrata se il partecipante ha fallito le control questions."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se il partecipante ha fallito le control questions."""
        return has_failed_control_questions(player, 'part3')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_thank_you_part3 = save_time_value(player.time_on_page)
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class DecisionPart3(Page):
    form_model = 'player'
    form_fields = ['decision', 'time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le control questions sono corrette."""
        return has_passed_control_questions(player, 'part3')

    @staticmethod
    def vars_for_template(player):
        return _part3_color_context(player)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_decision_part3 = save_time_value(player.time_on_page)

class ResultsPart3(Page):
    """Payoff Page - mostra i payoff dell'esperimento."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le control questions sono corrette e la decisione è stata presa."""
        return player.all_control_questions_correct and player.decision is not None
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_results_part3 = save_time_value(player.time_on_page)
        get_part2_payoff_data(player)
        
        # ==============================================================
        # SELEZIONE CASUALE 50/50: Part 1 vs Part 3
        # 1 = viene pagato per Part 1 (payoff già calcolato)
        # 0 = viene pagato per Part 3 (gruppi formati a posteriori dal ricercatore)
        # ==============================================================
        import random
        selected = random.randint(0, 1)
        player.selected_part_for_payment = selected
        player.participant.vars['selected_part_for_payment'] = selected
        
        if selected == 1:
            # Paga Part 1: il payoff di Part 1 rimane intatto in participant.vars
            # oTree accumula: participant.payoff = Part1.payoff + Part2.payoff + Part3.payoff(=0)
            player.payoff = cu(0)
            logger.info(f"Player {player.participant.code}: selected Part 1 for payment")
        else:
            # Paga Part 3: azzera il payoff di Part 1 (gruppi Part3 formati a posteriori)
            # Il ricercatore calcolerà il payoff Part3 offline dai dati esportati
            try:
                from bargaining_tdl_main import Player as MainPlayer  # type: ignore
                for app_player in player.participant.get_players():
                    if isinstance(app_player, MainPlayer):
                        app_player.payoff = cu(0)
                        break
            except Exception as e:
                logger.warning(f"Could not zero out Part1 payoff: {e}")
            player.participant.vars['part1_payoff'] = cu(0)
            player.payoff = cu(0)
            logger.info(f"Player {player.participant.code}: selected Part 3 for payment (payoff TBD by researcher)")
    
    @staticmethod
    def vars_for_template(player):
        """Recupera i payoff per la visualizzazione e calcola il payoff di Part 2 se necessario."""
        part1_payoff = cu(0)
        if 'part1_payoff' in player.participant.vars:
            part1_payoff = player.participant.vars['part1_payoff']

        part2_payoff_data = get_part2_payoff_data(player)
        part2_payoff = player.participant.vars.get('part2_payoff', cu(0))

        colors = _part3_color_context(player)
        decision_display = _decision_display_text(player.decision, colors)

        return dict(
            part1_payoff=part1_payoff,
            part2_payoff=part2_payoff,
            part2_payoff_data=part2_payoff_data,
            decision_display=decision_display,
            **colors,
        )

page_sequence = [
    InstructionsPart3,
    SummaryPart3,
    ControlQuestionsPart3Attempt1,
    ControlQuestionsPart3Attempt2,
    ControlQuestionsPart3Attempt3,
    ControlQuestionsPart3Attempt4,
    ControlQuestionsPart3Attempt5,
    ThankYouPart3,  # Solo se control questions sbagliate
    DecisionPart3,  # Solo se control questions corrette
    ResultsPart3,  # Solo se control questions corrette - mostra payoff
]
