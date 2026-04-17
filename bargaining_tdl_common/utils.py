"""
Utility functions for cross-module operations in bargaining_tdl.
"""

from functools import lru_cache
from .logger import get_logger

logger = get_logger('utils')

# Cache per get_main_group_player - evita lookup multipli dello stesso player
# Max size 128 entries (sufficiente per sessioni tipiche)
# Nota: La cache usa session_id e participant_id come chiavi
@lru_cache(maxsize=128)
def _get_main_group_player_cached(session_id, participant_id):
    """
    Versione cached di get_main_group_player.
    
    Questa funzione interna usa lru_cache per memorizzare i risultati
    delle lookup, migliorando le performance quando get_main_group_player
    viene chiamata multiple volte per lo stesso player.
    
    Args:
        session_id: ID della sessione (int)
        participant_id: ID del participant (int)
    
    Returns:
        Player instance da bargaining_tdl_main, o None se non trovato
    
    Note:
        - La cache viene invalidata automaticamente quando la sessione cambia
        - Max 128 entries (sufficiente per sessioni tipiche con 6-12 partecipanti)
        - Usa session_id e participant_id come chiavi composite
    """
    try:
        from importlib import import_module
        from otree.models import Session
        
        # Importiamo l'app main
        main_app = import_module('bargaining_tdl_main')
        MainPlayer = main_app.Player
        MainSubsession = main_app.Subsession
        
        # Recupera la sessione
        try:
            session = Session.objects.get(id=session_id)
        except Exception:
            logger.debug(f"Session {session_id} not found")
            return None
        
        # Cerchiamo il subsession dell'app main
        main_subsession = None
        for subsession in session.get_subsessions():
            if isinstance(subsession, MainSubsession):
                main_subsession = subsession
                break
        
        if main_subsession is None:
            logger.debug(f"No main subsession found in session {session_id}")
            return None
        
        # Cerchiamo il player corrispondente (stesso participant)
        for main_player in main_subsession.get_players():
            if main_player.participant.id == participant_id:
                logger.debug(f"Found main player for participant {participant_id}")
                return main_player
        
        logger.debug(f"No main player found for participant {participant_id} in session {session_id}")
        return None
    except Exception as e:
        logger.error(f"Error in _get_main_group_player_cached: {e}", exc_info=True)
        return None


def get_main_group_player(player):
    """
    Recupera il player dal gruppo di main (bargaining_tdl_main).
    ⚠️ SOLO LETTURA - Non modifica i dati di main.
    
    In oTree, per accedere ai dati di un'app precedente, dobbiamo:
    1. Ottenere la sessione corrente
    2. Cercare il subsession dell'app main
    3. Trovare il player corrispondente (stesso participant)
    
    Questa funzione usa caching per migliorare le performance quando chiamata
    multiple volte per lo stesso player.
    
    Args:
        player: Player instance da qualsiasi app
    
    Returns:
        Player instance da bargaining_tdl_main, o None se non trovato
    
    Example:
        >>> main_player = get_main_group_player(current_player)
        >>> if main_player:
        ...     role = main_player.id_in_group
    """
    try:
        # Usa la cache per migliorare le performance
        # La cache è trasparente: se il risultato è già stato calcolato,
        # viene restituito immediatamente senza lookup nel database
        session_id = player.session.id
        participant_id = player.participant.id
        
        cached_result = _get_main_group_player_cached(session_id, participant_id)
        if cached_result is not None:
            logger.debug(f"Cache hit for participant {participant_id}")
            return cached_result
        
        # Fallback: implementazione diretta (per compatibilità)
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
            logger.debug(f"No main subsession found for session {session_id}")
            return None
        
        # Cerchiamo il player corrispondente (stesso participant)
        for main_player in main_subsession.get_players():
            if main_player.participant == player.participant:
                # Aggiorna la cache per future chiamate
                _get_main_group_player_cached.cache_clear()  # Clear per forzare refresh
                return main_player
        
        logger.debug(f"No main player found for participant {participant_id}")
        return None
    except Exception as e:
        # In caso di errore, ritorniamo None
        # Questo può succedere durante i test o se l'app main non è ancora stata eseguita
        logger.error(f"Error in get_main_group_player: {e}", exc_info=True)
        return None


