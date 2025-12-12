from otree.api import *
from bargaining_tdl_common import (
    save_time_value,
    check_control_questions_intro,
    set_control_questions_failed,
    has_failed_control_questions,
    get_max_attempts,
    get_control_questions_attempts,
    increment_control_questions_attempts,
    has_passed_control_questions,
    set_control_questions_passed,
    get_logger,
)

logger = get_logger('intro')

doc = """
Bargaining Game (Part 1: Individual Tasks)
Instructions -> Chat and Intentions
Data is saved to participant.vars for the next app.
"""

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Drafts (Simulated Chat)
    draft_history_left = models.LongStringField(blank=True)
    draft_history_right = models.LongStringField(blank=True)
    
    # Intentions
    signal_left = models.StringField(
        choices=[
            "I wish to split the $ 12 equally with you only, player on the left.",
            "I wish to split the $ 12 equally with the other player only, the one on the right.",
            "I wish to split the $ 12 equally with both you and player on the right"
        ],
        widget=widgets.RadioSelect,
        label="Select intention for the participant on your LEFT:"
    )
    signal_right = models.StringField(
        choices=[
            "I wish to split the $ 12 equally with you only, player on the right.",
            "I wish to split the $ 12 equally with the other player only, the one on the left.",
            "I wish to split the $ 12 equally with both you and player on the left"
        ],
        widget=widgets.RadioSelect,
        label="Select intention for the participant on your RIGHT:"
    )
    
    # Track which chat/intention was selected first
    first_intention_selected = models.StringField(
        choices=[
            ['left', 'Left'],
            ['right', 'Right']
        ],
        blank=True,
        label="Which intention was selected first"
    )
    
    # Control Questions - Example 1
    example1_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],  # Corretta
            ['4', '$4'],  # Sbagliata 1
            ['0', '$0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 1 in this case?"
    )
    example1_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 2
            ['4', '$4'],  # Sbagliata 1
            ['0', '$0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 1 in this case?"
    )
    example1_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],  # Corretta
            ['4', '$4'],  # Sbagliata 1
            ['0', '$0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 1 in this case?"
    )
    
    # Control Questions - Example 2
    example2_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 1
            ['4', '$4'],  # Corretta
            ['0', '$0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 1 in this case?"
    )
    example2_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 1
            ['4', '$4'],  # Corretta
            ['0', '$0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 1 in this case?"
    )
    example2_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 1
            ['4', '$4'],  # Corretta
            ['0', '$0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 1 in this case?"
    )
    
    # Control Questions - Example 3
    example3_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 2
            ['4', '$4'],  # Sbagliata 1
            ['0', '$0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 1 in this case?"
    )
    example3_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 2
            ['4', '$4'],  # Sbagliata 1
            ['0', '$0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 1 in this case?"
    )
    example3_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],  # Sbagliata 2
            ['4', '$4'],  # Sbagliata 1
            ['0', '$0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 1 in this case?"
    )
    
    # Control Questions - Payoff determination
    payoff_determination = models.StringField(
        choices=[
            ['I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.', 
             'I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.'],  # Corretta
            ['I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.', 
             'I will only get paid for one of the following parts: Part 1, Part 2, or Part 3.'],  # Sbagliata 1
            ['I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment.', 
             'I will be paid an amount equal to the sum of the earnings achieved in each part of the experiment.'],  # Sbagliata 2
            ["I don't know.", "I don't know."],  # Sbagliata 3
        ],
        widget=widgets.RadioSelect,
        label="Excluding the participation fee of $2, how will your total payoff be determined in this experiment?"
    )
    
    # Time tracking fields (in seconds)
    time_welcome = models.FloatField(initial=0)
    time_instructions_part1 = models.FloatField(initial=0)
    time_control_questions = models.FloatField(initial=0)
    time_goodbye = models.FloatField(initial=0)
    time_chat_and_signals = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)

# PAGES

