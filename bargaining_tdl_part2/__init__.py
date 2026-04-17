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
    check_control_questions_part2,
    set_control_questions_failed,
    has_failed_control_questions,
    get_max_attempts,
    get_control_questions_attempts,
    increment_control_questions_attempts,
    has_passed_control_questions,
    set_control_questions_passed,
    get_main_group_player,
    get_participant_role_in_group,
    get_player_color,
    get_partner_colors,
    get_id_from_role,
    get_partner_side,
    get_logger,
)

logger = get_logger('part2')

doc = """
Bargaining Game (Part 2: Matching Probability List - MPL)
Genera 12 MPL questions per ogni partecipante basandosi sui dati della Parte 1.
"""

# ============================================================================
# TESTI OBBLIGATORI - NON MODIFICARE
# Fonte: Sezione "⚠️ SEZIONE CRITICA: TESTI ORIGINALI OBBLIGATORI"
# ============================================================================

# Testi delle Opzioni di Scelta Parte 1 (Sezione 📄 4)
# Usiamo le nuove etichette descrittive che corrispondono a quelle in bargaining_tdl_main
# Mapping basato su EVENT_TO_DECISION per determinare quale etichetta usare

# Decision labels use a {target_color} placeholder resolved at runtime per player
DECISION_LABEL_LEFT_TPL = "I would like to divide the $12 equally with the {target_color} player"
DECISION_LABEL_RIGHT_TPL = "I would like to divide the $12 equally with the {target_color} player"
DECISION_LABEL_BOTH = "I would like to divide the $12 equally among all the members of the group"

# EVENT_TO_TEXT_CODE maps event codes to short codes ('left'/'right'/'both')
# so we can resolve the actual color-based text at runtime.
EVENT_TO_TEXT_CODE = {
    'EB1': 'right',   # B divide with C only
    'EB2': 'left',    # B divide with A only
    'EB3': 'both',    # B divide among all three
    'EC1': 'left',    # C divide with B only
    'EC2': 'right',   # C divide with A only
    'EC3': 'both',    # C divide among all three
    'EA1': 'right',   # A divide with C only (per B) o A divide with B only (per C)
    'EA2': 'left',    # A divide with B only (per B) o A divide with C only (per C)
    'EA3': 'both',    # A divide among all three
}


def _resolve_event_text(event_code, left_color, right_color):
    """Resolve an event code to its display text using player-specific colors."""
    code = EVENT_TO_TEXT_CODE.get(event_code)
    if code == 'left':
        return DECISION_LABEL_LEFT_TPL.format(target_color=left_color)
    elif code == 'right':
        return DECISION_LABEL_RIGHT_TPL.format(target_color=right_color)
    elif code == 'both':
        return DECISION_LABEL_BOTH
    return ""


# Struttura Testo Option 1 (Sezione 📄 5) — now uses {target_label} for the color name
OPTION1_SINGLE_TEMPLATE = "You win $5 if {target_label} chose \"{event_text}\" (and nothing otherwise)."
OPTION1_COMPOSITE_TEMPLATE = "You win $5 if {target_label} chose \"{event_text_1}\" or \"{event_text_2}\" (and nothing otherwise)."


def _format_signal_for_reminder(signal_code, target_color, other_color):
    """Convert a short signal code (split_you/split_other/split_both) to display text."""
    if signal_code == 'split_you':
        return f"I wish to split the $12 equally with you only, the {target_color} player."
    elif signal_code == 'split_other':
        return f"I wish to split the $12 equally with the other player only, the {other_color} player."
    elif signal_code == 'split_both':
        return f"I wish to split the $12 equally with both you and the {other_color} player."
    return signal_code or ""

# Struttura Testo Option 2 (Sezione 📄 6)
OPTION2_TEXT = "You win $5 with the following probability (and nothing otherwise)."

# Testo Reminder Parte 1 (Sezione 📄 3)
REMINDER_TEMPLATE = """We remind you of the following information regarding what you and {target_label} have declared to each other:
<br>
<br>
You said: {you_said}
<br>
<br>
{target_label} said: {target_said}"""

# Testi UI (Sezione 📄 9)
UI_OPTION1_HEADER = "OPTION 1"
UI_OPTION2_HEADER = "OPTION 2"
UI_COLUMN1_LABEL = "1"
UI_COLUMN2_LABEL = "2"
UI_OK_BUTTON_TEXT = "OK"

# Liste Probabilità (Sezione 📄 7)
# Single Event: valori specifici per single event
PROBABILITIES_SINGLE_EVENT = [0, 1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 85, 100]
# Composite Event: valori specifici per composite event
PROBABILITIES_COMPOSITE_EVENT = [0, 20, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 93, 95, 97, 98, 99, 100]

# Costanti generali
PRIZE_AMOUNT = "$5"
NUM_QUESTIONS_PER_PARTICIPANT = 12

# ============================================================================
# CLASSI OTREE
# ============================================================================