def get_participant_role_in_group(player):
    """
    Determina il ruolo del player nel gruppo (A, B, o C).
    Basato sulla posizione nel gruppo (id 1, 2, o 3).
    
    ⚠️ SOLO LETTURA - Non modifica i dati di main.
    
    Mapping:
    - P1 (id_in_group=1) → A
    - P2 (id_in_group=2) → B  
    - P3 (id_in_group=3) → C
    
    Args:
        player: Player instance da qualsiasi app
    
    Returns:
        str: 'A', 'B', o 'C', o None se non determinabile
    
    Example:
        >>> role = get_participant_role_in_group(current_player)
        >>> if role == 'A':
        ...     # Player è A nel gruppo
    """
    main_player = get_main_group_player(player)
    if main_player is None:
        logger.debug(f"Could not determine role: main player not found for player {player.id}")
        return None
    
    # Il ruolo è determinato da id_in_group nel gruppo di main
    id_in_group = main_player.id_in_group
    role = get_role_from_id(id_in_group)
    
    if role:
        logger.debug(f"Player {player.id} has role {role} (id_in_group={id_in_group})")
    
    return role


# ============================================================================
# COLOR-BASED PLAYER IDENTIFICATION
# Each player in a triad is identified by a color: Red, Green, Blue.
# Always referenced as written text for colorblind accessibility.
# ============================================================================

COLOR_MAPPING = {1: 'Red', 2: 'Green', 3: 'Blue'}
ROLE_TO_ID = {'A': 1, 'B': 2, 'C': 3}
ID_TO_ROLE = {1: 'A', 2: 'B', 3: 'C'}

TOPOLOGY = {
    1: {'left': 3, 'right': 2},
    2: {'left': 1, 'right': 3},
    3: {'left': 2, 'right': 1},
}


def get_player_color(id_in_group):
    """Returns the color name for a given id_in_group (1=Red, 2=Green, 3=Blue)."""
    return COLOR_MAPPING.get(id_in_group, 'Unknown')


def get_role_from_id(id_in_group):
    """Returns role code (A/B/C) from id_in_group."""
    return ID_TO_ROLE.get(id_in_group)


def get_id_from_role(role_code):
    """Returns id_in_group (1/2/3) from role code A/B/C."""
    return ROLE_TO_ID.get(role_code)


def get_left_partner_id(id_in_group):
    """Returns the internal 'left' partner id for a player id_in_group."""
    partners = TOPOLOGY.get(id_in_group, {})
    return partners.get('left')


def get_right_partner_id(id_in_group):
    """Returns the internal 'right' partner id for a player id_in_group."""
    partners = TOPOLOGY.get(id_in_group, {})
    return partners.get('right')


def get_partner_side(current_id, target_id):
    """
    Returns partner side from internal topology: 'left', 'right', or None.
    """
    if get_left_partner_id(current_id) == target_id:
        return 'left'
    if get_right_partner_id(current_id) == target_id:
        return 'right'
    return None


def get_partner_colors(player):
    """
    Returns a dict with 'my_color', 'left_partner_color', 'right_partner_color'
    based on the main group topology.

    Works from any app (intro, main, part2, part3) by resolving the
    player's id_in_group in bargaining_tdl_main.
    """
    main_player = get_main_group_player(player)
    if main_player is None:
        return {
            'my_color': 'Unknown',
            'left_partner_color': 'Unknown',
            'right_partner_color': 'Unknown',
        }

    my_id = main_player.id_in_group
    partners = TOPOLOGY[my_id]
    return {
        'my_color': COLOR_MAPPING[my_id],
        'left_partner_color': COLOR_MAPPING[partners['left']],
        'right_partner_color': COLOR_MAPPING[partners['right']],
    }

