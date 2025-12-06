from otree.api import *
from bargaining_tdl_common import (
    save_time_value,
    has_failed_control_questions,
)

doc = """
Bargaining Game (Part 2: Grouping & Decision)
GroupingWaitPage -> Decision -> Results
"""

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_main'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    PAYOFF_MAX = cu(6)
    PAYOFF_SPLIT = cu(4)
    PAYOFF_DISAGREEMENT = cu(0)

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Decision
    decision_choice = models.StringField(
        choices=['Left', 'Right', 'Both'],
        widget=widgets.RadioSelect,
        label="Select your choice:"
    )

    # Mapped Fields (Populated from participant.vars)
    received_history_left = models.LongStringField(initial="")
    received_history_right = models.LongStringField(initial="")
    received_signal_left = models.StringField(initial="")
    received_signal_right = models.StringField(initial="")
    
    # Time tracking fields (in seconds)
    time_experiment_terminated = models.FloatField(initial=0)
    time_decision = models.FloatField(initial=0)
    time_results = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def map_player_data_in_group(group: Group):
    """
    Mappa i dati tra i player nel gruppo seguendo la topology circolare.
    
    Topology:
    - P1 (id=1): Left=P3, Right=P2
    - P2 (id=2): Left=P1, Right=P3
    - P3 (id=3): Left=P2, Right=P1
    
    Logica di mapping (Postman Logic):
    - Ogni player riceve i dati che gli altri player hanno inviato a lui
    - P1 riceve da Left (P3): quello che P3 ha inviato a Right (P1)
    - P1 riceve da Right (P2): quello che P2 ha inviato a Left (P1)
    
    Args:
        group: Group instance con 3 player
    """
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p3 = group.get_player_by_id(3)
    
    # Helper per accedere ai participant.vars in modo sicuro
    def get_vars(p):
        return p.participant.vars
    
    # Mapping topology: (receiver_id, direction) -> (sender_id, sender_direction)
    # receiver riceve da direction quello che sender ha inviato a sender_direction
    topology = {
        (1, 'left'): (3, 'right'),   # P1 riceve da Left (P3) quello che P3 ha inviato a Right
        (1, 'right'): (2, 'left'),   # P1 riceve da Right (P2) quello che P2 ha inviato a Left
        (2, 'left'): (1, 'right'),   # P2 riceve da Left (P1) quello che P1 ha inviato a Right
        (2, 'right'): (3, 'left'),   # P2 riceve da Right (P3) quello che P3 ha inviato a Left
        (3, 'left'): (2, 'right'),   # P3 riceve da Left (P2) quello che P2 ha inviato a Right
        (3, 'right'): (1, 'left'),   # P3 riceve da Right (P1) quello che P1 ha inviato a Left
    }
    
    # Mapping player objects per accesso rapido
    players = {1: p1, 2: p2, 3: p3}
    
    # Applica il mapping per ogni player e direzione
    for receiver_id in [1, 2, 3]:
        receiver = players[receiver_id]
        
        for direction in ['left', 'right']:
            sender_id, sender_direction = topology[(receiver_id, direction)]
            sender = players[sender_id]
            
            # Recupera i dati dal sender
            sender_vars = get_vars(sender)
            
            # Mappa history e signal
            if direction == 'left':
                receiver.received_history_left = sender_vars.get(f'draft_history_{sender_direction}', "")
                receiver.received_signal_left = sender_vars.get(f'signal_{sender_direction}', "")
            else:  # right
                receiver.received_history_right = sender_vars.get(f'draft_history_{sender_direction}', "")
                receiver.received_signal_right = sender_vars.get(f'signal_{sender_direction}', "")

# PAGES

class ExperimentTerminated(Page):
    """Pagina mostrata se il partecipante ha fallito le control questions."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se il partecipante ha fallito le control questions."""
        return has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_experiment_terminated = save_time_value(player.time_on_page)
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "Please wait for other participants"
    body_text = "Waiting for other participants to finish the initial phase."

    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento se il partecipante ha fallito le control questions."""
        if has_failed_control_questions(player, 'intro'):
            return []
        # NON restituire nulla - lascia che oTree gestisca automaticamente il flusso
        # Restituire upcoming_apps causa validazione prematura di tutte le app nella sequenza
        # Se part2 non è ancora riconosciuta, fallisce
        return None

    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        Mappa i dati tra i player quando tutti sono arrivati nel gruppo.
        Usa la funzione helper map_player_data_in_group per semplificare la logica.
        """
        map_player_data_in_group(group)

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision_choice', 'time_on_page']

    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_decision = save_time_value(player.time_on_page)

class ResultsWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        p1 = group.get_player_by_id(1)
        p2 = group.get_player_by_id(2)
        p3 = group.get_player_by_id(3)
        players = [p1, p2, p3]

        # Choices
        c1 = p1.decision_choice
        c2 = p2.decision_choice
        c3 = p3.decision_choice

        # Initialize payoffs to Disagreement (0)
        for p in players:
            p.payoff = C.PAYOFF_DISAGREEMENT

        # Logic:
        # 1. All choose Both -> All get 4
        if c1 == 'Both' and c2 == 'Both' and c3 == 'Both':
            for p in players:
                p.payoff = C.PAYOFF_SPLIT
            return

        # 2. Pairwise matches (Strict majority, implicit)
        # P1-P2 match? (P1->Right, P2->Left)
        match_12 = (c1 == 'Right' and c2 == 'Left')
        
        # P2-P3 match? (P2->Right, P3->Left)
        match_23 = (c2 == 'Right' and c3 == 'Left')

        # P3-P1 match? (P3->Right, P1->Left)
        match_31 = (c3 == 'Right' and c1 == 'Left')

        if match_12:
            p1.payoff = C.PAYOFF_MAX
            p2.payoff = C.PAYOFF_MAX
            p3.payoff = C.PAYOFF_DISAGREEMENT
        elif match_23:
            p2.payoff = C.PAYOFF_MAX
            p3.payoff = C.PAYOFF_MAX
            p1.payoff = C.PAYOFF_DISAGREEMENT
        elif match_31:
            p3.payoff = C.PAYOFF_MAX
            p1.payoff = C.PAYOFF_MAX
            p2.payoff = C.PAYOFF_DISAGREEMENT
        
        # Else remains 0 (Disagreement)

class Results(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_results = save_time_value(player.time_on_page)
        """Salva il payoff della Part 1 in participant.vars per uso futuro."""
        player.participant.vars['part1_payoff'] = player.payoff

page_sequence = [
    GroupingWaitPage,  # Deve essere prima per group_by_arrival_time=True
    ExperimentTerminated,  # Mostrata solo se failed_control_questions=True
    Decision,
    ResultsWaitPage,
    Results
]