class Welcome(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # oTree salva automaticamente i form fields prima di chiamare before_next_page
        # Quindi player.time_on_page dovrebbe già avere il valore dal form
        time_value = save_time_value(player.time_on_page)
        player.time_welcome = time_value
        logger.debug(f"Welcome page - time_on_page received: {player.time_on_page}, time_welcome saved: {player.time_welcome}")

class InstructionsPart1(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part1 = save_time_value(player.time_on_page)
        logger.debug(f"InstructionsPart1 - time_instructions_part1 saved: {player.time_instructions_part1}")

def create_control_questions_class(attempt_number):
    """
    Factory function che crea dinamicamente una classe ControlQuestions per un tentativo specifico.
    
    Args:
        attempt_number: Numero del tentativo (1-based)
    
    Returns:
        Classe Page per oTree
    """
    class_name = f'ControlQuestionsAttempt{attempt_number}'
    
    class ControlQuestionsPage(Page):
        template_name = 'bargaining_tdl_intro/ControlQuestions.html'
        form_model = 'player'
        form_fields = [
            'example1_earnings_you',
            'example1_earnings_left',
            'example1_earnings_right',
            'example2_earnings_you',
            'example2_earnings_left',
            'example2_earnings_right',
            'example3_earnings_you',
            'example3_earnings_left',
            'example3_earnings_right',
            'payoff_determination',
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
            if has_passed_control_questions(player, 'intro'):
                return False
            
            if has_failed_control_questions(player, 'intro'):
                return False
            
            current_attempts = get_control_questions_attempts(player, 'intro')
            # Mostra solo quando è il turno di questo tentativo
            return current_attempts == (attempt_number - 1)

        @staticmethod
        def vars_for_template(player):
            max_attempts = get_max_attempts(player.session)
            current_attempts = get_control_questions_attempts(player, 'intro')
            attempts_remaining = max_attempts - current_attempts
            
            return {
                'example1_scenario': "Imagine that you chose 'Share only with the player on the right', that the player on the left chose 'Share with both you and the player on the right', and that the player on the right chose 'Share only with you'.",
                'example2_scenario': "Imagine that you chose 'Share with both the player on the left and the player on the right', that the player on the left chose 'Share only with the player on the right', and that the player on the right chose 'Share with both you and the player on the left'.",
                'example3_scenario': "Imagine that you chose 'Share with both the player on the left and the player on the right', that the player on the left chose 'Share only with you', and that the player on the right chose 'Share only with the player on the left'.",
                'max_attempts': max_attempts,
                'current_attempt': attempt_number,
                'attempts_remaining': max_attempts - attempt_number,
                'is_first_attempt': attempt_number == 1,
            }

        @staticmethod
        def before_next_page(player, timeout_happened):
            """Gestisce la logica di retry per le control questions."""
            player.time_control_questions = save_time_value(player.time_on_page)
            logger.debug(f"ControlQuestions Attempt {attempt_number} - time_control_questions saved: {player.time_control_questions}")
            
            # Verifica le risposte
            is_correct = check_control_questions_intro(player)
            max_attempts = get_max_attempts(player.session)
            current_attempts = increment_control_questions_attempts(player, 'intro')
            
            if is_correct:
                # Risposte corrette: imposta passed e resetta attempts
                set_control_questions_passed(player, 'intro', passed=True)
                set_control_questions_failed(player, 'intro', failed=False)
                logger.debug(f"ControlQuestions Attempt {attempt_number} - All answers correct on attempt {current_attempts}")
            else:
                # Risposte sbagliate
                logger.debug(f"ControlQuestions Attempt {attempt_number} - Incorrect answers on attempt {current_attempts}/{max_attempts}")
                
                if current_attempts >= max_attempts:
                    # Raggiunto il massimo numero di tentativi: imposta failed
                    set_control_questions_failed(player, 'intro', failed=True)
                    logger.debug(f"ControlQuestions Attempt {attempt_number} - Max attempts reached, setting failed flag")
    
    # Imposta il nome della classe per il debug
    ControlQuestionsPage.__name__ = class_name
    ControlQuestionsPage.__qualname__ = class_name
    
    return ControlQuestionsPage


# Crea fino a 5 istanze di ControlQuestions (supporta fino a 5 tentativi)
# Ogni istanza gestirà un tentativo specifico
ControlQuestionsAttempt1 = create_control_questions_class(1)
ControlQuestionsAttempt2 = create_control_questions_class(2)
ControlQuestionsAttempt3 = create_control_questions_class(3)
ControlQuestionsAttempt4 = create_control_questions_class(4)
ControlQuestionsAttempt5 = create_control_questions_class(5)

class Goodbye(Page):
    """Pagina di saluto che termina l'esperimento per il partecipante."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
        return has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_goodbye = save_time_value(player.time_on_page)
        logger.debug(f"Goodbye - time_goodbye saved: {player.time_goodbye}")
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class ChatAndSignals(Page):
    form_model = 'player'
    form_fields = ['signal_left', 'signal_right', 'draft_history_left', 'draft_history_right', 'first_intention_selected', 'time_on_page']

    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se tutte le risposte alle control questions erano corrette."""
        return has_passed_control_questions(player, 'intro')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.time_chat_and_signals = save_time_value(player.time_on_page)
        logger.debug(f"ChatAndSignals - time_chat_and_signals saved: {player.time_chat_and_signals}")
        # Save data to participant vars for the next app
        player.participant.vars['draft_history_left'] = player.draft_history_left
        player.participant.vars['draft_history_right'] = player.draft_history_right
        player.participant.vars['signal_left'] = player.signal_left
        player.participant.vars['signal_right'] = player.signal_right
        # TEMPORANEO: Imposta failed_control_questions = False per permettere il test senza control questions
        set_control_questions_failed(player, 'intro', failed=False)

page_sequence = [
    Welcome,
    InstructionsPart1,
    ControlQuestionsAttempt1,
    ControlQuestionsAttempt2,
    ControlQuestionsAttempt3,
    ControlQuestionsAttempt4,
    ControlQuestionsAttempt5,
    Goodbye,
    ChatAndSignals
]
