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
import time
from bargaining_tdl_common import (  # type: ignore
    save_time_value,
    get_page_timeout_seconds,
    timeout_submission_with_time,
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
    CHAT_RECONNECT_WINDOW_SECONDS = 90
    # Heartbeat tolerance tuned to avoid false disconnect flicker under network jitter.
    CHAT_DISCONNECT_DETECTION_SECONDS = 8
    CHAT_DISCONNECT_CONFIRMATION_SECONDS = 12

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    # Group-level variables for CSV export
    grp_coordinate = models.IntegerField(initial=0)  # 1 if group payoff is different from disagreement (at least one player has payoff > 0)
    grp_triadicsplit = models.IntegerField(initial=0)  # 1 if at least two players vote for "equally split among all the members of the group" (Both)
    selected_part_for_payment = models.IntegerField(initial=-1) # -1 = non ancora estratto, 0 = Part 3 paga, 1 = Part 1 paga
    chat_left_p1 = models.BooleanField(initial=False)
    chat_left_p2 = models.BooleanField(initial=False)
    chat_left_p3 = models.BooleanField(initial=False)
    group_dropped = models.BooleanField(initial=False)
    reconnect_deadline_ts = models.FloatField(initial=0)
    interrupted_player_id = models.IntegerField(initial=0)
    last_ping_p1 = models.FloatField(initial=0)
    last_ping_p2 = models.FloatField(initial=0)
    last_ping_p3 = models.FloatField(initial=0)
    submit_grace_until_p1 = models.FloatField(initial=0)
    submit_grace_until_p2 = models.FloatField(initial=0)
    submit_grace_until_p3 = models.FloatField(initial=0)
    part1_payoff_eligible = models.BooleanField(initial=True)

class Player(BasePlayer):
    # Color assigned to this player (Red/Green/Blue), stored for CSV export clarity
    player_color = models.StringField(blank=True)
    
    # Campo per salvare il vero payoff calcolato per tracciabilità nel DB
    part1_calculated_payoff = models.CurrencyField(
        initial=0,
        doc="Il vero payoff calcolato per Part 1, salvato per tracciabilità anche se Part 3 viene estratta per il pagamento."
    )

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
    chat_interrupted = models.BooleanField(initial=False)
    participant_left_ts = models.FloatField(initial=0)
    part1_payoff_eligible = models.BooleanField(initial=True)
    # 0 = active, 99 = timed out on Decision without making a choice
    decision_inactive = models.IntegerField(initial=0)
    # 0 = active, 99 = timed out on Signals without making a choice
    signal_inactive = models.IntegerField(initial=0)
    received_signal_left_inactive = models.IntegerField(initial=0)
    received_signal_right_inactive = models.IntegerField(initial=0)

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


def _signal_display_text(code, target_color, other_color, sender_inactive=False):
    """Human-readable text for a signal internal code."""
    # We no longer show "did not send a message" for inactive participants
    # as per user request to show the random choice instead.
    if code == 'split_you':
        # "you" refers to the receiver, so do not append a color label.
        return "I wish to split the $12 equally with you only."
    elif code == 'split_other':
        return f"I wish to split the $12 equally with the other Participant only, the {other_color} Participant."
    elif code == 'split_both':
        return f"I wish to split the $12 equally with both you and the {other_color} Participant."
    return code or ""


def _chat_left_state(group: Group):
    interrupted_id = group.interrupted_player_id
    is_dropped = group.group_dropped
    return {
        1: group.chat_left_p1 or (is_dropped and interrupted_id == 1),
        2: group.chat_left_p2 or (is_dropped and interrupted_id == 2),
        3: group.chat_left_p3 or (is_dropped and interrupted_id == 3),
    }


def _is_inactive_excluded(player: Player):
    return bool(player.participant.vars.get('inactive_excluded', False))


def _set_player_left_chat(player: Player):
    field_name = f'chat_left_p{player.id_in_group}'
    if hasattr(player.group, field_name):
        setattr(player.group, field_name, True)


def _set_last_ping(group: Group, player_id: int, ts: float):
    setattr(group, f'last_ping_p{player_id}', ts)


def _get_last_ping(group: Group, player_id: int):
    return getattr(group, f'last_ping_p{player_id}', 0)


def _set_submit_grace_until(group: Group, player_id: int, ts: float):
    setattr(group, f'submit_grace_until_p{player_id}', ts)


def _get_submit_grace_until(group: Group, player_id: int):
    return getattr(group, f'submit_grace_until_p{player_id}', 0)


def _advance_interrupted_player_to_waitpage(group: Group, wait_page_index: int):
    """
    Advance interrupted participant by timeout flow until wait page index.

    Important: submissions are triggered only after each page timeout expires,
    so auto-advance respects Chat/Signals/Decision timers.
    """
    interrupted_id = group.interrupted_player_id
    if not interrupted_id:
        return

    interrupted_player = group.get_player_by_id(interrupted_id)
    participant = interrupted_player.participant

    def _page_timeout_seconds(page_name: str):
        if page_name == 'Chat':
            return get_page_timeout_seconds(interrupted_player, Chat._CHAT_TIMEOUT)
        if page_name == 'Signals':
            return get_page_timeout_seconds(interrupted_player, Signals._SIGNALS_TIMEOUT)
        if page_name == 'Decision':
            return get_page_timeout_seconds(interrupted_player, Decision._DECISION_TIMEOUT)
        return None

    safety_steps = 10
    while participant._index_in_pages < wait_page_index and safety_steps > 0:
        safety_steps -= 1
        page = participant._get_page_instance()
        if not page:
            break
        if page._lookup.app_name != C.NAME_IN_URL:
            break

        # On wait pages rely on standard oTree polling/redirect behavior.
        if isinstance(page, WaitPage):
            before_idx = participant._index_in_pages
            try:
                participant._visit_current_page()
            except Exception as exc:
                logger.warning(
                    f"Could not visit wait page for interrupted participant {participant.code}: {exc}"
                )
                break
            if participant._index_in_pages == before_idx:
                break
            continue

        page_name = page.__class__.__name__
        timeout_seconds = _page_timeout_seconds(page_name)

        # If 2 peers already moved past Chat, force third to leave Chat immediately.
        if page_name == 'Chat':
            players = group.get_players()
            peers_ahead = sum(
                1
                for p in players
                if p.id_in_group != interrupted_id
                and p.participant._index_in_pages > participant._index_in_pages
            )
            if peers_ahead >= 2:
                try:
                    participant._submit_current_page()
                    participant._visit_current_page()
                except Exception as exc:
                    logger.warning(
                        f"Could not force Chat->Signals for interrupted participant {participant.code}: {exc}"
                    )
                    break
                continue

        if timeout_seconds is not None:
            # Never call page.remaining_timeout_seconds(): it can reset timeout state.
            # Read stored timeout markers directly from participant.
            if (
                participant._timeout_page_index == participant._index_in_pages
                and participant._timeout_expiration_time is not None
            ):
                remaining = participant._timeout_expiration_time - time.time()
            elif page_name == 'Signals' and interrupted_player.participant_left_ts:
                elapsed_offline = max(0.0, time.time() - interrupted_player.participant_left_ts)
                remaining = timeout_seconds - elapsed_offline
            else:
                remaining = timeout_seconds

            # If we moved an offline participant to Signals, oTree sets a fresh timeout.
            # For dropout handling we must also account for time already spent offline.
            if page_name == 'Signals' and interrupted_player.participant_left_ts:
                elapsed_offline = max(0.0, time.time() - interrupted_player.participant_left_ts)
                offline_remaining = timeout_seconds - elapsed_offline
                remaining = min(remaining, offline_remaining)

            if remaining > 0:
                # Timer still running on this page; do not force-skip early.
                break

        try:
            participant._submit_current_page()
            participant._visit_current_page()
        except Exception as exc:
            logger.warning(
                f"Could not auto-advance interrupted participant {participant.code}: {exc}"
            )
            break


def _mark_group_dropped(group: Group):
    group.group_dropped = True
    # We do NOT set group.part1_payoff_eligible = False globally anymore.
    # The interaction continues with random choices for the missing player.
    interrupted_id = group.interrupted_player_id
    import random
    for p in group.get_players():
        if p.id_in_group == interrupted_id:
            p.part1_payoff_eligible = False
            p.participant.part1_payoff_eligible = False
            p.participant.vars['part1_payoff_eligible'] = False
            p.decision_inactive = 99  # Garantisce la scelta casuale
            p.signal_inactive = 99
            p.signal_left = random.choice(['split_you', 'split_other', 'split_both'])
            p.signal_right = random.choice(['split_you', 'split_other', 'split_both'])
            p.participant.vars['signal_left'] = p.signal_left
            p.participant.vars['signal_right'] = p.signal_right
            p.participant.vars['signal_inactive'] = 99
            p.participant.vars['group_dropped'] = True
        else:
            # Gli attivi rimangono idonei e NON vengono spinti avanti
            p.part1_payoff_eligible = True
            p.participant.part1_payoff_eligible = True
            p.participant.vars['part1_payoff_eligible'] = True
            p.participant.vars['group_dropped'] = False


def _evaluate_dropout(group: Group):
    if group.group_dropped:
        return

    now = time.time()
    interrupted_id = group.interrupted_player_id

    if interrupted_id:
        last_ping = _get_last_ping(group, interrupted_id)
        # Se il giocatore è tornato (ping recente), annulliamo l'interruzione
        if last_ping and (now - last_ping) <= 5:
            group.interrupted_player_id = 0
            group.reconnect_deadline_ts = 0
            return
        # Se il tempo di riconnessione è scaduto, marchiamo il dropout definitivo
        if group.reconnect_deadline_ts and now >= group.reconnect_deadline_ts:
            _mark_group_dropped(group)
        return

    # Controlliamo se qualcuno è sparito (nessun ping recente e non ha ancora finito la fase)
    # Nota: escludiamo chi ha già finito la fase di chat (chat_left_pX)
    for player_id in [1, 2, 3]:
        # Se il giocatore ha già lasciato la chat regolarmente, non è un dropout qui
        # Ma se siamo in Signals/Decision, dobbiamo monitorare comunque.
        # Per semplicità monitoriamo chiunque non sia in "grace period" (invio form)
        grace_until = _get_submit_grace_until(group, player_id)
        if grace_until and now < grace_until:
            continue
            
        last_ping = _get_last_ping(group, player_id)
        if last_ping and (now - last_ping) > C.CHAT_DISCONNECT_CONFIRMATION_SECONDS:
            # Dropout rilevato: diamo 90 secondi per tornare
            group.interrupted_player_id = player_id
            group.reconnect_deadline_ts = now + C.CHAT_RECONNECT_WINDOW_SECONDS
            participant_player = group.get_player_by_id(player_id)
            participant_player.chat_interrupted = True
            participant_player.participant_left_ts = now
            break


def _chat_status_payload(player: Player):
    statuses = _chat_left_state(player.group)
    my_id = player.id_in_group
    left_id = get_left_partner_id(my_id)
    right_id = get_right_partner_id(my_id)
    left_count = sum(1 for has_left in statuses.values() if has_left)
    now = time.time()
    interrupted_id = player.group.interrupted_player_id
    reconnect_seconds_left = 0
    if interrupted_id and player.group.reconnect_deadline_ts:
        reconnect_seconds_left = max(0, int(round(player.group.reconnect_deadline_ts - now)))
    left_partner_temporarily_offline = bool(
        interrupted_id == left_id and reconnect_seconds_left > 0 and not player.group.group_dropped
    )
    right_partner_temporarily_offline = bool(
        interrupted_id == right_id and reconnect_seconds_left > 0 and not player.group.group_dropped
    )
    left_partner_permanently_dropped = bool(player.group.group_dropped and interrupted_id == left_id)
    right_partner_permanently_dropped = bool(player.group.group_dropped and interrupted_id == right_id)

    both_partners_left_chat = bool(statuses[left_id] and statuses[right_id])
    return dict(
        left_partner_id=left_id,
        right_partner_id=right_id,
        left_partner_active=not statuses[left_id] and not left_partner_temporarily_offline and not left_partner_permanently_dropped,
        right_partner_active=not statuses[right_id] and not right_partner_temporarily_offline and not right_partner_permanently_dropped,
        should_auto_advance=both_partners_left_chat and not statuses[my_id],
        left_count=left_count,
        group_dropped=player.group.group_dropped,
        interrupted_player_id=interrupted_id,
        waiting_on_reconnect=bool(interrupted_id and interrupted_id != my_id and reconnect_seconds_left > 0),
        reconnect_seconds_left=reconnect_seconds_left,
    )


def _chat_rows_for_decision(player: Player, channel: str, partner_label: str):
    """Return chat history formatted for read-only rendering on Decision page."""
    try:
        from otree.models_concrete import ChatMessage  # type: ignore
    except Exception:
        return []

    try:
        rows = list(ChatMessage.objects_filter(channel=channel).order_by('timestamp'))
    except Exception:
        return []

    my_participant_id = player.participant.id
    formatted = []
    for row in rows:
        speaker = 'You' if row.participant_id == my_participant_id else partner_label
        formatted.append(
            dict(
                speaker=speaker,
                body=row.body or '',
            )
        )
    return formatted


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
        receiver.received_signal_left_inactive = left_sender.participant.vars.get('signal_inactive', 0)
        receiver.received_signal_right_inactive = right_sender.participant.vars.get('signal_inactive', 0)

# PAGES

class GroupingAfterControlQuestions(WaitPage):
    """Form groups of 3 by arrival time (order of passing control questions). First page of app (oTree requirement)."""
    group_by_arrival_time = True
    title_text = "Please wait for other participants"
    body_text = "Please wait for the other participants to form your group."

    @staticmethod
    def after_all_players_arrive(group: Group):
        now = time.time()
        group.chat_left_p1 = False
        group.chat_left_p2 = False
        group.chat_left_p3 = False
        group.group_dropped = False
        group.part1_payoff_eligible = True
        group.interrupted_player_id = 0
        group.reconnect_deadline_ts = 0
        group.last_ping_p1 = now
        group.last_ping_p2 = now
        group.last_ping_p3 = now
        group.submit_grace_until_p1 = 0
        group.submit_grace_until_p2 = 0
        group.submit_grace_until_p3 = 0
        for p in group.get_players():
            p.time_welcome = p.participant.vars.get('time_welcome', 0)
            p.player_color = get_player_color(p.id_in_group)
            p.chat_interrupted = False
            p.participant_left_ts = 0
            p.part1_payoff_eligible = True
            p.participant.group_dropped = False
            p.participant.part1_payoff_eligible = True
            p.participant.vars['group_dropped'] = False
            p.participant.vars['part1_payoff_eligible'] = True
        triad_pids = [p.participant.id for p in group.get_players()]
        intro_groups = group.session.vars.setdefault('intro_groups', [])
        if triad_pids not in intro_groups:
            intro_groups.append(triad_pids)
        logger.debug(f"GroupingAfterControlQuestions: group formed ({len(intro_groups)} triads so far)")


class Chat(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    _CHAT_TIMEOUT = 600
    timer_text = "Chat time remaining:"

    @staticmethod
    def get_timeout_seconds(player):
        return get_page_timeout_seconds(player, Chat._CHAT_TIMEOUT)

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
            chat_timeout_seconds=get_page_timeout_seconds(player, Chat._CHAT_TIMEOUT),
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            **_chat_status_payload(player),
            **colors,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        _set_player_left_chat(player)
        player.time_chat = save_time_value(player.time_on_page)
        logger.debug(f"Chat - time_chat saved: {player.time_chat}")
        # Record why the player left the Chat page (used by Signals page for context messages)
        if timeout_happened:
            player.participant.vars['chat_advanced_reason'] = 'timeout'
        elif player.group.group_dropped:
            player.participant.vars['chat_advanced_reason'] = 'group_dropped'
        else:
            my_id = player.id_in_group
            left_id = get_left_partner_id(my_id)
            right_id = get_right_partner_id(my_id)
            statuses = _chat_left_state(player.group)
            if statuses.get(left_id) and statuses.get(right_id):
                player.participant.vars['chat_advanced_reason'] = 'partners_left'
            else:
                player.participant.vars['chat_advanced_reason'] = 'normal'

    @staticmethod
    def live_method(player: Player, data):
        now = time.time()
        payload_type = (data or {}).get('type')
        _set_last_ping(player.group, player.id_in_group, now)
        if payload_type == 'next_button_intent':
            # User opened confirm to proceed: avoid false disconnect while native dialog blocks JS.
            _set_submit_grace_until(player.group, player.id_in_group, now + 30)
        elif payload_type == 'next_button_cancelled':
            _set_submit_grace_until(player.group, player.id_in_group, now)

        if payload_type == 'client_leaving' and not player.group.group_dropped:
            player.group.interrupted_player_id = player.id_in_group
            player.group.reconnect_deadline_ts = now + C.CHAT_RECONNECT_WINDOW_SECONDS
            player.chat_interrupted = True
            player.participant_left_ts = now

        _evaluate_dropout(player.group)
        return {
            p.id_in_group: _chat_status_payload(p)
            for p in player.group.get_players()
        }


class Signals(Page):
    form_model = 'player'
    form_fields = ['signal_left', 'signal_right', 'first_intention_selected', 'time_on_page']
    _SIGNALS_TIMEOUT = 300
    timeout_submission = timeout_submission_with_time(
        _SIGNALS_TIMEOUT,
        signal_left='split_you',
        signal_right='split_you',
        first_intention_selected='left',
    )

    @staticmethod
    def get_timeout_seconds(player):
        return get_page_timeout_seconds(player, Signals._SIGNALS_TIMEOUT)

    @staticmethod
    def is_displayed(player: Player):
        return True

    @staticmethod
    def live_method(player: Player, data):
        now = time.time()
        _set_last_ping(player.group, player.id_in_group, now)
        
        payload_type = (data or {}).get('type')
        if payload_type == 'client_leaving' and not player.group.group_dropped:
            player.group.interrupted_player_id = player.id_in_group
            player.group.reconnect_deadline_ts = now + C.CHAT_RECONNECT_WINDOW_SECONDS
            player.chat_interrupted = True
            player.participant_left_ts = now

        _evaluate_dropout(player.group)
        return {
            p.id_in_group: _chat_status_payload(p)
            for p in player.group.get_players()
        }

    @staticmethod
    def vars_for_template(player: Player):
        colors = _color_context(player)
        reason = player.participant.vars.get('chat_advanced_reason', 'normal')
        return dict(
            chat_timeout=(reason == 'timeout'),
            chat_partners_left=(reason in ('group_dropped', 'partners_left')),
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            **_chat_status_payload(player),
            **colors,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_signals = save_time_value(player.time_on_page)
        player.time_chat_and_signals = player.time_chat + player.time_signals
        if timeout_happened:
            player.signal_inactive = 99
            # Inattività rilevata: escludiamo dal pagamento come richiesto
            player.part1_payoff_eligible = False
            player.participant.vars['part1_payoff_eligible'] = False
            import random
            player.signal_left = random.choice(['split_you', 'split_other', 'split_both'])
            player.signal_right = random.choice(['split_you', 'split_other', 'split_both'])
        else:
            set_control_questions_failed(player, 'intro', failed=False)
        logger.debug(f"Signals - time_signals saved: {player.time_signals}, time_chat_and_signals: {player.time_chat_and_signals}")
        player.participant.vars['signal_left'] = player.signal_left
        player.participant.vars['signal_right'] = player.signal_right
        player.participant.vars['signal_inactive'] = player.signal_inactive


class ExperimentTerminated(Page):
    """Pagina mostrata se il partecipante ha fallito le control questions."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se il partecipante ha fallito le control questions."""
        return has_failed_control_questions(player, 'intro') or _is_inactive_excluded(player)

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.session.config.get('completionlink', '').strip(),
        )
    
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
    def vars_for_template(player):
        _evaluate_dropout(player.group)
        _advance_interrupted_player_to_waitpage(
            player.group, player.participant._index_in_pages
        )
        return {}

    @staticmethod
    def after_all_players_arrive(group: Group):
        map_player_data_in_group(group)

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision_choice', 'time_on_page']
    _DECISION_TIMEOUT = 300
    timeout_submission = timeout_submission_with_time(
        _DECISION_TIMEOUT,
        decision_choice='Left',
    )

    @staticmethod
    def get_timeout_seconds(player):
        return get_page_timeout_seconds(player, Decision._DECISION_TIMEOUT)

    @staticmethod
    def live_method(player: Player, data):
        now = time.time()
        _set_last_ping(player.group, player.id_in_group, now)
        
        payload_type = (data or {}).get('type')
        if payload_type == 'client_leaving' and not player.group.group_dropped:
            player.group.interrupted_player_id = player.id_in_group
            player.group.reconnect_deadline_ts = now + C.CHAT_RECONNECT_WINDOW_SECONDS
            player.chat_interrupted = True
            player.participant_left_ts = now

        _evaluate_dropout(player.group)
        return {
            p.id_in_group: _chat_status_payload(p)
            for p in player.group.get_players()
        }

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
        
        left_inactive = bool(player.received_signal_left_inactive == 99)
        right_inactive = bool(player.received_signal_right_inactive == 99)
        
        received_left_display = _signal_display_text(
            player.received_signal_left,
            colors['left_partner_color'],
            colors['right_partner_color'],
            sender_inactive=left_inactive,
        )
        received_right_display = _signal_display_text(
            player.received_signal_right,
            colors['right_partner_color'],
            colors['left_partner_color'],
            sender_inactive=right_inactive,
        )
        left_chat_rows = _chat_rows_for_decision(
            player,
            channel_left,
            f"{colors['left_partner_color']} Participant",
        )
        right_chat_rows = _chat_rows_for_decision(
            player,
            channel_right,
            f"{colors['right_partner_color']} Participant",
        )
        options = [
            {
                'value': 'Left', 
                'id': 'dc_left', 
                'label': f'I would like to divide the $12 equally with the {colors["left_partner_color"]} Participant', 
                'details': f'($6 to you, $6 to the {colors["left_partner_color"]} Participant, $0 to the {colors["right_partner_color"]} Participant)'
            },
            {
                'value': 'Right', 
                'id': 'dc_right', 
                'label': f'I would like to divide the $12 equally with the {colors["right_partner_color"]} Participant', 
                'details': f'($6 to you, $6 to the {colors["right_partner_color"]} Participant, $0 to the {colors["left_partner_color"]} Participant)'
            },
            {
                'value': 'Both', 
                'id': 'dc_both', 
                'label': 'I would like to divide the $12 equally with the two other Participants', 
                'details': f'($4 to you, $4 to the {colors["left_partner_color"]} Participant, $4 to the {colors["right_partner_color"]} Participant)'
            },
        ]
        import random
        random.shuffle(options)

        return dict(
            channel_left=channel_left,
            channel_right=channel_right,
            received_signal_left_display=received_left_display,
            received_signal_right_display=received_right_display,
            left_chat_rows=left_chat_rows,
            right_chat_rows=right_chat_rows,
            signals_expired=bool(player.signal_inactive == 99),
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            decision_options=options,
            **_chat_status_payload(player),
            **colors,
        )

    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions o se è caduto."""
        if player.participant.vars.get('group_dropped'):
            player.decision_inactive = 99
            return False
        return not has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_decision = save_time_value(player.time_on_page)
        if timeout_happened:
            # Mark as inactive (99) for dataset tracking.
            player.decision_inactive = 99
            # Inattività rilevata: escludiamo dal pagamento
            player.part1_payoff_eligible = False
            player.participant.vars['part1_payoff_eligible'] = False


class InactivityGoodbyeMain(Page):
    template_name = 'bargaining_tdl_main/ExperimentTerminated.html'
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        # Se il giocatore è stato escluso per inattività o dropout, vede questa pagina
        return _is_inactive_excluded(player) or player.decision_inactive == 99 or not player.part1_payoff_eligible

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.session.config.get('completionlink', '').strip(),
        )

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return []

class ResultsWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro') and not _is_inactive_excluded(player)

    @staticmethod
    def vars_for_template(player):
        _evaluate_dropout(player.group)
        _advance_interrupted_player_to_waitpage(
            player.group, player.participant._index_in_pages
        )
        return {}
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        p1 = group.get_player_by_id(1)
        p2 = group.get_player_by_id(2)
        p3 = group.get_player_by_id(3)
        players = [p1, p2, p3]

        # If any player timed out without choosing, assign a random choice now.
        # The payoff logic below runs unchanged on whatever value is assigned.
        import random
        for p in [p1, p2, p3]:
            if p.decision_inactive == 99:
                p.decision_choice = random.choice(['Left', 'Right', 'Both'])

        # Choices
        c1 = p1.decision_choice
        c2 = p2.decision_choice
        c3 = p3.decision_choice

        # Initialize payoffs to Disagreement (0)
        for p in players:
            p.payoff = C.PAYOFF_DISAGREEMENT

        # We NO LONGER abort payoffs if group.group_dropped is True.
        # The logic below will use random choices for anyone with decision_inactive == 99.

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

        # ======= SELEZIONE CASUALE PARTE 1 O PARTE 3 =======
        import random
        selected = random.randint(0, 1)
        group.selected_part_for_payment = selected
        
        for p in players:
            # Salva il vero payoff calcolato nel DB per tracciabilità
            p.part1_calculated_payoff = p.payoff
            
            # If a player is not eligible (e.g. they dropped out), their official payoff is 0
            if not p.part1_payoff_eligible:
                p.payoff = cu(0)

            # Salva i valori originali in participant.vars
            p.participant.vars['part1_payoff'] = p.payoff
            p.participant.vars['selected_part_for_payment'] = selected
            p.participant.vars['part1_group_id'] = group.id
            
            # Se Part 3 è estratta, azzera il payoff UFFICIALE di Part 1 per non farlo sommare da oTree al totale
            if selected == 0:
                p.payoff = cu(0)

class Results(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    _RESULTS_TIMEOUT = 180
    timeout_submission = timeout_submission_with_time(_RESULTS_TIMEOUT)

    @staticmethod
    def get_timeout_seconds(player):
        return get_page_timeout_seconds(player, Results._RESULTS_TIMEOUT)

    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro') and not _is_inactive_excluded(player) and player.decision_inactive != 99

    @staticmethod
    def vars_for_template(player: Player):
        colors = _color_context(player)
        choice = player.decision_choice
        if choice == 'Left':
            choice_display = f"I would like to divide the $12 equally with the {colors['left_partner_color']} Participant"
        elif choice == 'Right':
            choice_display = f"I would like to divide the $12 equally with the {colors['right_partner_color']} Participant"
        else:
            choice_display = "I would like to divide the $12 equally among all the members of the group"
        return dict(choice_display=choice_display, **colors)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_results = save_time_value(player.time_on_page)

page_sequence = [
    GroupingAfterControlQuestions,  # Must be first (oTree: group_by_arrival_time)
    Chat,
    Signals,
    ExperimentTerminated,
    DataMappingWaitPage,
    Decision,
    ResultsWaitPage,
    Results,
    InactivityGoodbyeMain
]

