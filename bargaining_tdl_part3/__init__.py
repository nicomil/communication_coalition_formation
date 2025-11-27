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
    pass

class SummaryPart3(Page):
    pass

class ControlQuestionsPart3(Page):
    form_model = 'player'
    form_fields = [
        'example1_earnings_you',
        'example1_earnings_left',
        'example1_earnings_right',
        'example2_earnings_you',
        'example2_earnings_left',
        'example2_earnings_right',
        'payoff_question'
    ]
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Valida tutte le risposte alle control questions."""
        player.all_control_questions_correct = check_all_control_questions_correct(player)
        if not player.all_control_questions_correct:
            player.participant.vars['failed_control_questions_part3'] = True

class ThankYouPart3(Page):
    """Pagina mostrata se il partecipante ha fallito le control questions."""
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se il partecipante ha fallito le control questions."""
        return not player.all_control_questions_correct
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class DecisionPart3(Page):
    form_model = 'player'
    form_fields = ['decision']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le control questions sono corrette."""
        return player.all_control_questions_correct

class ResultsPart3(Page):
    """Payoff Page - mostra i payoff dell'esperimento."""
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le control questions sono corrette e la decisione è stata presa."""
        return player.all_control_questions_correct and player.decision is not None
    
    @staticmethod
    def vars_for_template(player):
        """Recupera i payoff per la visualizzazione."""
        # Per ora: recuperare solo payoff Part 1
        # Il payoff della Part 1 è già stato calcolato e salvato in bargaining_tdl_main
        # In oTree, ogni app ha i propri player objects, quindi dobbiamo accedere ai dati della app precedente
        
        # Prova a recuperare il payoff dalla Part 1 (bargaining_tdl_main)
        # Il payoff viene salvato automaticamente in player.payoff per ogni app
        # Per accedere ai dati di un'altra app, possiamo usare participant.vars o accedere direttamente
        part1_payoff = cu(0)
        
        # Verifica se il payoff è stato salvato in participant.vars
        if 'part1_payoff' in player.participant.vars:
            part1_payoff = player.participant.vars['part1_payoff']
        else:
            # Prova a recuperare dai dati della app precedente
            # In oTree, possiamo accedere ai player objects delle app precedenti
            # Per semplicità, se non trovato, mostriamo 0
            # In futuro, questo verrà implementato correttamente quando si calcoleranno tutti i payoff
            pass
        
        # In futuro: aggiungere part2_payoff, part3_payoff, total_payoff
        return dict(
            part1_payoff=part1_payoff,
        )

page_sequence = [
    InstructionsPart3,
    SummaryPart3,
    ControlQuestionsPart3,
    ThankYouPart3,  # Solo se control questions sbagliate
    DecisionPart3,  # Solo se control questions corrette
    ResultsPart3,  # Solo se control questions corrette - mostra payoff
]
