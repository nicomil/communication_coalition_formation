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
    has_failed_control_questions,
    set_control_questions_failed,
    get_logger,
    get_player_color,
    COLOR_MAPPING,
    TOPOLOGY,
    get_left_partner_id,
    get_right_partner_id,
)

logger = get_logger('main')

# Compat patch SQLAlchemy>=2.x: oTree WSChat._get_history usa .values(*str)
# che rompe con "Textual column expression 'nickname'..."
try:
    from otree.channels import consumers as _consumers  # type: ignore
    from otree.models_concrete import ChatMessage as _ChatMessage  # type: ignore

    def _patched_chat_history(self, channel):
        rows = list(_ChatMessage.objects_filter(channel=channel).order_by('timestamp'))
        return [
            {
                'nickname': row.nickname,
                'body': row.body,
                'participant_id': row.participant_id,
            }
            for row in rows
        ]

    _consumers.WSChat._get_history = _patched_chat_history
except Exception:
    pass

doc = """
Bargaining Game (Part 1: Grouping, Chat/Signals & Decision)
First page = group_by_arrival_time (form triads); then Chat, Signals, data mapping, Decision, Results.
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
    # Group-level variables for CSV export
    grp_coordinate = models.IntegerField(initial=0)  # 1 if group payoff is different from disagreement (at least one player has payoff > 0)
    grp_triadicsplit = models.IntegerField(initial=0)  # 1 if at least two players vote for "equally split among all the members of the group" (Both)

class Player(BasePlayer):
    # Color assigned to this player (Red/Green/Blue), stored for CSV export clarity
    player_color = models.StringField(blank=True)

    # Chat/Signals — internal values are short codes; display labels are rendered
    # in templates using the per-player color context variables.
    signal_left = models.StringField(
        choices=[
            ['split_you', 'split_you'],
            ['split_other', 'split_other'],
            ['split_both', 'split_both'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )
    signal_right = models.StringField(
        choices=[
            ['split_you', 'split_you'],
            ['split_other', 'split_other'],
            ['split_both', 'split_both'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )
    first_intention_selected = models.StringField(
        choices=[['left', 'Left'], ['right', 'Right']],
        blank=True,
        label="Which intention was selected first"
    )
    time_welcome = models.FloatField(initial=0)
    time_chat = models.FloatField(initial=0)
    time_signals = models.FloatField(initial=0)
    time_chat_and_signals = models.FloatField(initial=0)

    # Decision — internal values Left/Right/Both; display labels rendered in template
    decision_choice = models.StringField(
        choices=[
            ('Left', 'Left'),
            ('Right', 'Right'),
            ('Both', 'Both'),
        ],
        widget=widgets.RadioSelect,
        label="Select your choice:"
    )

    # Mapped Fields (Populated from participant.vars)
    received_signal_left = models.StringField(initial="")
    received_signal_right = models.StringField(initial="")
    
    # Player identification fields (for CSV export compatibility).
    # Internal meaning: topological first/second partner in the fixed ring topology.
    id_player_on_the_left = models.StringField(blank=True)  # partner code in internal 'left' coordinate
    id_player_on_the_right = models.StringField(blank=True)  # partner code in internal 'right' coordinate
    
    # Time tracking fields (in seconds)
    time_experiment_terminated = models.FloatField(initial=0)
    time_decision = models.FloatField(initial=0)
    time_results = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _color_context(player):
    """Build color labels for UI from stable internal topology coordinates."""
    my_id = player.id_in_group
    left_id = get_left_partner_id(my_id)
    right_id = get_right_partner_id(my_id)
    return dict(
        my_color=COLOR_MAPPING[my_id],
        left_partner_color=COLOR_MAPPING[left_id],
        right_partner_color=COLOR_MAPPING[right_id],
    )


def _signal_display_text(code, target_color, other_color):
    """Human-readable text for a signal internal code."""
    if code == 'split_you':
        return f"I wish to split the $12 equally with you only, the {target_color} player."
    elif code == 'split_other':
        return f"I wish to split the $12 equally with the other player only, the {other_color} player."
    elif code == 'split_both':
        return f"I wish to split the $12 equally with both you and the {other_color} player."
    return code or ""


def map_player_data_in_group(group: Group):
    """
    Mappa i dati tra i player nel gruppo seguendo la topology circolare.
    
    Questa funzione implementa la logica "Postman" per distribuire i dati
    tra i player del gruppo. Ogni player riceve i dati che gli altri player
    hanno inviato a lui durante la fase intro (draft_history e signal).
    
    Topology del Gruppo (circolare):
    - P1 (id=1): Left=P3, Right=P2
    - P2 (id=2): Left=P1, Right=P3
    - P3 (id=3): Left=P2, Right=P1
    
    Logica di mapping (Postman Logic):
    - Ogni player riceve i dati che gli altri player hanno inviato a lui
    - P1 riceve da Left (P3): quello che P3 ha inviato a Right (P1)
    - P1 riceve da Right (P2): quello che P2 ha inviato a Left (P1)
    
    I dati (segnali) vengono letti da participant.vars (salvati in intro) e mappati
    nei campi received_* del Player model in main.
    
    Args:
        group: Group instance con esattamente 3 player
    
    Side Effects:
        - Modifica i campi received_* di tutti i player nel gruppo:
          * received_signal_left/right
        - Imposta i campi id_player_on_the_left/right per ogni player:
          * id_player_on_the_left: participant.code del player a sinistra
          * id_player_on_the_right: participant.code del player a destra
    
    Example:
        >>> map_player_data_in_group(group)
        >>> p1.received_signal_left
        "I wish to split the $ 12 equally with you only."
    
    Note:
        - Richiede che i dati siano già presenti in participant.vars
        - Funziona solo con gruppi di esattamente 3 player
        - I dati mancanti vengono sostituiti con stringa vuota ("")
    """
    players = {p.id_in_group: p for p in group.get_players()}

    for receiver_id in [1, 2, 3]:
        receiver = players[receiver_id]
        left_player_id = get_left_partner_id(receiver_id)
        right_player_id = get_right_partner_id(receiver_id)

        receiver.id_player_on_the_left = players[left_player_id].participant.code
        receiver.id_player_on_the_right = players[right_player_id].participant.code

        left_sender = players[left_player_id]
        right_sender = players[right_player_id]

        # Internal convention:
        # - receiver.received_signal_left stores the signal that left partner sent to receiver
        # - receiver.received_signal_right stores the signal that right partner sent to receiver
        receiver.received_signal_left = left_sender.participant.vars.get('signal_right', "")
        receiver.received_signal_right = right_sender.participant.vars.get('signal_left', "")

# PAGES

class GroupingAfterControlQuestions(WaitPage):
    """Form groups of 3 by arrival time (order of passing control questions). First page of app (oTree requirement)."""
    group_by_arrival_time = True
    title_text = "Please wait for other participants"
    body_text = "Please wait for the other participants to form your group."

    @staticmethod
    def after_all_players_arrive(group: Group):
        for p in group.get_players():
            p.time_welcome = p.participant.vars.get('time_welcome', 0)
            p.player_color = get_player_color(p.id_in_group)
        triad_pids = [p.participant.id for p in group.get_players()]
        intro_groups = group.session.vars.setdefault('intro_groups', [])
        if triad_pids not in intro_groups:
            intro_groups.append(triad_pids)
        logger.debug(f"GroupingAfterControlQuestions: group formed ({len(intro_groups)} triads so far)")


class Chat(Page):
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def vars_for_template(player: Player):
        my_id = player.id_in_group
        partners = TOPOLOGY[my_id]
        left_id = partners['left']
        right_id = partners['right']
            
        group_id = player.group.id
        channel_left = f"{group_id}_{min(my_id, left_id)}_{max(my_id, left_id)}"
        channel_right = f"{group_id}_{min(my_id, right_id)}_{max(my_id, right_id)}"
        
        colors = _color_context(player)
        return dict(
            channel_left=channel_left,
            channel_right=channel_right,
            **colors,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_chat = save_time_value(player.time_on_page)
        logger.debug(f"Chat - time_chat saved: {player.time_chat}")


class Signals(Page):
    form_model = 'player'
    form_fields = ['signal_left', 'signal_right', 'first_intention_selected', 'time_on_page']

    @staticmethod
    def vars_for_template(player: Player):
        colors = _color_context(player)
        return dict(**colors)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_signals = save_time_value(player.time_on_page)
        player.time_chat_and_signals = player.time_chat + player.time_signals
        logger.debug(f"Signals - time_signals saved: {player.time_signals}, time_chat_and_signals: {player.time_chat_and_signals}")
        player.participant.vars['signal_left'] = player.signal_left
        player.participant.vars['signal_right'] = player.signal_right
        set_control_questions_failed(player, 'intro', failed=False)


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

class DataMappingWaitPage(WaitPage):
    """Sync and map participant.vars (intro chat/signals) to group received_* fields."""
    title_text = "Please wait"
    body_text = "Waiting for other participants."

    @staticmethod
    def is_displayed(player):
        return not has_failed_control_questions(player, 'intro')

    @staticmethod
    def after_all_players_arrive(group: Group):
        map_player_data_in_group(group)

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision_choice', 'time_on_page']

    @staticmethod
    def vars_for_template(player: Player):
        my_id = player.id_in_group
        partners = TOPOLOGY[my_id]
        left_id = partners['left']
        right_id = partners['right']
            
        group_id = player.group.id
        channel_left = f"{group_id}_{min(my_id, left_id)}_{max(my_id, left_id)}"
        channel_right = f"{group_id}_{min(my_id, right_id)}_{max(my_id, right_id)}"
        
        colors = _color_context(player)
        received_left_display = _signal_display_text(
            player.received_signal_left,
            colors['left_partner_color'],
            colors['right_partner_color'],
        )
        received_right_display = _signal_display_text(
            player.received_signal_right,
            colors['right_partner_color'],
            colors['left_partner_color'],
        )
        return dict(
            channel_left=channel_left,
            channel_right=channel_right,
            received_signal_left_display=received_left_display,
            received_signal_right_display=received_right_display,
            **colors,
        )

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
        # 1. At least 2 choose Both -> All get 4
        both_count = sum([c1 == 'Both', c2 == 'Both', c3 == 'Both'])
        if both_count >= 2:
            for p in players:
                p.payoff = C.PAYOFF_SPLIT
        else:
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
        
        # Calculate group-level variables
        # grp_coordinate: 1 if at least one player has payoff different from disagreement (payoff > 0)
        group.grp_coordinate = 1 if any(p.payoff > C.PAYOFF_DISAGREEMENT for p in players) else 0
        
        # grp_triadicsplit: 1 if at least two players voted for "Both" (equally split among all members)
        group.grp_triadicsplit = 1 if both_count >= 2 else 0

class Results(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro')

    @staticmethod
    def vars_for_template(player: Player):
        colors = _color_context(player)
        choice = player.decision_choice
        if choice == 'Left':
            choice_display = f"I would like to divide the $12 equally with the {colors['left_partner_color']} player"
        elif choice == 'Right':
            choice_display = f"I would like to divide the $12 equally with the {colors['right_partner_color']} player"
        else:
            choice_display = "I would like to divide the $12 equally among all the members of the group"
        return dict(choice_display=choice_display, **colors)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_results = save_time_value(player.time_on_page)
        player.participant.vars['part1_payoff'] = player.payoff

page_sequence = [
    GroupingAfterControlQuestions,  # Must be first (oTree: group_by_arrival_time)
    Chat,
    Signals,
    ExperimentTerminated,
    DataMappingWaitPage,
    Decision,
    ResultsWaitPage,
    Results
]

