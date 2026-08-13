import random
import secrets
import time

from otree.api import (  # type: ignore
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as cu,
    ExtraModel,
    Page,
    WaitPage,
)
from otree.common import get_models_module  # type: ignore

# Patch oTree bot: response.url può essere URL object (Starlette/httpx), unquote() richiede str;
# client.post() in nuove versioni richiede keyword (data=, follow_redirects=).
try:
    from urllib.parse import unquote, urlsplit
    import otree.bots.bot as _bot  # type: ignore

    _fget = _bot.ParticipantBot.response.fget

    def _response_setter(self, response):
        url = response.url
        if not isinstance(url, str):
            url = str(url)
        self.url = unquote(url)
        self.path = urlsplit(self.url).path
        self._response = response
        self.html = response.content.decode('utf-8')

    _bot.ParticipantBot.response = property(_fget, _response_setter)

    _orig_submit = _bot.ParticipantBot.submit

    def _submit(self, submission):
        post_data = submission.post_data
        pretty_post_data = _bot.bot_prettify_post_data(post_data)
        log_string = 'Submit ' + self.path
        if pretty_post_data:
            log_string += ', {}'.format(pretty_post_data)
        if post_data.get('must_fail'):
            log_string += ', SubmissionMustFail'
        if post_data.get('timeout_happened'):
            log_string += ', timeout_happened'
        _bot.logger.info(log_string)
        try:
            self.response = self.client.post(
                self.url, data=post_data, follow_redirects=True
            )
        except TypeError:
            self.response = self.client.post(
                self.url, post_data, allow_redirects=True
            )

    _bot.ParticipantBot.submit = _submit

    # client.get() in nuove versioni usa follow_redirects invece di allow_redirects
    from otree import common as _otree_common  # type: ignore

    _orig_open_start_url = _bot.ParticipantBot.open_start_url
    def _open_start_url(self):
        start_url = _otree_common.participant_start_url(self.participant_code)
        try:
            self.response = self.client.get(start_url, follow_redirects=True)
        except TypeError:
            self.response = self.client.get(start_url, allow_redirects=True)
    _bot.ParticipantBot.open_start_url = _open_start_url

    def _on_wait_page(self):
        if not _bot.is_wait_page(self.response):
            return False
        try:
            self.response = self.client.get(self.url, follow_redirects=True)
        except TypeError:
            self.response = self.client.get(self.url, allow_redirects=True)
        return _bot.is_wait_page(self.response)
    _bot.ParticipantBot.on_wait_page = _on_wait_page
except Exception:
    pass

from bargaining_tdl_common import (  # type: ignore
    save_time_value,
    get_page_timeout_seconds,
    timeout_submission_with_time,
    check_control_questions_intro,
    set_control_questions_failed,
    has_failed_control_questions,
    get_max_attempts,
    get_control_questions_attempts,
    increment_control_questions_attempts,
    has_passed_control_questions,
    set_control_questions_passed,
    get_logger,
    get_active_treatments,
    get_treatment,
    treatment_flag,
)

logger = get_logger('intro')

doc = """
Bargaining Game (Part 1: Individual Tasks)
Instructions -> Chat and Intentions
Data is saved to participant.vars for the next app.
"""


def _skip_intro_control_questions(player):
    return bool(player.session.config.get('skip_intro_control_questions', False))


def _require_prolific_id(player):
    return bool(player.session.config.get('require_prolific_id', True))


def _mark_inactive_exclusion(player, reason):
    player.participant.inactive_excluded = True
    player.participant.inactive_excluded_reason = reason
    player.participant.vars['inactive_excluded'] = True
    player.participant.vars['inactive_excluded_reason'] = reason


def _is_inactive_excluded(player):
    return bool(player.participant.vars.get('inactive_excluded', False))


