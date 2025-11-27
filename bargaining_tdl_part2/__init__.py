from otree.api import *

doc = """
Bargaining Game (Part 2: Matching Probability List - MPL)
Genera 12 MPL questions per ogni partecipante basandosi sui dati della Parte 1.
"""

# ============================================================================
# TESTI OBBLIGATORI - NON MODIFICARE
# Fonte: Sezione "⚠️ SEZIONE CRITICA: TESTI ORIGINALI OBBLIGATORI"
# ============================================================================

# Testi delle Opzioni di Scelta Parte 1 (Sezione 📄 4)
# Per il "player on the left" (B nel gruppo):
EVENT_TEXT_EB1 = "Share only with the player on the right"
EVENT_TEXT_EB2 = "Share only with you"
EVENT_TEXT_EB3 = "Share with both you and the player on the right"

# Per il "player on the right" (C nel gruppo):
EVENT_TEXT_EC1 = "Share only with the player on the left"
EVENT_TEXT_EC2 = "Share only with you"
EVENT_TEXT_EC3 = "Share with both you and the player on the left"

# Per A (quando B o C fanno domande su A):
# Quando B o C fanno domande su A, A è sempre "the player on the left" per entrambi
# Quindi i testi sono gli stessi di EB1-3 (perché A è left come B)
# EA1: A divide with C only (per B) o A divide with B only (per C) → "Share only with the player on the right"
# EA2: A divide with B only (per B) o A divide with C only (per C) → "Share only with you"
# EA3: A divide among all three → "Share with both you and the player on the right"
EVENT_TEXT_EA1 = EVENT_TEXT_EB1  # A divide with C only (per B) o A divide with B only (per C)
EVENT_TEXT_EA2 = EVENT_TEXT_EB2  # A divide with B only (per B) o A divide with C only (per C)
EVENT_TEXT_EA3 = EVENT_TEXT_EB3  # A divide among all three

# Mapping Eventi → Testi
EVENT_TO_TEXT = {
    'EB1': EVENT_TEXT_EB1,
    'EB2': EVENT_TEXT_EB2,
    'EB3': EVENT_TEXT_EB3,
    'EC1': EVENT_TEXT_EC1,
    'EC2': EVENT_TEXT_EC2,
    'EC3': EVENT_TEXT_EC3,
    'EA1': EVENT_TEXT_EA1,  # Usato quando B o C fanno domande su A (stesso di EB1)
    'EA2': EVENT_TEXT_EA2,  # Usato quando B o C fanno domande su A (stesso di EB2)
    'EA3': EVENT_TEXT_EA3,  # Usato quando B o C fanno domande su A (stesso di EB3)
}

# Struttura Testo Option 1 (Sezione 📄 5)
# Nota: Usiamo £5 invece di €5 perché REAL_WORLD_CURRENCY_CODE = 'GBP'
OPTION1_SINGLE_TEMPLATE_LEFT = "You win £5 if the player on the left chose \"{event_text}\" (and nothing otherwise)."
OPTION1_SINGLE_TEMPLATE_RIGHT = "You win £5 if the player on the right chose \"{event_text}\" (and nothing otherwise)."
OPTION1_COMPOSITE_TEMPLATE_LEFT = "You win £5 if the player on the left chose \"{event_text_1}\" or \"{event_text_2}\" (and nothing otherwise)."
OPTION1_COMPOSITE_TEMPLATE_RIGHT = "You win £5 if the player on the right chose \"{event_text_1}\" or \"{event_text_2}\" (and nothing otherwise)."

