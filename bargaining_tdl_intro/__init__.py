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

# PAGES

class Welcome(Page):
    pass

class InstructionsPart1(Page):
    pass

class ChatAndSignals(Page):
    form_model = 'player'
    form_fields = ['signal_left', 'signal_right', 'draft_history_left', 'draft_history_right']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Save data to participant vars for the next app
        player.participant.vars['draft_history_left'] = player.draft_history_left
        player.participant.vars['draft_history_right'] = player.draft_history_right
        player.participant.vars['signal_left'] = player.signal_left
        player.participant.vars['signal_right'] = player.signal_right

page_sequence = [
    Welcome,
    InstructionsPart1,
    ChatAndSignals
]
