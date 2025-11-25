from otree.api import *

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

# PAGES

class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "Please wait for other participants"
    body_text = "Waiting for other participants to finish the initial phase."

    @staticmethod
    def after_all_players_arrive(group: Group):
        # Form Triad: IDs 1, 2, 3 are assigned by otree automatically within the group
        p1 = group.get_player_by_id(1)
        p2 = group.get_player_by_id(2)
        p3 = group.get_player_by_id(3)

        # Helper to safely get vars
        def get_vars(p):
            return p.participant.vars

        # Topology:
        # P1: Left=P3, Right=P2
        # P2: Left=P1, Right=P3
        # P3: Left=P2, Right=P1

        # Mapping Data (Postman Logic)
        # Note: participant.vars access
        
        # P1
        # Receives from Left (P3). P3 sent to Right (P1).
        p1.received_history_left = get_vars(p3).get('draft_history_right', "")
        p1.received_signal_left = get_vars(p3).get('signal_right', "")
        # Receives from Right (P2). P2 sent to Left (P1).
        p1.received_history_right = get_vars(p2).get('draft_history_left', "")
        p1.received_signal_right = get_vars(p2).get('signal_left', "")

        # P2
        # Receives from Left (P1). P1 sent to Right (P2).
        p2.received_history_left = get_vars(p1).get('draft_history_right', "")
        p2.received_signal_left = get_vars(p1).get('signal_right', "")
        # Receives from Right (P3). P3 sent to Left (P2).
        p2.received_history_right = get_vars(p3).get('draft_history_left', "")
        p2.received_signal_right = get_vars(p3).get('signal_left', "")

        # P3
        # Receives from Left (P2). P2 sent to Right (P3).
        p3.received_history_left = get_vars(p2).get('draft_history_right', "")
        p3.received_signal_left = get_vars(p2).get('signal_right', "")
        # Receives from Right (P1). P1 sent to Left (P3).
        p3.received_history_right = get_vars(p1).get('draft_history_left', "")
        p3.received_signal_right = get_vars(p1).get('signal_left', "")

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision_choice']

class ResultsWaitPage(WaitPage):
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
    pass

page_sequence = [
    GroupingWaitPage,
    Decision,
    ResultsWaitPage,
    Results
]