# Struttura Testo Option 2 (Sezione 📄 6)
OPTION2_TEXT = "You win £5 with the following probability (and nothing otherwise)."

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
PRIZE_AMOUNT = "£5"
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
    # Campi per le 12 risposte MPL (switch values)
    mpl_question_1_switch_value = models.IntegerField(blank=True)
    mpl_question_2_switch_value = models.IntegerField(blank=True)
    mpl_question_3_switch_value = models.IntegerField(blank=True)
    mpl_question_4_switch_value = models.IntegerField(blank=True)
    mpl_question_5_switch_value = models.IntegerField(blank=True)
    mpl_question_6_switch_value = models.IntegerField(blank=True)
    mpl_question_7_switch_value = models.IntegerField(blank=True)
    mpl_question_8_switch_value = models.IntegerField(blank=True)
    mpl_question_9_switch_value = models.IntegerField(blank=True)
    mpl_question_10_switch_value = models.IntegerField(blank=True)
    mpl_question_11_switch_value = models.IntegerField(blank=True)
    mpl_question_12_switch_value = models.IntegerField(blank=True)
    
    # Opzionale: salvare anche le scelte complete per validazione (JSON)
    mpl_question_1_choices = models.LongStringField(blank=True)
    mpl_question_2_choices = models.LongStringField(blank=True)
    mpl_question_3_choices = models.LongStringField(blank=True)
    mpl_question_4_choices = models.LongStringField(blank=True)
    mpl_question_5_choices = models.LongStringField(blank=True)
    mpl_question_6_choices = models.LongStringField(blank=True)
    mpl_question_7_choices = models.LongStringField(blank=True)
    mpl_question_8_choices = models.LongStringField(blank=True)
    mpl_question_9_choices = models.LongStringField(blank=True)
    mpl_question_10_choices = models.LongStringField(blank=True)
    mpl_question_11_choices = models.LongStringField(blank=True)
    mpl_question_12_choices = models.LongStringField(blank=True)
    
    # Control Questions for Part 2
    control_question_1 = models.StringField(
        choices=[
            ["nothing", "I don't win anything."],
            ["5", "£5."],
            ["dont_know", "I don't know."]
        ],
        label="Question 1: What would be the payment for Part 2?"
    )
    
    control_question_2 = models.StringField(
        choices=[
            ["nothing", "I don't win anything."],
            ["5", "£5."],
            ["dont_know", "I don't know."]
        ],
        label="Question 2: What would be the payment for Part 2?"
    )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_main_group_player(player: Player):
    """
    Recupera il player dal gruppo di main (bargaining_tdl_main).
    ⚠️ SOLO LETTURA - Non modifica i dati di main.
    
    In oTree, per accedere ai dati di un'app precedente, dobbiamo:
    1. Ottenere la sessione corrente
    2. Cercare il subsession dell'app main
    3. Trovare il player corrispondente (stesso participant)
    """
    try:
        # Importiamo il modello Player di main
        from importlib import import_module
        
        # Importiamo l'app main
        main_app = import_module('bargaining_tdl_main')
        MainPlayer = main_app.Player
        MainSubsession = main_app.Subsession
        
        # Otteniamo la sessione corrente
        session = player.session
        
        # Cerchiamo il subsession dell'app main
        # In oTree, ogni app ha un subsession per round
        # Cerchiamo tutti i subsessions e controlliamo se sono di tipo MainSubsession
        main_subsession = None
        for subsession in session.get_subsessions():
            # Controlliamo se questo subsession è un'istanza di MainSubsession
            if isinstance(subsession, MainSubsession):
                main_subsession = subsession
                break
        
        if main_subsession is None:
            return None
        
        # Cerchiamo il player corrispondente (stesso participant)
        for main_player in main_subsession.get_players():
            if main_player.participant == player.participant:
                return main_player
        
        return None
    except Exception as e:
        # In caso di errore, ritorniamo None
        # Questo può succedere durante i test o se l'app main non è ancora stata eseguita
        import traceback
        print(f"ERROR in get_main_group_player: {e}")
        traceback.print_exc()
        return None

def get_participant_role_in_group(player: Player) -> str:
    """
    Determina il ruolo del player nel gruppo (A, B, o C).
    Basato sulla posizione nel gruppo (id 1, 2, o 3).
    
    ⚠️ SOLO LETTURA - Non modifica i dati di main.
    
    Mapping:
    - P1 (id_in_group=1) → A
    - P2 (id_in_group=2) → B  
    - P3 (id_in_group=3) → C
    """
    main_player = get_main_group_player(player)
    if main_player is None:
        return None
    
    # Il ruolo è determinato da id_in_group nel gruppo di main
    id_in_group = main_player.id_in_group
    if id_in_group == 1:
        return 'A'
    elif id_in_group == 2:
        return 'B'
    elif id_in_group == 3:
        return 'C'
    return None

