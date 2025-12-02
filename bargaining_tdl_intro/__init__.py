from otree.api import *

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
            "I wish to split the $ 12 equally with you only.",
            "I wish to split the $ 12 equally with the other player only.",
            "I wish to split the $ 12 equally with both the two players."
        ],
        widget=widgets.RadioSelect,
        label="Select intention for the participant on your LEFT:"
    )
    signal_right = models.StringField(
        choices=[
            "I wish to split the $ 12 equally with you only.",
            "I wish to split the $ 12 equally with the other player only.",
            "I wish to split the $ 12 equally with both the two players."
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
            ['6', '£6'],  # Corretta
            ['4', '£4'],  # Sbagliata 1
            ['0', '£0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 1 in this case?"
    )
    example1_earnings_left = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 2
            ['4', '£4'],  # Sbagliata 1
            ['0', '£0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 1 in this case?"
    )
    example1_earnings_right = models.StringField(
        choices=[
            ['6', '£6'],  # Corretta
            ['4', '£4'],  # Sbagliata 1
            ['0', '£0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 1 in this case?"
    )
    
    # Control Questions - Example 2
    example2_earnings_you = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 1
            ['4', '£4'],  # Corretta
            ['0', '£0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 1 in this case?"
    )
    example2_earnings_left = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 1
            ['4', '£4'],  # Corretta
            ['0', '£0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 1 in this case?"
    )
    example2_earnings_right = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 1
            ['4', '£4'],  # Corretta
            ['0', '£0'],  # Sbagliata 2
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the right be for Part 1 in this case?"
    )
    
    # Control Questions - Example 3
    example3_earnings_you = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 2
            ['4', '£4'],  # Sbagliata 1
            ['0', '£0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would your earnings be for Part 1 in this case?"
    )
    example3_earnings_left = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 2
            ['4', '£4'],  # Sbagliata 1
            ['0', '£0'],  # Corretta
        ],
        widget=widgets.RadioSelect,
        label="What would the earnings for the player on the left be for Part 1 in this case?"
    )
    example3_earnings_right = models.StringField(
        choices=[
            ['6', '£6'],  # Sbagliata 2
            ['4', '£4'],  # Sbagliata 1
            ['0', '£0'],  # Corretta
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
        label="Excluding the participation fee of £2, how will your total payoff be determined in this experiment?"
    )
    
    # Time tracking fields (in seconds)
    time_welcome = models.FloatField(initial=0)
    time_instructions_part1 = models.FloatField(initial=0)
    time_control_questions = models.FloatField(initial=0)
    time_goodbye = models.FloatField(initial=0)
    time_chat_and_signals = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)

# HELPER FUNCTIONS

def save_time_value(time_value, default=0.0):
    """Helper function to safely convert time_on_page value to float."""
    if time_value is None or time_value == '':
        return default
    try:
        return float(time_value)
    except (ValueError, TypeError):
        return default

def check_all_answers_correct(player):
    """Verifica se tutte le risposte alle control questions sono corrette."""
    # Verifica che tutti i campi siano stati compilati
    if (not player.example1_earnings_you or 
        not player.example1_earnings_left or 
        not player.example1_earnings_right or
        not player.example2_earnings_you or 
        not player.example2_earnings_left or 
        not player.example2_earnings_right or
        not player.example3_earnings_you or 
        not player.example3_earnings_left or 
        not player.example3_earnings_right or
        not player.payoff_determination):
        return False
    
    correct = (
        player.example1_earnings_you == "6" and
        player.example1_earnings_left == "0" and
        player.example1_earnings_right == "6" and
        player.example2_earnings_you == "4" and
        player.example2_earnings_left == "4" and
        player.example2_earnings_right == "4" and
        player.example3_earnings_you == "0" and
        player.example3_earnings_left == "0" and
        player.example3_earnings_right == "0" and
        player.payoff_determination == "I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3."
    )
    return correct

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
        print(f"Welcome page - time_on_page received: {player.time_on_page}, time_welcome saved: {player.time_welcome}")

class InstructionsPart1(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part1 = save_time_value(player.time_on_page)
        print(f"InstructionsPart1 - time_instructions_part1 saved: {player.time_instructions_part1}")

class ControlQuestions(Page):
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
    def vars_for_template(player):
        return {
            'example1_scenario': "Imagine that you chose 'Share only with the player on the right', that the player on the left chose 'Share with both you and the player on the right', and that the player on the right chose 'Share only with you'.",
            'example2_scenario': "Imagine that you chose 'Share with both the player on the left and the player on the right', that the player on the left chose 'Share only with the player on the right', and that the player on the right chose 'Share with both you and the player on the left'.",
            'example3_scenario': "Imagine that you chose 'Share with both the player on the left and the player on the right', that the player on the left chose 'Share only with you', and that the player on the right chose 'Share only with the player on the left'.",
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        """Salva un flag se le risposte sono sbagliate."""
        player.time_control_questions = save_time_value(player.time_on_page)
        print(f"ControlQuestions - time_control_questions saved: {player.time_control_questions}")
        # Verifica le risposte e salva il flag
        is_correct = check_all_answers_correct(player)
        player.participant.vars['failed_control_questions'] = not is_correct

class Goodbye(Page):
    """Pagina di saluto che termina l'esperimento per il partecipante."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
        # Usa il flag salvato in before_next_page invece di chiamare check_all_answers_correct
        # perché is_displayed viene chiamato prima che i dati siano salvati
        failed = player.participant.vars.get('failed_control_questions')
        # Se il flag non è stato ancora impostato, non mostrare Goodbye
        # (significa che siamo ancora prima di ControlQuestions o che le risposte sono corrette)
        if failed is None:
            return False
        return failed
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_goodbye = save_time_value(player.time_on_page)
        print(f"Goodbye - time_goodbye saved: {player.time_goodbye}")
    
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
        # Usa il flag salvato in before_next_page invece di chiamare check_all_answers_correct
        # perché is_displayed viene chiamato prima che i dati siano salvati
        failed = player.participant.vars.get('failed_control_questions')
        # Se il flag non è stato ancora impostato, mostra la pagina (per retrocompatibilità)
        # Altrimenti mostra solo se non ha fallito
        if failed is None:
            return True
        return not failed

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.time_chat_and_signals = save_time_value(player.time_on_page)
        print(f"ChatAndSignals - time_chat_and_signals saved: {player.time_chat_and_signals}")
        # Save data to participant vars for the next app
        player.participant.vars['draft_history_left'] = player.draft_history_left
        player.participant.vars['draft_history_right'] = player.draft_history_right
        player.participant.vars['signal_left'] = player.signal_left
        player.participant.vars['signal_right'] = player.signal_right
        # TEMPORANEO: Imposta failed_control_questions = False per permettere il test senza control questions
        player.participant.vars['failed_control_questions'] = False

page_sequence = [
    Welcome,
    InstructionsPart1,
    ControlQuestions,
    Goodbye,
    ChatAndSignals
]