class C(BaseConstants):
    NAME_IN_URL = 'bargaining_tdl_part2'
    PLAYERS_PER_GROUP = None  # Non serve gruppo per questa parte
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Campi per le risposte MPL (switch values) - nomenclatura basata su eventi
    # Left player events (L)
    EL1_switch_value = models.IntegerField(blank=True)   # Event Left 1
    EL2_switch_value = models.IntegerField(blank=True)   # Event Left 2
    EL3_switch_value = models.IntegerField(blank=True)   # Event Left 3
    EL12_switch_value = models.IntegerField(blank=True) # Event Left 12 (composite)
    EL23_switch_value = models.IntegerField(blank=True) # Event Left 23 (composite)
    EL31_switch_value = models.IntegerField(blank=True) # Event Left 31 (composite)
    
    # Right player events (R)
    ER1_switch_value = models.IntegerField(blank=True)   # Event Right 1
    ER2_switch_value = models.IntegerField(blank=True)   # Event Right 2
    ER3_switch_value = models.IntegerField(blank=True)   # Event Right 3
    ER12_switch_value = models.IntegerField(blank=True) # Event Right 12 (composite)
    ER23_switch_value = models.IntegerField(blank=True) # Event Right 23 (composite)
    ER31_switch_value = models.IntegerField(blank=True) # Event Right 31 (composite)
    
    # Opzionale: salvare anche le scelte complete per validazione (JSON)
    # Usiamo una nomenclatura basata sugli eventi per coerenza
    EL1_choices = models.LongStringField(blank=True)
    EL2_choices = models.LongStringField(blank=True)
    EL3_choices = models.LongStringField(blank=True)
    EL12_choices = models.LongStringField(blank=True)
    EL23_choices = models.LongStringField(blank=True)
    EL31_choices = models.LongStringField(blank=True)
    ER1_choices = models.LongStringField(blank=True)
    ER2_choices = models.LongStringField(blank=True)
    ER3_choices = models.LongStringField(blank=True)
    ER12_choices = models.LongStringField(blank=True)
    ER23_choices = models.LongStringField(blank=True)
    ER31_choices = models.LongStringField(blank=True)
    
    # Control Questions for Part 2
    control_question_1 = models.StringField(
        choices=[
            ["nothing", "I don't win anything."],
            ["5", "$5."],
            ["dont_know", "I don't know."]
        ],
        label="Question 1: What would be the payment for Part 2?"
    )
    
    control_question_2 = models.StringField(
        choices=[
            ["nothing", "I don't win anything."],
            ["5", "$5."],
            ["dont_know", "I don't know."]
        ],
        label="Question 2: What would be the payment for Part 2?"
    )
    
    # Tracking della randomizzazione MPL
    # Ordine dei player: 'left_first' o 'right_first'
    mpl_player_order = models.StringField(blank=True)
    # Ordine dei tipi di domande per left: 'single_first' o 'composite_first'
    mpl_left_type_order = models.StringField(blank=True)
    # Ordine dei tipi di domande per right: 'single_first' o 'composite_first'
    mpl_right_type_order = models.StringField(blank=True)
    # Ordine finale delle domande (JSON con lista di question_num nell'ordine visualizzato)
    mpl_question_order = models.LongStringField(blank=True)
    
    # Time tracking fields (in seconds)
    time_instructions_part2 = models.FloatField(initial=0)
    time_payment_instruction_part2 = models.FloatField(initial=0)
    time_control_questions_part2 = models.FloatField(initial=0)
    time_thank_you_part2 = models.FloatField(initial=0)
    time_mpl_intro_first = models.FloatField(initial=0)
    time_mpl_intro_second = models.FloatField(initial=0)
    # Time tracking for each MPL question (1-12)
    time_mpl_question_1 = models.FloatField(initial=0)
    time_mpl_question_2 = models.FloatField(initial=0)
    time_mpl_question_3 = models.FloatField(initial=0)
    time_mpl_question_4 = models.FloatField(initial=0)
    time_mpl_question_5 = models.FloatField(initial=0)
    time_mpl_question_6 = models.FloatField(initial=0)
    time_mpl_question_7 = models.FloatField(initial=0)
    time_mpl_question_8 = models.FloatField(initial=0)
    time_mpl_question_9 = models.FloatField(initial=0)
    time_mpl_question_10 = models.FloatField(initial=0)
    time_mpl_question_11 = models.FloatField(initial=0)
    time_mpl_question_12 = models.FloatField(initial=0)
    time_results_part2 = models.FloatField(initial=0)
    
    # Hidden field for JavaScript to populate
    time_on_page = models.FloatField(initial=0, blank=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# get_participant_role_in_group è ora importato da bargaining_tdl_common

def get_target_player_label(player: Player, target_code: str) -> str: # type: ignore
    """
    Converte un codice target (A/B/C) in "the <Color> player"
    basandosi sul ruolo del player corrente nel gruppo.
    """
    target_id = get_id_from_role(target_code)
    if target_id is None:
        return "the other player"  # type: ignore
    color = get_player_color(target_id)
    if color == 'Unknown':
        return "the other player"  # type: ignore
    return f"the {color} player"

def is_question_for_left_player(player: Player, target_code: str) -> bool:
    """
    Determina se una domanda è relativa al partner 'left' nella topology interna.

    Returns:
        True se il target occupa la posizione 'left' nella topology del player corrente.
    """
    role = get_participant_role_in_group(player)
    if role is None:
        return False
    current_id = get_id_from_role(role)
    target_id = get_id_from_role(target_code)
    if current_id is None or target_id is None:
        return False
    return get_partner_side(current_id, target_id) == 'left'

def get_first_player_label(player: Player) -> str:
    """Returns color-based label of the partner shown first in MPL questions."""
    generate_mpl_questions(player)
    colors = get_partner_colors(player)
    player_order = player.field_maybe_none('mpl_player_order')
    if player_order == 'left_first':
        return f"the {colors['left_partner_color']} player"
    elif player_order == 'right_first':
        return f"the {colors['right_partner_color']} player"
    else:
        all_questions = generate_mpl_questions(player)
        if all_questions and len(all_questions) > 0:
            target_code = all_questions[0].get('target_code')
            if target_code:
                return get_target_player_label(player, target_code) or "the other player"
        return "the other player"

def get_second_player_label(player: Player) -> str:
    """Returns color-based label of the partner shown second in MPL questions."""
    generate_mpl_questions(player)
    colors = get_partner_colors(player)
    player_order = player.field_maybe_none('mpl_player_order')
    if player_order == 'left_first':
        return f"the {colors['right_partner_color']} player"
    elif player_order == 'right_first':
        return f"the {colors['left_partner_color']} player"
    else:
        all_questions = generate_mpl_questions(player)
        if all_questions and len(all_questions) > 6:
            target_code = all_questions[6].get('target_code')
            if target_code:
                return get_target_player_label(player, target_code) or "the other player"
        return "the other player"

def generate_option1_single_event(
    player: Player,
    target_code: str, # type: ignore
    event_code: str
) -> str:
    """
    Genera il testo di Option 1 per un Single Event.
    """
    target_label = get_target_player_label(player, target_code)
    if target_label is None:
        return ""

    colors = get_partner_colors(player)
    left_color = colors['left_partner_color']
    right_color = colors['right_partner_color']
    event_text = _resolve_event_text(event_code, left_color, right_color)
    if not event_text:
        return ""

    return OPTION1_SINGLE_TEMPLATE.format(
        target_label=target_label,
        event_text=event_text,
    )

def generate_option1_composite_event(
    player: Player,
    target_code: str, # type: ignore
    event_codes: list[str] # type: ignore
) -> str:
    """
    Genera il testo di Option 1 per un Composite Event (OR logico).
    
    Un composite event rappresenta l'unione logica (OR) di due eventi.
    Il testo generato usa etichette colore lato UI, mentre internamente
    left/right resta una coordinata topologica.
    
    Args:
        player: Player corrente (da bargaining_tdl_part2)
        target_code: 'A', 'B', o 'C' - Il participant che ha fatto la scelta
        event_codes: Lista di esattamente 2 codici evento (es. ['EB2', 'EB3'])
                    Rappresenta l'unione logica: evento1 OR evento2
    
    Returns:
        str: Testo completo di Option 1, o stringa vuota se:
             - event_codes non ha esattamente 2 elementi
             - I dati non sono disponibili
    
    Example:
        >>> text = generate_option1_composite_event(player, 'B', ['EB2', 'EB1'])
        >>> text
        "You win $5 if the Green player chose ..."
    
    Note:
        - Richiede esattamente 2 event_codes
        - L'ordine degli eventi è preservato nel testo generato
    """
    target_label = get_target_player_label(player, target_code)
    if target_label is None:
        return ""
    
    if len(event_codes) != 2:
        return ""

    colors = get_partner_colors(player)
    left_color = colors['left_partner_color']
    right_color = colors['right_partner_color']
    event_text_1 = _resolve_event_text(event_codes[0], left_color, right_color)
    event_text_2 = _resolve_event_text(event_codes[1], left_color, right_color)
    
    if not event_text_1 or not event_text_2:
        return ""

    return OPTION1_COMPOSITE_TEMPLATE.format(
        target_label=target_label,
        event_text_1=event_text_1,
        event_text_2=event_text_2,
    )

def load_part1_data_for_mpl(player: Player, target_code: str) -> dict: # type: ignore
    """
    Carica i dati della Parte 1 relativi a un target participant specifico.
    
    ⚠️ VINCOLO: SOLO LETTURA - Non modifica i dati di intro/main.
    
    Questa funzione recupera i dati necessari per generare il reminder nelle
    domande MPL. I dati vengono letti da participant.vars (salvati in intro)
    e dal Player model di main (decision_choice).
    
    La funzione gestisce la topology complessa del gruppo per determinare
    quale signal è stato inviato a chi, basandosi sulla posizione relativa
    dei player nel gruppo.
    
    Args:
        player: Player corrente (da bargaining_tdl_part2)
        target_code: 'A', 'B', o 'C' (il participant di cui si sta chiedendo la scelta)
    
    Returns:
        Dict con:
        - 'you_said': str - Intenzione dichiarata dal player corrente al target
                          (es. "I wish to split the $ 12 equally with you only.")
        - 'target_said': str - Intenzione dichiarata dal target al player corrente
        - 'target_decision': str - Scelta finale del target in Part 1
                                ('Left', 'Right', o 'Both')
    
    Example:
        >>> data = load_part1_data_for_mpl(player, 'B')
        >>> data['you_said']
        "I wish to split the $ 12 equally with you only."
        >>> data['target_decision']
        'Both'
    
    Note:
        - Restituisce dict con valori vuoti se i dati non sono disponibili
        - Gestisce automaticamente la topology del gruppo (P1-P2-P3)
    """
    # Recupera il player corrente dal gruppo di main
    main_player = get_main_group_player(player)
    if main_player is None:
        return {
            'you_said': '',
            'target_said': '',
            'target_decision': ''
        }
    
    # Recupera il ruolo del player corrente
    current_role = get_participant_role_in_group(player)
    if current_role is None:
        return {
            'you_said': '',
            'target_said': '',
            'target_decision': ''
        }
    
    # Recupera il gruppo di main
    main_group = main_player.group
    if main_group is None:
        return {
            'you_said': '',
            'target_said': '',
            'target_decision': ''
        }
    
    # Determina l'id_in_group del target
    target_id = get_id_from_role(target_code)
    if target_id is None:
        return {
            'you_said': '',
            'target_said': '',
            'target_decision': ''
        }
    
    # Recupera il target player dal gruppo di main
    target_player = main_group.get_player_by_id(target_id)
    if target_player is None:
        return {
            'you_said': '',
            'target_said': '',
            'target_decision': ''
        }
    
    current_id = main_player.id_in_group
    target_side_for_current = get_partner_side(current_id, target_id)

    # Recupera "you_said" - intenzione del player corrente al target
    # (internamente signal_left/signal_right sono coordinate topologiche)
    you_said = ""
    if target_side_for_current == 'left':
        you_said = player.participant.vars.get('signal_left', '')
    elif target_side_for_current == 'right':
        you_said = player.participant.vars.get('signal_right', '')
    
    # Recupera "target_said" - intenzione del target al player corrente
    # coordinate inverse nella topologia: se current è left per target, target usa signal_left.
    target_said = ""
    target_vars = target_player.participant.vars
    current_side_for_target = get_partner_side(target_id, current_id)
    if current_side_for_target == 'left':
        target_said = target_vars.get('signal_left', '')
    elif current_side_for_target == 'right':
        target_said = target_vars.get('signal_right', '')
    
    # Recupera "target_decision" - scelta finale del target
    # Dati dal campo decision_choice del target player in main
    target_decision = target_player.decision_choice if hasattr(target_player, 'decision_choice') else ''
    
    return {
        'you_said': you_said,
        'target_said': target_said,
        'target_decision': target_decision
    }

def get_event_description(player: Player, target_code: str, event_codes: list[str]) -> str:
    """
    Genera la descrizione testuale dell'evento basandosi sulla tabella degli eventi.
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C' (il participant target)
        event_codes: Lista di codici evento (es. ['EB1'] o ['EB2', 'EB3'])
    
    Returns:
        Stringa con la descrizione dell'evento (es. "Participant B divide equally with Participant A only")
    """
    role = get_participant_role_in_group(player)
    if role is None or not event_codes:
        return ""
    
    # Mapping dei codici evento alle descrizioni in base al ruolo
    # La tabella mostra le descrizioni per ogni ruolo
    event_descriptions = {
        'A': {
            # Single events
            'EB2': "Participant B divide equally with Participant A only",
            'EC2': "Participant C divide equally with Participant A only",
            'EB1': "Participant B divide equally with Participant C only",
            'EC1': "Participant C divide equally with Participant B only",
            'EB3': "Participant B divide equally among all three participants",
            'EC3': "Participant C divide equally among all three participants",
            # Composite events
            ('EB2', 'EB1'): "Participant B divide equally with Participant A only or Participant B divide equally with Participant C only",
            ('EC2', 'EC1'): "Participant C divide equally with Participant A only or Participant C divide equally with Participant B only",
            ('EB1', 'EB3'): "Participant B divide equally with Participant C only or Participant B divide equally among all three participants",
            ('EC1', 'EC3'): "Participant C divide equally with Participant B only or Participant C divide equally among all three participants",
            ('EB3', 'EB2'): "Participant B divide equally among all three participants or Participant B divide equally with Participant A only",
            ('EC3', 'EC2'): "Participant C divide equally among all three participants or Participant C divide equally with Participant A only",
        },
        'B': {
            # Single events
            'EA2': "Participant A divide equally with Participant B only",
            'EC2': "Participant C divide equally with Participant B only",
            'EA1': "Participant A divide equally with Participant C only",
            'EC1': "Participant C divide equally with Participant A only",
            'EA3': "Participant A divide equally among all three participants",
            'EC3': "Participant C divide equally among all three participants",
            # Composite events
            ('EA2', 'EA1'): "Participant A divide equally with Participant B only or Participant A divide equally with Participant C only",
            ('EC2', 'EC1'): "Participant C divide equally with Participant B only or Participant C divide equally with Participant A only",
            ('EA1', 'EA3'): "Participant A divide equally with Participant C only or Participant A divide equally among all three participants",
            ('EC1', 'EC3'): "Participant C divide equally with Participant A only or Participant C divide equally among all three participants",
            ('EA3', 'EA2'): "Participant A divide equally among all three participants or Participant A divide equally with Participant B only",
            ('EC3', 'EC2'): "Participant C divide equally among all three participants or Participant C divide equally with Participant B only",
        },
        'C': {
            # Single events
            'EA2': "Participant A divide equally with Participant C only",
            'EB2': "Participant B divide equally with Participant C only",
            'EA1': "Participant A divide equally with Participant B only",
            'EB1': "Participant B divide equally with Participant A only",
            'EA3': "Participant A divide equally among all three participants",
            'EB3': "Participant B divide equally among all three participants",
            # Composite events
            ('EA2', 'EA1'): "Participant A divide equally with Participant C only or Participant A divide equally with Participant B only",
            ('EB2', 'EB1'): "Participant B divide equally with Participant C only or Participant B divide equally with Participant A only",
            ('EA1', 'EA3'): "Participant A divide equally with Participant B only or Participant A divide equally among all three participants",
            ('EB1', 'EB3'): "Participant B divide equally with Participant A only or Participant B divide equally among all three participants",
            ('EA3', 'EA2'): "Participant A divide equally among all three participants or Participant A divide equally with Participant C only",
            ('EB3', 'EB2'): "Participant B divide equally among all three participants or Participant B divide equally with Participant C only",
        }
    }
    
    # Determina la chiave per il mapping
    if len(event_codes) == 1:
        # Single event
        key = event_codes[0]
    elif len(event_codes) == 2:
        # Composite event - usa tupla nell'ordine esatto (non sorted)
        key = tuple(event_codes)
    else:
        return ""
    
    # Cerca la descrizione nel mapping
    role_mapping = event_descriptions.get(role, {})  # type: ignore
    description = role_mapping.get(key, "")
    
    return description # type: ignore  # type: ignore  # type: ignore  # type: ignore

def get_event_field_name(player: Player, question_num: int) -> str:
    """
    Converte question_num in nome campo evento (EL1, ER1, EL12, ecc.).
    
    Mapping basato sulla tabella di mapping delle domande MPL:
    - E = Event
    - L/R = Left o Right (posizione relativa del target player)
    - Numero = numero evento (1, 2, 3 per single, 12, 23, 31 per composite)
    
    Args:
        player: Player corrente
        question_num: Numero della domanda (1-12)
    
    Returns:
        Nome del campo (es. 'EL1_switch_value', 'ER12_switch_value')
    """
    role = get_participant_role_in_group(player)
    if role is None:
        return f'mpl_question_{question_num}_switch_value'  # Fallback
    
    # Tabella di mapping question_num → (target_code, event_codes, event_number)
    # event_number: 1, 2, 3 per single, 12, 23, 31 per composite
    mapping = {
        'A': {
            1: ('B', ['EB2'], 1),      # B (left) divide with A only → EL1
            2: ('C', ['EC2'], 1),      # C (right) divide with A only → ER1
            3: ('B', ['EB1'], 2),      # B (left) divide with C only → EL2
            4: ('C', ['EC1'], 2),      # C (right) divide with B only → ER2
            5: ('B', ['EB3'], 3),      # B (left) divide among all three → EL3
            6: ('C', ['EC3'], 3),      # C (right) divide among all three → ER3
            7: ('B', ['EB2', 'EB1'], 12),  # B (left) composite → EL12
            8: ('C', ['EC2', 'EC1'], 12),  # C (right) composite → ER12
            9: ('B', ['EB1', 'EB3'], 23),   # B (left) composite → EL23
            10: ('C', ['EC1', 'EC3'], 23),  # C (right) composite → ER23
            11: ('B', ['EB3', 'EB2'], 31),  # B (left) composite → EL31
            12: ('C', ['EC3', 'EC2'], 31),  # C (right) composite → ER31
        },
        'B': {
            1: ('A', ['EA2'], 1),      # A (left) divide with B only → EL1
            2: ('C', ['EC2'], 1),      # C (right) divide with B only → ER1
            3: ('A', ['EA1'], 2),      # A (left) divide with C only → EL2
            4: ('C', ['EC1'], 2),      # C (right) divide with A only → ER2
            5: ('A', ['EA3'], 3),      # A (left) divide among all three → EL3
            6: ('C', ['EC3'], 3),      # C (right) divide among all three → ER3
            7: ('A', ['EA2', 'EA1'], 12),  # A (left) composite → EL12
            8: ('C', ['EC2', 'EC1'], 12),  # C (right) composite → ER12
            9: ('A', ['EA1', 'EA3'], 23),   # A (left) composite → EL23
            10: ('C', ['EC1', 'EC3'], 23),  # C (right) composite → ER23
            11: ('A', ['EA3', 'EA2'], 31),  # A (left) composite → EL31
            12: ('C', ['EC3', 'EC2'], 31),  # C (right) composite → ER31
        },
        'C': {
            1: ('A', ['EA2'], 1),      # A (left) divide with C only → EL1
            2: ('B', ['EB2'], 1),      # B (right) divide with C only → ER1
            3: ('A', ['EA1'], 2),      # A (left) divide with B only → EL2
            4: ('B', ['EB1'], 2),      # B (right) divide with A only → ER2
            5: ('A', ['EA3'], 3),      # A (left) divide among all three → EL3
            6: ('B', ['EB3'], 3),      # B (right) divide among all three → ER3
            7: ('A', ['EA2', 'EA1'], 12),  # A (left) composite → EL12
            8: ('B', ['EB2', 'EB1'], 12),  # B (right) composite → ER12
            9: ('A', ['EA1', 'EA3'], 23),   # A (left) composite → EL23
            10: ('B', ['EB1', 'EB3'], 23),  # B (right) composite → ER23
            11: ('A', ['EA3', 'EA2'], 31),  # A (left) composite → EL31
            12: ('B', ['EB3', 'EB2'], 31),  # B (right) composite → ER31
        }
    }
    
    if question_num not in mapping[role]:
        return f'mpl_question_{question_num}_switch_value'  # Fallback
    
    target_code, event_codes, event_number = mapping[role][question_num]
    
    # Determina se il target è left o right
    is_left = is_question_for_left_player(player, target_code)
    lr = 'L' if is_left else 'R'
    
    # Costruisci il nome del campo
    field_name = f'E{lr}{event_number}_switch_value'
    return field_name

def generate_mpl_questions(player: Player) -> list[dict]:
    """
    Genera la lista delle 12 domande MPL per il player con doppia randomizzazione.
    
    ⚠️ SOLO LETTURA - Non modifica i dati di intro/main.
    
    Questa funzione è il cuore del sistema MPL della Part 2. Genera dinamicamente
    le 12 domande basandosi sul ruolo del player nel gruppo (A, B, o C) e applica
    una doppia randomizzazione per evitare effetti di ordine.
    
    Randomizzazione implementata:
    1. Prima randomizzazione: ordine dei player (left first o right first)
       - Determina quale player (left o right) viene mostrato per primo
       - Basata su seed deterministica (hash del participant.id)
    2. Seconda randomizzazione: shuffle completo delle domande per ogni player
       - Le 6 domande per left player vengono mescolate
       - Le 6 domande per right player vengono mescolate
       - L'ordine finale è salvato in mpl_question_order per persistenza
    
    Struttura delle domande:
    - 6 domande per partner interno 'left' (3 single + 3 composite)
    - 6 domande per partner interno 'right' (3 single + 3 composite)
    - Ogni domanda è mappata a un evento specifico (EB1, EC2, etc.)
    
    Args:
        player: Player instance da bargaining_tdl_part2
    
    Returns:
        Lista di dict, ognuno con:
        - 'question_num': int (1-12) - numero originale della domanda (fisso)
        - 'display_order': int (1-12) - ordine di visualizzazione dopo randomizzazione
        - 'type': str - 'single' o 'composite'
        - 'target_code': str - 'A', 'B', o 'C' (il target della domanda)
        - 'event_codes': list[str] - Codici evento (es. ['EB1'] o ['EB2', 'EB3'])
        - 'option1_text': str - Testo completo di Option 1
        - 'reminder_text': str - Reminder con dati Parte 1
        - 'reminder_intro': str - Introduzione del reminder
        - 'you_said_text': str - Testo "You said: ..."
        - 'target_said_text': str - Testo "{target} said: ..."
        - 'probabilities': list[int] - Lista probabilità per Option 2
    
    Side Effects:
        - Salva mpl_player_order in player se non già presente
        - Salva mpl_question_order in player se non già presente
        - Genera dati se non già generati (idempotente)
    
    Example:
        >>> questions = generate_mpl_questions(player)
        >>> len(questions)
        12
        >>> questions[0]['type']
        'single'
        >>> questions[0]['display_order']
        1
    """
    import random
    import json
    
    role = get_participant_role_in_group(player)
    if role is None:
        return []
    
    # Definizione delle 12 domande per ogni ruolo
    # Mapping: i codici evento nel piano (EB1, EC1, etc.) devono essere mappati
    # agli eventi corretti in base al ruolo del player
    
    questions = []
    
    if role == 'A':
        # Participant A - 12 domande
        questions = [
            # Single Events (6)
            {'question_num': 1, 'type': 'single', 'target_code': 'B', 'event_codes': ['EB2']},  # B divide with A only
            {'question_num': 2, 'type': 'single', 'target_code': 'C', 'event_codes': ['EC2']},  # C divide with A only
            {'question_num': 3, 'type': 'single', 'target_code': 'B', 'event_codes': ['EB1']},  # B divide with C only
            {'question_num': 4, 'type': 'single', 'target_code': 'C', 'event_codes': ['EC1']},  # C divide with B only
            {'question_num': 5, 'type': 'single', 'target_code': 'B', 'event_codes': ['EB3']},  # B divide among all three
            {'question_num': 6, 'type': 'single', 'target_code': 'C', 'event_codes': ['EC3']},  # C divide among all three
            # Composite Events (6)
            {'question_num': 7, 'type': 'composite', 'target_code': 'B', 'event_codes': ['EB2', 'EB1']},  # EB12: B divide with A only OR B divide with C only
            {'question_num': 8, 'type': 'composite', 'target_code': 'C', 'event_codes': ['EC2', 'EC1']},  # EC12: C divide with A only OR C divide with B only
            {'question_num': 9, 'type': 'composite', 'target_code': 'B', 'event_codes': ['EB1', 'EB3']},  # EB23: B divide with C only OR B divide among all three
            {'question_num': 10, 'type': 'composite', 'target_code': 'C', 'event_codes': ['EC1', 'EC3']},  # EC23: C divide with B only OR C divide among all three
            {'question_num': 11, 'type': 'composite', 'target_code': 'B', 'event_codes': ['EB3', 'EB2']},  # EB31: B divide among all three OR B divide with A only
            {'question_num': 12, 'type': 'composite', 'target_code': 'C', 'event_codes': ['EC3', 'EC2']},  # EC31: C divide among all three OR C divide with A only
        ]
    elif role == 'B':
        # Participant B - 12 domande
        questions = [
            # Single Events (6)
            {'question_num': 1, 'type': 'single', 'target_code': 'A', 'event_codes': ['EA2']},  # A divide with B only
            {'question_num': 2, 'type': 'single', 'target_code': 'C', 'event_codes': ['EC2']},  # C divide with B only
            {'question_num': 3, 'type': 'single', 'target_code': 'A', 'event_codes': ['EA1']},  # A divide with C only
            {'question_num': 4, 'type': 'single', 'target_code': 'C', 'event_codes': ['EC1']},  # C divide with A only
            {'question_num': 5, 'type': 'single', 'target_code': 'A', 'event_codes': ['EA3']},  # A divide among all three
            {'question_num': 6, 'type': 'single', 'target_code': 'C', 'event_codes': ['EC3']},  # C divide among all three
            # Composite Events (6)
            {'question_num': 7, 'type': 'composite', 'target_code': 'A', 'event_codes': ['EA2', 'EA1']},  # EA12: A divide with B only OR A divide with C only
            {'question_num': 8, 'type': 'composite', 'target_code': 'C', 'event_codes': ['EC2', 'EC1']},  # EC12: C divide with B only OR C divide with A only
            {'question_num': 9, 'type': 'composite', 'target_code': 'A', 'event_codes': ['EA1', 'EA3']},  # EA23: A divide with C only OR A divide among all three
            {'question_num': 10, 'type': 'composite', 'target_code': 'C', 'event_codes': ['EC1', 'EC3']},  # EC23: C divide with A only OR C divide among all three
            {'question_num': 11, 'type': 'composite', 'target_code': 'A', 'event_codes': ['EA3', 'EA2']},  # EA31: A divide among all three OR A divide with B only
            {'question_num': 12, 'type': 'composite', 'target_code': 'C', 'event_codes': ['EC3', 'EC2']},  # EC31: C divide among all three OR C divide with B only
        ]
    elif role == 'C':
        # Participant C - 12 domande
        questions = [
            # Single Events (6)
            {'question_num': 1, 'type': 'single', 'target_code': 'A', 'event_codes': ['EA2']},  # A divide with C only
            {'question_num': 2, 'type': 'single', 'target_code': 'B', 'event_codes': ['EB2']},  # B divide with C only
            {'question_num': 3, 'type': 'single', 'target_code': 'A', 'event_codes': ['EA1']},  # A divide with B only
            {'question_num': 4, 'type': 'single', 'target_code': 'B', 'event_codes': ['EB1']},  # B divide with A only
            {'question_num': 5, 'type': 'single', 'target_code': 'A', 'event_codes': ['EA3']},  # A divide among all three
            {'question_num': 6, 'type': 'single', 'target_code': 'B', 'event_codes': ['EB3']},  # B divide among all three
            # Composite Events (6)
            {'question_num': 7, 'type': 'composite', 'target_code': 'A', 'event_codes': ['EA2', 'EA1']},  # EA12: A divide with C only OR A divide with B only
            {'question_num': 8, 'type': 'composite', 'target_code': 'B', 'event_codes': ['EB2', 'EB1']},  # EB12: B divide with C only OR B divide with A only
            {'question_num': 9, 'type': 'composite', 'target_code': 'A', 'event_codes': ['EA1', 'EA3']},  # EA23: A divide with B only OR A divide among all three
            {'question_num': 10, 'type': 'composite', 'target_code': 'B', 'event_codes': ['EB1', 'EB3']},  # EB23: B divide with A only OR B divide among all three
            {'question_num': 11, 'type': 'composite', 'target_code': 'A', 'event_codes': ['EA3', 'EA2']},  # EA31: A divide among all three OR A divide with C only
            {'question_num': 12, 'type': 'composite', 'target_code': 'B', 'event_codes': ['EB3', 'EB2']},  # EB31: B divide among all three OR B divide with C only
        ]
    
    # Arricchiamo ogni domanda con i dati necessari (prima della randomizzazione)
    enriched_questions = []
    for q in questions:
        # Genera il testo di Option 1
        if q['type'] == 'single':
            option1_text = generate_option1_single_event(
                player, q['target_code'], q['event_codes'][0]
            )
        else:  # composite
            option1_text = generate_option1_composite_event(
                player, q['target_code'], q['event_codes']
            )
        
        # Carica i dati della Parte 1 per il reminder
        part1_data = load_part1_data_for_mpl(player, q['target_code'])
        target_label = get_target_player_label(player, q['target_code'])
        colors = get_partner_colors(player)
        # Determine which color is the target and which is the "other"
        target_is_left = is_question_for_left_player(player, q['target_code'])
        if target_is_left:
            t_color = colors['left_partner_color']
            o_color = colors['right_partner_color']
        else:
            t_color = colors['right_partner_color']
            o_color = colors['left_partner_color']
        you_said_display = _format_signal_for_reminder(
            part1_data['you_said'], t_color, o_color
        )
        target_said_display = _format_signal_for_reminder(
            part1_data['target_said'], colors['my_color'], o_color
        )
        reminder_text = REMINDER_TEMPLATE.format(
            target_label=target_label or "the other participant",
            you_said=you_said_display,
            target_said=target_said_display,
        )
        reminder_intro = f"We remind you of the following information regarding what you and {target_label or 'the other participant'} have declared to each other:"
        you_said_text = f"You said: {you_said_display}"
        target_said_text = f"{target_label or 'the other participant'} said: {target_said_display}"
        
        # Determina le probabilità in base al tipo
        probabilities = PROBABILITIES_SINGLE_EVENT if q['type'] == 'single' else PROBABILITIES_COMPOSITE_EVENT
        
        enriched_questions.append({
            **q,
            'option1_text': option1_text,
            'reminder_text': reminder_text,
            'reminder_intro': reminder_intro,
            'you_said_text': you_said_text,
            'target_said_text': target_said_text,
            'probabilities': probabilities
        })
    
    # ========================================================================
    # DOPPIA RANDOMIZZAZIONE
    # ========================================================================
    
    # Se l'ordine è già stato generato, riutilizzalo
    question_order_json = player.field_maybe_none('mpl_question_order')
    if question_order_json:
        # L'ordine è già stato generato, ricostruisci la lista nell'ordine corretto
        question_order = json.loads(question_order_json)
        # Crea un dizionario per accesso rapido per question_num
        questions_dict = {q['question_num']: q for q in enriched_questions}
        # Ricostruisci la lista nell'ordine salvato
        final_questions = []
        for idx, question_num in enumerate(question_order, start=1):
            if question_num in questions_dict:
                q = questions_dict[question_num].copy()
                q['display_order'] = idx
                final_questions.append(q)
        return final_questions
    
    # Separare le domande per player (left vs right)
    left_questions = []
    right_questions = []
    
    for q in enriched_questions:
        if is_question_for_left_player(player, q['target_code']):
            left_questions.append(q)
        else:
            right_questions.append(q)
    
    # Prima randomizzazione: ordine dei player (left first o right first)
    # Usa un seed basato sul participant per garantire riproducibilità
    base_seed = hash(str(player.participant.id)) % (2**31)
    
    # Scegli quale gruppo mostrare per primo
    rng_player = random.Random(base_seed + 1000)
    player_order = rng_player.choice(['left_first', 'right_first'])
    
    # Shuffle di tutte le domande di ciascun gruppo (senza distinguere single/composite)
    rng_left_shuffle = random.Random(base_seed + 2000)
    rng_left_shuffle.shuffle(left_questions)
    
    rng_right_shuffle = random.Random(base_seed + 3000)
    rng_right_shuffle.shuffle(right_questions)
    
    # Costruisci l'ordine finale delle domande
    final_questions = []
    
    if player_order == 'left_first':
        # Prima tutte le domande del player left (già mescolate)
        final_questions.extend(left_questions)
        # Poi tutte le domande del player right (già mescolate)
        final_questions.extend(right_questions)
    else:  # right_first
        # Prima tutte le domande del player right (già mescolate)
        final_questions.extend(right_questions)
        # Poi tutte le domande del player left (già mescolate)
        final_questions.extend(left_questions)
    
    # Aggiungi display_order a ogni domanda (1-12)
    for idx, q in enumerate(final_questions, start=1):
        q['display_order'] = idx
    
    # Salva le informazioni di randomizzazione nel player
    player.mpl_player_order = player_order
    # Non servono più left_type_order e right_type_order (semplificato)
    player.mpl_left_type_order = ''  # Campo mantenuto per compatibilità ma non più usato
    player.mpl_right_type_order = ''  # Campo mantenuto per compatibilità ma non più usato
    player.mpl_question_order = json.dumps([q['question_num'] for q in final_questions])
    
    return final_questions


# ============================================================================
# PAYOFF CALCULATION FUNCTIONS (Part 2)
# ============================================================================

# Mapping Event Codes → Decision Choices
# Questo mapping definisce quale decision_choice ('Left', 'Right', 'Both') 
# corrisponde a ciascun evento, dal punto di vista del target player.
EVENT_TO_DECISION = {
    'EB1': 'Right',  # B divide with C only (internal right coordinate)
    'EB2': 'Left',   # B divide with A only (Share only with you = Left per A)
    'EB3': 'Both',   # B divide among all three
    'EC1': 'Left',   # C divide with B only (internal left coordinate)
    'EC2': 'Right',  # C divide with A only (Share only with you = Right per A)
    'EC3': 'Both',   # C divide among all three
    'EA1': 'Right',  # A divide with C only (internal right coordinate)
    'EA2': 'Left',   # A divide with B only (Share only with you = Left per B)
    'EA3': 'Both',   # A divide among all three
}

def map_event_code_to_decision_choice(event_code: str) -> str:
    """
    Mappa un codice evento a una decision choice ('Left', 'Right', 'Both').
    
    Args:
        event_code: Codice evento (es. 'EB1', 'EC2', 'EA3')
    
    Returns:
        Stringa con la decision choice attesa ('Left', 'Right', 'Both'), 
        o None se il codice evento non è valido
    """
    return EVENT_TO_DECISION.get(event_code)

def get_part2_player(player):
    """
    Recupera il player della Part 2 da un player di un'altra app (es. Part 3).
    
    Args:
        player: Player di qualsiasi app (es. Part 3)
    
    Returns:
        Player della Part 2 corrispondente allo stesso participant, o None se non trovato
    """
    try:
        from importlib import import_module
        
        # Importa l'app Part 2
        part2_app = import_module('bargaining_tdl_part2')
        Part2Player = part2_app.Player
        Part2Subsession = part2_app.Subsession
        
        # Ottieni la sessione corrente
        session = player.session
        
        # Cerchiamo il subsession dell'app Part 2
        part2_subsession = None
        for subsession in session.get_subsessions():
            if isinstance(subsession, Part2Subsession):
                part2_subsession = subsession
                break
        
        if part2_subsession is None:
            return None
        
        # Cerchiamo il player corrispondente (stesso participant)
        for part2_player in part2_subsession.get_players():
            if part2_player.participant == player.participant:
                return part2_player
        
        return None
    except Exception as e:
        import traceback
        logger.error(f"ERROR in get_part2_player: {e}", exc_info=True)
        traceback.print_exc()
        return None

def get_target_player_from_part1(player: Player, target_code: str):
    """
    Recupera il target player dalla Part 1.
    
    Args:
        player: Player corrente (Part 2)
        target_code: 'A', 'B', o 'C'
    
    Returns:
        Player della Part 1 corrispondente al target_code, o None se non trovato
    """
    from importlib import import_module
    main_app = import_module('bargaining_tdl_main')
    MainPlayer = main_app.Player
    MainSubsession = main_app.Subsession
    
    # Recupera il gruppo della Part 1
    main_player = get_main_group_player(player)
    if main_player is None:
        return None
    
    group = main_player.group
    
    # Mapping target_code → id_in_group
    target_id_map = {'A': 1, 'B': 2, 'C': 3}
    target_id = target_id_map.get(target_code)
    if target_id is None:
        return None
    
    # Trova il player con quell'id
    target_player = group.get_player_by_id(target_id)
    return target_player

def check_event_occurred_in_part1(player: Player, target_code: str, event_codes: list[str]) -> bool:
    """
    Verifica se l'evento (o almeno uno degli eventi per composite) è accaduto nella Part 1.
    
    Args:
        player: Player corrente (Part 2)
        target_code: 'A', 'B', o 'C' (chi ha fatto la scelta)
        event_codes: Lista di codici evento (es. ['EB1'] o ['EB2', 'EB3'])
    
    Returns:
        True se l'evento è accaduto, False altrimenti
    """
    # Recupera il target player dalla Part 1
    target_player = get_target_player_from_part1(player, target_code)
    if target_player is None:
        return False
    
    # Ottieni la scelta effettiva del target
    actual_choice = target_player.decision_choice  # 'Left', 'Right', o 'Both'
    if not actual_choice:
        return False
    
    # Per ogni evento, verifica se è accaduto
    for event_code in event_codes:
        expected_choice = map_event_code_to_decision_choice(event_code)
        if expected_choice == actual_choice:
            return True  # Almeno un evento è accaduto (OR logico per composite)
    
    return False

def calculate_part2_payoff(player) -> dict:
    """
    Calcola il payoff della Part 2 seguendo la logica specificata nel paper.
    
    Questa funzione implementa l'algoritmo di calcolo del payoff per la Part 2,
    che combina selezione casuale di una domanda MPL, estrazione di probabilità,
    e verifica di eventi della Part 1.
    
    Algoritmo:
    1. Selezione casuale: sceglie una domanda MPL tra 1-12
    2. Estrazione pr1: numero casuale 0-100
    3. Decisione Option 1 vs Option 2:
       - Se pr1 < switching_point → Option 1
         * Verifica se l'evento della domanda è accaduto in Part 1
         * Se sì: payoff = $5, altrimenti = $0
       - Se pr1 >= switching_point → Option 2
         * Estrae pr2 (0-99)
         * Se pr2 <= pr1: payoff = $5, altrimenti = $0
    
    Args:
        player: Player di qualsiasi app (es. Part 2 o Part 3).
                Se non è un player di Part 2, viene recuperato automaticamente
                tramite get_part2_player().
    
    Returns:
        Dict con tutti i dettagli del calcolo:
        - 'payoff': Currency - cu(5) o cu(0)
        - 'selected_question': int - Numero domanda selezionata (1-12)
        - 'switching_point': int - Valore di switching point della domanda
        - 'pr1': int - Probabilità estratta (0-100)
        - 'pr2': int - Probabilità estratta per Option 2 (0-99) o None
        - 'option_selected': str - 'Option 1' o 'Option 2'
        - 'event_occurred': bool - Se evento è accaduto (solo Option 1) o None
        - 'payoff_amount': int - 5 o 0
        - 'question_text': str - Testo della domanda
        - 'reminder_text': str - Reminder della domanda
        - 'target_code': str - Codice target ('A', 'B', 'C')
        - 'event_codes': list[str] - Codici evento
        - 'question_type': str - 'single' o 'composite'
        - 'error': str - Messaggio di errore se presente
    
    Side Effects:
        - Usa random.randint() per selezione ed estrazioni
        - Può chiamare get_part2_player() se necessario
        - Può chiamare check_event_occurred_in_part1()
    
    Example:
        >>> result = calculate_part2_payoff(player)
        >>> result['payoff']
        cu(5)
        >>> result['option_selected']
        'Option 1'
        >>> result['event_occurred']
        True
    """
    import random
    
    # Se il player non è di Part 2, recuperalo
    # Controlla se il player ha i campi MPL (è un player di Part 2)
    # Usa field_maybe_none per evitare TypeError quando il campo è None
    try:
        el1_value = player.field_maybe_none('EL1_switch_value')
        mpl1_value = player.field_maybe_none('mpl_question_1_switch_value')
        # Se almeno uno dei due campi esiste (non è None), è un player di Part 2
        is_part2_player = (el1_value is not None) or (mpl1_value is not None)
    except AttributeError:
        # Se il campo non esiste affatto, non è un player di Part 2
        is_part2_player = False
    
    if not is_part2_player:
        # Non è un player di Part 2, recuperalo
        part2_player = get_part2_player(player)
        if part2_player is None:
            # Se non troviamo il player di Part 2, ritorna payoff 0
            return {
                'payoff': cu(0),
                'selected_question': None,
                'switching_point': None,
                'pr1': None,
                'pr2': None,
                'option_selected': None,
                'event_occurred': None,
                'payoff_amount': 0,
                'error': 'Part 2 player not found'
            }
        player = part2_player
    
    # Step 1: Selezione casuale domanda (1-12)
    selected_question_num = random.randint(1, 12)
    
    questions = generate_mpl_questions(player)
    # Accesso per question_num originale (non per indice randomizzato)
    # Garantisce che metadati (target_code, event_codes) e switching_point
    # si riferiscano sempre alla stessa domanda originale numero N
    questions_by_num = {q['question_num']: q for q in questions}
    selected_question = questions_by_num.get(selected_question_num)
    
    # Recupera switching point usando il nuovo nome del campo
    event_field_name = get_event_field_name(player, selected_question_num)
    switching_point = player.field_maybe_none(event_field_name)
    
    if switching_point is None:
        # Se non c'è switching point, payoff = 0
        return {
            'payoff': cu(0),
            'selected_question': selected_question_num,
            'switching_point': None,
            'pr1': None,
            'pr2': None,
            'option_selected': None,
            'event_occurred': None,
            'payoff_amount': 0,
            'question_text': selected_question.get('option1_text', '') if selected_question else '',
            'reminder_text': selected_question.get('reminder_text', '') if selected_question else '',
            'target_code': selected_question.get('target_code', '') if selected_question else '',
            'event_codes': selected_question.get('event_codes', []) if selected_question else [],
            'question_type': selected_question.get('type', 'single') if selected_question else 'single'
        }
    
    # Step 2: Estrai pr1 (0-100)
    pr1 = random.randint(0, 100)
    
    # Step 3: Decisione Option 1 vs Option 2
    if pr1 < switching_point:
        # Scenario 2.1: Option 1 - Verifica evento Part 1
        target_code = selected_question['target_code']
        event_codes = selected_question['event_codes']
        
        # Verifica se evento è accaduto
        event_occurred = check_event_occurred_in_part1(player, target_code, event_codes)
        
        payoff_amount = 5 if event_occurred else 0
        
        return {
            'payoff': cu(payoff_amount),
            'selected_question': selected_question_num,
            'switching_point': switching_point,
            'pr1': pr1,
            'pr2': None,
            'option_selected': 'Option 1',
            'event_occurred': event_occurred,
            'payoff_amount': payoff_amount,
            'question_text': selected_question.get('option1_text', ''),
            'reminder_text': selected_question.get('reminder_text', ''),
            'target_code': target_code,
            'event_codes': event_codes,
            'question_type': selected_question.get('type', 'single')
        }
    else:
        # Scenario 2.2: Option 2 - Estrai pr2
        pr2 = random.randint(0, 99)
        
        # Se pr2 <= pr1, vinci $5
        payoff_amount = 5 if pr2 <= pr1 else 0
        
        return {
            'payoff': cu(payoff_amount),
            'selected_question': selected_question_num,
            'switching_point': switching_point,
            'pr1': pr1,
            'pr2': pr2,
            'option_selected': 'Option 2',
            'event_occurred': None,
            'payoff_amount': payoff_amount,
            'question_text': selected_question.get('option1_text', ''),
            'reminder_text': selected_question.get('reminder_text', ''),
            'target_code': selected_question.get('target_code', ''),
            'event_codes': selected_question.get('event_codes', []),
            'question_type': selected_question.get('type', 'single')
        }

# ============================================================================
# PAGES
# ============================================================================
# Base per Part 2: nasconde Group/ID in group nel debug (fase individuale, PLAYERS_PER_GROUP=None)
class BasePagePart2(Page):
    def _get_debug_tables(self, vars_for_template):
        tables = super()._get_debug_tables(vars_for_template)
        for t in tables:
            if getattr(t, 'title', None) == 'Basic info':
                t.rows = [(k, v) for k, v in t.rows if k not in ('Group', 'ID in group')]
                break
        return tables


class InstructionsPart2(BasePagePart2):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_instructions_part2 = save_time_value(player.time_on_page)

class PaymentInstructionPart2(BasePagePart2):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_payment_instruction_part2 = save_time_value(player.time_on_page)

def create_control_questions_part2_class(attempt_number):
    """
    Factory function che crea dinamicamente una classe ControlQuestionsPart2 per un tentativo specifico.
    
    Args:
        attempt_number: Numero del tentativo (1-based)
    
    Returns:
        Classe Page per oTree
    """
    class_name = f'ControlQuestionsPart2Attempt{attempt_number}'
    
    class ControlQuestionsPart2Page(BasePagePart2):
        template_name = 'bargaining_tdl_part2/ControlQuestionsPart2.html'
        form_model = 'player'
        preserve_unsubmitted_inputs = True
        form_fields = ['control_question_1', 'control_question_2', 'time_on_page']
        
        @staticmethod
        def is_displayed(player):
            """
            Mostra questa pagina solo se:
            - Non ha ancora passato le control questions E
            - Non ha ancora fallito definitivamente E
            - È il tentativo corretto (current_attempts == attempt_number - 1)
            """
            if has_passed_control_questions(player, 'part2'):
                return False
            
            if has_failed_control_questions(player, 'part2'):
                return False
            
            current_attempts = get_control_questions_attempts(player, 'part2')
            # Mostra solo quando è il turno di questo tentativo
            return current_attempts == (attempt_number - 1)

        @staticmethod
        def vars_for_template(player):
            max_attempts = get_max_attempts(player.session)
            
            return {
                'max_attempts': max_attempts,
                'current_attempt': attempt_number,
                'attempts_remaining': max_attempts - attempt_number,
                'is_first_attempt': attempt_number == 1,
            }
        
        @staticmethod
        def before_next_page(player, timeout_happened):
            """Gestisce la logica di retry per le control questions."""
            player.time_control_questions_part2 = save_time_value(player.time_on_page)
            logger.debug(f"ControlQuestionsPart2 Attempt {attempt_number} - time_control_questions_part2 saved: {player.time_control_questions_part2}")
            
            # Verifica le risposte
            is_correct = check_control_questions_part2(player)
            max_attempts = get_max_attempts(player.session)
            current_attempts = increment_control_questions_attempts(player, 'part2')
            
            if is_correct:
                # Risposte corrette: imposta passed e resetta attempts
                set_control_questions_passed(player, 'part2', passed=True)
                set_control_questions_failed(player, 'part2', failed=False)
                logger.debug(f"ControlQuestionsPart2 Attempt {attempt_number} - All answers correct on attempt {current_attempts}")
            else:
                # Risposte sbagliate
                logger.debug(f"ControlQuestionsPart2 Attempt {attempt_number} - Incorrect answers on attempt {current_attempts}/{max_attempts}")
                
                if current_attempts >= max_attempts:
                    # Raggiunto il massimo numero di tentativi: imposta failed
                    set_control_questions_failed(player, 'part2', failed=True)
                    logger.debug(f"ControlQuestionsPart2 Attempt {attempt_number} - Max attempts reached, setting failed flag")
    
    # Imposta il nome della classe per il debug
    ControlQuestionsPart2Page.__name__ = class_name
    ControlQuestionsPart2Page.__qualname__ = class_name
    
    return ControlQuestionsPart2Page


# Crea fino a 5 istanze di ControlQuestionsPart2 (supporta fino a 5 tentativi)
ControlQuestionsPart2Attempt1 = create_control_questions_part2_class(1)
ControlQuestionsPart2Attempt2 = create_control_questions_part2_class(2)
ControlQuestionsPart2Attempt3 = create_control_questions_part2_class(3)
ControlQuestionsPart2Attempt4 = create_control_questions_part2_class(4)
ControlQuestionsPart2Attempt5 = create_control_questions_part2_class(5)

class ThankYouPart2(BasePagePart2):
    """Pagina di saluto che termina l'esperimento per il partecipante."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
        return has_failed_control_questions(player, 'part2')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_thank_you_part2 = save_time_value(player.time_on_page)
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class MPLIntroFirstPlayer(BasePagePart2):
    """Pagina introduttiva prima delle MPL questions che spiega quale player viene mostrato per primo."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        if not has_passed_control_questions(player, 'part2'):
            return False
        # Assicurati che le domande siano state generate per determinare l'ordine
        generate_mpl_questions(player)
        return True
    
    @staticmethod
    def vars_for_template(player):
        """Prepara i dati per il template."""
        first_player_label = get_first_player_label(player)
        return {
            'first_player_label': first_player_label
        }
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_mpl_intro_first = save_time_value(player.time_on_page)

class MPLIntroSecondPlayer(BasePagePart2):
    """Pagina introduttiva dopo le prime 6 MPL questions che spiega quale player viene mostrato per secondo."""
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return has_passed_control_questions(player, 'part2')
    
    @staticmethod
    def vars_for_template(player):
        """Prepara i dati per il template."""
        second_player_label = get_second_player_label(player)
        return {
            'second_player_label': second_player_label
        }
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_mpl_intro_second = save_time_value(player.time_on_page)

class MPLQuestion(BasePagePart2):
    form_model = 'player'
    # form_fields sarà impostato dinamicamente per ogni istanza
    
    @staticmethod
    def vars_for_template(player):
        """Prepara i dati per il template."""
        import json
        
        # display_order è l'ordine di visualizzazione (1-12)
        display_order = player.participant.vars.get('current_display_order', 1)
        
        # Genera tutte le domande (questo genera anche l'ordine randomizzato se non esiste già)
        all_questions = generate_mpl_questions(player)
        
        # Debug: log informazioni utili
        if not all_questions:
            logger.warning(f"generate_mpl_questions returned empty list for player {player.id}")
            logger.debug(f"  - participant: {player.participant.id}")
            logger.debug(f"  - role: {get_participant_role_in_group(player)}")
            logger.debug(f"  - main_player: {get_main_group_player(player)}")
        
        # Trova la domanda corrente usando display_order
        current_question = None
        for q in all_questions:
            if q.get('display_order') == display_order:
                current_question = q
                break
        
        # Base return sempre con question_num (originale) e display_order e costanti UI
        question_num = current_question.get('question_num', display_order) if current_question else display_order
        base_return = {
            'question_num': display_order,  # Per il template, usiamo display_order come numero visualizzato
            'question_num_original': question_num,  # Numero originale per riferimento
            'UI_OPTION1_HEADER': UI_OPTION1_HEADER,
            'UI_OPTION2_HEADER': UI_OPTION2_HEADER,
            'UI_COLUMN1_LABEL': UI_COLUMN1_LABEL,
            'UI_COLUMN2_LABEL': UI_COLUMN2_LABEL,
            'UI_OK_BUTTON_TEXT': UI_OK_BUTTON_TEXT,
            'OPTION2_TEXT': OPTION2_TEXT,
        }
        
        if current_question is None:
            # Se non troviamo la domanda, restituiamo almeno question_num e valori di default
            # Ma proviamo a mostrare un messaggio di debug
            debug_info = f"DEBUG: No question found. Total questions: {len(all_questions)}, Display order: {display_order}"
            return {
                **base_return,
                'option1_text': debug_info,
                'reminder_text': '',
                'reminder_intro': '',
                'you_said_text': '',
                'target_said_text': '',
                'probabilities': PROBABILITIES_SINGLE_EVENT,  # Usa almeno le probabilità di default
                'probabilities_json': json.dumps(PROBABILITIES_SINGLE_EVENT),
                'question_type': 'single',  # Default
            }
        
        # Aggiungi i dati della domanda corrente
        question_type = current_question.get('type', 'single')
        probabilities = current_question.get('probabilities', PROBABILITIES_SINGLE_EVENT)
        
        # Salva il question_num originale in participant.vars per usarlo nel form
        player.participant.vars['current_question_num_original'] = question_num
        
        # Determina il nome del campo evento per il form
        event_field_name = get_event_field_name(player, question_num)  # type: ignore
        # Per le choices, usa lo stesso pattern ma con _choices invece di _switch_value
        event_choices_name = event_field_name.replace('_switch_value', '_choices')
        
        return {
            **base_return,
            'option1_text': current_question.get('option1_text', ''),
            'reminder_text': current_question.get('reminder_text', ''),
            'reminder_intro': current_question.get('reminder_intro', ''),
            'you_said_text': current_question.get('you_said_text', ''),
            'target_said_text': current_question.get('target_said_text', ''),
            'probabilities': probabilities,
            'probabilities_json': json.dumps(probabilities),
            'question_type': question_type,  # 'single' o 'composite' per la nota nel template
            'event_field_name': event_field_name,  # Nome del campo evento per il form
            'event_choices_name': event_choices_name,  # Nome del campo choices per il form
        }
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Salva i dati della risposta."""
        # Usa il question_num originale salvato in vars_for_template
        question_num = player.participant.vars.get('current_question_num_original', 1)
        
        # Salva il tempo nel campo specifico per questa domanda MPL
        if 1 <= question_num <= 12:
            time_field_name = f'time_mpl_question_{question_num}'
            time_value = save_time_value(player.time_on_page)
            setattr(player, time_field_name, time_value)
            logger.debug(f"MPLQuestion {question_num} - time saved: {time_value}")
        
        # Determina il nome del campo evento basato su question_num
        event_field_name = get_event_field_name(player, question_num)
        event_choices_name = event_field_name.replace('_switch_value', '_choices')
        
        # I dati vengono salvati automaticamente dal form nei nuovi campi evento
        # Verifica che il switch_value sia stato salvato correttamente
        switch_value = player.field_maybe_none(event_field_name)
        if switch_value is None:
            # Se il valore è None, potrebbe essere un problema con il form submission
            # Log per debug
            logger.warning(f"switch_value is None for question {question_num}, player {player.id}")
            logger.debug(f"  - participant: {player.participant.id}")
            logger.debug(f"  - event_field: {event_field_name}")
            logger.debug(f"  - choices_field: {player.field_maybe_none(event_choices_name)}")
        else:
            logger.debug(f"MPLQuestion {question_num} - saved to {event_field_name}: {switch_value}")

class ResultsPart2(BasePagePart2):
    form_model = 'player'
    form_fields = ['time_on_page']
    
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        return has_passed_control_questions(player, 'part2')
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.time_results_part2 = save_time_value(player.time_on_page)
        # Calcola il payoff di Part 2 e impostalo
        # Verifica se è già stato calcolato (per evitare ricalcoli con valori casuali diversi)
        if 'part2_payoff_data' not in player.participant.vars:
            # Calcola il payoff usando la funzione calculate_part2_payoff
            part2_payoff_data = calculate_part2_payoff(player)
            # Salva in participant.vars per uso futuro
            player.participant.vars['part2_payoff_data'] = part2_payoff_data
            player.participant.vars['part2_payoff'] = part2_payoff_data['payoff']
        else:
            # Usa il valore già calcolato
            part2_payoff_data = player.participant.vars['part2_payoff_data']
        
        # Imposta player.payoff con il valore calcolato (o già salvato)
        player.payoff = player.participant.vars.get('part2_payoff', cu(0))  # type: ignore
    
    @staticmethod
    def vars_for_template(player):
        """Mostra un riepilogo delle risposte."""
        # Raccogli tutte le risposte usando i nuovi nomi dei campi evento
        responses = []
        all_questions = generate_mpl_questions(player)
        
        # Crea un dizionario per accesso rapido per question_num
        questions_dict = {q['question_num']: q for q in all_questions}
        
        for i in range(1, 13):
            # Usa il nuovo nome del campo evento
            event_field_name = get_event_field_name(player, i)
            switch_value = player.field_maybe_none(event_field_name)
            
            if switch_value is not None:
                # Recupera le informazioni della domanda per la descrizione
                question_info = questions_dict.get(i, {})
                event_codes = question_info.get('event_codes', [])
                target_code = question_info.get('target_code', '')
                
                # Genera la descrizione dell'evento
                event_description = get_event_description(player, target_code, event_codes)
                
                responses.append({
                    'question_num': i,
                    'switch_value': switch_value,
                    'event_description': event_description,
                    'event_field_name': event_field_name
                })
        
        return {
            'responses': responses,
            'num_questions': NUM_QUESTIONS_PER_PARTICIPANT
        }

# ============================================================================
# FACTORY FUNCTION PER GENERARE DINAMICAMENTE LE 12 CLASSI MPLQuestion
# ============================================================================

def get_form_fields_for_display_order(player, display_order):
    """Determina i form_fields dinamicamente in base all'ordine randomizzato."""
    import json
    # time_on_page deve essere sempre incluso per il tracking del tempo
    # Assicurati che l'ordine sia stato generato
    question_order_json = player.field_maybe_none('mpl_question_order')
    if not question_order_json:
        # Se l'ordine non esiste ancora, generalo
        generate_mpl_questions(player)
        question_order_json = player.field_maybe_none('mpl_question_order')
    
    if not question_order_json:
        # Fallback: usa display_order come question_num se ancora non esiste
        question_num = display_order
    else:
        question_order = json.loads(question_order_json)
        # display_order è 1-based, quindi sottraiamo 1 per l'indice
        if 1 <= display_order <= len(question_order):
            question_num = question_order[display_order - 1]
        else:
            question_num = display_order
    
    # Usa i nuovi nomi dei campi evento
    event_field_name = get_event_field_name(player, question_num)
    event_choices_name = event_field_name.replace('_switch_value', '_choices')
    
    return [event_field_name, event_choices_name, 'time_on_page']


def create_mpl_question_class(display_order):
    """
    Factory function che crea dinamicamente una classe MPLQuestion per un display_order specifico.
    
    Args:
        display_order: Numero dell'ordine di visualizzazione (1-12)
    
    Returns:
        Classe Page per oTree
    """
    class_name = f'MPLQuestion{display_order}'
    
    class MPLQuestionPage(MPLQuestion):
        template_name = 'bargaining_tdl_part2/MPLQuestion.html'
        
        @staticmethod
        def is_displayed(player):
            """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
            if not has_passed_control_questions(player, 'part2'):
                return False
            # Imposta display_order per questa pagina
            player.participant.vars['current_display_order'] = display_order
            # Genera le domande per inizializzare la randomizzazione se non esiste già (solo per la prima)
            if display_order == 1:
                generate_mpl_questions(player)
            return True
        
        @staticmethod
        def get_form_fields(player):
            return get_form_fields_for_display_order(player, display_order)
    
    # Imposta il nome della classe per il debug
    MPLQuestionPage.__name__ = class_name
    MPLQuestionPage.__qualname__ = class_name
    
    return MPLQuestionPage


# Genera dinamicamente le 12 classi MPLQuestion
MPLQuestion1 = create_mpl_question_class(1)
MPLQuestion2 = create_mpl_question_class(2)
MPLQuestion3 = create_mpl_question_class(3)
MPLQuestion4 = create_mpl_question_class(4)
MPLQuestion5 = create_mpl_question_class(5)
MPLQuestion6 = create_mpl_question_class(6)
MPLQuestion7 = create_mpl_question_class(7)
MPLQuestion8 = create_mpl_question_class(8)
MPLQuestion9 = create_mpl_question_class(9)
MPLQuestion10 = create_mpl_question_class(10)
MPLQuestion11 = create_mpl_question_class(11)
MPLQuestion12 = create_mpl_question_class(12)

class ExampleScreenPart2(Page):
    form_model = 'player'
    form_fields = ['time_on_page']

page_sequence = [
    InstructionsPart2,
    ExampleScreenPart2,
    PaymentInstructionPart2,
    ControlQuestionsPart2Attempt1,
    ControlQuestionsPart2Attempt2,
    ControlQuestionsPart2Attempt3,
    ControlQuestionsPart2Attempt4,
    ControlQuestionsPart2Attempt5,
    ThankYouPart2,
    MPLIntroFirstPlayer,
    MPLQuestion1,
    MPLQuestion2,
    MPLQuestion3,
    MPLQuestion4,
    MPLQuestion5,
    MPLQuestion6,
    MPLIntroSecondPlayer,
    MPLQuestion7,
    MPLQuestion8,
    MPLQuestion9,
    MPLQuestion10,
    MPLQuestion11,
    MPLQuestion12,
    ResultsPart2
]