def get_target_player_label(player: Player, target_code: str) -> str:
    """
    Converte un codice target (A/B/C) in "player on the left" o "player on the right"
    basandosi sul ruolo del player corrente nel gruppo.
    
    Mapping:
    - Se subject = A (P1 nel gruppo):
    #   B (P2) → player on the left
    #   C (P3) → player on the right
    
    - Se subject = B (P2 nel gruppo):
    #   A (P1) → player on the left
    #   C (P3) → player on the right
    
    - Se subject = C (P3 nel gruppo):
    #   A (P1) → player on the left
    #   B (P2) → player on the right
    """
    role = get_participant_role_in_group(player)
    if role is None:
        return None
    
    # Mapping basato sul ruolo
    if role == 'A':
        if target_code == 'B':
            return "the player on the left"
        elif target_code == 'C':
            return "the player on the right"
    elif role == 'B':
        if target_code == 'A':
            return "the player on the left"
        elif target_code == 'C':
            return "the player on the right"
    elif role == 'C':
        if target_code == 'A':
            return "the player on the left"
        elif target_code == 'B':
            return "the player on the right"
    
    return None

def generate_option1_single_event(
    player: Player,
    target_code: str,
    event_code: str
) -> str:
    """
    Genera il testo di Option 1 per un Single Event.
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C' (chi ha fatto la scelta)
        event_code: Codice evento (es. 'EB1', 'EC1')
    
    Returns:
        Stringa con il testo completo di Option 1
    """
    target_label = get_target_player_label(player, target_code)
    if target_label is None:
        return ""
    
    event_text = EVENT_TO_TEXT.get(event_code, "")
    if not event_text:
        return ""
    
    # Determina se il target è "left" o "right"
    if "left" in target_label:
        return OPTION1_SINGLE_TEMPLATE_LEFT.format(event_text=event_text)
    else:
        return OPTION1_SINGLE_TEMPLATE_RIGHT.format(event_text=event_text)

def generate_option1_composite_event(
    player: Player,
    target_code: str,
    event_codes: list[str]
) -> str:
    """
    Genera il testo di Option 1 per un Composite Event (OR logico).
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C'
        event_codes: Lista di codici evento (es. ['EB2', 'EB3'])
    
    Returns:
        Stringa con il testo completo di Option 1
    """
    target_label = get_target_player_label(player, target_code)
    if target_label is None:
        return ""
    
    if len(event_codes) != 2:
        return ""
    
    event_text_1 = EVENT_TO_TEXT.get(event_codes[0], "")
    event_text_2 = EVENT_TO_TEXT.get(event_codes[1], "")
    
    if not event_text_1 or not event_text_2:
        return ""
    
    # Determina se il target è "left" o "right"
    if "left" in target_label:
        return OPTION1_COMPOSITE_TEMPLATE_LEFT.format(
            event_text_1=event_text_1,
            event_text_2=event_text_2
        )
    else:
        return OPTION1_COMPOSITE_TEMPLATE_RIGHT.format(
            event_text_1=event_text_1,
            event_text_2=event_text_2
        )

