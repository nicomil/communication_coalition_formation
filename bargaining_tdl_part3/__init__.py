from otree.api import *

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

def check_all_control_questions_correct(player):
    """Verifica se tutte le risposte alle control questions sono corrette."""
    # Verifica che tutti i campi siano stati compilati
    if (not player.example1_earnings_you or 
        not player.example1_earnings_left or 
        not player.example1_earnings_right or
        not player.example2_earnings_you or 
        not player.example2_earnings_left or 
        not player.example2_earnings_right or
        not player.payoff_question):
        return False
    
    # Example 1: tutte le risposte devono essere '4'
    # Example 2: you='0', left='6', right='6'
    # Payoff question: risposta corretta specifica
    correct = (
        player.example1_earnings_you == '4' and
        player.example1_earnings_left == '4' and
        player.example1_earnings_right == '4' and
        player.example2_earnings_you == '0' and
        player.example2_earnings_left == '6' and
        player.example2_earnings_right == '6' and
        player.payoff_question == 'I will be paid an amount equal to the sum of my earnings in Part 2 and my earnings in either Part 1 or Part 3.'
    )
    return correct

# PAGES

class InstructionsPart3(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        def save_time_value(time_value, default=0.0):
            if time_value is None or time_value == '':
                return default
            try:
                return float(time_value)
            except (ValueError, TypeError):
                return default
        player.time_instructions_part3 = save_time_value(player.time_on_page)

class SummaryPart3(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        def save_time_value(time_value, default=0.0):
            if time_value is None or time_value == '':
                return default
            try:
                return float(time_value)
            except (ValueError, TypeError):
                return default
        player.time_summary_part3 = save_time_value(player.time_on_page)

class ControlQuestionsPart3(Page):
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
    def before_next_page(player, timeout_happened):
        def save_time_value(time_value, default=0.0):
            if time_value is None or time_value == '':
                return default
            try:
                return float(time_value)
            except (ValueError, TypeError):
                return default
        player.time_control_questions_part3 = save_time_value(player.time_on_page)
        """Valida tutte le risposte alle control questions."""
        player.all_control_questions_correct = check_all_control_questions_correct(player)
        if not player.all_control_questions_correct:
            player.participant.vars['failed_control_questions_part3'] = True

class ThankYouPart3(Page):
    """Pagina mostrata se il partecipante ha fallito le control questions."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se il partecipante ha fallito le control questions."""
        return not player.all_control_questions_correct
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        def save_time_value(time_value, default=0.0):
            if time_value is None or time_value == '':
                return default
            try:
                return float(time_value)
            except (ValueError, TypeError):
                return default
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
        return player.all_control_questions_correct
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        def save_time_value(time_value, default=0.0):
            if time_value is None or time_value == '':
                return default
            try:
                return float(time_value)
            except (ValueError, TypeError):
                return default
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
        def save_time_value(time_value, default=0.0):
            if time_value is None or time_value == '':
                return default
            try:
                return float(time_value)
            except (ValueError, TypeError):
                return default
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
    ControlQuestionsPart3,
    ThankYouPart3,  # Solo se control questions sbagliate
    DecisionPart3,  # Solo se control questions corrette
    ResultsPart3,  # Solo se control questions corrette - mostra payoff
]
