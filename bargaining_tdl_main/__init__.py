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
import random
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
    get_partner_side,
    get_treatment,
    treatment_flag,
    VALID_DECISIONS,
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
    PAYOFF_MAX = cu(3)
    PAYOFF_NO_DWL = cu(6)
    PAYOFF_DISAGREEMENT = cu(0)
    CHAT_RECONNECT_WINDOW_SECONDS = 90
    # Heartbeat tolerance tuned to avoid false disconnect flicker under network jitter.
    CHAT_DISCONNECT_DETECTION_SECONDS = 8
    CHAT_DISCONNECT_CONFIRMATION_SECONDS = 12


VALID_SIGNALS = ('split_you', 'split_other', 'support_none')


class Subsession(BaseSubsession):
    pass


def group_by_arrival_time_method(subsession, waiting_players):
    """
    Forma triadi OMOGENEE per trattamento (requisito del gioco a 3) e composte
    solo da chi ha superato le control questions.

    Chi fallisce le CQ termina già nell'intro e non arriva qui; il filtro è
    comunque difensivo. Per ogni trattamento si forma un gruppo non appena ci
    sono almeno PLAYERS_PER_GROUP partecipanti in attesa con lo stesso trattamento.
    """
    from collections import defaultdict
    pools = defaultdict(list)
    for p in waiting_players:
        if has_failed_control_questions(p, 'intro'):
            continue
        pools[get_treatment(p)].append(p)
    for _treatment, players in pools.items():
        if len(players) >= C.PLAYERS_PER_GROUP:
            return players[:C.PLAYERS_PER_GROUP]
    return None