def load_part1_data_for_mpl(player: Player, target_code: str) -> dict:
    """
    Carica i dati della Parte 1 relativi a un target participant specifico.
    
    ⚠️ VINCOLO: SOLO LETTURA - Non modifica i dati di intro/main.
    
    Args:
        player: Player corrente
        target_code: 'A', 'B', o 'C' (il participant di cui si sta chiedendo la scelta)
    
    Returns:
        Dict con:
        - 'you_said': str (intenzione dichiarata al target)
        - 'target_said': str (intenzione dichiarata dal target)
        - 'target_decision': str (scelta finale del target: Left/Right/Both)
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
    target_id = None
    if target_code == 'A':
        target_id = 1
    elif target_code == 'B':
        target_id = 2
    elif target_code == 'C':
        target_id = 3
    
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
    
    # Determina quale signal recuperare in base al target
    # Topology in main:
    # P1: Left=P3, Right=P2
    # P2: Left=P1, Right=P3
    # P3: Left=P2, Right=P1
    
    current_id = main_player.id_in_group
    
    # Determina se il target è "left" o "right" per il player corrente
    target_is_left = False
    target_is_right = False
    
    if current_id == 1:  # P1 (A)
        if target_id == 3:  # P3 (C) è left
            target_is_left = True
        elif target_id == 2:  # P2 (B) è right
            target_is_right = True
    elif current_id == 2:  # P2 (B)
        if target_id == 1:  # P1 (A) è left
            target_is_left = True
        elif target_id == 3:  # P3 (C) è right
            target_is_right = True
    elif current_id == 3:  # P3 (C)
        if target_id == 2:  # P2 (B) è left
            target_is_left = True
        elif target_id == 1:  # P1 (A) è right
            target_is_right = True
    
    # Recupera "you_said" - intenzione del player corrente al target
    # Dati da participant.vars (salvati da intro)
    you_said = ""
    if target_is_left:
        you_said = player.participant.vars.get('signal_left', '')
    elif target_is_right:
        you_said = player.participant.vars.get('signal_right', '')
    
    # Recupera "target_said" - intenzione del target al player corrente
    # Dati da participant.vars del target (salvati da intro)
    target_said = ""
    target_vars = target_player.participant.vars
    
    # Determina quale signal del target è rivolto al player corrente
    # Topology inversa:
    # Se current è left per target, allora target ha inviato signal_right a current
    # Se current è right per target, allora target ha inviato signal_left a current
    
    # Per il target, determiniamo se current è left o right
    if target_id == 1:  # P1 (A)
        if current_id == 3:  # P3 (C) è left per P1, quindi P1 ha inviato signal_left a P3
            target_said = target_vars.get('signal_left', '')
        elif current_id == 2:  # P2 (B) è right per P1, quindi P1 ha inviato signal_right a P2
            target_said = target_vars.get('signal_right', '')
    elif target_id == 2:  # P2 (B)
        if current_id == 1:  # P1 (A) è left per P2, quindi P2 ha inviato signal_left a P1
            target_said = target_vars.get('signal_left', '')
        elif current_id == 3:  # P3 (C) è right per P2, quindi P2 ha inviato signal_right a P3
            target_said = target_vars.get('signal_right', '')
    elif target_id == 3:  # P3 (C)
        if current_id == 2:  # P2 (B) è left per P3, quindi P3 ha inviato signal_left a P2
            target_said = target_vars.get('signal_left', '')
        elif current_id == 1:  # P1 (A) è right per P3, quindi P3 ha inviato signal_right a P1
            target_said = target_vars.get('signal_right', '')
    
    # Recupera "target_decision" - scelta finale del target
    # Dati dal campo decision_choice del target player in main
    target_decision = target_player.decision_choice if hasattr(target_player, 'decision_choice') else ''
    
    return {
        'you_said': you_said,
        'target_said': target_said,
        'target_decision': target_decision
    }

def generate_mpl_questions(player: Player) -> list[dict]:
    """
    Genera la lista delle 12 domande MPL per il player.
    
    ⚠️ SOLO LETTURA - Non modifica i dati di intro/main.
    
    Returns:
        Lista di dict, ognuno con:
        - 'question_num': int (1-12)
        - 'type': 'single' o 'composite'
        - 'target_code': str ('A', 'B', o 'C')
        - 'event_codes': list[str] (es. ['EB1'] o ['EB2', 'EB3'])
        - 'option1_text': str (testo completo)
        - 'reminder_text': str (reminder Parte 1)
        - 'probabilities': list[int] (lista probabilità)
    """
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
    
    # Arricchiamo ogni domanda con i dati necessari
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
        reminder_text = REMINDER_TEMPLATE.format(
            target_label=target_label or "the other participant",
            you_said=part1_data['you_said'],
            target_said=part1_data['target_said']
        )
        # Preparo anche le parti separate per inserirle nella tabella
        reminder_intro = f"We remind you of the following information regarding what you and {target_label or 'the other participant'} have declared to each other:"
        you_said_text = f"You said: {part1_data['you_said']}"
        target_said_text = f"{target_label or 'the other participant'} said: {part1_data['target_said']}"
        
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
    
    return enriched_questions

def check_control_questions_part2_correct(player: Player) -> bool:
    """Verifica se entrambe le risposte alle control questions sono corrette."""
    if not player.control_question_1 or not player.control_question_2:
        return False
    
    # Entrambe le risposte corrette devono essere "5" (£5)
    correct = (
        player.control_question_1 == "5" and
        player.control_question_2 == "5"
    )
    return correct

# ============================================================================
# PAGES
# ============================================================================

class InstructionsPart2(Page):
    pass

class PaymentInstructionPart2(Page):
    pass

class ControlQuestionsPart2(Page):
    form_model = 'player'
    form_fields = ['control_question_1', 'control_question_2']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Salva un flag se le risposte sono sbagliate."""
        is_correct = check_control_questions_part2_correct(player)
        player.participant.vars['failed_control_questions_part2'] = not is_correct

class ThankYouPart2(Page):
    """Pagina di saluto che termina l'esperimento per il partecipante."""
    
    @staticmethod
    def is_displayed(player):
        """Mostra questa pagina solo se le risposte alle control questions erano sbagliate."""
        failed = player.participant.vars.get('failed_control_questions_part2')
        if failed is None:
            return False
        return failed
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """Termina l'esperimento dopo questa pagina."""
        return []

