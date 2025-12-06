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
    role_mapping = {1: 'A', 2: 'B', 3: 'C'}
    role = role_mapping.get(id_in_group)
    
    if role:
        logger.debug(f"Player {player.id} has role {role} (id_in_group={id_in_group})")
    
    return role