class Group(BaseGroup):
    # Group-level variables for CSV export
    grp_coordinate = models.IntegerField(initial=0)  # 1 if group payoff is different from disagreement (at least one player has payoff > 0)
    group_outcome = models.StringField(initial='pending')
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
    # Color assigned to this player (Yellow/Orange/Purple), stored for CSV export clarity
    player_color = models.StringField(blank=True)
    # Trattamento sperimentale, per CSV export.
    treatment = models.StringField(blank=True)
    
    # Campo per salvare il vero payoff calcolato per tracciabilità nel DB
    part1_calculated_payoff = models.CurrencyField(
        initial=0,
        doc="Payoff calcolato in Part 1 prima dell'eventuale esclusione per inattività."
    )

    # Chat/Signals — internal values are short codes; display labels are rendered
    # in templates using the per-player color context variables.
    signal_left = models.StringField(
        choices=[
            ['split_you', 'split_you'],
            ['split_other', 'split_other'],
            ['support_none', 'support_none'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )
    signal_right = models.StringField(
        choices=[
            ['split_you', 'split_you'],
            ['split_other', 'split_other'],
            ['support_none', 'support_none'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )
    first_intention_selected = models.StringField(
        choices=[['left', 'Left'], ['right', 'Right']],
        blank=True,
        label="Which intention was selected first"
    )
    guess_left_confidence = models.IntegerField(min=1, max=8, blank=True)
    guess_right_confidence = models.IntegerField(min=1, max=8, blank=True)
    time_welcome = models.FloatField(initial=0)
    time_chat = models.FloatField(initial=0)
    time_signals = models.FloatField(initial=0)

    # Decision — supporta partner left/right oppure nessuno.
    decision_choice = models.StringField(
        choices=[
            ('Left', 'Left'),
            ('Right', 'Right'),
            ('NoOne', 'NoOne'),
        ],
        widget=widgets.RadioSelect,
        label="Select your choice:"
    )
    # Ordine in cui le tre opzioni sono state mostrate in Decision. Viene
    # assegnato una sola volta al primo rendering e poi riutilizzato anche in
    # caso di refresh o riconnessione, per rendere l'ordine osservato
    # ricostruibile dall'export.
    decision_option_1 = models.StringField(
        choices=[('Left', 'Left'), ('Right', 'Right'), ('NoOne', 'NoOne')],
        initial='',
        blank=True,
    )
    decision_option_2 = models.StringField(
        choices=[('Left', 'Left'), ('Right', 'Right'), ('NoOne', 'NoOne')],
        initial='',
        blank=True,
    )
    decision_option_3 = models.StringField(
        choices=[('Left', 'Left'), ('Right', 'Right'), ('NoOne', 'NoOne')],
        initial='',
        blank=True,
    )

    # Mapped Fields (Populated from participant.vars)
    received_signal_left = models.StringField(initial="")
    received_signal_right = models.StringField(initial="")
    
    # Player identification fields (for CSV export compatibility).
    # Internal meaning: topological first/second partner in the fixed ring topology.
    id_player_on_the_left = models.StringField(blank=True)  # partner code in internal 'left' coordinate
    id_player_on_the_right = models.StringField(blank=True)  # partner code in internal 'right' coordinate
    # Per-player randomized visual order. This is deliberately separate from
    # the topological left/right fields above, which define game semantics.
    id_player_visualized_on_the_left = models.StringField(blank=True)
    id_player_visualized_on_the_right = models.StringField(blank=True)
    
    # Time tracking fields (in seconds)
    time_experiment_terminated = models.FloatField(initial=0)
    time_decision = models.FloatField(initial=0)
    time_post_decision_confidence = models.FloatField(initial=0)
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

    # Belief elicitation: guess delle scelte dei partner (stesso encoding di decision_choice)
    # Il valore è la scelta dal POV del partner interrogato: 'NoOne' | 'Left' | 'Right'
    guess_left_choice = models.StringField(
        choices=[('NoOne', 'No one'), ('Left', 'Left'), ('Right', 'Right')],
        blank=True,
        initial='',
        doc="Player's guess of left partner's decision_choice (NoOne/Left/Right from left partner's POV)"
    )
    guess_right_choice = models.StringField(
        choices=[('NoOne', 'No one'), ('Left', 'Left'), ('Right', 'Right')],
        blank=True,
        initial='',
        doc="Player's guess of right partner's decision_choice (NoOne/Left/Right from right partner's POV)"
    )


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
    """Human-readable text for a signal received by the current player.
    target_color: colore del mittente (mantenuto per retro-compatibilità firma).
    other_color: colore del TERZO partecipante (non il viewer, non il mittente).
    """
    if code == 'split_you':
        return "I intend to support you."
    elif code == 'split_other':
        return f"I intend to support {other_color}."
    elif code == 'support_none':
        return "I intend to support no one."
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


def _force_advance_lagging_chat_player(group: Group):
    """
    Rete di sicurezza server-side: se 2 dei 3 giocatori hanno già lasciato la
    Chat regolarmente ma il terzo no, lo facciamo avanzare noi (indipendentemente
    da 'interrupted_player_id', che potrebbe essere occupato da un falso
    positivo di dropout su uno degli altri due). Copre i casi in cui il push
    client-side 'should_auto_advance' non arriva (tab in background, glitch di
    rete) e non c'è nessun altro meccanismo che lo forzi avanti.
    """
    statuses = _chat_left_state(group)
    lagging_ids = [pid for pid, left in statuses.items() if not left]
    if len(lagging_ids) != 1:
        return

    lagging_player = group.get_player_by_id(lagging_ids[0])
    participant = lagging_player.participant
    page = participant._get_page_instance()
    if not page or page.__class__.__name__ != 'Chat':
        return

    try:
        participant._submit_current_page()
        participant._visit_current_page()
    except Exception as exc:
        logger.warning(
            f"Could not force-advance lagging chat participant {participant.code}: {exc}"
        )
        return

    # Avanzare l'indice lato server non basta: il browser resta sulla Chat finché
    # non riceve la notifica di auto-advance (come fa oTree in
    # Session.advance_last_place_participants). Senza questa, il terzo resta fermo
    # a video anche se il server l'ha già portato a Signals.
    _notify_browser_auto_advance(participant)


def _notify_browser_auto_advance(participant):
    """Dice al browser del partecipante di navigare alla pagina server corrente."""
    try:
        import otree.channels.utils as channel_utils
        channel_utils.sync_group_send(
            group=channel_utils.auto_advance_group(participant.code),
            data={'auto_advanced': True},
        )
    except Exception as exc:
        logger.warning(
            f"Could not notify auto-advance for participant {participant.code}: {exc}"
        )


# Secondi di silenzio oltre i quali un partecipante viene finalizzato d'ufficio.
# Serve perché il timer di pagina di oTree vive nel browser: se la scheda è
# chiusa il timeout non scatta mai, decision_choice resta NULL e gli altri due
# del gruppo non possono chiudere Part 1.
ABSENT_FINALIZE_SECONDS = 180


def _seconds_since_last_request(player: Player):
    ts = player.participant._last_request_timestamp or 0
    if not ts:
        return 0.0
    return max(0.0, time.time() - ts)


def _decision_option_order(player: Player):
    """Return and persist the one random order shown on the Decision page."""
    fields = (
        'decision_option_1',
        'decision_option_2',
        'decision_option_3',
    )

    order = [player.field_maybe_none(field) or '' for field in fields]
    if sorted(order) == sorted(VALID_DECISIONS):
        return order

    import random
    order = list(VALID_DECISIONS)
    random.shuffle(order)
    for field, value in zip(fields, order):
        setattr(player, field, value)
    # In oTree 6 i modelli sono SQLAlchemy: l'assegnazione entra nella
    # sessione e viene scritta a fine richiesta. Non esiste un .save(), e
    # chiamarlo solleva AttributeError.
    return order


def _ensure_visualized_order(player: Player):
    """Assign and persist a random visual order for this player's two partners."""
    # I campi partono a None, e oTree solleva TypeError se un campo nullo viene
    # letto direttamente: qui si legge per sapere se l'ordine e' gia' stato
    # assegnato, quindi il valore nullo e' il caso normale, non un errore.
    already_left = player.field_maybe_none('id_player_visualized_on_the_left')
    already_right = player.field_maybe_none('id_player_visualized_on_the_right')
    if already_left and already_right:
        return

    my_id = player.id_in_group
    partner_ids = [get_left_partner_id(my_id), get_right_partner_id(my_id)]
    random.SystemRandom().shuffle(partner_ids)
    group_players = {p.id_in_group: p for p in player.group.get_players()}
    player.id_player_visualized_on_the_left = group_players[partner_ids[0]].participant.code
    player.id_player_visualized_on_the_right = group_players[partner_ids[1]].participant.code


def _visualized_partner_context(player):
    """Return visual partner IDs/colors/channels, preserving topological semantics."""
    _ensure_visualized_order(player)
    by_code = {p.participant.code: p.id_in_group for p in player.group.get_players()}
    visual_left_id = by_code[player.id_player_visualized_on_the_left]
    visual_right_id = by_code[player.id_player_visualized_on_the_right]
    my_id = player.id_in_group
    group_id = player.group.id
    return dict(
        visual_left_id=visual_left_id,
        visual_right_id=visual_right_id,
        visual_left_color=COLOR_MAPPING[visual_left_id],
        visual_right_color=COLOR_MAPPING[visual_right_id],
        visual_left_channel=f"{group_id}_{min(my_id, visual_left_id)}_{max(my_id, visual_left_id)}",
        visual_right_channel=f"{group_id}_{min(my_id, visual_right_id)}_{max(my_id, visual_right_id)}",
        visual_left_is_topological_left=(visual_left_id == get_left_partner_id(my_id)),
        visual_right_is_topological_left=(visual_right_id == get_left_partner_id(my_id)),
        # Il nickname non dice chi c'e' in quella colonna: dice come appaio io
        # a chi legge. Nell'anello, se X e' il mio partner sinistro allora io
        # sono il partner destro di X, quindi nella chat con lui mi annuncio
        # come 'RightPartner'. _chat_customization.html risolve la stringa con
        # i colori topologici del destinatario: invertirla gli fa comparire il
        # colore del terzo giocatore.
        visual_left_nickname=(
            'RightPartner' if visual_left_id == get_left_partner_id(my_id)
            else 'LeftPartner'
        ),
        visual_right_nickname=(
            'RightPartner' if visual_right_id == get_left_partner_id(my_id)
            else 'LeftPartner'
        ),
    )


def custom_export(players):
    # Riferimento dummy per silenziare il warning (id=131) del linter di oTree
    # per funzioni esportate in un'altra app (bargaining_tdl_survey).
    _ = [seconds_until_absent, finalize_absent_players]
    yield ['session', 'participant', 'player', 'payoff']


def is_participant_absent(player: Player):
    """True se il partecipante non risponde più: o il timeout della pagina su
    cui è fermo è già scaduto lato server, o non contatta il server da
    ABSENT_FINALIZE_SECONDS."""
    expiration = player.participant._timeout_expiration_time or 0
    if expiration and time.time() > expiration:
        return True
    return _seconds_since_last_request(player) > ABSENT_FINALIZE_SECONDS


def seconds_until_absent(player: Player):
    """Quanto manca prima che questo giocatore possa essere finalizzato."""
    if is_participant_absent(player):
        return 0
    remaining = [ABSENT_FINALIZE_SECONDS - _seconds_since_last_request(player)]
    expiration = player.participant._timeout_expiration_time or 0
    if expiration:
        remaining.append(expiration - time.time())
    return max(0, int(round(min(remaining))))


def finalize_absent_players(group: Group, force=False):
    """Assegna una scelta casuale a chi è sparito senza decidere, così il
    gruppo può calcolare i payoff. Chi viene finalizzato così perde
    l'idoneità al pagamento di Part 1: l'osservazione non è sua.

    Ritorna True se tutti e tre hanno ora una decisione valida.
    """
    import random
    for p in group.get_players():
        if p.field_maybe_none('decision_choice'):
            continue
        if not (force or is_participant_absent(p)):
            continue
        p.decision_choice = random.choice(VALID_DECISIONS)
        p.decision_inactive = 99
        p.part1_payoff_eligible = False
        p.participant.part1_payoff_eligible = False
        p.participant.vars['part1_payoff_eligible'] = False
        logger.info(
            f"finalize_absent_players: gruppo {group.id}, giocatore "
            f"{p.id_in_group} assente da {_seconds_since_last_request(p):.0f}s, "
            f"scelta casuale {p.decision_choice}"
        )
    return all(p.field_maybe_none('decision_choice') for p in group.get_players())


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
            p.signal_left = random.choice(VALID_SIGNALS)
            p.signal_right = random.choice(VALID_SIGNALS)
            p.decision_choice = random.choice(VALID_DECISIONS)  # uniform 1/3 su Left/Right/NoOne
            p.guess_left_choice = random.choice(VALID_DECISIONS)
            p.guess_right_choice = random.choice(VALID_DECISIONS)
            p.guess_left_confidence = 1
            p.guess_right_confidence = 1
            p.participant.vars['signal_left'] = p.signal_left
            p.participant.vars['signal_right'] = p.signal_right
            p.participant.vars['signal_inactive'] = 99
            p.participant.vars['group_dropped'] = True
            p.participant.vars['group_dropped_inactive'] = True
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

    # Controlliamo se qualcuno è sparito (nessun ping recente su pagine attive)
    for player_id in [1, 2, 3]:
        p = group.get_player_by_id(player_id)
        page = p.participant._get_page_instance()
        
        # Ignoriamo chi è su WaitPage o risultati, dove l'heartbeat è sospeso per design.
        if not page or page.__class__.__name__ not in ['Chat', 'Signals', 'Decision']:
            continue

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
    visual = _visualized_partner_context(player)
    left_id = visual['visual_left_id']
    right_id = visual['visual_right_id']
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


def _third_party_chat_rows(player: Player, channel: str):
    """
    Righe della chat tra gli ALTRI due partecipanti (canale di cui il viewer non
    fa parte), etichettate col colore reale del mittente. Sola lettura.
    Usato dal trattamento 'public' nella Decision finale.
    """
    try:
        from otree.models_concrete import ChatMessage  # type: ignore
    except Exception:
        return []
    try:
        rows = list(ChatMessage.objects_filter(channel=channel).order_by('timestamp'))
    except Exception:
        return []

    color_by_pid = {
        p.participant.id: COLOR_MAPPING[p.id_in_group]
        for p in player.group.get_players()
    }
    formatted = []
    for row in rows:
        speaker_color = color_by_pid.get(row.participant_id, '')
        speaker = f"{speaker_color} Participant" if speaker_color else 'Participant'
        formatted.append(dict(speaker=speaker, body=row.body or ''))
    return formatted


def _third_party_signal_display(code, receiver_color, other_color):
    """
    Testo del 'Final Message' inviato da un partner all'altro, visto da un terzo (viewer).
    receiver_color: colore del DESTINATARIO del messaggio (non il viewer).
    other_color: colore del VIEWER (my_color), referenziato da 'split_other'.
    Restituisce il testo con chiarimento parentetico dove necessario.
    """
    if code == 'split_you':
        return f"'I intend to support you.' <i>(i.e. {receiver_color})</i>"
    elif code == 'split_other':
        return f"'I intend to support {other_color}.' <i>(i.e. you)</i>"
    elif code == 'support_none':
        return "'I intend to support no one.'"
    return f"'{code}'" if code else ""


def _directed_signal_code(sender: Player, target_id: int):
    """Restituisce il codice del segnale che `sender` ha inviato al partner `target_id`."""
    side = get_partner_side(sender.id_in_group, target_id)
    if side == 'left':
        return sender.field_maybe_none('signal_left')
    if side == 'right':
        return sender.field_maybe_none('signal_right')
    return None


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
            p.treatment = get_treatment(p)
            p.chat_interrupted = False
            p.participant_left_ts = 0
            p.part1_payoff_eligible = True
            _ensure_visualized_order(p)
            p.participant.group_dropped = False
            p.participant.part1_payoff_eligible = True
            p.participant.vars['group_dropped'] = False
            p.participant.vars['part1_payoff_eligible'] = True
            # ID stabile della triade: coincide con il prefisso usato nei canali
            # chat, quindi permette di riunire scelte e messaggi in fase di
            # analisi. Va scritto qui e non solo al calcolo dei payoff, altrimenti
            # i gruppi che si interrompono a meta' resterebbero senza ID.
            p.participant.vars['part1_group_id'] = group.id
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
        visual = _visualized_partner_context(player)
        colors = _color_context(player)
        return dict(
            channel_left=visual['visual_left_channel'],
            channel_right=visual['visual_right_channel'],
            visual_left_color=visual['visual_left_color'],
            visual_right_color=visual['visual_right_color'],
            visual_left_nickname=visual['visual_left_nickname'],
            visual_right_nickname=visual['visual_right_nickname'],
            chat_timeout_seconds=get_page_timeout_seconds(player, Chat._CHAT_TIMEOUT),
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            reveal_third_party_chat=bool(treatment_flag(player, 'reveal_third_party_chat', False)),
            **_chat_status_payload(player),
            **colors,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        _set_player_left_chat(player)
        player.time_chat = save_time_value(player.time_on_page)
        logger.debug(f"Chat - time_chat saved: {player.time_chat}")
        # Record why the player left the Chat page (used by Signals page for context messages)
        if player.group.group_dropped:
            player.participant.vars['chat_advanced_reason'] = 'group_dropped'
        else:
            my_id = player.id_in_group
            left_id = get_left_partner_id(my_id)
            right_id = get_right_partner_id(my_id)
            statuses = _chat_left_state(player.group)
            if statuses.get(left_id) and statuses.get(right_id):
                player.participant.vars['chat_advanced_reason'] = 'partners_left'
            elif timeout_happened:
                player.participant.vars['chat_advanced_reason'] = 'timeout'
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
    form_fields = [
        'signal_left',
        'signal_right',
        'first_intention_selected',
        'time_on_page',
    ]
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
        # Chi è già su Signals fa da traino: se il terzo è rimasto indietro sulla
        # Chat mentre gli altri due l'hanno lasciata, lo accompagniamo avanti dal
        # contesto di un ALTRO partecipante (pattern sicuro, come su DataMappingWaitPage).
        _force_advance_lagging_chat_player(player.group)
        return {
            p.id_in_group: _chat_status_payload(p)
            for p in player.group.get_players()
        }

    @staticmethod
    def vars_for_template(player: Player):
        visual = _visualized_partner_context(player)
        colors = _color_context(player)
        reason = player.participant.vars.get('chat_advanced_reason', 'normal')
        return dict(
            visual_left_color=visual['visual_left_color'],
            visual_right_color=visual['visual_right_color'],
            visual_left_nickname=visual['visual_left_nickname'],
            visual_right_nickname=visual['visual_right_nickname'],
            visual_left_is_topological_left=visual['visual_left_is_topological_left'],
            chat_timeout=(reason == 'timeout'),
            chat_partners_left=(reason in ('group_dropped', 'partners_left')),
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            reveal_third_party_chat=bool(treatment_flag(player, 'reveal_third_party_chat', False)),
            **_chat_status_payload(player),
            **colors,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_signals = float(player.time_on_page)
        if timeout_happened:
            player.participant.vars['timeout_excluded'] = True
            player.group.interrupted_player_id = player.id_in_group
            _mark_group_dropped(player.group)
        else:
            set_control_questions_failed(player, 'intro', failed=False)
        logger.debug(f"Signals - time_signals saved: {player.time_signals}")
        
        if not timeout_happened:
            player.participant.vars['signal_left'] = player.signal_left
            player.participant.vars['signal_right'] = player.signal_right
            player.participant.vars['signal_inactive'] = player.signal_inactive


class ExperimentTerminated(Page):
    """Pagina mostrata se il partecipante ha fallito le control questions."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina se il partecipante ha fallito le CQ o è andato in timeout."""
        return has_failed_control_questions(player, 'intro') or _is_inactive_excluded(player) or player.participant.vars.get('timeout_excluded')

    @staticmethod
    def vars_for_template(player):
        return dict(
            is_inactive=_is_inactive_excluded(player) or player.participant.vars.get('timeout_excluded', False)
        )

    @staticmethod
    def js_vars(player):
        is_inactive = _is_inactive_excluded(player)
        is_timeout = player.participant.vars.get('timeout_excluded')
        if is_timeout or is_inactive:
            link = player.session.config.get('dropoutlink_inactive', '').strip()
        else:
            link = player.session.config.get('dropoutlink_cq', '').strip()
        return dict(completionlink=link)
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_experiment_terminated = save_time_value(player.time_on_page)
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class DataMappingWaitPage(WaitPage):
    """Sync and map participant.vars (intro chat/signals) to group received_* fields."""
    template_name = 'bargaining_tdl_main/DataMappingWaitPage.html'
    title_text = "Please wait"
    body_text = "Waiting for other participants."

    @staticmethod
    def is_displayed(player):
        # group_dropped_inactive arriva ~102s dopo la disconnessione
        # (12s di conferma + 90s di finestra di riconnessione), mentre
        # timeout_excluded arriva solo allo scadere del timer di pagina
        # dell'assente, cioe' a 300s. Senza il primo dei due i due superstiti
        # restavano fermi qui per oltre tre minuti in piu', a gruppo gia'
        # dichiarato caduto e con le scelte casuali gia' scritte.
        if player.participant.vars.get('group_dropped_inactive'):
            return False
        return not has_failed_control_questions(player, 'intro') and not player.participant.vars.get('timeout_excluded')

    @staticmethod
    def vars_for_template(player):
        _evaluate_dropout(player.group)
        _advance_interrupted_player_to_waitpage(
            player.group, player.participant._index_in_pages
        )
        _force_advance_lagging_chat_player(player.group)
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
            
        visual = _visualized_partner_context(player)
        
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
        visual_left_received_display = (
            received_left_display if visual['visual_left_is_topological_left'] else received_right_display
        )
        visual_right_received_display = (
            received_right_display if visual['visual_left_is_topological_left'] else received_left_display
        )
        # ===== Trattamento 'public': rivelazione della coppia di terzi =====
        # Canale tra i due partner (di cui il viewer NON fa parte).
        reveal_third_party = bool(treatment_flag(player, 'reveal_third_party_chat', False))
        third_chat_rows = []
        third_signal_from_left = ""
        third_signal_from_right = ""
        if reveal_third_party:
            # L'id del gruppo era una variabile locale del metodo prima che la
            # logica dell'ordine visivo fosse estratta: va riletto qui.
            group_id = player.group.id
            third_a, third_b = sorted((left_id, right_id))
            channel_third = f"{group_id}_{third_a}_{third_b}"
            # ChatMessage.channel è salvato con lo stesso prefisso che oTree
            # applica nel tag template {% chat %} (vedi otree/chat.py); qui
            # interroghiamo il DB direttamente quindi dobbiamo replicarlo.
            prefixed_channel_third = f"{player.session.id}-{C.NAME_IN_URL}-{channel_third}"
            third_chat_rows = _third_party_chat_rows(player, prefixed_channel_third)

            left_partner = player.group.get_player_by_id(left_id)
            right_partner = player.group.get_player_by_id(right_id)
            # Final Message inviato dal partner left al partner right e viceversa.
            third_signal_from_left = _third_party_signal_display(
                _directed_signal_code(left_partner, right_id),
                colors['right_partner_color'],
                colors['my_color'],
            )
            third_signal_from_right = _third_party_signal_display(
                _directed_signal_code(right_partner, left_id),
                colors['left_partner_color'],
                colors['my_color'],
            )
        option_labels = {
            'Left': f"I will support {colors['left_partner_color']}",
            'Right': f"I will support {colors['right_partner_color']}",
            'NoOne': "I will support no one",
        }
        option_ids = {
            'Left': 'dc_left',
            'Right': 'dc_right',
            'NoOne': 'dc_no_one',
        }
        order = _decision_option_order(player)

        options = [
            {
                'value': value,
                'id': option_ids[value],
                'label': option_labels[value],
                'details': '',
            }
            for value in order
        ]
        current_choice = player.field_maybe_none('decision_choice') or ''
        for opt in options:
            opt['checked'] = (opt['value'] == current_choice)

        return dict(
            channel_left=visual['visual_left_channel'],
            channel_right=visual['visual_right_channel'],
            visual_left_color=visual['visual_left_color'],
            visual_right_color=visual['visual_right_color'],
            visual_left_nickname=visual['visual_left_nickname'],
            visual_right_nickname=visual['visual_right_nickname'],
            received_signal_left_display=received_left_display,
            received_signal_right_display=received_right_display,
            visual_left_received_display=visual_left_received_display,
            visual_right_received_display=visual_right_received_display,
            reveal_third_party_chat=reveal_third_party,
            third_chat_rows=third_chat_rows,
            third_signal_from_left=third_signal_from_left,
            third_signal_from_right=third_signal_from_right,
            signals_expired=bool(player.signal_inactive == 99),
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            decision_options=options,
            current_decision_choice=player.field_maybe_none('decision_choice') or '',
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
            import random
            player.decision_choice = random.choice(['Left', 'Right', 'NoOne'])
            player.decision_inactive = 99
            player.part1_payoff_eligible = False
            player.participant.vars['part1_payoff_eligible'] = False
            player.participant.vars['timeout_excluded'] = True


class PostDecisionConfidence(Page):
    """
    Nuova pagina post-Decision: mostra le chat in sola lettura e raccoglie
    la scala di confidenza (1-5) sulla capacità persuasiva della conversazione.
    Visibile solo ai partecipanti attivi (decision_inactive != 99).
    """
    form_model = 'player'
    form_fields = [
        'guess_left_confidence',
        'guess_right_confidence',
        'guess_left_choice',
        'guess_right_choice',
        'time_on_page',
    ]

    @staticmethod
    def is_displayed(player):
        """Stessa condizione di Results: solo partecipanti attivi che hanno deciso."""
        return (
            not has_failed_control_questions(player, 'intro')
            and not _is_inactive_excluded(player)
            and player.decision_inactive != 99
        )

    @staticmethod
    def vars_for_template(player: Player):
        my_id = player.id_in_group
        partners = TOPOLOGY[my_id]
        left_id = partners['left']
        right_id = partners['right']

        visual = _visualized_partner_context(player)

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
        visual_left_received_display = (
            received_left_display if visual['visual_left_is_topological_left'] else received_right_display
        )
        visual_right_received_display = (
            received_right_display if visual['visual_left_is_topological_left'] else received_left_display
        )

        reveal_third_party = bool(treatment_flag(player, 'reveal_third_party_chat', False))
        third_chat_rows = []
        third_signal_from_left = ""
        third_signal_from_right = ""
        if reveal_third_party:
            # L'id del gruppo era una variabile locale del metodo prima che la
            # logica dell'ordine visivo fosse estratta: va riletto qui.
            group_id = player.group.id
            third_a, third_b = sorted((left_id, right_id))
            channel_third = f"{group_id}_{third_a}_{third_b}"
            prefixed_channel_third = f"{player.session.id}-{C.NAME_IN_URL}-{channel_third}"
            third_chat_rows = _third_party_chat_rows(player, prefixed_channel_third)

            left_partner = player.group.get_player_by_id(left_id)
            right_partner = player.group.get_player_by_id(right_id)
            third_signal_from_left = _third_party_signal_display(
                _directed_signal_code(left_partner, right_id),
                colors['right_partner_color'],
                colors['my_color'],
            )
            third_signal_from_right = _third_party_signal_display(
                _directed_signal_code(right_partner, left_id),
                colors['left_partner_color'],
                colors['my_color'],
            )

        # ── Belief elicitation: opzioni radio dinamiche ──────────────────────
        # LEFT partner: dal suo POV, 'Right' = ha supportato il viewer, 'Left' = ha supportato right_partner
        guess_left_options = [
            {'value': 'NoOne', 'label': 'No one',                           'id': 'guess_left_NoOne'},
            {'value': 'Right', 'label': 'You',                              'id': 'guess_left_You'},
            {'value': 'Left',  'label': colors['right_partner_color'],      'id': 'guess_left_Other'},
        ]
        # RIGHT partner: dal suo POV, 'Left' = ha supportato il viewer, 'Right' = ha supportato left_partner
        guess_right_options = [
            {'value': 'NoOne', 'label': 'No one',                           'id': 'guess_right_NoOne'},
            {'value': 'Left',  'label': 'You',                              'id': 'guess_right_You'},
            {'value': 'Right', 'label': colors['left_partner_color'],       'id': 'guess_right_Other'},
        ]

        return dict(
            channel_left=visual['visual_left_channel'],
            channel_right=visual['visual_right_channel'],
            visual_left_color=visual['visual_left_color'],
            visual_right_color=visual['visual_right_color'],
            visual_left_nickname=visual['visual_left_nickname'],
            visual_right_nickname=visual['visual_right_nickname'],
            visual_left_is_topological_left=visual['visual_left_is_topological_left'],
            received_signal_left_display=received_left_display,
            received_signal_right_display=received_right_display,
            visual_left_received_display=visual_left_received_display,
            visual_right_received_display=visual_right_received_display,
            reveal_third_party_chat=reveal_third_party,
            third_chat_rows=third_chat_rows,
            third_signal_from_left=third_signal_from_left,
            third_signal_from_right=third_signal_from_right,
            convincingness_scale=range(1, 6),
            guess_left_options=guess_left_options,
            guess_right_options=guess_right_options,
            reconnect_window_seconds=C.CHAT_RECONNECT_WINDOW_SECONDS,
            **_chat_status_payload(player),
            **colors,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_post_decision_confidence = save_time_value(player.time_on_page)
        # Questa pagina non ha timeout (rimosso in b7e646a): non esiste
        # timeout_submission ne' get_timeout_seconds, quindi ci si passa solo
        # inviando il form. La scelta qui e' sempre deliberata per costruzione
        # e non serve nessuna esclusione.

        logger.debug(
            f"PostDecisionConfidence - time saved: {player.time_post_decision_confidence}"
        )


class InactivityGoodbyeMain(Page):
    template_name = 'bargaining_tdl_main/ExperimentTerminated.html'
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def is_displayed(player):
        return _is_inactive_excluded(player) or player.decision_inactive == 99 or not player.part1_payoff_eligible or player.participant.vars.get('timeout_excluded')

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.session.config.get('dropoutlink_inactive', '').strip()
        )

    @staticmethod
    def vars_for_template(player):
        return dict(
            is_inactive=True
        )

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return []





class Results(Page):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    # CASO 8: Rimosso il timeout da Results
    
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return not has_failed_control_questions(player, 'intro') and not _is_inactive_excluded(player) and player.decision_inactive != 99

    @staticmethod
    def vars_for_template(player: Player):
        colors = _color_context(player)
        choice = player.decision_choice
        if choice == 'Left':
            choice_display = f"I will support {colors['left_partner_color']}"
        elif choice == 'Right':
            choice_display = f"I will support {colors['right_partner_color']}"
        else:
            choice_display = "I will support no one"
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
    PostDecisionConfidence,
    Results,
    InactivityGoodbyeMain
]