class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_intro'
    PLAYERS_PER_GROUP = None  # No groups in this app; grouping happens in bargaining_tdl_main
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Prolific PID passed through ?participant_label=... on the start URL
    prolific_id = models.StringField(blank=True)
    prolific_pid_url = models.StringField(blank=True)
    prolific_study_id = models.StringField(blank=True)
    prolific_session_id = models.StringField(blank=True)

    # Audit RCT. Copia persistente dell'assegnazione conservata anche per chi
    # non supera le control questions.
    assigned_treatment = models.StringField(blank=True)
    allocation_slot = models.IntegerField(initial=0)
    allocation_block = models.IntegerField(initial=0)
    allocation_attempt = models.IntegerField(initial=0)
    assignment_timestamp = models.FloatField(initial=0)
    assignment_status = models.StringField(initial='unassigned')
    is_replacement = models.BooleanField(initial=False)

    # Drafts (Simulated Chat) — not in active page_sequence but kept for consistency
    draft_history_left = models.LongStringField(blank=True)
    draft_history_right = models.LongStringField(blank=True)
    
    # Intentions — not in active page_sequence; signals are collected in bargaining_tdl_main
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
    
    # Track which chat/intention was selected first
    first_intention_selected = models.StringField(
        choices=[
            ['left', 'Left'],
            ['right', 'Right']
        ],
        blank=True,
        label="Which intention was selected first"
    )
    
    # Control Questions. La risposta di Example 2 dipende dal trattamento:
    # TDL=(0,0,0), private No-DWL=(12,0,0).
    example1_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would you earn?"
    )
    example1_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would Red earn?"
    )
    example1_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would Blue earn?"
    )
    
    example2_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would you earn?"
    )
    example2_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would Red earn?"
    )
    example2_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would Blue earn?"
    )
    
    example3_earnings_you = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would you earn?"
    )
    example3_earnings_left = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would Red earn?"
    )
    example3_earnings_right = models.StringField(
        choices=[
            ['6', '$6'],
            ['3', '$3'],
            ['0', '$0'],
        ],
        widget=widgets.RadioSelect,
        label="How much would Blue earn?"
    )

    # Time tracking fields (in seconds)
    time_welcome = models.FloatField(initial=0)
    time_instructions_part1 = models.FloatField(initial=0)
    time_control_questions = models.FloatField(initial=0)
    time_goodbye = models.FloatField(initial=0)

    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)


class TreatmentSlot(ExtraModel):
    """Slot RCT che deve essere riempito da un partecipante CQ-eligible."""

    subsession = models.Link(Subsession)
    slot_number = models.IntegerField()
    block_number = models.IntegerField()
    position_in_block = models.IntegerField()
    treatment = models.StringField()
    status = models.StringField(initial='available')
    assigned_participant_code = models.StringField(blank=True)
    assigned_at = models.FloatField(initial=0)
    returned_at = models.FloatField(initial=0)
    filled_at = models.FloatField(initial=0)
    replacement_count = models.IntegerField(initial=0)


class TreatmentAssignment(ExtraModel):
    """Storico immutabile dei tentativi di riempimento degli slot RCT."""

    player = models.Link(Player)
    slot_number = models.IntegerField()
    block_number = models.IntegerField()
    treatment = models.StringField()
    attempt_number = models.IntegerField()
    is_replacement = models.BooleanField(initial=False)
    status = models.StringField(initial='assigned')
    assigned_at = models.FloatField(initial=0)
    resolved_at = models.FloatField(initial=0)
    resolution_reason = models.StringField(blank=True)


def build_randomized_schedule(active_treatments, total_slots, seed):
    """
    Costruisce blocchi permutati bilanciati.

    Ogni blocco contiene 3 slot per trattamento: con tre arm produce blocchi
    da 9 e una triade completa per ciascun arm.
    """
    treatments = list(active_treatments)
    if not treatments:
        treatments = ['private']

    rng = random.Random(int(seed))
    block_template = [
        treatment
        for treatment in treatments
        for _ in range(3)
    ]
    schedule = []
    while len(schedule) < total_slots:
        block = list(block_template)
        rng.shuffle(block)
        schedule.extend(block)
    return schedule[:total_slots]


