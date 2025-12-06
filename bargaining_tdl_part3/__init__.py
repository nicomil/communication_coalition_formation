from otree.api import *
from bargaining_tdl_common import (
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
)

logger = get_logger('part3')

doc = """
Bargaining Game (Part 3: Three-Person Dictator Game)
Individual task - each participant makes a decision independently.
The experimenter will create groups with new triads a posteriori.
"""

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_part3'
    PLAYERS_PER_GROUP = None  # Individual task
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Decision
    decision = models.StringField(
        choices=[
            ['share_left', 'Share only with the player on the left'],
            ['share_right', 'Share only with the player on the right'],
            ['share_both', 'Share with both the player on the left and the player on the right']
        ],
        widget=widgets.RadioSelect,
        label="How would you like to divide $12?"
    )
    
    # Control Questions - Example 1
    example1_earnings_you = models.StringField(
        choices=[
            ['4', '$4'],
            ['6', '$6'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would your earning be for Part 3 in this case?"
    )
    example1_earnings_left = models.StringField(
        choices=[
            ['4', '$4'],
            ['6', '$6'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 3 in this case?"
    )
    example1_earnings_right = models.StringField(
        choices=[
            ['4', '$4'],
            ['6', '$6'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 3 in this case?"
    )
    
    # Control Questions - Example 2
    example2_earnings_you = models.StringField(
        choices=[
            ['0', '$0'],
            ['4', '$4'],
            ['6', '$6'],
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 3 in this case?"
    )
    example2_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 3 in this case?"
    )
    example2_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['4', '$4'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 3 in this case?"
    )
    
    # Control Questions - Payoff determination
    payoff_question = models.StringField(
        choices=[
            ['I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.', 
             'I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.'],
            ['I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.', 
             'I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.'],
            ['I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment.', 
             'I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment.'],
            ["I don't know.", "I don't know."],
        ],
        widget=widgets.RadioSelect,
        label="Excluding the participation fee of $2, how will your total payoff be determined in this experiment?"
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

# HELPER FUNCTIONS
# Le funzioni di validazione sono ora importate da bargaining_tdl_common

# PAGES

class InstructionsPart3(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part3 = save_time_value(player.time_on_page)

class SummaryPart3(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
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
        form_fields = [
            'example1_earnings_you',
            'example1_earnings_left',
            'example1_earnings_right',
            'example2_earnings_you',
            'example2_earnings_left',
            'example2_earnings_right',
            'payoff_question',
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
            
            return {
                'max_attempts': max_attempts,
                'current_attempt': attempt_number,
                'attempts_remaining': max_attempts - attempt_number,
                'is_first_attempt': attempt_number == 1,
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
    
    @staticmethod
    def vars_for_template(player):
        """Recupera i payoff per la visualizzazione e calcola il payoff di Part 2 se necessario."""
        from bargaining_tdl_part2 import calculate_part2_payoff
        
        # Prova a recuperare il payoff dalla Part 1 (bargaining_tdl_main)
        part1_payoff = cu(0)
        if 'part1_payoff' in player.participant.vars:
            part1_payoff = player.participant.vars['part1_payoff']
        
        # Calcola o recupera payoff Part 2
        # Se non è già stato calcolato, calcolalo ora
        if 'part2_payoff_data' not in player.participant.vars:
            # Calcola payoff Part 2 (la funzione gestisce automaticamente il recupero del player di Part 2)
            part2_payoff_data = calculate_part2_payoff(player)
            
            # Salva in participant.vars per uso futuro
            player.participant.vars['part2_payoff_data'] = part2_payoff_data
            player.participant.vars['part2_payoff'] = part2_payoff_data['payoff']
        else:
            # Recupera i dati già calcolati
            part2_payoff_data = player.participant.vars['part2_payoff_data']
        
        part2_payoff = player.participant.vars.get('part2_payoff', cu(0))
        
        return dict(
            part1_payoff=part1_payoff,
            part2_payoff=part2_payoff,
            part2_payoff_data=part2_payoff_data,
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Assicura che il payoff di Part 2 sia stato calcolato e salvato."""
        # Il calcolo viene fatto in vars_for_template, ma assicuriamoci che sia salvato
        # (già fatto in vars_for_template, ma questo metodo può essere usato per validazione)
        pass

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
