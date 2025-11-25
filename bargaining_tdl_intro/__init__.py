from otree.api import *

doc = """
Bargaining Game (Part 1: Individual Tasks)
Instructions -> Simulated Chat -> Signals
Data is saved to participant.vars for the next app.
"""

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TIMER_CHAT = 360

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Drafts (Simulated Chat)
    draft_history_left = models.LongStringField(blank=True)
    draft_history_right = models.LongStringField(blank=True)
    
    # Signals
    signal_left = models.StringField(
        choices=[
            "I wish to split the payoff equally with Participant Left only.",
            "I wish to split the payoff equally with Participant Right only.",
            "I wish to split the payoff equally with both of the other participants.",
            "I do not wish to communicate my intentions."
        ],
        widget=widgets.RadioSelect,
        label="Select signal for the participant on your LEFT:"
    )
    signal_right = models.StringField(
        choices=[
            "I wish to split the payoff equally with Participant Right only.",
            "I wish to split the payoff equally with Participant Left only.",
            "I wish to split the payoff equally with both of the other participants.",
            "I do not wish to communicate my intentions."
        ],
        widget=widgets.RadioSelect,
        label="Select signal for the participant on your RIGHT:"
    )

# PAGES

class Welcome(Page):
    pass

class InstructionsPart1(Page):
    pass

class SimulatedChat(Page):
    form_model = 'player'
    form_fields = ['draft_history_left', 'draft_history_right']
    timer_text = "Time remaining to write messages:"
    timeout_seconds = C.TIMER_CHAT

class SignalInput(Page):
    form_model = 'player'
    form_fields = ['signal_left', 'signal_right']

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
    SimulatedChat,
    SignalInput
]