class MPLQuestion(Page):
    form_model = 'player'
    # form_fields sarà impostato dinamicamente per ogni istanza
    
    @staticmethod
    def vars_for_template(player):
        """Prepara i dati per il template."""
        question_num = player.participant.vars.get('current_question_num', 1)
        
        # Genera tutte le domande
        all_questions = generate_mpl_questions(player)
        
        # Debug: stampa informazioni utili
        if not all_questions:
            print(f"WARNING: generate_mpl_questions returned empty list for player {player.id}")
            print(f"  - participant: {player.participant.id}")
            print(f"  - role: {get_participant_role_in_group(player)}")
            print(f"  - main_player: {get_main_group_player(player)}")
        
        # Trova la domanda corrente
        current_question = None
        for q in all_questions:
            if q['question_num'] == question_num:
                current_question = q
                break
        
        import json
        
        # Base return sempre con question_num e costanti UI
        base_return = {
            'question_num': question_num,
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
            debug_info = f"DEBUG: No question found. Total questions: {len(all_questions)}, Question num: {question_num}"
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
        }
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Salva i dati della risposta."""
        question_num = player.participant.vars.get('current_question_num', 1)
        
        # I dati vengono salvati automaticamente dal form
        # Qui possiamo fare validazioni aggiuntive se necessario
        # Converti choices_json da stringa a oggetto se necessario
        choices_field = getattr(player, f'mpl_question_{question_num}_choices', None)
        if choices_field and isinstance(choices_field, str):
            # Il campo è già una stringa JSON, va bene così
            pass

class ResultsPart2(Page):
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        return not failed
    
    @staticmethod
    def vars_for_template(player):
        """Mostra un riepilogo delle risposte."""
        # Raccogli tutte le risposte
        responses = []
        for i in range(1, 13):
            switch_value = getattr(player, f'mpl_question_{i}_switch_value', None)
            if switch_value is not None:
                responses.append({
                    'question_num': i,
                    'switch_value': switch_value
                })
        
        return {
            'responses': responses,
            'num_questions': NUM_QUESTIONS_PER_PARTICIPANT
        }

# Definiamo le 12 pagine MPLQuestion come classi separate per evitare problemi con oTree
# Tutte usano lo stesso template MPLQuestion.html
class MPLQuestion1(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_1_switch_value', 'mpl_question_1_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 1
        return True

class MPLQuestion2(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_2_switch_value', 'mpl_question_2_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 2
        return True

class MPLQuestion3(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_3_switch_value', 'mpl_question_3_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 3
        return True

class MPLQuestion4(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_4_switch_value', 'mpl_question_4_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 4
        return True

class MPLQuestion5(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_5_switch_value', 'mpl_question_5_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 5
        return True

class MPLQuestion6(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_6_switch_value', 'mpl_question_6_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 6
        return True

class MPLQuestion7(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_7_switch_value', 'mpl_question_7_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 7
        return True

class MPLQuestion8(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_8_switch_value', 'mpl_question_8_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 8
        return True

class MPLQuestion9(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_9_switch_value', 'mpl_question_9_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 9
        return True

class MPLQuestion10(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_10_switch_value', 'mpl_question_10_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 10
        return True

class MPLQuestion11(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_11_switch_value', 'mpl_question_11_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 11
        return True

class MPLQuestion12(MPLQuestion):
    template_name = 'bargaining_tdl_part2/MPLQuestion.html'
    form_fields = ['mpl_question_12_switch_value', 'mpl_question_12_choices']
    @staticmethod
    def is_displayed(player):
        """Non mostrare questa pagina se il partecipante ha fallito le control questions."""
        failed = player.participant.vars.get('failed_control_questions_part2', False)
        if failed:
            return False
        player.participant.vars['current_question_num'] = 12
        return True

page_sequence = [
    InstructionsPart2,
    PaymentInstructionPart2,
    ControlQuestionsPart2,
    ThankYouPart2,
    MPLQuestion1,
    MPLQuestion2,
    MPLQuestion3,
    MPLQuestion4,
    MPLQuestion5,
    MPLQuestion6,
    MPLQuestion7,
    MPLQuestion8,
    MPLQuestion9,
    MPLQuestion10,
    MPLQuestion11,
    MPLQuestion12,
    ResultsPart2
]