def creating_session(subsession):
    """Pre-genera schedule RCT auditabile quando nasce la sessione."""
    configured_seed = subsession.session.config.get('randomization_seed')
    seed = int(configured_seed) if configured_seed is not None else secrets.randbits(63)
    active_treatments = get_active_treatments(subsession.session)
    total_slots = len(subsession.get_players())
    schedule = build_randomized_schedule(active_treatments, total_slots, seed)

    subsession.session.vars['randomization_seed'] = seed
    subsession.session.vars['randomization_schedule'] = schedule
    subsession.session.vars['randomization_block_size'] = 3 * len(active_treatments)

    block_size = max(1, 3 * len(active_treatments))
    for index, treatment in enumerate(schedule, start=1):
        TreatmentSlot.create(
            subsession=subsession,
            slot_number=index,
            block_number=((index - 1) // block_size) + 1,
            position_in_block=((index - 1) % block_size) + 1,
            treatment=treatment,
        )


def _locked_slot_query(player):
    """
    Query con row lock.

    PostgreSQL serializza claim/release concorrenti tra processi web. SQLite
    ignora FOR UPDATE, ma oTree serializza le richieste nel processo locale.
    """
    return TreatmentSlot.objects_filter(
        subsession=player.subsession
    ).with_for_update()


def assign_treatment_slot(player):
    """
    Assegna slot dopo validazione Welcome/PID.

    Priorità a slot restituiti da CQ failure; altrimenti usa prossimo slot
    della schedule randomizzata. Operazione idempotente su refresh/re-submit.
    """
    assigned_treatment = player.field_maybe_none('assigned_treatment')
    if assigned_treatment:
        player.participant.vars['treatment'] = assigned_treatment
        return assigned_treatment

    query = _locked_slot_query(player).filter(
        TreatmentSlot.status == 'available'
    )
    slot = query.filter(
        TreatmentSlot.replacement_count > 0
    ).order_by(
        TreatmentSlot.returned_at,
        TreatmentSlot.slot_number,
    ).first()
    if slot is None:
        slot = query.order_by(TreatmentSlot.slot_number).first()
    if slot is None:
        raise RuntimeError(
            'No RCT allocation slots are available. Create a larger session.'
        )

    now = time.time()
    is_replacement = slot.replacement_count > 0
    attempt_number = slot.replacement_count + 1
    slot.status = 'assigned'
    slot.assigned_participant_code = player.participant.code
    slot.assigned_at = now

    player.assigned_treatment = slot.treatment
    player.allocation_slot = slot.slot_number
    player.allocation_block = slot.block_number
    player.allocation_attempt = attempt_number
    player.assignment_timestamp = now
    player.assignment_status = 'assigned'
    player.is_replacement = is_replacement

    player.participant.vars.update({
        'treatment': slot.treatment,
        'allocation_slot': slot.slot_number,
        'allocation_block': slot.block_number,
        'allocation_attempt': attempt_number,
        'assignment_timestamp': now,
        'assignment_status': 'assigned',
        'is_replacement': is_replacement,
    })

    TreatmentAssignment.create(
        player=player,
        slot_number=slot.slot_number,
        block_number=slot.block_number,
        treatment=slot.treatment,
        attempt_number=attempt_number,
        is_replacement=is_replacement,
        assigned_at=now,
    )
    return slot.treatment


def _active_assignment_query(player):
    return TreatmentAssignment.objects_filter(
        player=player,
        status='assigned',
    ).with_for_update()


def confirm_treatment_slot(player):
    """Conferma definitivamente slot quando CQ viene superata."""
    if player.assignment_status == 'passed':
        return
    if player.assignment_status != 'assigned':
        return

    slot = _locked_slot_query(player).filter(
        TreatmentSlot.slot_number == player.allocation_slot
    ).first()
    if (
        slot is None
        or slot.status != 'assigned'
        or slot.assigned_participant_code != player.participant.code
    ):
        raise RuntimeError('RCT slot ownership mismatch while confirming CQ pass.')

    now = time.time()
    slot.status = 'filled'
    slot.filled_at = now
    player.assignment_status = 'passed'
    player.participant.vars['assignment_status'] = 'passed'

    assignment = _active_assignment_query(player).first()
    if assignment:
        assignment.status = 'passed'
        assignment.resolved_at = now
        assignment.resolution_reason = 'control_questions_passed'


def release_treatment_slot(player, reason):
    """Restituisce slot alla testa logica della coda dopo CQ failure/timeout."""
    if player.assignment_status == 'failed':
        return
    if player.assignment_status != 'assigned':
        return

    slot = _locked_slot_query(player).filter(
        TreatmentSlot.slot_number == player.allocation_slot
    ).first()
    if (
        slot is None
        or slot.status != 'assigned'
        or slot.assigned_participant_code != player.participant.code
    ):
        raise RuntimeError('RCT slot ownership mismatch while releasing CQ slot.')

    now = time.time()
    slot.status = 'available'
    slot.assigned_participant_code = ''
    slot.assigned_at = 0
    slot.returned_at = now
    slot.replacement_count += 1

    player.assignment_status = 'failed'
    player.participant.vars['assignment_status'] = 'failed'
    player.participant.vars['allocation_failure_reason'] = reason

    assignment = _active_assignment_query(player).first()
    if assignment:
        assignment.status = 'failed'
        assignment.resolved_at = now
        assignment.resolution_reason = reason


def custom_export_rct_assignments(players):
    """Audit completo: una riga per ogni assegnazione, incluse CQ failure."""
    yield [
        'session_code',
        'participant_code',
        'prolific_id',
        'slot_number',
        'block_number',
        'treatment',
        'attempt_number',
        'is_replacement',
        'status',
        'assigned_at',
        'resolved_at',
        'resolution_reason',
    ]
    allowed_player_ids = {player.id for player in players}
    for assignment in TreatmentAssignment.filter():
        player = assignment.player
        if player.id not in allowed_player_ids:
            continue
        yield [
            player.session.code,
            player.participant.code,
            player.field_maybe_none('prolific_id') or '',
            assignment.slot_number,
            assignment.block_number,
            assignment.treatment,
            assignment.attempt_number,
            assignment.is_replacement,
            assignment.status,
            assignment.assigned_at,
            assignment.resolved_at,
            assignment.resolution_reason,
        ]


def custom_export_rct_slots(players):
    """Audit schedule: slot pianificati, riempiti e ancora disponibili."""
    yield [
        'session_code',
        'randomization_seed',
        'slot_number',
        'block_number',
        'position_in_block',
        'treatment',
        'status',
        'assigned_participant_code',
        'replacement_count',
        'assigned_at',
        'returned_at',
        'filled_at',
    ]
    allowed_subsession_ids = {player.subsession.id for player in players}
    for slot in TreatmentSlot.filter():
        if slot.subsession.id not in allowed_subsession_ids:
            continue
        yield [
            slot.subsession.session.code,
            slot.subsession.session.vars.get('randomization_seed'),
            slot.slot_number,
            slot.block_number,
            slot.position_in_block,
            slot.treatment,
            slot.status,
            slot.assigned_participant_code,
            slot.replacement_count,
            slot.assigned_at,
            slot.returned_at,
            slot.filled_at,
        ]


# PAGES

class Welcome(Page):
    """General Instructions (moved from bargaining_tdl_welcome)."""
    form_model = 'player'
    form_fields = [
        'time_on_page',
        'prolific_pid_url',
        'prolific_study_id',
        'prolific_session_id',
    ]

    @staticmethod
    def vars_for_template(player):
        return dict(
            require_prolific_id=_require_prolific_id(player),
            participation_fee=cu(player.session.config.get('participation_fee', 1.50)),
            prolific_pid_initial=(
                (player.participant.label or '').strip()
                or (player.field_maybe_none('prolific_pid_url') or '').strip()
            ),
        )

    @staticmethod
    def prolific_pid_url_error_message(player, value):
        if not _require_prolific_id(player):
            return
        has_pid = bool((value or '').strip() or (player.participant.label or '').strip())
        if not has_pid:
            return 'Please enter your Prolific participant ID.'

    @staticmethod
    def before_next_page(player, timeout_happened):
        time_value = save_time_value(player.time_on_page)
        player.time_welcome = time_value
        player.participant.vars['time_welcome'] = time_value
        prolific_pid = (player.prolific_pid_url or '').strip() or (player.participant.label or '').strip()
        if not prolific_pid and not _require_prolific_id(player):
            prolific_pid = f'local-{player.participant.code}'
        player.prolific_id = prolific_pid
        player.participant.prolific_id = prolific_pid
        player.participant.prolific_study_id = (player.prolific_study_id or '').strip()
        player.participant.prolific_session_id = (player.prolific_session_id or '').strip()
        player.participant.vars['prolific_id'] = player.participant.prolific_id
        player.participant.vars['prolific_study_id'] = player.participant.prolific_study_id
        player.participant.vars['prolific_session_id'] = player.participant.prolific_session_id
        # Assegna solo dopo form/PID valido: preview e semplice GET non
        # consumano uno slot della randomizzazione.
        assign_treatment_slot(player)
        logger.debug(f"Welcome - time_welcome saved: {player.time_welcome}")


class InstructionsPart1(Page):
    form_model = 'player'
    form_fields = ['time_on_page']

    @staticmethod
    def vars_for_template(player):
        # Gancio per istruzioni specifiche del trattamento (testo a cura del prof.).
        return dict(
            treatment=get_treatment(player),
            reveal_third_party_chat=bool(treatment_flag(player, 'reveal_third_party_chat', False)),
            no_deadweight_loss=bool(treatment_flag(player, 'no_deadweight_loss', False)),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part1 = save_time_value(player.time_on_page)
        logger.debug(f"InstructionsPart1 - time_instructions_part1 saved: {player.time_instructions_part1}")
        if _skip_intro_control_questions(player):
            # Temporary fast-path for manual testing of chat flow.
            set_control_questions_passed(player, 'intro', passed=True)
            set_control_questions_failed(player, 'intro', failed=False)
            confirm_treatment_slot(player)

def create_control_questions_class(attempt_number):
    """
    Factory function che crea dinamicamente una classe ControlQuestions per un tentativo specifico.
    
    Args:
        attempt_number: Numero del tentativo (1-based)
    
    Returns:
        Classe Page per oTree
    """
    class_name = f'ControlQuestionsAttempt{attempt_number}'
    
    class ControlQuestionsPage(Page):
        template_name = 'bargaining_tdl_intro/ControlQuestions.html'
        form_model = 'player'
        preserve_unsubmitted_inputs = True
        _CONTROL_QUESTIONS_TIMEOUT = 300
        # Risposte SBAGLIATE intenzionalmente: se timeout_happened non fosse
        # rilevato correttamente, le risposte errate garantiscono comunque il
        # fallimento. La guard primaria rimane `if timeout_happened` in
        # before_next_page. Questo è un secondo livello di sicurezza.
        timeout_submission = timeout_submission_with_time(
            _CONTROL_QUESTIONS_TIMEOUT,
            # Valori intenzionalmente errati per ogni trattamento:
            # Ex1 corretta=(0,0,0); Ex2 corretta=(0 o 6, 0, 0); Ex3 corretta=(0,3,3)
            example1_earnings_you='6',   # corretta: '0'
            example1_earnings_left='6',  # corretta: '0'
            example1_earnings_right='6', # corretta: '0'
            example2_earnings_you='3',   # corretta: '0' (TDL/Public) o '6' (no-DWL) → '3' sempre errata
            example2_earnings_left='6',  # corretta: '0'
            example2_earnings_right='6', # corretta: '0'
            example3_earnings_you='6',   # corretta: '0'
            example3_earnings_left='6',  # corretta: '3'
            example3_earnings_right='6', # corretta: '3'
        )

        @staticmethod
        def get_timeout_seconds(player):
            return get_page_timeout_seconds(player, ControlQuestionsPage._CONTROL_QUESTIONS_TIMEOUT)
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
            'time_on_page'
        ]

        @staticmethod
        def is_displayed(player):
            """
            Mostra questa pagina solo se:
            - Non ha ancora passato le control questions E
            - Non ha ancora fallito definitivamente E
            - È il tentativo corretto (current_attempts == attempt_number - 1)
            """
            if _skip_intro_control_questions(player):
                return False
            if has_passed_control_questions(player, 'intro'):
                return False
            
            if has_failed_control_questions(player, 'intro'):
                return False
            
            current_attempts = get_control_questions_attempts(player, 'intro')
            # Mostra solo quando è il turno di questo tentativo
            return current_attempts == (attempt_number - 1)

        @staticmethod
        def vars_for_template(player):
            max_attempts = get_max_attempts(player.session)
            current_attempts = get_control_questions_attempts(player, 'intro')
            attempts_remaining = max_attempts - current_attempts
            
            return {
                'example1_scenario': (
                    "Imagine that you are Green: you support no one, Red supports Blue, and Blue supports no one."
                ),
                'example2_scenario': (
                    "Imagine that you are Green: you support no one, Red supports you, and Blue supports you."
                ),
                'example3_scenario': (
                    "Imagine that you are Green: you support Red, Red supports Blue, and Blue supports Red."
                ),
                'max_attempts': max_attempts,
                'current_attempt': attempt_number,
                'attempts_remaining': max_attempts - attempt_number + 1,
                'is_first_attempt': attempt_number == 1,
                'cq_errors': player.participant.vars.get('intro_cq_errors', []),
                'cq_errors_str': ", ".join(player.participant.vars.get('intro_cq_errors', [])),
                # Serve al partial _instructions_content.html per mostrare il testo
                # di visibilità messaggi corretto per il trattamento.
                'reveal_third_party_chat': bool(treatment_flag(player, 'reveal_third_party_chat', False)),
                'no_deadweight_loss': bool(treatment_flag(player, 'no_deadweight_loss', False)),
            }

        @staticmethod
        def before_next_page(player, timeout_happened):
            """Gestisce la logica di retry per le control questions."""
            player.time_control_questions = save_time_value(player.time_on_page)
            logger.debug(f"ControlQuestions Attempt {attempt_number} - time_control_questions saved: {player.time_control_questions}")

            if timeout_happened:
                _mark_inactive_exclusion(player, f'intro_control_questions_attempt_{attempt_number}_timeout')
                set_control_questions_failed(player, 'intro', failed=True)
                release_treatment_slot(
                    player,
                    f'intro_control_questions_attempt_{attempt_number}_timeout',
                )
                logger.debug(f"ControlQuestions Attempt {attempt_number} - timeout, marking participant as inactive")
                return
            
            # Verifica le risposte
            is_correct = check_control_questions_intro(player)
            
            # Identify which examples are wrong
            errors = []
            # Example 1: tutti i trattamenti → (0, 0, 0)
            if not (player.example1_earnings_you == "0" and player.example1_earnings_left == "0" and player.example1_earnings_right == "0"):
                errors.append("Example 1")
            # Example 2: no-DWL → you=$6; TDL/Public → you=$0; Red=$0; Blue=$0
            expected_example2_you = (
                "6" if treatment_flag(player, 'no_deadweight_loss', False) else "0"
            )
            if not (
                player.example2_earnings_you == expected_example2_you
                and player.example2_earnings_left == "0"
                and player.example2_earnings_right == "0"
            ):
                errors.append("Example 2")
            # Example 3: tutti i trattamenti → you=$0, Red=$3, Blue=$3
            if not (player.example3_earnings_you == "0" and player.example3_earnings_left == "3" and player.example3_earnings_right == "3"):
                errors.append("Example 3")
                
            player.participant.vars['intro_cq_errors'] = errors
            
            max_attempts = get_max_attempts(player.session)
            current_attempts = increment_control_questions_attempts(player, 'intro')
            
            if is_correct:
                # Risposte corrette: imposta passed e resetta attempts
                set_control_questions_passed(player, 'intro', passed=True)
                set_control_questions_failed(player, 'intro', failed=False)
                confirm_treatment_slot(player)
                logger.debug(f"ControlQuestions Attempt {attempt_number} - All answers correct on attempt {current_attempts}")
            else:
                # Risposte sbagliate
                logger.debug(f"ControlQuestions Attempt {attempt_number} - Incorrect answers on attempt {current_attempts}/{max_attempts}")
                
                if current_attempts >= max_attempts:
                    # Raggiunto il massimo numero di tentativi: imposta failed
                    set_control_questions_failed(player, 'intro', failed=True)
                    release_treatment_slot(
                        player,
                        f'intro_control_questions_failed_after_{current_attempts}_attempts',
                    )
                    logger.debug(f"ControlQuestions Attempt {attempt_number} - Max attempts reached, setting failed flag")
    
    # Imposta il nome della classe per il debug
    ControlQuestionsPage.__name__ = class_name
    ControlQuestionsPage.__qualname__ = class_name
    
    return ControlQuestionsPage


# Crea fino a 5 istanze di ControlQuestions (supporta fino a 5 tentativi)
# Ogni istanza gestirà un tentativo specifico
ControlQuestionsAttempt1 = create_control_questions_class(1)
ControlQuestionsAttempt2 = create_control_questions_class(2)
ControlQuestionsAttempt3 = create_control_questions_class(3)
ControlQuestionsAttempt4 = create_control_questions_class(4)
ControlQuestionsAttempt5 = create_control_questions_class(5)

class Goodbye(Page):
    """Pagina di saluto che termina l'esperimento per il partecipante."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
        return has_failed_control_questions(player, 'intro')
    
    @staticmethod
    def vars_for_template(player):
        return dict(
            is_inactive=_is_inactive_excluded(player)
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_goodbye = save_time_value(player.time_on_page)
        logger.debug(f"Goodbye - time_goodbye saved: {player.time_goodbye}")

    @staticmethod
    def js_vars(player):
        link = player.session.config.get(
            'dropoutlink_inactive' if _is_inactive_excluded(player) else 'dropoutlink_cq',
            ''
        ).strip()
        return dict(
            dropoutlink=link,
        )
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []


page_sequence = [
    Welcome,
    InstructionsPart1,
    ControlQuestionsAttempt1,
    ControlQuestionsAttempt2,
    ControlQuestionsAttempt3,
    ControlQuestionsAttempt4,
    ControlQuestionsAttempt5,
    Goodbye,
]
